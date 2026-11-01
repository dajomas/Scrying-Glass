# 010 - Scope and current state

[Back to handover index](../../HANDOVER.md)

Last updated: 2026-11-01.

## Repository and branch

- Repository: `dajomas/Scrying-Glass`.
- Working branch for this handover: `features/perplexity`.
- Keep changes scoped to this branch unless explicitly requested otherwise.

## Work completed in this session

A GitHub Actions workflow was added at `.github/workflows/tests.yml` in commit `8465afc86d19340a91433f6d4d7c4112de504a23`, with message `ci: run all tests on pushes to features/perplexity`. The GitHub write succeeded. The first workflow run and its results have not been verified.

This handover records that workflow and the required modular documentation convention. It is not a complete audit of the application or a claim that the test suite passes.

## Application context

The current branch README describes a self-hosted encounter manager with separate FastAPI Admin and Client applications in one process, SQLite persistence and WebSocket updates. The root entry point is `scrying_glass_server.py`. Runtime dependencies are declared in `requirements.txt`; Python, Node.js and browser tests live under `tests/`.

## Existing documentation

- [Repository README](../../README.md)
- [Deployment package](../../DEPLOYMENT.md)
- [Technical documentation](../Technical-Documentation.md)
- [User guide](../User-Guide.md)
- [Systemd deployment](../Systemd-Deployment.md)

Use live branch files as the source of truth. Older project attachments may describe an earlier architecture or different Python requirements.
