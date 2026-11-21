// Upstream oracle (SG-TODO-033 part 2): generic and specific magic-item variants from the
// pinned 5etools runtime, as Renderer.item.pGetSiteUnresolvedRefItems builds them, before
// Renderer.item._enhanceItems (item enhancement is not in scope).
// Usage: node item_oracle.mjs <5etools-src checkout> <out.json>
// Output: {"generic": [...], "specific": [...]} in runtime order; __prop and the generic
// variants' back-references (variants) removed.
import fs from "fs";
import path from "path";
const root = process.argv[2];
const outPath = process.argv[3];
await import(path.join(root, "js/parser.js"));
await import(path.join(root, "js/utils.js"));
await import(path.join(root, "js/render.js"));
await import(path.join(root, "js/render-dice.js"));
// Page services the item path touches, with the site defaults: the style setting (default
// "one", see js/utils-config/utils-config-registry.js) and no prerelease/homebrew content.
globalThis.VetoolsConfig = {get: (group, id) => (group === "styleSwitcher" && id === "style" ? "one" : undefined)};
Renderer.item._pAddPrereleaseBrewPropertiesAndTypes = async () => {};
DataUtil._pLoad = async ({url}) => JSON.parse(fs.readFileSync(path.join(root, url.slice(url.indexOf("data/"))), "utf8"));
const baseItemsJson = await DataUtil.loadJSON(`${Renderer.get().baseUrl}data/items-base.json`);
const baseItems = await Renderer.item._pGetAndProcBaseItems(baseItemsJson);
const {genericVariants, linkedLootTables} = await Renderer.item._pGetCacheSiteGenericVariants();
const specificVariants = Renderer.item._createSpecificVariants(baseItems, genericVariants, {linkedLootTables});
const clean = ent => {
  const c = {...ent};
  delete c.__prop;
  delete c.variants;
  return JSON.parse(JSON.stringify(c));
};
// items.json internal copies, merged by DataUtil.loadJSON (checks the item preserve rule).
const itemCopies = {};
for (const it of (await DataUtil.loadJSON(`${Renderer.get().baseUrl}data/items.json`)).item) {
  if (it._isCopy) itemCopies[`${it.name}|${it.source}`] = clean(it);
}
fs.writeFileSync(outPath, JSON.stringify({generic: genericVariants.map(clean), specific: specificVariants.map(clean), itemCopies}));
console.log(genericVariants.length, "generic,", specificVariants.length, "specific");
