# 050 - Admin script source split

[Back to handover index](../../HANDOVER.md)

Last updated: 2026-11-02.
Task: [SG-TODO-008](../todo/080-source-size-refactors.md).

## Current status: final source pair prepared; runtime unchanged

The user approved the five-commit Admin plan on 2026-11-02.
- Increment 1 (010/020): 4b50a5c5f9bf21b679dd568a85f838827fb9700c.
- Additional newline correction: aeea1aa44586665dd1a9c4860d43ac0680f89766.
- Increment 2 (030/040): db8b567704b3b5d77357200b122f298ad18d2dd7.
- Increment 3 (050/060): 8cec926408dca2e4cc6f4fa6d58fbb17d5183e1f.

The correction removed one accidentally transcribed extra final LF per fragment;
the unchanged tests reproduced the defect and passed with corrected slices.
It did not count as a planned increment. Post-push sizes and exact Git blobs
were verified for all six currently committed fragments. No CI outcome was
checked or claimed for those commits.

Increment 4 adds unchanged static/admin/070-source.js (18,831 bytes) and
080-source.js (1,739 bytes), plus complete-reassembly regressions. All eight
fragments remain unused by the application. The original static/admin.js, HTML
includes, mounts, helpers and runtime behavior are unchanged.

## Remaining activation (commit 5)

Activate assembly, enforce 20,000 bytes per source file, replace the tracked
monolith with a small failure marker, adapt all affected source-reading tests
and update deployment documentation. Preserve the deferred /static/admin.js URL
and a single classic-script execution scope. Both /media mounts stay ordinary
StaticFiles; the generated response may exceed the tracked-source size limit.

Each write requires exact-content approval and normal CI. Do not activate the
inactive scrying_glass_admin_source.py / scrying_glass_admin_static.py helpers
until their old five-part/25,000-byte setup and all fixture readers are updated.
Sizes in order: 17605, 18043, 19585, 11336, 15145, 11921, 18831, 1739 bytes.
Assembly inserts no separators. The complete sources being staged are not yet
a working split-runtime deployment; the monolith remains authoritative until activation.

## Source identity and increment-4 validation

Preparation base: 8cec926408dca2e4cc6f4fa6d58fbb17d5183e1f.
Original Git blob: cdec53064a1a9855bf2d140830d33cf0b33e54f2.
All eight calculated slices reassemble exactly to the uploaded 114,205-byte source,
SHA-256 b97c2a3fda01aa8d3fa4cfa619939909a3c797c678c60a19512aa50c0d05fef5.
Older 112,153-byte preparation evidence does not validate this revision.
Expected new Git blobs: 070 = 627e6e2e3586126e1f8ae6d9c81a8e60c69bac3a;
080 = 8a6faa11845b8263686e12104342bd47b93f4b36.

Five local test methods passed against all eight parts: the unchanged three
preparation methods (test blob 58d0485a10fa3497c5a44468ab093c35751e702b), plus
new complete-file-set/reassembly identity and assembled Node parsing tests in
test_admin_source_complete.py. The existing CI discovery includes the new module.
These verify source bytes, UTF-8, limits and syntax, not FastAPI/static HTTP,
authenticated browser behavior, or live providers. Full application tests and CI
remain pending. Check committed sizes and blobs after pushing.
Both test modules' monolith comparisons must be adapted at activation.

README and root index links remain unchanged; no deployment change occurs yet.
SG-TODO-006 stage 2 remains paused; SG-TODO-004 stays on hold. SQLite splitting
follows separately. Manifest, documentation and CI logs are not code-refactor targets.
