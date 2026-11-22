# 720 - 5e.tools monster versions (SG-TODO-033 part 1)

[Back to HANDOVER index](../../HANDOVER.md)

Implementation group 4, part 1, on `features/claude`, 2026-11-22. Decisions:
[330](../todo/330-fivetools-variants.md#decisions-2026-11-21).

## Runtime behaviour reproduced

`DataUtil.monster.getVersions` (5etools-src 32ef600, js/utils.js): the resolved monster's
`_versions` plus the versions its `variant` entries declare with `_version` (addAs /
addHeadersAs); `_abstract` + `_implementations` expand with `{{variable}}` substitution in
string values. Each version is `copyApplier.getCopy(parent, version)` where the parent lacks
`_versions`, `hasToken`, `hasFluff`, `hasFluffImages`, its source lists drop the version's own
source, and `_preserve` defaults to `{"*": true}`; the result gets the `_versionBase_*` fields.

## Code

- New `python/scrying_glass_fivetools_versions.py`: `version_specs`, `version_names`,
  `resolve_version`. The copy runs through the existing `OrderedResolver` over a two-record
  loader (stripped parent + synthetic version) that delegates templates to the dataset, so
  the `_copy` semantics are reused exactly and the main resolver cache never holds a stripped
  parent.
- `FiveToolsData.records(kind, source)` and `Collector.resolve_selected(name, source,
  version_of)`: an exact monster wins; a version is prepared from its base, given
  (`version_of`) or searched among the monsters stored with the version's source.
- `prepare_statblock(..., version_of=None)`, `prepare_isolated(..., version_of=None)` (sent in
  the worker head) and the 5e.tools runner pass the identity's `version_of`.
- Discovery (`_fivetools`): a monster matching the species brings all its versions; a version
  whose own name matches is offered alone. Version identities are
  `{root, name, source, version_of: {name, source}}`; `identity_key` stays name/source (all 368
  version identities are unique and none equals a monster). 5e.tools summaries now carry
  `name`; versions carry `version_of` (with `label`). `omitted_versions` now counts only
  versions that could not be expanded or did not fit the 32-candidate limit.
- Original source: a 5e.tools link to a version already resolves to that version's
  name/source; when discovery found the same version, the original entry takes its identity
  and summary (with `version_of`) and keeps `original: true`.
- Admin: `groupCandidates` and `candidateLabel(candidate, {grouped})` in
  `monster-statblock-common.js` (v=3). Edit Monster lists a base's versions in a closed
  `details.monster-statblock-versions` under it (`monster-statblock-edit.js` v=3); Load
  statblocks uses an `optgroup` "Versions of …" (`monster-statblock-bulk.js` v=3); a version
  without its base listed is labelled "— version of X (SRC)". CSS
  `monster-statblock-import.css` v=4.

## Evidence (pinned runtime, local checkout of 5etools-src 32ef600)

- `tools/fivetools_oracle/version_oracle.mjs` + `compare.py versions`: 368 of 368 versions
  identical to the runtime, key order included; the discovery name list equals the runtime's
  version set (0 missing, 0 extra). `compare.py copies` unchanged: 1,161 of 1,161.
- Every version prepared through `prepare_statblock`: 368 of 368 with the base given; 4 with
  `reference_unavailable` warnings (generated magic items, part 2).
- Known limit: by name alone (auto-load of an original source) 352 of 368 prepare. The 16
  others are versions from another book than their base (for example Beholder (Variant
  Abilities)|VGM on Beholder|MM); their base is in a different file. Find statblock offers them
  with their base, so choosing them works.

## Tests

- New `tests/test_fivetools_versions.py` (12): spec expansion and order, template variables,
  malformed versions, resolution (copy, modifications, stripped fields, source lists,
  `_versionBase_*`), preparation with and without the base and through the isolated worker,
  discovery by base and own name, omitted count.
- `tests/test_statblock_import_service.py`: an original 5e.tools link to a version keeps its
  base, is not duplicated, and prepares with `version_of`.
- `tests/test_statblock_import_browser.py`: Edit chooser groups versions under the base; Load
  statblocks uses an option group.
- Full unittest suite here: 2,147 tests, no new failures; Node tests as on HEAD; connection
  check clean. CI 44960931606 green on 9e8eb26.

## Close-out

Group 4 completed and closed 2026-11-22: CI 44964454668 green on 69624cf (both jobs); the
user's e2e run 20261122T073821Z on 29b52d9 (69624cf plus its CI results commit): 137 passed,
0 failed, 0 skipped (Chromium and Firefox).
