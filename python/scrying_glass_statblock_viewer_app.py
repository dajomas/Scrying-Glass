"""The protected statblock listener (SG-TODO-022.09, default port 3200).

A third FastAPI application with its own session cookie. Only a regular admin
can sign in; every page, read API and WebSocket frame additionally requires a
live session and assignment to the active campaign (superadmin-only and Client
Display accounts are refused). Routes: GET / (page), GET/POST /login,
POST /logout, GET /api/statblocks/state, GET /api/statblocks/monsters/{id},
WebSocket /ws. Imports (discover/prepare/apply) stay on the Admin app.
"""
from fastapi import FastAPI, Form, Request, WebSocket


def install_statblock_viewer(context, app: FastAPI):
    cookie = context.STATBLOCK_SESSION_COOKIE

    async def statblock_home(request: Request):
        from .scrying_glass_statblock_contract import StatblockAPIError
        from .scrying_glass_statblock_service import statblock_service
        try:
            statblock_service(context).authorize(request.cookies.get(cookie, ''))
        except StatblockAPIError as exc:
            if exc.status == 401:
                return context.RedirectResponse('/login', 303)
            # Signed in but not permitted (superadmin, other campaign, no campaign): no content.
            return _status(context.login(exc.message), exc.status)
        from web_html.statblock_html import STATBLOCK_HTML
        return context.HTMLResponse(STATBLOCK_HTML)

    def statblock_login_get():
        return context.login()

    async def statblock_login_post(username: str = Form(...), password: str = Form(...)):
        user = context.user(username)
        if not user or not context.password_ok(password, str(user.get('password', ''))):
            return context.login('Invalid credentials')
        if user.get('role') != 'admin':
            return context.login('Statblocks need a regular admin account assigned to the campaign')
        token = context.secrets.token_urlsafe(32)
        context.SESSIONS[token] = {'username': username, 'role': user['role']}
        response = context.RedirectResponse('/', 303)
        response.set_cookie(cookie, token, httponly=True, samesite='strict', secure=False)
        return response

    async def ws(websocket: WebSocket):
        from .scrying_glass_statblock_transport import statblock_socket
        await statblock_socket(context, websocket, cookie)

    app.add_api_route('/', statblock_home, methods=['GET'], include_in_schema=False)
    app.add_api_route('/login', statblock_login_get, methods=['GET'])
    app.add_api_route('/login', statblock_login_post, methods=['POST'])
    app.add_api_websocket_route('/ws', ws)
    from .scrying_glass_statblock_routes import install_statblock_routes
    install_statblock_routes(context, app, cookie=cookie, writes=False)
    from .scrying_glass_logout import install_logout
    install_logout(context, app, cookie)


def _status(response, status):
    response.status_code = status
    return response
