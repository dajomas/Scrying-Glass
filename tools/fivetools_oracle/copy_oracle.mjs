// Upstream oracle: resolve every _copy entity with the pinned 5etools runtime.
// Usage: node copy_oracle.mjs <5etools-src checkout> <out.json>
import fs from "fs";
import path from "path";
const root = process.argv[2];
const outPath = process.argv[3];
await import(path.join(root, "js/parser.js"));
await import(path.join(root, "js/utils.js"));
await import(path.join(root, "js/render.js"));
const read = p => JSON.parse(fs.readFileSync(path.join(root, "data", p), "utf8"));
const tplData = read("bestiary/template.json");
const templates = tplData.monsterTemplate.map(t => ({...t, __prop: "monsterTemplate"}));
const out = {monster: {}, monsterTemplate: {}, legendaryGroup: {}};
const key = e => `${e.name}|${e.source}`;
const strip = e => { const c = JSON.parse(JSON.stringify(e)); delete c.__prop; return c; };
for (const t of templates) {
  if (!t._copy) continue;
  try { await DataUtil.generic._pMergeCopy(DataUtil.monsterTemplate, "monsterTemplate", templates, t, {isErrorOnMissing: true}); out.monsterTemplate[key(t)] = {ok: strip(t)}; }
  catch (e) { out.monsterTemplate[key(t)] = {error: String(e.message || e)}; }
}
DataUtil.generic._pMergeCopy_pGetTemplates = async (entry) => entry._copy?._templates ? templates : null;
const monsters = [];
for (const f of fs.readdirSync(path.join(root, "data/bestiary")).filter(f => /^bestiary-.*\.json$/.test(f)).sort()) {
  for (const m of read(`bestiary/${f}`).monster || []) { m.__prop = "monster"; monsters.push(m); }
}
const copies = monsters.filter(m => m._copy).map(m => key(m));
for (const m of monsters) {
  if (!m._copy) continue;
  const k = key(m);
  try { await DataUtil.generic._pMergeCopy(DataUtil.monster, UrlUtil.PG_BESTIARY, monsters, m, {isErrorOnMissing: true}); out.monster[k] = {ok: strip(m)}; }
  catch (e) { out.monster[k] = {error: String(e.message || e)}; }
}
const groups = read("bestiary/legendarygroups.json").legendaryGroup.map(g => ({...g, __prop: "legendaryGroup"}));
for (const g of groups) {
  if (!g._copy) continue;
  try { await DataUtil.generic._pMergeCopy(DataUtil.legendaryGroup, "legendaryGroup", groups, g, {isErrorOnMissing: true}); out.legendaryGroup[key(g)] = {ok: strip(g)}; }
  catch (e) { out.legendaryGroup[key(g)] = {error: String(e.message || e)}; }
}
fs.writeFileSync(outPath, JSON.stringify(out));
console.log(Object.keys(out.monster).length, Object.keys(out.monsterTemplate).length, Object.keys(out.legendaryGroup).length);
