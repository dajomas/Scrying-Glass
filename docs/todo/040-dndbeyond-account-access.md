# 040 - Deferred D&D Beyond account access

[Back to TODO index](../../TODO.md)

## SG-TODO-004 - Account-backed monster authentication and entitlement filtering

- Status: on hold until further notice, explicitly requested by the user on 2026-11-02.
- Do not resume investigation or implementation unless the user lifts the hold.
- Underlying integration blocker remains: supported and permitted authentication/search access has not been established.
- Origin: unfinished account requirements carried forward from [SG-TODO-001](010-monster-lookup.md) at its agreed-scope close-out, 2026-11-02.
- Priority, owner and deadline: not assigned.
- Implementation and live account verification: not started.

### Requirements retained

Allow adding a D&D Beyond account for monster searches using a verified supported
and permitted authentication/search mechanism. Offer only monsters accessible to
that configured account, not merely public search hits. Public-provider candidate
selection delivered by SG-TODO-001 is not account authentication or entitlement
verification and must not be described as such.

Retain D&D Beyond priority, automatic one-result use, explicit multiple-result
selection and fallback only after zero accessible primary matches. Define how
account/provider failures differ from a valid zero-match result; do not silently
change the delivered public-provider error policy when adding account support.

### Dependencies and unresolved decisions

- Establish an authorized integration mechanism and its authentication/entitlement contract. If unsupported or unpermitted, retain the blocker; do not bypass access controls.
- Decide per-administrator versus installation-wide account scope.
- Define connection, disconnection and expired-session behavior.
- Choose protected credential/session storage; exclude secrets from Git, logs, exported bundles and documentation.
- Define account-authentication error handling and any explicitly permitted fallback policy.
- Verify entitlement-aware deduplication and preserve selected-candidate identity through stats/image lookup.
- Retain cancellation without applying a candidate or silently triggering fallback; revisit identifying metadata only if the authorized provider contract requires it.

### Acceptance and validation

- [ ] User explicitly lifts the hold before work resumes.
- [ ] Supported and permitted authentication/search access verified and documented.
- [ ] An account can be connected/disconnected with protected secret handling.
- [ ] Only account-accessible matching monsters are offered.
- [ ] Account-aware zero/one/many provider ordering and selected-candidate continuity verified.
- [ ] Expired sessions, authentication failures, provider errors and cancellation verified against the agreed policy.
- [ ] Deterministic offline/UI tests and authorized live account checks reported separately.

This is preservation of deferred work, not a commitment to implement an unsupported
API or to retrieve purchased content without authorization. Related delivered
behavior and limits: [candidate-selection handover](../handover/200-monster-candidate-selection.md).
