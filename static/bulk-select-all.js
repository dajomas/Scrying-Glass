/* Reuse the existing selection sets; do not merely check DOM boxes. */
(() => {
    'use strict';
    document.querySelectorAll('button[data-select-all-kind]').forEach(button=>{
        button.addEventListener('click',()=>{
            const kind=button.dataset.selectAllKind;
            if(kind!=='characters'&&kind!=='monsters')return;
            if(typeof latest==='undefined'||!latest||!Array.isArray(latest[kind]))return;
            setAllSelected(kind,true);
        });
    });
})();
