# Bulk selection shortcuts

Documented baseline: `features/development` at `4f401b4adfca92e9c9599aea8924c14efb49aea4`.

Characters and Monsters each have Select all immediately before Bulk. Select all is not a toggle. Unselect all clears the selection; Select dead replaces it with matching IDs from the current list.

- Characters: explicit `life_state=dead` or at least three death-save failures. Down/stable characters are not selected merely because HP is zero.
- Monsters: explicit dead state or `alive=False`, including non-standing monsters.

Selection updates the internal ID set and checkboxes, but makes no API write. Review the selection before Reset/Remove or another bulk mutation. Selection is scoped to the appropriate list and stale IDs are removed by the existing selection helper.

Implementation: `static/bulk-select-all.js`, existing helpers in `static/admin.js`, and the character/monster fragments. Checks:

```bash
node tests/test_bulk_select_all.js
node --test tests/bulk-select-dead.test.cjs
```
