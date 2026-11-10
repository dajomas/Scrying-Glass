# 050 - Admin script source split

[Back to handover index](../../HANDOVER.md)

Last updated: 2026-11-03. Task: [SG-TODO-008](../todo/080-source-size-refactors.md).

## Activation history and compatibility

Activation: 9f1b14ae99d3b297f4557f05f7f72485ab674d56.
Preparation base: 76f9f7ffa9f28ccfcedb2570c413b76052e1fe11.
Earlier increments: 4b50a5c5f9bf21b679dd568a85f838827fb9700c,
db8b567704b3b5d77357200b122f298ad18d2dd7,
8cec926408dca2e4cc6f4fa6d58fbb17d5183e1f. The increment-1 extra newline was
corrected in aeea1aa44586665dd1a9c4860d43ac0680f89766. Eight slices were verified.

Both /static mounts use AdminScriptStaticFiles; /media retains StaticFiles.
Eight explicit UTF-8 parts assemble without separators at deferred /static/admin.js;
the tracked file remains a failure marker. Reader bounds remain 20,000 bytes per
part. At split activation the response was byte-identical to original blob
cdec53064a1a9855bf2d140830d33cf0b33e54f2: 114,205 bytes, SHA-256
b97c2a3fda01aa8d3fa4cfa619939909a3c797c678c60a19512aa50c0d05fef5.

## Intentional SG-TODO-006 updates and close-out

The notification-label increment c49a890d198098622f40f1d22e5e92db6e8914c4 deliberately
changes 010-source.js only; the other seven parts remain unchanged. The first part
is 18,214 bytes, SHA-256
85e469e2073cd957bddd54b4de5e979b516fe6efc8e4c56a09244e49886b15d2.
At the SG-TODO-006 close-out the assembled size was 114,814 bytes, SHA-256
40fca092f989bcd85eaf7f06dc02b962b662a28827864df68c998919cdf87b46.
Identity tests intentionally update these values, retaining all size, syntax,
UTF-8, ordered assembly and runner-isolation checks. There is no re-split, scope
change, new script include or change to the production adapter/reader/marker.

The separate popup script was updated in f2f63c1fc28238fb2c32b27ce180c54863b30fa5;
it uses the shared label formatter without changing the assembled bundle. Combined
CI run 41622079200 attempt 1, exact head f2f63c1fc28238fb2c32b27ce180c54863b30fa5,
was verified completed/success from ci-results-41622079200-attempt-1/run.json at
21f5de181659458c763672b2b871a21fd2baebb9. Configured test/check steps all report
success. SG-TODO-006 is closed at the user's request on 2026-11-03; no unreported
live-provider/authenticated-browser checks are inferred. See
[label handover](230-fivetools-sources.md) and [task](../todo/060-fivetools-source-configuration.md).
This feature close-out does not itself close the separate Admin-split SG-TODO-008.

## Validation and deployment

Seven source/reader/runner methods and three Node label-fixture subtests passed
locally for stage 2A. Stage 2B had ten local Chromium browser methods pass with
intercepted HTTP. These are not authenticated server or live-provider checks.
Combined CI and label-feature acceptance are recorded above. Historical Admin
activation CI metadata was verified at 430574c584162099c61168cd680b0422479c1541,
run 41584927496 attempt 1, head 9f1b14ae99d3b297f4557f05f7f72485ab674d56:
workflow/tests and configured steps reported success. HTTP/mount fixtures and
deployed service-account/browser acceptance for the source-split task remain
distinct; do not infer a feature's full live validation from a green workflow.

Legacy fixtures use tools/run_split_tests.py to assemble admin.js in a disposable
checkout, never overwriting the real marker. Normal CI wraps Python/pytest/Node
and standalone audit/browser checks. Static adapter tests use fixture FastAPI apps
and inspect server wiring separately. Deploy server, python/ and the complete
static/ tree together, restart and reload browsers. The service account needs a
writable temporary directory; deploying the marker alone or loading individual
fragments is unsupported. No manifest refresh, migration or workflow changes.
This documentation-only close-out requests no CI skip or workflow dispatch.
SG-TODO-005 closure and SG-TODO-004's hold remain separate and unchanged.

## 009.7 fixture and identity reconciliation - 2026-11-10

The [approved CI repair stages](380-feedback-delivery-plan.md#ci-repair-stages---2026-11-10)
cover run 42783429331 attempt 1, tested e777c8e8972c8945aa9576ac3e00dba810760cc1,
evidence commit 6b9e54b66c3ab5169ed194cee91d9d186955c3c5. Its 14 Python assertion
failures are two foundations-message subcases, three shell-setter methods, five
source-identity/isolation outcomes and four preview-alignment subcases. The suite
reported no errors; the preceding roster-rejection repair explicitly passed.

This test-only correction replaces old text-node/automatic-expiry expectations
with explicit error notices, scoped text/dismissal assertions and related-result
resolution. Lookup progress is cleared through its real invalidation API. Shell
fixtures load the real controller/view/bootstrap and first core fragment, then use
the current message entry point; no regex reconstruction of the removed setter.
Existing layout, blank-collapse, scrolling, wrapping, focus, mutation and ARIA
checks remain. Preview alignment accepts flex-start or flow-start only after
requiring flex display, row direction and normal wrap; all existing desktop,
narrow, image, bounds and unrelated-group geometry/style assertions remain.
No production CSS, JavaScript, renderer, permissions, API or workflow changes.

The two changed fragment pins now match the intentional 009.7 contents reported
by covering source logs: 010 SHA-256 174b907526607ab534c4ec34f04624906fe52a771bda4115807f28462458275f;
030 SHA-256 943f2c753cd3104842221ed039141647d3010ba1a03f51755dac8eb912b13a66.
The six other pins remain unchanged. Expected assembled length is 114,400 bytes.
verified_admin_bundle independently enforces all eight ordered pins, UTF-8 and
20,000-byte bounds before returning expected bytes. Both identity modules use
that verified reference. The isolation subprocess receives a fixed length/hash
computed from the verified pinned bytes before it runs; marker before/after,
reader-boundary and syntax checks remain. No current digest is accepted merely
because it was calculated from an unchecked file. A new regression modifies a
copied fragment and requires the pinned guard to reject it. Historical bundle
hashes above remain historical, not current 009.7 identities.

Executed preparation: AST parsing of both revised identity modules and the shell
message helper; four embedded-JavaScript syntax checks; seven synthetic identity
guard checks (valid assembly plus rejection of tampering, oversized/invalid-UTF-8/
missing fragments, reordered inventory and wrong total size); four minimal
Chromium wrapping-flex cases at 1440/375 with empty/labelled preview placeholders.
The local browser computed flex-start; CI's flow-start spelling was observed in
the supplied failure logs, not reproduced locally. The minimal cases retained
same-row top alignment. They are not the full image-preview or Admin fixture.
Actual repository bundle assembly, runner isolation, full browser methods and
combined suites were not executed locally and require covering CI. No passing
corrective CI or commit SHA is invented. Normal CI applies without a skip marker.

This payload targets all 14 reviewed Python assertions; it does not certify that
other JavaScript/standalone failures are resolved or complete 009.7/4A.1. Keep the
existing task statuses open pending combined validation and acceptance. README,
TODO and HANDOVER indexes were reviewed/reused against verified live identities
and need no unrelated edits; the existing source-split handover link is retained.
