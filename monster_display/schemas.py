from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field

class MonsterUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    monster_type: str | None = Field(default=None, min_length=1, max_length=100)
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
    field: Literal["active", "ally", "show_ac", "show_hp", "show_initiative"]

class CharacterCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    color: str = Field(min_length=1, max_length=40)
    hp: int = Field(default=1, ge=0, le=99999)
    initiative: int | None = Field(default=None, ge=-100, le=100)

class CharacterUpdate(BaseModel):
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
    order: list[str]

class SetupName(BaseModel):
    name: str = Field(min_length=1, max_length=100)

class SetupImport(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    kind: Literal['characters', 'monsters', 'both']
admin = FastAPI(title='Monster Display Admin')
client = FastAPI(title='Monster Display Client')

class BattleActionRow(BaseModel):
    target_id: str = Field(min_length=1, max_length=100)
    action: Literal["damage", "heal", "buff", "debuff"]
    amount: int | None = Field(default=None, ge=1, le=99999)

class BattleActions(BaseModel):
    actor_id: str = Field(min_length=1, max_length=100)
    actions: list[BattleActionRow] = Field(min_length=1, max_length=100)
