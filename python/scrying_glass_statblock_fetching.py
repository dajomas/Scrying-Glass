"""Shared, bounded provider fetching for statblock discovery and preparation (022.08).

One SharedFetcher serves the whole application:

- at most ``outbound_requests`` requests at once, and ``provider_requests`` per
  provider (both are semaphores waited on only until the caller's deadline);
- identical in-flight requests are fetched once; every consumer waits only
  until its own deadline. A leader that stops for its own deadline or
  cancellation does not fail the others: a waiting consumer with time left
  takes over the request;
- successful responses are kept in one LRU (``cache_entries``/``cache_bytes``,
  ``cache_seconds``). Failures and oversized or truncated responses are never
  cached; a failed exact request is refused for ``failure_cooldown_seconds``
  with its retry time, never reported as an empty result;
- the same LRU holds converted snapshots under separate keys that include the
  adapter version, provider configuration and limits, so changing any of them
  never reuses an older conversion.

Callers pass ``fn(deadline) -> bytes`` raising an exception with a ``code``
attribute (SourceError/FetchError). Run outside the event loop and the
database lock.
"""
from __future__ import annotations

import threading
import time
from collections import OrderedDict

NOT_COOLED = frozenset(('deadline', 'cancelled'))


class FetchFailure(Exception):
    """Sanitized failure: code and, for a cooldown, the monotonic retry time."""

    def __init__(self, code, retry_at=None):
        self.code, self.retry_at = code, retry_at
        super().__init__(code)


class _Flight:
    __slots__ = ('event', 'data', 'code')

    def __init__(self):
        self.event = threading.Event()
        self.data = None
        self.code = None


class SharedFetcher:
    def __init__(self, limits, *, clock=time.monotonic):
        self.limits, self.clock = limits, clock
        self._lock = threading.Lock()
        self._cache = OrderedDict()  # key -> (stored_at, value, size)
        self._size = 0
        self._flights = {}
        self._cooldown = {}
        self._global = threading.BoundedSemaphore(limits.outbound_requests)
        self._providers = {}
        self.requests = 0  # completed network requests, for tests and diagnostics

    # -- cache ---------------------------------------------------------------
    def _get(self, key, now):
        hit = self._cache.get(key)
        if hit is None:
            return None
        if now - hit[0] >= self.limits.cache_seconds:
            self._drop(key)
            return None
        self._cache.move_to_end(key)
        return hit[1]

    def _drop(self, key):
        old = self._cache.pop(key, None)
        if old is not None:
            self._size -= old[2]

    def _put(self, key, value, size, now):
        if size > self.limits.cache_bytes:
            return
        self._drop(key)
        self._cache[key] = (now, value, size)
        self._size += size
        while len(self._cache) > self.limits.cache_entries or self._size > self.limits.cache_bytes:
            evicted, _ = next(iter(self._cache.items()))
            self._drop(evicted)

    def cached_conversion(self, key):
        with self._lock:
            return self._get(('conversion',) + tuple(key), self.clock())

    def store_conversion(self, key, value, size):
        with self._lock:
            self._put(('conversion',) + tuple(key), value, size, self.clock())

    def cache_stats(self):
        with self._lock:
            return {'entries': len(self._cache), 'bytes': self._size}

    # -- requests ------------------------------------------------------------
    def _semaphore(self, provider):
        with self._lock:
            semaphore = self._providers.get(provider)
            if semaphore is None:
                semaphore = self._providers[provider] = threading.BoundedSemaphore(self.limits.provider_requests)
            return semaphore

    def _acquire(self, semaphore, deadline, cancelled):
        while True:
            if cancelled():
                raise FetchFailure('cancelled')
            remaining = deadline - self.clock()
            if remaining <= 0:
                raise FetchFailure('deadline')
            if semaphore.acquire(timeout=min(remaining, 0.05)):
                return

    def fetch(self, provider, key, fn, *, deadline, cancelled=lambda: False):
        cache_key = ('response', provider, key)
        while True:
            now = self.clock()
            with self._lock:
                hit = self._get(cache_key, now)
                if hit is not None:
                    return hit
                cooling = self._cooldown.get(cache_key)
                if cooling is not None:
                    if cooling[0] > now:
                        raise FetchFailure('cooldown', cooling[0])
                    del self._cooldown[cache_key]
                flight = self._flights.get(cache_key)
                leader = flight is None
                if leader:
                    flight = self._flights[cache_key] = _Flight()
            if not leader:
                while not flight.event.wait(timeout=0.05):
                    if cancelled():
                        raise FetchFailure('cancelled')
                    if self.clock() >= deadline:
                        raise FetchFailure('deadline')
                if flight.code is None:
                    return flight.data
                if flight.code in NOT_COOLED:
                    continue  # that consumer's own deadline/cancellation; try ourselves
                raise FetchFailure(flight.code)
            return self._lead(provider, cache_key, flight, fn, deadline, cancelled)

    def _lead(self, provider, cache_key, flight, fn, deadline, cancelled):
        acquired = []
        try:
            for semaphore in (self._global, self._semaphore(provider)):
                self._acquire(semaphore, deadline, cancelled)
                acquired.append(semaphore)
            try:
                data = fn(deadline)
            except FetchFailure:
                raise
            except Exception as exc:
                code = getattr(exc, 'code', None) or (str(exc) if str(exc).isidentifier() else 'provider_error')
                raise FetchFailure(code) from None
            if type(data) is not bytes or len(data) > self.limits.response_bytes:
                raise FetchFailure('response_bytes_limit')
            if self.clock() >= deadline:
                raise FetchFailure('deadline')
            flight.data = data
            with self._lock:
                self.requests += 1
                self._put(cache_key, data, len(data), self.clock())
            return data
        except FetchFailure as exc:
            flight.code = exc.code
            if exc.code not in NOT_COOLED and exc.code != 'cooldown':
                with self._lock:
                    self._cooldown[cache_key] = (self.clock() + self.limits.failure_cooldown_seconds, exc.code)
            raise
        finally:
            if flight.code is None and flight.data is None:
                flight.code = 'cancelled'  # interrupted leader: waiting consumers retry themselves
            for semaphore in reversed(acquired):
                semaphore.release()
            with self._lock:
                if self._flights.get(cache_key) is flight:
                    del self._flights[cache_key]
            flight.event.set()
