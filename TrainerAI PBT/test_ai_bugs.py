"""
PBT for bugs in the Platinum trainer AI script.

Structure per bug:
  1. A property that SHOULD hold
  2. A property that DEMONSTRATES the bug
  3. A targeted test that constructs the exact triggering state
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from pbt_engine import (
    check_property, generate_state, state_with_defender_ability,
    state_with_attacker_ability, RNG,
)
from battle_state import BattleState, NEUTRAL_STAGE
from battle_types import (
    Ability, PokeType, Effectiveness, Weather,
    StatusCondition, BattleEffect, Item, HeldItemEffect, SpeedCompare,
)
from ai_script_translation import (
    ImmunityCheckBug, ImmunityCheckFixed,
    SunnyDayBug, SunnyDayFixed,
    ExpertWaterSpoutBuggy, ExpertWaterSpoutFix,
    ExpertFacadeBuggy, ExpertFacadeFixed,
    ExpertForesightBug, ExpertForesightFixed,
    MetalBurstBuggy, MetalBurstFixed,
)

TRIALS = 50_000
results = []

def record(result):
    results.append(result)
    print(result)
    print()

# BUG 1 — Dry Skin / Levitate (Basic_CheckForImmunity)
print("=" * 70)
print("BUG 1: Dry Skin branch unreachable (labelled Levitate instead)")
print("=" * 70)

# Intent: a defender with Dry Skin against a Water move should be penalised -12
def DrySkinWaterIntent(state: BattleState):
    """Fixed version must penalise Dry Skin + Water."""
    state.defender_ability = Ability.DRY_SKIN
    state.attacker_ability = Ability.NONE
    state.move_type = PokeType.WATER
    state.effectiveness = Effectiveness.NORMAL_DAMAGE
    delta = ImmunityCheckFixed(state)
    if delta != -12:
        return f"Expected -12 for DRY_SKIN + WATER, got {delta}"
    return None

record(check_property(
    "BUG1 [intent] Dry Skin + Water move → always -12",
    DrySkinWaterIntent,
    trials=TRIALS,
))

# Bug: Water attacks are not penalizing Dry Skin
def DrySkinWaterBug(state: BattleState):
    """
    Buggy version: DRY_SKIN defender facing a Water move should score -12
    but the dead-code branch means it NEVER does — score will be 0.
    This function should expect the bug to confirm it exists.
    """
    state.defender_ability = Ability.DRY_SKIN
    state.attacker_ability = Ability.NONE
    state.move_type = PokeType.WATER
    state.effectiveness = Effectiveness.NORMAL_DAMAGE
    delta = ImmunityCheckBug(state)
    if delta == -12:
        return f"Bug appears ABSENT — got -12 (expected 0 due to dead branch)"
    return None

record(check_property(
    "BUG1 [bug] Dry Skin + Water → confirms dead branch (always 0, not -12)",
    DrySkinWaterBug,
    trials=TRIALS,
))

# Show exact divergence
print("  Targeted divergence test (Dry Skin + Water move):")
s = state_with_defender_ability(Ability.DRY_SKIN, move_type=PokeType.WATER,
                                 effectiveness=Effectiveness.NORMAL_DAMAGE)
buggy  = ImmunityCheckBug(s)
fixed  = ImmunityCheckFixed(s)
print(f"    buggy() = {buggy}  (should be -12, is wrong)")
print(f"    fixed() = {fixed}  (correct)")
print()


# BUG 2 — Sunny Day / Hydration interaction
print("=" * 70)
print("BUG 2: Sunny Day checks DEFENDER Hydration instead of ATTACKER")
print("=" * 70)

# Intent: setting Sun when YOUR OWN Hydration is wasted is bad; opponent's is irrelevant
def SunnyHydrationFixed(state: BattleState):
    """Fixed: attacker with Hydration + status → penalised."""
    state.attacker_ability = Ability.HYDRATION
    state.attacker_status  = StatusCondition.POISON
    state.defender_ability = Ability.NONE
    state.weather = Weather.NONE
    delta = SunnyDayFixed(state)
    if delta != -10:
        return f"Expected -10 (attacker Hydration wasted in Sun), got {delta}"
    return None

record(check_property(
    "BUG2 [intent] Attacker has Hydration + status → penalise Sunny Day",
    SunnyHydrationFixed,
    trials=TRIALS,
))

# Bug: defender Hydration + status incorrectly penalises
def SunnyHydrationBug(state: BattleState):
    """Buggy: defender's Hydration + status wrongly scores -10."""
    state.defender_ability = Ability.HYDRATION
    state.defender_status  = StatusCondition.POISON
    state.attacker_ability = Ability.NONE   # no sun-benefit ability
    state.weather = Weather.NONE
    delta = SunnyDayBug(state)
    if delta != -10:
        return f"Bug appears absent: expected -10 from defender Hydration, got {delta}"
    return None

