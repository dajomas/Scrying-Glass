'use strict';

function createRefreshSelection(rows) {
    const fields = ['initiative_bonus', 'ac', 'max_hp', 'hp'];
    const available = new Map();
    const checked = new Map();
    for (const row of rows) {
        if (!row || typeof row.id !== 'string' || !row.id || available.has(row.id)) {
            throw new Error('Invalid or duplicate refresh row');
        }
        const enabled = new Set(fields.filter(field =>
            Object.hasOwn(row.offer || {}, field) && row.offer[field] !== null &&
            row.offer[field] !== undefined));
        available.set(row.id, enabled);
        checked.set(row.id, new Set());
    }
    function cells(axis, key) {
        if (axis === 'row') {
            if (!available.has(key)) throw new Error('Unknown refresh row');
            return [...available.get(key)].map(field => [key, field]);
        }
        if (axis !== 'column' || !fields.includes(key)) {
            throw new Error('Unknown refresh column');
        }
        return [...available].filter(([, enabled]) => enabled.has(key))
            .map(([id]) => [id, key]);
    }
    function state(axis, key) {
        const entries = cells(axis, key);
        const count = entries.filter(([id, field]) => checked.get(id).has(field)).length;
        return {disabled: entries.length === 0,
                checked: entries.length > 0 && count === entries.length,
                indeterminate: count > 0 && count < entries.length};
    }
    function set(id, field, value) {
        if (!available.get(id)?.has(field)) throw new Error('Unavailable refresh field');
        if (typeof value !== 'boolean') throw new Error('Selection must be boolean');
        if (value) checked.get(id).add(field);
        else checked.get(id).delete(field);
    }
    function toggle(axis, key) {
        const value = !state(axis, key).checked;
        for (const [id, field] of cells(axis, key)) set(id, field, value);
    }
    function payload() {
        return Object.fromEntries([...checked].filter(([, selected]) => selected.size)
            .map(([id, selected]) => [id, fields.filter(field => selected.has(field))]));
    }
    return {state, set, toggle, payload};
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {createRefreshSelection};
}
