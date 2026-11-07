"""Authenticated server-held refresh reviews; no browser UI or durable review tokens."""
import asyncio
import copy
import secrets
import time
from fastapi import Body, Depends
from .scrying_glass_campaign_ownership import actor
from .scrying_glass_database_transactions import serialized_handler, transactional_handler
from .scrying_glass_request_security import same_origin
from .scrying_glass_monster_refresh_sources import resolve_selected_sources
from .scrying_glass_monster_source_snapshot import FIELDS
from .scrying_glass_monster_initiative import initiative_patch
from .scrying_glass_monster_initiative_order import order_for_monster_change
from .scrying_glass_statistics import legacy_max_edit
from .scrying_glass_feature_rules import sync_health
from .scrying_glass_health_limits import MAX_STORED_HP

TTL = 600
MAX_REVIEWS = 64
ALLOWED = {'initiative_bonus', 'ac', 'max_hp', 'hp'}


def _scope(context):
    user = actor(context)
    if not user or user.get('role') not in {'admin', 'superadmin'}:
        raise context.HTTPException(401, 'Authenticated refresh context required')
    return (str(user['id']), user['username'], str(context.active_campaign()),
            copy.deepcopy(context.STATE.get('active_setup')), id(context.STATE))


def _store(context):
    if not hasattr(context, '_monster_refresh_reviews'):
        context._monster_refresh_reviews = {}
    return context._monster_refresh_reviews


def _review(context, token):
    if not isinstance(token, str) or len(token) > 200:
        raise context.HTTPException(422, 'Invalid review ID')
    review = _store(context).get(token)
    if review is None or time.monotonic() >= review['expires']:
        _store(context).pop(token, None)
        raise context.HTTPException(410, 'Review expired or already consumed')
    scope = _scope(context)
    if scope[:2] != review['scope'][:2]:
        raise context.HTTPException(403, 'Review belongs to another user')
    if (scope != review['scope'] or context.STATE != review['state']
            or context.CONFIG.get('display') != review['display']):
        raise context.HTTPException(409, 'Encounter or source configuration changed; repeat review')
    return review


def _public(token, review):
    return dict(review_id=token, expires_in=max(0, int(review['expires']-time.monotonic())),
                ids=list(review['ids']), rows=copy.deepcopy(review['rows']))


