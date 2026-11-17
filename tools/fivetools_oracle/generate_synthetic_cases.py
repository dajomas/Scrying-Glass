"""Generate synthetic _copy cases covering every copy mode and edge option (022.04f oracle)."""
import json, itertools
base = {
 "name": "Base", "source": "SRC", "size": ["M", "L"], "type": "undead", "cr": "13", "str": 18, "dex": 14, "con": 16, "int": 11, "wis": 13, "cha": 18,
 "save": {"dex": "+6", "wis": "+5"}, "skill": {"perception": "+7", "stealth": "+9"}, "senses": ["darkvision 120 ft."], "passive": 17,
 "trait": [{"name": "Regeneration", "entries": ["The base regains 20 {@variantrule Hit Points|XPHB}. The base can't {@condition charmed}.", {"type": "list", "items": ["the base fights", "base"]}]},
           {"name": "Spider Climb", "entries": ["The base climbs. DC {@dc 15|display} and {@hit 5} to hit {@hit -1}."]}, "the base string trait"],
 "action": [{"name": "Multiattack", "entries": ["The base makes two attacks."]}, {"name": "Bite", "entries": ["{@atkr m} {@hit 9}, {@dc 17}"]}, "plain"],
 "legendaryHeader": ["The base can take 3 legendary actions."],
 "spellcasting": [{"name": "Innate Spellcasting", "headerEntries": ["The base casts."], "will": ["{@spell mage hand}"], "daily": {"1e": ["{@spell fly}"], "2": ["{@spell b}", "{@spell a}"]},
                   "spells": {"1": {"slots": 3, "spells": ["{@spell shield}", "{@spell magic missile}"]}, "0": {"spells": ["{@spell light}"]}}, "constant": ["{@spell x}"]},
                  {"name": "Second", "headerEntries": ["Other."], "will": ["{@spell y}"]}],
 "speed": {"walk": 30, "fly": {"number": 60, "condition": "(hover)"}}, "ac": [16], "hp": {"average": 100, "formula": "10d10"},
 "mixed": {"a": 1, "b": "+2", "c": "3", "10": 4, "2": "-5", "d": -2}, "shortName": None, "isNamedCreature": None,
}
base = {k: v for k, v in base.items() if v is not None}
def m(**kw): return kw
cases = []
def add(mods, **extra):
    copy = {"name": "Copy", "source": "SRC", "_copy": {"name": "Base", "source": "SRC", "_mod": mods}}
    copy.update(extra)
    cases.append({"base": base, "copy": copy})
# replaceTxt
for rep, fl, w in [("base", None, "copy"), ("base", "i", "$&!"), ("\\bthe base\\b", "i", "the copy"), ("(Base|base)", "", "<$1>"), ("x*", "", "-"), ("{@", "", "["), ("climb", "g", "z")]:
    for prop in ("trait", "action", "*", "legendaryHeader", "nonexistent", "_"):
        mi = {"mode": "replaceTxt", "replace": rep, "with": w}
        if fl is not None: mi["flags"] = fl
        add({prop: mi})
add({"trait": {"mode": "replaceTxt", "replace": "base", "with": "copy", "props": ["entries"]}})
add({"trait": {"mode": "replaceTxt", "replace": "base", "with": "copy", "props": []}})
add({"trait": {"mode": "replaceTxt", "replace": "base", "with": "copy", "props": [None]}})
add({"trait": {"mode": "replaceTxt", "replace": "base", "with": "copy", "props": ["name"]}})
add({"trait": {"mode": "replaceTxt", "replace": "Hit", "with": "X", "tagInsensitive": True}})
add({"trait": {"mode": "replaceTxt", "replace": "Hit", "with": "X"}})
add({"trait": {"mode": "replaceTxt", "replace": "(", "with": "X"}})
add({"trait": {"mode": "replaceTxt", "replace": "a", "with": "b", "flags": "gu"}})
add({"mixed": {"mode": "replaceTxt", "replace": "a", "with": "b"}})
# replaceName
for prop in ("trait", "action", "*", "mixed"):
    add({prop: {"mode": "replaceName", "replace": "i", "with": "I", "flags": "i"}})
