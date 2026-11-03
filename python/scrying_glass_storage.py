"""SQLiteStorage compatibility facade; native schema, records and operations mixins."""
from __future__ import annotations
import copy
import json
import sqlite3
import time
import uuid
from contextlib import contextmanager, closing
from pathlib import Path
from .scrying_glass_identity_rules import validate_roster_setup_ids
from .scrying_glass_storage_fields import (
    TEXT_FIELDS, INT_FIELDS, BOOL_FIELDS, ENTITY_FIELDS, LOG_FIELDS, LIST_FIELDS, STATE_FIELDS,
)
from .scrying_glass_storage_schema import StorageSchemaMixin
from .scrying_glass_storage_records import StorageRecordsMixin
from .scrying_glass_storage_operations import StorageOperationsMixin


class SQLiteStorage(StorageSchemaMixin, StorageRecordsMixin, StorageOperationsMixin):
    SCHEMA_VERSION = 8

    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        self.migration_backup = None
        try:
            self.connection.row_factory = sqlite3.Row
            self.connection.execute("PRAGMA foreign_keys=ON")
            self.connection.execute("PRAGMA busy_timeout=10000")
            version = self.connection.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, 1, 2, 3, 4, 5, 6, 7, 8):
                raise RuntimeError(f"Unsupported schema version: {version}")
            if version == 0:
                if self.connection.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchone():
                    raise RuntimeError("Nonempty unversioned database; refusing to overwrite")
                with self.transaction():
                    self._create_schema()
                    self.connection.execute("PRAGMA user_version=3")
            elif version in (1, 2):
                self._backup()
                self._upgrade(version)
            if version not in (4, 5, 6, 7, 8):
                if version == 3:
                    self._backup()
                with self.transaction():
                    self.connection.execute("CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, role TEXT NOT NULL CHECK(role IN ('superadmin','admin','client')), password_hash TEXT NOT NULL)")
                    self.connection.execute("CREATE TABLE account_migration (id INTEGER PRIMARY KEY CHECK(id=1), completed INTEGER NOT NULL CHECK(completed=1))")
                    self.connection.execute("PRAGMA user_version=4")
            from .scrying_glass_feature_storage import upgrade_features
            upgrade_features(self, backup=version != 0)
            from .scrying_glass_lair_storage import upgrade_lairs
            upgrade_lairs(self, backup=version != 0)
            from .scrying_glass_setup_lair import upgrade_setup_lair
            upgrade_setup_lair(self, backup=version != 0)
            from .scrying_glass_statistics_storage import upgrade_statistics
            upgrade_statistics(self, backup=version != 0)
            self._check_foreign_keys()
        except BaseException:
            self.close()
            raise

    @contextmanager
    def transaction(self):
        if self.connection.in_transaction:
            savepoint = "nested_" + uuid.uuid4().hex
            self.connection.execute(f"SAVEPOINT {savepoint}")
            try:
                yield self
                self.connection.execute(f"RELEASE SAVEPOINT {savepoint}")
            except BaseException:
                self.connection.execute(f"ROLLBACK TO SAVEPOINT {savepoint}")
                self.connection.execute(f"RELEASE SAVEPOINT {savepoint}")
                raise
            return
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            yield self
            self.connection.execute("COMMIT")
        except BaseException:
            if self.connection.in_transaction:
                self.connection.execute("ROLLBACK")
            raise

    def close(self): self.connection.close()

    def _check_foreign_keys(self):
        rows = list(self.connection.execute("PRAGMA foreign_key_check"))
        if rows: raise RuntimeError(f"Foreign-key violations: {[tuple(r) for r in rows]}")

    def _backup(self):
        target = self.path.with_name(self.path.name + ".before-normalization.bak")
        number = 2
        while target.exists():
            target = self.path.with_name(self.path.name + f".before-normalization-{number}.bak")
            number += 1
        with closing(sqlite3.connect(target)) as destination, destination:
            self.connection.backup(destination)
        self.migration_backup = target
