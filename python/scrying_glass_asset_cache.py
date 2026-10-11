"""Per-response cache busting for local CSS/JS includes in HTML pages."""
from html import escape
from html.parser import HTMLParser
import re
import secrets
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

CACHE_PARAMETER = "_cb"


def version_asset_url(url: str, token: str) -> str:
    parts = urlsplit(url)
    query = [(key, value) for key, value in parse_qsl(parts.query, keep_blank_values=True)
             if key != CACHE_PARAMETER]
    query.append((CACHE_PARAMETER, token))
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


class _AssetIncludes(HTMLParser):
    def __init__(self, source: str, token: str):
        super().__init__(convert_charrefs=False)
        self.source = source
        self.token = token
        self.edits = []
        self.offsets = [0]
        for match in re.finditer("\n", source):
            self.offsets.append(match.end())

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "script":
            attribute, extension = "src", ".js"
        elif tag == "link" and "stylesheet" in (attributes.get("rel") or "").lower().split():
            attribute, extension = "href", ".css"
        else:
            return
        url = attributes.get(attribute)
        if not url:
            return
        parts = urlsplit(url)
        if parts.scheme or parts.netloc or not parts.path.startswith("/static/"):
            return
        if not parts.path.lower().endswith(extension):
            return
        raw = self.get_starttag_text()
        pattern = re.compile(r"(?<![\w:-])" + attribute +
                             r"\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s>]+)", re.I)
        match = pattern.search(raw)
        if not match:
            return
        replacement = attribute + '="' + escape(version_asset_url(url, self.token), quote=True) + '"'
        line, column = self.getpos()
        offset = self.offsets[line - 1] + column
        self.edits.append((offset + match.start(), offset + match.end(), replacement))

    handle_startendtag = handle_starttag


def cache_bust_html(source: str, token: str | None = None) -> str:
    """Use one fresh token per render without changing scripts or other markup."""
    parser = _AssetIncludes(source, secrets.token_hex(16) if token is None else token)
    parser.feed(source)
    parser.close()
    for start, end, replacement in reversed(parser.edits):
        source = source[:start] + replacement + source[end:]
    return source


class AssetCacheBustingMiddleware:
    """Transform UTF-8 HTML only; pass API, assets, streams and sockets through."""
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        start = None
        chunks = []
        transform = False

        async def send_response(message):
            nonlocal start, transform
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                lookup = {key.lower(): value for key, value in headers}
                content_type = lookup.get(b"content-type", b"").lower()
                is_html = content_type.split(b";", 1)[0].strip() == b"text/html"
                if is_html:
                    headers = [(key, value) for key, value in headers
                               if key.lower() not in {b"cache-control", b"etag", b"last-modified", b"expires"}]
                    headers.append((b"cache-control", b"no-cache"))
                start = dict(message, headers=headers)
                transform = (is_html and scope.get("method", "GET") != "HEAD"
                             and message["status"] not in {204, 304}
                             and b"content-encoding" not in lookup
                             and not message.get("trailers", False))
                if not transform:
                    await send(start)
            elif message["type"] == "http.response.body" and transform:
                chunks.append(message.get("body", b""))
                if not message.get("more_body", False):
                    original = b"".join(chunks)
                    try:
                        body = cache_bust_html(original.decode("utf-8")).encode("utf-8")
                    except UnicodeDecodeError:
                        body = original
                    headers = [(key, value) for key, value in start["headers"]
                               if key.lower() != b"content-length"]
                    headers.append((b"content-length", str(len(body)).encode("ascii")))
                    await send(dict(start, headers=headers))
                    await send({"type": "http.response.body", "body": body, "more_body": False})
            else:
                await send(message)

        await self.app(scope, receive, send_response)
