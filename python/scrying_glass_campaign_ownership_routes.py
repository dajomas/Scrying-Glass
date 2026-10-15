"""Lifespan initialization and superadmin-only ownership endpoints."""
from contextlib import asynccontextmanager
from fastapi import APIRouter, Body, Depends
from .scrying_glass_campaign_ownership import ownership
from .scrying_glass_database_transactions import operation_lock, serialized_handler, transactional_handler
from .scrying_glass_request_security import same_origin

def install_campaign_ownership(context, app, *, admin=False):
    @asynccontextmanager
    async def lifespan(application):
        async with operation_lock(context): ownership(context).initialize()
        yield
    app.include_router(APIRouter(lifespan=lifespan))
    if not admin: return
    async def get_campaign_owners():
        return ownership(context).catalog()
    async def reassign_campaign_owner(campaign_id: str, body: dict=Body(...)):
        result = ownership(context).reassign(campaign_id, body)
        await context.broadcast()
        return result
    guard = Depends(context.require('superadmin', context.ADMIN_SESSION_COOKIE))
    app.add_api_route('/api/campaign-ownership',
        serialized_handler(context, get_campaign_owners, role='superadmin', cookie_name=context.ADMIN_SESSION_COOKIE),
        methods=['GET'], dependencies=[guard])
    app.add_api_route('/api/campaign-ownership/{campaign_id}',
        transactional_handler(context, reassign_campaign_owner, role='superadmin', cookie_name=context.ADMIN_SESSION_COOKIE),
        methods=['PUT'], dependencies=[guard, Depends(same_origin)])
