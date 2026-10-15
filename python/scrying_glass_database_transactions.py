"""Serialize mutations, roll back state, and broadcast only committed changes."""
from __future__ import annotations
import asyncio
import copy
import inspect
from functools import wraps
from .scrying_glass_campaign_ownership import ownership_request, admin_state, actor, ownership
from .scrying_glass_health_limits import HpStorageRangeError
from .scrying_glass_identity_rules import ParticipantIdentityConflict
from .scrying_glass_initiative_gate import validate_initiative_request, validate_initiative_transition


def operation_lock(context):
    lock = getattr(context, "_database_operation_lock", None)
    if lock is None:
        lock = asyncio.Lock()
        context._database_operation_lock = lock
    return lock


def serialized_handler(context, handler, *, role=None, cookie_name=None):
    @wraps(handler)
    async def wrapped(*args, **kwargs):
        request = kwargs.pop("_operation_request", None)
        async with operation_lock(context):
            # Resolve the actor only after waiting for the serialized operation lock.
            session = None
            if request is not None and role is not None:
                session = await context.require(role, cookie_name)(request)
            with ownership_request(context, session, handler, args, kwargs, request):
                result = handler(*args, **kwargs)
                if inspect.isawaitable(result):
                    result = await result
                if handler.__name__ == 'feature_summary' and actor(context) and actor(context)['role'] == 'admin' and isinstance(result, dict):
                    result['displays'] = []
                if handler.__name__ == 'admin_get_state':
                    result = admin_state(context, result)
                return copy.deepcopy(result) if isinstance(result, (dict, list)) else result

    if role is not None:
        from fastapi import Request
        signature = inspect.signature(handler)
        wrapped.__signature__ = signature.replace(parameters=[
            *signature.parameters.values(),
            inspect.Parameter("_operation_request", inspect.Parameter.KEYWORD_ONLY,
                              annotation=Request),
        ])
    return wrapped


def transactional_handler(context, handler, *, role=None, cookie_name=None):
    @wraps(handler)
    async def transaction(*args, **kwargs):
        original = copy.deepcopy(context.STATE)
        features = getattr(context, 'features', None)
        campaign_before = context.active_campaign() if features else None
        context._bundle_files = []
        context._defer_database_broadcast = True
        context._database_broadcast_pending = False
        try:
            with context.STORAGE.transaction():
                existing_campaigns = ownership(context).ids() if actor(context) is not None else None
                validate_initiative_request(context, handler, args, kwargs)
                result = await handler(*args, **kwargs)
                validate_initiative_transition(context, original, handler.__name__)
                if existing_campaigns is not None:
                    for campaign_id in ownership(context).ids() - existing_campaigns:
                        ownership(context).assign_created(campaign_id)
                if features:
                    features.reconcile()
                    if context.STATE != original:
                        context.save_active_campaign_characters()
                        context.save_active_setup_monsters()
                        context.save_state()
                    features.after_transaction(handler.__name__,original,campaign_before)
            pending = context._database_broadcast_pending
        except BaseException as exc:
            context.STATE = original
            for path in getattr(context,'_bundle_files',[]):
                try: path.unlink(missing_ok=True)
                except OSError: pass
            if isinstance(exc, HpStorageRangeError):
                raise context.HTTPException(422, str(exc)) from exc
            if isinstance(exc, ParticipantIdentityConflict):
                raise context.HTTPException(409, str(exc)) from exc
            raise
        finally:
            context._bundle_files = []
            context._defer_database_broadcast = False
            context._database_broadcast_pending = False
        if pending:
            await context.broadcast()
        return result
    return serialized_handler(context, transaction, role=role, cookie_name=cookie_name)

