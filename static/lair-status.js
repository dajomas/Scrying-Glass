(() => {
    'use strict';
    function install() {
        const note = document.getElementById('lairActiveStatus');
        if (!note) return;
        function draw(snapshot) {
            const active = (snapshot?.lairs || []).filter(lair => lair.active);
            const text = active.length
                ? `${active.length === 1 ? 'Active lair' : 'Active lairs'}: ${active.map(lair => lair.name || 'Lair').join(', ')}`
                : 'No active lair.';
            if (note.textContent !== text) note.textContent = text;
            note.classList.toggle('has-active-lair', active.length > 0);
            note.classList.toggle('no-active-lair', active.length === 0);
        }
        const render = window.scryingLairsRender;
        window.scryingLairsRender = function (snapshot) {
            const result = typeof render === 'function' ? render.apply(this, arguments) : undefined;
            draw(snapshot);
            return result;
        };
        if (typeof latest !== 'undefined' && latest) draw(latest);
    }
    // Install after the existing deferred lair render/control scripts.
    if (document.readyState !== 'complete') {
        document.addEventListener('DOMContentLoaded', install, {once: true});
    } else install();
})();
