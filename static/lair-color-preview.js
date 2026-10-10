/* Lair preview: update on picker edits and programmatic encounter refreshes. */
(() => {
    'use strict';
    const input = document.getElementById('lairColor');
    const preview = document.getElementById('lairColorPreview');
    if (!input || !preview || preview.dataset.previewInstalled) return;
    preview.dataset.previewInstalled = 'true';

    function update() {
        preview.style.backgroundColor = input.value;
    }
    input.addEventListener('input', update);
    input.addEventListener('change', update);

    // lairs.js runs first. Its renderer preserves unsaved input and sets colors
    // after setup switches, undo and refresh; read the actual input afterwards.
    const render = window.scryingLairsRender;
    if (typeof render === 'function') {
        window.scryingLairsRender = function (...args) {
            const result = render.apply(this, args);
            update();
            return result;
        };
    }
    update();
})();
