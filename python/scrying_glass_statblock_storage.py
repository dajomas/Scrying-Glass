"""022.02b storage foundation. Schema upgrade is callable, not startup-wired yet."""
from datetime import datetime, timezone

FIELDS = {
    'definitions': ('local_id kind name source_key position', 'source_code'),
    'provenance': ('position role provider entity_id adapter_version', 'definition_id endpoint api_version source_code edition source_url file_name file_sha256'),
    'credits': ('position attribution', 'publisher license_name license_url'),
    'facts': ('position key label display_text', 'definition_id integer_value'),
    'nodes': ('local_id parent_local_id definition_id position kind', 'text url target_definition_local_id source_path label enabled ordered'),
    'warnings': ('position code message', 'definition_id source_path'),
}
HEADER = 'model_version revision source_label subtitle completeness prepared_at content_digest'.split()
INTEGER = {'position', 'integer_value', 'enabled', 'ordered', 'definition_id'}
NULLABLE = {'parent_local_id', 'definition_id'}


def create_statblock_schema(db):
    db.execute("""CREATE TABLE monster_statblocks (
        id INTEGER PRIMARY KEY, monster_id INTEGER NOT NULL UNIQUE REFERENCES monsters(id) ON DELETE CASCADE,
        model_version INTEGER NOT NULL CHECK(model_version=1),
        revision INTEGER NOT NULL CHECK(typeof(revision)='integer' AND revision>=1),
        source_label TEXT NOT NULL, subtitle TEXT NOT NULL,
        completeness TEXT NOT NULL CHECK(completeness IN ('available','partial')),
        prepared_at TEXT NOT NULL, content_digest TEXT NOT NULL CHECK(length(content_digest)=64))""")
    for kind, (required, optional) in FIELDS.items():
        parent = 'provenance_id' if kind == 'credits' else 'statblock_id'
        relation = 'statblock_provenance' if kind == 'credits' else 'monster_statblocks'
        columns = ['id INTEGER PRIMARY KEY CHECK(id>0)',
                   f'{parent} INTEGER NOT NULL REFERENCES {relation}(id) ON DELETE CASCADE',
                   'present INTEGER NOT NULL CHECK(present>=0)']
        for key in (required + ' ' + optional).split():
            declaration = key + (' INTEGER' if key in INTEGER else ' TEXT')
            if key in required.split() and key not in NULLABLE:
                declaration += ' NOT NULL'
            if key == 'position':
                declaration += " CHECK(typeof(position)='integer' AND position>=0)"
            if key in {'enabled', 'ordered'}:
                declaration += f' CHECK({key} IS NULL OR {key} IN (0,1))'
            if key == 'local_id':
                declaration += " CHECK(length(local_id)>0)"
            columns.append(declaration)
        if kind == 'definitions':
            columns += ['UNIQUE(statblock_id,id)', 'UNIQUE(statblock_id,local_id)',
                        'UNIQUE(statblock_id,position)', 'UNIQUE(statblock_id,kind,source_key)']
        if kind == 'nodes':
            columns.append('owner_key INTEGER NOT NULL CHECK(owner_key=coalesce(definition_id,0))')
        if kind in {'nodes', 'facts', 'provenance', 'warnings'}:
            columns.append('FOREIGN KEY(statblock_id,definition_id) REFERENCES statblock_definitions(statblock_id,id) DEFERRABLE INITIALLY DEFERRED')
        if kind == 'provenance':
            columns.append("CHECK(role IN ('selected','base','template','reference'))")
        if kind == 'nodes':
            columns += ['UNIQUE(statblock_id,local_id)', 'UNIQUE(statblock_id,owner_key,local_id)',
                        'FOREIGN KEY(statblock_id,owner_key,parent_local_id) REFERENCES statblock_nodes(statblock_id,owner_key,local_id) DEFERRABLE INITIALLY DEFERRED',
                        'FOREIGN KEY(statblock_id,target_definition_local_id) REFERENCES statblock_definitions(statblock_id,local_id) DEFERRABLE INITIALLY DEFERRED']
        db.execute(f"CREATE TABLE statblock_{kind} ({','.join(columns)})")
        if kind in {'nodes', 'facts', 'provenance', 'warnings'}:
            sibling = ",coalesce(parent_local_id,'')" if kind == 'nodes' else ''
            db.execute(f'CREATE UNIQUE INDEX statblock_{kind}_positions ON statblock_{kind}(statblock_id,coalesce(definition_id,0){sibling},position)')
        elif kind == 'credits':
            db.execute('CREATE UNIQUE INDEX statblock_credits_positions ON statblock_credits(provenance_id,position)')
    db.execute("CREATE UNIQUE INDEX statblock_selected ON statblock_provenance(statblock_id) WHERE role='selected'")


def upgrade_statblocks(storage, *, backup=True):
    """Upgrade exactly v8 to v9 atomically; reuse an earlier upgrade-chain backup."""
    db = storage.connection
    version = db.execute('PRAGMA user_version').fetchone()[0]
    if version == 9:
        return
    if version != 8:
        raise RuntimeError(f'Statblocks require schema 8, got {version}')
    storage._check_foreign_keys()
    if backup and storage.migration_backup is None:
        storage._backup()
    with storage.transaction():
        create_statblock_schema(db)
        storage._check_foreign_keys()
        db.execute('PRAGMA user_version=9')


