# 350 - Remove the 20,000-byte file splitting

[Back to TODO index](../../TODO.md) · [SG-TODO-008 size refactors](080-source-size-refactors.md) · [Admin split](../handover/050-admin-script-split.md) · [Storage split](../handover/240-sqlite-storage-split.md)

## Task and status

SG-TODO-035 - proposed 2026-11-22 by the user: "get rid of all the file splitting and split
files due to the 20k file size limit … roll all file splitting back." The limit was imposed
for the Perplexity git connector, which could not read larger files. Inventory made
2026-11-22 (below); no rollback done yet. Scope decisions are open (see the end).

## Origin of the limit

The limit first appears on 2026-11-01 (CI evidence chunking), then in the SG-TODO-008
refactors of 2026-11-02/03. The written policy is in
[080](080-source-size-refactors.md#size-policy-and-final-code-audit): new code files at most
20,000 bytes, existing files tolerated up to 25,000; the Admin reader at most 20,000 bytes
per fragment. It was never in `PERPLEXITY_INSTRUCTIONS.md` or `CLAUDE_INSTRUCTIONS.md`.

Not part of this: the October module split (PR #25, `features/split_code`: server,
`admin_*`/`service_*` modules and `templates/admin/` fragments). It predates the limit and is
a feature structure, not a size split. The `docs/handover/` and `docs/todo/` indexes (from
2026-11-01) are a documentation convention with no size reason recorded.

## Inventory

### A. Admin script, split into eight fragments and re-assembled (SG-TODO-008)

- Split files: `static/admin/010-source.js` … `080-source.js` (8 files, 132,480 bytes
  together; largest 19,692). `static/admin.js` is a 254-byte failure marker.
- Code that joins them: `python/scrying_glass_admin_source.py` (`ADMIN_SCRIPT_PARTS`,
  `MAX_SOURCE_BYTES`), `python/scrying_glass_admin_static.py` (`AdminScriptStaticFiles`, a
  generated bundle in a temporary directory), its mount in `scrying_glass_server.py`.
- Tool: `tools/run_split_tests.py` (copies the checkout and writes the assembled `admin.js`
  so legacy tests can read it). Used by every test step in `.github/workflows/tests.yml`
  (unittest, pytest, Node, scripts, connection audit) and by `tools/runlocaltests.sh`.
- Tests: `test_admin_source.py`, `test_admin_split_runtime.py`, the fragment checks in
  `test_admin_asset_wiring.py`; 30 test files read the fragments or `read_admin_script`
  directly (Node `.cjs` fixtures and Python tests).
- Docs: README "Source layout and deployment", handover 050, task 080; deployment needs a
  writable temporary directory for the bundle.

### B. SQLite storage, split into mixins (SG-TODO-008, 2026-11-03)

- `python/scrying_glass_storage.py` (facade, 5,017) with `_fields` (984), `_schema`
  (10,076), `_records` (13,068), `_operations` (12,218). `_statblocks` (4,864) was added later
  as a feature mixin, not a size split.
- Tests built for the split: `tests/storage_split_reference.py`,
  `test_storage_facade.py` (AST/identity checks of the facade, a 20,000-byte assertion),
  the former `*_preparation` tests (already consolidated in 600).
- Docs: handover 240, task 080.

### C. Documentation split for size

- `docs/Technical-Documentation.md` (31,226 bytes) became an index plus
  `docs/technical/010-…`, `020-…`, `030-…` (2026-11-03); test
  `tests/test_technical_documentation_split.py`. Many handovers link the three parts.
- `docs/handover/380-feedback-delivery-plan.md` (43,100 bytes) became 380 plus 381, 382 and
  383 (2026-11-11).
- README and DEPLOYMENT were shortened in the same 2026-11-03 commit; the removed history
  is in Git, not in a split file.

### D. CI evidence reader chunks

- `tools/chunk_ci_evidence.py` writes lossless 4,000-byte copies of every evidence file
  into `reader-chunks/` beside the originals (with `--verify`).
- Called by `tools/publish_ci_results.sh` (the `publish-ci-results.yml` workflow, every CI
  run) and `tools/getworkflow.sh`. Every `ci-results-*` publish commit carries them: the
  current one, `ci-results-45018908380-attempt-1/`, has 1,325 chunk files.
- Tests and docs: `test_ci_publication_branch_allowlists.py` and
  `test_local_runner_publication.py` cover the publication scripts; handovers 020, 021, 025
  and 9 others, tasks 010 and 100 describe the chunks.

### E. Size guards in tests

Assertions that a file is at most 20,000 bytes: `test_admin_asset_wiring.py` (all static
files and template fragments), `test_admin_source.py`, `test_admin_foundations.py`,
`test_admin_header_hierarchy.py`, `test_admin_panel_forms.py`, `test_admin_rosters.py`,
`test_battle_action_statistics.py`, `test_character_hp_display.py`,
`test_initiative_keyboard_navigation.py`, `test_monster_image_previews.py`,
`test_storage_facade.py`, `test_technical_documentation_split.py`.

### F. Files created small because of the policy

New code from 2026-11-01 onward was written to the 20,000-byte rule, often as several
modules or mixins from the start. Only two cases name the limit as the reason:
`static/monster-image-choice.js`, split from `monster-candidate-selection.js` ("fragment
size limit"), and the statblock service mixins `scrying_glass_statblock_discovering.py`,
`_preparing.py`, `_applying.py` and `_contract.py` (handover 084). Elsewhere the module
boundaries also follow features, so a size-only reason cannot be shown from the record.
Today 4 tracked code files are above 25,000 bytes, 18 between 18,000 and 25,000.

## Decisions needed

1. Categories A–E are mechanical; roll all back? (A: one `static/admin.js`, served as a
   plain static file, tests read it directly, `run_split_tests.py` removed. B: one
   `scrying_glass_storage.py`. C: rejoin both documents. D: stop chunking; earlier publish
   commits stay as history. E: remove the size assertions.)
2. Category F: leave as is (modules with feature boundaries), or merge named cases
   (monster-image-choice.js, statblock service mixins)?
3. Drop the size policy in task 080 and the README text, and record that the limit is gone.
4. Order: one commit per category, each with CI (A last or first, it touches the most
   tests), and an e2e run after A.
