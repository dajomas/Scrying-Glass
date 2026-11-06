/* SG-TODO-009.1: suppress blank pane notices without changing messages or timers. */
(() => {
    'use strict';
    if (window.scryingPaneNoticeLayoutInstalled) return;
    window.scryingPaneNoticeLayoutInstalled = true;

    for (const id of ['campaignNotification', 'characterAddNotification',
                      'battleSetupNotification', 'monsterAddNotification']) {
        const notice = document.getElementById(id);
        if (!notice) continue;
        const update = () => {
            const empty = !notice.textContent.trim();
            if (notice.hidden !== empty) notice.hidden = empty;
        };
        // Observe text replacement and in-place text edits, not our hidden attribute.
        new MutationObserver(update).observe(notice, {
            childList: true, characterData: true, subtree: true,
        });
        update();
    }
})();
