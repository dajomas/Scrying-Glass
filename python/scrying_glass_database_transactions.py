"""Serialize mutations, roll back state, and broadcast only committed changes."""
from __future__ import annotations
import asyncio
import copy
import inspect
from functools import wraps


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
            # Recheck authorization after waiting for another request.
            if request is not None and role is not None:
                await context.require(role, cookie_name)(request)
            result = handler(*args, **kwargs)
            if inspect.isawaitable(result):
                result = await result
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
        context._defer_database_broadcast = True
        context._database_broadcast_pending = False
        try:
            with context.STORAGE.transaction():
                result = await handler(*args, **kwargs)
            pending = context._database_broadcast_pending
        except BaseException:
            context.STATE = original
            raise
        finally:
            context._defer_database_broadcast = False
            context._database_broadcast_pending = False
        if pending:
            await context.broadcast()
        return result
    return serialized_handler(context, transaction, role=role, cookie_name=cookie_name)

