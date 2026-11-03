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

## Intentional SG-TODO-006 stage 2A update

The notification-label increment deliberately changes 010-source.js only; the other
seven parts remain unchanged. The first part is 18,214 bytes, SHA-256
85e469e2073cd957bddd54b4de5e979b516fe6efc8e4c56a09244e49886b15d2.
Current assembled size is 114,814 bytes, SHA-256
40fca092f989bcd85eaf7f06dc02b962b662a28827864df68c998919cdf87b46.
Identity tests intentionally update these values, retaining all size, syntax,
UTF-8, ordered assembly and runner-isolation checks. There is no re-split, scope
change, new script include or change to the production adapter/reader/marker.
Popup rendering is unchanged until the second approved label commit. See
[label handover](230-fivetools-sources.md) and [task](../todo/060-fivetools-source-configuration.md).

## Validation and deployment

Seven source/reader/runner methods passed locally for stage 2A. Node label fixtures
also passed; these are not authenticated browser or live-provider checks. Stage 2A
CI and manual acceptance remain pending. Historical Admin activation CI metadata
was verified at 430574c584162099c61168cd680b0422479c1541, run 41584927496 attempt 1,
head 9f1b14ae99d3b297f4557f05f7f72485ab674d56: workflow/tests and configured steps
reported success. HTTP/mount fixture and deployed service-account/browser acceptance
remain distinct. Do not infer a new feature's validation from an earlier green run.

Legacy fixtures use tools/run_split_tests.py to assemble admin.js in a disposable
checkout, never overwriting the real marker. Normal CI wraps Python/pytest/Node
and standalone audit/browser checks. Static adapter tests use fixture FastAPI apps
and inspect server wiring separately. Deploy server, python/ and the complete
static/ tree together, restart and reload browsers. The service account needs a
writable temporary directory; deploying the marker alone or loading individual
fragments is unsupported. No manifest refresh, migration, workflow dispatch or CI skip.
SG-TODO-005 dependent-button work and SG-TODO-004's hold remain separate.
