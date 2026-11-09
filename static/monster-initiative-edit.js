/* Monster Edit bonus UI; character editing remains delegated unchanged. */
(() => {
    const renderMonster = monsterEdit;
    monsterEdit = function(monster) {
        const template = document.createElement('template');
        template.innerHTML = renderMonster(monster);
        const total = template.content.querySelector('input[name="initiative"]');
        total.readOnly = true;
        total.removeAttribute('min');
        total.removeAttribute('max');
        total.setAttribute('aria-describedby', 'editMonsterBonusHelp');
        total.parentElement.firstChild.textContent = 'Initiative total (calculated or legacy) ';

        const label = document.createElement('label');
        label.textContent = 'Initiative bonus ';
        const bonus = document.createElement('input');
        bonus.name = 'initiative_bonus';
        bonus.type = 'text';
        bonus.inputMode = 'numeric';
        bonus.pattern = '([+]|-)?[0-9]+';
        bonus.value = String(monster.initiative_bonus ?? 0);
        bonus.defaultValue = bonus.value;
        bonus.dataset.assignedBonus = bonus.value;
        bonus.setAttribute('aria-describedby', 'editMonsterBonusHelp');
        label.appendChild(bonus);
        total.parentElement.before(label);
        const help = document.createElement('p');
        help.id = 'editMonsterBonusHelp';
        help.className = 'field-help full';
        help.textContent = 'Enter a signed whole-number bonus, not a dice roll. ' +
            'Blank or unchanged keeps the assigned bonus and its origin. Explicit changes are manual. ' +
            'A retained raw roll recalculates the total; otherwise a legacy total stays unchanged. ' +
            'Saving does not roll initiative.';
        total.parentElement.after(help);
        return template.innerHTML;
    };

    const form = document.querySelector('#editForm');
    const previousSubmit = form.onsubmit;
    let saving = false;
    form.onsubmit = async function(event) {
        if (!editing || editing.kind !== 'monsters') {
            return previousSubmit.call(this, event);
        }
        event.preventDefault();
        if (saving || !form.reportValidity()) return;
        const target = {kind: editing.kind, id: editing.id};
        const payload = new FormData(form);
        payload.set('name', form.elements.name.value.trim());
        payload.set('monster_species', form.elements.monster_species.value.trim());
        const bonus = form.elements.initiative_bonus;
        const value = bonus.value.trim();
        if (!value || value === bonus.dataset.assignedBonus) {
            payload.delete('initiative_bonus');
        } else {
            payload.set('initiative_bonus', value);
        }
        const image = payload.get('image');
        if (!(image instanceof File) || !image.name) payload.delete('image');
        const controls = [...form.querySelectorAll('input, select, button')];
        const disabled = controls.map(control => control.disabled);
        controls.forEach(control => { control.disabled = true; });
        form.setAttribute('aria-busy', 'true');
        saving = true;
        let applied = false;
        try {
            await request(`/api/monsters/${encodeURIComponent(target.id)}/edit`, {
                method: 'POST', body: payload,
            });
            applied = true;
            if (editing?.kind === target.kind && editing?.id === target.id) closeEdit();
            await load(true);
        } catch (error) {
            paneNotification('monsters', applied
                ? `Monster saved, but refresh failed: ${error.message}. Reload before continuing.`
                : error.message);
        } finally {
            controls.forEach((control, index) => { control.disabled = disabled[index]; });
            form.removeAttribute('aria-busy');
            saving = false;
        }
    };
})();