record(check_property(
    "BUG2 [bug] Defender Hydration + status → wrongly penalises Sunny Day (-10)",
    SunnyHydrationBug,
    trials=TRIALS,
))

# Targeted divergence
print("  Targeted divergence (defender Hydration + Poison, attacker no ability):")
s = generate_state()
s.attacker_ability = Ability.NONE
s.defender_ability = Ability.HYDRATION
s.defender_status  = StatusCondition.POISON
s.attacker_status  = StatusCondition.NONE
s.weather          = Weather.NONE
print(f"    buggy() = {SunnyDayBug(s)}  (wrong: -10 from defender)")
print(f"    fixed() = {SunnyDayFixed(s)}  (correct: 0, attacker unaffected)")
print()

print("  Targeted divergence (attacker Hydration + Poison, defender no ability):")
s2 = generate_state()
s2.attacker_ability = Ability.HYDRATION
s2.attacker_status  = StatusCondition.POISON
s2.defender_ability = Ability.NONE
s2.defender_status  = StatusCondition.NONE
s2.weather          = Weather.NONE
print(f"    buggy() = {SunnyDayBug(s2)}  (wrong: 0, misses attacker penalty)")
print(f"    fixed() = {SunnyDayFixed(s2)}  (correct: -10)")
print()

# BUG 3 — Water Spout checks defender HP (Expert_WaterSpout)
print("=" * 70)
print("BUG 3: Water Spout penalty reads DEFENDER HP instead of ATTACKER HP")
print("=" * 70)

# Low attacker HP → penalise Water Spout (weakened)
def WaterSpoutFixed(state: BattleState):
    """Fixed: attacker at 30% HP → penalised even if defender is full HP."""
    state.attacker_hp_pct  = 30
    state.defender_hp_pct  = 100
    state.speed_compare    = SpeedCompare.FASTER
    state.effectiveness    = Effectiveness.NORMAL_DAMAGE
    delta = ExpertWaterSpoutFix(state)
    if delta != -1:
        return f"Expected -1 (attacker low HP), got {delta}"
    return None

record(check_property(
    "BUG3 [intent] Attacker at 30% HP → Water Spout penalised",
    WaterSpoutFixed,
    trials=TRIALS,
))

def WaterSpoutBugged(state: BattleState):
    """
    Buggy: attacker at 5% HP, defender at 100% HP, attacker moves first.
    Should be heavily penalised (Water Spout is nearly useless at 5% HP).
    But the bug means no penalty — defender HP is 100% so no -1 is applied.
    """
    state.attacker_hp_pct  = 5
    state.defender_hp_pct  = 100
    state.speed_compare    = SpeedCompare.FASTER
    state.effectiveness    = Effectiveness.NORMAL_DAMAGE
    delta = ExpertWaterSpoutBuggy(state)
    if delta == -1:
        return f"Bug appears absent: got -1 even though defender HP=100 (unexpected)"
    return None

record(check_property(
    "BUG3 [bug] Attacker 5% HP, defender 100% HP → no penalty (confirms bug)",
    WaterSpoutBugged,
    trials=TRIALS,
))

# Targeted
print("  Targeted (attacker=5% HP, defender=100% HP, faster):")
s = generate_state()
s.attacker_hp_pct = 5
s.defender_hp_pct = 100
s.speed_compare   = SpeedCompare.FASTER
s.effectiveness   = Effectiveness.NORMAL_DAMAGE
print(f"    buggy() = {ExpertWaterSpoutBuggy(s)}  (wrong: 0, ignores dying attacker)")
print(f"    fixed() = {ExpertWaterSpoutFix(s)}  (correct: -1)")
print()

print("  Inverted (attacker=100% HP, defender=5% HP, faster):")
s2 = generate_state()
s2.attacker_hp_pct = 100
s2.defender_hp_pct = 5
s2.speed_compare   = SpeedCompare.FASTER
s2.effectiveness   = Effectiveness.NORMAL_DAMAGE
print(f"    buggy() = {ExpertWaterSpoutBuggy(s2)}  (wrong: -1, penalises full-HP attacker)")
print(f"    fixed() = {ExpertWaterSpoutFix(s2)}  (correct: 0)")
print()

# BUG 4 — Facade checks defender status (Expert_Facade)
print("=" * 70)
print("BUG 4: Facade bonus checks DEFENDER status instead of ATTACKER")
print("=" * 70)

def FacadeFixed(state: BattleState):
    """Fixed: attacker Burned → reward Facade."""
    state.attacker_status = StatusCondition.BURN
    state.defender_status = StatusCondition.NONE
    delta = ExpertFacadeFixed(state)
    if delta != 1:
        return f"Expected +1 for burned attacker, got {delta}"
    return None

