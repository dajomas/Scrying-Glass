# 230 - Configurable 5e.tools source stages

[Back to handover index](../../HANDOVER.md)

Updated 2026-11-03. Task: [SG-TODO-006](../todo/060-fivetools-source-configuration.md), completed at the user's request.
Close-out preparation base: 21f5de181659458c763672b2b871a21fd2baebb9.

## Close-out and verified combined CI

The user explicitly requested closure on 2026-11-03 after delivery of both UI
increments and successful combined CI. Stage 2A is
c49a890d198098622f40f1d22e5e92db6e8914c4; stage 2B is
f2f63c1fc28238fb2c32b27ce180c54863b30fa5. Both deliveries were verified after push.

Evidence: ci-results-41622079200-attempt-1/run.json at
21f5de181659458c763672b2b871a21fd2baebb9 identifies Branch tests run
41622079200 attempt 1, features/perplexity, head
f2f63c1fc28238fb2c32b27ce180c54863b30fa5, completed/success. Workflow/tests job and
all configured steps report success: setup/dependencies, syntax/server import,
unittest/browser fixtures, pytest regressions, JavaScript and standalone browser/
audit checks. This is inspected workflow/step metadata, not a new local execution,
an individual-test count or review of every assertion. It covers the combined
notification/popup implementation rather than implying a separately inspected 2A run.

Closure records acceptance of the delivered scope on that basis. Actual live
stats/images from all six sources and authenticated deployed-browser checks were
not separately reported at close-out; retain these as operational verification
limits, not passed checks. Earlier live-fetch failure/index-only evidence below
is not erased or reclassified. SG-TODO-004 remains on hold and separate.

## Agreed delivery and provider compatibility

The user corrected XPBH to XPHB and approved configuration/providers followed by UI
names. On 2026-11-03 the UI stage was split into 2A notifications/shared formatter/
tests/docs and 2B popup labels/browser regressions/docs. Each external write requires
bound approval; plan approval was not blanket write approval.

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
Seven source/reader/runner methods and three Node VM/DOM subtests passed locally.
The other seven Admin fragments remained unchanged. The assembled classic script
is 114,814 bytes, SHA-256
40fca092f989bcd85eaf7f06dc02b962b662a28827864df68c998919cdf87b46. Stage 2B does not
change that bundle, its fingerprints or the formatter. The source-split reader,
marker and adapter remain unchanged; see [Admin handover](050-admin-script-split.md).

## Stage 2B delivered

f2f63c1fc28238fb2c32b27ce180c54863b30fa5 changes popup label construction in
static/monster-candidate-selection.js (5,267 bytes; Git blob
20c6985e3a42800dde3827a441bc4878560dcbcb). monsterSourceLabel(candidate,true)
supplies provider/book/year text. Selected objects, API fields, source links,
tokens, generation/cancellation/pending-submit/focus logic and script/template
ordering remain unchanged. Known names use the task's exact table; custom codes
stay literal without fabricated edition metadata; missing sources use Source
unavailable. D&D Beyond preserves provider/source/legacy-current display. Labels
continue through textContent, not innerHTML.

The existing candidate-browser module retains four original tests and adds three
regressions (seven total). Its fixture records raw responses and page errors. Tests
verify six exact labels and untouched HTTPS href/target/rel, chosen XPHB token and
AC/HP, raw response byte-equivalent JSON, matching notification and restored focus;
custom/XPBH/prototype/HTML-like/missing sources render literally and remain selectable;
D&D labels/cancel remain unchanged. Existing pending-submit/edit/species-change tests
remain. The unchanged typing/focus module also ran, checking no extra debounce/blur
lookups after selection, Cancel or Escape.

All ten browser methods passed locally in real Chromium with intercepted HTTP.
JavaScript syntax/Python compilation passed. Fixtures used the verified stage-2A
assembled source and real popup code, not a complete authenticated server or live
providers. Stage-2A local checks were not rerun for 2B preparation; combined CI
subsequently succeeded as recorded above. No live source/image access is inferred.

## Documentation and deployment

README, task/index and handovers now reflect delivered stages, verified CI and user
acceptance without the former stale prepared/pending-CI status. Deploy the matching
static/ tree and hard-refresh Admin; do not mix an old assembled Admin formatter
with the new popup file. Restart as appropriate for full application deployment.
Root HANDOVER links, templates, provider/API code, schema and configuration files
remain unchanged. Existing user-guide provider/source guidance remains applicable.

This close-out is documentation-only; no code, tests or workflow changes, new test
execution, archive, manifest refresh or workflow dispatch. Normal CI applies to the
proposed close-out commit; the earlier SG-TODO-005-specific skip request is not reused.
Other task statuses and the account-integration hold remain unchanged.

## Source-label VM feedback dependency repair - 2026-11-10

The [approved 009.7 CI repairs](380-feedback-delivery-plan.md#ci-repair-stages---2026-11-10)
include tests/fivetools-source-labels.test.cjs. Run 42789493875 attempt 1 tested
62b824501cefc5418ef6f41b853faf5c2b2289b9; evidence publication is
978453c1164bcb632cb9a041a37b981ed6d07d3f. The JavaScript step's sole failing
file had two passing subtests and one lookup subtest throwing window is not defined.
The Python/browser, pytest and standalone groups passed; this does not itself
validate the unexecuted lookup assertions in that failing VM subtest.

The fixture now supplies window as its VM global, initializes the real feedback
controller and Admin bootstrap, and routes notifier ticket/severity options through
the real deliver API. Only accepted publications enter the message recorder.
Missing DOM view roots are deliberate for this record-level VM fixture; no renderer
is mounted. A deterministic timer queue supports the persistence check without
leaving real success timers alive. No always-current/success feedback stub or
production fallback is introduced. All original label, immutable ID/token/URL,
AC/HP overwrite and pending-edit assertions remain. Three added regressions cover
explicit lookup-success metadata and lookup-only clearing, persistent request
errors, and rejection of an older response after a newer lookup succeeds.

Executed preparation: node --check and all six subtests passed on Node 20.20.1;
CI is configured for Node 22, whose covering result remains pending. The exact
original fixture reproduced the CI failure as a negative control (two pass, one
window-is-not-defined failure). Controller, bootstrap and original test reconstructions
matched their live Git blob identities. The production lookup prefix was rebuilt
from the verified prior read; a complete local 010-file identity is not claimed.
These are isolated Node VM/source-slice tests with mocked request results, not
full Admin/browser, authenticated-server or live-provider verification.

This changes only the test file and this existing handover, using normal CI with
no skip marker, workflow change or separate dispatch. Root README/TODO/HANDOVER
identities were rechecked and their descriptions/statuses/links need no edits.
SG-TODO-006 stays closed; 4A.1/009.7 and combined validation remain open. No new
commit SHA or passing corrective CI is invented before supporting evidence. The
older documentation-only close-out/skip notes above are historical.
