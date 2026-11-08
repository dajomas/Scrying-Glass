# 335 - 5e.tools initiative extraction correction

[Back to handover index](../../HANDOVER.md)

2026-11-08. [SG-TODO-018 A.1](../todo/185-monster-correction-plan.md).
Branch features/perplexity-018; baseline 3486eaee2303d1caa3f031bf0867e4fb3710b3b3.
Implementation delivered; first CI failed, fixture correction included with new CI/acceptance pending. No close-out or merge/write-back.

## Evidence and behavior

Supplied bestiary-xmm.json SHA-256:
b616645bb1b81031f55d23e4d226a5453a02da01318fd0a463a64981a9d7eee3.
Supplied render.js SHA-256:
7c46f9ac9312c0d9271b1ca915693fc7e1426ce9dbe0f381999ff84f2fa55f1c.
Neither file is bundled. Noble Prodigy explicitly has proficiency=1, dex=16,
cr="10": +3 + 1*4 = +7. Passive initiative 17 is not the roll bonus.

The new helper validates explicit totals or proficiency multipliers 0/1/2.
Missing initiative does not use the renderer's Dexterity fallback. Explicit zero
is available; unsupported data/copies are not. Advantage affects passive score,
not the roll bonus. Candidate extraction feeds existing signed creation offers
and exact-source Refresh preview/apply/storage. No UI, schema, review defaults,
HP-generation, provider-enable or character changes; A.2/A.3 and stage B remain.
README, 180/330 history, TODO index and CI were reviewed and remain unchanged:
existing contracts, fallback-only lookup, links and overall pending status remain.

## Initial preparation validation (historical)

Ten pure unit methods passed. Offline supplied-XMM scan: 503 entries, 187 available,
316 missing; Noble Prodigy +7. Prepared Python AST parsing passed; files are below
20,000 bytes. Original candidate/input blobs were verified before editing.
Two secured ASGI/SQLite methods are prepared, not executed: FastAPI is absent.
They use real candidate/creation/preview/apply/reopen paths, mocked JSON transport,
existing fixture HP/image operations and pre-seeded sessions. They cover +7,
zero/negative, raw recalculation, unchecked fields, missing/invalid and exact edition.
This is not live-provider, login, browser, TCP or new-process restart evidence.
Existing CI discovers both new test modules; covering CI and visual/workflow
acceptance remain pending. Normal CI applies, without skip/workflow changes/dispatch.

## Failed CI and fixture correction - 2026-11-08

Verified run 42496852926 attempt 1, branch features/perplexity-018, tested
7fb5c1ce9c2cddd2275dac4520b6b3b10ad2fcfd. Publication:
6d4b882e0c9591c8d7172a57a9322605dbcb881d / ci-results-42496852926-attempt-1.
The ten pure initiative methods passed. Both new ASGI/SQLite methods errored
before their intended workflows: the reused fixture assigns self.candidate to a
dict, shadowing candidate(). Four extracted source-configuration methods errored
at the new relative import because their exec namespace lacked package metadata.
Main suite: 1,375 tests, six errors; repeated suite reports the same six errors.
Syntax/server import, pytest and JavaScript steps succeeded. Standalone audit
step failed; connection tracking 738 opened/0 without explicit close does not
make it pass. Python/Node post-setup steps were skipped. No green-CI claim.

Evidence under reader-chunks/file-000026: parts 64-65 show test outcomes;
98-101 show exceptions/main summary; 133 shows repeated summary/connection count.
The original failed run remains failed after later corrections.

This corrective increment only renames candidate() to lookup_fivetools_candidate()
and supplies __name__="python.scrying_glass_monster_selection", __package__="python"
in the existing extracted-function fixture. No production code or assertions are
removed/relaxed; all 24 flow and 30 configuration assertion calls are identical.
Original file blobs were verified; corrected AST parsing and assertion-preservation
checks passed locally. FastAPI is still absent, so no corrected ASGI/full-suite
execution or new CI pass is claimed. Existing CI runs both modules normally.
README, root indexes and workflow remain unchanged; links, task scope and pending
status remain accurate. A.1 acceptance, A.2/A.3, stage B and merge remain pending.
