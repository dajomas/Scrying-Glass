from typing import Literal

from pydantic import BaseModel, Field

class DisplayBackgroundUpdate(BaseModel):
    """Displaybackgroundupdate."""
    background: str = Field(min_length=1, max_length=4096)

class BulkCombatantAction(BaseModel):
    """Bulkcombatantaction."""
    action: str
    ids: list[str] = Field(min_length=1, max_length=500)

class MonsterUpdate(BaseModel):
    """Monsterupdate."""
    name: str | None = Field(default=None, min_length=1, max_length=100)
    monster_species: str | None = Field(default=None, min_length=1, max_length=100)
    ac: int | None = Field(default=None, ge=0, le=999)
    max_hp: int | None = Field(default=None, ge=0, le=99999)
    original_hp: int | None = Field(default=None, ge=0, le=99999)
    color: str | None = Field(default=None, min_length=1, max_length=40)
    active: bool | None = None
    ally: bool | None = None
    visible: bool | None = None
    initiative: int | None = Field(default=None, ge=-100, le=100)
    hp: int | None = Field(default=None, ge=-99999, le=99999)
    hp_delta: int | None = Field(default=None, ge=-99999, le=99999)
    show_ac: bool | None = None
    show_hp: bool | None = None
    show_initiative: bool | None = None
    in_turn: bool | None = None

class MonsterBulkUpdate(BaseModel):
    """Monsterbulkupdate."""
    field: Literal["active", "ally", "show_ac", "show_hp", "show_initiative"]

class CharacterCreate(BaseModel):
    """Charactercreate."""
    name: str = Field(min_length=1, max_length=100)
    color: str = Field(min_length=1, max_length=40)
    hp: int = Field(default=1, ge=0, le=99999)
    initiative: int | None = Field(default=None, ge=-100, le=100)

class CharacterUpdate(BaseModel):
    """Characterupdate."""
    name: str | None = Field(default=None, min_length=1, max_length=100)
    color: str | None = Field(default=None, min_length=1, max_length=40)
    active: bool | None = None
    alive: bool | None = None
    visible: bool | None = None
    initiative: int | None = Field(default=None, ge=-100, le=100)
    hp: int | None = Field(default=None, ge=-99999, le=99999)
    max_hp: int | None = Field(default=None, ge=0, le=99999)
    hp_delta: int | None = Field(default=None, ge=-99999, le=99999)
    in_turn: bool | None = None

class BattleStart(BaseModel):
    """Battlestart."""
    order: list[str]

class SetupName(BaseModel):
    """Setupname."""
    name: str = Field(min_length=1, max_length=100)
    campaign: str | None = Field(default=None, max_length=100)

class SetupRename(BaseModel):
    """Setuprename."""
    name: str = Field(min_length=1, max_length=100)
    new_name: str = Field(min_length=1, max_length=100)
    campaign: str | None = Field(default=None, max_length=100)

class SetupImport(BaseModel):
    """Setupimport."""
    name: str = Field(min_length=1, max_length=100)
    kind: Literal["monsters"]
    campaign: str | None = Field(default=None, max_length=100)

class CampaignCreate(BaseModel):
    """Campaigncreate."""
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default='', max_length=2000)
    activate: bool = True

class CampaignUpdate(BaseModel):
    """Campaignupdate."""
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=2000)

class CampaignSetupAdd(BaseModel):
    """Campaignsetupadd."""
    setup: str = Field(min_length=1, max_length=100)
    from_campaign: str = Field(min_length=1, max_length=100)
    mode: Literal['move', 'copy'] = 'move'

class BattleActionRow(BaseModel):
    """Battleactionrow."""
    target_id: str = Field(min_length=1, max_length=100)
    action: Literal["damage", "heal", "buff", "debuff"]
    amount: int | None = Field(default=None, ge=1, le=99999)

class BattleActions(BaseModel):
    """Battleactions."""
    actor_id: str = Field(min_length=1, max_length=100)
    actions: list[BattleActionRow] = Field(min_length=1, max_length=100)