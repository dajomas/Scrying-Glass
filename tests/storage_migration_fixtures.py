"""Single-threaded migration-test fixtures; never use with deployed storage."""
from unittest.mock import patch


def pre_statblock_storage(factory, path):
    """Construct a genuine v8 fixture before explicitly removing older additions.

    Suppress only the new statblock migration during construction, not the later
    production reopen that the migration test is intended to exercise. Reject a
    hybrid schema rather than silently deleting statblock data or lowering its
    version. The caller must use a disposable fixture path.
    """
    with patch('python.scrying_glass_statblock_storage.upgrade_statblocks', return_value=None):
        storage = factory(path)
    try:
        db = storage.connection
        if db.execute('PRAGMA user_version').fetchone()[0] != 8:
            raise RuntimeError('Expected a pre-statblock schema-8 fixture')
        if db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND (name='monster_statblocks' OR name GLOB 'statblock_*')").fetchone():
            raise RuntimeError('Statblock tables present in pre-statblock fixture')
        return storage
    except BaseException:
        storage.close()
        raise
