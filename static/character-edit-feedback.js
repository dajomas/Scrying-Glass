/* Stage 2: character Edit feedback; load before monster-initiative-edit.js. */
(() => {
    'use strict';
    const form = document.querySelector('#editForm');
    if (!form || form.scryingCharacterEditFeedbackInstalled) return;
    form.scryingCharacterEditFeedbackInstalled = true;
    const previousSubmit = form.onsubmit;
    const pending = new Map();
    form.onsubmit = async function(event) {
        if (!editing || editing.kind !== 'characters') {
            return previousSubmit.call(this, event);
        }
        event.preventDefault();
        const feedback = window.scryingAdminFeedback;
        const session = editing;
        const target = JSON.stringify(['characters', session.id]);
        const prior = pending.get(target);
        if (prior && (feedback.isCurrent(prior.refresh) || prior.session === session)) return;
        if (!form.reportValidity()) return;
        const data = {
            name: form.elements.name.value.trim(),
            color: form.elements.color.value,
            hp: numberValue(form, 'hp', 0),
            max_hp: numberValue(form, 'max_hp', 0),
            initiative: form.elements.initiative.value === ''
                ? null : +form.elements.initiative.value,
        };
        const spec = {region: 'characters', operation: 'character.edit',
            target, label: 'Save character'};
        const ticket = feedback.begin(spec);
        // Success settles ticket; refresh remains current through display reload.
        const refresh = feedback.begin({...spec, operation: 'character.edit.refresh',
            label: 'Refresh saved character'});
        const attempt = {refresh, session};
        pending.set(target, attempt);
        const controls = [...form.querySelectorAll('input, select, textarea, button')]
            .filter(control => control.tagName !== 'BUTTON' || control.type === 'submit');
        const disabled = controls.map(control => control.disabled);
        controls.forEach(control => { control.disabled = true; });
        const current = () => feedback.isCurrent(refresh) &&
            editing === session && !editModal.hidden;
        try {
            try {
                await request(`/api/characters/${encodeURIComponent(session.id)}`, {
                    method: 'PATCH', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data),
                });
            } catch (error) {
                if (current()) feedback.publish(ticket, {severity: 'error', text: error.message});
                return;
            }
            if (!current()) return;
            feedback.publish(ticket, {severity: 'success', text: 'Character saved.'});
            closeEdit();
            try {
                await load(true);
                feedback.resolve(refresh);
            } catch {
                // A newly opened Edit session must not receive an old refresh error.
                if (editing === null && editModal.hidden) {
                    feedback.publish(refresh, {severity: 'error', text:
                        'Character saved, but display reload failed. Reload the page; do not repeat the save.'});
                }
            }
        } finally {
            controls.forEach((control, index) => { control.disabled = disabled[index]; });
            if (pending.get(target) === attempt) pending.delete(target);
        }
    };
})();
