# 010 - Monster lookup accounts and candidate selection

[Back to TODO index](../../TODO.md)

## SG-TODO-001 - Account-backed monster lookup and explicit candidate selection

- Status: in progress; candidate-selection increment prepared, validation pending.
- Requested: 2026-11-01. Narrowed delivery agreed: 2026-11-02.
- Priority, owner and deadline: not assigned.
- Original account-backed scope: deferred/blocked on verified supported and permitted authentication and entitlement access.

### Original requested behavior retained

1. Allow adding a D&D Beyond account for monster searches.
2. Count accessible matching monsters, not inaccessible search hits.
3. Search D&D Beyond first. One accessible match is automatic; multiple accessible matches require explicit selection, without searching 5e.tools.
4. Only zero accessible D&D Beyond matches triggers 5e.tools. One fallback match is automatic; multiple fallback matches require selection.
5. Neither provider finding a match reports the outcome and preserves manual entry.

The original account-backed acceptance criteria remain open. Publicly retrievable
usable stats are not proof of access through a configured account.

### Agreed candidate-selection increment - 2026-11-02

Implement selection using existing public providers without credentials or account
entitlement claims. A usable candidate has parseable AC or HP. Enumerate all usable
matches for the primary provider, and search configured 5e.tools sources only after
a successful zero-result primary lookup (or when the primary provider is disabled).

| Primary usable matches | Fallback matches | Behavior |
|---|---|---|
| 1 | Not searched | Use automatically. |
| More than 1 | Not searched | Select from primary popup. |
| 0 | 1 | Use fallback automatically. |
| 0 | More than 1 | Select from fallback popup. |
| 0 | 0 | Report no match; retain manual entry. |

Provider errors stop lookup with a distinct outcome; they do not masquerade as
zero matches. Incomplete candidate enumeration is an error, not an incomplete
selection list. Cancel or Escape closes selection without applying a result or
triggering fallback. Species edits invalidate the selection. Preserve existing
AC/HP overwrite/edit-race guards and use the chosen candidate's image snapshot
through creation, even when that image is absent. Uploaded images take precedence.

### Acceptance and required validation

All completion boxes remain unchecked until supporting verification is reviewed.

- [ ] Original: add an account using verified supported/permitted authentication.
- [ ] Original: offer only candidates accessible to that configured account.
- [ ] Candidate increment: verify every zero/one/many row in the table.
- [ ] Verify deduplication, unusable results, independent provider flags and failed/incomplete searches.
- [ ] Verify popup selection, automatic handling, cancellation, species changes and manual entry.
- [ ] Verify existing-value protection and edits made while selection is open.
- [ ] Verify selected-image continuity, upload precedence, token expiry and no-image behavior through actual HTTP creation.
- [ ] Review full CI, real FastAPI route registration/authentication and live authorized provider/browser checks separately from mocks.

Automated offline and intercepted-HTTP Chromium fixtures are included. The final
committed fixtures have not yet been executed in the application environment.
Existing CI discovers test_*.py modules; do not skip CI for this delivery.

### Remaining account decisions and dependencies

Verify an authorized authentication/search mechanism; do not bypass access controls.
Account configuration scope (per administrator versus installation), connection,
disconnection, expired-session behavior and protected credential/session storage
remain deferred with account access. Do not store secrets in Git, logs or campaign
bundles. Revisit error policies if an authorized integration becomes available.

Candidate identifiers use source links, provider/source labels and legacy/current
metadata where available; D&D Beyond source-book names are not inferred. See
[implementation and limitations](../handover/200-monster-candidate-selection.md).
Earlier diagnostics repairs remain documented in
[monster lookup diagnostics](../handover/080-monster-lookup-diagnostics.md).
