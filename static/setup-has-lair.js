(() => {
    'use strict';
    const checkbox = document.getElementById('setupHasLair');
    const pane = document.getElementById('lairTools');
    const toggle = document.getElementById('toggleLairPane');
    if (!checkbox || !pane || !toggle) return;
    let snapshot = null, pending = false;
    const enabled = state => state?.has_lair === true;
    function draw(value) {
        checkbox.checked = value;
        pane.dataset.setupHasLair = String(value);
        toggle.dataset.setupHasLair = String(value);
    }
    const render = window.scryingLairsRender;
    window.scryingLairsRender = function (state) {
        snapshot = state;
        if (!pending) draw(enabled(state));
        return typeof render === 'function' ? render.apply(this, arguments) : undefined;
    };
    checkbox.addEventListener('change', async () => {
        if (pending || !snapshot) { draw(enabled(snapshot)); return; }
        const scope = {campaign_id: snapshot.active_campaign_id, setup: snapshot.active_setup ?? null};
        const chosen = checkbox.checked;
        pending = true;
        checkbox.disabled = true;
        draw(chosen);
        try {
            await request('/api/setups/has-lair', {
                method: 'PATCH', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({has_lair: chosen, scope}),
            });
        } catch (error) {
            paneNotification('battleSetup', error.message);
        } finally {
            pending = false;
            await load();
            draw(enabled(snapshot));
            checkbox.disabled = false;
        }
    });
    draw(false);
    if (typeof latest !== 'undefined' && latest) window.scryingLairsRender(latest);
})();
