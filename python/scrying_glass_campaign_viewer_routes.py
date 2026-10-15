"""Admin-only grant management; initialize additive ACL storage at startup."""
from fastapi import Body, Depends
from .scrying_glass_campaign_viewers import viewers
from .scrying_glass_database_transactions import serialized_handler, transactional_handler, operation_lock
from .scrying_glass_request_security import same_origin

def install_campaign_viewers(context, app, *, admin=False):
    async def initialize():
        async with operation_lock(context): viewers(context).initialize()
    app.add_event_handler('startup', initialize)
    if not admin: return
    async def get_viewers(campaign_id: str):
        return viewers(context).grants(campaign_id)
    async def set_viewers(campaign_id: str, body: dict=Body(...)):
        result=viewers(context).replace(campaign_id,body)
        await context.broadcast()
        return result
    guard=Depends(context.require('admin',context.ADMIN_SESSION_COOKIE))
    app.add_api_route('/api/campaigns/{campaign_id}/viewers',
        serialized_handler(context,get_viewers,role='admin',cookie_name=context.ADMIN_SESSION_COOKIE),
        methods=['GET'],dependencies=[guard])
    app.add_api_route('/api/campaigns/{campaign_id}/viewers',
        transactional_handler(context,set_viewers,role='admin',cookie_name=context.ADMIN_SESSION_COOKIE),
        methods=['PUT'],dependencies=[guard,Depends(same_origin)])
