/* Shared client for statblock import in the Admin (SG-TODO-022.13/022.14).
 * window.scryingStatblockImport: API calls with the statblock error envelope,
 * discovery, preparation jobs (submit, poll, cancel), candidate labels,
 * provider notes and previews (statblocks-render.js). All text via textContent.
 */
(() => {
    'use strict';
    const POLL_MS = 300;

    class StatblockError extends Error {
        constructor(status, body) {
            const items = Array.isArray(body?.items) ? body.items : [];
            const detail = items.map(item => item?.message).filter(Boolean);
            const message = (typeof body?.message === 'string' && body.message) ||
                (typeof body?.detail === 'string' && body.detail) || `Request failed with HTTP ${status}`;
            super(detail.length ? `${message} ${detail.join(' ')}` : message);
            this.status = status;
            this.code = body?.code || null;
            this.items = items;
            this.retryAt = body?.retry_at || null;
        }
    }

    async function api(url, options = {}) {
        const response = await fetch(url, {credentials: 'same-origin', cache: 'no-store', ...options});
        const body = await response.json().catch(() => null);
        if (!response.ok) throw new StatblockError(response.status, body);
        return body;
    }

    const json = (method, body) => ({method, headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)});
    const state = () => api('/api/statblocks/state');

    async function discover(monsterIds, species) {
        const current = await state();
        const body = {campaign_id: current.campaign_id, encounter_token: current.encounter_token, monster_ids: monsterIds};
        if (species) body.species = species;
        const result = await api('/api/statblocks/discover', json('POST', body));
        return {state: current, result};
    }

    const wait = ms => new Promise(resolve => setTimeout(resolve, ms));

    // Submit one preparation; a full queue (429) is retried until `control.cancelled`.
    async function submit(build, control) {
        for (;;) {
            if (control.cancelled) throw new StatblockError(499, {code: 'cancelled', message: 'Cancelled.'});
            try {
                return await api('/api/statblocks/prepare', build());
            } catch (error) {
                if (error.status !== 429 || error.code !== 'queue_full') throw error;
                await wait(1000);
            }
        }
    }

    async function follow(job, control) {
        control.jobId = job.job_id;
        control.onAccepted?.(job);
        while (job.status === 'queued' || job.status === 'running') {
            await wait(POLL_MS);
            if (control.cancelled) {
                await cancel(job.job_id);
                throw new StatblockError(499, {code: 'cancelled', message: 'Cancelled.'});
            }
            job = await api('/api/statblocks/jobs/' + encodeURIComponent(job.job_id));
        }
        if (job.status !== 'completed') {
            const error = new StatblockError(422, {code: job.error?.code, message: job.error?.message || 'Preparation failed.'});
            error.retryAt = job.error?.retry_at || null;
            throw error;
        }
        return job;
    }

    function prepareCandidate(context, monsterId, revision, candidateId, control = {}) {
        return submit(() => json('POST', {campaign_id: context.campaign_id, encounter_token: context.encounter_token,
            monster_id: monsterId, expected_statblock_revision: revision, candidate_id: candidateId}), control)
            .then(job => follow(job, control));
    }

    function prepareFile(context, monsterId, revision, file, control = {}) {
        return submit(() => {
            const form = new FormData();
            form.set('campaign_id', context.campaign_id);
            form.set('encounter_token', context.encounter_token);
            form.set('monster_id', monsterId);
            form.set('expected_statblock_revision', String(revision));
            form.set('file', file, file.name);
            return {method: 'POST', body: form};
        }, control).then(job => follow(job, control));
    }

    function cancel(jobId) {
        if (!jobId) return Promise.resolve(null);
        return api('/api/statblocks/jobs/' + encodeURIComponent(jobId), {method: 'DELETE'}).catch(() => null);
    }

    function candidateLabel(candidate) {
        const parts = [candidate.label, candidate.provider, candidate.source, candidate.document, candidate.game_system]
            .filter((value, index, all) => value && all.indexOf(value) === index);
        let text = parts.join(' · ');
        if (candidate.legacy) text += ' (legacy)';
        if (candidate.original) text += ' — original source';
        if (candidate.disabled) text += ' (provider disabled)';
        return text;
    }

    function providerNotes(row) {
        const notes = [];
        for (const provider of row.providers || []) {
            if (provider.status === 'partial') notes.push(`${provider.provider}: incomplete results (${provider.code || 'partial'}).`);
            else if (provider.status === 'error') notes.push(`${provider.provider}: not searched (${provider.code || 'error'}).`);
            else if (provider.status === 'cooldown') {
                notes.push(`${provider.provider}: failed recently; retry after ${time(provider.retry_at)}.`);
            }
            if (provider.omitted_versions) notes.push(`${provider.provider}: ${provider.omitted_versions} variant version(s) not offered.`);
            if (provider.omitted_unavailable) {
                notes.push(`${provider.provider}: ${provider.omitted_unavailable} result(s) without a public statblock not offered.`);
            }
        }
        if (row.status === 'no_species') notes.push('No species to search for.');
        if (row.status === 'target_changed') notes.push('The monster changed during the search; search again.');
        return notes;
    }

    function time(value) {
        const date = value ? new Date(value) : null;
        return date && !Number.isNaN(date.getTime()) ? date.toLocaleTimeString() : 'a moment';
    }

    function statusText(summary) {
        if (!summary) return 'Unknown';
        const words = {available: 'Statblock saved', partial: 'Partial statblock saved', missing: 'No statblock',
            loading: 'Loading original statblock…', unavailable: 'Original statblock unavailable',
            error: 'Original statblock failed to load'};
        return (words[summary.status] || summary.status) + (summary.statblock_revision ? ` (revision ${summary.statblock_revision})` : '');
    }

    function preview(container, job, live) {
        container.replaceChildren();
        const heading = document.createElement('p');
        heading.className = 'monster-statblock-preview-source';
        heading.textContent = `${job.source_label} — ${candidateSource(job.source)}` +
            (job.completeness === 'partial' ? ' — partial' : '');
        container.append(heading);
        if (window.ScryingStatblock && job.preview) {
            container.append(window.ScryingStatblock.render(job.preview, live || {}, {prefix: 'preview-' + job.job_id + '-'}));
        }
    }

    function candidateSource(source) {
        if (!source) return '';
        return [source.provider, source.source_code, source.edition, source.file_name].filter(Boolean).join(' · ');
    }

    function element(tag, props = {}, children = []) {
        const node = document.createElement(tag);
        for (const [key, value] of Object.entries(props)) {
            if (value === null || value === undefined || value === false) continue;
            if (key === 'text') node.textContent = value;
            else if (key === 'className') node.className = value;
            else node.setAttribute(key, value === true ? '' : String(value));
        }
        node.append(...children.filter(Boolean));
        return node;
    }

    const operationId = () => (crypto.randomUUID ? crypto.randomUUID() :
        Array.from(crypto.getRandomValues(new Uint8Array(16)), b => b.toString(16).padStart(2, '0')).join(''));

    window.scryingStatblockImport = {StatblockError, api, json, state, discover, prepareCandidate, prepareFile, cancel,
        candidateLabel, providerNotes, statusText, preview, element, operationId, time};
})();
