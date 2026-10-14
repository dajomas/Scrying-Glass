# Initiative required before joining battle

Characters and monsters need a whole-number initiative before joining battle.
Zero and negative initiatives are valid; empty/unset initiative is not.

## Rejection feedback

Clicking an individual Join Battle button without initiative does not submit the
join. It shows `Enter initiative before joining battle: <name>` in the fixed
`#message` area. Buttons remain clickable for feedback and use `aria-disabled`
and a tooltip to indicate the blocked state. The normal join handler is stopped
by a capture-phase listener. After saved-state refresh with initiative entered,
the button follows its normal behavior again. Leave Battle remains allowed.

Server-rejected individual or bulk joins also show the returned error in
`#message`. For example, a mixed bulk selection displays the names missing
initiative while the server rejects the entire action atomically. Non-JSON
errors show an HTTP-status fallback. Network errors show an explanatory message.
Existing pane-specific error messages may still appear as well.

The existing five-second global-message timeout applies and restarts on each
new rejection. Messages remain visible below the stationary button row.

## Server enforcement

The prior server gate is unchanged: individual and bulk joins require integer
initiative. Clearing it while active is rejected; leave first or submit
active=false and initiative=null together. Imports cannot newly activate
characters/monsters without initiative. Legacy active missing-initiative records
must be corrected or leave before starting a battle. Lairs remain unchanged.

The UI script observes row rendering and intercepts blocked individual clicks.
It wraps fetch to mirror failed same-origin character/monster join requests to
#message, using a cloned response so existing request/error handling still works.
Successful joins and unrelated API errors do not create a rejection message.

## Checks

```sh
node --test tests/initiative-join-gate.test.cjs
node --check static/initiative-join-gate.js
python -m unittest discover -s tests -p 'test_initiative_join_gate.py' -v
```
