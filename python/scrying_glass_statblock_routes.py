"""Private statblock API routes on the Admin application (SG-TODO-022.08).

| Route | Purpose |
|---|---|
| GET  /api/statblocks/state | campaign, encounter token, tile summaries and every monster's statblock revision |
| GET  /api/statblocks/monsters/{id}?known_revision=N | six live SG values plus the saved snapshot |
| POST /api/statblocks/discover | exact candidates per monster and per-provider completeness |
| POST /api/statblocks/prepare | JSON candidate or multipart ``.monster`` file -> preparation job (202) |
| GET  /api/statblocks/jobs/{job_id} | job status; on completion selection, expiry, source, warnings, preview |
| DELETE /api/statblocks/jobs/{job_id} | cancel; a completed job's unused selection is released |
| POST /api/statblocks/apply | atomic, idempotent apply of prepared selections |
| GET  /api/statblocks/collected | statblocks collected for added monsters that wait for confirmation (022.15) |
| POST /api/statblocks/collected/{id} | ``{decision: replace or keep, expected_statblock_revision}`` |

All routes need a signed-in regular admin assigned to the active campaign
(superadmin-only and Client Display sessions are refused) and are
``Cache-Control: no-store``. Writes are same-origin. Network work runs outside
the operation lock. The protected statblock listener (022.09, default port
3200) mounts the two read routes with its own session cookie.
"""
import asyncio
import json

from fastapi import Depends, Request
from fastapi.responses import JSONResponse

from .scrying_glass_database_transactions import serialized_handler, transactional_handler
from .scrying_glass_request_security import same_origin
from .scrying_glass_statblock_limits import APPLY_BODY_BYTES, MONSTER_FILE_BYTES
from .scrying_glass_statblock_service import StatblockAPIError, statblock_service

MULTIPART_OVERHEAD = 64 * 1024


async def _json_body(request, limit=APPLY_BODY_BYTES):
    length = request.headers.get('content-length')
    if length is not None and (not length.isdecimal() or int(length) > limit):
        raise StatblockAPIError(413, 'body_too_large', 'The request body is too large.')
    raw = bytearray()
    async for chunk in request.stream():
        raw.extend(chunk)
        if len(raw) > limit:
            raise StatblockAPIError(413, 'body_too_large', 'The request body is too large.')
    try:
        value = json.loads(bytes(raw))
    except (ValueError, UnicodeError, RecursionError):
        raise StatblockAPIError(422, 'invalid_request', 'Expected a JSON object.') from None
    if type(value) is not dict:
        raise StatblockAPIError(422, 'invalid_request', 'Expected a JSON object.')
    return value


async def _form_body(request):
    """multipart: campaign_id, encounter_token, monster_id, expected_statblock_revision, file."""
    length = request.headers.get('content-length')
    if length is None or not length.isdecimal() or int(length) > MONSTER_FILE_BYTES + MULTIPART_OVERHEAD:
        raise StatblockAPIError(413, 'file_too_large', 'The file is larger than 5 MiB.')
    try:
        form = await request.form(max_files=1, max_fields=8)
    except TypeError:  # older Starlette without form limits
        form = await request.form()
    except Exception:
        raise StatblockAPIError(422, 'invalid_request', 'Malformed multipart request.') from None
    upload = form.get('file')
    if upload is None or not hasattr(upload, 'read'):
        raise StatblockAPIError(422, 'invalid_request', 'Choose a .monster file.')
    data = await upload.read(MONSTER_FILE_BYTES + 1)
    if len(data) > MONSTER_FILE_BYTES:
        raise StatblockAPIError(413, 'file_too_large', 'The file is larger than 5 MiB.')
    fields = {}
    for key in ('campaign_id', 'encounter_token', 'monster_id', 'expected_statblock_revision'):
        value = form.get(key)
        if not isinstance(value, str):
            raise StatblockAPIError(422, 'invalid_request', f'Missing {key}.')
        fields[key] = value
    if set(form.keys()) - set(fields) - {'file'}:
        raise StatblockAPIError(422, 'invalid_request', 'Unexpected preparation fields.')
    try:
        fields['expected_statblock_revision'] = int(fields['expected_statblock_revision'])
    except ValueError:
        raise StatblockAPIError(422, 'invalid_request',
                                'expected_statblock_revision must be a nonnegative integer.') from None
    return fields, data, getattr(upload, 'filename', None)