# replaceArr / replaceOrAppendArr
for mode in ("replaceArr", "replaceOrAppendArr"):
    for sel in ["Bite", "plain", "Nope", {"regex": "^m"}, {"regex": "^M", "flags": "i"}, {"regex": "^(Multiattack|Bite)$", "flags": "g"}, {"index": 0}, {"index": 1.7}, {"index": -1}, {"index": -2}, {"index": 99}, {"index": 4294967295}, {"regex": ""}, {"index": None}]:
        for items in ({"name": "New", "entries": ["n"]}, [{"name": "A"}, "b"], []):
            add({"action": {"mode": mode, "replace": sel, "items": items}})
    add({"missing": {"mode": mode, "replace": "x", "items": ["y"]}})
    add({"action": {"mode": mode, "items": ["y"]}})
    add({"mixed": {"mode": mode, "replace": "x", "items": ["y"]}})
# removeArr
for mi in [m(mode="removeArr", names="Bite"), m(mode="removeArr", names=["Bite", "Multiattack"]), m(mode="removeArr", names="Nope"), m(mode="removeArr", names="Nope", force=True),
           m(mode="removeArr", items="plain"), m(mode="removeArr", items=["plain", "x"]), m(mode="removeArr", items={"name": "Bite"}), m(mode="removeArr"), m(mode="removeArr", names="")]:
    for prop in ("action", "missing"):
        add({prop: mi})
# renameArr
for mi in [m(mode="renameArr", renames={"rename": "Bite", "with": "Chomp"}), m(mode="renameArr", renames=[{"rename": "Bite", "with": "C"}, {"rename": "C", "with": "D"}]), m(mode="renameArr", renames={"rename": "Nope", "with": "x"}), m(mode="renameArr", renames=[])]:
    for prop in ("action", "missing"):
        add({prop: mi})
# scalar props
for mode in ("scalarAddProp", "scalarMultProp"):
    for prop in ("a", "b", "c", "*", "zz", "10"):
        for scalar in (2, -3, 0.5, 1.5):
            mi = {"mode": mode, "prop": prop, "scalar": scalar}
            add({"mixed": mi})
            if mode == "scalarMultProp":
                add({"mixed": dict(mi, floor=True)})
    add({"missing": {"mode": mode, "prop": "a", "scalar": 1}})
    add({"save": {"mode": mode, "prop": "*", "scalar": 2}})
# calculateProp
for formula in ("<$prof_bonus$>", "<$dex_mod$> + 1", "2 * <$prof_bonus$> + <$dex_mod$>", "10 / 4", "3,4", "<$wis_mod$>", "1/0", "2**3"):
    add({"mixed": {"mode": "calculateProp", "prop": "calc", "formula": formula}})
    add({"newobj": {"mode": "calculateProp", "prop": "calc", "formula": formula}})
# tag scalars
for mode in ("scalarAddHit", "scalarAddDc"):
    for prop in ("trait", "action", "*", "missing"):
        for scalar in (2, -10):
            add({prop: {"mode": mode, "scalar": scalar}})
# creature modes
for senses in ({"type": "darkvision", "range": 60}, {"type": "darkvision", "range": 240}, [{"type": "blindsight", "range": 30}, {"type": "Darkvision", "range": 200}], {"type": "tremor.sense", "range": 10}):
    add({"_": {"mode": "addSenses", "senses": senses}})
    add({"*": {"mode": "addSenses", "senses": senses}})
add({"_": {"mode": "addSenses", "senses": {"type": "darkvision", "range": 60}}}, senses=None)
for saves in ({"dex": 1}, {"str": 2, "wis": 1}, {"con": 1, "dex": 2}):
    add({"_": {"mode": "addSaves", "saves": saves}})
add({"_": {"mode": "addAllSaves", "saves": 1}})
add({"_": {"mode": "addAllSaves", "saves": 2}})
for skills in ({"perception": 1}, {"perception": 2, "athletics": 1}, {"arcana": 1}):
    add({"_": {"mode": "addSkills", "skills": skills}})