record(check_property(
    "BUG4 [intent] Attacker burned → Facade rewarded (+1)",
    FacadeFixed,
    trials=TRIALS,
))

def FacadeBugged(state: BattleState):
    """
    Buggy: attacker burned but defender healthy → should score +1, scores 0.
    Defender burned but attacker healthy → should score 0, scores +1.
    """
    state.attacker_status = StatusCondition.BURN
    state.defender_status = StatusCondition.NONE
    delta_when_attacker_burned = ExpertFacadeBuggy(state)

    state.attacker_status = StatusCondition.NONE
    state.defender_status = StatusCondition.BURN
    delta_when_defender_burned = ExpertFacadeBuggy(state)

    if delta_when_attacker_burned == 1:
        return f"Bug absent: attacker-burned case correctly got +1"
    if delta_when_defender_burned != 1:
        return f"Bug absent: defender-burned case didn't get +1"
    return None  # bug confirmed

record(check_property(
    "BUG4 [bug] Attacker burned→0, defender burned→+1 (confirms backwards check)",
    FacadeBugged,
    trials=TRIALS,
))

print("  Targeted (attacker=BURN, defender=NONE):")
s = generate_state()
s.attacker_status = StatusCondition.BURN
s.defender_status = StatusCondition.NONE
print(f"    buggy() = {ExpertFacadeBuggy(s)}  (wrong: 0)")
print(f"    fixed() = {ExpertFacadeFixed(s)}  (correct: +1)")

print("  Targeted (attacker=NONE, defender=BURN):")
s.attacker_status = StatusCondition.NONE
s.defender_status = StatusCondition.BURN
print(f"    buggy() = {ExpertFacadeBuggy(s)}  (wrong: +1)")
print(f"    fixed() = {ExpertFacadeFixed(s)}  (correct: 0)")
print()

# BUG 5 — Foresight checks attacker type (Expert_Foresight)
print("=" * 70)
print("BUG 5: Foresight bonus checks ATTACKER type for Ghost instead of DEFENDER")
print("=" * 70)

def ForesightGhostFixed(state: BattleState):
    """Fixed: defender is Ghost → reward Foresight."""
    state.defender_type1   = PokeType.GHOST
    state.defender_type2   = PokeType.NORMAL
    state.attacker_type1   = PokeType.NORMAL
    state.attacker_type2   = PokeType.NORMAL
    state.defender_stages.evasion = NEUTRAL_STAGE  # not high
    delta = ExpertForesightFixed(state)
    if delta != 2:
        return f"Expected +2 for Ghost defender, got {delta}"
    return None

record(check_property(
    "BUG5 [intent] Defender is Ghost → Foresight rewarded (+2)",
    ForesightGhostFixed,
    trials=TRIALS,
))

def ForesightBugged(state: BattleState):
    """
    Buggy: ghost DEFENDER → no reward; ghost ATTACKER → reward (backwards).
    """
    # Ghost defender, normal attacker → should reward, doesn't
    state.defender_type1 = PokeType.GHOST
    state.attacker_type1 = PokeType.NORMAL
    state.attacker_type2 = PokeType.NORMAL
    state.defender_stages.evasion = NEUTRAL_STAGE
    delta_ghost_defender = ExpertForesightBug(state)

    # Normal defender, ghost attacker → should NOT reward, does
    state.defender_type1 = PokeType.NORMAL
    state.attacker_type1 = PokeType.GHOST
    state.attacker_type2 = PokeType.NORMAL
    delta_ghost_attacker = ExpertForesightBug(state)

    if delta_ghost_defender == 2:
        return f"Bug absent: ghost-defender correctly got +2"
    if delta_ghost_attacker != 2:
        return f"Bug absent: ghost-attacker didn't incorrectly get +2"
    return None  # confirms bug

record(check_property(
    "BUG5 [bug] Ghost defender→-2, ghost attacker→+2 (confirms backwards check)",
    ForesightBugged,
    trials=TRIALS,
))

print("  Targeted (Ghost DEFENDER, Normal attacker):")
s = generate_state()
s.defender_type1 = PokeType.GHOST
s.defender_type2 = PokeType.NORMAL
s.attacker_type1 = PokeType.NORMAL
s.attacker_type2 = PokeType.NORMAL
s.defender_stages.evasion = NEUTRAL_STAGE
print(f"    buggy() = {ExpertForesightBug(s)}  (wrong: -2 — misses ghost defender)")
print(f"    fixed() = {ExpertForesightFixed(s)}  (correct: +2)")

