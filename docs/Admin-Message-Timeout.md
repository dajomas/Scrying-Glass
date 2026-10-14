# Global admin message timeout

Global messages in the fixed header clear automatically after five seconds.
Each text update restarts the timer, including repeating the same message.
Manually clearing the message cancels the pending timer. Timeout clears the text
rather than deleting the element; the existing empty-message CSS hides the area
and restores space to the scrolling panes.

The global message helper and its callers are unchanged. A small deferred script,
`static/admin-message-timeout.js`, observes text mutations on `#message`, covering
both the existing helper and direct text updates. Only the global message area is
affected; per-pane notifications retain their existing timing.

Run the deterministic timer tests with:

```sh
node --test tests/admin-message-timeout.test.cjs
node --check static/admin-message-timeout.js
```

An additional real-time Chromium check (requires Playwright and Chromium) is:

```sh
python tests/admin-message-timeout-browser.py
```
