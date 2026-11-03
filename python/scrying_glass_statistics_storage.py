"""Schema 8: normalized attack-reduction fields on combatant effect rows."""


def upgrade_statistics(storage, *, backup=True):
    db = storage.connection
    if db.execute('PRAGMA user_version').fetchone()[0] >= 8:
        return
    if backup and storage.migration_backup is None:
        storage._backup()
    with storage.transaction():
        for table in ('characters', 'monsters', 'snapshot_characters'):
            db.execute(f'ALTER TABLE {table}_effects ADD COLUMN mechanical_version INTEGER')
            db.execute(f'ALTER TABLE {table}_effects ADD COLUMN reduction_stat TEXT')
            db.execute(f'ALTER TABLE {table}_effects ADD COLUMN reduction_amount INTEGER')
        db.execute('PRAGMA user_version=8')
