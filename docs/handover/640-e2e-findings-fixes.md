# 640 - Fixes for the SG-TODO-021 Stage 4 findings

[Back to HANDOVER index](../../HANDOVER.md)

User request, 2026-11-14, delivered on `features/perplexity-021` (follow-up to SG-TODO-021; no TODO ID assigned). User instruction: "Please fix the open findings". The findings are listed in the [610 handover](610-playwright-end-to-end-suite.md#findings-for-a-follow-up-no-application-change-made). For the restart finding the user chose "Keep sign-ins in memory" (2026-11-14): a restart still signs everyone out, but the pages now go to the sign-in page.

## Changes

- **Focus return after the New campaign dialog.** `static/admin-dialog-accessibility.js` (now `?v=2`) records the last control used outside every overlay (`focusin`, and `pointerdown` for browsers that do not focus a clicked button). When a dialog's opener has already moved focus into the dialog before the hidden-attribute observer runs, that control is stored as the opener, so closing the dialog returns focus to it. The rule "return focus only when it was lost with the overlay" is unchanged.
- **Restart sign-out.**
  - Client Display (`static/client.js`, now `?v=2`): after every WebSocket close it checks the sign-in with `/api/state`, not only after close code 1008. A handshake rejected for a missing session closes with 1006, so the old check never ran and the display stayed on "Reconnecting…". While the server is down the check fails and reconnecting continues as before; once the server answers 401 the display goes to `/login`.
  - Admin: new `static/admin-session-expiry.js?v=1`, loaded before `admin-view-restore.js` in `templates/admin/190_document_end.html`. When an Admin `/api/` call answers 401, it confirms with `/api/state` and then goes to `/login`, instead of repeating "Background refresh failed: Sign in required". Other 401 answers keep their normal handling. Sessions stay in server memory (no security change).
- **axe findings.**
  - Login page (`web_html/login_html.py`): `<html lang="en">` and a `<main>` around the form (fixes `html-has-lang`, `landmark-one-main`, `region`).
  - Client Display (`web_html/client_html.py`): `<html lang="en">`, a `<main>` around `#initiative` and `#stage`, and a visually hidden `<h1>Scrying Glass display</h1>` (fixes `html-has-lang`, `landmark-one-main`, `page-has-heading-one`). `static/client.css` (now `?v=2`) gives `main` the column layout the body had and adds `.sg-visually-hidden`.
  - Battle preparation: the image preview captions in `static/monster-image-previews.js` (now `?v=2`) keep `aria-live="polite"` but no longer carry `role="status"`, which is not allowed on `figcaption` (fixes `aria-allowed-role`).
- **Header controls at narrow widths.** The workflow tabs (`static/admin-workflow-navigation.css`) and the panel toggle strip (`static/admin-header-hierarchy.css`) now wrap onto more lines instead of scrolling sideways, so at 360 and 768 px no tab or toggle runs past the screen edge. The roster action buttons stay in their horizontally scrolling roster tables, as before.
- No admin fragment changed (the 8 fragments and the 20,000-byte limit are untouched).

## Tests

- `e2e/test_layout_accessibility.py`: the axe test now requires zero violations on all six pages (the baseline is removed); the strict xfail on the campaign focus return is removed, so it is a normal test; the width test also checks that every workflow tab and panel toggle is inside the viewport.
- `e2e/test_feedback.py`: after a restart the Client Display and the Admin page are expected to reach `/login` by themselves.
- `tests/test_monster_image_previews.py`: the script version pin is now `?v=2`.

## Validation (local, this sandbox)

- `e2e/test_layout_accessibility.py` and `e2e/test_feedback.py`, Chromium and Firefox: 32 passed (including the focus-return test, the zero-violation axe scan and both restart tests).
- `e2e/test_view_restore.py`, `e2e/test_access.py` and `e2e/test_client_display.py`, both browsers: 27 passed.
- Node checks for `client.js`: `test_display_reconnect.js`, `test_bughunt_504cb25.js`, `test_bughunt_985b4b2.js`, `test_lair_presentation.js` passed.
- `tests/test_admin_header_hierarchy.py`, `tests/test_browser_smoke.py`, `tests/test_monster_image_previews.py`: the same 16 sandbox-only failures with and without this change (identical failure lists); `test_logout.py`, `test_display_connection.py` and `test_bughunt_711881a.py` passed. These sandbox failures mean the header-hierarchy browser test did not validate the wrapping change here; CI runs the full suite on a normal branch, but no CI runs on `features/perplexity-021`.
- Not yet run with `tools/run_e2e.sh` on the user's host. User acceptance is pending.
