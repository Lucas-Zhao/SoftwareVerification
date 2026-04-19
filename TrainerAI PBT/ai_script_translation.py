"""
Faithful translation of the relevant sections of the trainer AI script.
Scores:
  negative = AI is discouraged from using the move
  positive = AI is encouraged
  0        = no change
"""

from battle_state import BattleState, NEUTRAL_STAGE
from battle_types import (
    Ability, PokeType, Effectiveness, Weather,
    StatusCondition, BattleEffect, Item, HeldItemEffect, SpeedCompare,
)
def _score(value: int) -> int:
    return value

# BUG 1
# Source location: Basic_CheckForImmunity
# Effect: the Dry Skin water-absorption check is UNREACHABLE because
# Levitate is already checked one line earlier (Basic_CheckGroundAbsorption).
# A Pokemon with Dry Skin will never have its water immunity considered.

def ImmunityCheckBug(state: BattleState) -> int:
    """
    Translated from Basic_CheckForImmunity.
    Contains the Levitate/DrySkip bug verbatim.
    """
    score = 0

    if state.effectiveness == Effectiveness.IMMUNE:
        return -10

    # Mold Breaker skips ability checks
    if state.attacker_ability == Ability.MOLD_BREAKER:
        return score

    ability = state.defender_ability

    if ability == Ability.VOLT_ABSORB:
        if state.move_type == PokeType.ELECTRIC:
            return -12
        return score

    if ability == Ability.MOTOR_DRIVE:
        if state.move_type == PokeType.ELECTRIC:
            return -12
        return score

    if ability == Ability.WATER_ABSORB:
        if state.move_type == PokeType.WATER:
            return -12
        return score

    if ability == Ability.FLASH_FIRE:
        if state.move_type == PokeType.FIRE:
            return -12
        return score

    if ability == Ability.WONDER_GUARD:
        if state.effectiveness in (
            Effectiveness.DOUBLE_DAMAGE,
            Effectiveness.QUADRUPLE_DAMAGE,
        ):
            return score
        return -12

    if ability == Ability.LEVITATE:
        # Ground absorption
        if state.move_type == PokeType.GROUND:
            return -12
        return score

    # BUG: the next check branches on LEVITATE again instead of DRY_SKIN.
    # Since Levitate was already handled above, this branch is DEAD CODE.
    # A defender with Dry Skin will fall through to Basic_NoImmunityAbility
    # and never receive a -12 penalty for Water moves.
    if ability == Ability.LEVITATE:          # <-- should be Ability.DRY_SKIN
        if state.move_type == PokeType.WATER:
            return -12
        return score

    return score  # Basic_NoImmunityAbility


def ImmunityCheckFixed(state: BattleState) -> int:
    """
    Corrected version: the second Levitate check is replaced with Dry Skin.
    """
    score = 0

    if state.effectiveness == Effectiveness.IMMUNE:
        return -10

    if state.attacker_ability == Ability.MOLD_BREAKER:
        return score

    ability = state.defender_ability

    if ability == Ability.VOLT_ABSORB:
        if state.move_type == PokeType.ELECTRIC:
            return -12
        return score

    if ability == Ability.MOTOR_DRIVE:
        if state.move_type == PokeType.ELECTRIC:
            return -12
        return score

    if ability == Ability.WATER_ABSORB:
        if state.move_type == PokeType.WATER:
            return -12
        return score

    if ability == Ability.FLASH_FIRE:
        if state.move_type == PokeType.FIRE:
            return -12
        return score

    if ability == Ability.WONDER_GUARD:
        if state.effectiveness in (
            Effectiveness.DOUBLE_DAMAGE,
            Effectiveness.QUADRUPLE_DAMAGE,
        ):
            return score
        return -12

    if ability == Ability.LEVITATE:
        if state.move_type == PokeType.GROUND:
            return -12
        return score

    # Now correctly checks DRY_SKIN
    if ability == Ability.DRY_SKIN:
        if state.move_type == PokeType.WATER:
            return -12
        return score

    return score

