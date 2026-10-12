from typing import Literal

from pydantic import BaseModel, Field, model_validator

from .scrying_glass_health_limits import MAX_STORED_HP

class _Utf8Model(BaseModel):
    """Reject decoded text that cannot be persisted or served as UTF-8."""

    @model_validator(mode="after")
    def _validate_utf8_text(self):
        pending = [self.model_dump()]
        while pending:
            value = pending.pop()
            if isinstance(value, dict):
                pending.extend(value.values())
            elif isinstance(value, list):
                pending.extend(value)
            elif isinstance(value, str):
                try:
                    value.encode("utf-8")
                except UnicodeEncodeError as exc:
                    raise ValueError("Text must not contain unpaired Unicode surrogates") from exc
        return self

class DisplayBackgroundUpdate(_Utf8Model):
    """Displaybackgroundupdate."""
    background: str = Field(min_length=1, max_length=4096)

class BulkCombatantAction(_Utf8Model):
    """Bulkcombatantaction."""
    action: str
    ids: list[str] = Field(min_length=1, max_length=500)

class MonsterUpdate(_Utf8Model):
    """Monsterupdate."""
    name: str | None = Field(default=None, min_length=1, max_length=100)
    monster_species: str | None = Field(default=None, min_length=1, max_length=100)
    ac: int | None = Field(default=None, ge=0, le=999)
    max_hp: int | None = Field(default=None, ge=0, le=MAX_STORED_HP)
    original_hp: int | None = Field(default=None, ge=0, le=MAX_STORED_HP)
    color: str | None = Field(default=None, min_length=1, max_length=40)
    active: bool | None = None
    ally: bool | None = None
    visible: bool | None = None
    initiative: int | None = Field(default=None, ge=-100, le=100)
    hp: int | None = Field(default=None, ge=0, le=MAX_STORED_HP)
    hp_delta: int | None = Field(default=None, ge=-99999, le=99999)
    critical_hit: bool = False
    show_ac: bool | None = None
    show_hp: bool | None = None
    show_initiative: bool | None = None
    in_turn: bool | None = None

    @model_validator(mode="after")
    def _critical_hit_requires_damage(self):
        if self.critical_hit and (self.hp_delta is None or self.hp_delta >= 0):
            raise ValueError("critical_hit requires a negative hp_delta damage event")
        return self

class MonsterBulkUpdate(_Utf8Model):
    """Monsterbulkupdate."""
    field: Literal["active", "ally", "show_ac", "show_hp", "show_initiative"]

class CharacterCreate(_Utf8Model):
    """Charactercreate."""
    name: str = Field(min_length=1, max_length=100)
    color: str = Field(min_length=1, max_length=40)
    hp: int = Field(default=1, ge=0, le=99999)
    initiative: int | None = Field(default=None, ge=-100, le=100)

class CharacterUpdate(_Utf8Model):
    """Characterupdate."""
    name: str | None = Field(default=None, min_length=1, max_length=100)
    color: str | None = Field(default=None, min_length=1, max_length=40)
    active: bool | None = None
    alive: bool | None = None
    visible: bool | None = None
    initiative: int | None = Field(default=None, ge=-100, le=100)
    hp: int | None = Field(default=None, ge=0, le=MAX_STORED_HP)
    max_hp: int | None = Field(default=None, ge=0, le=99999)
    hp_delta: int | None = Field(default=None, ge=-99999, le=99999)
    critical_hit: bool = False
    in_turn: bool | None = None

    @model_validator(mode="after")
    def _critical_hit_requires_damage(self):
        if self.critical_hit and (self.hp_delta is None or self.hp_delta >= 0):
            raise ValueError("critical_hit requires a negative hp_delta damage event")
        return self

class BattleStart(_Utf8Model):
    """Battlestart."""
    order: list[str]

class SetupName(_Utf8Model):
    """Setupname."""
    name: str = Field(min_length=1, max_length=100)
    campaign: str | None = Field(default=None, max_length=100)

class SetupRename(_Utf8Model):
    """Setuprename."""
    name: str = Field(min_length=1, max_length=100)
    new_name: str = Field(min_length=1, max_length=100)
    campaign: str | None = Field(default=None, max_length=100)

class SetupImport(_Utf8Model):
    """Setupimport."""
    life_filter: Literal["alive", "dead", "all"] = "alive"
    name: str = Field(min_length=1, max_length=100)
    kind: Literal["monsters"]
    campaign: str | None = Field(default=None, max_length=100)

class CampaignCreate(_Utf8Model):
    """Campaigncreate."""
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default='', max_length=2000)
    activate: bool = True

class CampaignUpdate(_Utf8Model):
    """Campaignupdate."""
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=2000)

class CampaignSetupAdd(_Utf8Model):
    """Campaignsetupadd."""
    setup: str = Field(min_length=1, max_length=100)
    from_campaign: str = Field(min_length=1, max_length=100)
    mode: Literal['move', 'copy'] = 'move'

class BattleActionRow(_Utf8Model):
    """Battleactionrow."""
    source_id: str | None = Field(default=None, min_length=1, max_length=100)
    target_id: str = Field(min_length=1, max_length=100)
    action: Literal["damage", "heal", "buff", "debuff"]
    amount: int | None = Field(default=None, ge=1, le=99999)
    critical_hit: bool = False

class BattleActions(_Utf8Model):
    """Battleactions."""
    actor_id: str = Field(min_length=1, max_length=100)
    actions: list[BattleActionRow] = Field(min_length=1, max_length=100)

class BattleOrderFontAdjust(_Utf8Model):
    """Adjust viewer battle-order text by one step."""
    direction: Literal["increase", "decrease"]