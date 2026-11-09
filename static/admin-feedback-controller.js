/* SG-TODO-009.7: explicit operation feedback; no network or DOM interception. */
(() => {
    'use strict';
    function createController(options = {}) {
        const schedule = options.setTimeout || globalThis.setTimeout.bind(globalThis);
        const cancel = options.clearTimeout || globalThis.clearTimeout.bind(globalThis);
        const lanes = new Map(), attempts = new Map(), tickets = new WeakMap();
        const records = new Map(), listeners = new Set();
        let sequence = 0, disposed = false, notifying = false, dirty = false;
        const required = (value, field) => {
            if (typeof value !== 'string' || !value.trim()) throw new TypeError(field + ' must be a nonempty string');
            return value;
        };
        function alive() { if (disposed) throw new Error('Feedback controller is disposed'); }
        function snapshot() { return Object.freeze([...records.values()].map(entry => entry.record)); }
        function notify() {
            dirty = true;
            if (notifying) return;
            notifying = true;
            try {
                while (dirty) {
                    dirty = false;
                    const value = snapshot();
                    for (const listener of [...listeners]) {
                        if (listeners.has(listener)) listener(value);
                        if (dirty) break;
                    }
                }
            } finally { notifying = false; }
        }
        function remove(id) {
            const entry = records.get(id);
            if (!entry) return false;
            if (entry.timer !== null) cancel(entry.timer);
            records.delete(id);
            return true;
        }
        function removeOperation(key, predicate = () => true) {
            let changed = false;
            for (const [id, entry] of records) {
                if (entry.key === key && predicate(entry.record)) changed = remove(id) || changed;
            }
            return changed;
        }
        function setScope(lane, scope) {
            alive(); required(lane, 'lane'); required(scope, 'scope');
            const previous = lanes.get(lane);
            if (previous?.scope === scope) return false;
            const epoch = ++sequence;
            lanes.set(lane, {scope, epoch});
            for (const [key, entry] of attempts) if (entry.lane === lane) attempts.delete(key);
            let changed = false;
            for (const [id, entry] of records) if (entry.record.lane === lane) changed = remove(id) || changed;
            if (changed) notify();
            return true;
        }
        function begin(spec) {
            alive();
            const lane = required(spec.lane, 'lane'), scope = required(spec.scope, 'scope');
            const operation = required(spec.operation, 'operation');
            const target = required(spec.target, 'target'), region = required(spec.region, 'region');
            const label = required(spec.label, 'label');
            if (!['global', 'pane'].includes(spec.placement)) throw new TypeError('placement must be global or pane');
            const active = lanes.get(lane);
            if (!active || active.scope !== scope) throw new Error('Activate the matching lane scope before beginning feedback');
            const key = JSON.stringify([lane, operation, target]);
            const token = ++sequence;
            const ticket = Object.freeze({lane, scope, operation, target, region, label,
                placement: spec.placement, epoch: active.epoch, token});
            const entry = {lane, key, ticket, settled: false};
            attempts.set(key, entry); tickets.set(ticket, entry);
            return ticket;
        }
        function current(ticket) {
            if (disposed || !ticket || typeof ticket !== 'object') return null;
            const entry = tickets.get(ticket), lane = lanes.get(ticket.lane);
            return entry && !entry.settled && attempts.get(entry.key) === entry &&
                lane?.epoch === ticket.epoch && lane.scope === ticket.scope ? entry : null;
        }
        function publish(ticket, outcome) {
            alive();
            const entry = current(ticket);
            if (!entry) return false;
            const severity = outcome.severity;
            if (!['success', 'error', 'info'].includes(severity)) throw new TypeError('Explicit severity is required');
            const text = required(outcome.text, 'text');
            if (severity === 'info') removeOperation(entry.key, record => record.severity === 'info');
            else {
                removeOperation(entry.key);
                entry.settled = true;
            }
            const id = 'sg-feedback-' + (++sequence);
            const record = Object.freeze({id, ...ticket, severity, text});
            const stored = {record, key: entry.key, timer: null};
            records.set(id, stored);
            if (severity === 'success') {
                stored.timer = schedule(() => {
                    if (records.get(id) !== stored) return;
                    remove(id); notify();
                }, ticket.placement === 'global' ? 5000 : 3000);
            }
            notify();
            return id;
        }
        function resolve(ticket) {
            alive();
            const entry = current(ticket);
            if (!entry) return false;
            entry.settled = true;
            if (removeOperation(entry.key)) notify();
            return true;
        }
        function dismiss(id) {
            alive();
            const changed = remove(id);
            if (changed) notify();
            return changed;
        }
        function subscribe(listener) {
            alive();
            if (typeof listener !== 'function') throw new TypeError('listener must be a function');
            listeners.add(listener);
            listener(snapshot());
            return () => listeners.delete(listener);
        }
        function dispose() {
            if (disposed) return;
            disposed = true;
            for (const id of [...records.keys()]) remove(id);
            attempts.clear(); lanes.clear();
            notify(); listeners.clear();
        }
        return Object.freeze({setScope, begin, publish, resolve, dismiss, snapshot, subscribe, dispose,
            isCurrent: ticket => Boolean(current(ticket))});
    }
    const api = Object.freeze({createController});
    if (typeof module === 'object' && module.exports) module.exports = api;
    else globalThis.ScryingFeedback = api;
})();
