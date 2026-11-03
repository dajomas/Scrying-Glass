# 150 - Renderer VM window fixture repair

[Back to handover index](../../HANDOVER.md)

Last updated: 2026-11-01. Preparation baseline: `8f07bbf8a936794c9aa46ac234625a760b845231`.

## Diagnosis and scope

Run 41319342579, attempt 1, tested `7b0967c06913272856e83eb0d675850f3c430ae5`. Main unittest discovery passed all 889 tests and the separate pytest step passed 43 cases, but the JavaScript stage failed. The inspected JavaScript log region identified two failing files:

- `tests/test_bughunt_985b4b2.js`: all eight renderer-recovery checks failed before their intended card-DOM assertions.
- `tests/test_lair_presentation.js`: execution stopped during actual viewer-token rendering after nine earlier checks passed.

Both failures reached `renderClientCampaign` in production `static/client.js`, whose optional viewer-selection call uses `window.renderViewerCampaignSelection?.(state)`. The fixtures provide a campaign-heading element but omit `window`. Optional chaining permits a missing hook, not an undeclared base global. This is a Node VM browser-environment mismatch, not evidence that production browser rendering needs a new fallback.

## Repair

Add `sandbox.window=sandbox;` immediately before VM creation in the recovery fixture and the lair test's `viewer()` fixture. Leave its separate picker fixture unchanged. This aliases the VM global as a browser window, while allowing the optional hook to remain absent.

No assertions, cases, fault injection, timer behavior or source extraction boundaries change. Production renderer, runtime requirements and CI workflow are unchanged. No local harness files or source substitutes are committed.

## Local verification

The preceding investigation used Node v20.20.1. Reconstructed originals matched Git blobs `d13d8aad857c3909a887675be8c21d66aa71b64e` and `79d7d57274dc38c09ddfd9aecdfc94399328256b`. Both live files were retrieved again at the same pinned baseline before approval preparation and retained those blobs.

Original runs reproduced `window is not defined`: the recovery file reported eight failures and the lair file aborted. With the one-line changes, `node --test` passed all eight recovery checks and all 14 lair-presentation checks. Original and candidate files also passed `node --check`.

The focused local tree used the copied production renderer prefix through the tests' existing extraction boundary. It did not contain the complete client connection implementation or a full checkout, and no complete client-file hash verification is claimed. The preview script and supporting templates matched their retrieved Git blobs. These were DOM-mock regression runs, not browser, live-server or end-to-end validation.

## Outstanding verification and continuity

Node 22 execution, the entire JavaScript stage and full CI remain unverified for this repair. After approved delivery, inspect the actual push-triggered run; no skip marker or additional workflow dispatch is requested. Do not claim the whole workflow passes while standalone browser/audit checks remain failing. See [open validation](030-validation-and-next-steps.md).

README, the TODO index and relevant handover sections were reviewed at the pinned baseline. No application documentation or unrelated feature-task status changes are needed. The broader source split remains unfinished and the Admin adapter remains inactive.
