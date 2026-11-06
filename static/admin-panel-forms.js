/* SG-TODO-009.3: presentation only; move original nodes, never clone controls. */
(() => {
    'use strict';
    const byId = id => document.getElementById(id);
    function text(tag, value, className) {
        const node = document.createElement(tag);
        node.textContent = value;
        if (className) node.className = className;
        return node;
    }
    function group(root, title, ids) {
        const nodes = ids.map(id => root.querySelector('#' + id));
        if (nodes.some(node => !node)) return;
        const items = nodes.map(node => node.closest('label.field') || node);
        if (!items.every(node => node.parentElement === items[0].parentElement)) return;
        const fieldset = document.createElement('fieldset');
        fieldset.className = 'sg-field-group';
        const row = document.createElement('div');
        row.className = 'sg-group-row';
        items[0].before(fieldset);
        fieldset.append(text('legend', title), row);
        row.append(...items);
    }
    function disclosure(id, title, nodes) {
        if (!nodes.length || nodes.some(node => !node)) return;
        const details = document.createElement('details');
        details.id = id;
        details.className = 'sg-form-disclosure';
        // Retain immediate access to established upload/background workflows.
        details.open = true;
        const body = document.createElement('div');
        body.className = 'sg-disclosure-body';
        nodes[0].before(details);
        details.append(text('summary', title), body);
        body.append(...nodes);
    }
    function install() {
        if (document.body.dataset.panelForms === 'ready') return;
        const specs = [
            ['campaignInputPane', 'Campaign setup', 'Choose the active campaign and manage its characters, setups and access.'],
            ['characterInputPane', 'Add character', 'Add a character to the active campaign. * marks required fields.'],
            ['battleSetupInputPane', 'Battle setups', 'Create, save or load an encounter setup for the active campaign.'],
            ['monsterInputPane', 'Add monsters', 'Add monsters to the current battle setup. * marks required fields.']
        ];
        if (specs.some(([id]) => !byId(id)?.querySelector('h2'))) return;
        for (const [id, title, description] of specs) {
            const pane = byId(id);
            pane.classList.add('sg-input-panel');
            const heading = pane.querySelector('h2');
            heading.textContent = title;
            heading.id = id + 'Title';
            pane.setAttribute('aria-labelledby', heading.id);
            const intro = text('p', description, 'sg-panel-description');
            intro.id = id + 'Description';
            heading.parentElement.after(intro);
            // A button is not a labelled form field; remove blank spacer labels.
            for (const label of pane.querySelectorAll('label.field')) {
                const button = label.querySelector('button');
                if (button && !label.querySelector('input, select, textarea')) {
                    button.classList.add('sg-local-action');
                    label.replaceWith(button);
                }
            }
        }
        for (const id of ['characterForm', 'monsterForm', 'monsterUpload']) {
            const form = byId(id);
            if (!form) continue;
            form.classList.add('sg-entry-form');
            form.setAttribute('aria-describedby', form.closest('.sg-input-panel').id + 'Description');
            const submit = form.querySelector('button:not([type]), button[type="submit"]');
            if (submit) {
                const actions = document.createElement('div');
                actions.className = 'sg-form-actions';
                submit.before(actions);
                actions.append(submit);
            }
        }
        group(byId('characterForm'), 'Character details', ['characterName', 'characterColor']);
        group(byId('characterForm'), 'Starting statistics', ['characterHp', 'characterInitiative']);
        group(byId('monsterForm'), 'Monster identity', ['monsterName', 'monsterSpecies']);
        group(byId('monsterForm'), 'Combat statistics', ['monsterAc', 'monsterHpRangeStart', 'monsterHpRangeEnd', 'monsterQuantity']);
        group(byId('monsterForm'), 'Appearance', ['monsterColor', 'monsterImage']);
        group(byId('monsterUpload'), 'Import options', ['monsterFile', 'monsterFileQuantity', 'monsterFileColor', 'monsterFileImage']);
        const setup = byId('battleSetupInputPane');
        group(setup, 'Save a setup', ['setupName', 'newSetup', 'saveSetup']);
        group(setup, 'Saved setups', ['setupSelect', 'loadSetup', 'renameSetup', 'deleteSetup']);
        const savedLabel = byId('setupSelect')?.closest('label')?.querySelector('.field-label');
        if (savedLabel) savedLabel.textContent = 'Saved battle setup';
        const background = byId('backgroundColor')?.closest('.row');
        if (background && background.previousElementSibling?.querySelector('h3')) {
            background.previousElementSibling.remove();
            disclosure('sgBackgroundOptions', 'View screen background', [background, background.nextElementSibling]);
        }
        const upload = byId('monsterUpload');
        if (upload && upload.previousElementSibling?.classList.contains('monster-file-help-row')) {
            disclosure('sgMonsterFileImport', 'Import a .monster file', [upload.previousElementSibling, upload]);
        }
        for (const selector of ['#characterForm .sg-form-actions button', '#monsterForm .sg-form-actions button', '#saveSetup', '#switchCampaign']) {
            document.querySelector(selector)?.classList.add('sg-panel-primary');
        }
        for (const details of document.querySelectorAll('#campaignViewerAccess, .campaign-backups-panel')) {
            details.classList.add('sg-form-disclosure');
        }
        document.body.dataset.panelForms = 'ready';
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', install, {once: true});
    } else {
        install();
    }
})();
