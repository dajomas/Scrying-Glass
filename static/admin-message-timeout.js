/* Clear global messages five seconds after the most recent text update. */
(() => {
    'use strict';
    const area = document.getElementById('message');
    if (!area) return;
    let timeout = null;
    function restart() {
        clearTimeout(timeout);
        timeout = null;
        if (!area.textContent) return;
        timeout = setTimeout(() => {
            timeout = null;
            area.textContent = '';
        }, 5_000);
    }
    const observer = new MutationObserver(restart);
    observer.observe(area, {childList: true, characterData: true, subtree: true});
    restart();
})();
