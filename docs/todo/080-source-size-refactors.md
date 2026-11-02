# 080 - Source-size refactors

[Back to TODO index](../../TODO.md)

## SG-TODO-008 - Split oversized code without behavior changes

- Status: in progress; Admin increment 1 delivered; newline correction prepared, bound approval/CI pending.
- Requested and five-commit Admin plan approved: 2026-11-02.
- Priority, owner and deadline: not assigned.
- Branch: features/perplexity. Preparation base: ffe1fdb94c56537507ca9b556609ea1becc0eb1b.

Split code files one at a time into tracked files no larger than 20,000 UTF-8
bytes. Start with static/admin.js; python/scrying_glass_storage.py follows
separately. Do not split package-manifest.json, documentation or CI logs as code.

Admin delivery uses four unused source-pair increments, then one activation
increment with tests, caller/fixture adjustments and deployment documentation.
Increment 1 adds 010/020 and preparation tests; it does not change runtime.
See [handover](../handover/050-admin-script-split.md) for sizes and evidence.

### Remaining acceptance

- [ ] Deliver all eight Admin source parts and verify exact reassembly.
- [ ] Activate one classic-script response at the existing URL; enforce the size limit.
- [ ] Update all affected source-reading fixtures and deployment guidance.
- [ ] Validate HTTP/static behavior and browser behavior; review full CI evidence.
- [ ] Obtain acceptance before claiming the Admin refactor completed.
- [ ] Prepare and separately validate the SQLite storage split after Admin.

Three local preparation tests passed; full CI and live behavior remain pending.
SG-TODO-006 stage 2 is paused during this work; no source-label functionality is
added here. SG-TODO-004 remains on hold. Each external write requires bound approval.

Increment 1: 4b50a5c5f9bf21b679dd568a85f838827fb9700c. Correct its two extra trailing
LF bytes before proceeding to increment 2. The unchanged tests reproduced the
fault locally and passed with the exact corrected slices. The corrective write
is additional to the five planned increments; task completion is not claimed.
