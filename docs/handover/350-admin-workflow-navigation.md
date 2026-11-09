# 350 - Admin workflow navigation

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-09. Task: [SG-TODO-009.5](../todo/095-admin-workflow-navigation.md).
Status: navigation and its test corrections have successful covering CI at 7df8cbe67b62b4df772dd192f2ac38d19c4cfad8. User visual/workflow acceptance remains outstanding. The subsequently requested Add Monsters form refinement is prepared, not pushed or validated; the earlier green run does not cover it. No closure is claimed.

## Workflow and compatibility

- Campaign: campaign selection/access/backups, Add character and Characters.
- Battle preparation: setups/background/imports, Add monsters, both rosters for participation/initiative and independently gated lair configuration.
- Live encounter: existing rosters, encounter tools, gated lair controls and activity log. No filtered rosters or 009.6 focused workspace is implemented.
- Shared: Battle/order/Danger zone and fixed header context, Start/Next/End, More/logout/viewer controls and global feedback. Current-view pane controls retain parent/child and lair gating.

Campaign is the per-page initial view; refresh and battle transitions do not steal the chosen tab. The view layer writes data-workflow-excluded rather than native hidden/aria-expanded, retaining DOM/listeners, drafts, files and selection. Existing initial and automatic battle collapse/restoration and encounter-tools preferences remain authoritative. Tabs use roving tabindex, aria-selected, Left/Right/Home/End and the labelled shared tabpanel, with local narrow-screen scrolling and per-view scroll retention. Missing prerequisites preserve the legacy interface; installation is idempotent. Core assembly/failure marker, API, security, persistence and combat rules are unchanged.

Deploy matching templates and static assets, restart the correct process for import-assembled HTML and reload Admin. No migration or configuration change is introduced.

## First covering CI and approved correction split - 2026-11-09

Implementation: 1beff730580b17551ae5c95115ad31badf39b3f1. First run 42586178034 attempt 1 failed with 31 failures/31 errors in both 1,416-test suite executions; audit reported 762/0 connections. Publication c01beaf5dcfdb931ab1c2a271e717f02cc7d4b6b. Missing workflow-selection preconditions and an incorrectly sampled battle-forced tools preference required fixture corrections; failed history remains failed.

User-approved stage 1 c490943d5921b8abbec65fbeba0c012df39d2619 corrected shared roster/header/navigation entry and both saved tools-preference scenarios. Stage 2 ef07efbc9373fb62fecaeab727e4996acdd58660 corrected cross-view foundation/forms and secured Refresh fixtures without removing behavioral assertions.

## Covering stage-2 CI and standalone smoke follow-up - 2026-11-09

Run 42590952958 attempt 1 covered ef07efbc and remained failed on the independent smoke's excluded monster-toggle click. Main and repeated audit: 1,416 tests OK, audit 764 connections/zero without explicit close. Other configured test steps succeeded. Publication 86a515cd5bb2d94abce7aa7c2715cdc2018a7279. Smoke follow-up 7df8cbe67b62b4df772dd192f2ac38d19c4cfad8 added readiness/view selection and visibility assertions, retaining the original 12 assertions and byte-identical users/client suffix. Its static AST/compile and assertion/blob checks passed during preparation.

Full prior diagnosis, exact evidence paths, stage preparation checks and limitations remain in the [immutable smoke-delivery handover](https://github.com/dajomas/Scrying-Glass/blob/7df8cbe67b62b4df772dd192f2ac38d19c4cfad8/docs/handover/350-admin-workflow-navigation.md). This consolidation supersedes obsolete pending-run wording, not historical failures.

## Successful covering CI - 2026-11-09

Run 42594146455 attempt 1 completed/success on exact 7df8cbe67b62b4df772dd192f2ac38d19c4cfad8, features/perplexity. Publication 07b12ed92b2d1c292381685611a41a7e9c1ded90, ci-results-42594146455-attempt-1. run/jobs metadata and reviewed workflow reader file-000032 parts 23, 113, 115, 155/156 establish configured-step success, 1,416 main tests OK, repeated 1,416 tests OK, 764/0 audited connections and 43 pytest passes. Navigation methods and the full Admin/users/client smoke pass with no page errors; mocked HTTP/WS transport remains distinct from a live server. Twenty-four fixture images include six navigation views; collection is not visual acceptance. Historical successful 018 run 42526295799 covers f5808a2 on features/perplexity-018 only.

## Add Monsters form refinement - prepared 2026-11-09

The user requested removing the initiative-bonus description entirely, positioning its editor between HP Range end and Quantity, and copying nonempty species into an empty name on leaving the species field. Template markup removes the help paragraph and its aria-describedby reference, moves the original optional signed field into the requested order, and preserves the import form. Panel assembly includes that original field in Combat statistics so the rendered layout cannot move it back outside the group. IDs, name, blank/default-zero, signed validation and source-offer semantics remain unchanged. The candidate extension already guards its optional help-node lookup, so it does not recreate the removed paragraph.

The existing guarded panel installer adds a blur listener to Monster species. It checks current values on blur, treats whitespace-only names/species as empty, and copies trimmed species only when the name is blank. Existing/custom/generated names are never overwritten. Typing alone does not copy; the name remains editable. No synthetic input/change events, API requests or form submission are introduced by the copy. Source lookup timing, candidate selection and edit guards are not changed.

Updated manual-bonus tests retain optional signed field, backend parameter, import-form checksum, FormData/reset and scope assertions, replacing only the now-obsolete help-reference contract with absence/raw-order assertions. Added assembled-page tests at 1440/375 check rendered Combat statistics order, absent help/reference, idempotence/value retention and actual Tab-induced blur for empty/custom/already-populated/whitespace cases, with no mutations/page errors. Existing CI unittest discovery covers the module; no workflow changes or skip marker.

Executed preparation: Node syntax check of the changed grouping/blur block and Python AST parsing of the changed test snippets passed. Complete module/application/browser execution and covering CI for this new refinement remain pending; prior green navigation CI is not coverage of these application edits. Review screenshots/keyboard order and source/manual creation before acceptance. README, User Guide, indexes and relevant existing docs were reviewed/reused; deployed bonus/lookup mechanics remain unchanged and this section documents the new UI default.

No password-login, live TCP/provider, process-restart or exhaustive accessibility audit is claimed. Remaining acceptance includes desktop/narrow workflow presentation, drafts/files, initial/delayed context, parent/child/lair gating, battle transitions and modal/initiative continuation. Overall 009 and 009.5 are not closed by this proposal.
