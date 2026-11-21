"""Ordered graph entry; isolated execution is available through its worker.

Resolver remains the backward-compatible foundation API. OrderedResolver uses
its graph/cycle/cache/limit machinery and executes every copy mode of the
pinned runtime. Both are internal pure interpreters; statblock preparation
(scrying_glass_fivetools_preparation) builds on OrderedResolver.
"""
from .scrying_glass_fivetools_resolution import Resolver
from .scrying_glass_fivetools_modifications import apply_modifications, ModificationError

class OrderedResolver(Resolver):
    ADAPTER_VERSION = '04f-1'

    def _apply_compiled_modifications(self, record, mods, *, check, fail):
        try:
            return apply_modifications(record, mods, check=check,
                intermediate_creature_bytes=self.limits.intermediate_creature_bytes,
                modification_operations=self.limits.modification_operations)
        except ModificationError as exc:
            d = exc.diagnostic
            group = [x for x in mods if x.property == d.property]
            item = group[d.operation_index] if d.operation_index is not None and 0 <= d.operation_index < len(group) else None
            chain = item.chain if item is not None else None
            source_path = d.source_path
            if chain and chain[-1].kind.endswith('Template'):
                source_path = source_path.replace('$/_copy/_mod', '$/apply/_mod', 1)
            fail(d.code, source_path, d.property, d.operation_index, d.mode, chain=chain)
