# Encounter logging correction

Apply this changed-files-only overlay after the six-feature encounter patch. It is compatible
with the subsequent Encounter tools layout patch; no HTML fragments, encounter-tools.css,
features.js, authentication, network configuration or database schema are changed here.

## Behaviour

- Mark concentrating records concentration-started rather than a generic combat-features event.
- Marking an already-concentrating combatant does not create another started event.
- Adding a concentration-linked effect that starts source concentration also records a start event.
- End concentration retains concentration-ended and lists the linked effect names removed.
- Feature changes name the changed fields and record actual before/after values: HP,
  temporary HP, life state, death-save successes and failures.
- Combined changes produce one readable feature-details entry plus a concentration event
  when the concentration flag changes.
- Effect add/remove/expiry events retain their effect names in note.
- The admin log gains a Details column that renders note using the existing HTML escape helper.
- CSV export includes note with the existing spreadsheet-formula protection.
- JSON export already includes the entire entry and requires no changes.

Examples:

    concentration-started | Concentration started
    combat-features       | Temporary HP: 0 → 7
    combat-features       | HP: 12 → 9; Temporary HP: 7 → 0
    effect-added          | Blessed
    effect-removed        | Blessed
    concentration-ended  | Concentration ended; removed linked effects: Blessed

Older effect entries already containing note show their names once the new renderer loads.
Older combat-features entries retain their existing JSON notes. Historical events are not
rewritten and missing historical details cannot be recovered by this patch.

## Files

Replacement files:
- python/scrying_glass_service_features.py
- python/scrying_glass_admin_activity.py
- static/admin.js
- static/admin.css

New files:
- python/scrying_glass_feature_logging.py
- tests/test_feature_logging.py

The service replacement depends on the feature_rules, feature_storage and campaign_bundle
modules from the earlier six-feature patch. This is not a standalone installation.
The replacements target the uploaded development baseline plus the supplied feature patches;
review local edits before overwriting them. The prior scoped Encounter tools stylesheet and its
head link stay in place, preserving the tidied layout.

## Apply

1. Stop Scrying Glass and back up the files listed above.
2. Extract at the application root, preserving folder structure.
3. Restart the service and hard-refresh the admin browser.
4. Mark a combatant concentrating, add/remove an effect, change temporary HP, and inspect Details.
5. Export CSV and confirm the note column contains the same descriptions.

No database migration or data reset is needed for this logging-only overlay.

## Validation

10 focused Python tests passed: start/end naming, duplicate suppression, combined feature/
concentration changes, readable HP/temp/life-state/death-save descriptions, the actual logger's
note preservation, and CSV note export/formula safety. All provided Python files compile.
Node syntax check passed for admin.js. A Node VM test exercised the actual modified renderer,
checking the Details column, HTML escaping, missing legacy notes and empty-log behaviour.
ZIP integrity is verified during packaging.

The entire 99-test feature regression suite and a live browser/server integration test were
not run in this logging-only build. The tests here cover the targeted logging changes, not an
end-to-end deployment certification.

Run the focused tests from the application root:

    python -m unittest discover -s tests -p 'test_feature_logging.py'
    node --check static/admin.js

Rollback: restore the four prior replacement files and remove the new helper/test if desired.
No database rollback is required.