print("  Targeted (Normal DEFENDER, Ghost attacker):")
s.defender_type1 = PokeType.NORMAL
s.attacker_type1 = PokeType.GHOST
print(f"    buggy() = {ExpertForesightBug(s)}  (wrong: +2 — rewards ghost attacker)")
print(f"    fixed() = {ExpertForesightFixed(s)}  (correct: -2)")
print()

# BUG 6 — Metal Burst checks Shiny Stone not Lagging Tail effect
print("=" * 70)
print("BUG 6: Metal Burst checks item ID (Shiny Stone) instead of Lagging Tail EFFECT")
print("=" * 70)

def MetalBurstIntent(state: BattleState):
    """Fixed: defender with Lagging Tail effect → penalised (-10)."""
    state.defender_item_effect = HeldItemEffect.PRIORITY_DOWN
    state.defender_item        = Item.NONE  # not Shiny Stone
    state.defender_ability     = Ability.NONE
    state.attacker_ability     = Ability.NONE
    state.attacker_item_effect = HeldItemEffect.NONE
    state.effectiveness        = Effectiveness.NORMAL_DAMAGE
    state.speed_compare        = SpeedCompare.SLOWER
    delta = MetalBurstFixed(state)
    if delta != -10:
        return f"Expected -10 for defender Lagging Tail effect, got {delta}"
    return None

record(check_property(
    "BUG6 [intent] Defender has Lagging Tail effect → Metal Burst penalised (-10)",
    MetalBurstIntent,
    trials=TRIALS,
))

def MetalBurstBugged(state: BattleState):
    """
    Buggy:
    - Shiny Stone triggers penalty even though it has no speed effect.
    - Actual Lagging Tail item (without the Shiny Stone ID) is not caught.
    """
    # Shiny Stone should NOT trigger -10, but does
    state.defender_item        = Item.SHINY_STONE
    state.defender_item_effect = HeldItemEffect.NONE   # no lagging tail effect
    state.defender_ability     = Ability.NONE
    state.attacker_ability     = Ability.NONE
    state.attacker_item        = Item.NONE
    state.attacker_item_effect = HeldItemEffect.NONE
    state.effectiveness        = Effectiveness.NORMAL_DAMAGE
    state.speed_compare        = SpeedCompare.SLOWER
    shiny_stone_delta = MetalBurstBuggy(state)

    # Lagging Tail should trigger -10, but doesn't
    state.defender_item        = Item.NONE
    state.defender_item_effect = HeldItemEffect.PRIORITY_DOWN
    lagging_tail_delta = MetalBurstBuggy(state)

    if shiny_stone_delta != -10:
        return f"Bug absent: Shiny Stone didn't trigger -10"
    if lagging_tail_delta == -10:
        return f"Bug absent: Lagging Tail effect correctly triggered -10"
    return None  # bug confirmed

record(check_property(
    "BUG6 [bug] Shiny Stone → wrong -10; Lagging Tail effect → missed (confirms bug)",
    MetalBurstBugged,
    trials=TRIALS,
))

print("  Targeted (defender has Shiny Stone, no Lagging Tail effect):")
s = generate_state()
s.defender_item        = Item.SHINY_STONE
s.defender_item_effect = HeldItemEffect.NONE
s.defender_ability     = Ability.NONE
s.attacker_ability     = Ability.NONE
s.attacker_item        = Item.NONE
s.attacker_item_effect = HeldItemEffect.NONE
s.effectiveness        = Effectiveness.NORMAL_DAMAGE
s.speed_compare        = SpeedCompare.SLOWER
print(f"    buggy() = {MetalBurstBuggy(s)}  (wrong: -10 from irrelevant item)")
print(f"    fixed() = {MetalBurstFixed(s)}  (correct: 0)")

print("  Targeted (defender has Lagging Tail EFFECT, item is not Shiny Stone):")
s.defender_item        = Item.LAGGING_TAIL
s.defender_item_effect = HeldItemEffect.PRIORITY_DOWN
print(f"    buggy() = {MetalBurstBuggy(s)}  (wrong: 0 — misses Lagging Tail)")
print(f"    fixed() = {MetalBurstFixed(s)}  (correct: -10)")
print()

# Summary
print("=" * 70)
print("SUMMARY")
print("=" * 70)
passed = sum(1 for r in results if r.passed)
failed = sum(1 for r in results if not r.passed)
print(f"  Properties checked : {len(results)}")
print(f"  Passed             : {passed}")
print(f"  Failed             : {failed}")
print()
if failed:
    print("UNEXPECTED FAILURES (these indicate a translation error):")
    for r in results:
        if not r.passed:
            print(f"  {r}")
else:
    print("All properties behaved as expected.")
    print("  '[bug]' properties confirmed the bugs exist.")
    print("  '[intent]' properties confirmed the corrections work.")