add({"_": {"mode": "addAllSkills", "skills": 1}})
add({"_": {"mode": "addSaves", "saves": {"dex": 1}}}, cr={"cr": "1/2", "lair": "2"})
add({"_": {"mode": "addSaves", "saves": {"dex": 1}}}, cr="Unknown")
for mi in [m(mode="addSpells", spells={"1": {"spells": ["{@spell zap}"]}}), m(mode="addSpells", spells={"2": {"slots": 2, "spells": ["{@spell a}"]}}),
           m(mode="addSpells", will=["{@spell c}"], daily={"1e": ["{@spell d}"], "3": ["{@spell e}"], "x": ["{@spell f}"]}), m(mode="addSpells", name="Second", will=["{@spell z}"]),
           m(mode="addSpells", name="Nope", will=["{@spell z}"]), m(mode="addSpells", constant=["{@spell q}"], ritual=["{@spell r}"], recharge={"5": ["{@spell s}"]}),
           m(mode="addSpells", spells={"1": {"slots": 4}}), m(mode="addSpells", name="Second", spells={"1": {"spells": ["{@spell a}"]}}),
           m(mode="replaceSpells", spells={"1": [{"replace": "{@spell shield}", "with": "{@spell aa}"}]}), m(mode="replaceSpells", spells={"1": [{"replace": "{@spell nope}", "with": "x"}]}),
           m(mode="replaceSpells", daily={"2": [{"replace": "{@spell b}", "with": ["{@spell c}", "{@spell A}"]}]}), m(mode="replaceSpells", spells={"9": [{"replace": "x", "with": "y"}]}),
           m(mode="removeSpells", spells={"1": ["{@spell shield}"]}), m(mode="removeSpells", daily={"2": ["{@spell a}"]}), m(mode="removeSpells", will=["{@spell mage hand}"]),
           m(mode="removeSpells", daily={"3": ["x"]}), m(mode="removeSpells", spells={"5": ["x"]})]:
    add({"_": mi})
add({"_": {"mode": "addSpells", "will": ["x"]}}, spellcasting=None)
for mx in ("S", "M", "L", "G", "Q"):
    add({"_": {"mode": "maxSize", "max": mx}})
add({"_": {"mode": "maxSize", "max": "M"}}, size="H")
for cr, scalar, floor in [("13", 2, False), ({"cr": "13", "xp": 100}, 1.5, True), ({"cr": "1/4"}, 0.5, False), ("Unknown", 2, False), ("0", 3, False)]:
    mi = {"mode": "scalarMultXp", "scalar": scalar}
    if floor: mi["floor"] = True
    add({"_": mi}, cr=cr)
# dynamic substitutions
for text in ("<$name$> hits", "<$short_name$>", "<$title_short_name$>", "DC <$dc__con$>", "<$spell_dc__cha$>", "<$to_hit__str$>", "1d6<$damage_mod__dex$>", "<$damage_avg__2.5+str$>", "<$damage_avg__4.5*size_mult+dex$>",
             "<$size_mult$>", "<$size_mult__1.5$>", "<$unknown__x$>", "<$dc__xyz$>", "<$name$><$name$>", "<$damage_mod__int$>"):
    add({"action": {"mode": "appendArr", "items": {"name": "Dyn", "entries": [text]}}})
add({"action": {"mode": "appendArr", "items": {"name": "Dyn", "entries": ["<$short_name$> / <$title_short_name$>"]}}}, name="Adult Red Dragon")
add({"action": {"mode": "appendArr", "items": {"name": "Dyn", "entries": ["<$short_name$> / <$title_short_name$>"]}}}, name="Strahd von Zarovich", isNamedCreature=True)
add({"action": {"mode": "appendArr", "items": {"name": "Dyn", "entries": ["<$short_name$> / <$title_short_name$>"]}}}, shortName="the big one of a kind")
add({"action": {"mode": "appendArr", "items": {"name": "Dyn", "entries": ["<$short_name$> / <$title_short_name$>"]}}}, shortName="drow mage", isNamedCreature=True)
add({"action": {"mode": "appendArr", "items": {"name": "Dyn", "entries": ["<$short_name$>"]}}}, shortName=True)
# ordering compositions
add({"action": [{"mode": "replaceTxt", "replace": "base", "with": "X", "flags": "i"}, {"mode": "appendArr", "items": "the base"}]})
add({"action": [{"mode": "appendArr", "items": "the base"}, {"mode": "replaceTxt", "replace": "base", "with": "X", "flags": "i"}]})
add({"*": {"mode": "replaceTxt", "replace": "base", "with": "W"}, "_": {"mode": "setProp", "prop": "trait", "value": ["base"]}, "action": {"mode": "removeArr", "names": "Bite"}})
import sys
json.dump(cases, open(sys.argv[1] if len(sys.argv) > 1 else 'synthetic_cases.json', 'w'))
print(len(cases))
