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


## 2026-11-02 - CI connection-lifetime correction

Analyzed supplied run 41452426944, attempt 1, branch features/perplexity, tested
commit 14404e34828ed5e4fed6828245250aaa348b4396. Syntax/server import, 911 unittest
cases, 43 pytest checks and 36 JavaScript scripts passed. The restore-layout
Chromium fixture passed too. The standalone connection-lifetime audit reran the
suite successfully but found 1 connection without explicit close out of 637;
its nonzero status failed the job. These are results of the original failing run,
not a passing post-fix run. Artifact download was unavailable but logs were present.

The defect is in AttackStatisticsTests.test_v7_backup: a plain SQLite connection
context manages transactions but does not close the backup reader. The corrective
archive adds contextlib.closing and wraps that reader; assertions and the audit
remain unchanged. No production, migration, UI, dependency or workflow code is
changed. Original source was read at the tested SHA and its Git blob verified as
9d57777238b22655ca863409452c70345b9285cc before the narrow edit.

A new test module AST-extracts the actual backup-test method and exercises it with
real temporary SQLite connections, explicit-close tracking and a minimal storage
fixture. Both success and injected backup-assertion-failure cases pass after the
fix and both detect the old defect when run against the unmodified source. This
is isolated resource-lifetime coverage, not the actual full application migration
fixture or complete connection audit. Syntax and documentation checks also ran.
The full attack module, full suite/audit and CI have not been rerun after this fix.

After overlay, run the real migration test and tests/audit_connection_lifetime.py
in the complete checkout; the required result is zero connections without explicit
close. Then rerun CI with its configured dependencies. The wider task stays open;
SG-TODO-003 remains proposed and is not implemented by this correction.

Current README was reviewed and left unchanged because runtime behavior is
unchanged. Existing handover/TODO indexes are included unchanged; their sections
180 and 020 receive these notes in place. The archive includes complete verified
indexed context, supporting Patch/ instructions/logs/manifest and a proposed
commit message without a skip token so normal CI can verify the correction.
No GitHub write or new workflow outcome is claimed for archive generation.
