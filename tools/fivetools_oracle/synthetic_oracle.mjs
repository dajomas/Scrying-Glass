// 022.04f oracle: apply each synthetic _copy case with the pinned 5etools runtime (not run by CI).
import fs from "fs"; import path from "path";
const root = process.argv[2];
await import(path.join(root, "js/parser.js")); await import(path.join(root, "js/utils.js")); await import(path.join(root, "js/render.js"));
const cases = JSON.parse(fs.readFileSync(process.argv[3]));
const out = cases.map(c => {
  const to = JSON.parse(JSON.stringify(c.copy)); to.__prop = "monster";
  for (const k of Object.keys(to)) if (to[k] === null && k !== "_copy") {} // keep nulls (null deletes base key)
  try { DataUtil.generic.copyApplier.getCopy(DataUtil.monster, JSON.parse(JSON.stringify(c.base)), to, null); delete to.__prop;
        let dirty = false; const walk = v => { if (v === undefined || (typeof v === "number" && !isFinite(v))) dirty = true; else if (Array.isArray(v)) v.forEach(walk); else if (v && typeof v === "object") Object.values(v).forEach(walk); };
        walk(to); return {ok: JSON.parse(JSON.stringify(to)), dirty}; }
  catch (e) { return {error: String(e.message || e).slice(0, 200)}; }
});
fs.writeFileSync(process.argv[4], JSON.stringify(out));
