"""Operator limits for statblock discovery, preparation and apply (SG-TODO-022.08).

The ``statblocks.limits`` configuration namespace holds the 26 agreed keys
(TODO 220, "Approved limits and configuration"). Every value is a positive
integer controlled by the operator, never by an import request; unknown keys
and invalid values are rejected at start-up. Lowered limits apply to new
preparations only: saved snapshots stay readable.

The retained request bounds (``.monster`` upload, apply targets and apply body)
are named constants, not configuration.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, fields

MONSTER_FILE_BYTES = 5 * 1024 * 1024
APPLY_TARGETS = 50
APPLY_BODY_BYTES = 1024 * 1024
DISCOVERY_TARGETS = 50
MAX_REDIRECTS = 3
# Engineering safeguards for server-held candidate references; not agreed limits.
CANDIDATES_PER_PROVIDER = 32
CANDIDATE_REFERENCES = 4000
SESSION_CANDIDATE_REFERENCES = 2000
FAILED_JOB_SECONDS = 60
FAILED_JOB_RECORDS = 64


@dataclass(frozen=True)
class StatblockLimits:
    inheritance_steps: int = 16
    modification_operations: int = 1024
    reference_steps: int = 16
    supporting_definitions: int = 256
    intermediate_creature_bytes: int = 8388608
    preparation_seconds: int = 10
    supporting_reference_bytes: int = 16777216
    snapshot_bytes: int = 2097152
    content_nodes: int = 16384
    content_depth: int = 16
    text_value_bytes: int = 65536
    response_bytes: int = 10485760
    active_jobs: int = 2
    queued_jobs: int = 16
    outbound_requests: int = 4
    provider_requests: int = 2
    worker_memory_bytes: int = 268435456
    cache_entries: int = 64
    cache_bytes: int = 67108864
    cache_seconds: int = 3600
    failure_cooldown_seconds: int = 30
    selection_seconds: int = 600
    prepared_snapshots: int = 200
    prepared_bytes: int = 134217728
    session_selection_references: int = 200
    selection_references: int = 1000

    def __post_init__(self):
        for field in fields(self):
            value = getattr(self, field.name)
            if type(value) is not int or not 0 < value <= 2**63 - 1:
                raise ValueError(f'statblocks.limits.{field.name} must be a positive integer')

    @classmethod
    def from_mapping(cls, values):
        if values is None:
            return cls()
        if not isinstance(values, dict):
            raise ValueError('statblocks.limits must be a mapping/object')
        unknown = set(values) - {field.name for field in fields(cls)}
        if unknown:
            raise ValueError('Unknown statblocks.limits keys: ' + ', '.join(sorted(map(str, unknown))))
        return cls(**values)

    @classmethod
    def from_config(cls, config):
        section = (config or {}).get('statblocks')
        if section is None:
            return cls()
        if not isinstance(section, dict) or set(section) - {'limits'}:
            raise ValueError('statblocks must be a mapping with only a limits mapping')
        return cls.from_mapping(section.get('limits'))

    def model(self):
        from .scrying_glass_statblock_model import ModelLimits
        return ModelLimits(snapshot_bytes=self.snapshot_bytes, content_nodes=self.content_nodes,
                           content_depth=self.content_depth, text_value_bytes=self.text_value_bytes,
                           supporting_definitions=self.supporting_definitions)

    def preparation(self):
        """5e.tools PreparationLimits (resolution/collection/model) from these values."""
        from .scrying_glass_fivetools_collector import CollectionLimits
        from .scrying_glass_fivetools_preparation import PreparationLimits
        from .scrying_glass_fivetools_resolution import Limits
        resolution = Limits(inheritance_steps=self.inheritance_steps,
                            modification_operations=self.modification_operations,
                            intermediate_creature_bytes=self.intermediate_creature_bytes,
                            response_bytes=self.response_bytes, cache_entries=self.cache_entries,
                            cache_bytes=self.cache_bytes, cache_seconds=self.cache_seconds)
        collection = CollectionLimits(reference_steps=self.reference_steps,
                                      supporting_definitions=self.supporting_definitions,
                                      supporting_reference_bytes=self.supporting_reference_bytes)
        return PreparationLimits(resolution, collection, self.model())

    def fingerprint(self):
        """Stable text for conversion-cache keys: changed limits never reuse results."""
        return ','.join(f'{key}={value}' for key, value in sorted(asdict(self).items()))
