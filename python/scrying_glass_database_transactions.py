"""Serialize mutations, roll back state, and broadcast only committed changes."""
from __future__ import annotations
import asyncio
import copy
from functools import wraps

def transactional_handler(context, handler):
    @wraps(handler)
    async def wrapped(*args, **kwargs):
        lock = getattr(context,"_database_operation_lock",None)
        if lock is None:
            lock=asyncio.Lock()
            context._database_operation_lock=lock
        async with lock:
            original=copy.deepcopy(context.STATE)
            context._defer_database_broadcast=True
            context._database_broadcast_pending=False
            try:
                with context.STORAGE.transaction():
                    result=await handler(*args,**kwargs)
                pending=context._database_broadcast_pending
            except BaseException:
                context.STATE=original
                raise
            finally:
                context._defer_database_broadcast=False
                context._database_broadcast_pending=False
            if pending:
                await context.broadcast()
            return result
    return wrapped
