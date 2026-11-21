"""022.04d creature modes and dynamic substitutions on synthetic records."""
import json
import unittest
from types import SimpleNamespace

from python.scrying_glass_fivetools_modifications import apply_modifications, ModificationError
from python.scrying_glass_fivetools_substitutions import short_name, title_case


def op(selector, mode, **payload):
    data = {'mode': mode, **payload}
    return SimpleNamespace(property=selector, mode=mode, payload_json=json.dumps(data).encode())


def apply(record, *ops):
    return apply_modifications(record, ops, check=lambda: None)


BASE = {'name': 'Grave Wight', 'cr': '13', 'size': ['M', 'L'], 'str': 18, 'dex': 14, 'con': 16, 'int': 11, 'wis': 13, 'cha': 8,
        'save': {'dex': '+6'}, 'skill': {'perception': '+7'}, 'senses': ['darkvision 120 ft.'],
        'spellcasting': [{'name': 'Innate', 'will': ['{@spell b}'], 'daily': {'2': ['{@spell b}', '{@spell a}']},
                          'spells': {'1': {'slots': 3, 'spells': ['{@spell shield}', '{@spell alarm}']}}},
                         {'name': 'Second', 'will': ['{@spell y}']}]}


def fail(code):
    raise ValueError(code)


class CreatureModeTests(unittest.TestCase):
    def error(self, code, record, *ops):
        with self.assertRaises(ModificationError) as caught:
            apply(record, *ops)
        self.assertEqual(caught.exception.diagnostic.code, code)

    def test_senses_keep_greater_ranges(self):
        out = apply(BASE, op('_', 'addSenses', senses=[{'type': 'Darkvision', 'range': 60}, {'type': 'blindsight', 'range': 30}]))
        self.assertEqual(out['senses'], ['darkvision 120 ft.', 'blindsight 30 ft.'])
        out = apply(BASE, op('_', 'addSenses', senses={'type': 'darkvision', 'range': 240}))
        self.assertEqual(out['senses'], ['darkvision 240 ft.'])
        self.assertEqual(apply({'name': 'A'}, op('_', 'addSenses', senses={'type': 'tremorsense', 'range': 10}))['senses'], ['tremorsense 10 ft.'])

    def test_saves_and_skills_never_reduce(self):
        out = apply(BASE, op('_', 'addSaves', saves={'dex': 1, 'cha': 0}), op('_', 'addSkills', skills={'perception': 1, 'athletics': 2}))
        self.assertEqual(out['save'], {'dex': '+7', 'cha': -1})
        self.assertEqual(out['skill'], {'perception': '+7', 'athletics': '+14'})
        out = apply(BASE, op('_', 'addAllSaves', saves=1))
        self.assertEqual(list(out['save']), ['dex', 'str', 'con', 'int', 'wis', 'cha'])
        self.assertEqual(out['save']['cha'], '+4')
        self.error('nonfinite_numeric_result', {'name': 'A', 'cr': '1'}, op('_', 'addSaves', saves={'dex': 1}))

    def test_spell_additions_replacements_and_removals(self):
        out = apply(BASE, op('_', 'addSpells', spells={'1': {'spells': ['{@spell Burning Hands}']}}, will=['{@spell c}'],
                             daily={'1e': ['{@spell d}'], 'x': ['{@spell e}']}))
        first = out['spellcasting'][0]
        self.assertEqual(first['spells']['1']['spells'], ['{@spell alarm}', '{@spell Burning Hands}', '{@spell shield}'])
        self.assertEqual(first['will'], ['{@spell b}', '{@spell c}'])
        self.assertEqual(first['daily'], {'2': ['{@spell b}', '{@spell a}'], '1e': ['{@spell d}']})
        out = apply(BASE, op('_', 'addSpells', name='Second', will=['{@spell z}']))
        self.assertEqual(out['spellcasting'][1]['will'], ['{@spell y}', '{@spell z}'])
        self.error('missing_spellcasting', BASE, op('_', 'addSpells', name='Nope', will=['x']))
        out = apply(BASE, op('_', 'replaceSpells', daily={'2': [{'replace': '{@spell b}', 'with': ['{@spell c}', '{@spell A}']}]}))
        self.assertEqual(out['spellcasting'][0]['daily']['2'], ['{@spell A}', '{@spell a}', '{@spell c}'])
        self.error('missing_modification_item', BASE, op('_', 'replaceSpells', spells={'1': [{'replace': 'x', 'with': 'y'}]}))
        out = apply(BASE, op('_', 'removeSpells', spells={'1': ['{@spell shield}']}, will=['{@spell b}'], daily={'2': ['{@spell a}']}))
        self.assertEqual(out['spellcasting'][0]['spells']['1']['spells'], ['{@spell alarm}'])
        self.assertEqual(out['spellcasting'][0]['will'], ['{@spell b}'])
        self.assertEqual(out['spellcasting'][0]['daily']['2'], ['{@spell b}'])
        self.error('missing_spellcasting', {'name': 'A'}, op('_', 'addSpells', will=['x']))

    def test_size_and_experience(self):
        self.assertEqual(apply(BASE, op('_', 'maxSize', max='M'))['size'], ['M'])
        self.assertEqual(apply(BASE, op('_', 'maxSize', max='S'))['size'], ['S'])
        self.error('unsupported_size', BASE, op('_', 'maxSize', max='Q'))
        self.assertEqual(apply(BASE, op('_', 'scalarMultXp', scalar=2))['cr'], {'cr': '13', 'xp': 20000})
        self.assertEqual(apply({'name': 'A', 'cr': {'cr': '1', 'xp': 100}}, op('_', 'scalarMultXp', scalar=1.5, floor=True))['cr']['xp'], 150)

    def test_wildcard_runs_creature_modes_per_target(self):
        out = apply({'name': 'A', 'senses': []}, op('*', 'addSenses', senses={'type': 'darkvision', 'range': 60}))
        self.assertEqual(out['senses'], ['darkvision 60 ft.'])