def _insert(db, kind, parent, record, definitions):
    required, optional = (part.split() for part in FIELDS[kind])
    keys = required + optional
    values = [record.get(key) for key in keys]
    if 'definition_id' in keys:
        i = keys.index('definition_id')
        values[i] = definitions[values[i]] if values[i] is not None else None
    if kind == 'nodes':
        keys.append('owner_key')
        values.append(values[keys.index('definition_id')] or 0)
    owner = 'provenance_id' if kind == 'credits' else 'statblock_id'
    keys += [owner, 'present']
    values += [parent, sum(1 << i for i, key in enumerate(optional) if key in record)]
    return db.execute(f"INSERT INTO statblock_{kind}({','.join(keys)}) VALUES ({','.join('?' for _ in keys)})", values).lastrowid


def _record(kind, row, definitions):
    required, optional = (part.split() for part in FIELDS[kind])
    keys = required + [key for i, key in enumerate(optional) if row['present'] & (1 << i)]
    result = {key: row[key] for key in keys}
    if result.get('definition_id') is not None:
        result['definition_id'] = definitions[result['definition_id']]
    for key in ('enabled', 'ordered'):
        if result.get(key) is not None:
            result[key] = bool(result[key])
    return result


class StatblockStorage:
    """Internal stored-monsters.id API, not a public authorization boundary.

    Callers own campaign/encounter authorization. No runtime/export integration yet.
    Optional-field presence is a scalar bitmask, preserving absent versus null.
    """
    def __init__(self, storage):
        self.storage = storage
        self.db = storage.connection

    def save(self, monster_id, snapshot, *, expected_revision, limits=None):
        from .scrying_glass_statblock_model import validate_snapshot, canonical_bytes, content_digest
        import json
        if type(monster_id) is not int or not 0 < monster_id < 2**63:
            raise ValueError('Invalid stored monster ID')
        if type(expected_revision) is not int or not 0 <= expected_revision < 2**63-1:
            raise ValueError('Invalid expected revision')
        value = json.loads(canonical_bytes(snapshot, limits))
        value['revision'] = expected_revision + 1
        value.setdefault('prepared_at', datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))
        value['content_digest'] = content_digest(value, limits)
        value = validate_snapshot(value, limits)
        with self.storage.transaction():
            if not self.db.execute('SELECT 1 FROM monsters WHERE id=?', (monster_id,)).fetchone():
                raise ValueError('Stored monster not found')
            row = self.db.execute('SELECT revision FROM monster_statblocks WHERE monster_id=?', (monster_id,)).fetchone()
            if (row[0] if row else 0) != expected_revision:
                raise ValueError('Stale statblock revision')
            self.db.execute('DELETE FROM monster_statblocks WHERE monster_id=?', (monster_id,))
            ident = self.db.execute(f"INSERT INTO monster_statblocks(monster_id,{','.join(HEADER)}) VALUES ({','.join('?' for _ in range(len(HEADER)+1))})", [monster_id] + [value[k] for k in HEADER]).lastrowid
            definitions = {}
            for record in value['definitions']:
                definitions[record['local_id']] = _insert(self.db, 'definitions', ident, record, {})
            for kind in ('facts', 'nodes', 'warnings', 'provenance'):
                for record in value[kind]:
                    parent = _insert(self.db, kind, ident, record, definitions)
                    if kind == 'provenance':
                        for credit in record['credits']:
                            _insert(self.db, 'credits', parent, credit, {})
            self.storage._check_foreign_keys()
        return value

    def load(self, monster_id):
        from .scrying_glass_statblock_model import validate_snapshot, ModelLimits
        with self.storage.transaction():
            header = self.db.execute('SELECT * FROM monster_statblocks WHERE monster_id=?', (monster_id,)).fetchone()
            if header is None:
                return None
            value = {key: header[key] for key in HEADER}
            ident = header['id']
            definitions = {r['id']: r['local_id'] for r in self.db.execute('SELECT id,local_id FROM statblock_definitions WHERE statblock_id=?', (ident,))}
            for kind in ('definitions', 'facts', 'nodes', 'warnings', 'provenance'):
                value[kind] = []
                for row in self.db.execute(f'SELECT * FROM statblock_{kind} WHERE statblock_id=? ORDER BY id', (ident,)):
                    record = _record(kind, row, definitions)
                    if kind == 'provenance':
                        record['credits'] = [_record('credits', credit, {}) for credit in self.db.execute('SELECT * FROM statblock_credits WHERE provenance_id=? ORDER BY position', (row['id'],))]
                    value[kind].append(record)
        # Configuration reductions must not make previously accepted saved content unreadable.
        read_limits = ModelLimits(**{name: 2**63-1 for name in ModelLimits.__dataclass_fields__})
        return validate_snapshot(value, read_limits)
