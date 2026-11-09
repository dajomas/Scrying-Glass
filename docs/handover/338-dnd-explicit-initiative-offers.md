# 338. Explicit D&D Beyond initiative candidate offers

[Selected-source identity](337-selected-monster-source-identity.md) |
[Task SG-TODO-018](../todo/180-monster-initiative-bonus.md)

Prepared 2026-11-07 for features/perplexity-018. Task remains incomplete.
No merge or write-back authorized.

## Covering baseline and format evidence

Run 42394776811 attempt 1 reports success for exact tested commit
cac768eb0db1ca6b4dcc6e22a0806c4df2e2a4ee. Its run.json was reviewed at
publication 2431ed2e96c588a66608a13915849fd514a1ad2c under
ci-results-42394776811-attempt-1. This is run-level verification, not an
individual log/count audit. Earlier failures retain their status.

Public source text shows signed header modifiers, including Goblin Warrior
https://www.dndbeyond.com/monsters/5195050-goblin-warrior with Initiative +2 (12),
and Ochre Jelly https://www.dndbeyond.com/monsters/5195148-ochre-jelly with
Initiative minus 2 (8). These support the text grammar, not a claim that all live
HTML templates or container classes were verified. Markup fixtures are synthetic.

## Offer-only scope

A bounded HTML text reader recognizes a mon-stat-block container, excludes
scripts/navigation and explicitly hidden or inline-style-hidden content, and
examines only the header before HP/speed/ability/action boundaries. It accepts
an explicit AC / Initiative signed-modifier (score) / HP header. ASCII minus and
Unicode minus normalize to the same signed integer. The parenthesized score is
not used to derive a modifier. Existing strict integer/storage validation is
reused; Dexterity and lair-action prose are never used as substitutes.

A recognized modifier yields initiative_bonus, available status and at most
512 characters of header evidence. Missing, invalid and ambiguous cases yield
None plus status/reason, never a fabricated zero. Explicit +0 remains available.
Multiple recognized blocks or duplicate header labels require review. Unfamiliar
templates stay unavailable; stylesheet-computed visibility is not evaluated.

The D&D Beyond candidate adapter adds these offer fields from the already fetched
HTML only after the existing usable AC/HP filter. Candidate identity, images,
lookup order, provider-error behavior and fallback rules remain unchanged.
Missing bonus alone does not trigger fallback. Existing AC/HP parsing is not
expanded here, so a new template rejected by that filter still produces no
candidate. No claim of complete current-template coverage is made.

Creation and signed snapshot logic remain unchanged. The offer is not promoted
to source provenance, auto-assigned, or applied to existing monsters; retaining
an authenticated candidate identity does not authenticate an arbitrary browser
bonus. The Admin candidate UI does not yet render or apply this offer. No
5e.tools initiative extraction, refresh endpoint/UI, schema or workflow change
is included. Normal CI applies without skip marker or separate dispatch.

## Executed checks and limits

All 16 pure parser methods passed locally, covering signed/zero values, nested
markup/entities, hidden content, duplicate blocks/labels, scope isolation,
Dexterity/lair exclusions, malformed input and bounds. The existing strict input
helper copy was verified against its retrieved blob before executing the tests.
Four candidate/creation integration methods are prepared and syntax-parsed, but
have not run locally because FastAPI is unavailable. They check offer plumbing,
missing/invalid behavior, unchanged AC/HP filtering and no automatic assignment.

No live provider HTML, authenticated HTTP, browser, persistence/restart or new
full-suite/CI pass is claimed. Review covering CI, verify additional provider
formats, then connect signed/reviewed offer selection and source refresh with
scope/lifetime/replay protection. Retained identity storage/import provenance and
all remaining agreed SG-TODO-018 acceptance still require integration validation.
