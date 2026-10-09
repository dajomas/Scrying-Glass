/* Per-page visibility state; temporary battle visibility does not overwrite preference. */
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
    const controller=window.createEncounterVisibility(visible=>{
        pane.dataset.etVisible=String(visible);pane.hidden=!visible;
        button.textContent=visible?'Hide encounter tools':'Show encounter tools';
        button.setAttribute('aria-expanded',String(visible));
    });
    button.addEventListener('click',()=>controller.toggle());
    window.updateEncounterToolsVisibility=state=>controller.update(state);
})();
