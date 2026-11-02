# 080 - Source-size refactors

[Back to TODO index](../../TODO.md)

## SG-TODO-008 - Split oversized code without behavior changes

- Status: in progress; Admin increments 1-3 and newline correction delivered; increment 4 prepared, bound approval/CI pending.
- Requested and five-commit Admin plan approved: 2026-11-02.
- Priority, owner and deadline: not assigned.
- Branch: features/perplexity. Current preparation base: 8cec926408dca2e4cc6f4fa6d58fbb17d5183e1f.

Split code files one at a time into tracked files no larger than 20,000 UTF-8
bytes. Start with static/admin.js; python/scrying_glass_storage.py follows
separately. Do not split package-manifest.json, documentation or CI logs as code.

The approved Admin plan uses four unused source-pair increments, then activation.
Increment 4 stages the last unchanged pair 070/080 and adds complete-reassembly
tests. The original monolith is still the runtime script. The eight parts must
concatenate without separators to exactly 114,205 bytes matching the original.
See [handover](../handover/050-admin-script-split.md) for commit identities and hashes.

### Remaining acceptance

- [ ] Deliver all eight Admin source parts and verify exact committed reassembly.
- [ ] Activate one classic-script response at the existing URL; enforce the size limit.
- [ ] Update all affected source-reading fixtures and deployment guidance.
- [ ] Validate HTTP/static behavior and browser behavior; review full CI evidence.
- [ ] Obtain acceptance before claiming the Admin refactor completed.
- [ ] Prepare and separately validate the SQLite storage split after Admin.

Five test methods passed locally against all eight prepared parts, including
exact whole-source reassembly and assembled Node syntax. Full CI and live
behavior remain pending. Adapt both monolith-comparison test modules in commit 5.
No runtime or source-label functionality changes in increment 4. SG-TODO-006
stage 2 remains paused; SG-TODO-004 remains on hold. Each write needs approval.
The earlier newline correction is additional to the five planned increments.
Next is activation, not task completion; acceptance/validation remain outstanding.
