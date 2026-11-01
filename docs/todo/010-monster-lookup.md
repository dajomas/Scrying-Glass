# 010 - Monster lookup accounts and candidate selection

[Back to TODO index](../../TODO.md)

## SG-TODO-001 - Account-backed monster lookup and explicit candidate selection

- Status: proposed.
- Requested: 2026-11-01.
- Priority: not assigned.
- Owner: not assigned.
- Deadline: not assigned.
- Implementation and validation: not started.

### Requested behavior

1. Allow adding a D&D Beyond account for monster searches.
2. If D&D Beyond returns multiple monsters accessible to that account, show a popup so the user can select the wanted monster.
3. If no accessible monsters are found in D&D Beyond, search 5e.tools. If it returns multiple matching monsters, show a popup to select the wanted monster.
4. For either provider, automatically use the result when exactly one accessible matching monster is found; do not ask the user to select the only result.

### Provider and selection rules

Count accessible matching monsters, not inaccessible search hits. Search D&D Beyond first. Search 5e.tools only when D&D Beyond produces no accessible matching monsters, rather than combining both providers into one selection list.

| D&D Beyond accessible matches | 5e.tools matches | Required behavior |
|---|---|---|
| Exactly 1 | Not searched | Use the D&D Beyond result automatically. |
| More than 1 | Not searched | Show the D&D Beyond selection popup; use the selected result. |
| 0 | Exactly 1 | Use the 5e.tools result automatically. |
| 0 | More than 1 | Show the 5e.tools selection popup; use the selected result. |
| 0 | 0 | Report that no match was found and retain manual entry. |

### Acceptance criteria

- [ ] An account can be added for D&D Beyond monster searches, using an authentication approach whose feasibility and permitted use have been verified.
- [ ] Only monsters accessible through the configured account are offered for D&D Beyond selection.
- [ ] A single D&D Beyond match is used without a popup and without a 5e.tools search.
- [ ] Multiple D&D Beyond matches produce a selection popup, and the selected monster is used without a 5e.tools search.
- [ ] Zero accessible D&D Beyond matches triggers the 5e.tools fallback.
- [ ] A single 5e.tools match is used without a popup.
- [ ] Multiple 5e.tools matches produce a selection popup, and the selected monster is used.
- [ ] Neither provider finding a match leaves manual entry available and provides a clear outcome.
- [ ] Verification covers the match-count table, inaccessible results, account/authentication failures and popup cancellation; the unresolved policies below must be agreed before those last two cases are finalized.

### Dependencies and decisions still required

These are implementation considerations, not additional user commitments or a claim that an account integration already exists:

- Verify a supported and permitted way to authenticate and search accessible D&D Beyond content. Record a blocker if that cannot be established; do not bypass access controls.
- Decide whether an account is configured per Scrying Glass administrator or for the installation, and define connection/disconnection and expired-session behavior.
- Decide how authentication or provider errors differ from a valid zero-match result, including whether an error should permit fallback.
- Decide popup cancellation behavior and which identifying fields distinguish candidates, such as provider, source book or edition where available.
- Choose protected credential/session storage. Do not put account secrets in Git, logs, exported bundles or documentation.
- Review search-result deduplication and how the selected candidate feeds the existing stat/image lookup without silently choosing a different candidate later.

### Validation plan

Add deterministic offline tests for provider order and zero/one/many accessible matches. Add UI tests for popup selection, automatic single-result handling and the agreed cancellation/error behavior. Perform any live account/provider verification only with authorized access; report mocked and live verification separately.

### Related handover

See [TODO tracking initialization](../handover/100-todo-tracking.md). Existing lookup diagnostic repairs are documented separately in [monster lookup diagnostics](../handover/080-monster-lookup-diagnostics.md); they do not implement this feature.
