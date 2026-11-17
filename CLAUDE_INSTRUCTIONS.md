# Claude project instructions — Scrying Glass

Standing instructions the user gave Claude for work on this repository. Read
this file together with `PERPLEXITY_INSTRUCTIONS.md` before planning or
preparing changes. Where the two differ, the instructions below take
precedence for Claude's work. New generic instructions from the user are added
here, dated.

## Repository and branch - 2026-11-17

- Repository: `dajomas/Scrying-Glass`.
- Claude's working branch: `features/claude-statblock`, started from
  `features/perplexity-statblock` (commit `1e78d75`).
- Before planning, read `PERPLEXITY_INSTRUCTIONS.md`, `HANDOVER.md`,
  `TODO.md` and the linked `docs/handover/` and `docs/todo/` sections needed to
  decide which TODO items are open and ready.
- Follow `PERPLEXITY_INSTRUCTIONS.md`, except where this file says otherwise.

## Delivery - 2026-11-17

Until the user says otherwise, this replaces delivery by GitHub push:

- Claude does not push to GitHub.
- For every implementation, Claude provides a zip archive with all new and
  changed files at their repository-relative paths.
- Claude writes the Git commit message to a file in the `Patch/`
  subdirectory whose name ends in `COMMIT_MESSAGE.txt`.
- `Patch/` is excluded from Git by `.gitignore`; it is delivery material only.
- The archive contains the new and changed files only, not the complete
  handover and TODO folders that section 6 of `PERPLEXITY_INSTRUCTIONS.md`
  describes.

## SG-TODO-022 staged delivery - 2026-11-17

The user agreed to deliver the rest of SG-TODO-022 in five larger stages,
each a single zip, with CI/e2e results reviewed by the user before the next
stage builds on it:

| Stage | Scope |
|---|---|
| A | All of 022.04: complete 5e.tools adapter, reference collection and normalization |
| B | 022.05-022.07: Open5e, D&D Beyond and `.monster` adapters |
| C | 022.08-022.09: discover/prepare/apply APIs and the protected 3200 listener |
| D | 022.10-022.12: viewer tiles, statblocks, keyboard/accessibility, live sync |
| E | 022.13-022.14: individual and bulk import in the Admin |

022.15 (integrated verification) and 022.16 (user acceptance) follow as the
final correction round.

## Commit messages - 2026-11-17

- Add `[skip ci]` to every commit message for SG-TODO-022 deliveries until the
  very last code delivery. The last code delivery omits it so CI runs.
- Documentation-only commits always carry `[skip ci]`
  (`PERPLEXITY_INSTRUCTIONS.md` section 5).

## Recording instructions - 2026-11-17

Save any and all generic instructions the user gives Claude in this file.

## Stage B decisions - 2026-11-17

- Offer Open5e records from every document, including other game systems such as
  Advanced 5th Edition, labelled with their document and game system.
- The Open5e adapter may make one extra cached request per document for its
  licence and publisher.
- Add user-supplied example files (such as `.monster` files) to `monsters_examples/`.

## Stage D decisions - 2026-11-17

- Automatic original-source statblock loading runs only while a permitted statblock viewer
  is connected, and only for monsters in the battle.
- When the monster species changes and a new statblock is chosen from any valid source,
  the new statblock is shown. When only the species changes and the statblock stays, the
  new species is substituted in the saved statblock (shown through species placeholders).
  A discarded automatic load is retried from the same retained tracker source.
