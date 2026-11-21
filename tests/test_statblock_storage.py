"""022.02b foundation: real SQLite protocol fixtures, not startup integration."""
import contextlib
import copy
import sqlite3
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch
from python import scrying_glass_statblock_storage as subject


class Fixture:
    def __init__(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'fixture.sqlite3'
        self.migration_backup = None
        self.reopen()
        self.connection.execute('CREATE TABLE monsters(id INTEGER PRIMARY KEY, hp INTEGER)')
        self.connection.executemany('INSERT INTO monsters VALUES(?,10)', [(1,), (2,)])
        self.connection.execute('PRAGMA user_version=8')

    def reopen(self):
        self.connection = sqlite3.connect(self.path, isolation_level=None)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute('PRAGMA foreign_keys=ON')

    @contextlib.contextmanager
    def transaction(self):
        name = 'test_' + uuid.uuid4().hex
        self.connection.execute(f'SAVEPOINT {name}')
        try:
            yield
            self.connection.execute(f'RELEASE {name}')
        except BaseException:
            self.connection.execute(f'ROLLBACK TO {name}')
            self.connection.execute(f'RELEASE {name}')
            raise

    def _check_foreign_keys(self):
        if list(self.connection.execute('PRAGMA foreign_key_check')):
            raise RuntimeError('Foreign-key violations')

    def _backup(self):
        self.migration_backup = self.path.with_suffix('.bak')
        with contextlib.closing(sqlite3.connect(self.migration_backup)) as destination:
            self.connection.backup(destination)

    def close(self):
        self.connection.close()
        self.temp.cleanup()


def sample():
    return dict(model_version=1, source_label='Source', subtitle='', completeness='available',
        definitions=[], facts=[], warnings=[],
        provenance=[dict(position=0, role='selected', provider='file', entity_id='sample',
            adapter_version='1', credits=[dict(position=0, attribution='Publisher', license_name=None)])],
        nodes=[dict(local_id='p', parent_local_id=None, definition_id=None, position=0, kind='paragraph'),
            dict(local_id='t', parent_local_id='p', definition_id=None, position=0, kind='text', text='Safe text', enabled=False)])


class SchemaTests(unittest.TestCase):
    def setUp(self):
        self.f = Fixture()
        self.addCleanup(self.f.close)

    def header(self, monster=1):
        return self.f.connection.execute("INSERT INTO monster_statblocks(monster_id,model_version,revision,source_label,subtitle,completeness,prepared_at,content_digest) VALUES (?,1,1,'Source','','available','2026-11-15T00:00:00Z',?)", (monster, 'a'*64)).lastrowid

    def test_upgrade_backup_idempotence_reopen(self):
        subject.upgrade_statblocks(self.f)
        with contextlib.closing(sqlite3.connect(self.f.migration_backup)) as backup:
            self.assertEqual(backup.execute('PRAGMA user_version').fetchone()[0], 8)
        self.f.connection.close()
        self.f.reopen()
        subject.upgrade_statblocks(self.f)
        self.assertEqual(self.f.connection.execute('PRAGMA user_version').fetchone()[0], 9)
        tables = list(self.f.connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%statblock%'"))
        self.assertEqual(len(tables), 7)
        for row in tables:
            columns = list(self.f.connection.execute(f'PRAGMA table_info({row[0]})'))
            self.assertIn('id', [c[1] for c in columns])
            self.assertFalse(any('json' in c[1].lower() for c in columns))
        self.f._check_foreign_keys()

    def test_wrong_versions_and_failed_migration(self):
        for version in (0, 7, 10):
            self.f.connection.execute(f'PRAGMA user_version={version}')
            with self.assertRaises(RuntimeError): subject.upgrade_statblocks(self.f)
        self.f.connection.execute('PRAGMA user_version=8')
        original = subject.create_statblock_schema
        def fail(db):
            original(db)
            raise OSError('injected')
        with patch.object(subject, 'create_statblock_schema', side_effect=fail):
            with self.assertRaises(OSError): subject.upgrade_statblocks(self.f)
        self.assertEqual(self.f.connection.execute('PRAGMA user_version').fetchone()[0], 8)
        self.assertFalse(list(self.f.connection.execute("SELECT name FROM sqlite_master WHERE name='monster_statblocks'")))
        subject.upgrade_statblocks(self.f)

    def test_null_owner_positions_and_delete_cascade(self):
        subject.upgrade_statblocks(self.f)
        ident = self.header()
        fact = dict(position=0, key='str', label='STR', display_text='18')
        subject._insert(self.f.connection, 'facts', ident, fact, {})
        with self.assertRaises(sqlite3.IntegrityError): subject._insert(self.f.connection, 'facts', ident, fact, {})
        p = sample()['provenance'][0]
        parent = subject._insert(self.f.connection, 'provenance', ident, p, {})
        subject._insert(self.f.connection, 'credits', parent, p['credits'][0], {})
        self.f.connection.execute('DELETE FROM monsters WHERE id=1')
        for table in ('monster_statblocks', 'statblock_facts', 'statblock_provenance', 'statblock_credits'):
            self.assertEqual(self.f.connection.execute(f'SELECT count(*) FROM {table}').fetchone()[0], 0)

    def test_cross_snapshot_definition_and_cross_owner_parent(self):
        subject.upgrade_statblocks(self.f)
        a, b = self.header(), self.header(2)
        definition = dict(local_id='d', kind='spell', name='Spell', source_key='spell', position=0)
        did = subject._insert(self.f.connection, 'definitions', a, definition, {})
        root = sample()['nodes'][0]
        subject._insert(self.f.connection, 'nodes', a, root, {})
        for statblock, record in ((b, dict(position=0, key='str', label='', display_text='', definition_id='d')),
                                 (a, dict(root, local_id='child', parent_local_id='p', definition_id='d'))):
            with self.assertRaises(RuntimeError):
                with self.f.transaction():
                    subject._insert(self.f.connection, 'facts' if statblock == b else 'nodes', statblock, record, {'d': did})
                    self.f._check_foreign_keys()
        self.f._check_foreign_keys()


class RepositoryTests(unittest.TestCase):
    def setUp(self):
        self.f = Fixture()
        self.addCleanup(self.f.close)
        subject.upgrade_statblocks(self.f)
        self.api = subject.StatblockStorage(self.f)

    def test_roundtrip_revision_reopen_and_tracker_independence(self):
        self.assertIsNone(self.api.load(1))
        saved = self.api.save(1, sample(), expected_revision=0)
        self.assertEqual(self.api.load(1), saved)
        self.f.connection.close()
        self.f.reopen()
        self.api = subject.StatblockStorage(self.f)
        self.assertEqual(self.api.load(1), saved)
        other = self.api.save(2, sample(), expected_revision=0)
        self.f.connection.execute('UPDATE monsters SET hp=2 WHERE id=1')
        updated = self.api.save(1, saved, expected_revision=1)
        self.assertEqual(updated['revision'], 2)
        self.assertEqual(updated['content_digest'], saved['content_digest'])
        self.assertEqual(self.api.load(2), other)
        self.assertEqual(self.f.connection.execute('SELECT hp FROM monsters WHERE id=1').fetchone()[0], 2)
        with self.assertRaises(ValueError): self.api.save(1, sample(), expected_revision=1)
        self.assertEqual(self.api.load(1), updated)

    def test_invalid_content_and_failed_replacement_rollback(self):
        saved = self.api.save(1, sample(), expected_revision=0)
        broken = sample()
        broken['nodes'][0]['parent_local_id'] = 'p'
        with self.assertRaises(ValueError): self.api.save(1, broken, expected_revision=1)
        with patch.object(subject, '_insert', side_effect=OSError('injected')):
            with self.assertRaises(OSError): self.api.save(1, sample(), expected_revision=1)
        self.assertEqual(self.api.load(1), saved)
        with self.assertRaises(RuntimeError):
            with self.f.transaction():
                self.api.save(1, sample(), expected_revision=1)
                raise RuntimeError('outer rollback')
        self.assertEqual(self.api.load(1), saved)
        for monster, revision in ((True, 0), (999, 0), (1, True)):
            with self.assertRaises(ValueError): self.api.save(monster, sample(), expected_revision=revision)

    def test_supporting_references_and_optional_presence(self):
        value = sample()
        value['definitions'] = [dict(local_id='d', kind='spell', name='Spell', source_key='spell', position=0)]
        value['facts'] = [dict(position=0, key='ac', label='AC', display_text='10', definition_id='d')]
        value['nodes'] += [dict(local_id='dp', kind='paragraph', parent_local_id=None, definition_id='d', position=0),
            dict(local_id='r', kind='reference', parent_local_id='dp', definition_id='d', position=0, target_definition_local_id='d')]
        saved = self.api.save(1, value, expected_revision=0)
        self.assertEqual(self.api.load(1), saved)
        self.assertNotIn('integer_value', saved['facts'][0])
        self.assertIsNone(saved['provenance'][0]['credits'][0]['license_name'])
        self.assertIs(saved['nodes'][1]['enabled'], False)
        self.f.connection.execute('DELETE FROM monsters WHERE id=1')
        self.assertIsNone(self.api.load(1))
        self.f._check_foreign_keys()

    def test_saved_content_survives_lower_default_limits(self):
        from python.scrying_glass_statblock_model import ModelLimits
        value = sample()
        value['nodes'][1]['text'] = 'x'*70000
        saved = self.api.save(1, value, expected_revision=0, limits=ModelLimits(text_value_bytes=80000))
        self.assertEqual(self.api.load(1), saved)


if __name__ == '__main__':
    unittest.main()
