/* Relocate the existing controls without replacing them or their event handlers. */
(() => {
    'use strict';
    function moveCampaignBackups() {
        const campaignPane = document.getElementById('campaignInputPane');
        if (!campaignPane || campaignPane.querySelector('.campaign-backups-panel')) return;
        const backupPanel = document.querySelector('#encounterFeatures .et-backup-panel');
        if (!backupPanel) return;
        if (!backupPanel.querySelector('#exportBundle') || !backupPanel.querySelector('#importBundle')) {
            console.warn('Campaign backups relocation skipped: expected controls are missing.');
            return;
        }
        backupPanel.classList.add('campaign-backups-panel');
        campaignPane.appendChild(backupPanel);
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', moveCampaignBackups, {once: true});
    } else {
        moveCampaignBackups();
    }
})();
