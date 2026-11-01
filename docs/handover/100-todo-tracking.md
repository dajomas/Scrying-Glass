# 100 - TODO tracking initialization

[Back to handover index](../../HANDOVER.md)

Last updated: 2026-11-01.

## Documentation-only change

Initialize the root [TODO index](../../TODO.md) and numbered task sections under `docs/todo/`, following `PERPLEXITY_INSTRUCTIONS.md`. Earlier handover sections describing TODO.md as absent record the state before this initialization.

The first task is [SG-TODO-001 - Account-backed monster lookup and explicit candidate selection](../todo/010-monster-lookup.md). It records the user's requested D&D Beyond account support, selection among multiple accessible matches, fallback to 5e.tools when D&D Beyond has no accessible matches, and automatic use of a single match.

The task is proposed, not implemented. No owner, priority or deadline has been assigned. Authentication feasibility, account scope and error/cancellation policies remain decisions to resolve. Keep future task progress in the indexed TODO section rather than duplicating the backlog here.

## Delivery and validation scope

This commit changes only task and handover documentation. README was reviewed and remains accurate; no runtime behavior, credentials, source tests or workflow configuration is changed. No tests are claimed to have run for this documentation change.

The user explicitly requested `[skip ci]` for this documentation push. Do not dispatch an extra workflow or cancel a run from an earlier commit. The existing CI result for the StatsFallbackTests repair remains a separate matter and has not been verified by this documentation change.
