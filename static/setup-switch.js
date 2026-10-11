(() => {
    'use strict';
    function install() {
        const select = document.getElementById('setupSelect');
        const button = document.getElementById('loadSetup');
        if (!select || !button) return;
        let busy = false;
        const activeReference = () => typeof latest === 'undefined' ? null : latest?.active_setup;
        async function switchSetup(event) {
            event?.preventDefault();
            if (busy) return;
            const name = select.value;
            const reference = activeReference();
            const campaign = typeof campaignData === 'undefined' ? null : campaignData.active;
            if (!name) {
                paneNotification('battleSetup', 'Choose a saved battle setup to load');
                return;
            }
            if (!campaign) {
                paneNotification('battleSetup', 'Choose an active campaign first');
                return;
            }
            if (reference?.name === name && reference?.campaign_id === campaign) return;
            busy = true;
            const disabled = [select.disabled, button.disabled];
            select.disabled = button.disabled = true;
            let applied = false;
            try {
                const result = await request('/api/setups/load', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name, campaign}),
                });
                applied = true;
                document.getElementById('setupName').value = result?.name || name;
                await load();
                await setups();
                select.value = result?.name || name;
                paneNotification('battleSetup', `Loaded battle setup: ${result?.name || name}`);
            } catch (error) {
                if (!applied) select.value = reference?.name || '';
                paneNotification('battleSetup', applied
                    ? `Battle setup switched, but refresh failed: ${error.message}. Reload the page.`
                    : error.message);
            } finally {
                select.disabled = disabled[0];
                button.disabled = disabled[1];
                busy = false;
            }
        }
        // Replace only setup-load event handlers, not the global confirm function.
        select.onchange = switchSetup;
        button.onclick = switchSetup;
    }
    if (document.readyState !== 'complete') {
        document.addEventListener('DOMContentLoaded', install, {once: true});
    } else install();
})();
