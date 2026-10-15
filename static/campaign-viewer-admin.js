/* Viewer grants target an explicitly selected, authorized campaign, not live state. */
(() => {
    'use strict';
    function install() {
        const panel = document.getElementById('campaignViewerAccess');
        if (!panel) return;
        const heading = document.getElementById('campaignViewerAccessTitle');
        const list = document.getElementById('campaignViewerUsers');
        const notice = document.getElementById('campaignViewerNotice');
        const save = document.getElementById('saveCampaignViewers');
        const selector = document.getElementById('campaignSelect');
        let campaign = null, generation = 0, saving = false;

        async function api(url, options = {}) {
            const response = await fetch(url, {cache: 'no-store', ...options});
            const body = await response.json().catch(() => ({}));
            if (!response.ok) {
                throw new Error(typeof body.detail === 'string'
                    ? body.detail : `Request failed (${response.status})`);
            }
            return body;
        }

        function selectedCampaign(data) {
            const allowed = Array.isArray(data.campaigns) ? data.campaigns : [];
            const selected = String(selector?.value || '');
            return allowed.find(item => String(item.id) === selected)
                || allowed.find(item => String(item.id) === String(data.active))
                || allowed[0]
                || null;
        }

        function clear(text) {
            campaign = null;
            list.replaceChildren();
            save.disabled = true;
            heading.textContent = 'Viewer access';
            notice.textContent = text;
        }

        function setInputsDisabled(value) {
            list.querySelectorAll('input').forEach(input => {input.disabled = value;});
        }

        function draw(data) {
            campaign = {...data.campaign, id: String(data.campaign.id)};
            heading.textContent = 'Viewer access: ' + campaign.name;
            list.replaceChildren();
            for (const user of data.users) {
                const label = document.createElement('label');
                const check = document.createElement('input');
                check.type = 'checkbox';check.value = user.id;check.checked = user.granted;
                check.disabled = saving;
                label.append(check, document.createTextNode(' ' + user.username));
                label.style.display = 'block';list.append(label);
            }
            if (!data.users.length) {
                list.textContent = 'No client-role users exist. A superadmin can create them on the Users page.';
            }
            notice.textContent = '';
            save.disabled = saving;
        }

        async function refresh(force = false) {
            const request = ++generation;
            try {
                const campaigns = await api('/api/campaigns');
                if (request !== generation) return;
                const target = selectedCampaign(campaigns);
                if (!target) {
                    clear('No campaigns are assigned to your account. Ask a superadmin to assign a campaign.');
                    return;
                }
                const id = String(target.id);
                if (!force && campaign?.id === id) return;
                clear('Loading viewer access…');
                const data = await api(`/api/campaigns/${encodeURIComponent(id)}/viewers`);
                if (request !== generation) return;
                if (String(data.campaign?.id) !== id || !Array.isArray(data.users)) {
                    throw new Error('Unexpected viewer-access response; reload the campaign list.');
                }
                draw(data);
            } catch (error) {
                if (request === generation) clear(error.message);
            }
        }

        save.onclick = async () => {
            if (!campaign || saving) return;
            const target = campaign.id;
            const ids = [...list.querySelectorAll('input:checked')].map(input => input.value);
            saving = true;save.disabled = true;setInputsDisabled(true);
            notice.textContent = 'Saving viewer access…';
            try {
                await api(`/api/campaigns/${encodeURIComponent(target)}/viewers`, {
                    method: 'PUT', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({user_ids: ids}),
                });
                if (campaign?.id === target) notice.textContent = 'Viewer access saved.';
            } catch (error) {
                if (campaign?.id === target) notice.textContent = error.message;
            } finally {
                saving = false;save.disabled = !campaign;setInputsDisabled(false);
            }
        };

        const info = document.getElementById('activeCampaignInfo');
        if (info) {
            new MutationObserver(() => refresh()).observe(info, {
                childList: true, subtree: true, characterData: true,
            });
        }
        if (selector) {
            selector.addEventListener('change', () => refresh());
            new MutationObserver(() => refresh()).observe(selector, {childList: true});
        }
        panel.addEventListener('toggle', () => {if (panel.open) refresh(true);});
        refresh();
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', install, {once: true});
    } else install();
})();
