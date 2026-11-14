/* SG-TODO-009.7 Stage 4: dialog semantics and keyboard containment for the
 * legacy Admin overlays (.modal). The Encounter tools dialog keeps its own
 * owner in admin-live-workspace.js; this layer never opens, closes or rebuilds
 * a dialog's controls, and it only acts for the topmost open overlay. */
(() => {
    'use strict';
    if (window.scryingDialogAccessibilityInstalled) return;
    window.scryingDialogAccessibilityInstalled = true;
    const OWNED_ELSEWHERE = new Set(['encounterToolsModal']);
    // Escape for overlays that no earlier owner closes; mirrors their Cancel/Close button.
    const ESCAPE_BUTTONS = {lairActionModal: 'cancelLairAction', tieModal: 'cancelOrder',
        battleActionModal: 'closeBattleActions'};
    const FOCUSABLE = 'a[href], button, input, select, textarea, summary, [tabindex]';
    const stack = [], openers = new Map();
    // Last control used outside every overlay: an opener may move focus into its
    // dialog before the hidden-attribute observer runs, so record it beforehand.
    let lastOutside = null;
    const outside = node => node instanceof Element && node !== document.body && !node.closest('.modal');
    const remember = event => { if (outside(event.target)) lastOutside = event.target; };
    const visible = node => node && node.isConnected && node.getClientRects().length > 0;
    const dialogOf = modal => modal.getAttribute('role') === 'dialog' ? modal
        : modal.querySelector('[role="dialog"]') || modal.firstElementChild;
    const focusables = dialog => [...dialog.querySelectorAll(FOCUSABLE)].filter(node =>
        !node.disabled && node.tabIndex >= 0 && !node.closest('[hidden],[inert]') && visible(node));

    function describe(modal) {
        const dialog = dialogOf(modal);
        if (!dialog) return;
        if (dialog.getAttribute('role') !== 'dialog') dialog.setAttribute('role', 'dialog');
        if (!dialog.hasAttribute('aria-modal')) dialog.setAttribute('aria-modal', 'true');
        if (!dialog.hasAttribute('aria-labelledby') && !dialog.hasAttribute('aria-label')) {
            const heading = dialog.querySelector('h1, h2, h3');
            if (heading) {
                if (!heading.id) heading.id = modal.id + 'Title';
                dialog.setAttribute('aria-labelledby', heading.id);
            }
        }
        if (!dialog.hasAttribute('tabindex')) dialog.tabIndex = -1;
    }

    function opened(modal) {
        if (!stack.includes(modal)) stack.push(modal);
        if (OWNED_ELSEWHERE.has(modal.id)) return;
        const dialog = dialogOf(modal), active = document.activeElement;
        if (active && active !== document.body && !modal.contains(active)) openers.set(modal, active);
        else if (lastOutside && lastOutside.isConnected) openers.set(modal, lastOutside);
        // Openers that already placed focus (for example a first field) keep it.
        if (dialog && !dialog.contains(document.activeElement)) {
            (focusables(dialog)[0] || dialog).focus({preventScroll: true});
        }
    }

    function closed(modal) {
        const index = stack.indexOf(modal);
        if (index >= 0) stack.splice(index, 1);
        const opener = openers.get(modal);
        openers.delete(modal);
        if (OWNED_ELSEWHERE.has(modal.id)) return;
        const active = document.activeElement;
        // Return focus only when it was lost with the overlay, never steal it elsewhere.
        const lost = !active || active === document.body || modal.contains(active);
        if (lost && opener && visible(opener) && !opener.disabled) opener.focus({preventScroll: true});
    }

    const topmost = () => {
        for (let index = stack.length - 1; index >= 0; index--) {
            if (!stack[index].hidden) return stack[index];
            stack.splice(index, 1);
        }
        return null;
    };

    function install() {
        document.addEventListener('focusin', remember, true);
        // Some browsers do not focus a clicked button; the click still names the opener.
        document.addEventListener('pointerdown', event => {
            const control = event.target instanceof Element && event.target.closest(FOCUSABLE);
            if (control && outside(control)) lastOutside = control;
        }, true);
        const modals = [...document.querySelectorAll('.modal')];
        const observer = new MutationObserver(records => {
            for (const record of records) {
                const modal = record.target;
                if (modal.hidden) closed(modal); else opened(modal);
            }
        });
        for (const modal of modals) {
            if (!OWNED_ELSEWHERE.has(modal.id)) describe(modal);
            if (!modal.hidden) stack.push(modal);
            observer.observe(modal, {attributes: true, attributeFilter: ['hidden']});
        }
        document.addEventListener('keydown', event => {
            const modal = topmost();
            if (!modal || OWNED_ELSEWHERE.has(modal.id)) return;
            if (event.key === 'Escape' && ESCAPE_BUTTONS[modal.id]) {
                const button = document.getElementById(ESCAPE_BUTTONS[modal.id]);
                if (button && !button.disabled) { event.preventDefault(); button.click(); }
                return;
            }
            if (event.key !== 'Tab') return;
            const dialog = dialogOf(modal), nodes = focusables(dialog);
            const first = nodes[0], last = nodes[nodes.length - 1], active = document.activeElement;
            if (!first) { event.preventDefault(); dialog.focus(); return; }
            if (!dialog.contains(active)) { event.preventDefault(); first.focus(); return; }
            if (event.shiftKey && (active === first || active === dialog)) { event.preventDefault(); last.focus(); }
            else if (!event.shiftKey && active === last) { event.preventDefault(); first.focus(); }
        });
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', install, {once: true});
    else install();
})();
