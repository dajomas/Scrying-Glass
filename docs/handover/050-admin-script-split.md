# 050 - Admin script source split

[Back to handover index](../../HANDOVER.md)

Last updated: 2026-11-02.
Task: [SG-TODO-008](../todo/080-source-size-refactors.md).

## Current status: third fragment pair prepared; runtime unchanged

The user approved the five-commit Admin plan on 2026-11-02.
- Increment 1 (010/020): 4b50a5c5f9bf21b679dd568a85f838827fb9700c.
- Additional newline correction: aeea1aa44586665dd1a9c4860d43ac0680f89766.
- Increment 2 (030/040): db8b567704b3b5d77357200b122f298ad18d2dd7.

The correction removed one accidentally transcribed extra final LF per fragment;
the unchanged tests reproduced the defect and passed with corrected slices.
It did not count as a planned source-pair increment. Post-push sizes and exact
Git blobs were verified for 010/020 and subsequently all four committed parts.
No CI outcome was checked or claimed for those commits.

This increment adds unchanged static/admin/050-source.js (15,145 bytes) and
060-source.js (11,921 bytes). All six fragments remain unused by the application.
The original static/admin.js, HTML includes, mounts, helpers, tests and runtime
behavior are unchanged. Existing preparation tests cover all six parts.

## Remaining approved delivery

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

## Source identity and increment-3 validation

Preparation base: db8b567704b3b5d77357200b122f298ad18d2dd7.
The uploaded original matches Git blob cdec53064a1a9855bf2d140830d33cf0b33e54f2:
114,205 bytes, SHA-256 b97c2a3fda01aa8d3fa4cfa619939909a3c797c678c60a19512aa50c0d05fef5.
Older 112,153-byte preparation evidence does not validate this revision.

Expected new Git blobs:
- 050: f101b67ccb01e9c50a3a379b024ac944d37d05b6.
- 060: 3deb17bd6354937203b383b66f9ca28ebee07e6d.

The unchanged test_admin_source_preparation.py was reconstructed and hash-verified
against live test blob 58d0485a10fa3497c5a44468ab093c35751e702b. All three methods
passed locally with six fragments: UTF-8/size/hash checks, exact 93,635-byte staged
prefix comparison, and Node syntax checks. All eight locally calculated slices
also recombined byte-for-byte to the original. These are source/preparation tests,
not live-provider, authenticated-browser or FastAPI/static-response verification.
Full application tests and CI for this increment remain pending. Verify committed
sizes and blobs after pushing; do not infer them from pre-push checks.

README, HANDOVER.md and TODO.md index links remain unchanged; no deployment or
runtime change occurs yet. The monolith-prefix test must be replaced at activation.
SG-TODO-006 stage 2 remains paused; SG-TODO-004 stays on hold. SQLite splitting
follows separately. Manifest, documentation and CI logs are not code-refactor targets.
