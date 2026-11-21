"""Server-held candidates, prepared selections and apply outcomes (SG-TODO-022.08).

Nothing here is persisted: a restart invalidates every reference.

- Candidates: opaque IDs for discovered exact source identities, bound to the
  session, user, campaign, encounter token, target monster, its species and
  original-source identity. Bounded by engineering safeguards; a session at
  its cap loses only its own oldest candidates.
- Prepared snapshots: immutable canonical content shared by digest between
  bindings (``prepared_snapshots``/``prepared_bytes``). Released when the last
  reference expires, is cancelled or is consumed.
- Selection references: one per accepted preparation job (reserved at
  acceptance) or completed selection, plus retained operation outcomes
  (``session_selection_references`` per session, ``selection_references``
  in all). At capacity new work is rejected; another user's unexpired
  selection is never evicted.
- Selections expire ``selection_seconds`` after completion; viewing does not
  extend them. Outcomes are kept until the original expiry of the selections
  they consumed, so an identical retry returns the recorded result.
"""
from __future__ import annotations

import hashlib
import json
import secrets
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass, field

from .scrying_glass_statblock_limits import CANDIDATE_REFERENCES, SESSION_CANDIDATE_REFERENCES


class SelectionError(Exception):
    def __init__(self, code, retry_at=None):
        self.code, self.retry_at = code, retry_at
        super().__init__(code)


def session_key(token):
    return hashlib.sha256(('statblock-session:' + str(token)).encode()).hexdigest()


@dataclass
class Scope:
    """Who prepared a reference and for which target, checked again at every use."""
    session: str
    user_id: str
    campaign: str
    encounter_token: str
    monster_id: str
    species: str
    source_identity: tuple

    def same_target(self, other):
        return (self.session, self.user_id, self.campaign, self.encounter_token, self.monster_id,
                self.species, self.source_identity) == (other.session, other.user_id, other.campaign,
                other.encounter_token, other.monster_id, other.species, other.source_identity)


@dataclass
class Candidate:
    id: str
    scope: Scope
    provider: str
    identity: dict
    summary: dict
    expires_at: float


@dataclass
class Binding:
    id: str
    scope: Scope
    expected_revision: int
    digest: str
    expires_at: float
    expires_wall: float
    summary: dict = field(default_factory=dict)
    consumed: bool = False


@dataclass
class Outcome:
    digest: str
    result: dict
    expires_at: float


