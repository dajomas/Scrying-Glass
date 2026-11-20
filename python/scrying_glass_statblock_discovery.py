"""Statblock providers: configuration, exact identities and candidate discovery (022.08).

Discovery lists exact-name candidates per enabled provider through the shared
bounded fetcher. A provider that fails, is cooling down or cannot be read
completely reports that status; a failure is never a zero-match result.
Candidate identities are exact and server-held:

| Provider   | Identity                                   |
|------------|--------------------------------------------|
| 5e.tools   | configured data root, record name, source  |
| Open5e     | configured v2 endpoint, creature key       |
| D&D Beyond | canonical public monster path (numeric id) |
| file       | SHA-256 of the uploaded bytes (prepare)    |

The tracker's retained lookup identity (``monster_source_*`` fields) becomes
the "original" candidate without any network request.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from urllib.parse import unquote, urlsplit

from .scrying_glass_statblock_fetching import FetchFailure
from .scrying_glass_statblock_limits import CANDIDATES_PER_PROVIDER
from .scrying_glass_statblock_sources import ProviderFetcher, SourceError, name_key

FIVETOOLS, OPEN5E, DNDBEYOND, FILE = '5e.tools', 'Open5e', 'D&D Beyond', 'file'
ORDER = (DNDBEYOND, FIVETOOLS, OPEN5E)
SWITCHES = {DNDBEYOND: ('dndbeyond_image_lookup', True), FIVETOOLS: ('fivetools_fallback', True),
            OPEN5E: ('open5e_lookup', False)}
SITE_5ETOOLS = 'https://5e.tools'


@dataclass(frozen=True)
class ProviderConfig:
    enabled: dict
    fivetools_root: str | None
    fivetools_sources: tuple
    open5e_base: str | None

    def fingerprint(self, provider):
        if provider == FIVETOOLS:
            return self.fivetools_root or ''
        if provider == OPEN5E:
            return self.open5e_base or ''
        return provider


def provider_config(display):
    """Read switches and endpoints; invalid endpoints disable that provider."""
    from .scrying_glass_fivetools import configured_sources
    from .scrying_glass_fivetools_fetch import FetchError, data_root_from_display
    enabled = {provider: display.get(key, default) is True for provider, (key, default) in SWITCHES.items()}
    try:
        root = data_root_from_display(display)
        sources = tuple(configured_sources(display))
    except (FetchError, ValueError):
        root, sources = None, ()
    try:
        from .scrying_glass_open5e import base_url
        base = base_url(display)
    except ValueError:
        base = None
    return ProviderConfig(enabled, root, sources, base)


def default_transport(limits):
    """(provider, url, deadline) -> bytes over the network, bounded per response."""
    from .scrying_glass_dndbeyond_statblock import HOSTS
    from .scrying_glass_fivetools_fetch import HttpsFetcher
    def transport(provider, url, deadline, root=None):
        if provider == FIVETOOLS:
            return HttpsFetcher(root, response_bytes=limits.response_bytes)(url[len(root) + 1:], deadline=deadline)
        if provider == OPEN5E:
            host = urlsplit(url).hostname
            return ProviderFetcher({host}, response_bytes=limits.response_bytes)(url, deadline=deadline)
        if provider == DNDBEYOND:
            return ProviderFetcher(HOSTS, response_bytes=limits.response_bytes,
                                   accept='text/html,application/xhtml+xml')(url, deadline=deadline)
        raise SourceError('unsafe_url')
    return transport


def hosts(provider, config):
    if provider == OPEN5E and config.open5e_base:
        return frozenset((urlsplit(config.open5e_base).hostname,))
    if provider == DNDBEYOND:
        from .scrying_glass_dndbeyond_statblock import HOSTS
        return HOSTS
    if provider == FIVETOOLS and config.fivetools_root:
        return frozenset((urlsplit(config.fivetools_root).hostname,))
    return frozenset()


def identity_key(provider, identity):
    """Canonical comparison key for an exact identity (never a display name)."""
    if provider == FIVETOOLS:
        return (provider, identity['root'], identity['name'].casefold(), identity['source'].casefold())
    if provider == OPEN5E:
        return (provider, identity['base_url'], identity['key'])
    if provider == DNDBEYOND:
        from .scrying_glass_dndbeyond_statblock import canonical_url
        return (provider, canonical_url(identity['path'])[1])
    return (provider, identity.get('sha256'))


def original_identity(monster, config):
    """Exact identity from the tracker's retained source fields, or None."""
    from .scrying_glass_monster_source_snapshot import NAME, PROVIDER, URL, BOOK
    provider, url = monster.get(PROVIDER), monster.get(URL)
    if type(provider) is not str or type(url) is not str:
        return None
    if provider == FIVETOOLS and config.fivetools_root:
        fragment = unquote(urlsplit(url).fragment)
        name, _, source = fragment.rpartition('_')
        if not name or not source:
            return None
        if type(monster.get(NAME)) is str and name_key(monster[NAME]) == name_key(name):
            name = monster[NAME]
        if type(monster.get(BOOK)) is str and monster[BOOK].casefold() == source.casefold():
            source = monster[BOOK]
        return provider, {'root': config.fivetools_root, 'name': name, 'source': source}
    if provider == OPEN5E and config.open5e_base:
        match = re.fullmatch(r'https://api\.open5e\.com/v2/creatures/([A-Za-z0-9][A-Za-z0-9_.-]{0,199})/', url)
        if match is None:
            return None
        return provider, {'base_url': config.open5e_base, 'key': match.group(1)}
    if provider == DNDBEYOND:
        from .scrying_glass_dndbeyond_statblock import canonical_url
        try:
            canonical, _ = canonical_url(url)
        except SourceError:
            return None
        return provider, {'path': urlsplit(canonical).path}
    return None


