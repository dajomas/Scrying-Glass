# Admin page header and scrolling

The page title, top pane-control button row and global message area remain
stationary. Messages appear immediately below the button row and stay visible
when the panes are scrolled. An empty message reserves no space.

All panes, including the activity log, share one vertically scrollable region
below the complete header. The activity log expands vertically; wide tables can
still scroll horizontally. Dialogs retain viewport-wide fixed overlays.

## Implementation

`body.admin-shell` is a viewport-height flex column with document scrolling
disabled. `#adminHeader` keeps its natural height; `#adminScroll` fills the
remaining space with `min-height: 0` and overflow auto. Wrapped toolbar buttons
and messages automatically resize the available pane area without fixed offsets.

`#message` is a single direct child of `#adminHeader`, after `#adminButtonBar`.
Its ID, message helper and existing callers are unchanged. The existing
`role="status"` and `aria-live="polite"` remain. CSS hides empty messages and
wraps long unbroken text. No message element remains inside the scroll region.

Styles are in `static/admin-shell.css`. The main container closes after the
activity log. Button order and pane visibility rules are unchanged.

## Regression checks

```sh
python -m unittest discover -s tests -p 'test_admin_shell_layout.py' -v
```

Requires Playwright and Chromium for tests only. Nine checks cover header
spacing, shared scrolling, responsive boundaries, conditional buttons, expanding
log, modal stacking, message visibility after scroll, clearing messages and long
message wrapping. The message tests execute the existing admin.js message
setter. Other application scripts are disabled in the local layout fixture;
authenticated operations are not exercised.
