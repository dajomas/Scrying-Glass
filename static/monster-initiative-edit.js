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

    let editSequence = 0;
    const previousOpen = openEdit;
    openEdit = function(...args) {
        editSequence++;
        return previousOpen.apply(this, args);
    };
    const form = document.querySelector('#editForm');
    const previousSubmit = form.onsubmit;
    const pending = new Map();
    let busyOwner = null;
    form.onsubmit = async function(event) {
        if (!editing || editing.kind !== 'monsters') {
            return previousSubmit.call(this, event);
        }
        event.preventDefault();
        const feedback = window.scryingAdminFeedback;
        const session = editing;
        const sequence = editSequence;
        const target = JSON.stringify(['monsters', session.id]);
        const previous = pending.get(target);
        if (previous && (feedback.isCurrent(previous.refresh) || previous.session === session)) return;
        const spec = {region: 'monsters', operation: 'monster.edit', target, label: 'Save monster'};
        const validation = feedback.begin({...spec, operation: 'monster.edit.validation'});
        if (!form.reportValidity()) {
            feedback.publish(validation, {severity: 'error', text: 'Correct the invalid monster fields before saving.'});
            return;
        }
        feedback.resolve(validation);
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
        const ticket = feedback.begin(spec);
        const refresh = feedback.begin({...spec, operation: 'monster.edit.refresh'});
        const attempt = {refresh, session};
        pending.set(target, attempt);
        const controls = [...form.querySelectorAll('input, select, button')];
        const disabled = controls.map(control => control.disabled);
        controls.forEach(control => { control.disabled = true; });
        form.setAttribute('aria-busy', 'true');
        busyOwner = attempt;
        const current = () => feedback.isCurrent(ticket) && feedback.isCurrent(refresh) &&
            editing === session && !editModal.hidden && sequence === editSequence;
        try {
            try {
                await request(`/api/monsters/${encodeURIComponent(session.id)}/edit`, {
                    method: 'POST', body: payload,
                });
            } catch (error) {
                if (current()) feedback.publish(ticket, {severity: 'error', text: error.message});
                return;
            }
            if (!current()) return;
            feedback.resolve(ticket);
            closeEdit();
            try {
                await load(true);
                if (editing === null && editModal.hidden && sequence === editSequence) feedback.resolve(refresh);
            } catch (error) {
                if (editing === null && editModal.hidden && sequence === editSequence) {
                    feedback.publish(refresh, {severity: 'error',
                        text: `Monster saved, but refresh failed: ${error.message}. Reload before continuing.`});
                }
            }
        } finally {
            controls.forEach((control, index) => { control.disabled = disabled[index]; });
            if (busyOwner === attempt) {
                form.removeAttribute('aria-busy');
                busyOwner = null;
            }
            if (pending.get(target) === attempt) pending.delete(target);
        }
    };
})();
