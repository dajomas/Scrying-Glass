"""Private stored-monster revision counters; no schema or clear API changes."""
REVISION_FIELD = '__sg_statblock_revision'
REVISION_KIND = 'statblock_revision_v1'
MAX_REVISION = 2**63 - 1


def _integer(value, minimum=1):
    if type(value) is not int or not minimum <= value <= MAX_REVISION:
        raise ValueError('Invalid private statblock revision or owner')
    return value


def _ledger(row):
    if row['value_kind'] != 'integer' or row['text_value'] != REVISION_KIND or row['real_value'] is not None:
        raise ValueError('Invalid private statblock revision ledger')
    return _integer(row['integer_value'])


def revision_head(db, monster):
    _integer(monster)
    row = db.execute('SELECT * FROM monsters_attributes WHERE parent_id=? AND field_name=?',
                     (monster, REVISION_FIELD)).fetchone()
    counter = _ledger(row) if row else 0
    header = db.execute('SELECT revision FROM monster_statblocks WHERE monster_id=?', (monster,)).fetchone()
    return max(counter, _integer(header[0]) if header else 0)


def _store(db, monster, revision):
    _integer(monster); _integer(revision)
    db.execute("INSERT INTO monsters_attributes(parent_id,field_name,value_kind,text_value,integer_value) VALUES (?,?,'integer',?,?) "
               'ON CONFLICT(parent_id,field_name) DO UPDATE SET value_kind=excluded.value_kind,'
               'text_value=excluded.text_value,integer_value=excluded.integer_value,real_value=NULL',
               (monster, REVISION_FIELD, REVISION_KIND, revision))


def next_revision(db, monster):
    revision = revision_head(db, monster)
    if revision == MAX_REVISION: raise ValueError('Statblock revision limit reached')
    return revision + 1


def record_revision(db, monster, revision):
    _integer(revision)
    if revision < revision_head(db, monster): raise ValueError('Statblock revision cannot decrease')
    _store(db, monster, revision)


class StatblockRevisionMixin:
    """Caller owns transactions. Ordinary state never supplies or exports counters."""
    def _statblock_revision_head(self, monster):
        return revision_head(self.connection, monster)

    def _next_statblock_revision(self, monster):
        return next_revision(self.connection, monster)

    def _record_statblock_revision(self, monster, revision):
        record_revision(self.connection, monster, revision)

    def _attributes(self, table, parent, extras, present=()):
        if table != 'monsters': return super()._attributes(table, parent, extras, present=present)
        if REVISION_FIELD in extras or REVISION_FIELD in present:
            raise ValueError('Reserved private statblock revision attribute')
        row = self.connection.execute('SELECT * FROM monsters_attributes WHERE parent_id=? AND field_name=?',
                                      (parent, REVISION_FIELD)).fetchone()
        counter = _ledger(row) if row else None
        if counter is not None: extras = {**extras, REVISION_FIELD:counter}
        result = super()._attributes(table, parent, extras, present=present)
        if counter is not None: _store(self.connection, parent, counter)
        return result

    def _read_attributes(self, table, parent):
        if table != 'monsters': return super()._read_attributes(table, parent)
        extra, present = {}, set()
        for row in self.connection.execute('SELECT * FROM monsters_attributes WHERE parent_id=?', (parent,)):
            field, kind = row['field_name'], row['value_kind']
            if field == REVISION_FIELD:
                _ledger(row)
                continue
            if kind == 'present': present.add(field)
            elif kind == 'null': extra[field] = None
            elif kind == 'boolean': extra[field] = bool(row['integer_value'])
            else: extra[field] = row[{'text':'text_value','integer':'integer_value','real':'real_value'}[kind]]
        return extra, present
