(() => {
    'use strict';
    function install() {
        const note = document.getElementById('lairActiveStatus');
        if (!note) return;
        function draw(snapshot) {
            const lairs = snapshot?.lairs || [];
            const lair = lairs.find(item => item.active) || lairs[0];
            const text = !lair ? 'No Lair'
                : `${lair.active ? 'Active Lair' : 'Lair'}: ${lair.name || 'Lair'}`;
            if (note.textContent !== text) note.textContent = text;
            note.classList.toggle('has-active-lair', Boolean(lair?.active));
            note.classList.toggle('no-active-lair', !lair?.active);
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
