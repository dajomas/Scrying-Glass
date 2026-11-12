# 530 - Stage 1 setup-operation feedback

[Back to handover index](../../HANDOVER.md)

Task record: [097 setup-operation delivery split](../todo/097-feedback-delivery-plan.md#stage-1-step-2-setup-operation-delivery-split---2026-11-12).
Accepted campaign Step 1 history: [520](520-campaign-operation-feedback.md).

## SG-TODO-009.7-S1-2A - create a new empty setup - 2026-11-12

Status: implementation prepared on base
1b54a2c4c47644c9ac0f72939043652d818cf337 (features/perplexity-009.7). Archive
only: no GitHub commit, push, workflow dispatch, hosted CI result, deployment or
acceptance is claimed here. The user applies, commits and pushes. Delivered together
with 2B-2E in one cumulative archive (see below).

### Delivered behavior

- The New setup button is now owned by a controller-backed handler in
  static/admin/060-source.js. It replaces the 050 legacy `#newSetup` handler at
  load time; 050 itself is unchanged and no later asset rebinds this button.
- Validation (blank name, case-insensitive duplicate in the active campaign) is a
  persistent `setup.new.validation` error in the Battle setup pane; focus returns to
  the name field and no request is sent. A valid attempt resolves only that matching
  error. Cancelling the existing confirmation sends nothing.
- Identity: page lane, region battleSetup, target `["setup-new", <campaign>]`,
  operations `setup.new.validation`, `setup.new` and `setup.new.refresh`.
- POST /api/setups/new keeps the exact `{name, campaign}` JSON payload, endpoint,
  confirmation wording and server validation. A rejected request is a persistent
  `setup.new` error; the typed name is preserved.
- Success ("Created and saved empty battle setup ...") is published immediately after
  the completed POST and expires after three seconds. The campaign list is then
  refreshed through a direct GET /api/campaigns (so failures propagate instead of
  being swallowed by the shared `setups()` helper), the dropdown selects the new
  setup and `load(true, relevant)` reloads state with operation ownership. The
  server's `moved` campaign notice is retained unchanged.
- Completed creation followed by a failed list/state refresh, or a reload that does
  not apply the created setup scope, is a separate persistent `setup.new.refresh`
  error advising reload and "do not create the setup again". No mutation is replayed.
- Guards: the attempt is relevant only while its refresh ticket is current, the
  active campaign is unchanged and the encounter scope is unchanged or the expected
  `[campaign, campaign, setup]` transition (which may arrive before the POST
  response). Obsolete results, errors and refreshes are suppressed. Newer typing in
  the name field is not overwritten. Duplicate clicks are ignored through the POST
  and refresh; the button's prior disabled state is restored.
- Save, Load/switch, Rename and Delete are covered by 2B-2E below; setup copy/move
  and background controls are unchanged and still use their existing feedback paths.

### Source identity

Only fragment 060 changes: 17,828 UTF-8 bytes (below 20,000), SHA-256
390145d6ede11af31b3ec579c63b38b278e46e667543b570912f95eb0f2a4c99. Bundle size pin:
150,740 bytes. Other seven digests, eight-fragment order, tamper/size guards and the
tracked static/admin.js failure marker are unchanged. The assembled admin.js URL is
unversioned and served from the fragments; no template or cache-version change.

### Verification executed locally on the prepared files

- New tests/setup-new-feedback.test.cjs: 13 Node tests pass (complete 060 with the
  production feedback controller; mocked DOM/transport/context).
- Six negative controls were detected (removed busy guard, post-POST stale guard,
  rejection stale guard, newer-input guard, applied-state check, and refresh via
  error-swallowing `load()`); the restored file is byte-identical and passes.
- New tests/test_setup_new_feedback_composition.py: 3 full-Admin Chromium scenarios
  pass with intercepted HTTP (success/exact payload, validation then request error,
  refresh failure without replay).
- Through tools/run_split_tests.py: all 78 JavaScript test files pass (616 Node
  tests); `unittest discover -s tests -p 'test_*.py'` ran 1,555 tests, OK; the two
  pytest regression modules pass (43); standalone browser/audit scripts were run as
  listed in Patch/CHANGES.md.

Local runs used Python 3.14 and Node 20 with a locally provisioned Chromium, not the
CI runner (Node 22). They are scoped preparation evidence, not hosted CI,
authenticated live-server, human visual, screen-reader or exhaustive accessibility
acceptance. The commit omits [skip ci] so normal push CI runs; no workflow edit or
dispatch.

## SG-TODO-009.7-S1-2B-2E - save, load/switch, rename, delete - 2026-11-12

Status: implementation prepared together with 2A in one cumulative archive on base
1b54a2c4c47644c9ac0f72939043652d818cf337, because 2A was not yet published and the
user explicitly asked for 2B-2E together. This replaces the plan's one-operation-
per-archive sequencing for this delivery only. Archive only: no commit, push,
dispatch, hosted CI result, deployment or acceptance is claimed.

### Delivered behavior

- Owner: static/setup-switch.js (separate asset, installed on DOMContentLoaded after
  the core bundle) now owns `#saveSetup`, `#setupSelect` change, `#loadSetup`,
  `#renameSetup` and `#deleteSetup`, replacing the 050 legacy handlers at load time.
  050 is unchanged. The template reference becomes `/static/setup-switch.js?v=1`.
- One shared guarded lifecycle per operation `<op>` in save, load, rename, delete:
  page lane, region battleSetup, target `["setup-<op>", <campaign>]`, operations
  `setup.<op>.validation`, `setup.<op>` and `setup.<op>.refresh`.
- Validation is a persistent error without a request: "Enter a battle setup name
  before saving", "Choose a saved battle setup to load", "Choose an active campaign
  first", "Choose a saved setup to rename", "Choose a saved setup to delete". A valid
  attempt resolves only its matching validation error.
- Requests keep exact endpoints and payloads: POST /api/setups/save `{name,
  campaign}`, POST /api/setups/load `{name, campaign}`, POST /api/setups/rename
  `{name, new_name, campaign}`, DELETE `/api/setups/<name>?campaign=<id>`. Rejections
  are persistent `setup.<op>` errors.
- Success is published right after the completed mutation and expires after three
  seconds: "Saved setup: X (campaign: Y)", "Loaded battle setup: X", "Renamed battle
  setup A to B", "Deleted battle setup A; opened [new empty setup ]B".
- Refresh uses a direct GET /api/campaigns (failures propagate; the error-swallowing
  `setups()` helper is no longer used here; the `moved` campaign notice is retained)
  and `load(true, relevant)`. A completed mutation followed by a failed refresh, or a
  reload that does not apply the expected setup scope, is a separate persistent
  `setup.<op>.refresh` error advising reload and not repeating the operation.
  Nothing is replayed.
- Guards: relevant only while the refresh ticket is current, the active campaign is
  unchanged and the encounter scope is unchanged or the expected `[campaign,
  campaign, setup]` transition (save: saved name; load: loaded name; rename: new name
  when the renamed setup was loaded; delete: server-opened setup). Duplicate clicks
  are ignored per operation through refresh; prior disabled states are restored.
- Preserved behavior: save keeps newer typing in the name field; load has no
  confirmation, an already-loaded no-op and restores the selection on request
  failure only if the user has not picked something else; rename keeps
  cancel/blank/unchanged no-ops, updates the name field only if it still held the old
  name, and reloads state when the loaded setup was renamed; delete keeps the
  existing confirmation wording and opens the server-selected replacement (or the new
  empty default).

### Source identity

Fragments, digests, bundle size pin (150,740 bytes from 2A), eight-fragment order
and the tracked static/admin.js failure marker are unchanged by 2B-2E.
static/setup-switch.js is 12,340 bytes; only its template URL gains `?v=1`.

### Verification executed locally on the prepared files

- tests/setup-switch.test.cjs adapted: failures are now asserted through the
  production controller instead of legacy paneNotification calls; payload, no-op,
  selection restoration, empty selection, no-confirmation and refresh-failure checks
  remain. It also fails if the error-swallowing `setups()` helper is used.
- New tests/setup-operations-feedback.test.cjs: 15 Node tests pass.
- Eight negative controls on static/setup-switch.js were run; seven were detected
  (campaign guard, refresh-error publication, disabled-state restoration, applied-
  scope check, unconditional selection restore, duplicate-click guard, target
  identity). The eighth (a pre-request predicted scope) was not detected because it
  was redundant and was removed from the source. The original pre-2B
  static/setup-switch.js fails all new Node and composition tests.
- New tests/test_setup_operations_feedback_composition.py: 4 full-Admin Chromium
  scenarios pass with intercepted HTTP.
- Through tools/run_split_tests.py on the cumulative 2A-2E files: `unittest discover
  -s tests -p 'test_*.py'` ran 1,559 tests, OK; all 79 JavaScript test files in one
  `node --test` run: 631 tests pass, 0 fail; the two pytest modules pass (43);
  the seven standalone scripts exit 0.

Same environment limits as 2A: local Python 3.14 / Node 20 / provisioned Chromium,
not CI, live-server, human visual or accessibility acceptance. Normal CI (no
[skip ci]).

### Remaining

Publication and covering-CI review of the cumulative 2A-2E commit; bounded
acceptance; setup copy/move and background controls; Stages 3-4; Deliverable 1
acceptance; Deliverable 2; 009.7/009 close-out. Test-suite cleanup stays deferred.

### Publication and covering CI (recorded 2026-11-12)

The cumulative 2A-2E files were committed by the user as
3adf212646aa8956ca6a42870c23075d5c482c9b on features/perplexity-009.7 (normal CI).
CI run 43272584707 attempt 1 (push event, headSha 3adf2126) succeeded; its published
evidence ci-results-43272584707-attempt-1 was committed as
1a6e562474fe3fb82d2a9f37b6d5493a70d2307c ([skip ci]). The reviewed log reports Python
1,559 tests OK, 79 JavaScript files with 631 pass / 0 fail and pytest 43 passed; the 10
committed files matched the archive byte for byte. Screenshots were not inspected.
Bounded Step 2 acceptance has not been given explicitly by the user and is not
recorded here.

## SG-TODO-009.7-S1-3 - setup copy/move and background controls - 2026-11-12

Status: implementation archive prepared on 1a6e562474fe3fb82d2a9f37b6d5493a70d2307c.
Archive only: no commit, push, dispatch, hosted CI result, deployment or acceptance
is claimed. These are the last Stage 1 producers that still used legacy
paneNotification feedback.

### Delivered behavior

- Owner: static/setup-switch.js (template URL now `/static/setup-switch.js?v=2`),
  installed independently per control group so missing nodes are tolerated.
- Copy/move (campaign region, page lane): `#openCampaignSetup` refreshes through a
  direct GET /api/campaigns; a failure or fewer than two campaigns ("Create a second
  campaign first; setups can only be added from another campaign") is a persistent
  `setup.transfer.open.validation` error and the modal stays closed. Source/target
  defaults and `renderCampaignSetupNames()` are unchanged.
- `#campaignSetupForm` submit keeps "Choose a battle setup" and "Source and target
  campaign are the same" as persistent `setup.transfer.validation` errors (target
  `["setup-transfer","selection"]`) and the exact POST
  `/api/campaigns/<to>/setups` `{setup, from_campaign, mode}`. Rejections are
  persistent `setup.transfer` errors (target `["setup-transfer", from, setup, to]`)
  and leave the modal open. Success ("Copied|Moved setup X to campaign Y[ as Z]")
  expires after three seconds; the modal closes only if it was not cancelled
  meanwhile (Cancel bumps a session counter); campaign data is replaced by the result.
- Moving the currently loaded setup (server clears the active setup) expects the
  `[campaign, null, null]` scope and runs `load(true, relevant)`; otherwise no state
  reload is needed. A failed or unapplied refresh is a persistent
  `setup.transfer.refresh` error ("... do not repeat the move ..."). The submit
  button is busy-guarded with disabled-state restoration.
- Background (battleSetup region, page lane, target `["view-background", campaign]`):
  the handler block that 030 `load()` rebound on every state load is removed;
  `setBackgroundInputs()` stays. `background.apply` (PATCH /api/display/background
  with the trimmed value or `#080b14`), `background.clear` (PATCH with the colour
  picker value) and `background.upload` (FormData `image`, POST
  /api/display/background-image, sets `#backgroundValue`, always clears the file
  input, silent without a file) keep their success texts, publish early, then
  `load(true, relevant)`; a refresh failure is a persistent no-replay error. One
  shared busy key disables all three controls. Results are suppressed after a scope
  change. The colour picker click/input behaviour is preserved. The 060
  `applyBackground()` helper is now unused but left in place (fragment unchanged).

### Source identity

Only 030 changes among fragments: 19,609 -> 17,529 bytes, sha256
ebbdb9ce89c287323b5bd6c1c5d343b4ea29703a53d3de9c738501a33119c155; bundle pin 150,740
-> 148,660 bytes. Eight-fragment order, the 20,000-byte limit, 050 (sliced by the
campaign-delete fixture) and the tracked static/admin.js failure marker are
unchanged. static/setup-switch.js is 19,346 bytes. Script inventory stays 43.

### Verification executed locally on the prepared files

- New tests/setup-transfer-background-feedback.test.cjs: 8 Node tests pass with the
  production controller. Negative controls detected: unconditional modal close,
  missing unloaded-setup refresh, missing file-input reset, separate busy key for
  clear, and a disabled duplicate guard.
- New tests/test_setup_transfer_background_composition.py: 3 full-Admin Chromium
  scenarios pass with intercepted HTTP (copy, rejected then successful move of the
  loaded setup, background apply/upload/refresh failure). They fail with the Step 3
  installers disabled, and the background scenario fails with the pre-Step-3 030
  (its `load()` rebinding the legacy handlers).
- Full-suite results are listed in the archive's Patch/CHANGES.md.

Same environment limits as before: local Python 3.14 / Node 20 / provisioned
Chromium, not CI, live-server, human visual or accessibility acceptance. Normal CI
(no [skip ci]).

### Remaining

Publication and covering CI of Step 3; explicit bounded acceptance of Step 2 and
Step 3, after which Stage 1 can be recorded closed. Then Stages 3-4, Deliverable 1
acceptance, Deliverable 2 and 009.7/009 close-out. Test-suite cleanup stays deferred.
