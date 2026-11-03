# 010 - Scope and current state

[Back to handover index](../../HANDOVER.md)

Last updated: 2026-11-03.

## Repository and branch

- Repository: `dajomas/Scrying-Glass`.
- Working branch: `features/perplexity`.
- Keep changes scoped to this branch unless explicitly requested otherwise.

## Initial workflow record - 2026-11-01

The Branch tests workflow was added at `.github/workflows/tests.yml` in commit
8465afc86d19340a91433f6d4d7c4112de504a23. At the time of that initial handover
the first run had not been verified. Later feature-specific evidence and limits
are recorded in the corresponding numbered sections; this entry is not a complete
application audit.

## Application context

Scrying Glass is a self-hosted encounter manager with separate FastAPI Admin and
Client applications in one process, SQLite persistence and WebSocket updates.
The root entry point is scrying_glass_server.py. Runtime dependencies are in
requirements.txt; Python, Node and browser fixtures are under tests/.

## Documentation and packaging maintenance - 2026-11-03

The user accepted the Admin and Storage refactors as done. The live size audit at
9703102f1929aedd1887c17f1d7b4a8996dfc04b found no code files above the agreed
25,000-byte existing-file allowance. Temporary CI logs are excluded from refactor
targets and are not deleted by this maintenance. SG-TODO-004's subsequent
cancellation is recorded below.

Technical-Documentation.md is an index to three files under docs/technical/, all
below 20,000 bytes. The draft split reconstructed the exact 31,226-byte source
blob 7f9861b62a11c6efeb82fcb286f5abe300f4db2e and checked 25 compatibility links.
The text and historical validation limits are preserved, except for the required
relative-link rebasing; it is not a fresh technical audit. Preservation/link
regressions accompany the split. README and deployment guidance are refreshed as
current entry points; historical detail remains in Git and numbered feature handovers.

Manifest-dependent verification is retired. deployment/check.py now performs
runtime preflight by default, accepting --runtime as a compatibility alias. It
checks Python/sqlite3/dependencies and server import, not package integrity, live
startup or authenticated workflows. Four mocked contract methods passed locally;
this is not real dependency installation/server validation. The split regression
module parsed successfully; full repository CI was not rerun.

The user approved two commits with [skip ci]: first this documentation/preflight/
test delivery, then a separately confirmed deletion of the unused manifest. The
physical presence of any legacy manifest is not a dependency of the new tooling.
No separate workflow is dispatched, and this skip request is limited to those two
maintenance commits. No application runtime or storage behavior is changed.

## SG-TODO-004 cancelled - 2026-11-03

After a user-requested integration-options review, the user concluded that none
of the investigated approaches were viable for this project and explicitly
requested cancellation. [SG-TODO-004](../todo/040-dndbeyond-account-access.md) is
cancelled, not completed; older hold/deferred references are historical and
superseded by that decision. Its archived requirements and unfulfilled acceptance
criteria are preserved. No account-backed implementation or live account
verification was started, and no credentials were collected or account accessed.
Do not resume this work without a new explicit user request.

The delivered public-provider candidate selection, imports and manual entry remain
unchanged. This is a documentation-only cancellation: no code/test/workflow/data
changes, no automated tests executed and no new CI result claimed. The user
explicitly requested [skip ci] for this cancellation push; no workflow is
separately dispatched. The TODO index now contains seven completed tasks and one
cancelled task, with none active or on hold.

## Documentation entry points

- [README](../../README.md)
- [Deployment](../../DEPLOYMENT.md)
- [Technical documentation index](../Technical-Documentation.md)
- [User guide](../User-Guide.md)
- [Systemd deployment](../Systemd-Deployment.md)
- [Refactor task and acceptance](../todo/080-source-size-refactors.md)

Use live branch files as authoritative; older attachments may describe an earlier
architecture or Python requirement.
