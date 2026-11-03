# 050 - Initial Admin section visibility

[Back to TODO index](../../TODO.md)

## SG-TODO-005 - Hide already-active campaign/setup sections on initial opening

- Status: reopened/in progress, 2026-11-03; dependent-button correction prepared, approval/CI/live validation pending.
- Prior closure: 2026-11-02, at the user's request after user-confirmed green CI.
- Requested: 2026-11-02. Group scope and per-page behavior accepted: 2026-11-02.
- Implementation: ee9a4bd56439d8a5e7d5a94e5d9d1c1788c4c9e4 on features/perplexity.
- Priority, owner and deadline: not assigned.

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

### Acceptance and validation record

The delivered behavior and prepared regressions cover both agreed groups, all
four active/inactive combinations, delayed/incomplete state, early/later manual
choices, later scope changes, independent lair gating, unaffected display/log/Battle
panes, synchronized accessibility labels and assembled-page initialization without
API mutations. The user confirmed green CI and explicitly requested closure on
2026-11-02 at 22:37 CET, following delivery of ee9a4bd.

No workflow databaseId, result-artifact path or tested SHA was supplied with that
confirmation. CI success is user-reported, not an independently inspected run in
this close-out. Do not invent a run ID or treat earlier task runs as this result.

Eight focused Chromium unittest methods passed locally during preparation (the
four initial-condition subtests are included in that count). They use the actual
controller but stub pane handlers/renderers and transport. A ninth assembled-page
test loads real HTML/scripts with intercepted HTTP and an existing SQLite fixture,
checking all five hidden/aria states, no initialization mutations and manual
visibility surviving load(true). Both Python sources compiled. The assembled-page
fixture and full suite were not executed by the assistant locally; the later CI
success is the user's confirmation of their run.

The earlier checklist's deployed first-opening/reload/manual-Show/Hide verification
was not separately reported in the close-out request. The user's acceptance closes
the task on the confirmed-CI basis without relabelling an unexecuted or unreported
live check as passed. Fixture coverage is not authenticated live end-to-end evidence.

### Operation and retained limits

Deploy the new script and document-end fragment, restart for imported markup and
reload browsers. No migration or configuration change. Defaults are per page;
no persistent preferences are claimed. This close-out changes documentation only
and runs no new tests. Other tasks and the SG-TODO-004 hold are unchanged.
See [handover](../handover/220-admin-initial-visibility.md).

### Reopened dependent controls - 2026-11-03

The preceding closure/validation paragraphs are historical. The user reports
visible Show character/monster input buttons beneath hidden Campaign/Battle setup
parents. Automatic battle collapse resets all button.hidden flags, unlike the
individual parent handlers. New CSS in admin-shell.css makes each dependent
button display:none whenever its parent pane has [hidden]. It does not modify
child preferences, accessibility labels, initialization or independent lair gating.
It uses :has() and retains the existing modern-browser requirement.

Five new Chromium methods extract the actual pane controller from the production
assembled source and use the real stylesheet and initial-visibility script with
a minimal DOM/state fixture. Three methods failed on the original CSS; all five
passed with the correction. They check actual rendered visibility, manual/global
collapse, repeated refresh, initial boot, restore, child preferences and unaffected
controls. This is not authenticated live/full-server coverage.

- [ ] Deliver correction with bound approval and normal CI.
- [ ] Review corrective CI against its exact commit.
- [ ] Confirm parent/child buttons behave correctly in deployed Admin, then accept close-out.

Preparation base: 430574c584162099c61168cd680b0422479c1541.
Run 41584927496 attempt 1 is verified successful for the earlier Admin-split SHA
9f1b14ae99d3b297f4557f05f7f72485ab674d56; it does not validate this correction.
No split JavaScript bytes, provider behavior, workflow or backend are changed here.
