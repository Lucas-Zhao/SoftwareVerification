"""
A minimal property-based testing engine.

No external dependencies — uses only the standard library.

Design:
  - generate_state() produces a random BattleState
  - check_property() runs a predicate N times and reports counterexamples
  - shrink_state() tries to simplify a failing state for readability
"""

import random
import copy
from dataclasses import fields
from typing import Callable, Optional

from battle_state import BattleState, StatStages, NEUTRAL_STAGE
from battle_types import (
    Ability, PokeType, Effectiveness, Weather,
    StatusCondition, BattleEffect, Item, HeldItemEffect,
    Move, Gender, SpeedCompare,
)

RNG = random.Random()


# Random samplers

def _pick(enum_cls):
    """Pick a uniformly random member of an Enum."""
    members = list(enum_cls)
    return RNG.choice(members)


def _hp() -> int:
    return RNG.randint(1, 100)


def _stage() -> int:
    return RNG.randint(0, 12)


def random_stat_stages() -> StatStages:
    return StatStages(
        attack    = _stage(),
        defense   = _stage(),
        speed     = _stage(),
        sp_attack = _stage(),
        sp_defense= _stage(),
        accuracy  = _stage(),
        evasion   = _stage(),
    )


def generate_state(seed: Optional[int] = None) -> BattleState:
    """Return a fully random BattleState."""
    if seed is not None:
        RNG.seed(seed)

    return BattleState(
        move_effect       = _pick(BattleEffect),
        move_type         = _pick(PokeType),
        effectiveness     = _pick(Effectiveness),

        attacker_ability     = _pick(Ability),
        attacker_type1       = _pick(PokeType),
        attacker_type2       = _pick(PokeType),
        attacker_status      = _pick(StatusCondition),
        attacker_hp_pct      = _hp(),
        attacker_stages      = random_stat_stages(),
        attacker_item        = _pick(Item),
        attacker_item_effect = _pick(HeldItemEffect),
        attacker_gender      = _pick(Gender),

        defender_ability     = _pick(Ability),
        defender_type1       = _pick(PokeType),
        defender_type2       = _pick(PokeType),
        defender_status      = _pick(StatusCondition),
        defender_hp_pct      = _hp(),
        defender_stages      = random_stat_stages(),
        defender_item        = _pick(Item),
        defender_item_effect = _pick(HeldItemEffect),
        defender_gender      = _pick(Gender),

        weather              = _pick(Weather),
        speed_compare        = _pick(SpeedCompare),
    )


# Property runner

class PropertyResult:
    def __init__(self, name: str, trials: int):
        self.name = name
        self.trials = trials
        self.failures: list[tuple[BattleState, str]] = []

    @property
    def passed(self) -> bool:
        return len(self.failures) == 0

    def __repr__(self):
        if self.passed:
            return f"[PASS] {self.name} — {self.trials} trials, 0 failures"
        lines = [f"[FAIL] {self.name} — {len(self.failures)} failure(s) in {self.trials} trials"]
        for state, reason in self.failures[:3]:  # show up to 3
            lines.append(f"  Reason  : {reason}")
            lines.append(f"  State   : {_summarise(state)}")
        return "\n".join(lines)


def _summarise(state: BattleState) -> str:
    """Compact one-liner summary of the fields most relevant to failures."""
    return (
        f"atk_ability={state.attacker_ability.name} "
        f"def_ability={state.defender_ability.name} "
        f"move_type={state.move_type.name} "
        f"effectiveness={state.effectiveness.name} "
        f"atk_status={state.attacker_status.name} "
        f"def_status={state.defender_status.name} "
        f"atk_hp={state.attacker_hp_pct} "
        f"def_hp={state.defender_hp_pct} "
        f"atk_item={state.attacker_item.name} "
        f"def_item={state.defender_item.name} "
        f"atk_item_eff={state.attacker_item_effect.name} "
        f"def_item_eff={state.defender_item_effect.name} "
        f"speed={state.speed_compare.name} "
        f"weather={state.weather.name} "
        f"atk_t1={state.attacker_type1.name} "
        f"def_t1={state.defender_type1.name} "
        f"def_eva={state.defender_stages.evasion}"
    )


def check_property(
    name: str,
    predicate: Callable[[BattleState], Optional[str]],
    trials: int = 10_000,
    seed: int = 42,
) -> PropertyResult:
    """
    Run `predicate(state)` for `trials` random states.
    predicate should return None on pass, or a string describing the failure.
    """
    RNG.seed(seed)
    result = PropertyResult(name, trials)
    for _ in range(trials):
        state = generate_state()
        failure_reason = predicate(state)
        if failure_reason is not None:
            result.failures.append((copy.deepcopy(state), failure_reason))
    return result


# Targeted generators
# Produce states guaranteed to exercise a specific condition so we can
# confirm the buggy path is actually reachable (not just randomly missed).

def state_with_defender_ability(ability: Ability, **overrides) -> BattleState:
    s = generate_state()
    s.defender_ability = ability
    s.attacker_ability = Ability.NONE   # ensure mold breaker doesn't skip
    for k, v in overrides.items():
        setattr(s, k, v)
    return s


def state_with_attacker_ability(ability: Ability, **overrides) -> BattleState:
    s = generate_state()
    s.attacker_ability = ability
    for k, v in overrides.items():
        setattr(s, k, v)
    return s
