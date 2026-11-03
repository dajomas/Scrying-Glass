# 060 - 5e.tools sources and descriptive names

[Back to TODO index](../../TODO.md)

## SG-TODO-006 - Expand configurable 5e.tools defaults and display book names

- Status: completed, 2026-11-03, at the user's explicit close-out request after implementation delivery and verified successful combined CI.
- Requested: 2026-11-02. Original two-stage delivery approved: 2026-11-02.
- Remaining UI stage split into two commits approved: 2026-11-03.
- Priority, owner and deadline: not assigned.
- Stage 2A: c49a890d198098622f40f1d22e5e92db6e8914c4 on features/perplexity.
- Stage 2B: f2f63c1fc28238fb2c32b27ce180c54863b30fa5 on features/perplexity.
- Close-out preparation base: 21f5de181659458c763672b2b871a21fd2baebb9.
- Identifier decision: user corrected XPBH to XPHB on 2026-11-02.

### Delivered scope and compatibility

1. Configuration/providers/tests/docs: delivered.
2A. Notification labels/shared formatter/source guards/tests/docs: delivered.
2B. Popup labels using the same formatter, browser regressions/final docs: delivered.
The user accepts close-out of this delivered scope on the verified-CI basis below.
SG-TODO-004 stays on hold and was not a dependency or part of this delivery.

Omitted display.fivetools_sources uses MM, XMM, PHB, XPHB, DMG, XDMG, in order.
Explicit lists replace defaults; duplicates retain first occurrence. [] searches no
5e.tools source/index without disabling D&D Beyond. IDs are case-sensitive nonempty
strings without surrounding whitespace; max 32 input entries. Invalid/null/scalar/
malformed settings or display mappings fail loading. Existing MM/XMM overrides
remain restricted; remove/expand and restart for all six. No migration, new key,
credentials, data bundling or provider-order change.

| Identifier | Exact label |
|---|---|
| MM | Monster Manuals 2014 |
| XMM | Monster Manuals 2024 |
| PHB | Player Handbook 2014 |
| XPHB | Player Handbook 2024 |
| DMG | Dungeon Master Guide 2014 |
| XDMG | Dungeon Master Guide 2024 |

Notifications and popup choices use these names. Raw IDs in URLs, matching,
deduplication, responses and selected-candidate tokens remain unchanged. Custom IDs
stay raw without guessed names/year; missing popup sources use Source unavailable.
D&D Beyond notification and popup edition wording is unchanged.

### Verified CI and acceptance

Inspected ci-results-41622079200-attempt-1/run.json at
21f5de181659458c763672b2b871a21fd2baebb9 identifies Branch tests run
41622079200, attempt 1, exact head f2f63c1fc28238fb2c32b27ce180c54863b30fa5,
features/perplexity, completed/success. The workflow/tests job and all configured
steps report success, including syntax/server imports, unittest/browser fixtures,
pytest regressions, JavaScript tests and standalone Python browser/audit checks.
This verifies combined stage-2A/2B CI metadata, not review of every individual
assertion or authenticated live-provider behavior. No test count is inferred here.

- [x] User confirmed XPHB.
- [x] User agreed separate notification/popup commits.
- [x] Deliver notification increment: c49a890d198098622f40f1d22e5e92db6e8914c4.
- [x] Deliver popup increment: f2f63c1fc28238fb2c32b27ce180c54863b30fa5.
- [x] Verify successful combined exact-SHA regression CI: run 41622079200 attempt 1.
- [x] Accept and close SG-TODO-006 at the user's explicit request on 2026-11-03.

### Retained validation history and limits

Stage 1 had twelve local offline helper/config/candidate checks. All six upstream
index entries were found, but that was index metadata rather than usable live
stats/images. Stage 2A had seven source/reader/runner methods and three Node subtests
pass locally. Stage 2B had seven candidate-browser tests (four retained, three added)
and three unchanged typing/focus tests pass locally in real Chromium with intercepted
HTTP. Those checks cover exact labels, unknown/prototype/HTML-like fallback, source
links/raw response/token, selected AC/HP, matching notifications, cancel/Escape/focus,
pending submits, edits and no extra lookups. Syntax/compilation passed. Stage-2A local
checks were not rerun during 2B preparation; subsequent combined CI is recorded above.

Actual live stats/images for every configured source and authenticated deployed
browser checks were not separately reported with this close-out. The former live-
verification checklist item remains an explicit operational verification limit,
not a silently deleted task or a claimed pass. User-requested closure records
acceptance of the delivered scope with that limitation retained. Fixture/CI success
must not be represented as live upstream retrieval or entitlement verification.

See [handover](../handover/230-fivetools-sources.md) for provenance, deployment and
continuity. This close-out changes documentation only; no code/test/workflow change
or new test execution. Normal CI applies; the prior SG-TODO-005 [skip ci] request
does not carry over. Other tasks, including the SG-TODO-004 hold, remain unchanged.
