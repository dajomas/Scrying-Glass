# Admin campaign ownership

## Ownership rules

Each campaign can be assigned to one regular admin. A regular admin may own
multiple campaigns. Regular admins see only their own campaigns and may manage
only owned campaign data. Superadmins may see and reassign all campaigns.

A campaign created by a regular admin is immediately connected to its creator.
A campaign imported by a regular admin is also connected to that admin. Campaigns
created by a superadmin remain unassigned until assigned to a regular admin.

## One-time migration

Only users whose role is exactly `admin` are counted; superadmins are excluded.

| Regular admins at first migration | Existing campaigns |
| --- | --- |
| Exactly one | Assign all existing campaigns to that admin |
| More than one | Leave all campaigns unassigned, even with only one campaign |
| None | Leave all campaigns unassigned |

The migration is not rerun on subsequent restarts or after user-count changes.
Admins with no assignments may still log in. They receive an empty campaign list
and no other owner's encounter state. They may create their own new campaign.

## Superadmin reassignment

Sign in as a superadmin and open the existing Users page. The Campaign ownership
section lists every campaign, with a regular-admin dropdown and Save owner button.
Select an admin (or Unassigned), save and confirm. Refresh campaign owners reloads
the list. Removing an admin or changing that user away from the admin role clears
their assignments. It does not transfer ownership to another account automatically.

Ownership and client viewer rights are independent. Reassignment retains existing
client grants. Regular admins' access on the viewer page follows their ownership;
superadmins retain access to all campaigns. Client users still use explicit viewer
grants. A later request rechecks the database rather than relying on login-time
cached ownership.

## Active campaign and access checks

The application still has ONE shared live active campaign. This patch does not
create an independent live runtime per admin. If another owner's campaign is
active, the admin page returns blank encounter state and prompts the admin to
select a campaign they own and click Switch. Generic encounter edits cannot
change another owner's active state.

Server guards cover campaign targets, setup source/destination fields, active
encounter mutations, viewer-grant management and normal checkpoint/bundle routes.
Viewer snapshots use their own authorized projection without inheriting an
administrator's request scope. Global display-connection metadata is not returned
to regular admins; superadmin monitoring remains unchanged.

Deleting the active campaign requires a permitted replacement. If a regular
admin has no other owned replacement, the operation is rejected rather than
opening another owner's campaign; ask a superadmin to perform that deletion.

## Storage, upgrade and rollback

Startup installs the additive campaign_owners table, index and role-change
trigger through composed APIRouter lifespans. It uses the existing pre-upgrade
backup helper. No main PRAGMA user_version change or manual SQL is needed.
Ownership is installation-local and is not imported from campaign bundle metadata.
Back up the whole data directory before upgrading. To roll back the migration,
restore the matching database backup and previous application files; older code
does not enforce these ownership restrictions.

## Validation

Run:

```sh
python -m unittest discover -s tests -p 'test_campaign_ownership.py' -v
```

The 23 focused backend tests include the six migration subcases, ownership
assignment, state filtering, cross-owner denial, transfers, reassignment, role
changes, restart persistence, client grants and request-context cleanup.

See Patch/campaign-ownership-test-results.md for exact limitations. The browser
UI and real FastAPI startup/HTTP integration are still pending validation.
