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
        // SG-TODO-009.7 Stage 3: a persistent battleSetup error per setup; the next success resolves it
        // (the checkbox itself is the success indication, so no success message is shown).
        const feedback = window.scryingAdminFeedback;
        const ticket = feedback.begin({region: 'battleSetup', operation: 'setup.has-lair',
            target: JSON.stringify([scope.campaign_id, scope.setup]), label: 'Has lair'});
        try {
            await request('/api/setups/has-lair', {
                method: 'PATCH', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({has_lair: chosen, scope}),
            });
            feedback.resolve(ticket);
        } catch (error) {
            feedback.publish(ticket, {severity: 'error', text: error.message});
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
