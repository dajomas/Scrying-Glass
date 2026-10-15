# Campaign viewer access

## Admin workflow

In **Campaign Setup**, open **Viewer access**. Select the client-role users who
may view the active campaign, then choose **Save viewer access**. A campaign can
have multiple viewers and a viewer can have multiple campaigns. Only existing
client-role users can be granted access. A superadmin can create users on the
Users page. Changing the active campaign changes which grants the panel edits.

Admin and superadmin accounts implicitly retain viewer access to all campaigns.
Client accounts have no access until explicitly granted: configure their grants
before expecting existing client logins to resume after this update.

## Viewer workflow

After signing in:

- No granted campaigns: show an access message and no encounter data.
- One granted campaign: open it automatically.
- Multiple granted campaigns: show a selection popup before displaying data.

The campaign heading is a keyboard-accessible button when multiple campaigns
are available. Click it to reopen the popup and switch campaigns. Switching
reloads the viewer with a campaign_id query parameter; it does not activate that
campaign in the administrator's page or affect other viewer tabs.

The administrator's active campaign uses live state. Other campaigns use their
most recently saved setup and roster through the existing setup loader. Historical
turn markers and battle-round state are not revived for these saved views.

Removing a grant triggers a new scoped WebSocket state, clearing the denied
campaign's displayed data and offering any remaining permitted campaigns. Deleted
users/campaigns lose grants through database cascades. Changing a user away from
the client role removes their explicit grants.

## Storage and security

Startup installs an additive SQLite extension: campaign_viewers, its user index,
and a role-change cleanup trigger. It uses the existing database backup helper
before the first installation. No main PRAGMA user_version bump or manual SQL
is required. An existing installation is detected on subsequent startups.

Grant-management GET/PUT endpoints require admin authorization; writes also use
the existing same-origin and transaction protections. HTTP state requests reject
unauthorized campaign IDs. Initial WebSocket states, resynchronization and broadcasts
are scoped individually using the signed-in user and current database grants.
No shared global encounter frame is sent to all viewers. Existing player-safe
filtering still excludes private effects, GM notes and hidden monster statistics.

Permissions are installation-local, not copied into portable campaign bundles.
A full database backup includes them. Existing static/media serving behavior is
unchanged; this feature controls campaign selection and state access, not DRM or
revocation of files/content a viewer has already downloaded.

Do not revert to older viewer code expecting these ACLs to remain enforced:
older application versions do not know about campaign_viewers.

## Tests

```sh
python -m unittest discover -s tests -p 'test_campaign_view*.py' -v
```

The browser tests require Playwright plus Chromium as test tooling, not runtime
application dependencies. See Patch/campaign-viewer-test-results.md for exact
scope, source basis, results and limitations.
