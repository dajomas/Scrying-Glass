"""Initiative preconditions and transactional rollback regression tests."""
import asyncio
import copy
import sqlite3
import unittest
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import Mock
from python.scrying_glass_database_transactions import transactional_handler
from python.scrying_glass_initiative_gate import validate_initiative_request, validate_initiative_transition

class HTTPError(Exception):
    def __init__(self, status_code, detail):
        self.status_code, self.detail = status_code, detail
        super().__init__(detail)

class Storage:
    def __init__(self):
        self.db = sqlite3.connect(':memory:')
        self.db.execute('CREATE TABLE writes (value INTEGER)')
        self.db.commit()
    @contextmanager
    def transaction(self):
        with self.db: yield

class InitiativeJoinTests(unittest.TestCase):
    def setUp(self):
        self.c = SimpleNamespace(STATE={'characters': [], 'monsters': []}, HTTPException=HTTPError, STORAGE=Storage())
        self.c.selected_entities = lambda kind, ids: [item for item in self.c.STATE[kind] if item['id'] in ids]
    def tearDown(self): self.c.STORAGE.db.close()
    def item(self, initiative=None, active=False):
        return {'id': 'a', 'name': 'Alpha', 'initiative': initiative, 'active': active}
    def model(self, **values): return SimpleNamespace(model_dump=lambda **kwargs: values)
    def update_handler(self, kind):
        async def update(ident, update):
            self.c.STORAGE.db.execute('INSERT INTO writes VALUES (1)')
            self.c.STATE[kind][0].update(update.model_dump())
        update.__name__ = 'update_character' if kind == 'characters' else 'update_monster'
        return update
    def test_individual_join_without_initiative_rejected_for_both_kinds(self):
        for kind in ('characters', 'monsters'):
            self.c.STATE[kind] = [self.item()]
            before = copy.deepcopy(self.c.STATE)
            with self.assertRaises(HTTPError) as error:
                asyncio.run(transactional_handler(self.c, self.update_handler(kind))('a', self.model(active=True)))
            self.assertEqual(error.exception.status_code, 400)
            self.assertEqual(self.c.STATE, before)
            self.assertEqual(self.c.STORAGE.db.execute('SELECT count(*) FROM writes').fetchone()[0], 0)
    def test_zero_negative_and_positive_are_valid(self):
        for value in (0, -2, 15):
            self.c.STATE['characters'] = [self.item()]
            asyncio.run(transactional_handler(self.c, self.update_handler('characters'))('a', self.model(active=True, initiative=value)))
            self.assertTrue(self.c.STATE['characters'][0]['active'])
    def test_bulk_join_is_atomic_for_both_kinds(self):
        for kind in ('characters', 'monsters'):
            self.c.STATE[kind] = [self.item(12), {'id': 'b', 'name': 'Beta', 'active': False, 'initiative': None}]
            async def bulk(body):
                for item in self.c.STATE[kind]: item['active'] = True
            bulk.__name__ = 'bulk_characters' if kind == 'characters' else 'bulk_monsters'
            before = copy.deepcopy(self.c.STATE)
            with self.assertRaises(HTTPError) as error:
                asyncio.run(transactional_handler(self.c, bulk)(SimpleNamespace(action='join-battle', ids=['a', 'b'])))
            self.assertIn('Beta', error.exception.detail)
            self.assertEqual(self.c.STATE, before)
    def test_leaving_without_initiative_is_allowed(self):
        self.c.STATE['characters'] = [self.item(active=True)]
        asyncio.run(transactional_handler(self.c, self.update_handler('characters'))('a', self.model(active=False)))
        self.assertFalse(self.c.STATE['characters'][0]['active'])
    def test_cannot_clear_initiative_while_active(self):
        self.c.STATE['monsters'] = [self.item(12, True)]
        with self.assertRaises(HTTPError):
            asyncio.run(transactional_handler(self.c, self.update_handler('monsters'))('a', self.model(initiative=None)))
        self.assertEqual(self.c.STATE['monsters'][0]['initiative'], 12)
    def test_can_leave_and_clear_in_one_update(self):
        self.c.STATE['monsters'] = [self.item(12, True)]
        asyncio.run(transactional_handler(self.c, self.update_handler('monsters'))('a', self.model(active=False, initiative=None)))
        self.assertIsNone(self.c.STATE['monsters'][0]['initiative'])
    def test_edit_transition_failure_rolls_back_database_and_state(self):
        self.c.STATE['monsters'] = [self.item(12, True)]
        async def edit_monster():
            self.c.STATE['monsters'][0]['initiative'] = None
            self.c.STORAGE.db.execute('INSERT INTO writes VALUES (1)')
        with self.assertRaises(HTTPError): asyncio.run(transactional_handler(self.c, edit_monster)())
        self.assertEqual(self.c.STATE['monsters'][0]['initiative'], 12)
        self.assertEqual(self.c.STORAGE.db.execute('SELECT count(*) FROM writes').fetchone()[0], 0)
    def test_imported_active_missing_initiative_is_rejected(self):
        async def import_monsters_csv(): self.c.STATE['monsters'].append(self.item(active=True))
        with self.assertRaises(HTTPError): asyncio.run(transactional_handler(self.c, import_monsters_csv)())
        self.assertEqual(self.c.STATE['monsters'], [])
    def test_battle_start_rejects_legacy_active_missing_initiative(self):
        self.c.STATE['characters'] = [self.item(active=True)]
        async def battle_start(payload): pass
        with self.assertRaises(HTTPError): asyncio.run(transactional_handler(self.c, battle_start)(None))
    def test_invalid_initiative_types_are_not_entered_numbers(self):
        for value in (None, '', '12', True, 1.5):
            self.c.STATE['monsters'] = [self.item(value)]
            with self.assertRaises(HTTPError):
                asyncio.run(transactional_handler(self.c, self.update_handler('monsters'))('a', self.model(active=True)))

if __name__ == '__main__': unittest.main()
