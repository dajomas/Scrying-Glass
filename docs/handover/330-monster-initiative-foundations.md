# 330. Monster initiative and refresh foundations

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-08. [SG-TODO-018](../todo/180-monster-initiative-bonus.md) is completed and closed at the user's explicit request after covering CI, staged acceptance and reconciliation. Branch features/perplexity-018; no merge/write-back included. The previous foundation-only pending descriptions are historical, not missing current implementation.

## History and covering evidence

Foundation 539697fabdde7e564b198104739870760032d638, reset 44e5c7640007601f801858d740dfdf66ab61e541, compatibility 4e7128eb3e5349c186f0a80d34031031762a3d89, fixture repair bb866bd457f42e4a60a14e18c0c90177109e2db0 and state normalization cdd9957642a6754675dc7ace466def69c702b211 established the signed-bonus/raw/legacy semantics. Reset clears raw while retaining bonus/origin and legacy originals; shared raw rolls add individual bonuses once. Characters/lairs remain unchanged.

42304851642 remains failed for its AST import-context errors. Covering 42307450451 attempt 1 succeeded for cdd9957642a6754675dc7ace466def69c702b211. Full original increment hashes, counts, preparation details and evidence paths remain in the [immutable delivery record](https://github.com/dajomas/Scrying-Glass/blob/17932b9b5ac1f02ccdc4cb53e39277fb589e6d96/docs/handover/330-monster-initiative-foundations.md).

## Import stage

4a1685cbe811c478ae44021ceb255fc1f8f964d8 introduced optional .monster initiative_bonus with strict integer/storage validation and import/default provenance. Missing does not imply provider-backed zero; origin cannot be spoofed. Quantity copies preserve scalar bonus without inventing rolls. Earlier unavailable local collection is retained in the immutable record, not described as newly executed or still undelivered.

## Manual creation component

Add Monster accepts a signed optional bonus: blank defaults, explicit zero is manual. Validation precedes HP/image/append side effects. Scope, quantity IDs and image/token/upload handling remain. Creation starts with raw unset and no generated total; reset returns the form field blank. Later Edit, roster raw/bonus UI, active-order and Refresh integration supersede the old foundation-only exclusions.

## Executed checks and limits

Current test families include test_monster_bonus_import, test_manual_monster_bonus_creation/form, test_monster_initiative_bonus_edit, test_monster_bonus_edit_ui/roster, test_monster_raw_roll_rules/handler/composition/ui, test_monster_edit_order and test_monster_roll_order/handlers. The original contract remains authoritative; existence of tests alone is not an execution result.

Final covering Branch tests 42526295799 attempt 1 succeeded for exact f5808a2dfbc9b8d8bd4de9706956dbe8312815a5, publication 790a32b0f86eb60a86319d7c3158f9a7c22f489b. See [overall close-out](340-combined-monster-lookup.md#sg-todo-018-close-out---2026-11-08) for acceptance attribution and fixture limits. No tests are run by this documentation-only reconciliation and no new live-provider, password-login, TCP or OS-process restart result is claimed.
