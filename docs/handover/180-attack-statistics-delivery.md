# 180 - Attack statistics archive implementation

[Back to handover index](../../HANDOVER.md)

Recorded: 2026-11-02. Task: [SG-TODO-002](../todo/020-monster-damage-effects.md).

The previous Attack-Statistics archive implemented attack-window rows for Max HP
and all six ability scores, ordered atomic application with damage/healing, manual
restoration beside character/monster Reset, explicit original/base editing, private
mechanics, schema-8 persistence, audit/undo/checkpoints and bundle compatibility.
It was built from the original e0c321a attachment, not the earlier Encounter tools
patch. No repository commit or workflow result was claimed.

The prior delivery reported 910 unittest cases (2 skipped), 43 configured pytest
checks, 21 focused tests (included in discovery), 36 JavaScript scripts and
compilation passing. These are historical attack-implementation results, not
newly executed evidence for the layout correction. Full startup/authenticated
HTTP/browser integration and production migration validation remain outstanding.

The screenshot then showed unformatted inline original-score fields in Restore
statistics. The [190 correction](190-statistics-restoration-layout.md) replaces
that presentation with a filtered table and a separate original-score editor.
Refer to [User Guide](../User-Guide.md#attack-statistics-reductions) and the installed
attack increment's technical documentation for behavior and APIs. Base statistics,
manual recovery, HP clamping without second damage, no healing/resurrection from
restoration, and the distinction from ordinary Reset remain unchanged.

Do not apply the layout correction directly to the original baseline: it requires
the Attack-Statistics backend, admin buttons, token and assets already installed.
Do not treat it as a migration from the older Encounter tools patch. No broad
SG-TODO-002 completion or new CI outcome is implied.
