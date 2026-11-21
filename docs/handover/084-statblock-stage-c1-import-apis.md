# 084 - SG-TODO-022 Stage C1: discovery, preparation and apply APIs (022.08)

[Back to handover index](../../HANDOVER.md) · [Stage B](083-statblock-stage-b-sources.md) · [TODO 220](../todo/220-admin-statblock-viewer.md)

Date: 2026-11-17. Baseline: `9c2845ea363a33f54f5a2bb6abb426b36ba95c70` on
`features/claude-statblock`. Delivered as a zip archive; commit SHA not yet known.
CI not run (`[skip ci]`, agreed for Stages A-E until the last code delivery).

## Scope and staging

The user asked for "Stage C1". The repository defines Stage C as 022.08-022.09
but no C1/C2 split, so this delivery reads C1 as **022.08** (source resolution
and authenticated apply APIs). **C2 = 022.09** (the protected 3200 listener, its
read/transport wiring and port/deployment handling) is not started. Confirm or
correct this split before C2.

Not usable yet: no Admin UI calls these routes (Edit Monster import is 022.13,
bulk import 022.14) and no viewer renders statblocks (022.10-022.12).

## Delivered

- Routes on the Admin app (`scrying_glass_statblock_routes.py`, installed by
  `AdminAPI`): `GET /api/statblocks/state`, `GET /api/statblocks/monsters/{id}`,
  `POST /api/statblocks/discover`, `POST /api/statblocks/prepare` (JSON candidate
  or multipart `.monster`, 202 with a job), `GET`/`DELETE /api/statblocks/jobs/{id}`,
  `POST /api/statblocks/apply`. Summary in
  [technical 020](../technical/020-apis-workflows-validation.md#statblock-import-sg-todo-02208-admin-app).
- `scrying_glass_statblock_service.py` (authorization, encounter token, reads) with
  mixins `..._discovering.py`, `..._preparing.py` (jobs, isolated runners) and
  `..._applying.py` (atomic apply, Edit Monster staging); shared envelope and
  constants in `..._contract.py`. Each file stays below 20,000 bytes.
- `scrying_glass_statblock_limits.py`: the 26 agreed `statblocks.limits` keys with
  their defaults, validated by `load_config` (unknown/invalid values stop start-up);
  named constants for the retained bounds (5 MiB `.monster`, 50 apply targets,
  1 MiB apply body, 3 redirects). `config.example.yaml` lists every key.
- `scrying_glass_statblock_fetching.py`: one application-wide `SharedFetcher`
  (4 outbound / 2 per provider, in-flight deduplication with per-consumer deadlines,
  bounded LRU for responses and conversions, 30 s failure cooldown with retry time).
- `scrying_glass_statblock_jobs.py`: 2 active / 16 queued jobs, round-robin by
  session, deadline from acceptance (queue time counts), cancel queued/running.
- `scrying_glass_statblock_selections.py`: in-memory candidates, immutable prepared
  snapshots shared by digest, selection references (per session/global), apply
  outcomes; capacity rejects, never evicts another user's selection.
- `scrying_glass_statblock_discovery.py`: provider switches/endpoints, exact
  identities, the tracker's retained source as the "original" candidate, and
  per-provider discovery (5e.tools index + configured sources, Open5e v2, public
  D&D Beyond search) with `complete`/`partial`/`error`/`cooldown`/`disabled` status.
- `scrying_glass_statblock_worker.py`: Open5e, D&D Beyond and `.monster`
  preparation in a prlimit-bounded child (same enforcement as the 5e.tools worker,
  which is reused unchanged); the parent fetches only allowlisted HTTPS URLs.
- Edit Monster (`scrying_glass_monster_initiative_edit.py`) accepts optional
  `statblock_selection_id`, `statblock_operation_id`, `statblock_expected_revision`
  and `expected_values`; the statblock is saved in the same transaction as the edit.
- `transactional_handler` gained commit callbacks (run after commit, under the
  operation lock) so selections are consumed and outcomes recorded only on success.
- Logout revokes the session's candidates, selections, outcomes and jobs.
  `apply_statblocks` is an undo-tracked operation ("Apply statblocks").

## Decisions

- Encounter token: HMAC (per-process key) of the active campaign and the active
  setup reference. A restart, campaign switch or setup change invalidates it.
  Reloading the same setup keeps it; bindings are still rechecked against the
  monster, species, tracker source identity and statblock revision.
- `GET /api/statblocks/state` and `/monsters/{id}` are implemented on the Admin app
  now because import needs the encounter token and revisions. The state response
  adds `monsters` (every monster's revision/status) next to the contract's
  membership `tiles`. 022.09 mounts these reads on the protected listener.
- Job polling (`GET /api/statblocks/jobs/{id}`) and cancel (`DELETE`) are added;
  the contract named only prepare's job_id/status.
- Apply validates every row before writing; any failing row rejects the request
  (`apply_rejected` with per-row items, status of the rows or 409 when mixed).
- Outcome replay: identical `(session, operation_id, request digest)` returns the
  recorded result until the consumed selections' original expiry; failed attempts
  are not recorded.
- Provider switches are checked at discovery, preparation and apply; disabling a
  provider never deletes saved snapshots. Configuration changes (data root, Open5e
  endpoint), adapter versions and limits are part of conversion-cache keys.
- Failure cooldown is per exact request URL. Discovery deadline: one
  `preparation_seconds` budget per discovery request.
- Engineering safeguards that are not agreed limits (proposed here; **agreed by the user 2026-11-20** as fixed constants, see TODO 220):
  32 candidates per provider and species, 4,000 held candidates (2,000 per session,
  a session at its cap loses its own oldest), failed job records kept 60 s (64 at most).
- Preparation needs Linux with `prlimit` (as the Stage A worker). Elsewhere (for
  example the Windows launchers) every job fails with
  `worker_enforcement_unavailable`; nothing runs without the memory/CPU bounds.
- 5e.tools `_versions` are still not offered as candidates; discovery reports
  `omitted_versions` so the list is not presented as exhaustive.

## Validation (Python 3.13.18, this environment)

- `tests/test_statblock_import_core.py` (16 tests: limits, shared fetcher, scheduler,
  selection store), `tests/test_statblock_import_service.py` (18 tests on native
  SQLite: authorization, discovery, prepare/apply/replay/conflict/tamper/expiry/
  capacity, atomic rejection, failed-transaction retention, Edit staging, reads) and
  `tests/test_statblock_import_workers.py` (5 tests through the real isolated workers:
  a `.monster` file, captured Open5e/D&D Beyond goblin responses, the Stage A
  synthetic 5e.tools dataset, plain-state attach): all 39 pass.
- `tests/test_statblock_import_http.py` (5 FastAPI route tests: envelopes,
  same-origin, body limits, multipart, job cancel, Edit Monster route): **not run**;
  FastAPI and python-multipart are not installed here and cannot be installed.
- Regression comparison, every `tests/test_*.py` module run separately here, baseline
  worktree at `9c2845e` versus this change: 158 of 239 modules pass at the baseline and
  the same 158 pass after it (plus the new core and service modules); the other 81 fail
  identically in both (missing FastAPI, aiohttp, httpx2 or PyYAML). JavaScript tests
  were not run (no JavaScript changed).
- Not run: CI, Python 3.14, e2e, live provider requests.

## Open work

- 022.09 (Stage C2): delivered later the same day, see [085](085-statblock-stage-c2-listener.md).
- 022.13/022.14 UI; 022.12 automatic original-source loading uses `prepare` with
  the original candidate.
- 5e.tools `_versions` candidates (needs version expansion in the adapter).
- Agreement on the proposed safeguards above and Stage A's `dataset_files` (agreed 2026-11-20).
