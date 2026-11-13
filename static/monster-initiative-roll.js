/* Render raw rolls before table replacement; leave character totals unchanged. */
(() => {
    'use strict';
    const region = document.getElementById('monsters');
    if (!region) return;
    function decorate(input, monster) {
        if (!input || input.dataset.rawInitiative) return;
        const raw = monster.initiative_roll ?? null;
        const exact = raw === null || Number.isSafeInteger(raw);
        const text = raw === null || !exact ? '' : String(raw);
        input.defaultValue = text;
        input.value = text;
        input.readOnly = !exact;
        input.step = '1';
        input.removeAttribute('min');
        input.removeAttribute('max');
        input.dataset.rawInitiative = 'true';
        input.placeholder = exact ? 'roll' : 'Unavailable';
        input.setAttribute('aria-label', `${monster.name || 'Monster'} initiative raw roll`);
        input.title = 'Raw roll only. The server adds the assigned bonus once.';
        const label = document.createElement('label');
        label.textContent = 'Roll ';
        input.before(label);
        label.append(input);
        const total = document.createElement('output');
        total.className = 'sg-monster-initiative-total';
        total.style.display = 'block';
        const value = monster.initiative;
        total.textContent = value == null ? 'Total: unset' : Number.isSafeInteger(value)
            ? `Total: ${value}${raw === null ? ' (legacy)' : ''}` : 'Total: unavailable';
        label.after(total);
    }
    const render = monsterRow;
    monsterRow = function(monster) {
        const template = document.createElement('template');
        template.innerHTML = render(monster);
        decorate(template.content.querySelector('input[data-mi]'), monster);
        return template.innerHTML;
    };
    const items = typeof latest !== 'undefined' ? latest?.monsters || [] : [];
    const byId = new Map(items.map(item => [String(item.id), item]));
    for (const input of region.querySelectorAll('input[data-mi]')) {
        const item = byId.get(input.dataset.mi);
        if (item) decorate(input, item);
    }
    const feedback = window.scryingAdminFeedback;
    const pending = new Map();
    function begin(operation, target, field) {
        return feedback.begin({region: 'monsters', operation: 'monster.raw-roll.' + operation,
            target, label: 'Monster initiative raw roll', ...(field ? {field} : {})});
    }
    region.addEventListener('change', async event => {
        const input = event.target;
        if (!(input instanceof HTMLInputElement) || !input.matches('input[data-mi]')) return;
        event.stopPropagation();
        const target = String(input.dataset.mi);
        const previous = pending.get(target);
        if (previous && feedback.isCurrent(previous.ticket)) return;
        // Deliverable 2: the validation error is associated with this monster's raw-roll input.
        const validation = begin('validation', target, feedback.initiativeField?.('monsters', target));
        const name = (typeof latest !== 'undefined' ? latest?.monsters || [] : [])
            .find(item => String(item.id) === target)?.name;
        const text = input.value.trim();
        const roll = text === '' ? null : Number(text);
        if (!input.checkValidity() || (text !== '' &&
            (!/^[+-]?[0-9]+$/.test(text) || !Number.isSafeInteger(roll)))) {
            feedback.publish(validation, {severity: 'error',
                text: (name ? name + ': ' : '') + 'Enter an exactly representable whole-number raw roll or leave it blank.'});
            return;
        }
        feedback.resolve(validation);
        const ticket = begin('request', target);
        const refresh = begin('refresh', target);
        const attempt = {ticket};
        pending.set(target, attempt);
        const current = () => feedback.isCurrent(ticket) && feedback.isCurrent(refresh);
        let applied = false;
        try {
            await request(`/api/monsters/${encodeURIComponent(target)}/initiative-roll`, {
                method: 'PATCH', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({initiative_roll: roll}),
            });
            applied = true;
            if (!current()) return;
            await load(true);
            if (!current()) return;
            feedback.resolve(ticket);
            feedback.resolve(refresh);
        } catch (error) {
            if (!current()) return;
            if (applied) {
                feedback.resolve(ticket);
                feedback.publish(refresh, {severity: 'error',
                    text: `Roll saved, but refresh failed: ${error.message}. Reload before continuing.`});
            } else {
                feedback.publish(ticket, {severity: 'error', text: error.message});
            }
        } finally {
            if (pending.get(target) === attempt) pending.delete(target);
        }
    });
})();
