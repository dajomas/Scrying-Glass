const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const {installFeedback} = require('./battle-action-feedback-fixture.cjs');
const source = fs.readFileSync(path.join(__dirname, '../static/admin.js'), 'utf8');
const start = source.indexOf('function activeBattleTargets()');
const block = source.slice(start, source.indexOf("document.addEventListener('click', async event => {", start));
function fixture() {
    const ids = {}, requests = [], messages = [];
    const rows = {children: [], appendChild(x) {this.children.push(x);},
        querySelectorAll() {return this.children;},
        set innerHTML(value) {this.children = [];}};
    function element() {
        const fields = {};
        const row = {dataset: {}, children: [],
            set innerHTML(html) {
                for (const key of ['target', 'kind', 'stat', 'amount', 'critical', 'source', 'remove-action-row']) {
                    if (key === 'source' && !html.includes('data-action-source')) continue;
                    fields[key] = {value: key === 'kind' ? (html.includes('value="reduce-stat"')?'reduce-stat':'damage') : key === 'amount' ? '1' : '',
                        checked: false, disabled: false, required: ['target', 'source'].includes(key),
                        parentElement: {}, addEventListener() {}, closest() {return row;}};
                }
            },
            querySelector(selector) {
                if (selector === '.amount-field') return {};
                const key = selector === '[data-remove-action-row]' ? 'remove-action-row'
                    : selector.slice('[data-action-'.length, -1);
                return fields[key] || null;
            },
            querySelectorAll() {return Object.values(fields);},
            appendChild(x) {this.children.push(x);},
            remove() {rows.children.splice(rows.children.indexOf(row), 1);}};
        return row;
    }
    const button = () => ({disabled: false, closest() {return null;}});
    ids['#closeBattleActions'] = button();
    ids['#addBattleActionTarget'] = button(); ids['#addBattleReaction'] = button();
    const apply = button(), turn = button();
    const modal = {hidden: false, attributes: {}, addEventListener(type, fn) {this.click = fn;},
        querySelectorAll() {return [apply, turn, ...Object.values(ids).filter(x => 'disabled' in x),
            ...rows.children.flatMap(row => row.querySelectorAll())];},
        setAttribute(key, value) {this.attributes[key] = value;},
        removeAttribute(key) {delete this.attributes[key];}};
    const form = {querySelector() {return apply;}, reportValidity() {
        return rows.children.every(row => row.querySelectorAll().every(x =>
            x.disabled || !x.required || Boolean(x.value)));
    }};
    const ctx = {battleActionsApplying: false, battleActionActorId: 'm',
        battleActionRows: rows, battleActionForm: form, battleActionModal: modal,
        latest: {lairs: [], monsters: [{id:'m', name:'Monster', active:true, alive:true, in_turn:true}],
            characters:[{id:'c', name:'Character', active:true, alive:true}]},
        document: {createElement: element, querySelector: id => ids[id] ||= {}},
        message: x => messages.push(x), esc: String,
        request: async (url, options) => {
            const payload = JSON.parse(options.body); requests.push(payload);
            if (ctx.fail) throw new Error('Rejected');
            if (ctx.wait) await ctx.wait;
            return {applied: payload.actions.length};
        }, load: async () => {if (ctx.refreshFail) throw new Error('Offline');},
    };
    installFeedback(ctx);
    vm.runInNewContext(block, ctx);
    const add = (reaction = false, amount = 3) => {
        ctx.addBattleActionRow(reaction);
        const row = rows.children.at(-1);
        row.querySelector('[data-action-target]').value = 'c';
        row.querySelector('[data-action-amount]').value = String(amount);
        if (reaction) row.querySelector('[data-action-source]').value = 'm';
        return row;
    };
    return {ctx, rows, modal, form, ids, requests, messages, add, apply, turn,
        submit: () => form.onsubmit({preventDefault() {}})};
}
(async () => {
 const f=fixture();f.ctx.battleStatisticsToken='original-token';
 f.ctx.addStatisticsReductionRow();let row=f.rows.children[0];
 row.querySelector('[data-action-target]').value='c';row.querySelector('[data-action-stat]').value='wisdom';row.querySelector('[data-action-amount]').value='3';
 await f.submit();assert.equal(f.requests[0].statistics_token,'original-token');
 assert.equal(f.requests[0].actions[0].action,'reduce-stat');assert.equal(f.requests[0].actions[0].stat,'wisdom');assert.equal(f.requests[0].actions[0].amount,3);
 assert.equal(row.dataset.applied,'true');await f.submit();assert.equal(f.requests.length,1,'Applied reduction cannot replay');
 const g=fixture();g.ctx.addStatisticsReductionRow();assert.equal(g.rows.children.length,1);g.ctx.closeBattleActions();assert.equal(g.rows.children.length,0);assert.equal(g.requests.length,0);
 const h=fixture();h.ctx.battleStatisticsToken='token';h.add(false,4);h.ctx.addStatisticsReductionRow();row=h.rows.children[1];row.querySelector('[data-action-target]').value='c';row.querySelector('[data-action-stat]').value='dexterity';row.querySelector('[data-action-amount]').value='2';await h.submit();
 assert.deepEqual(h.requests[0].actions.map(x=>x.action),['damage','reduce-stat']);assert.equal(h.requests[0].actions[0].stat,undefined);
 const markup=fs.readFileSync(path.join(__dirname,'../templates/admin/180_battle_action_modal.html'),'utf8');assert.match(markup,/Add statistics reduction/);
 for(const value of ['max_hp','strength','dexterity','constitution','intelligence','wisdom','charisma'])assert.ok(source.includes('value="'+value+'"'));
 const encounter=fs.readFileSync(path.join(__dirname,'../templates/admin/020_battle_controls.html'),'utf8');assert.ok(!encounter.includes('manualReductionPanel'));
 assert.ok(source.indexOf('data-statistics="${esc(character.id)}"')>source.indexOf('data-cr="${esc(character.id)}"'));
 console.log('PASS: attack reduction rows, seven choices, ordered payload, locking/replay, cancellation and character restore location');
})().catch(error=>{console.error(error);process.exitCode=1;});
