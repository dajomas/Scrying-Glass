/* Compatibility helper retained for callers; the Admin UI now uses an explicit dialog. */
window.createEncounterVisibility=function(render) {
    let visible=false,inBattle=false,beforeBattle=false;
    function set(value) {visible=Boolean(value);render(visible);}
    set(false);
    return {
        toggle() {set(!visible);},
        update(state) {
            const active=Number.isInteger(state?.battle_round)&&state.battle_round>0;
            if(active&&!inBattle) {beforeBattle=visible;inBattle=true;set(true);}
            else if(!active&&inBattle) {inBattle=false;set(beforeBattle);}
        },
        get visible() {return visible;},
        get inBattle() {return inBattle;}
    };
};
(() => {
    'use strict';
    const pane=document.getElementById('encounterFeatures');
    const button=document.getElementById('toggleEncounterTools');
    if(!pane||!button)return;
    pane.dataset.etVisible='false';pane.hidden=true;
    button.textContent='Encounter tools';
    button.setAttribute('aria-expanded','false');
    button.setAttribute('aria-haspopup','dialog');
    // Keep aria-controls until navigation records the original opener's view filter.
    button.addEventListener('click',()=>window.scryingOpenEncounterTools?.());
    // Battle transitions/refresh must never open a seldom-used popup automatically.
    window.updateEncounterToolsVisibility=()=>{};
})();