# BUG 2
# Source location: Basic_CheckSunnyDay
#   If the target's ability is Hydration and they are currently statused, score -10.
#
# In Basic_CheckRainDance the same pattern correctly scores -8 (penalising
# Sunny Day when the *target* would heal their status via Hydration in rain,
# which makes no sense in sun). The intention was almost certainly to check
# for the attacker's ability instead, or to check Leaf Guard.

def SunnyDayBug(state: BattleState) -> int:
    """
    Attacker abilities that legitimately benefit from Sun are skipped first.
    Then: if the defender's ability is Hydration and they are statused,
    score -10.  This makes no logical sense — Hydration only works in Rain,
    not Sun, and even if it did you'd want to penalise setting Sun when your
    *own* Pokemon has Hydration, not the opponent's.
    """
    score = 0

    # Attacker has a Sun-benefiting ability → skip the Hydration detour
    if state.attacker_ability in (
        Ability.FLOWER_GIFT,
        Ability.LEAF_GUARD,
        Ability.SOLAR_POWER,
    ):
        pass  # falls through to weather check
    else:
        # BUG: checks DEFENDER Hydration, not attacker and also wrong weather
        if state.defender_ability == Ability.HYDRATION:
            if state.defender_status.is_any():
                score += -10
                return score

    # If weather is already Sun, penalise (score -8)
    if state.weather == Weather.SUNNY:
        score += -8

    return score


def SunnyDayFixed(state: BattleState) -> int:
    """
    Plausible fix: penalise if the *attacker's* Hydration would be wasted
    (Hydration doesn't work in Sun), and only if they are actually statused.
    This mirrors the Rain Dance logic symmetrically.
    """
    score = 0

    if state.attacker_ability in (
        Ability.FLOWER_GIFT,
        Ability.LEAF_GUARD,
        Ability.SOLAR_POWER,
    ):
        pass
    else:
        # FIXED: check ATTACKER Hydration (setting Sun wastes their ability)
        if state.attacker_ability == Ability.HYDRATION:
            if state.attacker_status.is_any():
                score += -10
                return score

    if state.weather == Weather.SUNNY:
        score += -8

    return score

# BUG 3
# Source location: Expert_WaterSpout
#
# Water Spout (and Eruption) deal damage proportional to the USER's HP.
# The AI penalises this move when it detects low HP — but it reads the
# *defender's* HP instead of the attacker's.  A dying attacker will still
# be encouraged to use Water Spout, and a full-HP attacker with a low-HP
# opponent will be incorrectly penalised.

def ExpertWaterSpoutBuggy(state: BattleState) -> int:
    """Reads defender HP when it should read attacker HP."""
    score = 0

    if state.effectiveness in (
        Effectiveness.IMMUNE,
        Effectiveness.QUARTER_DAMAGE,
        Effectiveness.HALF_DAMAGE,
    ):
        score += -1
        return score

    if state.speed_compare == SpeedCompare.SLOWER:
        # BUG: Should check attacker HP, checks defender HP
        if state.defender_hp_pct > 70:
            return score          # no penalty
        score += -1
        return score
    else:
        # BUG: Should be attacker_hp_pct
        if state.defender_hp_pct > 50:
            return score
        score += -1
        return score


def ExpertWaterSpoutFix(state: BattleState) -> int:
    """Corrected: Reads attacker HP."""
    score = 0

    if state.effectiveness in (
        Effectiveness.IMMUNE,
        Effectiveness.QUARTER_DAMAGE,
        Effectiveness.HALF_DAMAGE,
    ):
        score += -1
        return score

    if state.speed_compare == SpeedCompare.SLOWER:
        if state.attacker_hp_pct > 70:   # FIXED
            return score
        score += -1
        return score
    else:
        if state.attacker_hp_pct > 50:   # FIXED
            return score
        score += -1
        return score

# BUG 4
# Source location: Expert_Facade
#
# Facade doubles in power when the USER is statused.  The AI should reward
# using Facade when the attacker (user) has a Burn/Poison/Paralysis.
# Instead it checks the DEFENDER's status.

