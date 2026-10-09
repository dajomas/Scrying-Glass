/* Pure preview; the server remains authoritative. No negative HP balance. */
window.scryingDamagePreview=function(item,delta,absorb=true) {
    const hp=Math.max(0,item.hp||0),temp=item.temp_hp||0,maximum=Math.max(0,item.max_hp||0);
    const character=!('monster_species' in item);
    const dead=item.life_state==='dead'||(character&&(item.death_failures||0)>=3);
    if(dead)return `${item.name}: already dead; explicitly recover before healing or damaging.`;
    const damage=delta<0?-delta:0,consumed=absorb?Math.min(temp,damage):0,effective=damage-consumed;
    const nextHp=delta<0?Math.max(0,hp-effective):hp+delta;
    let outcome='';
    if(character&&damage) {
        const excess=Math.max(0,effective-hp);
        if(nextHp===0&&excess>0&&excess>=maximum)outcome=' Instant death from excess damage.';
        else if(hp===0) {
            const failures=(item.life_state==='stable'?0:(item.death_failures||0))+1;
            outcome=` Death-save failures: ${Math.min(3,failures)}/3.${failures>=3?' The character dies.':''}`;
        } else if(nextHp===0)outcome=' The character is downed (no failure for this initial drop).';
    }
    return `${item.name}: HP ${hp} → ${nextHp}; temporary HP ${temp} → ${temp-consumed}.${outcome} Apply?`;
};
