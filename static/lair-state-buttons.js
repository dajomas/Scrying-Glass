/* Lair state controls mirror the character/monster toggle buttons. */
(() => {
    'use strict';
    const $ = id => document.getElementById(id);
    const join = $('lairJoinBattle'), visible = $('lairToggleVisible'), turn = $('lairToggleTurn');
    if (!join || !visible || !turn) return;
    let state = null, busy = false;

    function draw() {
        const lair = state?.lairs?.[0];
        join.textContent = lair?.active ? 'In Battle' : 'Join Battle';
        for (const [button, value] of [[join, lair?.active], [visible, lair?.visible], [turn, lair?.in_turn]]) {
            button.classList.toggle('on', Boolean(value));
            button.setAttribute('aria-pressed', String(Boolean(value)));
            button.disabled = busy || !lair || (button === turn && !lair.active);
        }
        // The existing lairs.js form reads .checked and preserves unsaved
        // name/color/notes. These invisible bridges always reflect live state.
        $('lairActive').checked = lair ? lair.active : true;
        $('lairVisible').checked = lair ? lair.visible : true;
    }
    const render = window.scryingLairsRender;
    window.scryingLairsRender = function (snapshot) {
        const result = typeof render === 'function' ? render.apply(this, arguments) : undefined;
        state = snapshot;
        draw();
        return result;
    };
    async function toggle(field) {
        const lair = state?.lairs?.[0];
        if (busy || !lair || (field === 'in_turn' && !lair.active)) return;
        busy = true; draw();
        try {
            const response = await fetch(`/api/lairs/${encodeURIComponent(lair.id)}`, {
                method: 'PATCH', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({[field]: !lair[field]}),
            });
            if (!response.ok) {
                const data = await response.json().catch(() => ({}));
                throw new Error(typeof data.detail === 'string' ? data.detail : `Request failed (${response.status})`);
            }
            const updated = await response.json();
            if (state?.lairs?.[0]?.id === updated.id) state = {...state, lairs: [updated]};
            await load();
            $('lairNotice').textContent = 'Lair updated.';
        } catch (error) {
            $('lairNotice').textContent = error.message;
        } finally {
            busy = false; draw();
        }
    }
    join.onclick = () => toggle('active');
    visible.onclick = () => toggle('visible');
    turn.onclick = () => toggle('in_turn');
    if (typeof latest !== 'undefined' && latest) state = latest;
    draw();
})();
