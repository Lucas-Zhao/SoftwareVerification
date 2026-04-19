"""
BattleState: a plain dataclass holding everything the AI script
can read during a single move-scoring pass.

Stat stages run 0..12 where 6 is neutral (+0), 0 is -6, 12 is +6.
This matches the raw values the script compares against.
"""

from dataclasses import dataclass, field
from typing import Optional
from battle_types import (
    Ability, PokeType, Effectiveness, Weather,
    StatusCondition, BattleEffect, Item, HeldItemEffect,
    Move, Gender, BattleStat, SpeedCompare,
)

NEUTRAL_STAGE = 6  # stat stage value meaning +0

@dataclass
class StatStages:
    attack:    int = NEUTRAL_STAGE
    defense:   int = NEUTRAL_STAGE
    speed:     int = NEUTRAL_STAGE
    sp_attack: int = NEUTRAL_STAGE
    sp_defense:int = NEUTRAL_STAGE
    accuracy:  int = NEUTRAL_STAGE
    evasion:   int = NEUTRAL_STAGE

    def get(self, stat: BattleStat) -> int:
        return {
            BattleStat.ATTACK:     self.attack,
            BattleStat.DEFENSE:    self.defense,
            BattleStat.SPEED:      self.speed,
            BattleStat.SP_ATTACK:  self.sp_attack,
            BattleStat.SP_DEFENSE: self.sp_defense,
            BattleStat.ACCURACY:   self.accuracy,
            BattleStat.EVASION:    self.evasion,
        }[stat]


@dataclass
class BattleState:
    # --- current move being scored ---
    move_effect:      BattleEffect  = BattleEffect.NONE
    move_type:        PokeType      = PokeType.NORMAL
    effectiveness:    Effectiveness = Effectiveness.NORMAL_DAMAGE

    # --- attacker ---
    attacker_ability:    Ability         = Ability.NONE
    attacker_type1:      PokeType        = PokeType.NORMAL
    attacker_type2:      PokeType        = PokeType.NORMAL
    attacker_status:     StatusCondition = StatusCondition.NONE
    attacker_hp_pct:     int             = 100   # 0-100
    attacker_stages:     StatStages      = field(default_factory=StatStages)
    attacker_item:       Item            = Item.NONE
    attacker_item_effect:HeldItemEffect  = HeldItemEffect.NONE
    attacker_gender:     Gender          = Gender.GENDERLESS

    # --- defender ---
    defender_ability:    Ability         = Ability.NONE
    defender_type1:      PokeType        = PokeType.NORMAL
    defender_type2:      PokeType        = PokeType.NORMAL
    defender_status:     StatusCondition = StatusCondition.NONE
    defender_hp_pct:     int             = 100   # 0-100
    defender_stages:     StatStages      = field(default_factory=StatStages)
    defender_item:       Item            = Item.NONE
    defender_item_effect:HeldItemEffect  = HeldItemEffect.NONE
    defender_gender:     Gender          = Gender.GENDERLESS

    # --- field ---
    weather:             Weather         = Weather.NONE
    speed_compare:       SpeedCompare    = SpeedCompare.FASTER
