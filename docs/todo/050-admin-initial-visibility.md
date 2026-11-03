# 050 - Initial Admin section visibility

[Back to TODO index](../../TODO.md)

## SG-TODO-005 - Hide already-active campaign/setup sections on initial opening

- Status: completed, 2026-11-03, at the user's explicit close-out request after the delivered dependent-button correction.
- Prior closure: 2026-11-02, at the user's request after user-confirmed green CI; reopened 2026-11-03 for dependent controls.
- Requested: 2026-11-02. Group scope and per-page behavior accepted: 2026-11-02.
- Initial implementation: ee9a4bd56439d8a5e7d5a94e5d9d1c1788c4c9e4 on features/perplexity.
- Dependent-button correction: e7b3d96ce428ce4022bb3930a8c660f02f12b765.
- Priority, owner and deadline: not assigned.

### Current close-out - 2026-11-03

The user explicitly requested closure while SG-TODO-006's CI was pending, and
requested [skip ci] for this documentation-only push. The correction is delivered,
not merely prepared. Its static/admin-shell.css blob
d89a094bfd42b2f0e126038e4aebb75f41c31670 matches both current HEAD
f2f63c1fc28238fb2c32b27ce180c54863b30fa5 and tested commit
75b870ef9a204981bc778ccbaaea23f96b3fcb56. The delivered stylesheet contains the
parent-hidden :has() rules for both dependent buttons.

Inspected ci-results-41608182802-attempt-1/run.json identifies run 41608182802,
attempt 1, exact head 75b870ef9a204981bc778ccbaaea23f96b3fcb56, completed/success.
Workflow/tests job and syntax/import, unittest, pytest, JavaScript and standalone
browser/audit steps all report success. This is inspected run/step metadata, not a
new execution or a claim that every individual assertion was reviewed here.

Closure records user acceptance and delivered implementation with that CI evidence.
No new per-control authenticated/live test result was supplied with this close-out;
do not relabel historical fixtures or the separate Storage runbook as such evidence.
No application/test/workflow change or new test execution is included. The skip
request applies to this close-out commit only; SG-TODO-006 remains independently
pending its own CI/live validation. See [handover](../handover/220-admin-initial-visibility.md).

### Agreed and delivered behavior

On each initial opening/reload of Admin, evaluate the first complete authoritative
state once:

- An active campaign collapses Campaign setup and Character input.
- An active saved battle setup collapses Battle setup, Monster input and Lair input.
- Conditions are independent; false conditions preserve existing defaults.
- Battle controls, Character display, Monster display and Activity log are unaffected.

Use existing Show/Hide handlers so per-page visibility, labels and aria-expanded
remain synchronized. Already-hidden inputs stay hidden. Existing has-lair gating
remains independent. Manual choices before the initial response are respected
per pane; later polling, loads, renders and campaign/setup changes do not recollapse
inputs. Users can reopen normally. Reload starts a fresh decision. No stored
browser/database preference, new network request or backend mutation is introduced.

The source of truth is active_campaign_id plus a valid active_setup reference
with nonempty campaign_id/name strings; null means no saved active setup. Missing
or malformed data does not consume the initial decision. The script loads after
Admin/lair extensions, chains the existing renderer and catches up from latest.

### Historical initial acceptance and validation

The delivered behavior and prepared regressions cover both agreed groups, all
four active/inactive combinations, delayed/incomplete state, early/later manual
choices, later scope changes, independent lair gating, unaffected display/log/Battle
panes, synchronized accessibility labels and assembled-page initialization without
API mutations. The user confirmed green CI and explicitly requested closure on
2026-11-02 at 22:37 CET, following delivery of ee9a4bd.

No workflow databaseId, result-artifact path or tested SHA was supplied with that
initial confirmation. That initial CI success was user-reported, not independently
inspected then. Do not invent a run ID or treat earlier task runs as that result.

Eight focused Chromium unittest methods passed locally during initial preparation
(the four initial-condition subtests are included in that count). They use the
actual controller but stub pane handlers/renderers and transport. A ninth assembled-
page test loads real HTML/scripts with intercepted HTTP and an existing SQLite
fixture, checking all five hidden/aria states, no initialization mutations and
manual visibility surviving load(true). Both Python sources compiled. That assembled-
page fixture/full suite were not executed by the assistant locally at initial
preparation; later initial CI success was the user's confirmation.

The earlier checklist's deployed first-opening/reload/manual-Show/Hide verification
was not separately reported at the initial close-out. User acceptance closed that
initial task without relabelling unexecuted/unreported live checks as passed.
Fixture coverage is not authenticated live end-to-end evidence.

### Operation and retained limits

Deploy the script, matching document-end fragment and stylesheet; restart for
imported markup and reload browsers. No migration/configuration change. Defaults
are per page; no persistent preferences are claimed. Other tasks and the
SG-TODO-004 hold are unchanged.

### Historical reopening and delivered dependent controls - 2026-11-03

The user reported visible Show character/monster input buttons beneath hidden
Campaign/Battle setup parents. Automatic battle collapse resets all button.hidden
flags, unlike individual parent handlers. The correction in admin-shell.css makes
each dependent button display:none whenever its parent pane has [hidden]. It does
not modify child preferences, accessibility labels, initialization or independent
lair gating. It uses :has() and retains the existing modern-browser requirement.

Five new Chromium methods extract the actual pane controller from the production
assembled source and use the real stylesheet and initial-visibility script with
a minimal DOM/state fixture. Three methods failed on the original CSS; all five
passed with the correction during preparation. They check rendered visibility,
manual/global collapse, repeated refresh, initial boot, restore, child preferences
and unaffected controls. This is not authenticated live/full-server coverage.

- [x] Deliver correction: e7b3d96ce428ce4022bb3930a8c660f02f12b765.
- [x] Review successful run 41608182802 attempt 1 covering unchanged corrective CSS.
- [x] Accept close-out by explicit user request on 2026-11-03, with live-evidence limits recorded above.

Historical preparation base: 430574c584162099c61168cd680b0422479c1541.
Run 41584927496 attempt 1 verified the earlier Admin-split SHA
9f1b14ae99d3b297f4557f05f7f72485ab674d56, not the then-unpushed correction.
Current closure instead uses the later delivered correction and evidence above.
