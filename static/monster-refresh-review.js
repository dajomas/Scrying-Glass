/* One selected-monster review; only explicit Apply changes live state. */
(() => {
    'use strict';
    const bulk = document.querySelector('#monsterBulkAction');
    const roster = document.querySelector('#monsters');
    if (!bulk || !roster || typeof createRefreshSelection !== 'function') return;
    const fields = ['initiative_bonus', 'ac', 'max_hp', 'hp'];
    const labels = {initiative_bonus: 'Initiative bonus', ac: 'Armor Class', max_hp: 'Max HP', hp: 'Current HP'};
    const option = document.createElement('option');
    option.value = 'refresh-source-review';
    option.textContent = 'Refresh from source';
    bulk.append(option);
    let opened = false;
    let reviewFeedbackRoot = null;
    function rosterReady() {
        return typeof latest !== 'undefined' && Array.isArray(latest?.monsters);
    }
    function syncOption() {
        option.disabled = opened || !rosterReady() || selectedIds('monsters').length === 0;
    }
    for (const name of ['updateRowSelection', 'setAllSelected']) {
        // These bindings are declared by the assembled Admin script.
        if (name === 'updateRowSelection') {
            const original = updateRowSelection;
            updateRowSelection = function(...args) {const value = original(...args); syncOption(); return value;};
        } else {
            const original = setAllSelected;
            setAllSelected = function(...args) {const value = original(...args); syncOption(); return value;};
        }
    }
    new MutationObserver(syncOption).observe(roster, {childList: true, subtree: true});
    const originalBulk = runBulkAction;
    runBulkAction = async function(kind, action) {
        if (kind !== 'monsters' || action !== option.value) return originalBulk(kind, action);
        if (!rosterReady() || opened) return;
        const ids = selectedIds('monsters');
        if (!ids.length) return;
        await openReview([...ids]);
    };
    syncOption();

    async function openReview(ids) {
        opened = true;
        syncOption();
        const previousFocus = document.activeElement;
        const names = new Map((latest?.monsters || []).map(item => [item.id, item.name || item.id]));
        const dialog = document.createElement('dialog');
        dialog.className = 'sg-refresh-review';
        dialog.setAttribute('aria-labelledby', 'sgRefreshTitle');
        const title = document.createElement('h2');
        title.id = 'sgRefreshTitle';
        title.textContent = 'Refresh selected monsters from source';
        const help = document.createElement('p');
        help.textContent = 'Only the originally selected monsters are reviewed. Nothing changes until Apply. ' +
            'Current HP starts unchecked; row or column selection can explicitly select it. ' +
            'HP formulas are rolled once per monster only on Apply; HP and Max HP share that value when both are selected.';
        const status = document.createElement('p');
        status.setAttribute('role', 'status');
        status.setAttribute('aria-live', 'polite');
        const content = document.createElement('div');
        const actions = document.createElement('div');
        actions.className = 'sg-refresh-actions';
        const apply = button('Apply selected changes');
        const restart = button('Reload review');
        const cancel = button('Cancel');
        actions.append(apply, restart, cancel);
        dialog.append(title, help, status, content, actions);
        document.body.append(dialog);
        let review = null;
        let selection = null;
        let busy = false;
        let closed = false;
        let controls = [];
        const choices = Object.create(null);
        const feedback = window.scryingAdminFeedback;
        if (!reviewFeedbackRoot) {
            reviewFeedbackRoot = document.createElement('div');
            reviewFeedbackRoot.id = 'sgMonsterRefreshFeedback';
            status.after(reviewFeedbackRoot);
            feedback.mount('monsterRefreshReview', reviewFeedbackRoot.id);
        } else status.after(reviewFeedbackRoot);
        const reviewTarget = JSON.stringify([...ids].map(String).sort());
        const sessionTicket = feedback.begin({region: 'monsters', operation: 'monster.refresh.session',
            target: 'review-dialog', label: 'Source review session'});
        const previewSpec = {region: 'monsterRefreshReview', operation: 'monster.refresh.preview',
            target: reviewTarget, label: 'Load source review'};
        const applySpec = {...previewSpec, operation: 'monster.refresh.apply', label: 'Apply source changes'};
        const refreshSpec = {...applySpec, region: 'monsters', operation: 'monster.refresh.apply.refresh', label: 'Refresh applied source changes'};
        function currentReview() { return !closed && feedback.isCurrent(sessionTicket); }
        function staleReview() {
            review = null;
            status.textContent = 'The encounter changed. Close and reopen source review before continuing.';
            if (!closed) update();
        }
        function button(text) {
            const node = document.createElement('button');
            node.type = 'button'; node.textContent = text;
            return node;
        }
        function close(preserveApply = false) {
            if (busy || closed) return;
            if (feedback.isCurrent(sessionTicket)) {
                feedback.resolve(feedback.begin(previewSpec));
                if (preserveApply !== true) feedback.resolve(feedback.begin(applySpec));
                feedback.resolve(sessionTicket);
            }
            closed = true;
            dialog.close(); dialog.remove();
            opened = false; syncOption(); previousFocus?.focus();
        }
        cancel.addEventListener('click', close);
        dialog.addEventListener('cancel', event => {event.preventDefault(); close();});
        function update() {
            const unavailable = busy || !review || !currentReview();
            for (const control of controls) {
                if (control.axis) {
                    const state = selection.state(control.axis, control.key);
                    control.node.checked = state.checked;
                    control.node.indeterminate = state.indeterminate;
                    control.node.disabled = unavailable || state.disabled;
                    control.node.setAttribute('aria-checked', state.indeterminate ? 'mixed' : String(state.checked));
                } else {
                    control.node.checked = (selection.payload()[control.id] || []).includes(control.field);
                    control.node.disabled = unavailable || !control.enabled;
                }
            }
            content.querySelectorAll('button, select').forEach(node => {node.disabled = unavailable;});
            apply.disabled = busy || !review || !selection || !Object.keys(selection.payload()).length;
            restart.disabled = busy;
            cancel.disabled = busy;
            dialog.setAttribute('aria-busy', String(busy));
        }
        function checkbox(label, metadata, onChange) {
            const box = document.createElement('input');
            box.type = 'checkbox'; box.setAttribute('aria-label', label);
            box.addEventListener('change', () => {onChange(box); update();});
            controls.push({node: box, ...metadata});
            return box;
        }
        function render(result, retained = {}) {
            review = result;
            const rows = result.rows || [];
            selection = createRefreshSelection(rows.map(row => ({id: row.id, offer: Object.fromEntries(
                fields.filter(field => row.fields?.[field]?.enabled === true && row.fields[field].status === 'available')
                    .map(field => [field, row.fields[field].proposed]))})));
            for (const row of rows) for (const field of retained[row.id] || []) {
                if (row.fields?.[field]?.enabled && row.fields[field].status === 'available') selection.set(row.id, field, true);
            }
            controls = [];
            content.replaceChildren();
            const table = document.createElement('table');
            const caption = document.createElement('caption');
            caption.textContent = 'Source review for originally selected monsters';
            table.append(caption);
            const head = document.createElement('thead');
            const headings = document.createElement('tr');
            for (const text of ['Monster / select row', 'Source / status']) {
                const th = document.createElement('th'); th.scope = 'col'; th.textContent = text; headings.append(th);
            }
            for (const field of fields) {
                const th = document.createElement('th'); th.scope = 'col';
                const label = document.createElement('label');
                label.append(checkbox(`Select column ${labels[field]}`, {axis: 'column', key: field},
                    () => selection.toggle('column', field)), document.createTextNode(labels[field]));
                th.append(label); headings.append(th);
            }
            head.append(headings); table.append(head);
            const body = document.createElement('tbody');
            for (const row of rows) {
                const tr = document.createElement('tr'); tr.dataset.refreshId = row.id;
                const name = names.get(row.id) || row.id;
                const rowHead = document.createElement('th'); rowHead.scope = 'row';
                const rowLabel = document.createElement('label');
                rowLabel.append(checkbox(`Select row ${name}`, {axis: 'row', key: row.id},
                    () => selection.toggle('row', row.id)), document.createTextNode(name));
                rowHead.append(rowLabel); tr.append(rowHead);
                const source = document.createElement('td');
                source.textContent = `${row.source_fields?.monster_source_provider || 'Source not selected'} — ${row.status}`;
                if (row.source_fields?.monster_source_url?.startsWith('https://')) {
                    const link = document.createElement('a'); link.href = row.source_fields.monster_source_url;
                    link.target = '_blank'; link.rel = 'noopener noreferrer'; link.textContent = ' View source'; source.append(link);
                }
                if (row.reason) {const reason = document.createElement('p'); reason.textContent = row.reason; source.append(reason);}
                if (row.candidates?.length) {
                    const label = document.createElement('label'); label.textContent = `Source candidate for ${name}`;
                    const select = document.createElement('select');
                    select.setAttribute('aria-label', `Source candidate for ${name}`);
                    const placeholder = document.createElement('option'); placeholder.value = ''; placeholder.textContent = 'Choose candidate'; select.append(placeholder);
                    row.candidates.forEach((candidate, index) => {
                        const entry = document.createElement('option'); entry.value = String(index);
                        entry.textContent = `${candidate.name || candidate.species} — ${monsterSourceLabel(candidate, true)}`;
                        select.append(entry);
                    });
                    label.append(select); source.append(label);
                    const resolve = button(`Use candidate for ${name}`);
                    resolve.addEventListener('click', () => {
                        if (busy || !review || !currentReview()) {
                            if (!currentReview()) staleReview();
                            return;
                        }
                        if (select.value === '') return;
                        const candidate = row.candidates[Number(select.value)];
                        fetchReview({review_id: review.review_id, choices: {[row.id]: candidate.selection_token}},
                            {[row.id]: candidate.selection_token});
                    });
                    source.append(resolve);
                }
                tr.append(source);
                for (const field of fields) {
                    const td = document.createElement('td');
                    const proposal = row.fields?.[field] || {status: 'unavailable', enabled: false};
                    const label = document.createElement('label');
                    label.append(checkbox(`${labels[field]} for ${name}`, {id: row.id, field, enabled: proposal.enabled === true && proposal.status === 'available'},
                        box => selection.set(row.id, field, box.checked)));
                    const text = document.createElement('span');
                    text.textContent = `${labels[field]}: ${proposal.current ?? '—'} → ` +
                        (proposal.enabled ? `${proposal.proposed} (${proposal.format || 'value'})` : proposal.status);
                    label.append(text); td.append(label);
                    if (proposal.reason) {const reason = document.createElement('small'); reason.textContent = proposal.reason; td.append(reason);}
                    tr.append(td);
                }
                body.append(tr);
            }
            table.append(body); content.append(table);
            update();
        }
        async function fetchReview(payload, addedChoices = {}) {
            if (busy || closed) return;
            if (!currentReview()) {staleReview(); return;}
            const retained = selection?.payload() || {};
            const ticket = feedback.begin(previewSpec);
            busy = true; status.textContent = 'Resolving selected sources…'; update();
            try {
                const result = await request('/api/monsters/refresh/preview', {
                    method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)});
                if (!currentReview() || !feedback.isCurrent(ticket)) {staleReview(); return;}
                Object.assign(choices, addedChoices);
                render(result, retained);
                feedback.resolve(ticket);
                status.textContent = 'Review ready. Choose fields, then Apply selected changes.';
            } catch (error) {
                review = null;
                if (currentReview()) {
                    status.textContent = '';
                    feedback.publish(ticket, {severity: 'error', text: `${error.message} Reload review before applying.`});
                } else staleReview();
            } finally {busy = false; if (!closed) update();}
        }
        restart.addEventListener('click', () => fetchReview({ids, choices}));
        apply.addEventListener('click', async () => {
            if (busy || !review || closed) return;
            if (!currentReview()) {staleReview(); return;}
            const ticket = feedback.begin(applySpec);
            const refresh = feedback.begin(refreshSpec);
            busy = true; update();
            try {
                await request('/api/monsters/refresh/apply', {method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({review_id: review.review_id, selected: selection.payload()})});
            } catch (error) {
                review = null;
                if (currentReview()) {
                    status.textContent = '';
                    feedback.publish(ticket, {severity: 'error', text: `${error.message} Reload review before retrying.`});
                } else staleReview();
                busy = false; update(); return;
            }
            if (!currentReview() || !feedback.isCurrent(ticket)) {
                busy = false; staleReview(); return;
            }
            feedback.resolve(ticket);
            feedback.publish(feedback.begin({...applySpec, region: 'monsters'}),
                {severity: 'success', text: 'Selected source changes applied.'});
            busy = false; close(true);
            try {await load(true); feedback.resolve(refresh);}
            catch {feedback.publish(refresh, {severity: 'error', text:
                'Changes applied, but display reload failed. Reload the page; do not apply again.'});}
        });
        dialog.showModal();
        await fetchReview({ids});
    }
})();
