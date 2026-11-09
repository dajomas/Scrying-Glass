/* SG-TODO-009.5: workflow filtering is separate from controller-owned hidden state. */
(() => {
    'use strict';
    function install() {
        if (document.body.dataset.workflowNavigation === 'ready') return;
        const byId = id => document.getElementById(id);
        const bar = byId('adminButtonBar');
        const main = byId('adminScroll');
        const row = bar?.querySelector('.sg-pane-row');
        const battle = byId('battleInfo')?.closest('section');
        const log = byId('activityLog')?.closest('section');
        const specs = [
            ['campaign', 'Campaign'],
            ['preparation', 'Battle preparation'],
            ['live', 'Live encounter'],
        ];
        const mapping = [
            ['campaignInputPane', ['campaign']],
            ['characterInputPane', ['campaign']],
            ['battleSetupInputPane', ['preparation']],
            ['monsterInputPane', ['preparation']],
            ['characterDisplayPane', ['campaign', 'preparation', 'live']],
            ['monsterDisplayPane', ['preparation', 'live']],
            ['lairTools', ['preparation', 'live']],
            ['encounterFeatures', ['live']],
        ];
        if (!bar || !main || !row || !battle || !log ||
            mapping.some(([id]) => !byId(id))) return;
        const entries = mapping.map(([id, views]) => [byId(id), views]);
        entries.push([battle, ['campaign', 'preparation', 'live']], [log, ['live']]);
        for (const [id, views] of mapping) {
            const toggle = bar.querySelector('button[aria-controls="' + id + '"]');
            if (toggle) entries.push([toggle, views]);
        }
        const tabs = document.createElement('div');
        tabs.id = 'adminWorkflowTabs';
        tabs.className = 'sg-workflow-tabs';
        tabs.setAttribute('role', 'tablist');
        tabs.setAttribute('aria-label', 'Admin workflow');
        const buttons = specs.map(([key, label]) => {
            const button = document.createElement('button');
            button.type = 'button';
            button.id = 'adminWorkflow-' + key;
            button.textContent = label;
            button.dataset.workflow = key;
            button.setAttribute('role', 'tab');
            button.setAttribute('aria-controls', main.id);
            tabs.append(button);
            return button;
        });
        // One existing workspace; controls are never cloned, reparented or rebuilt.
        main.setAttribute('role', 'tabpanel');
        const scroll = new Map();
        let active = null;
        function select(key, focus = false) {
            if (!specs.some(([value]) => value === key)) return;
            if (active !== null && active !== key) scroll.set(active, main.scrollTop);
            const changed = active !== key;
            active = key;
            document.body.dataset.workflowView = key;
            for (const [node, views] of entries) {
                node.dataset.workflowExcluded = String(!views.includes(key));
            }
            for (const button of buttons) {
                const selected = button.dataset.workflow === key;
                button.setAttribute('aria-selected', String(selected));
                button.tabIndex = selected ? 0 : -1;
            }
            const button = buttons.find(item => item.dataset.workflow === key);
            main.setAttribute('aria-labelledby', button.id);
            if (changed) main.scrollTop = scroll.get(key) || 0;
            if (focus) {
                button.focus({preventScroll: true});
                button.scrollIntoView({block: 'nearest', inline: 'nearest'});
            }
        }
        buttons.forEach(button => button.addEventListener('click', () => select(button.dataset.workflow, true)));
        tabs.addEventListener('keydown', event => {
            const index = buttons.indexOf(event.target);
            if (index < 0 || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
            let next;
            if (event.key === 'ArrowRight') next = (index + 1) % buttons.length;
            else if (event.key === 'ArrowLeft') next = (index + buttons.length - 1) % buttons.length;
            else if (event.key === 'Home') next = 0;
            else if (event.key === 'End') next = buttons.length - 1;
            else return;
            event.preventDefault();
            select(buttons[next].dataset.workflow, true);
        });
        row.before(tabs);
        row.querySelector('.sg-context-label').textContent = 'View panels';
        document.body.dataset.workflowNavigation = 'ready';
        // Stable per-page default. Render/battle transitions never steal the chosen tab.
        select('campaign');
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', install, {once: true});
    } else install();
})();
