# 050 - Admin script source split

[Back to handover index](../../HANDOVER.md)

Last updated: 2026-11-02.
Task: [SG-TODO-008](../todo/080-source-size-refactors.md).

## Current status: second fragment pair prepared; runtime unchanged

The user approved the five-commit Admin plan on 2026-11-02. Increment 1 added
010/020 in 4b50a5c5f9bf21b679dd568a85f838827fb9700c. The additional corrective
commit aeea1aa44586665dd1a9c4860d43ac0680f89766 removed an accidentally transcribed
extra final LF from each fragment. Post-push blob and size verification confirmed
010 is 17,605 bytes / 8bd98db00cbcdd87a3e7910ccc860820262c5fc4 and
020 is 18,043 bytes / 350f9b2b998a035ec17a5ab2f7840ae622430bba.
The unchanged local tests reproduced the newline defect and passed after correction;
no CI outcome was checked or claimed. The correction did not count as increment 2.

This increment stages unchanged static/admin/030-source.js (19,585 bytes) and
040-source.js (11,336 bytes). All four fragments remain unused by the application.
The original static/admin.js, HTML includes, mounts, helpers and runtime behavior
are unchanged. Existing preparation tests cover the new files without modification.

## Remaining approved delivery

- Commit 3: stage 050/060; runtime unchanged.
- Commit 4: stage 070/080 and verify complete source identity; runtime unchanged.
- Commit 5: activate assembly, enforce 20,000 bytes per source file, replace the
  tracked monolith with a small failure marker, adapt source-reading tests and
  update deployment documentation. Preserve the deferred /static/admin.js URL
  and a single classic-script execution scope. Both /media mounts stay ordinary
  StaticFiles; the generated response may exceed the tracked-source size limit.

Each write requires exact-content approval and normal CI. Do not activate the
inactive scrying_glass_admin_source.py / scrying_glass_admin_static.py helpers
until all eight parts and fixture updates are ready. Their old five-part/25,000-byte
configuration is not the final design. New sizes in order: 17605, 18043, 19585,
11336, 15145, 11921, 18831, 1739 bytes. Assembly inserts no separators.

## Source identity and increment-2 validation

Preparation base: aeea1aa44586665dd1a9c4860d43ac0680f89766.
The uploaded original matches live Git blob cdec53064a1a9855bf2d140830d33cf0b33e54f2:
114,205 bytes, SHA-256 b97c2a3fda01aa8d3fa4cfa619939909a3c797c678c60a19512aa50c0d05fef5.
Older 112,153-byte preparation evidence does not validate this revision.

Expected new Git blobs:
- 030: e11e33373abc43b9570a03a92c59efdb7da09507.
- 040: 81ae5d291e6453ec024372de80d10a6b3b752bde.

The unchanged test_admin_source_preparation.py was reconstructed and hash-verified
against live test blob 58d0485a10fa3497c5a44468ab093c35751e702b. All three methods
passed locally with four fragments: UTF-8/size/hash checks, exact 66,569-byte staged
prefix comparison, and Node syntax checks. All eight locally calculated slices
also recombined byte-for-byte to the original. These are source/preparation tests,
not live-provider, authenticated-browser or FastAPI/static-response verification.
Full application tests and CI for this increment remain pending. Verify committed
sizes and blobs after pushing; do not infer them from pre-push checks.

README, HANDOVER.md and TODO.md index links remain unchanged; no deployment or
runtime change occurs yet. The monolith-prefix test must be replaced at activation.
SG-TODO-006 stage 2 remains paused; SG-TODO-004 stays on hold. SQLite splitting
follows separately. Manifest, documentation and CI logs are not code-refactor targets.
