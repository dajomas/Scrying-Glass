# 230 - Configurable 5e.tools source stages

[Back to handover index](../../HANDOVER.md)

Updated 2026-11-03. Task: [SG-TODO-006](../todo/060-fivetools-source-configuration.md).
Current preparation base: 24a7c18ead4203d21aa79f2b740a51799d3ef118.

## Agreed delivery and stage 1

The user corrected XPBH to XPHB and approved configuration/providers followed by UI
names. On 2026-11-03 the remaining UI stage was explicitly split into two commits:
2A notifications/shared formatter/tests/docs, then 2B popup labels/browser tests/docs.
Every write requires its own bound approval. Account integration SG-TODO-004 is on hold.

Stage 1 is already delivered, not a request to reimplement providers. Omitted sources
use MM, XMM, PHB, XPHB, DMG, XDMG in that order. Explicit lists replace defaults;
duplicates retain first occurrence; [] skips even the 5e.tools index fetch without
disabling D&D Beyond. Case-sensitive nonempty strings without surrounding whitespace,
maximum 32 input entries. Invalid display/null/scalar/malformed lists fail loading.
Existing MM/XMM settings remain restricted overrides; remove/expand and restart to
opt into all six. Default lists remain independent. No new key, schema or credentials.

Stage-1 preparation had twelve local offline tests with real helper and AST-extracted
config/candidate functions, mocked HTTP and temporary JSON/YAML. Upstream index IDs
were present at 8790755429c346d20020eed7826d312d484c393f in
5etools-mirror-3/5etools-src, index blob 6c1dc9533c847cd5e4d081b68b7ad705db0278ef.
That is index metadata, not successful live retrieval of all source data/images.
Direct live fetching failed in the assistant environment; live reachability remains
unverified. Provider errors, bounds/cache, matching and selection behavior are unchanged.

## Stage 2A prepared: notification labels

010-source.js adds pure monsterSourceLabel(candidate, popup=false). Notifications
use the six exact requested labels; prototype-property/custom/unknown codes fall
back to raw text without fabricated names or edition metadata. D&D Beyond keeps
its original legacy/current wording. Label strings use the existing textContent
notification path. Raw candidate/source IDs, tokens, URLs and matching are not
rewritten. Existing AC/HP overwrite, in-flight-edit and stale-response guards remain.

The formatter supports the upcoming popup format but the popup renderer is not
changed in 2A; it continues to show raw IDs until 2B. This is a usable partial UI
increment, not completed SG-TODO-006. Backend/provider/config/template/script order,
static adapter and marker remain unchanged. Only the first of eight Admin fragments
changes; sizes/identities are recorded in [Admin handover](050-admin-script-split.md).

Seven source/reader/runner unittest methods and three new Node VM/DOM-fixture
subtests passed locally. They cover exact names, immutable raw identity, unknown
codes, D&D wording, actual lookup notifications and existing/in-flight AC/HP guards.
Fragments and full assembled script passed syntax checks. VM mocks are not real
Chromium, authenticated server, live data or image verification. Existing normal CI
discovers the new .cjs file without workflow edits; CI/manual validation pending.

## Remaining stage 2B and acceptance

Use the same formatter for popup choices while preserving candidate identity/source
links and selection/cancel/focus/pending-submit behavior. Add browser regressions
for all six labels, unknown IDs and unchanged selected token/URL; finish docs and
inspect exact-SHA CI. Do not close until required live/browser validation is recorded.
README now distinguishes omitted six-source defaults from the explicit two-source
example and explains partial notification-only labels. Root HANDOVER links unchanged.
No archive, third-party data, manifest refresh, workflow dispatch or skip directive.
