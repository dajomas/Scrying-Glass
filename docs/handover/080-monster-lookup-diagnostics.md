# 080 - Monster lookup diagnostics repair

[Back to handover index](../../HANDOVER.md)

## Retained diagnostics repair and graph history

The accepted diagnostics repair and its exact baseline/blob identities, original
fixture failures, handler changes and verification limits are preserved in the
[complete prior handover](https://github.com/dajomas/Scrying-Glass/blob/ca5cdd94c267395fcada8fe21249ef17acc1bdcc/docs/handover/080-monster-lookup-diagnostics.md).
That record also retains the initial 04a/b graph, 04b.1 cache accounting and 04b.2
resource-preflight preparations, failures/corrections, dated test counts and source
pins. Consolidation does not reopen accepted work or relabel old results as CI.
The diagnostics repair's 17 diagnostics/15 fallback tests and earlier graph/cache/
bounds evidence remain historical; no new full provider validation is inferred.

## 022.04b.3 isolated worker - 2026-11-17

Baseline ca5cdd94c267395fcada8fe21249ef17acc1bdcc on features/perplexity-statblock.
New private blocking worker API wraps the unchanged exact graph in a fresh Linux
process. [224 contract, operational requirements and remaining gates](../todo/224-fivetools-statblock-resolution.md)
are authoritative for this preparation. Linux system prlimit applies address-space,
file and CPU limits before Python starts; the child verifies inheritance and a
refused cap-sized mapping. Missing/unsupported/unverified enforcement fails closed.
The default address-space cap is 256 MiB, not a total server memory allowance.

A fixed isolated-Python entry point exchanges bounded JSON/raw-byte data through
anonymous temporary files. No shell, pickle, imported JS, network fallback or DB
write. Absolute caller deadline is never reset. Cancellation/deadline failures
kill the process group, reap the child and discard output; successful calls also
leave no worker/cache behind. Global scheduling/fetch/provider gates and production
normalization/validation integration remain unfinished parent/04 work.

Thirteen focused tests passed on Linux/Python 3.12.8, repeated with ResourceWarning
as error: no skips/errors/failures. These include actual graph/output/provenance
comparisons, real kernel allocation refusal at 64 MiB, next-job recovery, blocked
infinite-loop kill and in-flight cancellation with reaping checks. Blocking/memory
faults use modified temporary core copies, not new production test hooks. Ordinary
subprocess tests use the SHA-verified live graph and bounds module. No assertion
in existing suites changes; earlier 22/12/11 modules were not rerun here. Full
provider/application/3.14/CI and final 04b acceptance remain pending.

README, root indexes, workflow and maintenance rules were reviewed/reused against
the verified baseline. The private helper changes no active application dependency,
listener or user workflow; those files remain unchanged. The indexed 080/224 paths
and old 04b increments anchor remain stable. [skip ci] on this and intermediate
04 deliveries until its last code push; no manual dispatch, merge or deployment.
022.01-022.03/lifecycle and accepted 016/017 stay closed; 04a/c-f remain open.
