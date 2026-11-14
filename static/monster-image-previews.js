/* SG-TODO-011: previews do not alter image inputs, tokens or submissions. */
(() => {
    'use strict';
    function install() {
    if (document.body.dataset.monsterImagePreviews === 'ready') return;
    let candidate = null;
    const previews = [];
    function safeRemote(value) {
        try {
            const url = new URL(value);
            return url.protocol === 'https:' && !url.username && !url.password ? url.href : '';
        } catch { return ''; }
    }
    function attach(id, allowProvider) {
        const input = document.getElementById(id);
        const label = input?.closest('label.field');
        if (!input || !label) return;
        const wrap = document.createElement('div');
        wrap.className = 'sg-image-field';
        label.before(wrap);
        const preview = document.createElement('figure');
        preview.className = 'sg-image-preview';
        preview.id = id + 'Preview';
        preview.setAttribute('aria-label', allowProvider ? 'Monster image preview' : 'Replacement image preview');
        const status = document.createElement('figcaption');
        status.setAttribute('aria-live', 'polite');
        wrap.append(label, preview);
        let localFile = null, objectUrl = '', sourceKey = null, image = null;
        function release() {
            if (objectUrl) URL.revokeObjectURL(objectUrl);
            objectUrl = '';
            localFile = null;
        }
        function render() {
            const file = input.files?.[0] || null;
            if (file !== localFile) release();
            let src = '', description = '';
            if (file) {
                if (!objectUrl) {
                    try {
                        objectUrl = URL.createObjectURL(file);
                        localFile = file;
                    } catch { /* Leave submission intact when preview creation fails. */ }
                }
                src = objectUrl;
                description = 'Selected file: ' + file.name;
            } else if (allowProvider && candidate) {
                src = safeRemote(candidate.image_url);
                description = candidate.provider + ' image for ' + candidate.species;
            }
            const key = src + '\n' + description;
            if (key === sourceKey) return;
            sourceKey = key;
            if (image) { image.onload = null; image.onerror = null; }
            image = null;
            preview.replaceChildren(status);
            if (!src) {
                status.textContent = file ? 'Image preview unavailable. The selected file is unchanged.' :
                    allowProvider && candidate ? 'No image available for this result.' : 'No image selected.';
                return;
            }
            const next = document.createElement('img');
            image = next;
            next.alt = description;
            next.referrerPolicy = 'no-referrer';
            status.textContent = 'Loading preview: ' + description;
            next.onload = () => {
                if (image === next) status.textContent = description;
            };
            next.onerror = () => {
                if (image !== next) return;
                next.hidden = true;
                status.textContent = 'Image preview unavailable. The image selection is unchanged.';
            };
            preview.prepend(next);
            next.src = src;
        }
        input.addEventListener('change', render);
        input.form?.addEventListener('reset', event => queueMicrotask(() => {
            if (!event.defaultPrevented) { release(); sourceKey = null; render(); }
        }));
        previews.push({render, release});
        render();
    }
    document.addEventListener('scrying:monster-selection', event => {
        candidate = event.detail || null;
        previews.forEach(preview => preview.render());
    });
    attach('monsterImage', true);
    attach('monsterFileImage', false);
    window.addEventListener('pagehide', () => previews.forEach(preview => preview.release()));
    window.addEventListener('pageshow', () => previews.forEach(preview => preview.render()));
    document.body.dataset.monsterImagePreviews = 'ready';
    }
    if (document.readyState === 'loading' ||
        (document.readyState === 'interactive' && document.currentScript?.defer)) {
        document.addEventListener('DOMContentLoaded', install, {once: true});
    } else {
        install();
    }
})();
