# 530 - Stage 1 setup-operation feedback

[Back to handover index](../../HANDOVER.md)

Task record: [097 setup-operation delivery split](../todo/097-feedback-delivery-plan.md#stage-1-step-2-setup-operation-delivery-split---2026-11-12).
Accepted campaign Step 1 history: [520](520-campaign-operation-feedback.md).

## SG-TODO-009.7-S1-2A - create a new empty setup - 2026-11-12

Status: implementation archive prepared on base
1b54a2c4c47644c9ac0f72939043652d818cf337 (features/perplexity-009.7). Archive
only: no GitHub commit, push, workflow dispatch, hosted CI result, deployment or
acceptance is claimed here. The user applies, commits and pushes; the published SHA
and its covering CI are reviewed before the 2B archive.

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
- Save, Load/switch, Rename, Delete (2B-2E), setup copy/move and background
  controls are unchanged and still use their existing feedback paths.

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

### Remaining

2B save, 2C load/switch (effective static/setup-switch.js owner), 2D rename and 2E
delete with combined setup regressions; setup copy/move and background controls;
Stages 3-4; Deliverable 1 acceptance; Deliverable 2; 009.7/009 close-out. 2A
acceptance follows reviewed covering CI. Test-suite cleanup stays deferred.
