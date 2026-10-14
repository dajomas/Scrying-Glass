"""Persist encounter-owned Lair-pane availability (schema v7)."""

def upgrade_setup_lair(storage, *, backup=True):
    db = storage.connection
    if db.execute("PRAGMA user_version").fetchone()[0] >= 7:
        return
    if backup and storage.migration_backup is None:
        storage._backup()
    with storage.transaction():
        db.execute("ALTER TABLE encounters ADD COLUMN has_lair INTEGER NOT NULL DEFAULT 0 CHECK(has_lair IN (0,1))")
        db.execute("UPDATE encounters SET has_lair=1 WHERE id IN (SELECT encounter_id FROM lairs)")
        db.execute("PRAGMA user_version=7")

async def update_setup_lair(context, body):
    """Reject stale-scope writes and change only pane availability."""
    if set(body) != {"has_lair", "scope"} or type(body.get("has_lair")) is not bool:
        raise context.HTTPException(422, "Expected boolean has_lair and encounter scope")
    scope = {"campaign_id": context.active_campaign(), "setup": context.STATE.get("active_setup")}
    if body["scope"] != scope:
        raise context.HTTPException(409, "The active campaign or setup changed; retry")
    context.STATE["has_lair"] = body["has_lair"]
    context.save_active_setup_monsters()
    await context.changed()
    return {"has_lair": context.STATE["has_lair"]}
