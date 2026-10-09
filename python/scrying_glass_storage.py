"""SQLite persistence; one connection owned by the single server event loop."""
from __future__ import annotations
import json
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path

class SQLiteStorage:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(path, timeout=10, isolation_level=None)
        self.connection.execute("PRAGMA foreign_keys=ON")
        self.connection.execute("PRAGMA busy_timeout=10000")
        version = self.connection.execute("PRAGMA user_version").fetchone()[0]
        if version not in (0, 1):
            self.close()
            raise RuntimeError(f"Unsupported database schema version: {version}")
        with self.transaction():
            self.connection.execute("CREATE TABLE IF NOT EXISTS campaigns (slug TEXT PRIMARY KEY, metadata_json TEXT NOT NULL)")
            self.connection.execute("CREATE TABLE IF NOT EXISTS campaign_characters (campaign_slug TEXT PRIMARY KEY REFERENCES campaigns(slug) ON UPDATE CASCADE ON DELETE CASCADE, characters_json TEXT NOT NULL)")
            self.connection.execute("CREATE TABLE IF NOT EXISTS battle_setups (campaign_slug TEXT NOT NULL REFERENCES campaigns(slug) ON UPDATE CASCADE ON DELETE CASCADE, name TEXT NOT NULL, snapshot_json TEXT NOT NULL, updated_at REAL NOT NULL, PRIMARY KEY(campaign_slug,name))")
            self.connection.execute("CREATE TABLE IF NOT EXISTS application_state (key TEXT PRIMARY KEY, value_json TEXT NOT NULL)")
            self.connection.execute("PRAGMA user_version=1")

    @contextmanager
    def transaction(self):
        nested = self.connection.in_transaction
        if nested:
            yield self
            return
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            yield self
            self.connection.execute("COMMIT")
        except BaseException:
            if self.connection.in_transaction:
                self.connection.execute("ROLLBACK")
            raise

    def close(self):
        self.connection.close()

    def get_value(self, key, default=None):
        row = self.connection.execute("SELECT value_json FROM application_state WHERE key=?", (key,)).fetchone()
        return json.loads(row[0]) if row else default

    def set_value(self, key, value):
        self.connection.execute("INSERT INTO application_state VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value_json=excluded.value_json", (key,json.dumps(value,allow_nan=False)))

    def read_campaigns(self):
        return {"active": self.get_value("active_campaign"), "campaigns": {slug: json.loads(raw) for slug,raw in self.connection.execute("SELECT slug,metadata_json FROM campaigns")}}

    def write_campaigns(self, data):
        with self.transaction():
            existing = set(self.read_campaigns()["campaigns"])
            for slug,meta in data["campaigns"].items():
                self.connection.execute("INSERT INTO campaigns VALUES (?,?) ON CONFLICT(slug) DO UPDATE SET metadata_json=excluded.metadata_json", (slug,json.dumps(meta,allow_nan=False)))
            for slug in existing-set(data["campaigns"]):
                self.connection.execute("DELETE FROM campaigns WHERE slug=?", (slug,))
            self.set_value("active_campaign",data["active"])

    def rename_campaign(self, old, new):
        self.connection.execute("UPDATE campaigns SET slug=? WHERE slug=?",(new,old))

    def load_characters(self, campaign):
        row=self.connection.execute("SELECT characters_json FROM campaign_characters WHERE campaign_slug=?",(campaign,)).fetchone()
        return json.loads(row[0]) if row else None

    def save_characters(self, campaign, characters):
        self.connection.execute("INSERT INTO campaign_characters VALUES (?,?) ON CONFLICT(campaign_slug) DO UPDATE SET characters_json=excluded.characters_json",(campaign,json.dumps(characters,allow_nan=False)))

    def list_setups(self, campaign):
        return sorted((r[0] for r in self.connection.execute("SELECT name FROM battle_setups WHERE campaign_slug=?",(campaign,))), key=str.casefold)

    def setup_exists(self, campaign, name):
        return self.connection.execute("SELECT 1 FROM battle_setups WHERE campaign_slug=? AND name=?",(campaign,name)).fetchone() is not None

    def load_setup(self, campaign, name):
        row=self.connection.execute("SELECT snapshot_json FROM battle_setups WHERE campaign_slug=? AND name=?",(campaign,name)).fetchone()
        if row is None: raise FileNotFoundError(f"Saved setup not found: {campaign}/{name}")
        return json.loads(row[0])

    def save_setup(self, campaign, name, snapshot, updated_at=None):
        self.connection.execute("INSERT INTO battle_setups VALUES (?,?,?,?) ON CONFLICT(campaign_slug,name) DO UPDATE SET snapshot_json=excluded.snapshot_json,updated_at=excluded.updated_at",(campaign,name,json.dumps(snapshot,allow_nan=False),time.time() if updated_at is None else updated_at))

    def rename_setup(self, campaign, old, new):
        self.connection.execute("UPDATE battle_setups SET name=? WHERE campaign_slug=? AND name=?",(new,campaign,old))

    def delete_setup(self, campaign, name):
        self.connection.execute("DELETE FROM battle_setups WHERE campaign_slug=? AND name=?",(campaign,name))

    def unique_setup_name(self, campaign, name):
        result=name;index=2
        while self.setup_exists(campaign,result):
            result=f"{name}-{index}";index+=1
        return result

    def transfer_setup(self, source, target, name, mode):
        with self.transaction():
            result=self.unique_setup_name(target,name)
            row=self.connection.execute("SELECT snapshot_json,updated_at FROM battle_setups WHERE campaign_slug=? AND name=?",(source,name)).fetchone()
            if row is None: raise FileNotFoundError(name)
            self.save_setup(target,result,json.loads(row[0]),row[1])
            if mode == "move": self.delete_setup(source,name)
            return result

    def newest_setup(self,campaign):
        rows=list(self.connection.execute("SELECT name,updated_at FROM battle_setups WHERE campaign_slug=?",(campaign,)))
        return min(rows,key=lambda r:(-r[1],r[0].casefold()))[0] if rows else None
