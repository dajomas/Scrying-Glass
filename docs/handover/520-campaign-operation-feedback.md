# 520 - Stage 1 campaign-operation feedback

[Back to handover index](../../HANDOVER.md)

## Current: 1C.2 success/refresh archive - 2026-11-12

Base: bb1581d4bd21608d79bbb0a246776c8246697901, published 1C.1 verified on the live branch.
Earlier 1B publication: 385ad5690f2783c1bb22767cba80b2bae5dff0db; 1A creation:
3c144a2279adf9446bf0f0c082df9aa3065961c4. This archive completes the agreed
1C implementation only; publication/covering validation/bounded acceptance remain
pending. No GitHub write, new commit, hosted CI or deployment is claimed.

The complete prior foundation/1A/1B/1C.1 records, evidence and checkpoint limits
are preserved in the [pre-1C.2 record](https://github.com/dajomas/Scrying-Glass/blob/bb1581d4bd21608d79bbb0a246776c8246697901/docs/handover/520-campaign-operation-feedback.md).
That immutable history remains authoritative for earlier deliveries; historical
pending-publication wording is superseded only where actual publication is now
verified. [Current task and remaining scope](../todo/096-campaign-operation-feedback.md).

### Delivered behavior

campaign.switch success now precedes refresh, uses the existing name/setup wording
and expires after three seconds. campaign.switch.refresh has its own page-lane,
campaign-ID ticket; actionable errors persist until dismissal/matching recovery.
Success settles the mutation ticket, never used as a later relevance guard.
A successful activation followed by state/render failure remains visibly applied
and advises reloading, not reissuing activation. load(true) propagates refresh
errors; a refresh that fails to apply the new state is not treated as recovery.

Registry reference, selection revision (including away/return), encounter scope/
epoch and independent refresh ownership guard late work and errors. The single
expected activation transition is allowed before or during refresh; unrelated
transitions and leave/return cannot revive old work. Busy protection spans the
request and refresh and restores the prior disabled state. No automatic replay.

1C.1 selection validation, request errors, encoded activation endpoint, payload
absence, replacement confirmation and authorization transport remain. Opened and
empty setup paths preserve setup fields/rendering. The guarded switch follow-up
mirrors the existing setup-opening behavior without modifying shared
applyOpenedSetup or 040 (also used by deletion). Original 1A/1B source prefix is
byte-for-byte intact. No 1D, D2, polling, workflow or deferred cleanup work.

### Validation actually executed

- Node: 10 retained switch-request cases, 10 switch-refresh cases, 14 retained
  creation cases, 18 viewer-font cases and 9 encounter-context cases all pass.
- Four source identity/assembly/pin/tamper/syntax checks pass.
- Complete Admin through the production split runner and Chromium: 10 distinct
  scenarios pass (4 refresh, 3 request, 3 creation); request cases also exercise
  retained edit error/draft independence. An initial imported TestCase alias caused
  duplicate discovery; module imports now give ten distinct scenarios, not thirteen.
- Four negative controls detected: refresh ownership, selection revision, epoch,
  and refresh propagation. Removing ownership alone initially remained protected
  by controller publication guards; an empty-setup late-render case was added to
  detect the missing UI-work guard. Restored source passes all scoped checks.

The request fixture is shared with refresh tests. Retained assertions now inspect
explicit success/refresh outcomes rather than the retired legacy follow-up, and
simulate accepted state before resolving refresh; endpoint, confirmation, stale,
busy and setup assertions remain. No broad suite audit or assertion weakening.
These are scoped mocked/intercepted-HTTP checks, not full-suite/hosted CI,
authenticated live-server, human visual or screen-reader acceptance. Existing
Node/Python discovery includes new suites; no workflow edit or dispatch.

### Source and delivery

Only 080 changes among eight fragments: 17,448 UTF-8 bytes, SHA-256
5c5b72146278603c56412cb0a786051b222833c18ee20bfbca7157d146682c02.
Bundle: 141,967 bytes. Only corresponding digest/size pins change; order,
20,000-byte guards, other fragments and tracked failure marker remain unchanged.

Archive contains complete replacement files, full TODO/handover context, an exact
manifest/base Git-blob hashes, safe apply helper, source-review diff and local logs.
Current records link immutable prior history rather than duplicating it. Patch is
archive-only; do not stage it or use newzip.sh unchanged. No deletions/renames.
Intermediate message includes [skip ci]; final 1D retains normal push CI. Publish
and review covering evidence under the existing sequence, then bounded acceptance;
1D and wider open gates remain open. Accepted Stage 2/4A/009.1-009.6 stay closed.
Test-suite cleanup remains deferred; no new acceptance gate is introduced.
