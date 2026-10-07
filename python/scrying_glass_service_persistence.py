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

    def load_campaign_characters(
        self,
        slug: str,
    ) -> list[dict[str, Any]]:
        """Load and validate a campaign's character roster."""
        path = self.context.campaign_characters_path(slug)

        if not path.exists():
            return []

        try:
            raw = self.context.json.loads(
                path.read_text(encoding="utf-8")
            )
        except (
            OSError,
            UnicodeDecodeError,
            self.context.json.JSONDecodeError,
        ) as exc:
            raise self.context.HTTPException(
                400,
                f"Unable to load campaign characters: {exc}",
            ) from exc

        characters = (
            raw.get("characters", raw)
            if isinstance(raw, dict)
            else raw
        )

        if not isinstance(characters, list):
            raise self.context.HTTPException(
                400,
                "Campaign character roster must contain a character list",
            )

        try:
            normalized = self.context.normalize_state({
                "characters": characters,
            })
        except ValueError as exc:
            raise self.context.HTTPException(
                400,
                f"Campaign character roster is invalid: {exc}",
            ) from exc

        return normalized["characters"]

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

    def load_setup_state(
        self,
        name: str,
        campaign: str,
    ) -> dict[str, Any]:
        """Load encounter data without reviving historical runtime turns."""
        import copy

        campaign = self.context.require_campaign(campaign)
        name = self.context.setup_slug(name)
        path = self.context.setup_path(name, campaign)

        try:
            raw = self.context.json.loads(
                path.read_text(encoding="utf-8")
            )
        except FileNotFoundError as exc:
            raise self.context.HTTPException(
                404,
                "Saved setup not found",
            ) from exc
        except (
            OSError,
            UnicodeDecodeError,
            self.context.json.JSONDecodeError,
        ) as exc:
            raise self.context.HTTPException(
                400,
                f"Unable to load setup: {exc}",
            ) from exc

        if not isinstance(raw, dict):
            raise self.context.HTTPException(
                400,
                "Saved setup must contain a JSON object",
            )

        candidate = copy.deepcopy(raw)
        candidate["characters"] = (
            self.context.load_campaign_characters(campaign)
        )

        for kind in ("monsters", "characters"):
            items = candidate.get(kind, [])

            if not isinstance(items, list):
                raise self.context.HTTPException(
                    400,
                    f"Unable to load setup: {kind} must be a list",
                )

            for index, item in enumerate(items):
                if not isinstance(item, dict):
                    raise self.context.HTTPException(
                        400,
                        f"Unable to load setup: "
                        f"{kind}[{index}] must be an object",
                    )

                if (
                    "in_turn" in item
                    and type(item["in_turn"]) is not bool
                ):
                    raise self.context.HTTPException(
                        400,
                        f"Unable to load setup: "
                        f"{kind}[{index}].in_turn must be a boolean",
                    )

                item["in_turn"] = False

        candidate["turn_successors"] = []
        candidate["active_setup"] = None
        candidate.pop("active_turn_id", None)

        try:
            return self.context.normalize_state(candidate)
        except ValueError as exc:
            raise self.context.HTTPException(
                400,
                f"Unable to load setup: {exc}",
            ) from exc

    def load_state(self) -> None:
        """Restore an encounter completely, or fail without replacing live state."""
        import copy
        import logging

        logger = logging.getLogger(__name__)

        def read_object(path: Any, description: str) -> dict[str, Any]:
            try:
                value = self.context.json.loads(
                    path.read_text(encoding="utf-8")
                )
            except (
                OSError,
                UnicodeDecodeError,
                self.context.json.JSONDecodeError,
            ) as exc:
                raise RuntimeError(
                    f"Unable to read {description} ({path}): {exc}"
                ) from exc

            if not isinstance(value, dict):
                raise RuntimeError(
                    f"{description} ({path}) must contain a JSON object"
                )

            return value

        try:
            campaign = self.context.require_campaign(None)
            characters = self.context.load_campaign_characters(campaign)
        except (ValueError, self.context.HTTPException) as exc:
            detail = getattr(exc, "detail", str(exc))
            raise RuntimeError(
                f"Unable to load the active campaign roster: {detail}"
            ) from exc

        if not self.context.STATE_FILE.exists():
            candidate = copy.deepcopy(self.context.STATE)
            candidate["characters"] = characters

            try:
                normalized = self.context.normalize_state(candidate)
            except ValueError as exc:
                raise RuntimeError(
                    f"Unable to initialize encounter state: {exc}"
                ) from exc

            self.context.STATE = normalized
            return

        saved = read_object(
            self.context.STATE_FILE,
            "state.json",
        )

        working_monsters = saved.get("monsters", [])
        if not isinstance(working_monsters, list):
            raise RuntimeError(
                "Unable to restore state.json: monsters must be a list"
            )

        candidate = copy.deepcopy(saved)
        candidate["characters"] = characters
        candidate["monsters"] = copy.deepcopy(working_monsters)

        reference = saved.get("active_setup")

        if reference is not None:
            if not isinstance(reference, dict):
                raise RuntimeError(
                    "Unable to restore state.json: "
                    "active_setup must be an object or null"
                )

            reference_campaign = reference.get("campaign")
            reference_name = reference.get("name")

            if (
                not isinstance(reference_campaign, str)
                or not reference_campaign.strip()
                or not isinstance(reference_name, str)
                or not reference_name.strip()
            ):
                raise RuntimeError(
                    "Unable to restore state.json: active_setup requires "
                    "nonempty campaign and name strings"
                )

            reference_campaign = reference_campaign.strip()

            if reference_campaign != campaign:
                raise RuntimeError(
                    "Unable to restore state.json: its setup belongs to "
                    f"campaign {reference_campaign!r}, but the active "
                    f"campaign is {campaign!r}. Resolve the mismatch "
                    "before restarting."
                )

            try:
                name = self.context.setup_slug(reference_name)
                path = self.context.setup_path(name, campaign)
            except (ValueError, self.context.HTTPException) as exc:
                detail = getattr(exc, "detail", str(exc))
                raise RuntimeError(
                    f"Unable to resolve the saved setup reference: {detail}"
                ) from exc

            setup = read_object(
                path,
                "referenced encounter setup",
            )

            setup_monsters = setup.get("monsters", [])
            if not isinstance(setup_monsters, list):
                raise RuntimeError(
                    f"Unable to restore setup {name!r}: "
                    "monsters must be a list"
                )

            if not working_monsters:
                candidate["monsters"] = copy.deepcopy(setup_monsters)

            candidate["active_setup"] = {
                "campaign": campaign,
                "name": name,
            }
        else:
            candidate["active_setup"] = None

        combatants = [
            *candidate["monsters"],
            *candidate["characters"],
        ]

        has_turn_marker = "active_turn_id" in saved
        active_turn_id = saved.get("active_turn_id")

        if has_turn_marker:
            if active_turn_id is not None and (
                not isinstance(active_turn_id, str)
                or not active_turn_id.strip()
            ):
                raise RuntimeError(
                    "Unable to restore state.json: active_turn_id "
                    "must be a nonempty string or null"
                )

            for index, item in enumerate(combatants):
                if not isinstance(item, dict):
                    continue

                if (
                    "in_turn" in item
                    and type(item["in_turn"]) is not bool
                ):
                    raise RuntimeError(
                        "Unable to restore state.json: "
                        f"combatant {index} has a non-boolean in_turn flag"
                    )

                item["in_turn"] = False
        else:
            legacy_turns = [
                item
                for item in combatants
                if isinstance(item, dict)
                and item.get("in_turn") is True
            ]

            if len(legacy_turns) > 1:
                logger.warning(
                    "Legacy persisted files contain conflicting turns. "
                    "Restoring without an active turn."
                )

                for item in legacy_turns:
                    item["in_turn"] = False

        candidate.pop("active_turn_id", None)

        try:
            normalized = self.context.normalize_state(candidate)
        except ValueError as exc:
            raise RuntimeError(
                f"Unable to restore encounter state: {exc}"
            ) from exc

        if has_turn_marker and active_turn_id is not None:
            target = next(
                (
                    item
                    for item in [
                        *normalized["monsters"],
                        *normalized["characters"],
                    ]
                    if item["id"] == active_turn_id
                ),
                None,
            )

            if (
                target is not None
                and target["active"]
                and target["alive"]
            ):
                target["in_turn"] = True
                target["visible"] = True
            else:
                logger.warning(
                    "Saved active turn %r is missing or ineligible; "
                    "restoring without an active turn.",
                    active_turn_id,
                )

        self.context.STATE = normalized

    def save_state(self) -> None:
        """Persist runtime references and an authoritative active-turn marker."""
        import copy

        combatants = self.context.entities()
        current_turns = [
            item
            for item in combatants
            if item.get("in_turn") is True
        ]

        if len(current_turns) > 1:
            raise ValueError(
                "Cannot save state: more than one combatant is in turn"
            )

        active_turn_id = None

        if current_turns:
            current = current_turns[0]
            ident = current.get("id")

            if not isinstance(ident, str) or not ident.strip():
                raise ValueError(
                    "Cannot save state: active combatant has an invalid ID"
                )

            if (
                current.get("active") is not True
                or current.get("alive") is not True
            ):
                raise ValueError(
                    "Cannot save state: the combatant in turn "
                    "must be active and alive"
                )

            active_turn_id = ident

        persisted = copy.deepcopy(self.context.STATE)
        persisted["active_turn_id"] = active_turn_id

        persisted["characters"] = []

        if self.context.active_setup_path() is not None:
            persisted["monsters"] = []
        else:
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

        try:
            campaign = self.context.require_campaign(reference["campaign"])
            name = self.context.setup_slug(reference["name"])
            path = self.context.setup_path(name, campaign)
        except self.context.HTTPException:
            self.context.clear_active_setup()
            return False

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
