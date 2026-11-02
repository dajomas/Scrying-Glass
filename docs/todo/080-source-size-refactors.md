# 080 - Source-size refactors

[Back to TODO index](../../TODO.md)

## SG-TODO-008 - Split oversized code without behavior changes

- Status: in progress; Admin increments 1/2 and newline correction delivered; increment 3 prepared, bound approval/CI pending.
- Requested and five-commit Admin plan approved: 2026-11-02.
- Priority, owner and deadline: not assigned.
- Branch: features/perplexity. Current preparation base: db8b567704b3b5d77357200b122f298ad18d2dd7.

Split code files one at a time into tracked files no larger than 20,000 UTF-8
bytes. Start with static/admin.js; python/scrying_glass_storage.py follows
separately. Do not split package-manifest.json, documentation or CI logs as code.

Admin delivery uses four unused source-pair increments, then one activation
increment with tests, caller/fixture adjustments and deployment documentation.
Increment 1 added 010/020 and preparation tests; increment 2 added 030/040.
Increment 3 adds unchanged 050/060. Runtime remains the original monolith and
the unchanged preparation suite checks all six staged parts.
See [handover](../handover/050-admin-script-split.md) for evidence.

### Remaining acceptance

- [ ] Deliver all eight Admin source parts and verify exact reassembly.
- [ ] Activate one classic-script response at the existing URL; enforce the size limit.
- [ ] Update all affected source-reading fixtures and deployment guidance.
- [ ] Validate HTTP/static behavior and browser behavior; review full CI evidence.
- [ ] Obtain acceptance before claiming the Admin refactor completed.
- [ ] Prepare and separately validate the SQLite storage split after Admin.

All three existing preparation test methods passed locally against six staged
parts, including their exact 93,635-byte prefix. Full CI and live behavior remain
pending. No application functionality or source-label behavior changes here.
SG-TODO-006 stage 2 is paused; SG-TODO-004 remains on hold. Each write needs approval.

Increment 1: 4b50a5c5f9bf21b679dd568a85f838827fb9700c. Its two extra trailing LFs
were fixed in aeea1aa44586665dd1a9c4860d43ac0680f89766 and exact blobs verified.
Increment 2: db8b567704b3b5d77357200b122f298ad18d2dd7, exact sizes/blobs verified.
The correction is additional to the five planned increments. Next are 070/080,
then activation; task completion is not claimed.
