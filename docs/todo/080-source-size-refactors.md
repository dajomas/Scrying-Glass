# 080 - Source-size refactors

[Back to TODO index](../../TODO.md)

## SG-TODO-008 - Split oversized code without behavior changes

- Status: in progress; Admin increment 1 and newline correction delivered; increment 2 prepared, bound approval/CI pending.
- Requested and five-commit Admin plan approved: 2026-11-02.
- Priority, owner and deadline: not assigned.
- Branch: features/perplexity. Current preparation base: aeea1aa44586665dd1a9c4860d43ac0680f89766.

Split code files one at a time into tracked files no larger than 20,000 UTF-8
bytes. Start with static/admin.js; python/scrying_glass_storage.py follows
separately. Do not split package-manifest.json, documentation or CI logs as code.

Admin delivery uses four unused source-pair increments, then one activation
increment with tests, caller/fixture adjustments and deployment documentation.
Increment 1 added 010/020 and preparation tests. Increment 2 adds unchanged 030/040;
runtime remains the original monolith. The unchanged preparation suite checks all
four parts. See [handover](../handover/050-admin-script-split.md) for evidence.

### Remaining acceptance

- [ ] Deliver all eight Admin source parts and verify exact reassembly.
- [ ] Activate one classic-script response at the existing URL; enforce the size limit.
- [ ] Update all affected source-reading fixtures and deployment guidance.
- [ ] Validate HTTP/static behavior and browser behavior; review full CI evidence.
- [ ] Obtain acceptance before claiming the Admin refactor completed.
- [ ] Prepare and separately validate the SQLite storage split after Admin.

All three existing preparation test methods passed locally against four staged
parts, including their exact 66,569-byte prefix. Full CI and live behavior remain
pending. No application functionality or source-label behavior changes here.
SG-TODO-006 stage 2 is paused; SG-TODO-004 remains on hold. Each write needs approval.

Increment 1: 4b50a5c5f9bf21b679dd568a85f838827fb9700c. Its two extra trailing LFs
were fixed in aeea1aa44586665dd1a9c4860d43ac0680f89766 and exact blobs verified.
The correction is additional to the five planned increments. Next are 050/060,
070/080, then activation; task completion is not claimed.