class SelectionStore:
    def __init__(self, limits, *, clock=time.monotonic, wall=time.time):
        self.limits, self.clock, self.wall = limits, clock, wall
        self._lock = threading.RLock()
        self._candidates = OrderedDict()
        self._prepared = {}  # digest -> [canonical bytes, size, refcount]
        self._prepared_bytes = 0
        self._bindings = {}
        self._reserved = {}  # session -> count
        self._outcomes = {}  # (session, operation_id) -> Outcome

    # -- accounting ------------------------------------------------------------
    def _session_refs(self, session):
        return self._reserved.get(session, 0) + sum(1 for b in self._bindings.values() if b.scope.session == session)

    def _global_refs(self):
        return sum(self._reserved.values()) + len(self._bindings) + len(self._outcomes)

    def counts(self):
        with self._lock:
            self.purge()
            return {'candidates': len(self._candidates), 'bindings': len(self._bindings),
                    'reserved': sum(self._reserved.values()), 'outcomes': len(self._outcomes),
                    'prepared_snapshots': len(self._prepared), 'prepared_bytes': self._prepared_bytes}

    def purge(self):
        now = self.clock()
        with self._lock:
            for key in [k for k, c in self._candidates.items() if c.expires_at <= now]:
                del self._candidates[key]
            for key in [k for k, b in self._bindings.items() if b.expires_at <= now]:
                self._release_binding(key)
            for key in [k for k, o in self._outcomes.items() if o.expires_at <= now]:
                del self._outcomes[key]

    # -- candidates ------------------------------------------------------------
    def add_candidate(self, scope, provider, identity, summary):
        with self._lock:
            self.purge()
            mine = [k for k, c in self._candidates.items() if c.scope.session == scope.session]
            while len(mine) >= SESSION_CANDIDATE_REFERENCES:
                del self._candidates[mine.pop(0)]
            if len(self._candidates) >= CANDIDATE_REFERENCES:
                raise SelectionError('candidate_capacity')
            ident = secrets.token_urlsafe(18)
            self._candidates[ident] = Candidate(ident, scope, provider, dict(identity), dict(summary),
                                                self.clock() + self.limits.selection_seconds)
            return ident

    def candidate(self, ident, session):
        with self._lock:
            self.purge()
            value = self._candidates.get(ident) if type(ident) is str else None
            if value is None or value.scope.session != session:
                raise SelectionError('candidate_expired')
            return value

    # -- reservations and selections ------------------------------------------------
    def reserve(self, session):
        with self._lock:
            self.purge()
            if self._session_refs(session) >= self.limits.session_selection_references:
                raise SelectionError('session_selection_capacity')
            if self._global_refs() >= self.limits.selection_references:
                raise SelectionError('selection_capacity')
            self._reserved[session] = self._reserved.get(session, 0) + 1

    def release(self, session):
        with self._lock:
            count = self._reserved.get(session, 0)
            if count <= 1:
                self._reserved.pop(session, None)
            else:
                self._reserved[session] = count - 1

    def complete(self, scope, expected_revision, snapshot, summary):
        """Turn the scope's reservation into a selection; capacity failures release it."""
        from .scrying_glass_statblock_model import ModelLimits, canonical_bytes
        unbounded = ModelLimits(**{name: 2**63 - 1 for name in ModelLimits.__dataclass_fields__})
        raw = canonical_bytes(snapshot, unbounded)
        digest = snapshot['content_digest']
        with self._lock:
            self.release(scope.session)
            self.purge()
            entry = self._prepared.get(digest)
            if entry is None:
                if len(self._prepared) >= self.limits.prepared_snapshots:
                    raise SelectionError('prepared_capacity')
                if self._prepared_bytes + len(raw) > self.limits.prepared_bytes:
                    raise SelectionError('prepared_capacity')
                entry = self._prepared[digest] = [raw, len(raw), 0]
                self._prepared_bytes += len(raw)
            entry[2] += 1
            ident = secrets.token_urlsafe(24)
            now, wall = self.clock(), self.wall()
            seconds = self.limits.selection_seconds
            self._bindings[ident] = Binding(ident, scope, expected_revision, digest, now + seconds, wall + seconds,
                                            dict(summary))
            return self._bindings[ident]

    def _release_binding(self, ident):
        binding = self._bindings.pop(ident, None)
        if binding is None:
            return
        entry = self._prepared.get(binding.digest)
        if entry is not None:
            entry[2] -= 1
            if entry[2] <= 0:
                del self._prepared[binding.digest]
                self._prepared_bytes -= entry[1]

    def binding(self, ident, session):
        with self._lock:
            self.purge()
            value = self._bindings.get(ident) if type(ident) is str else None
            if value is None:
                raise SelectionError('selection_expired')
            if value.scope.session != session:
                raise SelectionError('selection_forbidden')
            return value

    def snapshot(self, binding):
        with self._lock:
            entry = self._prepared.get(binding.digest)
            if entry is None:
                raise SelectionError('selection_expired')
            return json.loads(entry[0])

    def discard(self, ident, session):
        with self._lock:
            value = self._bindings.get(ident)
            if value is not None and value.scope.session == session:
                self._release_binding(ident)
                return True
            return False

    # -- apply outcomes -----------------------------------------------------------
    def outcome(self, session, operation_id):
        with self._lock:
            self.purge()
            return self._outcomes.get((session, operation_id))

    def reserve_outcome(self, session, operation_id, consumed):
        """Check before mutation that the outcome fits once the consumed selections are freed."""
        with self._lock:
            self.purge()
            if (session, operation_id) in self._outcomes:
                return
            freed = len([ident for ident in consumed if ident in self._bindings])
            if self._global_refs() - freed + 1 > self.limits.selection_references:
                raise SelectionError('selection_capacity')

    def finish_apply(self, session, operation_id, digest, consumed, result):
        """After commit: consume the selections and keep the outcome until their expiry."""
        with self._lock:
            expiry = max([self._bindings[i].expires_at for i in consumed if i in self._bindings]
                         or [self.clock() + self.limits.selection_seconds])
            for ident in consumed:
                self._release_binding(ident)
            self._outcomes[(session, operation_id)] = Outcome(digest, json.loads(json.dumps(result)), expiry)

    # -- revocation --------------------------------------------------------------
    def revoke_session(self, session):
        with self._lock:
            for key in [k for k, c in self._candidates.items() if c.scope.session == session]:
                del self._candidates[key]
            for key in [k for k, b in self._bindings.items() if b.scope.session == session]:
                self._release_binding(key)
            for key in [k for k in self._outcomes if k[0] == session]:
                del self._outcomes[key]

    def clear(self):
        with self._lock:
            self._candidates.clear()
            self._bindings.clear()
            self._prepared.clear()
            self._prepared_bytes = 0
            self._outcomes.clear()
