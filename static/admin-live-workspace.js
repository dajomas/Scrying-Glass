/* SG-TODO-009.6 revision: full-width main page and on-demand Encounter tools. */
(() => {
    'use strict';
    function install() {
        if (document.body.dataset.liveWorkspace === 'ready') return;
        const byId = id => document.getElementById(id);
        const main = byId('adminScroll'), pane = byId('encounterFeatures');
        const opener = byId('toggleEncounterTools');
        const log = byId('activityLog')?.closest('section');
        if (!main || !pane || !opener || !log) return;
        const make = (tag, text) => {
            const node = document.createElement(tag);
            if (text !== undefined) node.textContent = text;
            return node;
        };
        // No split grid, duplicate participant list or roster/battle reparenting.
        const modal = make('div'); modal.id = 'encounterToolsModal';
        modal.className = 'modal'; modal.hidden = true;
        modal.setAttribute('role', 'dialog'); modal.setAttribute('aria-modal', 'true');
        modal.setAttribute('aria-labelledby', 'encounterToolsTitle');
        const content = make('div'); content.className = 'sg-tools-dialog'; content.tabIndex = -1;
        const bar = make('div'); bar.className = 'sg-tools-dialog-bar';
        const closeButton = make('button', 'Close encounter tools'); closeButton.type = 'button';
        closeButton.id = 'closeEncounterTools';
        const notice = make('p'); notice.id = 'encounterToolsDialogNotice';
        notice.setAttribute('role', 'status'); notice.setAttribute('aria-live', 'polite');
        bar.append(closeButton); content.append(bar, notice, pane); modal.append(content);
        document.body.append(modal);
        pane.hidden = false; pane.dataset.etVisible = 'true';
        opener.textContent = 'Encounter tools';
        opener.setAttribute('aria-controls', modal.id);
        opener.setAttribute('aria-haspopup', 'dialog'); opener.setAttribute('aria-expanded', 'false');
        const history = make('details'); history.id = 'liveActivityDisclosure';
        history.className = 'sg-live-history'; history.open = true;
        history.append(make('summary', 'Activity log'));
        while (log.firstChild) history.append(log.firstChild);
        log.append(history);
        const backgrounds = new Map();
        let returnFocus = opener;
        const nested = () => [...document.querySelectorAll('.modal:not([hidden]), dialog[open]')]
            .some(n => n !== modal && n.getClientRects().length > 0);
        const focusables = () => [...content.querySelectorAll(
            'button,input,select,textarea,a[href],[tabindex]')].filter(n =>
                !n.disabled && n.tabIndex >= 0 && n.getClientRects().length > 0 && !n.closest('[inert]'));
        const focusFirst = () => (focusables()[0] || content).focus({preventScroll: true});
        function close() {
            if (modal.hidden) return true;
            if (nested()) return false;
            if (window.scryingEncounterToolsBusy?.()) {
                notice.textContent = 'An encounter-tools operation is still running. Wait before closing.';
                return false;
            }
            modal.hidden = true; opener.setAttribute('aria-expanded', 'false');
            delete document.body.dataset.encounterToolsOpen;
            for (const [node, inert] of backgrounds) node.inert = inert;
            backgrounds.clear(); notice.textContent = '';
            const target = returnFocus?.isConnected && returnFocus.getClientRects().length
                ? returnFocus : document.querySelector('#adminWorkflowTabs [aria-selected="true"]');
            target?.focus({preventScroll: true});
            return true;
        }
        function open() {
            if (!modal.hidden) { focusFirst(); return; }
            if (pane.dataset.workflowExcluded === 'true' || nested()) return;
            returnFocus = document.activeElement;
            for (const node of document.body.children) {
                if (node === modal || node.matches('.modal,dialog,script,style,link')) continue;
                backgrounds.set(node, node.inert); node.inert = true;
            }
            modal.hidden = false; document.body.dataset.encounterToolsOpen = 'true';
            opener.setAttribute('aria-expanded', 'true'); notice.textContent = ''; focusFirst();
        }
        window.scryingOpenEncounterTools = open;
        window.scryingCloseEncounterTools = close;
        closeButton.addEventListener('click', close);
        document.addEventListener('keydown', event => {
            if (modal.hidden || nested()) return;
            if (event.key === 'Escape') {
                event.preventDefault(); event.stopImmediatePropagation(); close();
            } else if (event.key === 'Tab') {
                const nodes = focusables(), first = nodes[0], last = nodes[nodes.length - 1];
                if (!first) { event.preventDefault(); content.focus(); }
                else if (event.shiftKey && (document.activeElement === first || !content.contains(document.activeElement))) {
                    event.preventDefault(); last.focus();
                } else if (!event.shiftKey && (document.activeElement === last || !content.contains(document.activeElement))) {
                    event.preventDefault(); first.focus();
                }
            }
        }, true);
        document.addEventListener('focusin', event => {
            if (!modal.hidden && !nested() && !content.contains(event.target)) focusFirst();
        });
        document.body.dataset.liveWorkspace = 'ready';
    }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', install, {once: true});
    else install();
})();