def ExpertFacadeBuggy(state: BattleState) -> int:
    """Checks defender status."""
    # BUG: should be attacker_status
    if state.defender_status.is_facade_boost():
        return 1
    return 0


def ExpertFacadeFixed(state: BattleState) -> int:
    """Corrected: Checks attacker status."""
    if state.attacker_status.is_facade_boost():
        return 1
    return 0


# BUG 5
# Source location: Expert_Foresight
#
# Foresight lets Normal and Fighting moves hit Ghost types.
# The AI tries to reward this when a Ghost type is present,
# but it checks the ATTACKER's type instead of the DEFENDER's.

def ExpertForesightBug(state: BattleState) -> int:
    """Checks attacker type for Ghost."""
    # BUG: should check defender type
    attacker_is_ghost = (
        state.attacker_type1 == PokeType.GHOST
        or state.attacker_type2 == PokeType.GHOST
    )

    defender_evasion_high = state.defender_stages.evasion > (NEUTRAL_STAGE + 2)  # > +2

    if attacker_is_ghost:
        # ~47% chance of +2 (represented here as deterministic +2 for testing)
        return 2  # ExtraRandomGate → ScorePlus2

    if defender_evasion_high:
        return 2  # second random gate → ScorePlus2

    return -2


def ExpertForesightFixed(state: BattleState) -> int:
    """Corrected: Checks defender type for Ghost."""
    defender_is_ghost = (
        state.defender_type1 == PokeType.GHOST
        or state.defender_type2 == PokeType.GHOST
    )

    defender_evasion_high = state.defender_stages.evasion > (NEUTRAL_STAGE + 2)

    if defender_is_ghost:
        return 2

    if defender_evasion_high:
        return 2

    return -2

# BUG 6
# Source location: Basic_CheckMetalBurst
#
# Metal Burst retaliates with 1.5x the damage received.  It works best when
# the user moves LAST.  The AI tries to penalise it when the opponent has
# a move-last item (Lagging Tail / Full Incense).  But instead of checking
# the held item's EFFECT it compares against the literal item ID SHINY_STONE,
# which has nothing to do with move order.
#
# Similarly for the attacker's item: having Shiny Stone is treated as a reason
# to skip the speed check, when it should be Lagging Tail effect.

def MetalBurstBuggy(state: BattleState) -> int:
    """Checks for Shiny Stone instead of Lagging Tail effect."""
    score = 0

    if state.effectiveness == Effectiveness.IMMUNE:
        return -10

    defender_ability = state.defender_ability
    if defender_ability == Ability.STALL:
        return -10

    # BUG: should check HeldItemEffect == PRIORITY_DOWN (Lagging Tail effect)
    # Instead checks literal item == SHINY_STONE which is unrelated
    if state.defender_item == Item.SHINY_STONE:
        return -10

    attacker_ability = state.attacker_ability
    if attacker_ability == Ability.STALL:
        return score  # terminate (skip speed check)

    # BUG: same wrong item check for attacker
    if state.attacker_item == Item.SHINY_STONE:
        return score  # terminate

    # If attacker is faster → penalise (Metal Burst needs to move second)
    if state.speed_compare == SpeedCompare.FASTER:
        return -10

    return score


def MetalBurstFixed(state: BattleState) -> int:
    """Corrected: Checks HeldItemEffect for Lagging Tail / Full Incense effect."""
    score = 0

    if state.effectiveness == Effectiveness.IMMUNE:
        return -10

    defender_ability = state.defender_ability
    if defender_ability == Ability.STALL:
        return -10

    # FIXED: check the item EFFECT, not a specific item ID
    if state.defender_item_effect == HeldItemEffect.PRIORITY_DOWN:
        return -10

    attacker_ability = state.attacker_ability
    if attacker_ability == Ability.STALL:
        return score

    # FIXED: same for attacker
    if state.attacker_item_effect == HeldItemEffect.PRIORITY_DOWN:
        return score

    if state.speed_compare == SpeedCompare.FASTER:
        return -10

    return score