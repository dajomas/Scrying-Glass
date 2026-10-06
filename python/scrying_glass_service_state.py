"""State services using the live server context."""

from __future__ import annotations
from typing import Any, Literal
from pathlib import Path
from fastapi import HTTPException, Request as FastAPIRequest, UploadFile


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

    def normalize_display(self, raw: Any) -> dict[str, str]:
        """Normalize display."""
        display = raw if isinstance(raw, dict) else {}
        background = str(
            display.get('background', self.context.configured_background())
        ).strip()

        return {
            'background': background or self.context.configured_background(),
        }

    def normalize_state(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Normalize state."""
        raw_active_setup = raw.get("active_setup")

        if isinstance(raw_active_setup, dict):
            raw_campaign = raw_active_setup.get("campaign")
            raw_name = raw_active_setup.get("name")

            if (
                isinstance(raw_campaign, str)
                and raw_campaign.strip()
                and isinstance(raw_name, str)
                and raw_name.strip()
            ):
                active_setup: dict[str, str] | None = {
                    "campaign": raw_campaign.strip(),
                    "name": raw_name.strip(),
                }
            else:
                active_setup = None
        else:
            active_setup = None

        state = {
            "monsters": raw.get("monsters", []),
            "characters": raw.get("characters", []),
            "battle_order": raw.get("battle_order", []),
            "activity_log": raw.get("activity_log", []),
            "display": self.context.normalize_display(raw.get("display")),
            "active_setup": active_setup,
        }

        if (
            not isinstance(state["monsters"], list)
            or not isinstance(state["characters"], list)
            or not isinstance(state["battle_order"], list)
            or not isinstance(state["activity_log"], list)
        ):
            raise ValueError('Setup has invalid monsters, characters, battle_order, or activity_log data')

        state["activity_log"] = [
            entry
            for entry in state["activity_log"]
            if isinstance(entry, dict)
        ]

        for m in state['monsters']:
            if not isinstance(m, dict):
                raise ValueError('Setup contains an invalid monster')
            m.setdefault('id', self.context.uuid.uuid4().hex)
            m.setdefault('name', 'Unnamed Monster')
            if 'monster_species' not in m:
                m['monster_species'] = m.pop('monster_type', 'unknown')
            else:
                m.pop('monster_type', None)

            m['monster_species'] = str(m['monster_species']).strip() or 'unknown'
            m.setdefault('ac', 0)
            m.setdefault('hp', 1)
            m.setdefault('original_hp', m.get('max_hp', m['hp']))
            m.setdefault('max_hp', m['original_hp'])
            m.setdefault('color', '#842029')
            m.setdefault('image_url', None)
            m.setdefault('alive', m['hp'] > 0)
            m.setdefault('active', False)
            m.setdefault('visible', False)
            m.setdefault('ally', False)
            m.setdefault('initiative', None)
            m.setdefault('original_initiative', m.get('initiative'))
            m.setdefault('show_ac', False)
            m.setdefault('show_hp', False)
            m.setdefault('show_initiative', False)
            m.setdefault('in_turn', False)
        for c in state['characters']:
            if not isinstance(c, dict):
                raise ValueError('Setup contains an invalid character')
            c.setdefault('id', self.context.uuid.uuid4().hex)
            c.setdefault('name', 'Unnamed Character')
            c.setdefault('color', '#1f4e79')
            c.setdefault('hp', 1)
            c.setdefault('max_hp', c['hp'])
            c.setdefault('original_hp', c['max_hp'])
            c.setdefault('original_initiative', c.get('initiative'))
            c.setdefault('alive', c['hp'] > 0)
            c.setdefault('active', False)
            c.setdefault('visible', False)
            c.setdefault('in_turn', False)
        known = {x['id'] for x in [*state['monsters'], *state['characters']]}
        state['battle_order'] = [x for x in state['battle_order'] if x in known]
        return state

    def public_state(self) -> dict[str, Any]:
        """Build the state payload exposed to authenticated displays."""
        d = self.context.CONFIG['display']
        return {
            "monsters": self.context.STATE["monsters"],
            "characters": self.context.STATE["characters"],
            "battle_order": self.context.STATE["battle_order"],
            "activity_log": self.context.STATE["activity_log"],
            "active_setup": self.context.STATE.get("active_setup"),
            "display": {
                "background": self.context.STATE["display"]["background"],
                "entry_direction": d["entry_direction"],
                "exit_direction": d["exit_direction"],
                "monster_width_percent": d["monster_width_percent"],
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

    def active_setup_path(self) -> Path | None:
        """Return the referenced setup path only when it still exists."""
        reference = self.context.active_setup_reference()

        if reference is None:
            return None

        try:
            campaign = self.context.require_campaign(reference["campaign"])
            name = self.context.setup_slug(reference["name"])
        except self.context.HTTPException:
            return None

        path = self.context.setup_path(name, campaign)

        return path if path.exists() else None
