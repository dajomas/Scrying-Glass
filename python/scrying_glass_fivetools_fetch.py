"""Bounded 5e.tools dataset fetching for statblock preparation (022.04e).

Only dataset paths verified against the pinned runtime's loaders
(5etools-src 32ef600, DataUtil in js/utils.js) can be requested, relative to
one configured HTTPS data root. Responses are size-limited while reading,
redirects stay on the same HTTPS host (at most three), and failures are never
cached. Network work belongs outside the database lock and the isolated
preparation worker, which asks its parent for files through
``allowed_dataset_path``.
"""
from __future__ import annotations

import re
import threading
import time
from collections import OrderedDict
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, HTTPSHandler, Request, build_opener

FIXED_PATHS = frozenset((
    'bestiary/index.json', 'bestiary/template.json', 'bestiary/legendarygroups.json',
    'spells/index.json', 'conditionsdiseases.json', 'items.json', 'items-base.json',
    'skills.json', 'senses.json', 'actions.json', 'variantrules.json', 'magicvariants.json',
    'generated/gendata-variantrules.json',
))
_INDEXED = re.compile(r'(?:bestiary/bestiary|spells/spells)-[a-z0-9][a-z0-9-]{0,63}\.json\Z')
MAX_REDIRECTS = 3


class FetchError(ValueError):
    """Sanitized fetch failure; the code never includes remote content."""


def allowed_dataset_path(path):
    return type(path) is str and (path in FIXED_PATHS or bool(_INDEXED.match(path)))


def data_root_from_display(display):
    """The configured data root: parent of fivetools_data_base_url (/bestiary)."""
    bestiary = str(display.get('fivetools_data_base_url', 'https://5e.tools/data/bestiary')).rstrip('/')
    root = bestiary[:-len('/bestiary')] if bestiary.endswith('/bestiary') else bestiary
    return validated_root(root)


def validated_root(root):
    parts = urlsplit(root)
    if (parts.scheme != 'https' or not parts.hostname or parts.username or parts.password
            or parts.query or parts.fragment or any(c.isspace() for c in root)):
        raise FetchError('invalid_data_root')
    return root.rstrip('/')


class _SameHostRedirects(HTTPRedirectHandler):
    def __init__(self, host):
        super().__init__()
        self.host, self.count = host, 0

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.count += 1
        target = urlsplit(newurl)
        if self.count > MAX_REDIRECTS or target.scheme != 'https' or target.hostname != self.host:
            raise FetchError('unsafe_redirect')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class HttpsFetcher:
    """fetch(path) -> bytes against one data root, bounded per response."""

    def __init__(self, root, *, response_bytes=10485760, opener_factory=None):
        self.root = validated_root(root)
        self.host = urlsplit(self.root).hostname
        self.response_bytes = response_bytes
        self._opener_factory = opener_factory

    def __call__(self, path, *, deadline):
        if not allowed_dataset_path(path):
            raise FetchError('dataset_path_not_allowed')
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise FetchError('deadline')
        redirects = _SameHostRedirects(self.host)
        opener = self._opener_factory(redirects) if self._opener_factory else build_opener(HTTPSHandler(), redirects)
        request = Request(f'{self.root}/{path}', headers={'User-Agent': 'ScryingGlass/1.0', 'Accept': 'application/json',
                                                          'Accept-Encoding': 'identity'})
        try:
            with opener.open(request, timeout=max(0.1, min(remaining, 10))) as response:
                if urlsplit(response.geturl()).hostname != self.host:
                    raise FetchError('unsafe_redirect')
                encoding = (response.headers.get('Content-Encoding') or 'identity').lower()
                if encoding not in ('identity', ''):
                    raise FetchError('unsupported_content_encoding')
                chunks, total = [], 0
                while True:
                    if time.monotonic() >= deadline:
                        raise FetchError('deadline')
                    chunk = response.read(65536)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > self.response_bytes:
                        raise FetchError('response_bytes_limit')
                    chunks.append(chunk)
                return b''.join(chunks)
        except FetchError:
            raise
        except HTTPError as exc:
            raise FetchError('not_found' if exc.code == 404 else 'provider_error') from None
        except (URLError, OSError, ValueError) as exc:
            raise FetchError('provider_unavailable') from None


class CachingFetcher:
    """Successful responses only, bounded by entries, bytes and age."""

    def __init__(self, fetch, *, entries=64, max_bytes=67108864, seconds=3600, clock=time.monotonic):
        self._fetch, self._clock = fetch, clock
        self._entries, self._bytes, self._seconds = entries, max_bytes, seconds
        self._cache, self._size, self._lock = OrderedDict(), 0, threading.Lock()

    def __call__(self, path, *, deadline):
        now = self._clock()
        with self._lock:
            hit = self._cache.get(path)
            if hit and now - hit[0] < self._seconds:
                self._cache.move_to_end(path)
                return hit[1]
        data = self._fetch(path, deadline=deadline)
        if len(data) <= self._bytes:
            with self._lock:
                old = self._cache.pop(path, None)
                if old:
                    self._size -= len(old[1])
                self._cache[path] = (now, data)
                self._size += len(data)
                while len(self._cache) > self._entries or self._size > self._bytes:
                    _, (_, evicted) = self._cache.popitem(last=False)
                    self._size -= len(evicted)
        return data
