"""Persistence services using the live server context."""

from __future__ import annotations
from typing import Any, Literal
from pathlib import Path
from fastapi import HTTPException, Request as FastAPIRequest, UploadFile


class PersistenceService:
    """Group persistence operations without owning a separate copy of runtime state."""

    def __init__(self, context: Any) -> None:
        """Retain the live server context."""
        self.context = context

    def load_campaign_characters(self, slug: str) -> list[dict[str, Any]]:
        """Load campaign characters."""
        path = self.context.campaign_characters_path(slug)

        if not path.exists():
            return []

        try:
            raw = self.context.json.loads(path.read_text(encoding="utf-8"))
        except (OSError, self.context.json.JSONDecodeError) as exc:
            raise self.context.HTTPException(
                400,
                f"Unable to load campaign characters: {exc}",
            ) from exc

        characters = raw.get("characters", raw) if isinstance(raw, dict) else raw

        if not isinstance(characters, list):
            raise self.context.HTTPException(400, "Campaign character roster is invalid")

        return self.context.normalize_state({"characters": characters})["characters"]

    def save_campaign_characters(self, slug: str, characters: list[dict[str, Any]]) -> None:
        """Save campaign characters."""
        self.context.CHARACTERS_DIR.mkdir(parents=True, exist_ok=True)

        path = self.context.campaign_characters_path(slug)
        temp = path.with_suffix(".tmp")

        temp.write_text(
            self.context.json.dumps({"characters": characters}, indent=2),
            encoding="utf-8",
        )
        temp.replace(path)

    def save_active_campaign_characters(self) -> None:
        """Save active campaign characters."""
        self.context.save_campaign_characters(
            self.context.require_campaign(None),
            self.context.STATE["characters"],
        )

    def load_setup_state(self, name: str, campaign: str) -> dict[str, Any]:
        """Load setup state."""
        path = self.context.setup_path(name, campaign)

        if not path.exists():
            raise self.context.HTTPException(404, "Saved setup not found")

        try:
            raw = self.context.json.loads(path.read_text(encoding="utf-8"))
        except (OSError, self.context.json.JSONDecodeError) as exc:
            raise self.context.HTTPException(400, f"Unable to load setup: {exc}") from exc

        if not isinstance(raw, dict):
            raise self.context.HTTPException(400, "Saved setup must contain a JSON object")

        raw["characters"] = self.context.load_campaign_characters(campaign)

        try:
            return self.context.normalize_state(raw)
        except ValueError as exc:
            raise self.context.HTTPException(400, f"Unable to load setup: {exc}") from exc

    def load_state(self) -> None:
        """Load state."""
    

        if not self.context.STATE_FILE.exists():
            self.context.STATE = self.context.normalize_state(self.context.STATE)
            return

        try:
            saved = self.context.json.loads(self.context.STATE_FILE.read_text(encoding="utf-8"))
        except (OSError, self.context.json.JSONDecodeError) as exc:
            raise RuntimeError(f"Unable to load state.json: {exc}") from exc

        saved_state = self.context.normalize_state(saved)
        reference = saved_state.get("active_setup")

        if isinstance(reference, dict):
            campaign = reference.get("campaign")
            name = reference.get("name")

            if isinstance(campaign, str) and isinstance(name, str):
                try:
                    # This obtains the saved setup's monster list, then restores
                    # campaign characters through the canonical setup loader.
                    restored = self.context.load_setup_state(name, campaign)

                    # Runtime working-state fields still come from state.json.
                    restored["battle_order"] = saved_state["battle_order"]
                    restored["activity_log"] = saved_state["activity_log"]
                    restored["display"] = saved_state["display"]
                    restored["active_setup"] = {
                        "campaign": campaign,
                        "name": name,
                    }

                    # If state.json is intentionally not storing monsters, use the
                    # monsters from the saved setup. If a transitional/older file
                    # does contain monsters, its data wins as working runtime data.
                    if saved_state["monsters"]:
                        restored["monsters"] = saved_state["monsters"]

                    self.context.STATE = self.context.normalize_state(restored)
                    return
                except self.context.HTTPException:
                    # The referenced campaign/setup no longer exists or is unreadable.
                    # Continue below and preserve state.json as an unsaved encounter.
                    pass

        # No valid setup association: state.json owns the working monsters.
        saved_state["active_setup"] = None
        self.context.STATE = self.context.normalize_state(saved_state)

    def save_state(self) -> None:
        """Persist the current encounter and active setup reference."""
        persisted = self.context.copy.deepcopy(self.context.STATE)

        # Characters are campaign-owned and must not be duplicated in state.json.
        persisted["characters"] = []

        # When the working monsters come from a valid saved battle setup, the setup
        # file is authoritative. state.json stores only the setup reference.
        if self.context.active_setup_path() is not None:
            persisted["monsters"] = []
        else:
            # If the referenced setup disappeared, was renamed, or was deleted,
            # preserve the working monsters as an unsaved encounter.
            persisted["active_setup"] = None

        temp = self.context.STATE_FILE.with_suffix(".tmp")
        temp.write_text(
            self.context.json.dumps(persisted, indent=2),
            encoding="utf-8",
        )
        temp.replace(self.context.STATE_FILE)

    def save_active_setup_monsters(self) -> bool:
        '\n    Persist the working monster encounter into the currently active saved setup.\n\n    Returns True when a saved setup was updated. Returns False when the current\n    encounter is intentionally unsaved and therefore exists only in state.json.\n    '
        reference = self.context.active_setup_reference()

        if reference is None:
            return False

        campaign = self.context.require_campaign(reference["campaign"])
        name = self.context.setup_slug(reference["name"])
        path = self.context.setup_path(name, campaign)

        if not path.exists():
            # The setup reference is stale. Preserve the current encounter as
            # unsaved runtime state rather than recreating an unexpected file.
            self.context.clear_active_setup()
            return False

        snapshot = self.context.setup_snapshot(self.context.STATE)
        temp = path.with_suffix(".tmp")

        temp.write_text(
            self.context.json.dumps(snapshot, indent=2),
            encoding="utf-8",
        )
        temp.replace(path)

        self.context.remember_setup(campaign, name)
        return True
