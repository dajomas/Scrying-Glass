# 050 - Admin script source split

[Back to handover index](../../HANDOVER.md)

Last updated: 2026-11-01.

## Status: helpers staged; runtime unchanged

This preparatory commit adds `python/scrying_glass_admin_source.py` and `python/scrying_glass_admin_static.py`. The server does not import or activate these helpers yet. The original `static/admin.js`, HTML includes and static/media mounts remain unchanged. The source fragments named by the reader are not delivered in this preparatory commit; do not instantiate the new static adapter until all five fragments are present.

The implementation is being delivered through separately approved staged commits. Approval of this commit does not authorize subsequent source or activation writes.

## Intended browser-delivery design

Store the Admin JavaScript as five ordered files under `static/admin/`, each at most 25,000 UTF-8 bytes. The reader concatenates their bytes without separators. `AdminScriptStaticFiles` substitutes a generated temporary file only for the `admin.js` lookup, leaving other static lookups to the existing base class.

The final activation must preserve the existing deferred `/static/admin.js` include and change both `/static` mounts to the adapter. Both `/media` mounts must retain ordinary `StaticFiles`. The tracked `static/admin.js` will then become an explanatory failure marker rather than the browser bundle.

The assembled runtime bundle remains 112,153 bytes and is generated outside the checkout. The 25,000-byte limit applies to repository source files, not the HTTP response or disposable runtime bundle. Source edits refresh the generated file on the next lookup.

## Source identity and local checks

Preparation used base commit `a89b798089205bddfc9ed76dc0c7b906fee8525a`. The supplied Admin source matched Git blob `48804b5dc92c3173fb107a031cb9ce4eedc8e3dd`. Concatenated candidate fragments matched the original byte-for-byte, with SHA-256 `99dc60c74e5d007aa2fb4cdea1ce1b2603c1bf245b7382e399aac821a6927cec`.

Candidate fragment sizes in order: 22,285; 23,607; 23,281; 23,940; 19,040 bytes. Each passed `node --check`. The helper modules compiled. Local reader checks covered missing, oversized and invalid-UTF-8 fragments. Adapter logic checks used a base-class substitute, including delegation, temporary-file creation, unchanged-content mtime and source refresh.

A Chromium 134.0.6998.35 fixture verified equivalent hoisting, lexical-state sharing, microtask ordering, subsequent deferred-script execution and DOMContentLoaded ordering for original and assembled fixture scripts. The complete production candidate was fetched, hash-checked and parsed. This used a local Python HTTP fixture and the candidate reader, not the real FastAPI/Starlette application or encounter UI.

## CI and remaining work

The user explicitly requested normal CI for these pushes; do not add `[skip ci]` or dispatch an extra workflow. No CI result is claimed by this document. Actual FastAPI/Starlette checks, including GET/HEAD, conditional requests and range behavior, are deferred to CI.

Remaining work requires separate approval: deliver all five source fragments; activate the static adapter and marker with relevant README updates; adapt existing fixtures that read `static/admin.js` directly; inspect CI results. Source-reading fixtures are expected to fail after activation until adapted. Do not describe this preparatory commit as completion of the browser integration.

The SQLite storage and package-manifest refactors are outside this commit. TODO tracking has not been created by this change.
