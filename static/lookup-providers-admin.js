/* Superadmin monster lookup provider toggles on the existing Users page. */
(() => {
    'use strict';
    const form = document.getElementById('lookupProviderForm');
    const list = document.getElementById('lookupProviderToggles');
    const notice = document.getElementById('lookupProviderNotice');
    if (!form || !list || !notice) return;
    const save = form.querySelector('button[type="submit"]');
    async function api(options = {}) {
        const response = await fetch('/api/settings/lookup-providers', {cache: 'no-store', ...options});
        const body = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(typeof body.detail === 'string' ? body.detail : `Request failed (${response.status})`);
        return body;
    }
    function render(data) {
        list.replaceChildren();
        for (const item of data.providers || []) {
            const label = document.createElement('label');
            const box = document.createElement('input');
            box.type = 'checkbox';
            box.name = item.provider;
            box.checked = item.enabled === true;
            const origin = item.saved === null || item.saved === undefined
                ? `configuration default (${item.config_key}: ${item.configured})` : 'saved setting';
            label.append(box, ` ${item.label} search — ${origin}`);
            const row = document.createElement('p');
            row.append(label);
            list.append(row);
        }
    }
    async function load() {
        notice.textContent = 'Loading provider settings…';
        try { render(await api()); notice.textContent = ''; }
        catch (error) { notice.textContent = `Provider settings unavailable: ${error.message}`; }
    }
    form.addEventListener('submit', async event => {
        event.preventDefault();
        const body = {};
        for (const box of list.querySelectorAll('input[type="checkbox"]')) body[box.name] = box.checked;
        if (!Object.keys(body).length) return;
        save.disabled = true;
        notice.textContent = 'Saving provider settings…';
        try {
            render(await api({method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)}));
            notice.textContent = 'Provider settings saved. They apply to the next monster lookup.';
        } catch (error) {
            notice.textContent = `Provider settings not saved: ${error.message}`;
        } finally { save.disabled = false; }
    });
    load();
})();
