"""Superadmin monster-lookup provider toggles (SG-TODO-017 Stage 2).

Configuration keys supply the defaults; a saved toggle overrides its key for
candidate lookup, legacy stats/image lookup and monster refresh. Overrides are
kept in a lazily created table, so databases without saved toggles keep their
existing schema. Lookups run in worker threads, so reads use a short-lived
read-only connection and an in-memory cache rather than the storage connection.
"""
import contextlib
import logging
import sqlite3
import threading
from fastapi import Body, Depends, HTTPException

TABLE = "lookup_provider_settings"
# Provider id, configuration key, default when the key is absent, label.
# Open5e is on through DEFAULT_CONFIG; hand-built configurations without the
# key keep it off so they never contact a new network service unexpectedly.
PROVIDERS = (
    ("dndbeyond", "dndbeyond_image_lookup", True, "D&D Beyond"),
    ("fivetools", "fivetools_fallback", True, "5e.tools"),
    ("open5e", "open5e_lookup", False, "Open5e"),
)
SCHEMA = (f"CREATE TABLE {TABLE} (provider TEXT PRIMARY KEY CHECK(provider IN "
          "('dndbeyond','fivetools','open5e')), enabled INTEGER NOT NULL CHECK(enabled IN (0,1)))")
LOG = logging.getLogger(__name__)
_LOCK = threading.Lock()
_CACHE = {}


def _storage(context):
    storage = getattr(context, "STORAGE", None)
    connection = getattr(storage, "connection", None)
    return storage if isinstance(connection, sqlite3.Connection) else None


def _read(storage):
    path = getattr(storage, "path", None)
    if path is None:
        return {}
    with contextlib.closing(sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=10)) as db:
        if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                          (TABLE,)).fetchone():
            return {}
        return {row[0]: bool(row[1]) for row in db.execute(f"SELECT provider,enabled FROM {TABLE}")}


def overrides(context):
    """Return saved toggles; no storage means configuration only."""
    storage = _storage(context)
    if storage is None:
        return {}
    with _LOCK:
        cached = _CACHE.get(id(storage))
        if cached is not None and cached[0] is storage:
            return dict(cached[1])
    values = _read(storage)
    with _LOCK:
        _CACHE[id(storage)] = (storage, values)
    return dict(values)


def effective_display(context):
    """Configuration display mapping with saved provider toggles applied."""
    display = dict(context.CONFIG["display"])
    try:
        saved = overrides(context)
    except sqlite3.Error:
        # Fail closed: an unreadable toggle must not re-enable a provider.
        LOG.warning("Provider settings unreadable; optional lookups disabled", exc_info=True)
        saved = {provider: False for provider, *_ in PROVIDERS}
    for provider, key, _default, _label in PROVIDERS:
        if provider in saved:
            display[key] = saved[provider]
    return display


def describe(context):
    display = context.CONFIG["display"]
    saved = overrides(context)
    result = []
    for provider, key, default, label in PROVIDERS:
        configured = display.get(key, default) is True
        result.append(dict(provider=provider, label=label, config_key=key,
                           configured=configured, saved=saved.get(provider),
                           enabled=saved.get(provider, configured)))
    return {"providers": result}


def save(context, body):
    names = {provider for provider, *_ in PROVIDERS}
    if (not isinstance(body, dict) or not body or set(body) - names
            or any(type(value) is not bool for value in body.values())):
        raise HTTPException(422, "Expected boolean dndbeyond, fivetools and/or open5e toggles")
    storage = _storage(context)
    if storage is None:
        raise HTTPException(503, "Provider settings storage unavailable")
    db = storage.connection
    if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (TABLE,)).fetchone():
        if storage.migration_backup is None:
            storage._backup()
        with storage.transaction():
            db.execute(SCHEMA)
    with storage.transaction():
        db.executemany(f"INSERT INTO {TABLE}(provider,enabled) VALUES (?,?) "
                       "ON CONFLICT(provider) DO UPDATE SET enabled=excluded.enabled",
                       [(name, int(value)) for name, value in body.items()])
    with _LOCK:
        _CACHE[id(storage)] = (storage, {row[0]: bool(row[1]) for row in
                                         db.execute(f"SELECT provider,enabled FROM {TABLE}")})
    return describe(context)


def install_provider_settings_routes(context, app):
    from .scrying_glass_database_transactions import serialized_handler
    from .scrying_glass_request_security import same_origin
    guard = Depends(context.require("superadmin", context.ADMIN_SESSION_COOKIE))

    def serialize(handler):
        return serialized_handler(context, handler, role="superadmin",
                                  cookie_name=context.ADMIN_SESSION_COOKIE)

    @app.get("/api/settings/lookup-providers", dependencies=[guard])
    async def lookup_providers():
        return describe(context)

    @app.put("/api/settings/lookup-providers", dependencies=[guard, Depends(same_origin)])
    @serialize
    async def update_lookup_providers(body: dict = Body(...)):
        return save(context, body)
