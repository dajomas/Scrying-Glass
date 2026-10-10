"""Admin-only routes using existing authorization and transaction gates."""
from fastapi import Body,Depends
from .scrying_glass_database_transactions import transactional_handler
from .scrying_glass_request_security import same_origin
from .scrying_glass_service_lairs import LairService

def install_lair_routes(context,app):
    service=LairService(context)
    async def create_lair(body:dict=Body(...)):return await service.create_lair(body)
    async def update_lair(ident:str,body:dict=Body(...)):return await service.update_lair(ident,body)
    async def delete_lair(ident:str):return await service.delete_lair(ident)
    async def apply_lair_action(ident:str,body:dict=Body(...)):return await service.apply_lair_action(ident,body)
    for path,handler,method in (
        ('/api/lairs',create_lair,'POST'),('/api/lairs/{ident}',update_lair,'PATCH'),
        ('/api/lairs/{ident}',delete_lair,'DELETE'),('/api/lairs/{ident}/actions',apply_lair_action,'POST')):
        app.add_api_route(path,transactional_handler(context,handler,role='admin',cookie_name=context.ADMIN_SESSION_COOKIE),
            methods=[method],dependencies=[Depends(context.require('admin',context.ADMIN_SESSION_COOKIE)),Depends(same_origin)])
