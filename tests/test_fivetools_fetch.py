"""022.04e dataset fetching: allowlist, HTTPS root, size/redirect bounds and cache."""
import io
import time
import unittest

from python.scrying_glass_fivetools_fetch import (
    CachingFetcher, FetchError, HttpsFetcher, allowed_dataset_path, data_root_from_display,
)


class Response(io.BytesIO):
    def __init__(self, data, url, encoding=None):
        super().__init__(data)
        self._url, self.headers = url, {'Content-Encoding': encoding} if encoding else {}

    def geturl(self):
        return self._url


class Opener:
    def __init__(self, data=b'{}', final=None, encoding=None):
        self.data, self.final, self.encoding, self.urls = data, final, encoding, []

    def __call__(self, redirects):
        return self

    def open(self, request, timeout):
        self.urls.append(request.full_url)
        return Response(self.data, self.final or request.full_url, self.encoding)


class FetchTests(unittest.TestCase):
    def test_allowlist(self):
        for path in ('bestiary/index.json', 'bestiary/bestiary-xmm.json', 'spells/spells-xphb.json', 'items.json',
                     'generated/gendata-variantrules.json'):
            self.assertTrue(allowed_dataset_path(path), path)
        for path in ('../secret', 'bestiary/../items.json', 'bestiary/bestiary-XMM.json', 'spells/other.json',
                     'https://evil/items.json', 'items.json?x', None, 'bestiary/fluff-bestiary-mm.json'):
            self.assertFalse(allowed_dataset_path(path), path)

    def test_data_root(self):
        self.assertEqual(data_root_from_display({}), 'https://5e.tools/data')
        self.assertEqual(data_root_from_display({'fivetools_data_base_url': 'https://mirror.example/x/data/bestiary/'}),
                         'https://mirror.example/x/data')
        for root in ('http://5e.tools/data/bestiary', 'https://user:pw@h/data/bestiary', 'https://h/data/bestiary?q=1'):
            with self.assertRaises(FetchError):
                data_root_from_display({'fivetools_data_base_url': root})

    def test_https_fetcher_bounds(self):
        opener = Opener(b'x' * 10)
        fetcher = HttpsFetcher('https://h.example/data', response_bytes=10, opener_factory=opener)
        self.assertEqual(fetcher('items.json', deadline=time.monotonic() + 5), b'x' * 10)
        self.assertEqual(opener.urls, ['https://h.example/data/items.json'])
        for opener, code in ((Opener(b'x' * 11), 'response_bytes_limit'), (Opener(final='https://other.example/x'), 'unsafe_redirect'),
                             (Opener(encoding='gzip'), 'unsupported_content_encoding')):
            with self.subTest(code=code):
                with self.assertRaises(FetchError) as caught:
                    HttpsFetcher('https://h.example/data', response_bytes=10, opener_factory=opener)('items.json', deadline=time.monotonic() + 5)
                self.assertEqual(str(caught.exception), code)
        with self.assertRaises(FetchError):
            fetcher('../etc/passwd', deadline=time.monotonic() + 5)
        with self.assertRaises(FetchError):
            fetcher('items.json', deadline=time.monotonic() - 1)

    def test_cache_keeps_successes_only(self):
        calls = []
        def fetch(path, deadline):
            calls.append(path)
            if path == 'bad':
                raise FetchError('provider_unavailable')
            return path.encode() * 10
        clock = [0.0]
        cache = CachingFetcher(fetch, entries=2, max_bytes=100, seconds=10, clock=lambda: clock[0])
        for path in ('a', 'a', 'b', 'c', 'a'):
            cache(path, deadline=1)
        self.assertEqual(calls, ['a', 'b', 'c', 'a'])
        for _ in range(2):
            with self.assertRaises(FetchError):
                cache('bad', deadline=1)
        self.assertEqual(calls.count('bad'), 2)
        clock[0] = 20
        cache('a', deadline=1)
        self.assertEqual(calls.count('a'), 3)


if __name__ == '__main__':
    unittest.main()
