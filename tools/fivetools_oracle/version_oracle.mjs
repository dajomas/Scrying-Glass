// Upstream oracle (SG-TODO-033): every monster version from the pinned 5etools runtime.
// Usage: node version_oracle.mjs <5etools-src checkout> <out.json>
// Output: {"<version name>|<version source>": {"base": "<name>|<source>", "ok": <version>} | {"error": ...}}
import fs from "fs";
import path from "path";
const root = process.argv[2];
const outPath = process.argv[3];
await import(path.join(root, "js/parser.js"));
await import(path.join(root, "js/utils.js"));
await import(path.join(root, "js/render.js"));
const read = p => JSON.parse(fs.readFileSync(path.join(root, "data", p), "utf8"));
const templates = read("bestiary/template.json").monsterTemplate.map(t => ({...t, __prop: "monsterTemplate"}));
DataUtil.generic._pMergeCopy_pGetTemplates = async (entry) => entry._copy?._templates ? templates : null;
// Stand-ins for the two page services the version path calls: the loader cache (version
// templates; no pinned version uses them) and the user's exclusion list (none here).
globalThis.DataLoader = {getAllFromCacheAll: () => templates};
globalThis.ExcludeUtil = {isExcluded: () => false};
const key = e => `${e.name}|${e.source}`;
const monsters = [];
for (const f of fs.readdirSync(path.join(root, "data/bestiary")).filter(f => /^bestiary-.*\.json$/.test(f)).sort()) {
  for (const m of read(`bestiary/${f}`).monster || []) { m.__prop = "monster"; monsters.push(m); }
}
// As on the bestiary page: copies are merged before versions are generated.
for (const m of monsters) {
  if (!m._copy) continue;
  try { await DataUtil.generic._pMergeCopy(DataUtil.monster, UrlUtil.PG_BESTIARY, monsters, m, {isErrorOnMissing: true}); }
  catch (e) { m.__mergeError = String(e.message || e); }
}
const out = {};
for (const m of monsters) {
  if (!DataUtil.monster.hasVersions(m)) continue;
  let versions;
  try { versions = DataUtil.monster.getVersions(m); }
  catch (e) { out[`?|${key(m)}`] = {base: key(m), error: String(e.message || e)}; continue; }
  for (const v of versions) {
    const c = JSON.parse(JSON.stringify(v));
    delete c.__prop;
    out[key(v)] = {base: key(m), ok: c};
  }
}
fs.writeFileSync(outPath, JSON.stringify(out));
console.log(Object.keys(out).length, "versions");
