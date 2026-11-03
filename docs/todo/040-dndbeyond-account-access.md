# 040 - Cancelled D&D Beyond account access

[Back to TODO index](../../TODO.md)

## SG-TODO-004 - Account-backed monster authentication and entitlement filtering

- Status: cancelled at the user's explicit request on 2026-11-03; not completed or implemented.
- Reason: after review, the user concluded that the investigated integration options were not viable for this project.
- Previously on hold at the user's request from 2026-11-02. Limited integration-options research was requested on 2026-11-03; implementation was not authorized or started.
- A supported and permitted authentication/search mechanism for Scrying Glass was not established. This is not a claim that no authorized integration could ever exist.
- Origin: unfinished account requirements carried forward from [SG-TODO-001](010-monster-lookup.md) at its agreed-scope close-out, 2026-11-02.
- Priority, owner and deadline: not assigned.
- Implementation and live account verification: not started; no account credentials were collected or account accessed during the options review.

### Cancellation and effect on delivered behavior

This task is removed from the active and held backlog. Do not resume investigation
or implementation without a new explicit user request. The cancellation supersedes
older on-hold/blocked references in continuity records. The record and historical
requirements remain for traceability rather than being deleted or marked passed.

The options review considered authorized direct integration, Avrae linking,
community importer/proxy approaches, browser/session bridges and permitted
user-supplied imports. It did not establish an implementation-ready supported
and permitted account-aware integration for Scrying Glass. The user's assessment
and cancellation are a project decision, not a universal technical/legal ruling.

Existing public-provider monster lookup, candidate selection, imports and manual
entry are unchanged. No account authentication, entitlement filtering, paid-content
retrieval or access-control bypass is delivered by this cancellation.

### Archived requirements - not active work

Allow adding a D&D Beyond account for monster searches using a verified supported
and permitted authentication/search mechanism. Offer only monsters accessible to
that configured account, not merely public search hits. Public-provider candidate
selection delivered by SG-TODO-001 is not account authentication or entitlement
verification and must not be described as such.

Retain D&D Beyond priority, automatic one-result use, explicit multiple-result
selection and fallback only after zero accessible primary matches. Define how
account/provider failures differ from a valid zero-match result; do not silently
change the delivered public-provider error policy when adding account support.

### Archived unresolved decisions

- Establish an authorized integration mechanism and its authentication/entitlement contract. If unsupported or unpermitted, retain the blocker; do not bypass access controls.
- Decide per-administrator versus installation-wide account scope.
- Define connection, disconnection and expired-session behavior.
- Choose protected credential/session storage; exclude secrets from Git, logs, exported bundles and documentation.
- Define account-authentication error handling and any explicitly permitted fallback policy.
- Verify entitlement-aware deduplication and preserve selected-candidate identity through stats/image lookup.
- Retain cancellation without applying a candidate or silently triggering fallback; revisit identifying metadata only if the authorized provider contract requires it.

### Archived acceptance criteria - not fulfilled by cancellation

- [ ] User explicitly lifts the hold before work resumes.
- [ ] Supported and permitted authentication/search access verified and documented.
- [ ] An account can be connected/disconnected with protected secret handling.
- [ ] Only account-accessible matching monsters are offered.
- [ ] Account-aware zero/one/many provider ordering and selected-candidate continuity verified.
- [ ] Expired sessions, authentication failures, provider errors and cancellation verified against the agreed policy.
- [ ] Deterministic offline/UI tests and authorized live account checks reported separately.

### Cancellation delivery and validation

This is a documentation-only status change. No application code, tests, workflows,
configuration or data are changed; no automated tests were executed. The user
explicitly requested [skip ci] for this cancellation commit. No separate workflow
is dispatched and no new CI outcome is claimed. README and the handover index
remain accurate and unchanged. See the
[current-state handover](../handover/010-scope-and-state.md) and the historical
[candidate-selection handover](../handover/200-monster-candidate-selection.md).
