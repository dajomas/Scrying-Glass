"""Admin-port-only feature routes; guarded, serialized and transactional."""
from fastapi import Body,Depends,File,UploadFile
from fastapi.responses import Response
from .scrying_glass_database_transactions import serialized_handler,transactional_handler
from .scrying_glass_request_security import same_origin

def install_feature_routes(context,app):
    guard=Depends(context.require('admin',context.ADMIN_SESSION_COOKIE))
    def route(path,handler,method='GET'):
        mutation=method!='GET'
        wrapper=transactional_handler if mutation else serialized_handler
        app.add_api_route(path,wrapper(context,handler,role='admin',cookie_name=context.ADMIN_SESSION_COOKIE),methods=[method],dependencies=[guard]+([Depends(same_origin)] if mutation else []))
    async def feature_summary(): return context.features.summary()
    async def undo(body:dict=Body(...)): return await context.features.undo(body)
    async def edit_features(ident:str,body:dict=Body(...)): return await context.features.edit_features(ident,body)
    async def add_effect(ident:str,body:dict=Body(...)): return await context.features.add_effect(ident,body)
    async def remove_effect(ident:str,effect_id:str): return await context.features.remove_effect(ident,effect_id)
    async def end_concentration(ident:str): return await context.features.end_concentration(ident)
    async def save_checkpoint(body:dict=Body(...)): return await context.features.save_checkpoint(body)
    async def preview_checkpoint(ident:int): return context.features.preview_checkpoint(ident)
    async def restore_checkpoint(ident:int,body:dict=Body(...)): return await context.features.restore_checkpoint(ident,body)
    async def delete_checkpoint(ident:int): return await context.features.delete_checkpoint(ident)
    async def export_bundle(): return Response(context.features.export_bundle(),media_type='application/zip',headers={'Content-Disposition':'attachment; filename="scrying-glass-campaign.zip"','Cache-Control':'no-store'})
    async def import_bundle(file:UploadFile=File(...)): return await context.features.import_bundle(await file.read(25*1024*1024+1))
    for path,handler,method in [('/api/features',feature_summary,'GET'),('/api/battle/undo',undo,'POST'),('/api/combatants/{ident}/features',edit_features,'PATCH'),('/api/combatants/{ident}/effects',add_effect,'POST'),('/api/combatants/{ident}/effects/{effect_id}',remove_effect,'DELETE'),('/api/combatants/{ident}/concentration/end',end_concentration,'POST'),('/api/checkpoints',save_checkpoint,'POST'),('/api/checkpoints/{ident}',preview_checkpoint,'GET'),('/api/checkpoints/{ident}/restore',restore_checkpoint,'POST'),('/api/checkpoints/{ident}',delete_checkpoint,'DELETE'),('/api/campaign-bundle',export_bundle,'GET'),('/api/campaign-bundle',import_bundle,'POST')]: route(path,handler,method)
