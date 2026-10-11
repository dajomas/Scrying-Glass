import asyncio
from html.parser import HTMLParser
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit
from python.scrying_glass_asset_cache import cache_bust_html, AssetCacheBustingMiddleware

class URLs(HTMLParser):
    def __init__(self, source):
        super().__init__(); self.values=[]; self.feed(source)
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag=='script' and attrs.get('src'): self.values.append(attrs['src'])
        if tag=='link' and attrs.get('href'): self.values.append(attrs['href'])

async def response(body, content_type=b'text/html; charset=utf-8', method='GET', headers=None, status=200):
    async def app(scope, receive, send):
        await send({'type':'http.response.start','status':status,'headers':headers or [(b'content-type',content_type),(b'content-length',str(len(body)).encode())]})
        midpoint=len(body)//2
        await send({'type':'http.response.body','body':body[:midpoint],'more_body':True})
        await send({'type':'http.response.body','body':body[midpoint:],'more_body':False})
    sent=[]
    async def send(message): sent.append(message)
    async def receive(): return {'type':'http.request','body':b''}
    await AssetCacheBustingMiddleware(app)({'type':'http','method':method},receive,send)
    return sent

class CacheBustingTests(unittest.TestCase):
    def test_shared_token(self):
        html='<link rel="stylesheet" href="/static/admin.css"><script src="/static/admin.js" defer></script>'
        urls=URLs(cache_bust_html(html,'one')).values
        self.assertEqual(urls,['/static/admin.css?_cb=one','/static/admin.js?_cb=one'])

    def test_fresh_token_per_render(self):
        html='<script src="/static/admin.js"></script>'
        with patch('python.scrying_glass_asset_cache.secrets.token_hex',side_effect=['one','two']):
            self.assertNotEqual(cache_bust_html(html),cache_bust_html(html))

    def test_query_fragment_and_replacement(self):
        html='<script src="/static/a.js?x=1&amp;_cb=old&amp;empty=#point"></script>'
        url=URLs(cache_bust_html(html,'new')).values[0]; parts=urlsplit(url)
        self.assertEqual(parse_qs(parts.query,keep_blank_values=True),{'x':['1'],'empty':[''],'_cb':['new']})
        self.assertEqual(parts.fragment,'point')

    def test_external_and_media_unchanged(self):
        html='<script src="https://x/a.js"></script><script src="//x/a.js"></script><link rel="stylesheet" href="/media/a.css"><img src="/static/a.png"><link rel="icon" href="/static/a.css">'
        self.assertEqual(cache_bust_html(html,'new'),html)

    def test_inline_script_and_comments_unchanged(self):
        html='<!-- <script src="/static/a.js"></script> --><script>const s=\'<script src="/static/b.js">\';</script>'
        self.assertEqual(cache_bust_html(html,'new'),html)

    def test_quotes_unquoted_and_case(self):
        html="<LINK REL='stylesheet' HREF='/static/a.css'/><script src=/static/a.js defer></script>"
        self.assertEqual(URLs(cache_bust_html(html,'x')).values,['/static/a.css?_cb=x','/static/a.js?_cb=x'])

    def test_script_attribute_preserved(self):
        html='<script nonce="abc" data-src="fake" src="/static/a.js" defer></script>'
        output=cache_bust_html(html,'x')
        self.assertIn('data-src="fake"',output);self.assertIn('nonce="abc"',output);self.assertIn(' defer',output)

    def test_html_response_headers_and_length(self):
        body='<script src="/static/a.js"></script> café'.encode()
        headers=[(b'content-type',b'text/html; charset=utf-8'),(b'cache-control',b'max-age=99'),(b'etag',b'old'),(b'last-modified',b'old'),(b'set-cookie',b'a=1')]
        sent=asyncio.run(response(body,headers=headers));h=dict(sent[0]['headers']);b=sent[1]['body']
        self.assertEqual(h[b'cache-control'],b'no-cache');self.assertNotIn(b'etag',h);self.assertNotIn(b'last-modified',h)
        self.assertEqual(h[b'set-cookie'],b'a=1');self.assertEqual(int(h[b'content-length']),len(b));self.assertIn(b'_cb=',b)

    def test_json_passthrough(self):
        sent=asyncio.run(response(b'{"ok":true}',b'application/json'))
        self.assertEqual(len(sent),3);self.assertNotIn(b'cache-control',dict(sent[0]['headers']))
        self.assertEqual(b''.join(x['body'] for x in sent[1:]),b'{"ok":true}')

    def test_static_css_passthrough(self):
        sent=asyncio.run(response(b'body {}',b'text/css'))
        self.assertEqual(b''.join(x['body'] for x in sent[1:]),b'body {}')

    def test_head_passthrough(self):
        sent=asyncio.run(response(b'',method='HEAD'))
        self.assertEqual(len(sent),3);self.assertEqual(dict(sent[0]['headers'])[b'cache-control'],b'no-cache')

    def test_websocket_passthrough(self):
        called=[]
        async def app(scope,receive,send): called.append(scope['type'])
        asyncio.run(AssetCacheBustingMiddleware(app)({'type':'websocket'},None,None))
        self.assertEqual(called,['websocket'])

    def test_error_page_includes(self):
        sent=asyncio.run(response(b'<link rel="stylesheet" href="/static/login.css">',status=403))
        self.assertEqual(sent[0]['status'],403);self.assertIn(b'_cb=',sent[1]['body'])

    def test_empty_html(self):
        sent=asyncio.run(response(b''));self.assertEqual(sent[1]['body'],b'')

if __name__=='__main__': unittest.main()
