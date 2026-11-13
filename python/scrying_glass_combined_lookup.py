"""Fail-closed provider orchestration over an ordered provider list."""
import copy
import logging

LOG = logging.getLogger(__name__)


def combined_candidates(dnd_fetch, fivetools_fetch, *, dnd_enabled=True,
                        fivetools_enabled=True, max_candidates=32, extra=()):
    """Collect every enabled provider, retaining versions and never merging stats.

    Callbacks return complete raw candidate lists or raise on incomplete search.
    Signing and application state changes are the caller's separate responsibility.
    A failed provider suppresses all candidates, even when another succeeded.
    `extra` appends further (name, enabled, fetch) providers in order (Open5e).
    """
    return ordered_candidates((("D&D Beyond", dnd_enabled, dnd_fetch),
                               ("5e.tools", fivetools_enabled, fivetools_fetch), *extra),
                              max_candidates=max_candidates)


def ordered_candidates(providers, *, max_candidates=32):
    """Fail-closed collection over an ordered (name, enabled, fetch) list."""
    providers = tuple(providers)
    if any(not isinstance(item, tuple) or len(item) != 3 or type(item[1]) is not bool
           for item in providers):
        raise ValueError("Provider enable settings must be boolean")
    if type(max_candidates) is not int or max_candidates < 1:
        raise ValueError("Candidate limit must be a positive integer")
    candidates, outcomes, failed = [], [], []
    for name, enabled, fetch in providers:
        if not enabled:
            outcomes.append(dict(provider=name, status="disabled"))
            continue
        try:
            found = fetch()
            if (not isinstance(found, list) or len(found) > max_candidates
                    or any(not isinstance(item, dict) or item.get("provider") != name
                           for item in found)):
                raise ValueError("Incomplete or unsupported candidate list")
            copied = copy.deepcopy(found)
        except Exception:
            LOG.warning("Combined monster lookup failed for %s", name, exc_info=True)
            failed.append(name)
            outcomes.append(dict(provider=name, status="failed"))
            continue
        candidates.extend(copied)
        outcomes.append(dict(provider=name, status="ok", count=len(copied)))
    if failed:
        return dict(status="error", candidates=[], providers=outcomes,
                    reason="Combined monster lookup incomplete: " + ", ".join(failed)
                    + ". No candidates were offered. Retry or enter stats manually.")
    return dict(status="ok", candidates=candidates, providers=outcomes)
