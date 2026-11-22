/* SG-TODO-029: distinct default monster color for the Add Monster and Import .monster forms.
 * Same palette and rule as python/scrying_glass_monster_palette.py: the first palette color
 * no monster in the battle setup uses, else the least used one. Characters do not count.
 * A color picked by hand is kept until its form is reset. While the computed default is
 * used, the form sends color_auto=true and each further copy gets the next color. */
(() => {
    const PALETTE = [
        '#842029', '#1d5fa8', '#2b7a34', '#7a3fa8',
        '#a8540f', '#127a84', '#a3195b', '#6b5a1a',
        '#4250b8', '#5f7a12', '#b0331f', '#4f5f6e',
    ];
    const fields = [
        {form: '#monsterForm', input: '#monsterColor', preview: '#monsterColorPreview'},
        {form: '#monsterUpload', input: '#monsterFileColor', preview: '#monsterFileColorPreview'},
    ];
    let monsters = [];

    function nextColor(items) {
        const counts = new Map(PALETTE.map(color => [color, 0]));
        for (const item of items) {
            const key = String(item?.color || '').trim().toLowerCase();
            if (counts.has(key)) counts.set(key, counts.get(key) + 1);
        }
        return PALETTE.reduce((best, color) => counts.get(color) < counts.get(best) ? color : best);
    }

    function autoField(field) {
        const form = document.querySelector(field.form);
        if (!form) return null;
        let hidden = form.querySelector('input[name="color_auto"]');
        if (!hidden) {
            hidden = document.createElement('input');
            hidden.type = 'hidden';
            hidden.name = 'color_auto';
            form.append(hidden);
        }
        return hidden;
    }

    function apply() {
        const color = nextColor(monsters);
        for (const field of fields) {
            const input = document.querySelector(field.input);
            if (!input) continue;
            const auto = autoField(field);
            if (input.dataset.handPicked === 'true') {
                if (auto) auto.value = '';
                continue;
            }
            if (auto) {
                auto.value = 'true';
                auto.defaultValue = 'true';
            }
            input.value = color;
            input.defaultValue = color;  // a later form.reset() keeps the computed default
            const preview = document.querySelector(field.preview);
            if (preview) {
                if (typeof setColorPreview === 'function') setColorPreview(preview, color);
                else preview.style.backgroundColor = color;
            }
        }
    }

    for (const field of fields) {
        const input = document.querySelector(field.input);
        const form = document.querySelector(field.form);
        if (!input) continue;
        input.addEventListener('input', () => {
            input.dataset.handPicked = 'true';
            const auto = autoField(field);
            if (auto) auto.value = '';
        });
        form?.addEventListener('reset', () => {
            delete input.dataset.handPicked;
            setTimeout(apply);  // after the browser restores the defaults
        });
    }

    window.scryingMonsterColorState = state => {
        monsters = Array.isArray(state?.monsters) ? state.monsters : [];
        apply();
    };
    window.scryingMonsterDefaultColor = nextColor;
    if (typeof latest !== 'undefined' && latest) window.scryingMonsterColorState(latest);
})();
