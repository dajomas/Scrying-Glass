# Campaign backups in Campaign Setup

Documented baseline: `features/development` at `4f401b4adfca92e9c9599aea8924c14efb49aea4`.

Expand Campaign Setup > Campaign backups to export or import a portable ZIP bundle. The panel is initially collapsed and follows Campaign Setup visibility, not Encounter tools visibility.

`static/campaign-backups.js` moves the existing panel into `#campaignInputPane` before feature handlers attach. It moves nodes rather than cloning them, retaining IDs and input state. The scoped stylesheet displays export/import side by side and stacks them below 700px.

Export contains the active campaign’s private GM data and referenced local media, not accounts or a full-instance backup. Import creates a new inactive campaign. See [Encounter Features](Encounter-Features.md#6-checkpoints-and-campaign-bundles) for limits and resuming the imported runtime encounter.

Check: `node tests/test_campaign_backups_layout.js`. For disaster recovery, stop the service and back up the whole storage directory plus configuration and matching code.
