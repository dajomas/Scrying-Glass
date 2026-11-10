# 190 - Activity log affected unit and resulting value

[Back to TODO index](../../TODO.md)

## SG-TODO-019 - Include the affected unit and new value in Activity log lines

Status: proposed. Requested by the user on 2026-11-10 as a backlog addition while awaiting CI. Not implemented. No priority, owner, deadline or position in the agreed delivery sequence has been assigned.

### Requested behavior

In each Activity log line describing a value change, identify the affected unit/combatant and include the resulting new value. Make clear which property changed; retain the measurement unit where applicable. Here, affected unit means the character, monster or other encounter entity impacted, not merely the numeric unit of measurement.

### Acceptance criteria and planned validation

- Relevant value-change entries identify the affected unit/combatant, the changed property and its resulting value in the same line.
- Report the actual resulting value after the operation, not just the requested change or delta.
- Entries remain distinguishable when similar units or multiple affected combatants are involved.
- Preserve combat behavior, permissions and existing log history; the logging enhancement must not apply an operation again.
- Before implementation, inspect the actual log producers and agree any unresolved coverage details. Add focused regressions for the affected producers and verify readable Activity log output for representative changes, including multiple affected units.

This records requested future work only. No application or test files are changed and no tests are executed for this backlog addition. Existing 009.7 work, acceptance status and CI results remain separate; no current CI outcome is claimed.
