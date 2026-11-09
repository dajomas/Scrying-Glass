"""Connection metadata scoped to the active authorized campaign, never all viewers."""
import time
from .scrying_glass_campaign_ownership import actor, ownership
from .scrying_glass_campaign_viewers import viewers


def campaign_display_status(context, revision):
    try:
        campaign = context.active_campaign()
        if campaign is None:
            return {'displays': [], 'display_scope_available': False}
        user = actor(context)
        if user is not None:
            ownership(context).require(campaign, user)
    except context.HTTPException:
        return {'displays': [], 'display_scope_available': False}
    campaign = str(campaign)
    service = viewers(context)
    result = []
    for socket, data in list(context.features.displays.items()):
        if socket not in context.SOCKETS:
            continue
        session = context.auth_session(socket.cookies.get(context.CLIENT_SESSION_COOKIE, ''))
        if not session:
            continue
        try:
            choices = service.choices(session)
        except context.HTTPException:
            continue
        permitted = {item['id'] for item in choices}
        selected = socket.query_params.get('campaign_id')
        if selected is None and len(choices) == 1:
            selected = choices[0]['id']
        if selected != campaign or selected not in permitted:
            continue
        status = 'stale' if time.time() - data['seen'] > 35 else (
            'live' if data['revision'] == revision else 'behind')
        result.append({'username': session['username'], 'revision': data['revision'],
                       'last_seen': data['seen'], 'status': status})
    return {'displays': result, 'display_scope_available': True, 'display_campaign_id': campaign}
