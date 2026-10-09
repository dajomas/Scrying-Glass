"""State services using the live server context."""

from __future__ import annotations
from typing import Any, Literal
from pathlib import Path


class StateService:
    """Group state operations without owning a separate copy of runtime state."""

    def __init__(self, context: Any) -> None:
        """Retain the live server context."""
        self.context = context

    def entities(self) -> list[dict[str, Any]]:
        """Return all monsters and campaign characters in the current encounter."""
        return [*self.context.STATE['monsters'], *self.context.STATE['characters']]

    def entity(self, ident: str) -> dict[str, Any] | None:
        """Find a combatant by its unique identifier."""
        return next((x for x in self.context.entities() if x['id'] == ident), None)

    def active_combatant(self) -> dict[str, Any] | None:
        """Active combatant."""
        return next(
            (combatant for combatant in self.context.entities() if combatant.get("in_turn")),
            None,
        )

    def configured_background(self) -> str:
        """Configured background."""
        return str(
            self.context.CONFIG.get('display', {}).get('background', self.context.DEFAULT_VIEW_BACKGROUND)
        ).strip() or self.context.DEFAULT_VIEW_BACKGROUND

    def normalize_display(self, raw: Any) -> dict[str, Any]:
        """Normalize display settings, including viewer battle-order font size."""
        display = raw if isinstance(raw, dict) else {}

        background = str(
            display.get(
                "background",
                self.context.configured_background(),
            )
        ).strip()

        font_size = display.get("battle_order_font_size", 16)

        if type(font_size) is not int:
            font_size = 16

        font_size = max(12, min(40, font_size))

        return {
            "background": (
                background or self.context.configured_background()
            ),
            "battle_order_font_size": font_size,
        }

    def normalize_state(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Validate and normalize a complete encounter without mutating input."""
        import copy

        if not isinstance(raw, dict):
            raise ValueError("State must contain a JSON object")

        def require_list(field: str) -> list[Any]:
            value = raw.get(field, [])
            if not isinstance(value, list):
                raise ValueError(f"{field} must be a list")
            return value

        def require_integer(
            item: dict[str, Any],
            field: str,
            location: str,
            *,
            nullable: bool = False,
        ) -> None:
            value = item[field]
            if nullable and value is None:
                return
            if type(value) is not int:
                expected = "an integer or null" if nullable else "an integer"
                raise ValueError(f"{location}.{field} must be {expected}")

        def require_string(
            item: dict[str, Any],
            field: str,
            location: str,
            *,
            nullable: bool = False,
        ) -> None:
            value = item[field]
            if nullable and value is None:
                return
            if not isinstance(value, str):
                expected = "a string or null" if nullable else "a string"
                raise ValueError(f"{location}.{field} must be {expected}")

        def normalize_id_list(field: str) -> list[str]:
            result: list[str] = []
            seen: set[str] = set()

            for index, ident in enumerate(require_list(field)):
                if not isinstance(ident, str) or not ident.strip():
                    raise ValueError(
                        f"{field}[{index}] must be a nonempty string"
                    )
                if ident not in seen:
                    result.append(ident)
                    seen.add(ident)

            return result

        monsters = copy.deepcopy(require_list("monsters"))
        characters = copy.deepcopy(require_list("characters"))
        activity_log = copy.deepcopy(require_list("activity_log"))
        battle_order = normalize_id_list("battle_order")
        turn_successors = normalize_id_list("turn_successors")
        turn_successors_before_wrap = normalize_id_list("turn_successors_before_wrap")

        battle_round = raw.get("battle_round", 0)

        if type(battle_round) is not int or battle_round < 0:
            raise ValueError(
                "battle_round must be a non-negative integer"
            )

        raw_display = raw.get("display")
        if raw_display is not None:
            if not isinstance(raw_display, dict):
                raise ValueError("display must be an object")
            if (
                "background" in raw_display
                and not isinstance(raw_display["background"], str)
            ):
                raise ValueError("display.background must be a string")

        active_setup = None
        raw_reference = raw.get("active_setup")

        if raw_reference is not None:
            if not isinstance(raw_reference, dict):
                raise ValueError("active_setup must be an object or null")

            campaign = raw_reference.get("campaign")
            name = raw_reference.get("name")

            if (
                not isinstance(campaign, str)
                or not campaign.strip()
                or not isinstance(name, str)
                or not name.strip()
            ):
                raise ValueError(
                    "active_setup must contain nonempty campaign "
                    "and name strings"
                )

            active_setup = {
                "campaign": campaign.strip(),
                "name": name.strip(),
            }

        id_locations: dict[str, str] = {}
        turn_locations: list[str] = []

        for kind, items in (
            ("monsters", monsters),
            ("characters", characters),
        ):
            is_monster = kind == "monsters"

            for index, item in enumerate(items):
                location = f"{kind}[{index}]"

                if not isinstance(item, dict):
                    raise ValueError(f"{location} must be an object")

                if "id" not in item:
                    item["id"] = self.context.uuid.uuid4().hex

                ident = item["id"]
                if not isinstance(ident, str) or not ident.strip():
                    raise ValueError(
                        f"{location}.id must be a nonempty string"
                    )

                if ident in id_locations:
                    raise ValueError(
                        f"Duplicate combatant ID {ident!r}: "
                        f"{id_locations[ident]} and {location}"
                    )

                id_locations[ident] = location

                item.setdefault(
                    "name",
                    "Unnamed Monster" if is_monster else "Unnamed Character",
                )
                item.setdefault(
                    "color",
                    "#842029" if is_monster else "#1f4e79",
                )
                item.setdefault("hp", 1)
                require_integer(item, "hp", location)

                if is_monster:
                    item.setdefault(
                        "original_hp",
                        item.get("max_hp", item["hp"]),
                    )
                    item.setdefault("max_hp", item["original_hp"])
                else:
                    item.setdefault("max_hp", item["hp"])
                    item.setdefault("original_hp", item["max_hp"])

                item.setdefault("initiative", None)
                item.setdefault(
                    "original_initiative",
                    item["initiative"],
                )
                item.setdefault("alive", item["hp"] > 0)
                item.setdefault("active", False)
                item.setdefault("visible", False)
                item.setdefault("in_turn", False)

                if is_monster:
                    if "monster_species" not in item:
                        item["monster_species"] = item.pop(
                            "monster_type",
                            "unknown",
                        )
                    else:
                        item.pop("monster_type", None)

                    require_string(item, "monster_species", location)
                    item["monster_species"] = (
                        item["monster_species"].strip() or "unknown"
                    )

                    item.setdefault("ac", 0)
                    item.setdefault("image_url", None)
                    item.setdefault("ally", False)
                    item.setdefault("show_ac", False)
                    item.setdefault("show_hp", False)
                    item.setdefault("show_initiative", False)

                for field in ("name", "color"):
                    require_string(item, field, location)

                for field in ("max_hp", "original_hp"):
                    require_integer(item, field, location)

                for field in ("initiative", "original_initiative"):
                    require_integer(
                        item,
                        field,
                        location,
                        nullable=True,
                    )

                if "ac" in item:
                    require_integer(item, "ac", location)

                if "image_url" in item:
                    require_string(
                        item,
                        "image_url",
                        location,
                        nullable=True,
                    )

                boolean_fields = [
                    "alive",
                    "active",
                    "visible",
                    "in_turn",
                ]

                if is_monster:
                    boolean_fields.extend([
                        "ally",
                        "show_ac",
                        "show_hp",
                        "show_initiative",
                    ])

                for field in boolean_fields:
                    if type(item[field]) is not bool:
                        raise ValueError(
                            f"{location}.{field} must be a boolean"
                        )

                if item["in_turn"]:
                    if not item["active"] or not item["alive"]:
                        raise ValueError(
                            f"{location}.in_turn requires an active, "
                            "living combatant"
                        )
                    turn_locations.append(location)

        if len(turn_locations) > 1:
            raise ValueError(
                "Only one combatant may be in turn: "
                + ", ".join(turn_locations)
            )

        known_ids = set(id_locations)

        return {
            "monsters": monsters,
            "characters": characters,
            "battle_order": [
                ident for ident in battle_order if ident in known_ids
            ],
            "turn_successors": [
                ident for ident in turn_successors if ident in known_ids
            ],
            "activity_log": [
                entry for entry in activity_log
                if isinstance(entry, dict)
            ],
            "display": self.context.normalize_display(raw_display),
            "active_setup": active_setup,
            "battle_round": battle_round,
            "turn_successors_before_wrap": [
                ident
                for ident in turn_successors_before_wrap
                if ident in known_ids
            ],
        }

    def display_state(self) -> dict[str, Any]:
        """Return only information intended for the player display."""
        full = self.context.public_state()

        common_fields = (
            "id",
            "name",
            "color",
            "active",
            "alive",
            "visible",
            "in_turn",
        )

        def display_character(item: dict[str, Any]) -> dict[str, Any]:
            return {key: item.get(key) for key in common_fields}

        def display_monster(item: dict[str, Any]) -> dict[str, Any]:
            result = display_character(item)
            result.update({
                "monster_species": item.get("monster_species", "unknown"),
                "ally": item.get("ally", False),
                "image_url": item.get("image_url"),
                "show_ac": item.get("show_ac", False),
                "show_hp": item.get("show_hp", False),
                "show_initiative": item.get("show_initiative", False),
                "initiative": None,
            })

            if result["show_ac"]:
                result["ac"] = item.get("ac")

            if result["show_hp"]:
                result["hp"] = item.get("hp")
                result["max_hp"] = item.get("max_hp")

            if result["show_initiative"]:
                result["initiative"] = item.get("initiative")

            return result

        # Monster cards are included whenever the monster is In Battle.
        # The browser retains the existing alive/dead card behavior.
        monsters = [
            display_monster(item)
            for item in full["monsters"]
            if item.get("active")
        ]

        # Characters appear only in the battle-order strip.
        characters = [
            display_character(item)
            for item in full["characters"]
            if item.get("active") and item.get("visible")
        ]

        # Visible controls inclusion in the battle-order strip,
        # independently of whether a monster card is displayed.
        visible_ids = {
            item["id"]
            for item in [*monsters, *characters]
            if item.get("active") and item.get("visible")
        }

        display_order = list(dict.fromkeys(
            ident
            for ident in full["battle_order"]
            if ident in visible_ids
        ))
        ordered_ids = set(display_order)

        additional = sorted(
            (
                item
                for item in [
                    *full["characters"],
                    *full["monsters"],
                ]
                if item["id"] in visible_ids
                and item["id"] not in ordered_ids
            ),
            key=self.context.admin_initiative_key,
        )

        display_order.extend(item["id"] for item in additional)

        return {
            "monsters": monsters,
            "characters": characters,
            "battle_round": full["battle_round"],
            "battle_order": [
                ident
                for ident in full["battle_order"]
                if ident in visible_ids
            ],
            "display_order": display_order,
            "display": self.context.copy.deepcopy(full["display"]),
        }

    def public_state(self) -> dict[str, Any]:
        """Build the full state payload for authenticated administration."""
        configured_display = self.context.CONFIG["display"]
        runtime_display = self.context.normalize_display(
            self.context.STATE.get("display"),
        )

        return {
            "monsters": self.context.STATE["monsters"],
            "characters": self.context.STATE["characters"],
            "battle_round": self.context.STATE.get("battle_round", 0),
            "battle_order": self.context.STATE["battle_order"],
            "activity_log": self.context.STATE["activity_log"],
            "active_setup": self.context.STATE.get("active_setup"),
            "display": {
                "background": runtime_display["background"],
                "battle_order_font_size": (
                    runtime_display["battle_order_font_size"]
                ),
                "entry_direction": configured_display["entry_direction"],
                "exit_direction": configured_display["exit_direction"],
                "monster_width_percent": (
                    configured_display["monster_width_percent"]
                ),
            },
        }

    def active_setup_reference(self) -> dict[str, str] | None:
        """Return the current saved battle setup reference, when valid."""
        value = self.context.STATE.get("active_setup")

        if not isinstance(value, dict):
            return None

        campaign = value.get("campaign")
        name = value.get("name")

        if not isinstance(campaign, str) or not campaign.strip():
            return None

        if not isinstance(name, str) or not name.strip():
            return None

        return {
            "campaign": campaign,
            "name": name,
        }

    def set_active_setup(self, campaign: str, name: str) -> None:
        """Mark the named saved setup as the source of the working monsters."""
        self.context.STATE["active_setup"] = {
            "campaign": campaign,
            "name": name,
        }

    def clear_active_setup(self) -> None:
        """Mark the current monster encounter as unsaved."""
        self.context.STATE["active_setup"] = None

    def active_setup_exists(self) -> bool:
        reference = self.context.active_setup_reference()
        if reference is None:
            return False
        return self.context.STORAGE.setup_exists(reference["campaign"], reference["name"])