def install_monster_refresh(context, app):
    async def preview_monster_refresh(body: dict = Body(...)):
        if set(body) - {'ids', 'choices', 'review_id'}:
            raise context.HTTPException(422, 'Unexpected review fields')
        previous = body.get('review_id')
        if previous is not None:
            review = _review(context, previous)
            if 'ids' in body and body['ids'] != review['ids']:
                raise context.HTTPException(422, 'Original selection cannot change')
            ids = list(review['ids'])
            choices = dict(review['choices'])
        else:
            ids, choices = body.get('ids'), {}
            review = dict(scope=_scope(context), state=copy.deepcopy(context.STATE),
                          display=copy.deepcopy(context.CONFIG.get('display')),
                          expires=time.monotonic()+TTL)
        updates = body.get('choices', {})
        if not isinstance(updates, dict):
            raise context.HTTPException(422, 'Expected candidate choices by row ID')
        choices.update(updates)
        if not isinstance(ids, list) or not ids:
            raise context.HTTPException(422, 'Select at least one monster')
        try:
            rows = await asyncio.to_thread(resolve_selected_sources, context,
                copy.deepcopy(context.STATE['monsters']), ids, choices=choices)
        except ValueError as exc:
            raise context.HTTPException(422, str(exc)) from exc
        if (review['scope'] != _scope(context) or review['state'] != context.STATE
                or review['display'] != context.CONFIG.get('display')):
            raise context.HTTPException(409, 'Encounter changed while resolving sources')
        if time.monotonic() >= review['expires']:
            raise context.HTTPException(410, 'Review expired while resolving sources')
        review.update(ids=list(ids), choices=copy.deepcopy(choices), rows=rows)
        store = _store(context)
        for key in list(store):
            if time.monotonic() >= store[key]['expires']:
                del store[key]
        if previous is not None:
            store.pop(previous, None)
        while len(store) >= MAX_REVIEWS:
            store.pop(next(iter(store)))
        token = secrets.token_urlsafe(32)
        store[token] = review
        return _public(token, review)

    async def apply_monster_refresh(body: dict = Body(...)):
        if set(body) != {'review_id', 'selected'} or not isinstance(body['selected'], dict):
            raise context.HTTPException(422, 'Expected review_id and selected field lists')
        review = _review(context, body['review_id'])
        selected = body['selected']
        rows = {row['id']: row for row in review['rows']}
        if set(selected) - set(review['ids']):
            raise context.HTTPException(422, 'Apply is limited to the original selection')
        for ident, fields in selected.items():
            if (not isinstance(fields, list) or any(not isinstance(field, str) for field in fields)
                    or len(fields) != len(set(fields)) or set(fields) - ALLOWED):
                raise context.HTTPException(422, 'Invalid field selection')
            for field in fields:
                proposal = rows[ident].get('fields', {}).get(field, {})
                if proposal.get('status') != 'available' or proposal.get('enabled') is not True:
                    raise context.HTTPException(422, 'Unavailable fields cannot be applied')
        if not any(selected.values()):
            raise context.HTTPException(422, 'Select at least one available field')
        # Consume before rolling or mutation. Failed applies require a fresh review.
        _store(context).pop(body['review_id'])
        working = copy.deepcopy(context.STATE)
        by_id = {item['id']: item for item in working['monsters']}
        changed_order = None
        try:
            for ident, fields in selected.items():
                if not fields:
                    continue
                item = by_id[ident]
                before = copy.deepcopy(item)
                row = rows[ident]
                values = {field: row['fields'][field]['proposed'] for field in fields}
                if 'hp' in values or 'max_hp' in values:
                    expressions = [values[field] for field in ('hp', 'max_hp') if field in values]
                    if len(set(expressions)) != 1:
                        raise ValueError('Conflicting HP proposals')
                    hp = context.hp_value_factory(expressions[0], '')()
                    if type(hp) is not int or not 0 <= hp <= MAX_STORED_HP:
                        raise ValueError('Generated HP is outside storage range')
                    for field in ('hp', 'max_hp'):
                        if field in values:
                            values[field] = hp
                bonus = values.pop('initiative_bonus', None)
                item.update(values)
                legacy_max_edit(item, values)
                if bonus is not None:
                    item.update(initiative_patch(item, bonus=bonus, origin='source'))
                if 'hp' in values or 'max_hp' in values:
                    sync_health(item)
                    expected_hp = values.get('hp', before['hp'])
                    if item['hp'] != expected_hp:
                        raise ValueError('Health reconciliation would alter unchecked or requested HP')
                for field in FIELDS:
                    item.pop(field, None)
                item.update(row['source_fields'])
                if item.get('initiative') != before.get('initiative'):
                    changed_order = ident
            if changed_order is not None:
                working['battle_order'] = order_for_monster_change(working, changed_order, by_id[changed_order])
        except ValueError as exc:
            raise context.HTTPException(409, str(exc)) from exc
        context.STATE = working
        await context.combatants_changed(monsters=True, characters=False)
        return dict(applied={ident: fields for ident, fields in selected.items() if fields})

    dependencies = [Depends(context.require('admin', context.ADMIN_SESSION_COOKIE)), Depends(same_origin)]
    for path, handler, wrapper in (
        ('/api/monsters/refresh/preview', preview_monster_refresh, serialized_handler),
        ('/api/monsters/refresh/apply', apply_monster_refresh, transactional_handler),
    ):
        app.add_api_route(path, wrapper(context, handler, role='admin',
            cookie_name=context.ADMIN_SESSION_COOKIE), methods=['POST'], dependencies=dependencies)