class SubstitutionTests(unittest.TestCase):
    def text(self, value, **record):
        record = {**BASE, **record}
        return apply(record, op('action', 'appendArr', items=value))['action'][0]

    def test_variables(self):
        self.assertEqual(self.text('<$name$>, <$short_name$>, <$title_short_name$>'), 'Grave Wight, the grave wight, The grave wight')
        self.assertEqual(self.text('DC <$dc__con$>, <$spell_dc__cha$>, <$to_hit__str$>'), 'DC 16, 12, +9')
        self.assertEqual(self.text('1d6<$damage_mod__dex$>|1d6<$damage_mod__cha$>|1d6<$damage_mod__int$>'), '1d6 + 2|1d6 - 1|1d6')
        self.assertEqual(self.text('<$damage_avg__4.5*size_mult+str$>|<$size_mult$>|<$size_mult__1.5$>'), '8|1|1')
        self.assertEqual(self.text('<$size_mult$>', size=['H']), '3')
        self.assertEqual(self.text('<$unknown__x$>'), '<$unknown__x$>')
        with self.assertRaises(ModificationError):
            self.text('<$dc__xyz$>')

    def test_short_names(self):
        self.assertEqual(short_name({'name': 'Adult Red Dragon'}, fail), 'the dragon')
        self.assertEqual(short_name({'name': 'Strahd von Zarovich', 'isNamedCreature': True}, fail, title=True), 'Strahd')
        self.assertEqual(short_name({'name': 'X', 'shortName': 'drow mage', 'isNamedCreature': True}, fail, title=True), 'Drow Mage')
        self.assertEqual(short_name({'name': 'X', 'shortName': True}, fail), 'the X')
        self.assertEqual(title_case('the lord of the rings'), 'The Lord of the Rings')


if __name__ == '__main__':
    unittest.main()
