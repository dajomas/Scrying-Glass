# 332. Monster Edit dialog initiative bonus

[API integration](331-monster-initiative-edit-integration.md) |
[Task SG-TODO-018](../todo/180-monster-initiative-bonus.md)

Updated: 2026-11-07. Task remains in progress on features/perplexity-018.
No merge or write-back authorized.

## Covering baseline

Run 42354652224 attempt 1 reports success for exact commit
57e15259c968acf4ecadb0beb04271cd2f8dc515. Evidence folder
ci-results-42354652224-attempt-1 was read at publication commit
f7fd7ca5fd3141a91ba15ecf7c2b586494583ef2. All run.json steps, including
cleanup, report success. Individual counts were not audited in this increment.
This covers the API integration and FieldInfo assertion fix. Earlier run
42353635700 remains failed: the ModelField.required introspection error repeated
in two 1,192-test executions. Passing later evidence does not relabel that run.

## Dialog increment

An additive deferred script decorates the existing monsterEdit renderer and
editForm submit handler. It loads last, after the Admin scripts. Split Admin
sources, bundle assembly and character rendering/save behavior are unchanged.
Monster saves now use the authenticated Edit POST endpoint both with and without
an image; the former no-image PATCH path did not support bonus edits.

Bonus uses a signed whole-number text input to preserve the submitted string,
including values above JavaScript's safe-integer limit, without numeric coercion.
Server validation remains authoritative. Blank or exactly unchanged text is
omitted, preserving bonus/provenance; explicit changes are manual. The browser
does not submit an origin. The total is read-only and retains its existing value
in FormData, preventing this dialog from detaching a raw roll via total editing.
No raw roll, preview arithmetic or new gameplay bounds are introduced.

Submission captures FormData before disabling controls, prevents duplicate
monster saves, retains the dialog on rejection, and restores controls. A save
followed by refresh failure is reported as saved, not as a failed mutation.
Character saves delegate to the previously installed handler. No roster columns,
raw-roll transport, source refresh or active-order algorithm is added.

## Checks and limits

Node syntax validation passed. The native Chromium image/rejection/refresh-failure
method passed locally in a separate Python process. An initial notebook attempt
could not enter Playwright Sync API because the notebook has a running event
loop; the separate-process rerun passed without framework substitutes.
The larger native rendering/submission fixture at widths 375 and 1440 and the
script-inclusion method are prepared but not executed locally. Python test syntax
was parsed before the final removal of a redundant cleanup registration.
Normal CI discovers the test module; no new-stage CI result is claimed.

Browser fixtures use recorded transport and isolated form markup; they do not
prove authenticated live HTTP, assembled Admin/CSS usability, storage/restart,
actual calculation/order changes or production character-save integration.
Complete those checks and add read-only roster bonus, raw-roll/separate-total UI,
source refresh and remaining agreed acceptance before closing SG-TODO-018.
