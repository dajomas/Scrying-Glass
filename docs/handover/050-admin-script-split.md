# 050 - Admin script source split

[Back to handover index](../../HANDOVER.md)

Last updated: 2026-11-02.
Task: [SG-TODO-008](../todo/080-source-size-refactors.md).

## Current status: first fragment pair staged; runtime unchanged

The user approved a five-commit Admin split plan on 2026-11-02. This increment
adds static/admin/010-source.js and 020-source.js (17,605 and 18,043 bytes),
unchanged slices of the existing script, plus preparation regressions. They are
not loaded by the application. static/admin.js, HTML, mounts and provider/UI
behavior remain unchanged. Do not activate assembly until all eight parts,
reader updates and affected fixture changes are delivered together.

## Approved remaining delivery

- Commit 2: stage 030/040; runtime unchanged.
- Commit 3: stage 050/060; runtime unchanged.
- Commit 4: stage 070/080 and verify complete source identity; runtime unchanged.
- Commit 5: activate assembly, enforce 20,000 bytes per source file, replace the
  tracked monolith with a small failure marker, adapt source-reading tests and
  update deployment documentation. Preserve the deferred /static/admin.js URL
  and one classic-script execution scope. Both /media mounts stay ordinary
  StaticFiles; the generated response may exceed the tracked-source size limit.

Each commit requires its own exact-content approval and normal CI. Existing
scrying_glass_admin_source.py and scrying_glass_admin_static.py are inactive
preparatory helpers; their old five-part/25,000-byte setup is not the final plan.
The eight new fragment sizes are 17605, 18043, 19585, 11336, 15145, 11921, 18831,
1739 bytes. No separators or application-logic changes are introduced.

## Evidence and limitations

Preparation base: ffe1fdb94c56537507ca9b556609ea1becc0eb1b.
The upload matches Git blob cdec53064a1a9855bf2d140830d33cf0b33e54f2.
The original is 114,205 bytes, SHA-256
b97c2a3fda01aa8d3fa4cfa619939909a3c797c678c60a19512aa50c0d05fef5.
This replaces the older 112,153-byte preparation described here previously;
those historical checks do not validate this new source revision.

Three preparation tests passed locally: UTF-8/size/hash checks, exact staged-prefix
comparison against the original runtime source, and Node syntax parsing of both
new fragments (Node v20.20.1). Recombining all eight locally calculated slices
also matched the original bytes. These are source/preparation checks, not
FastAPI/static-response, live-provider or authenticated browser verification.
Full application tests and CI have not been run or reviewed for this increment.
The normal workflow discovers the new test_admin_source_preparation.py module.
Its monolith-prefix test must be replaced with assembled-source checks at activation.

README and HANDOVER.md were reviewed and remain unchanged: runtime/deployment and
index links are unaffected by this preparatory increment. SG-TODO-006 stage 2 is
paused, not implemented or completed. SQLite splitting follows Admin separately;
manifest, documentation and CI-log files are not code-refactor targets.
