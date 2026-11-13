# 560 - Deliverable 2 connection warnings and near-field validation

[Back to handover index](../../HANDOVER.md)

Task record: [097](../todo/097-feedback-delivery-plan.md#deliverable-2-implementation---2026-11-12).
Previous stage: [550 Stage 4 close-out](550-integration-accessibility-hardening.md#stage-4-accepted-close-out---2026-11-12).

## Status - 2026-11-12

Completed and closed for the agreed Deliverable 2 scope following the user's explicit
"Accept and close Deliverable 2" request on 2026-11-12 at 22:43 CET after the green
covering-CI review. Earlier archive-only, publication/CI/acceptance-pending notes are
superseded; do not request Deliverable 2 acceptance again. Stages 1-4 remain closed.
Whole Deliverable 1 integrated review/acceptance and final 009.7/009 review,
documentation and acceptance remain open; Deliverable 2 does not satisfy them.

## Deliverable 2 accepted close-out - 2026-11-12

Implementation: 8da0657325818c69fc82dc1234995a5146e88ebc on
features/perplexity-009.7. Successful covering Branch tests 43310602854 attempt 1,
job 131505374358; evidence publication dbb78d3057a2d38527bd612b948a6566a1a741e3,
directory ci-results-43310602854-attempt-1. Reviewed run.json and jobs.json agree
on branch, tested SHA, attempt, completed status and success. All configured
Chromium provisioning, syntax/import, main Python/browser, pytest, JavaScript and
standalone browser/audit stages succeeded. Completion: 2026-11-12T21:37:28Z
(22:37 CET). The review did not individually re-review every test log/screenshot or
recount tests; no new authenticated live-server, human visual, screen-reader or
exhaustive accessibility evidence is claimed. Local fixture/audit results below
remain preparation evidence, not new executions or universal end-to-end coverage.

Accepted scope: the Admin background poll's persistent connection warning, matching
recovery and deduplication, explicit warning severity and field-selector contract,
near-field association/cleanup/re-render handling and the listed producer integration.
All limits below remain explicit: Client Display reconnect behavior is outside this
Admin plan; bulk operations have no single-field association; general HTTP detail is
not parsed into a guessed field. Existing gates, endpoints, payloads, permissions,
combat behavior, drafts and selections are unchanged.

Originally prepared as SG-TODO-009.7-D2.zip on 52061a68 at the user's request
"Now that stage 4 is closed, please implement Deliverable 2 and provide an archive".
The user requested this before whole Deliverable 1 integrated review; that review
and acceptance remain open. No Deliverable 2 implementation/publication/covering-CI/
acceptance action remains. This documentation-only close-out uses [skip ci], runs
no new tests and changes/dispatches no workflow. No application/test/template/asset/
pin/permission/assembly change, merge, deployment or blanket future write approval;
no new run outcome or close-out commit SHA is invented before publication.

Continuation: whole Deliverable 1 integrated evidence review and acceptance, then
final integrated evidence/corrections, documentation and explicit 009.7/009 acceptance
under [097](../todo/097-feedback-delivery-plan.md#remaining-scope-and-gates). No optional
scope or new acceptance gate; test-suite cleanup remains deferred until after 009.

## Scope

Approved policy items 5-8 (097): connection warnings persist while the problem exists
and clear on recovery; identical polling failures update one warning without duplicate
notices/announcements; near-field validation identifies the field/combatant and clears
when resolved; stale responses, recovery events and timers cannot overwrite/clear newer
or another campaign/setup's feedback. Existing initiative/server gates, endpoints,
payloads, combat rules, permissions, drafts and selections are unchanged.

## Connection warning (background poll)

- The Admin's only background poll is the Encounter tools refresh in `features.js`
  (`/api/state` + `/api/features` every 3 s; ?v=6). Its failures previously wrote
  text into the on-demand tools-dialog `#featureNotice`, which is not visible while the
  dialog is closed, and repeated every poll.
- Now one explicit identity owns the warning: page lane, global region,
  `connection.poll` / `server`, label "Server connection", new severity `warning`
  (persists like an error; no timer). Page lane means campaign/setup scope changes do
  not clear it, and it never touches encounter-lane records.
- Classification is by request outcome, never message wording: a rejected `fetch` is
  marked `connectionLost` ("Connection to the server was lost. Retrying
  automatically."); an HTTP failure keeps its detail ("Background refresh failed:
  <detail>. Retrying automatically.").
- Deduplication: an identical failure publishes nothing (the frozen record is kept, no
  controller notification, so no re-render or new live-region addition), also after the
  user dismissed it. A different failure replaces the record in place (one record).
- Recovery: the next successful refresh (background or manual) publishes a global
  success "Connection to the server restored." on the same identity (5 s), which removes
  only the warning; unrelated global, pane and page-lane errors stay. Successful polls
  without an outstanding warning publish nothing.
- Manual Refresh in Encounter tools keeps its Stage 3 tools-region error and does not
  raise the connection warning. Polls stay serialized by the existing `polling` promise,
  so an older poll cannot complete after a newer one. `#featureNotice` remains only as
  the fallback when the feedback API is absent.
- The global `state.load` error of the core Admin is a separate identity; recovery does
  not clear it (policy 8).

## Near-field association

- `admin-feedback-controller.js` (?v=2): an optional explicit `field` selector on
  `begin` is carried on the ticket and record (omitted when not supplied; a non-string
  or blank value throws). `warning` joins success/error/info as an explicit severity.
- `admin-feedback-view.js` (?v=2): record text nodes get stable ids; `warning` title.
- `admin-feedback-admin.js` (?v=6): for every current error/warning record with a
  field, the matching control gets `aria-invalid="true"`, the record's hint id is added
  to `aria-describedby` (existing tokens kept) and a non-live `span.sg-field-error`
  with the record text is inserted directly after it. The record in its global/pane
  region stays the single live announcement. Removal by dismissal, matching
  resolution, replacement or a lane scope change restores the prior `aria-invalid` and
  `aria-describedby`. A MutationObserver (only while associated records exist)
  re-associates controls replaced by roster re-renders. Helpers: `field(node|form)`
  (id selector, or `#form [name=...]`, or the first `:invalid` control of a form) and
  `initiativeField(kind, id)` (`input[data-ci|data-mi="<id>"]`).
- Associated producers (field explicitly chosen by the producer, never inferred from
  text):
  - Join gate (`initiative-join-gate.js?v=2`): single-combatant Join errors (blocked
    click and single PATCH rejection) -> that combatant's initiative input. Bulk Join
    keys stay unassociated.
  - Monster raw roll (`monster-initiative-roll.js?v=3`): validation -> the monster's
    raw-roll input; the text now starts with the monster name.
  - Monster Edit (`monster-initiative-edit.js?v=2`): first constraint-invalid field.
  - Setup save/load/rename/delete/transfer validation (`setup-switch.js?v=4`): the
    control it already focused, when that is an input/select/textarea.
  - Fragments: 060 setup New (`#setupName`) and entry forms (first invalid field or the
    prepared focus control); 040 modal imports (first invalid field when the browser
    constraint fails); 080 campaign create/edit (name or first invalid field) and
    campaign switch/edit-open selection (`#campaignSelect`); 050 campaign delete
    (`#campaignDeleteTarget` / `#campaignDeleteMoveTo`).
- `admin-feedback.css` (?v=2): warning accent, hint style (no inherited strike-through),
  outline on invalid controls.

Producers call the helpers optionally (`feedback.field?.()`), so existing test doubles
without them keep working; production always provides them.

## Assembly

Still eight fragments, each below 20,000 bytes (040 16,816; 050 10,472; 060 17,946;
080 17,802; total 131,939). `static/admin.js` marker unchanged. Script inventory stays 44.
`tests/test_admin_source_preparation.py` bundle bytes and digests updated.

## Tests

- New `tests/connection-feedback.test.cjs` (9): real controller/bootstrap with
  `features.js`; network/HTTP loss, identical-failure dedup (no notification),
  replacement, recovery keeping unrelated errors, quiet healthy polls, dismissal,
  scope independence and manual Refresh.
- `tests/admin-feedback-controller.test.cjs` (+2): warning persistence/identity and the
  field contract.
- New `tests/test_admin_deliverable2_composition.py` (4, loaded Admin in Chromium with
  intercepted HTTP): raw-roll association, re-association after `load(true)` and
  clearing on resolution; blocked Join association cleared by Dismiss; setup-name
  association preserving a prior `aria-describedby`; poll connection loss shown once in
  `#message`, unchanged over further failing polls, then recovered without clearing an
  unrelated global error.
- Version pins updated in the encounter-context, composition, bonus-edit and raw-roll
  composition tests.
- Local results and negative controls are recorded in the archive's Patch/CHANGES.md.

## Limits

- HTTP is intercepted in all browser tests; no authenticated live-server, human visual,
  screen-reader or exhaustive accessibility verification. A local axe colour-contrast/
  ARIA check of the hint and warning in the loaded fixture found no violations; it is
  preparation evidence only.
- Only the Admin background poll is covered; the Client Display portal's own
  WebSocket reconnect status is unchanged and outside this Admin plan.
- Server-side validation errors returned as HTTP detail stay in their region without a
  field, except the single Join rejection; no field is inferred from server text.
- Bulk operations are not field-associated (no single control).
