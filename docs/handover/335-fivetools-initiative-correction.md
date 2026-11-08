# 335 - 5e.tools initiative extraction correction

[Back to handover index](../../HANDOVER.md)

2026-11-08. [SG-TODO-018 A.1](../todo/185-monster-correction-plan.md).
Branch features/perplexity-018; baseline 3486eaee2303d1caa3f031bf0867e4fb3710b3b3.
Implementation included; CI/acceptance pending. No close-out or merge/write-back.

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

## Validation

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
