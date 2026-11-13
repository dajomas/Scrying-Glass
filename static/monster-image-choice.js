/* SG-TODO-017 follow-up: choose a monster image from the other found candidates. */
(() => {
    'use strict';
    function hasImage(candidate) {
        return typeof candidate?.image_url === 'string' && candidate.image_url.startsWith('https://');
    }
    function open(candidate, candidates, labelFor) {
        const others = [];
        const seen = new Set(hasImage(candidate) ? [candidate.image_url] : []);
        for (const other of candidates) {
            if (other !== candidate && hasImage(other) && !seen.has(other.image_url)) {
                seen.add(other.image_url);
                others.push(other);
            }
        }
        if (!others.length) return {promise: Promise.resolve(candidate), cancel: () => {}};
        let cancel = () => {};
        const promise = new Promise(resolve => {
            const previousFocus = document.activeElement;
            const dialog = document.createElement('dialog');
            dialog.setAttribute('aria-label', 'Select monster image');
            dialog.className = 'monster-image-choice';
            dialog.style.maxWidth = 'min(48rem, 90vw)';
            const heading = document.createElement('h2');
            heading.textContent = 'Select monster image';
            const intro = document.createElement('p');
            intro.textContent = hasImage(candidate)
                ? 'The selected monster has an image. Keep it or choose an image from another found monster.'
                : 'The selected monster has no image. Choose an image from another found monster, or cancel to keep none.';
            const grid = document.createElement('div');
            grid.style.cssText = 'display:flex;flex-wrap:wrap;gap:.75rem;margin:.75rem 0;';
            let finished = false;
            function finish(choice) {
                if (finished) return;
                finished = true;
                dialog.close();
                dialog.remove();
                previousFocus?.focus();
                resolve(choice);
            }
            const tiles = hasImage(candidate) ? [[candidate, 'Selected monster']] : [];
            for (const other of others) tiles.push([other, labelFor(other)]);
            for (const [owner, caption] of tiles) {
                const tile = document.createElement('button');
                tile.type = 'button';
                tile.className = 'monster-image-option';
                tile.style.cssText = 'display:grid;gap:.25rem;justify-items:center;width:10rem;padding:.4rem;';
                const thumb = document.createElement('img');
                thumb.src = owner.image_url;
                thumb.alt = '';
                thumb.loading = 'lazy';
                thumb.referrerPolicy = 'no-referrer';
                thumb.style.cssText = 'width:8rem;height:8rem;object-fit:contain;';
                const label = document.createElement('span');
                label.textContent = caption;
                label.style.fontSize = '.8rem';
                tile.setAttribute('aria-label', `Use image: ${caption}`);
                tile.append(thumb, label);
                tile.addEventListener('click', () => finish(owner));
                grid.append(tile);
            }
            const cancelButton = document.createElement('button');
            cancelButton.type = 'button';
            cancelButton.textContent = 'Cancel';
            cancelButton.title = hasImage(candidate) ? 'Keep the selected monster image' : 'Keep no image';
            cancelButton.addEventListener('click', () => finish(candidate));
            dialog.addEventListener('cancel', event => {event.preventDefault(); finish(candidate);});
            dialog.append(heading, intro, grid, cancelButton);
            document.body.append(dialog);
            cancel = () => finish(null);
            dialog.showModal();
        });
        return {promise, cancel: () => cancel()};
    }
    window.scryingMonsterImageChoice = {open};
})();
