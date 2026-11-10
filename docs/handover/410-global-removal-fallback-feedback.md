# 410 - Global removal fallback feedback

[Back to handover index](../../HANDOVER.md)

## 4A.8 preparation and delivery - 2026-11-10

Prepared at the user's finish/push request on features/perplexity-009.7, baseline
b36ed511e33980448ed0162802d1baee48371007. [4A.8](../todo/097-feedback-delivery-plan.md#4a8-global-removal-fallback-feedback---2026-11-10)
remains open pending covering CI/full-Admin validation and bounded acceptance.
No implementation SHA or covering success is invented before delivery/evidence.

Only the legacy data-remove branch changes. Modern data-remove-kind/data-remove-id
routing keeps priority and pane-based removeCombatant stays unchanged. Current
monster/character row renderers use that modern route; this unit does not migrate
pane roster removal. Preserve named confirmation and encoded bodyless DELETE.
After confirmation, capture encounter-scoped combatant.remove.fallback targeting
the endpoint ID; kind/name are display metadata. Cancel leaves feedback/control
state intact. Current request errors persist and reenable the original button.
Stale/superseded failures cannot publish or reenable a newer pending attempt.
Matching success replaces only its error with explicit success before load(),
using server name or confirmed name when JSON is absent, and existing five-second
global expiry. Refresh failure stays load-owned; confirmed deletion must not be
relabeled failed or reenabled for replay. Scope guards do not revoke sent mutations.
No automatic retry, new concurrency policy, pane/bulk-removal or server changes.

Historical preparation: slice and regression syntax passed; 20 Node regressions
passed with zero failures/skips; five negative controls were detected (error
severity, collapsed targets, missing stale guards, success after refresh, missing
failure-button restoration); restored draft passed all 20. Real controller and
complete bootstrap execute with production-derived delegated prefix, mocked DOM/
network and actual loadState handling of a rejected mock fetch. Not full Admin/
rendering/browser, authenticated live-server or manual evidence. Behavioral tests
were not rerun during final integration.

Final integration reconstructed complete original 070 against Git blob
1b8a2c9e53e6a9ae6f1faeb963b6c2dd411337f6. Complete modified fragment passed
node --check and reverse comparison verified all surrounding source, including
4A.7, unchanged. Size 19,912 UTF-8 bytes leaves 88 below the 20,000 limit. SHA-256:
d426d21ad53c79eed2c6944697b835337c9073c0862dd3a5085e63c6173750d1.
Calculated assembled size 115,481 bytes is 475 above the prior baseline; only 070's
digest/total-size expectations change. Updated pin file passed AST parsing/digest
agreement; size/order/tamper guards remain intact. Full assembled-bundle/reader/
isolation tests, browser/combined suites and covering CI remain pending. Other
fragments/pins, eight-part order and tracked admin.js failure marker are unchanged.

Live instructions/read/write schemas and branch head were checked. Complete prior
docs/source/config reads reused against the unchanged baseline. README and TODO
index retain accurate open-phase scope/links without edits. Task plan summarizes
closed 4A.7 with retained anchor/evidence; no open work/history is deleted. This
new section is linked from the existing handover index. Existing CI discovers the
new .cjs and source contracts; no workflow changes/dispatch. Mixed commit uses
normal CI without a skip marker. 4A.1-4A.7 stay closed; 4A.9 onward stays proposed.
Deliverable 1, Deliverable 2, SG-TODO-009.7 stay open. SG-TODO-019 and agreed order
are unchanged. No acceptance, merge or deployment is implied.
