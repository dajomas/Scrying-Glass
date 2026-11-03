# 230 - Configurable 5e.tools source stages

[Back to handover index](../../HANDOVER.md)

Updated 2026-11-03. Task: [SG-TODO-006](../todo/060-fivetools-source-configuration.md).
Stage 2B preparation base: c49a890d198098622f40f1d22e5e92db6e8914c4.

## Agreed delivery and provider compatibility

The user corrected XPBH to XPHB and approved configuration/providers followed by UI
names. On 2026-11-03 the UI stage was split into 2A notifications/shared formatter/
tests/docs and 2B popup labels/browser regressions/docs. Each write needs bound
approval. SG-TODO-004 remains on hold; no account integration is in this task.

Stage 1 is delivered. Omitted sources use MM, XMM, PHB, XPHB, DMG, XDMG, in order.
Explicit lists replace defaults; duplicates retain first occurrence; [] skips even
the 5e.tools index without disabling D&D Beyond. IDs are nonempty case-sensitive
strings without surrounding whitespace, max 32 input entries. Invalid display/null/
scalar/malformed lists fail loading. Existing MM/XMM overrides remain restricted;
remove/expand and restart to opt into all six. Defaults remain independent; no new
key/schema/credentials/provider priority or transport/cache change is introduced.

Twelve stage-1 offline checks used real helper and AST-extracted config/candidate
functions with mocked HTTP and temporary JSON/YAML. Upstream index metadata at
8790755429c346d20020eed7826d312d484c393f, index blob
6c1dc9533c847cd5e4d081b68b7ad705db0278ef in 5etools-mirror-3/5etools-src, included
all six IDs. Direct live fetching failed in the assistant environment. This verifies
index entries, not usable source stats/images or service-account reachability.

## Stage 2A delivered

c49a890d198098622f40f1d22e5e92db6e8914c4 adds monsterSourceLabel(candidate,popup=false)
and descriptive lookup notifications, preserving raw IDs/tokens/URLs and D&D wording.
Seven source/reader/runner methods and three Node VM/DOM subtests passed locally;
its full CI was not inspected. The other seven Admin fragments remained unchanged.
The assembled classic script is 114,814 bytes, SHA-256
40fca092f989bcd85eaf7f06dc02b962b662a28827864df68c998919cdf87b46. Stage 2B does not
change that bundle, its fingerprints or the formatter. The source-split reader,
marker and adapter remain unchanged; see [Admin handover](050-admin-script-split.md).

## Stage 2B prepared

static/monster-candidate-selection.js is 5,267 bytes, expected Git blob
20c6985e3a42800dde3827a441bc4878560dcbcb. Only popup label construction changes:
monsterSourceLabel(candidate,true) supplies provider/book/year text. Selected objects,
API fields, source links, tokens, generation/cancellation/pending-submit/focus logic
and script/template ordering remain unchanged. Known names use the exact task table;
unknown codes stay literal with no fabricated edition; missing sources use Source
unavailable. D&D Beyond preserves provider/source/legacy-current display. Labels
continue through textContent, not innerHTML.

The existing candidate-browser module retains its four original tests and adds three
regressions (seven total). Its fixture records raw responses and page errors. Tests
verify six exact labels and untouched HTTPS href/target/rel, chosen XPHB token and
AC/HP, raw response byte-equivalent JSON, matching notification and restored focus;
custom/XPBH/prototype/HTML-like/missing sources render literally and remain selectable;
D&D labels/cancel remain unchanged. Existing pending-submit/edit/species-change tests
remain. The unchanged typing/focus module also ran, proving no extra debounce/blur
lookups after selection, Cancel or Escape.

All ten browser methods passed locally in real Chromium with intercepted HTTP.
JavaScript syntax and Python compilation passed. Fixtures used the verified stage-2A
assembled source and real popup code, not a complete authenticated server or real
providers. No source data/image access is proven. Stage-2A source/Node checks were
not rerun for 2B; their previous results are historical. Full CI and live validation
remain pending; existing unittest discovery includes all new methods without workflow
edits. No successful new CI run or completed task is claimed.

## Documentation, deployment and acceptance

README and task/index describe both label surfaces and unchanged source IDs. Deploy
the matching static/ tree, restart if needed for application deployment and hard-
refresh Admin; do not mix an old assembled Admin formatter with the new popup file.
Root HANDOVER links, Admin split architecture, templates, provider/API code, schema
and configuration files remain unchanged. Existing user-guide provider/source guidance
remains applicable. No archive, manifest refresh, workflow dispatch or CI skip.

After approval/delivery, review exact-SHA CI, exercise authorized live/browser lookup
and distinguish all-six source metadata from actual returned stats/images before
closing SG-TODO-006. Unknown custom sources remain supported.
