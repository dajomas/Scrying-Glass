"""Admin-only grant management with lifespan-based ACL initialization."""
from contextlib import asynccontextmanager
from fastapi import APIRouter, Body, Depends
from .scrying_glass_campaign_viewers import viewers
from .scrying_glass_database_transactions import serialized_handler, transactional_handler, operation_lock
from .scrying_glass_request_security import same_origin


def install_campaign_viewers(context, app, *, admin=False):
    @asynccontextmanager
    async def initialize(application):
        async with operation_lock(context):
            viewers(context).initialize()
        yield

    # FastAPI merges included-router lifespans with the application's lifespan.
    # Do not use the removed/deprecated application startup-event helpers.
    app.include_router(APIRouter(lifespan=initialize))
    if not admin:
        return

    async def get_viewers(campaign_id: str):
        return viewers(context).grants(campaign_id)

    async def set_viewers(campaign_id: str, body: dict = Body(...)):
        result = viewers(context).replace(campaign_id, body)
        await context.broadcast()
        return result

    guard = Depends(context.require('admin', context.ADMIN_SESSION_COOKIE))
    app.add_api_route('/api/campaigns/{campaign_id}/viewers',
        serialized_handler(context, get_viewers, role='admin', cookie_name=context.ADMIN_SESSION_COOKIE),
        methods=['GET'], dependencies=[guard])
    app.add_api_route('/api/campaigns/{campaign_id}/viewers',
        transactional_handler(context, set_viewers, role='admin', cookie_name=context.ADMIN_SESSION_COOKIE),
        methods=['PUT'], dependencies=[guard, Depends(same_origin)])
