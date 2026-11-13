/* SG-TODO-009.2: reorganise existing controls; never replace their handlers. */
(() => {
    'use strict';
    if (window.scryingHeaderHierarchyInstalled) return;
    const byId = id => document.getElementById(id);
    const header = byId('adminHeader');
    const bar = byId('adminButtonBar');
    const strip = bar?.querySelector('.row');
    const start = byId('startBattle'), next = byId('nextBattle');
    const end = byId('endBattle'), reset = byId('resetAll');
    const state = byId('battleState'), round = byId('battleRound');
    const campaign = byId('activeCampaignInfo'), setup = byId('activeBattleSetupInfo');
    const fontRow = byId('battleOrderFontDecrease')?.closest('.row');
    const logout = byId('adminLogout')?.closest('form');
    if (![header, bar, strip, start, next, end, reset, state, round,
          campaign, setup, fontRow, logout].every(Boolean)) return;
    window.scryingHeaderHierarchyInstalled = true;
    const element = (tag, className, text) => {
        const node = document.createElement(tag);
        if (className) node.className = className;
        if (text) node.textContent = text;
        return node;
    };
    const context = element('div', 'sg-header-context');
    context.setAttribute('aria-label', 'Active encounter context');
    const fields = {};
    for (const [key, label] of [['campaign', 'Campaign'], ['setup', 'Setup'], ['state', 'Encounter']]) {
        const field = element('span', 'sg-context-field');
        field.append(element('span', 'sg-context-label', label + ': '));
        fields[key] = element('strong', '', 'Loading…');
        fields[key].id = 'adminContext' + key[0].toUpperCase() + key.slice(1);
        field.append(fields[key]);
        context.append(field);
    }
    const actions = element('div', 'sg-header-actions');
    actions.setAttribute('role', 'group');
    actions.setAttribute('aria-label', 'Encounter actions');
    const oldActions = start.parentElement;
    actions.append(start, next);
    const endGroup = element('span', 'sg-end-action');
    endGroup.append(end);
    actions.append(endGroup);
    const more = element('details', 'sg-header-more');
    more.id = 'adminMore';
    const summary = element('summary', '', 'More');
    const moreBody = element('div', 'sg-more-body');
    moreBody.append(element('h2', '', 'Viewer display'), fontRow, logout);
    more.append(summary, moreBody);
    actions.append(more);
    const battleSection = reset.closest('section');
    const danger = element('details', 'sg-danger-zone');
    danger.id = 'adminDangerZone';
    danger.append(element('summary', '', 'Danger zone'),
        element('p', '', 'Reset every monster and character. Review the confirmation before continuing.'), reset);
    battleSection.append(danger);
    if (!oldActions.children.length) oldActions.remove();
    for (const row of battleSection.querySelectorAll(':scope > .row')) {
        if (!row.children.length && !row.textContent.trim()) row.remove();
    }
    strip.classList.add('sg-pane-strip');
    strip.setAttribute('role', 'group');
    strip.setAttribute('aria-label', 'Panel visibility');
    strip.tabIndex = 0;
    const paneRow = element('div', 'sg-pane-row');
    paneRow.append(element('span', 'sg-context-label', 'Panels'), strip);
    bar.replaceChildren(context, actions, paneRow);
    document.body.dataset.headerHierarchy = 'ready';

    const putText = (node, value) => {
        if (node.textContent !== value) node.textContent = value;
    };
    const sourceLabel = (node, empty) => node.querySelector('strong')?.textContent.trim()
        || node.textContent.trim() || empty;
    function update() {
        const loaded = typeof latest !== 'undefined' && latest !== null;
        putText(fields.campaign, sourceLabel(campaign, 'Loading…'));
        putText(fields.setup, loaded ? sourceLabel(setup, 'Loading…') : 'Loading…');
        const active = loaded && state.classList.contains('active');
        const roundText = !round.hidden ? round.textContent.trim() : '';
        putText(fields.state, loaded ? state.textContent.trim() + (roundText ? ' · ' + roundText : '') : 'Loading…');
        fields.state.dataset.active = String(Boolean(active));
        start.classList.toggle('sg-primary-action', loaded && !active);
        next.classList.toggle('sg-primary-action', Boolean(active));
    }
    for (const source of [campaign, setup, state, round]) {
        new MutationObserver(update).observe(source, {
            childList: true, characterData: true, subtree: true,
            attributes: true, attributeFilter: ['class', 'hidden'],
        });
    }
    update();
    strip.addEventListener('focusin', event => {
        const target = event.target;
        if (!(target instanceof HTMLElement) || target === strip) return;
        const box = target.getBoundingClientRect();
        const left = strip.getBoundingClientRect().left + strip.clientLeft;
        const right = left + strip.clientWidth;
        if (box.left < left + 4) strip.scrollLeft += box.left - left - 4;
        else if (box.right > right - 4) strip.scrollLeft += box.right - right + 4;
    });
    more.addEventListener('keydown', event => {
        if (event.key === 'Escape' && more.open) {
            event.preventDefault();
            more.open = false;
            summary.focus();
        }
    });
    document.addEventListener('click', event => {
        if (more.open && !more.contains(event.target)) more.open = false;
    });
})();
