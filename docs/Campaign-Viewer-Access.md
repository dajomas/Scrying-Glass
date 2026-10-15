# Campaign viewer access

## Admin workflow

1. Select a campaign in the campaign dropdown on the admin page.
2. Open **Viewer access** and check the campaign name in its heading.
3. Select the client-role users allowed to view that campaign.
4. Choose **Save viewer access**.

The viewer editor uses the selected campaign from the administrator's authorized
campaign list. It does NOT require that campaign to be the globally active live
campaign. Changing the dropdown updates this editor without activating a campaign.
The main **Switch** button still controls the shared live campaign separately.

If the dropdown has no authorized selection, the editor falls back to the
permitted active campaign, then the first permitted campaign. With no assigned
campaigns it shows an assignment message and does not fetch a viewer user list.
The editor heading identifies the exact campaign to which Save applies.

All existing client-role users are listed for a permitted campaign. Which
checkboxes are checked is campaign-specific. A client can be granted multiple
campaigns and a campaign can have multiple clients. Ownership checks on the
server are unchanged; admins cannot edit viewer grants for another owner's
campaign, even by changing a dropdown value or calling the API directly.

## Viewer workflow

No granted campaigns shows an access message and no encounter data. One granted
campaign opens automatically. Multiple granted campaigns prompt selection before
displaying data; the campaign heading reopens the switcher. Selection changes
the viewer URL without changing the administrator's active campaign.

The shared active campaign supplies live state; other campaigns use their saved
setup/roster through the existing loader. Historical turns are not revived.
Revocation clears denied state on the next scoped update. Client grants are
independent of admin ownership and retained when an owner is reassigned.

## Storage and security

Existing campaign_viewers storage, role-cleanup rules and migration behavior are
unchanged by the editor-selection correction. No user or ownership data needs
repair for this UI issue. Existing role, same-origin and per-campaign checks
remain authoritative for both viewer-grant reads and writes. This correction
requires no database migration, API route change or runtime dependency.

Server/permission errors appear in the editor's status area rather than being
reported as an empty list of client-role users. Successful background refreshes
for the same selected campaign preserve unsaved checkbox edits. Old responses
cannot overwrite a newer campaign selection.

## Focused browser regressions

```sh
python -m unittest discover -s tests -p 'test_campaign_viewer_admin_selection.py' -v
node --check static/campaign-viewer-admin.js
```

The browser tests require Playwright and Chromium as test-only tooling. They use
mocked API replies representing ownership-filtered data, not a running authenticated
FastAPI application. Backend authorization is retained, not reimplemented here.
