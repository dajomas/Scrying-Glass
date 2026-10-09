"""One-time, non-destructive import of legacy JSON storage."""
from __future__ import annotations
import copy
import json
from pathlib import Path
from typing import Any

class MigrationsService:
    def __init__(self, context: Any):
        self.context = context

    def migrate_unassigned_setups(self) -> list[str]:
        # Legacy reconciliation now occurs only during the one-time import.
        return []

    def migrate_campaign_characters(self) -> None:
        return None

    def import_legacy_storage(self) -> dict[str, int]:
        c = self.context
        db = c.STORAGE
        if db.get_value("legacy_import_complete"):
            return {"campaigns": 0, "setups": 0, "characters": 0}
        if db.read_campaigns()["campaigns"]:
            raise RuntimeError("Database has campaigns but no import marker; refusing to overwrite it")

        def read_json(path: Path):
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, ValueError) as exc:
                raise RuntimeError(f"Cannot import {path}: {exc}") from exc

        registry = read_json(c.DATA_DIR / "campaigns.json") if (c.DATA_DIR / "campaigns.json").exists() else {"active": None, "campaigns": {}}
        if not isinstance(registry, dict) or not isinstance(registry.get("campaigns", {}), dict):
            raise RuntimeError("campaigns.json must contain a campaigns object")
        registry.setdefault("campaigns", {})
        directory = c.DATA_DIR / "setups"
        records = []
        loose = []
        if directory.exists():
            for entry in sorted(directory.iterdir(), key=lambda p: p.name.casefold()):
                if entry.is_dir():
                    registry["campaigns"].setdefault(entry.name, {})
                    records.extend((entry.name, p) for p in sorted(entry.glob("*.json")))
                elif entry.suffix == ".json":
                    loose.append(entry)
        if loose or not registry["campaigns"]:
            registry["campaigns"].setdefault(c.DEFAULT_CAMPAIGN_SLUG, {"name": c.DEFAULT_CAMPAIGN_NAME})
        for slug, meta in registry["campaigns"].items():
            if not isinstance(meta, dict):
                raise RuntimeError(f"Invalid metadata for campaign {slug!r}")
            meta.setdefault("name", slug.replace("-", " ").title())
            meta.setdefault("description", "")
            meta.setdefault("created", c.now_iso())
        if registry.get("active") not in registry["campaigns"]:
            registry["active"] = c.DEFAULT_CAMPAIGN_SLUG if c.DEFAULT_CAMPAIGN_SLUG in registry["campaigns"] else sorted(registry["campaigns"], key=str.casefold)[0]
        counts = {"campaigns": len(registry["campaigns"]), "setups": 0, "characters": 0}
        with db.transaction():
            mapping = {}
            for slug, meta in registry["campaigns"].items():
                mapping[slug] = db.create_campaign(meta["name"], meta["description"], meta["created"], metadata=meta)
            db.set_value("active_campaign", mapping[registry["active"]])
            records.extend((c.DEFAULT_CAMPAIGN_SLUG, p) for p in loose)
            imported = {}
            for slug, path in records:
                raw = read_json(path)
                if not isinstance(raw, dict):
                    raise RuntimeError(f"Setup {path} must contain an object")
                candidate = copy.deepcopy(raw)
                candidate["active_setup"] = None
                # Old snapshots may contain stale turns; opening a setup resets them.
                for kind in ("monsters", "characters"):
                    items = candidate.get(kind, [])
                    if not isinstance(items, list):
                        raise RuntimeError(f"{path}: {kind} must be a list")
                    for item in items:
                        if not isinstance(item, dict):
                            raise RuntimeError(f"{path}: invalid combatant")
                        if "in_turn" in item and type(item["in_turn"]) is not bool:
                            raise RuntimeError(f"{path}: invalid in_turn flag")
                        item["in_turn"] = False
                normalized = c.normalize_state(candidate)
                for original, monster in zip(raw.get("monsters", []), normalized["monsters"]):
                    monster["in_turn"] = original.get("in_turn", False)
                ident = mapping[slug]
                name = db.unique_setup_name(ident, path.stem)
                db.save_setup(ident, name, c.setup_snapshot(normalized), path.stat().st_mtime)
                imported[(ident, name)] = normalized
                counts["setups"] += 1
            for slug, meta in registry["campaigns"].items():
                ident = mapping[slug]
                if Path(slug).name != slug or slug in (".", ".."): raise RuntimeError("Unsafe legacy campaign slug")
                roster = c.DATA_DIR / "characters" / f"{slug}.json"
                if roster.exists():
                    raw = read_json(roster)
                    characters = raw.get("characters", raw) if isinstance(raw, dict) else raw
                    characters = c.normalize_state({"characters": characters})["characters"]
                else:
                    preferred = meta.get("last_setup")
                    name = preferred if isinstance(preferred, str) and db.setup_exists(ident, preferred) else db.newest_setup(ident)
                    characters = imported[(ident, name)]["characters"] if name else []
                db.save_characters(ident, characters)
                counts["characters"] += len(characters)
                if not db.list_setups(ident):
                    c.create_default_setup(ident)
            state_path = c.DATA_DIR / "state.json"
            if state_path.exists():
                state = read_json(state_path)
                if not isinstance(state, dict):
                    raise RuntimeError("state.json must contain an object")
                state = db.convert_campaign_references(state, mapping)
                state["characters"] = []
                db.set_value("runtime_state", state)
            data = db.read_campaigns()
            for old, meta in registry["campaigns"].items():
                data["campaigns"][mapping[old]] = meta
            db.write_campaigns(data)
            db.set_value("legacy_campaign_id_map", mapping)
            # Validate full startup restoration before committing the import marker.
            c.load_state()
            db.set_value("legacy_import_complete", {"at": c.now_iso(), "counts": counts})
        return counts