def source_fields(monster):
    """The tracker's retained source identity, compared at apply (not changed by it)."""
    from .scrying_glass_monster_source_snapshot import FIELDS
    return tuple(sorted((key, json.dumps(monster.get(key))) for key in FIELDS if key in monster))


def candidate_summary(provider, identity, label, **extra):
    summary = {'provider': provider, 'label': label}
    if provider == FIVETOOLS:
        summary['source'] = identity['source']
    summary.update({key: value for key, value in extra.items() if value is not None})
    return summary


class Discovery:
    """Per-species lookups for one request; fetch(provider, url, deadline) is shared."""

    def __init__(self, config, fetch, deadline, cancelled=lambda: False):
        self.config, self.fetch, self.deadline, self.cancelled = config, fetch, deadline, cancelled

    def _json(self, provider, url):
        raw = self.fetch(provider, url, self.deadline)
        try:
            return json.loads(raw, parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
        except (ValueError, UnicodeError, RecursionError):
            raise SourceError('malformed_response') from None

    def run(self, provider, species):
        """-> {'status', 'candidates': [(identity, summary)], 'code'?, 'retry_at'?, 'omitted_versions'?,
        'omitted_unavailable'?}"""
        if not self.config.enabled.get(provider):
            return {'status': 'disabled', 'candidates': []}
        try:
            if provider == FIVETOOLS:
                return self._fivetools(species)
            if provider == OPEN5E:
                return self._open5e(species)
            return self._dndbeyond(species)
        except FetchFailure as exc:
            if exc.code == 'cooldown':
                return {'status': 'cooldown', 'code': 'cooldown', 'retry_at': exc.retry_at, 'candidates': []}
            return {'status': 'error', 'code': exc.code, 'candidates': []}
        except SourceError as exc:
            return {'status': 'error', 'code': exc.code, 'candidates': []}
        except (ValueError, TypeError, KeyError, AttributeError):
            return {'status': 'error', 'code': 'malformed_response', 'candidates': []}

    def _fivetools(self, species):
        from .scrying_glass_fivetools_fetch import allowed_dataset_path
        root = self.config.fivetools_root
        if root is None:
            return {'status': 'error', 'code': 'invalid_configuration', 'candidates': []}
        if not self.config.fivetools_sources:
            return {'status': 'complete', 'candidates': []}
        index = self._json(FIVETOOLS, root + '/bestiary/index.json')
        if type(index) is not dict:
            raise SourceError('malformed_response')
        wanted, out, versions, failures = name_key(species), [], 0, []
        for source in self.config.fivetools_sources:
            filename = index.get(source)
            if filename is None:
                continue
            path = f'bestiary/{filename}' if type(filename) is str else None
            if path is None or not allowed_dataset_path(path):
                failures.append('malformed_response')
                continue
            try:
                data = self._json(FIVETOOLS, f'{root}/{path}')
            except (FetchFailure, SourceError) as exc:
                if exc.code in ('deadline', 'cancelled'):
                    raise
                failures.append(exc.code)
                continue
            for record in (data.get('monster') if type(data) is dict else None) or []:
                if type(record) is not dict or type(record.get('name')) is not str or type(record.get('source')) is not str:
                    continue
                if name_key(record['name']) != wanted:
                    continue
                versions += len(record['_versions']) if type(record.get('_versions')) is list else 0
                identity = {'root': root, 'name': record['name'], 'source': record['source']}
                if len(out) < CANDIDATES_PER_PROVIDER and identity_key(FIVETOOLS, identity) not in {
                        identity_key(FIVETOOLS, i) for i, _ in out}:
                    out.append((identity, candidate_summary(FIVETOOLS, identity, record['name'],
                                                            legacy=record['source'] == 'MM' or None)))
        result = {'status': 'partial' if failures else 'complete', 'candidates': out}
        if failures:
            result['code'] = failures[0]
        if versions:
            result['omitted_versions'] = versions
        return result

    def _open5e(self, species):
        from .scrying_glass_open5e_statblock import discover_open5e
        base = self.config.open5e_base
        if base is None:
            return {'status': 'error', 'code': 'invalid_configuration', 'candidates': []}
        try:
            found = discover_open5e(species, fetch=lambda url, deadline: self.fetch(OPEN5E, url, deadline),
                                    deadline=self.deadline, base_url=base)
        except ValueError as exc:
            if isinstance(exc, SourceError):
                raise
            raise SourceError('malformed_response') from None
        out = []
        for item in found[:CANDIDATES_PER_PROVIDER]:
            identity = {'base_url': base, 'key': item['key']}
            out.append((identity, candidate_summary(OPEN5E, identity, item['name'], document=item.get('document'),
                                                    game_system=item.get('gamesystem'))))
        return {'status': 'complete' if len(found) <= CANDIDATES_PER_PROVIDER else 'partial', 'candidates': out,
                **({} if len(found) <= CANDIDATES_PER_PROVIDER else {'code': 'candidate_limit'})}

    def _dndbeyond(self, species):
        """Search-page candidates whose own page has a public statblock.

        A candidate without one (gated content) is not offered and only counted
        (``omitted_unavailable``). A candidate whose page could not be checked
        is still offered and makes the result partial with that failure code.
        """
        from .scrying_glass_dndbeyond_statblock import canonical_url, discover_dndbeyond, public_statblock
        fetch = lambda url, deadline: self.fetch(DNDBEYOND, url, deadline)
        found = discover_dndbeyond(species, fetch=fetch, deadline=self.deadline)
        out, omitted, failures = [], [], []
        for item in found[:CANDIDATES_PER_PROVIDER]:
            try:
                canonical, _ = canonical_url(item['path'])
            except SourceError:
                continue
            identity = {'path': urlsplit(canonical).path}
            try:
                if not public_statblock(identity['path'], fetch=fetch, deadline=self.deadline):
                    omitted.append(identity['path'])
                    continue
            except (FetchFailure, SourceError) as exc:
                if exc.code == 'cancelled' or self.cancelled():
                    raise
                failures.append(exc.code)
            out.append((identity, candidate_summary(DNDBEYOND, identity, item['name'], legacy=item.get('legacy'))))
        limited = len(found) > CANDIDATES_PER_PROVIDER
        result = {'status': 'partial' if limited or failures else 'complete', 'candidates': out}
        if limited or failures:
            result['code'] = 'candidate_limit' if limited else failures[0]
        if omitted:
            result['omitted_unavailable'] = len(omitted)
            result['unavailable_paths'] = omitted
        return result

    def original_public(self, provider, identity):
        """For the tracker's original D&D Beyond candidate: False when its page has no
        public statblock; True when it has one or cannot be checked (offered as before)."""
        if provider != DNDBEYOND or not self.config.enabled.get(DNDBEYOND):
            return True
        from .scrying_glass_dndbeyond_statblock import public_statblock
        try:
            return public_statblock(identity['path'], fetch=lambda url, deadline: self.fetch(DNDBEYOND, url, deadline),
                                    deadline=self.deadline)
        except (FetchFailure, SourceError, ValueError, TypeError, KeyError):
            return True
