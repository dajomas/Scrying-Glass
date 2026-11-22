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
            const item = (typeof latest === 'undefined' ? null : latest)?.characters?.find(c => c.id === current.dataset.chp);
            if (window.scryingTracksHp && !window.scryingTracksHp(item)) {  // SG-TODO-024
                text.textContent = 'Not tracked';
                text.title = 'The player keeps this character\u2019s HP. Use Edit to track it.';
                cell.replaceChildren(text);
                continue;
            }
            text.textContent = current.value + '/' + maximum.value;
            text.title = 'Current / maximum HP. Use Edit to change these values.';
            cell.replaceChildren(text);
        }
    }
    new MutationObserver(render).observe(region, {childList: true});
    render();
})();
