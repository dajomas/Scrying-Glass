/* SG-TODO-024: optional HP tracking per character.
 * Untracked characters keep their stored HP; the Admin hides HP and asks for none. */
(() => {
    'use strict';
    if (window.scryingCharacterHpTrackingInstalled) return;
    window.scryingCharacterHpTrackingInstalled = true;

    // Monsters always track HP; characters unless switched off.
    window.scryingTracksHp = item => !item || 'monster_species' in item || item.track_hp !== false;

    function toggle(checkbox, fields) {
        const apply = () => {
            for (const input of fields()) {
                const label = input.closest('label');
                if (label) {
                    label.hidden = !checkbox.checked;
                    label.style.display = checkbox.checked ? '' : 'none';  // form CSS overrides [hidden]
                }
                // Not disabled: the entry forms restore saved disabled states after a submit.
                // Hidden HP is left out of the request instead, so it must not block it.
                if (!('wasRequired' in input.dataset)) input.dataset.wasRequired = String(input.required);
                input.required = checkbox.checked && input.dataset.wasRequired === 'true';
            }
        };
        checkbox.addEventListener('change', apply);
        apply();
        return apply;
    }

    // Add character: HP is neither required nor sent while tracking is off.
    const form = document.getElementById('characterForm');
    const addCheckbox = document.getElementById('characterTrackHp');
    if (form && addCheckbox) {
        const apply = toggle(addCheckbox, () => [document.getElementById('characterHp')].filter(Boolean));
        form.addEventListener('reset', () => setTimeout(apply));
    }

    // Edit dialog: a Track HP checkbox before Current HP.
    if (typeof openEdit === 'function') {
        const previousOpen = openEdit;
        openEdit = function(kind, id, ...rest) {
            const result = previousOpen.call(this, kind, id, ...rest);
            if (kind !== 'characters') return result;
            const item = latest?.characters?.find(character => character.id === id);
            const editForm = document.getElementById('editForm');
            const hp = editForm?.elements?.hp;
            if (!item || !hp || editForm.elements.track_hp) return result;
            const label = document.createElement('label');
            label.className = 'sg-track-hp-field';
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.name = 'track_hp';
            checkbox.checked = window.scryingTracksHp(item);
            label.append(checkbox, document.createTextNode('Track HP'));
            hp.closest('label').before(label);
            toggle(checkbox, () => [editForm.elements.hp, editForm.elements.max_hp].filter(Boolean));
            return result;
        };
    }
})();
