/* SG-TODO-012 option 2: HP edits remain in the existing Edit dialog. */
(() => {
    'use strict';
    const region = document.getElementById('characters');
    if (!region || window.scryingCharacterHpDisplayInstalled) return;
    window.scryingCharacterHpDisplayInstalled = true;
    function render() {
        for (const current of region.querySelectorAll('input[data-chp]')) {
            const cell = current.closest('td');
            const maximum = cell?.querySelector('input[data-cmaxhp]');
            if (!cell || !maximum || current.dataset.chp !== maximum.dataset.cmaxhp) continue;
            const text = document.createElement('span');
            text.className = 'sg-character-hp';
            text.textContent = current.value + '/' + maximum.value;
            text.title = 'Current / maximum HP. Use Edit to change these values.';
            cell.replaceChildren(text);
        }
    }
    new MutationObserver(render).observe(region, {childList: true});
    render();
})();
