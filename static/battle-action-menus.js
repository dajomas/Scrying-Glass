/* Battle Actions source and target menus with each combatant's colour marker.
 *
 * A native <select> cannot show a coloured dot per entry, so every
 * select[data-action-target] and select[data-action-source] in #battleActionRows gets a
 * select-only combobox in front of it. The native select stays the source of truth: the
 * apply code, locking, the statistics summary and the tests keep reading and setting it.
 * Choosing an entry sets its value and fires input and change; the menu follows the
 * select's value, options and disabled state. The select is hidden from view and from
 * assistive technology, so the combobox is the only control a user meets.
 */
(() => {
    'use strict';
    const rows = document.getElementById('battleActionRows');
    if (!rows || window.scryingBattleActionMenusInstalled) return;
    window.scryingBattleActionMenusInstalled = true;

    const SELECTOR = 'select[data-action-target], select[data-action-source]';
    const FALLBACK = '#ffffff';
    const menus = new Map();  // select -> menu
    let counter = 0;

    const nextId = prefix => {
        let id;
        do { id = `${prefix}-${++counter}`; } while (document.getElementById(id));
        return id;
    };
    const text = option => option.textContent.replace(/\s+/g, ' ').trim();
    const choices = select => [...select.options].filter(option => !option.disabled && option.value !== '');
    const placeholder = select => [...select.options].find(option => option.value === '');

    function colorOf(id) {
        const state = typeof latest === 'undefined' ? null : latest;
        const all = [...(Array.isArray(state?.monsters) ? state.monsters : []),
            ...(Array.isArray(state?.characters) ? state.characters : [])];
        const combatant = all.find(item => item && String(item.id) === String(id));
        return combatant ? (combatant.color || FALLBACK) : null;
    }

    function dot(color) {
        const marker = document.createElement('span');
        marker.className = 'turn-marker sg-menu-dot' + (color ? '' : ' sg-menu-dot-empty');
        marker.setAttribute('aria-hidden', 'true');
        if (color) { marker.style.background = color; marker.style.color = color; }
        return marker;
    }

    function enhance(select) {
        const name = select.hasAttribute('data-action-source') ? 'Reaction source' : 'Target';
        const trigger = document.createElement('button');
        trigger.type = 'button';
        trigger.className = 'sg-menu-trigger';
        trigger.id = nextId('sg-menu-trigger');
        trigger.setAttribute('role', 'combobox');
        trigger.setAttribute('aria-haspopup', 'listbox');
        trigger.setAttribute('aria-expanded', 'false');
        trigger.setAttribute('aria-label', name);
        const list = document.createElement('ul');
        list.className = 'sg-menu-list';
        list.id = nextId('sg-menu-list');
        list.setAttribute('role', 'listbox');
        list.setAttribute('aria-label', name);
        list.hidden = true;
        trigger.setAttribute('aria-controls', list.id);
        select.before(trigger, list);
        select.classList.add('sg-menu-native');
        select.setAttribute('aria-hidden', 'true');
        select.tabIndex = -1;
        select.closest('label')?.classList.add('sg-menu-host');

        const menu = {select, trigger, list, name, active: -1, typed: '', typedAt: 0};
        menus.set(select, menu);
        trigger.addEventListener('click', () => (list.hidden ? open(menu) : close(menu)));
        trigger.addEventListener('keydown', event => keydown(menu, event));
        trigger.addEventListener('blur', event => {
            if (!list.contains(event.relatedTarget)) close(menu);
        });
        list.addEventListener('mousedown', event => event.preventDefault());  // keep focus on the trigger
        list.addEventListener('click', event => {
            event.preventDefault();  // the list sits in the <label>: do not also activate the trigger
            const item = event.target.closest('[role="option"]');
            if (item) choose(menu, item.dataset.value);
        });
        select.addEventListener('change', () => sync(menu));
        select.addEventListener('invalid', event => invalid(menu, event));
        new MutationObserver(() => sync(menu)).observe(select, {
            attributes: true, attributeFilter: ['disabled', 'aria-describedby'], childList: true, subtree: true,
        });
        sync(menu);
    }

    function sync(menu) {
        const {select, trigger} = menu;
        const option = select.selectedOptions[0];
        const chosen = option && option.value !== '' ? option : null;
        const shown = chosen ? text(chosen) : text(placeholder(select) || {textContent: ''});
        const color = chosen ? colorOf(chosen.value) : null;
        if (menu.shown !== shown || menu.color !== color) {
            menu.shown = shown;
            menu.color = color;
            const label = document.createElement('span');
            label.className = 'sg-menu-text';
            label.textContent = shown;
            trigger.replaceChildren(dot(color), label);
        }
        trigger.classList.toggle('sg-menu-placeholder', !chosen);
        trigger.disabled = select.disabled;
        const described = select.getAttribute('aria-describedby');
        if (described) trigger.setAttribute('aria-describedby', described);
        else trigger.removeAttribute('aria-describedby');
        if (chosen) { trigger.removeAttribute('aria-invalid'); trigger.classList.remove('sg-menu-invalid'); }
        if (!menu.list.hidden) {
            if (select.disabled) close(menu);
            else fill(menu);
        }
    }

    function fill(menu) {
        const {select, list} = menu;
        const items = choices(select).map(option => {
            const item = document.createElement('li');
            item.id = `${list.id}-${option.index}`;
            item.setAttribute('role', 'option');
            item.dataset.value = option.value;
            item.setAttribute('aria-selected', String(option.selected && option.value === select.value));
            const label = document.createElement('span');
            label.textContent = text(option);
            item.append(dot(colorOf(option.value)), label);
            return item;
        });
        list.replaceChildren(...items);
        if (menu.active >= items.length) menu.active = items.length - 1;
        highlight(menu);
    }

    function highlight(menu) {
        const items = [...menu.list.children];
        items.forEach((item, index) => item.classList.toggle('sg-menu-active', index === menu.active));
        const active = items[menu.active];
        if (active) {
            menu.trigger.setAttribute('aria-activedescendant', active.id);
            active.scrollIntoView?.({block: 'nearest'});
        } else {
            menu.trigger.removeAttribute('aria-activedescendant');
        }
    }

    function open(menu) {
        if (menu.select.disabled) return;
        for (const other of menus.values()) if (other !== menu) close(other);
        const current = choices(menu.select).findIndex(option => option.value === menu.select.value);
        menu.active = current >= 0 ? current : 0;
        menu.list.hidden = false;
        menu.trigger.setAttribute('aria-expanded', 'true');
        fill(menu);
    }

    function close(menu) {
        if (menu.list.hidden) return;
        menu.list.hidden = true;
        menu.trigger.setAttribute('aria-expanded', 'false');
        menu.trigger.removeAttribute('aria-activedescendant');
        menu.list.replaceChildren();
    }

    function choose(menu, value) {
        const {select} = menu;
        close(menu);
        menu.trigger.focus();
        if (select.value === value) return;
        select.value = value;
        select.dispatchEvent(new Event('input', {bubbles: true}));
        select.dispatchEvent(new Event('change', {bubbles: true}));
        sync(menu);
    }

    function keydown(menu, event) {
        const {list} = menu;
        const count = choices(menu.select).length;
        const move = index => { menu.active = Math.max(0, Math.min(count - 1, index)); highlight(menu); };
        if (list.hidden) {
            if (['ArrowDown', 'ArrowUp', 'Enter', ' '].includes(event.key)) {
                event.preventDefault();
                open(menu);
            } else if (event.key.length === 1 && !event.ctrlKey && !event.metaKey && !event.altKey) {
                open(menu);
                typeahead(menu, event);
            }
            return;
        }
        switch (event.key) {
        case 'ArrowDown': event.preventDefault(); move(menu.active + 1); break;
        case 'ArrowUp': event.preventDefault(); move(menu.active - 1); break;
        case 'Home': case 'PageUp': event.preventDefault(); move(0); break;
        case 'End': case 'PageDown': event.preventDefault(); move(count - 1); break;
        case 'Enter': case ' ': {
            event.preventDefault();
            const item = list.children[menu.active];
            if (item) choose(menu, item.dataset.value); else close(menu);
            break;
        }
        case 'Escape':
            // Close only the menu, not the Battle Actions window.
            event.preventDefault();
            event.stopPropagation();
            close(menu);
            break;
        case 'Tab': close(menu); break;
        default:
            if (event.key.length === 1 && !event.ctrlKey && !event.metaKey && !event.altKey) typeahead(menu, event);
        }
    }

    function typeahead(menu, event) {
        event.preventDefault();
        const now = Date.now();
        menu.typed = (now - menu.typedAt < 700 ? menu.typed : '') + event.key.toLowerCase();
        menu.typedAt = now;
        const names = [...menu.list.children].map(item => item.textContent.trim().toLowerCase());
        const start = menu.typed.length === 1 ? menu.active + 1 : menu.active;
        for (let step = 0; step < names.length; step++) {
            const index = (start + step) % names.length;
            if (names[index].startsWith(menu.typed)) { menu.active = index; highlight(menu); return; }
        }
    }

    let focusPending = false;
    function invalid(menu, event) {
        // The native bubble would point at the hidden select: mark the menu instead.
        event.preventDefault();
        menu.trigger.setAttribute('aria-invalid', 'true');
        menu.trigger.classList.add('sg-menu-invalid');
        if (focusPending) return;
        focusPending = true;
        queueMicrotask(() => {
            focusPending = false;
            const first = [...menus.values()].find(item => item.trigger.isConnected &&
                item.trigger.getAttribute('aria-invalid') === 'true');
            if (!first) return;
            first.trigger.focus();
            const notice = document.getElementById('battleActionNotice');
            if (notice) notice.textContent = `Choose a ${first.name.toLowerCase()} for every row.`;
        });
    }

    function scan() {
        for (const select of menus.keys()) if (!select.isConnected) menus.delete(select);
        for (const select of rows.querySelectorAll(SELECTOR)) {
            if (!menus.has(select)) enhance(select);
        }
    }

    new MutationObserver(scan).observe(rows, {childList: true, subtree: true});
    document.addEventListener('pointerdown', event => {
        for (const menu of menus.values()) {
            if (!menu.list.hidden && !menu.trigger.contains(event.target) && !menu.list.contains(event.target)) close(menu);
        }
    });
    // Colours and names can change with every state refresh.
    const previous = window.scryingLairsRender;
    window.scryingLairsRender = function () {
        const result = typeof previous === 'function' ? previous.apply(this, arguments) : undefined;
        for (const menu of menus.values()) sync(menu);
        return result;
    };
    scan();
})();