def install_statblock_routes(context, app, *, cookie=None, writes=True):
    """Admin app: all routes. Statblock listener (022.09): reads only, with its own cookie."""
    # No postponed annotations here: FastAPI and serialized_handler need the Request class.
    cookie = cookie or context.ADMIN_SESSION_COOKIE
    def _token(context, request):
        return request.cookies.get(cookie, '')

    async def envelope(request, exc):
        headers = {'Cache-Control': 'no-store'}
        return JSONResponse(exc.envelope(), status_code=exc.status, headers=headers)
    app.add_exception_handler(StatblockAPIError, envelope)

    def serialized(handler):
        return serialized_handler(context, handler, role='admin', cookie_name=cookie)

    async def statblock_state(request: Request):
        service = statblock_service(context)
        return service.state_projection(service.authorize(_token(context, request)))

    async def statblock_monster(monster_id: str, request: Request):
        service = statblock_service(context)
        known = request.query_params.get('known_revision')
        known = int(known) if known is not None and known.isdecimal() else None
        return service.monster_projection(service.authorize(_token(context, request)), monster_id, known)

    async def discover_statblocks(request: Request):
        body = await _json_body(request)
        service = statblock_service(context)
        async def begin(request: Request):
            return service.discover_begin(service.authorize(_token(context, request), body.get('campaign_id')), body)
        plan = await serialized(begin)(request)
        results = await asyncio.to_thread(service.discover_run, plan)
        async def finish(request: Request):
            return service.discover_finish(service.authorize(_token(context, request), plan.principal.campaign),
                                           plan, results)
        return await serialized(finish)(request)

    async def prepare_statblock(request: Request):
        content_type = request.headers.get('content-type', '')
        if content_type.startswith('multipart/form-data'):
            body, data, filename = await _form_body(request)
        else:
            body, data, filename = await _json_body(request), None, None
        service = statblock_service(context)
        async def accept(request: Request):
            principal = service.authorize(_token(context, request), body.get('campaign_id'))
            return service.prepare(principal, body, file_bytes=data, filename=filename)
        return JSONResponse(await serialized(accept)(request), status_code=202)

    async def statblock_job(job_id: str, request: Request):
        service = statblock_service(context)
        return service.job_status(service.authorize(_token(context, request)), job_id)

    async def cancel_statblock_job(job_id: str, request: Request):
        service = statblock_service(context)
        return service.job_cancel(service.authorize(_token(context, request)), job_id)

    async def apply_statblocks(request: Request):
        body = await _json_body(request)
        service = statblock_service(context)
        async def apply_statblocks(request: Request):
            principal = service.authorize(_token(context, request), body.get('campaign_id'))
            return service.apply(principal, body)
        return await transactional_handler(context, apply_statblocks, role='admin', cookie_name=cookie)(request)

    async def collected_statblocks(request: Request):
        service = statblock_service(context)
        return service.collected_list(service.authorize(_token(context, request)))

    async def decide_collected_statblock(collected_id: str, request: Request):
        body = await _json_body(request)
        service = statblock_service(context)
        async def decide_collected_statblock(request: Request):
            return service.collected_decide(service.authorize(_token(context, request)), collected_id, body)
        return await transactional_handler(context, decide_collected_statblock, role='admin', cookie_name=cookie)(request)

    read = [Depends(context.require('admin', cookie))]
    write = read + [Depends(same_origin)]
    routes = [('/api/statblocks/state', statblock_state, 'GET', read, True),
              ('/api/statblocks/monsters/{monster_id}', statblock_monster, 'GET', read, True)]
    if writes:
        routes += [('/api/statblocks/discover', discover_statblocks, 'POST', write, False),
                   ('/api/statblocks/prepare', prepare_statblock, 'POST', write, False),
                   ('/api/statblocks/jobs/{job_id}', statblock_job, 'GET', read, True),
                   ('/api/statblocks/jobs/{job_id}', cancel_statblock_job, 'DELETE', write, True),
                   ('/api/statblocks/apply', apply_statblocks, 'POST', write, False),
                   ('/api/statblocks/collected', collected_statblocks, 'GET', read, True),
                   ('/api/statblocks/collected/{collected_id}', decide_collected_statblock, 'POST', write, False)]
    for path, handler, method, dependencies, wrap in routes:
        app.add_api_route(path, serialized(handler) if wrap else handler, methods=[method], dependencies=dependencies)
