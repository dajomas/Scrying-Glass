/* SG-TODO-009.6: presentation only; native sections and controllers retain ownership. */
(() => {
    'use strict';
    function install() {
        if (document.body.dataset.liveWorkspace === 'ready') return;
        const byId = id => document.getElementById(id);
        const main = byId('adminScroll');
        const battle = byId('battleInfo')?.closest('section');
        const tools = byId('encounterFeatures');
        const characters = byId('characterDisplayPane'), monsters = byId('monsterDisplayPane');
        const lair = byId('lairTools'), log = byId('activityLog')?.closest('section');
        if (![main, battle, tools, characters, monsters, lair, log].every(Boolean)) return;
        const make = (tag, className, text) => {
            const n = document.createElement(tag);
            if (className) n.className = className;
            if (text !== undefined) n.textContent = text;
            return n;
        };
        const workspace = make('div', 'sg-live-workspace');
        workspace.id = 'liveEncounterWorkspace'; workspace.hidden = true;
        const primary = make('div', 'sg-live-primary');
        const side = make('aside', 'sg-live-tools');
        side.setAttribute('aria-label', 'Encounter and lair tools');
        const overview = make('section', 'sg-live-overview');
        overview.setAttribute('aria-labelledby', 'liveTurnTitle');
        const title = make('h2', '', 'Participants in turn order'); title.id = 'liveTurnTitle';
        const current = make('p', 'sg-live-current'); current.id = 'liveCurrentTurn';
        current.setAttribute('role', 'status'); current.setAttribute('aria-live', 'polite');
        const list = make('ol', 'sg-live-participants'); list.id = 'liveTurnOrder';
        overview.append(title, current, list); primary.append(overview);
        workspace.append(primary, side); main.prepend(workspace);
        const placements = [battle, characters, monsters, tools, lair].map(node => {
            const anchor = document.createComment('live workspace home: ' + (node.id || 'battle'));
            node.before(anchor); return {node, anchor};
        });
        const history = make('details', 'sg-live-history'); history.id = 'liveActivityDisclosure';
        history.open = true; history.append(make('summary', '', 'Activity log'));
        while (log.firstChild) history.append(log.firstChild);
        log.append(history);
        let mounted = false;
        function arrange() {
            const live = document.body.dataset.workflowView === 'live';
            if (live === mounted) return;
            if (live) {
                primary.prepend(battle);
                primary.append(characters, monsters);
                side.append(tools, lair);
            } else {
                for (const {node, anchor} of placements) anchor.after(node);
            }
            mounted = live; workspace.hidden = !live;
        }
        const number = value => typeof value === 'number' && Number.isFinite(value) ? String(value) : '—';
        function render(state) {
            const combatants = [...(state?.characters || []), ...(state?.monsters || [])];
            const lairs = state?.lairs || [];
            const items = new Map([...combatants, ...lairs].map(item => [item.id, item]));
            const order = Array.isArray(state?.battle_order) ? state.battle_order : [];
            const ordered = order.map(id => items.get(id)).filter(Boolean);
            const names = ordered.filter(x => x.active && x.in_turn).map(x => x.name);
            const text = !order.length ? 'No battle order set. Use Battle preparation and Start battle.'
                : 'Round ' + number(state.battle_round) + ' · ' + (names.length ? 'Current turn: ' + names.join(', ') : 'No current participant');
            if (current.textContent !== text) current.textContent = text;
            const nodes = ordered.map(item => {
                const row = make('li', 'sg-live-participant'); row.dataset.combatantId = String(item.id);
                if (item.active && item.in_turn) row.setAttribute('aria-current', 'step');
                const heading = make('div', 'sg-live-participant-heading');
                heading.append(make('strong', '', item.name || 'Unnamed participant'));
                if (item.active && item.in_turn) heading.append(make('span', 'sg-live-turn-badge', 'Current turn'));
                const isLair = lairs.some(x => x.id === item.id);
                const stats = isLair ? 'Lair · Initiative 20 · No HP or AC'
                    : 'HP ' + number(item.hp) + '/' + number(item.max_hp) +
                      (typeof item.temp_hp === 'number' && item.temp_hp ? ' · Temp HP ' + number(item.temp_hp) : '') +
                      ' · Initiative ' + number(item.initiative);
                row.append(heading, make('p', 'sg-live-stat-line', stats));
                if (!isLair) {
                    const conditions = (Array.isArray(item.effects) ? item.effects : [])
                        .filter(e => !e.mechanical && typeof e.name === 'string').map(e => e.name);
                    if (item.concentrating) conditions.unshift('Concentrating');
                    if (item.life_state) conditions.unshift(item.life_state);
                    row.append(make('p', 'sg-live-condition-line', conditions.join(' · ') || 'No conditions recorded'));
                }
                return row;
            });
            list.replaceChildren(...nodes);
        }
        const previous = window.scryingLairsRender;
        window.scryingLairsRender = function(state) {
            const result = typeof previous === 'function' ? previous.apply(this, arguments) : undefined;
            render(state); return result;
        };
        new MutationObserver(arrange).observe(document.body, {
            attributes: true, attributeFilter: ['data-workflow-view'],
        });
        render(typeof latest === 'undefined' ? null : latest);
        arrange(); document.body.dataset.liveWorkspace = 'ready';
    }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', install, {once: true});
    else install();
})();
