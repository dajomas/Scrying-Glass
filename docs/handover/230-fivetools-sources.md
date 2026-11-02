# 230 - Configurable 5e.tools source stages

[Back to handover index](../../HANDOVER.md)

Prepared 2026-11-02 against a8461e93ac6281f618aa3b436a68e2787578e909.
Task: [SG-TODO-006](../todo/060-fivetools-source-configuration.md), in progress.

## Approved delivery and current stage

The user corrected XPBH to XPHB and approved two coherent commits: first usable
configuration/provider expansion, then descriptive UI names. Stage 1 is prepared
with tests/docs; it does not provide the final book-name UI. Each write needs its
own bound approval and normal CI. Do not mark the task complete after stage 1.
Account integration SG-TODO-004 stays on hold.

## Stage 1 configuration and operation

Omitted source lists use MM, XMM, PHB, XPHB, DMG, XDMG in that order. The config
loader's independent default list is checked against the provider tuple by tests.
Both providers call configured_sources for common fallback defaults and validation.
Explicit lists override; duplicates deduplicate in first-occurrence order. Empty
lists skip even the fallback index fetch. This affects 5e.tools only, not the
independent D&D Beyond flag or provider priority. Existing configurations explicitly
listing MM/XMM remain restricted until the key is removed or expanded. Restart
for config changes; no migration or new key is required.

Startup validates display as a mapping and sources as a list of at most 32 nonempty
case-sensitive strings without surrounding whitespace. Null/scalar/malformed lists
are errors, not requests for defaults. Legacy stats and image lookup retain first
usable result semantics; candidate lookup still enumerates configured usable
matches, keeps distinct variants and treats provider failures separately from zero
matches. Transport bounds/cache, stat parsing, image URLs, selection tokens, D&D
access gates and unrelated startup/password logic remain unchanged. Missing-index
entry and source-failure handling otherwise retain prior behavior. No third-party
data is bundled.

## Evidence and limits

Reconstructed originals were hash-verified against Git blobs e262538874b335a8455358a45d9f6bcc7e45969a
(provider), 9f1efb0caeae8be8f2c0cae9dfb585c1e016db69 (init),
908f5e98ef337c21e818ae06dde2cd25f52c44e1 (selection) and
 efa61721d589d3e4b3c2eeaa35ac3bc93a00ca0b (configuration example).
Twelve new offline regression methods passed locally after preparation. They cover
JSON/YAML omitted/explicit/empty settings, independent defaults, malformed input,
all six legacy stats/image source paths, full candidate enumeration/order,
deduplication, no-fetch empty lists and sanitized candidate errors. The real
5e.tools helper runs, while actual config/candidate functions are AST-extracted
without importing unrelated FastAPI/startup classes. HTTP is mocked and forbidden
at the transport boundary. Python source compilation passed. The full application
suite, server import and CI remain pending for this stage.

The upstream repository's bestiary index at 8790755429c346d20020eed7826d312d484c393f
contained all six IDs; index blob 6c1dc9533c847cd5e4d081b68b7ad705db0278ef in
5etools-mirror-3/5etools-src. This is index metadata, not verification of source
content availability or service-account access. Direct live index fetching failed
in the assistant environment. Verify actual provider data/token access separately.

## Documentation and next stage

config.example.yaml documents the six defaults, explicit override and empty-list
semantics. README was reviewed: its explicit MM/XMM example remains a supported
restricted override and does not declare those to be mandatory defaults. The
comprehensive source/label README refresh is deferred to approved stage 2 to keep
review payloads manageable. Detailed stage-1 operation is documented here and in
the task. Root indexes include the new handover and current task state.

Stage 2 must add the requested descriptive names to choices/notifications without
changing raw source identifiers, matching, URLs or selected identity. Include UI
regressions and update these notes. Existing UI still displays raw codes until
that stage. No successful CI result, complete task or live validation is claimed.
