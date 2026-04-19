"""
Types and constants translated from the trainer AI script.
Names are kept as close to the original as possible so bugs
can be cross-referenced directly with the source.
"""

from enum import Enum, auto

# Abilities (only those referenced by the AI script)
class Ability(Enum):
    NONE            = auto()
    MOLD_BREAKER    = auto()
    VOLT_ABSORB     = auto()
    MOTOR_DRIVE     = auto()
    WATER_ABSORB    = auto()
    FLASH_FIRE      = auto()
    WONDER_GUARD    = auto()
    LEVITATE        = auto()
    DRY_SKIN        = auto()
    SOUNDPROOF      = auto()
    INSOMNIA        = auto()
    VITAL_SPIRIT    = auto()
    IMMUNITY        = auto()
    MAGIC_GUARD     = auto()
    POISON_HEAL     = auto()
    LEAF_GUARD      = auto()
    HYDRATION       = auto()
    LIMBER          = auto()
    WATER_VEIL      = auto()
    DAMP            = auto()
    SUCTION_CUPS    = auto()
    HYPER_CUTTER    = auto()
    SPEED_BOOST     = auto()
    KEEN_EYE        = auto()
    NO_GUARD        = auto()
    OWN_TEMPO       = auto()
    OBLIVIOUS       = auto()
    CLEAR_BODY      = auto()
    WHITE_SMOKE     = auto()
    SIMPLE          = auto()
    STICKY_HOLD     = auto()
    MULTITYPE       = auto()
    TRUANT          = auto()
    SLOW_START      = auto()
    STENCH          = auto()
    RUN_AWAY        = auto()
    PICKUP          = auto()
    HONEY_GATHER    = auto()
    STALL           = auto()
    ROUGH_SKIN      = auto()
    ROCK_HEAD       = auto()
    FLOWER_GIFT     = auto()
    SOLAR_POWER     = auto()
    SWIFT_SWIM      = auto()
    RAIN_DISH       = auto()
    CHLOROPHYLL     = auto()
    ICE_BODY        = auto()
    GUTS            = auto()
    KLUTZ           = auto()

# Types
class PokeType(Enum):
    NORMAL   = auto()
    FIRE     = auto()
    WATER    = auto()
    ELECTRIC = auto()
    GRASS    = auto()
    ICE      = auto()
    FIGHTING = auto()
    POISON   = auto()
    GROUND   = auto()
    FLYING   = auto()
    PSYCHIC  = auto()
    BUG      = auto()
    ROCK     = auto()
    GHOST    = auto()
    DRAGON   = auto()
    DARK     = auto()
    STEEL    = auto()

# Type effectiveness multipliers (as used by AI script constants)
class Effectiveness(Enum):
    IMMUNE           = auto()   # TYPE_MULTI_IMMUNE
    QUARTER_DAMAGE   = auto()   # TYPE_MULTI_QUARTER_DAMAGE
    HALF_DAMAGE      = auto()   # TYPE_MULTI_HALF_DAMAGE
    NORMAL_DAMAGE    = auto()
    DOUBLE_DAMAGE    = auto()   # TYPE_MULTI_DOUBLE_DAMAGE
    QUADRUPLE_DAMAGE = auto()   # TYPE_MULTI_QUADRUPLE_DAMAGE

# Weather
class Weather(Enum):
    NONE      = auto()
    SUNNY     = auto()   # AI_WEATHER_SUNNY
    RAINING   = auto()   # AI_WEATHER_RAINING
    SANDSTORM = auto()   # AI_WEATHER_SANDSTORM
    HAILING   = auto()   # AI_WEATHER_HAILING
    DEEP_FOG  = auto()   # AI_WEATHER_DEEP_FOG

# Status conditions
class StatusCondition(Enum):
    NONE      = auto()
    SLEEP     = auto()
    POISON    = auto()
    TOXIC     = auto()
    BURN      = auto()
    PARALYSIS = auto()
    FREEZE    = auto()

    def is_any(self):
        return self != StatusCondition.NONE

    def is_facade_boost(self):
        """Burn, Poison, Toxic, or Paralysis boost Facade."""
        return self in (
            StatusCondition.BURN,
            StatusCondition.POISON,
            StatusCondition.TOXIC,
            StatusCondition.PARALYSIS,
        )

# Move effects (only those explicitly checked by the sections translated)
class BattleEffect(Enum):
    NONE                        = auto()
    STATUS_SLEEP                = auto()
    HALVE_DEFENSE               = auto()   # Explosion / Self-Destruct
    RECOVER_DAMAGE_SLEEP        = auto()   # Dream Eater
    ATK_UP                      = auto()
    DEF_UP                      = auto()
    SPEED_UP                    = auto()
    SP_ATK_UP                   = auto()
    SP_DEF_UP                   = auto()
    ACC_UP                      = auto()
    EVA_UP                      = auto()
    ATK_DOWN                    = auto()
    DEF_DOWN                    = auto()
    SPEED_DOWN                  = auto()
    SP_ATK_DOWN                 = auto()
    SP_DEF_DOWN                 = auto()
    ACC_DOWN                    = auto()
    EVA_DOWN                    = auto()
    ATK_DOWN_2                  = auto()
    DEF_DOWN_2                  = auto()
    SPEED_DOWN_2                = auto()
    SP_ATK_DOWN_2               = auto()
    SP_DEF_DOWN_2               = auto()
    EVA_DOWN_2                  = auto()   # BUG: label says EVA but code targets ACC
    ACC_DOWN_2                  = auto()   # BUG: label says ACC but code targets EVA
    STATUS_BADLY_POISON         = auto()
    STATUS_POISON               = auto()
    STATUS_PARALYZE             = auto()
    STATUS_BURN                 = auto()
    STATUS_CONFUSE              = auto()
    RESTORE_HALF_HP             = auto()
    HEAL_HALF_MORE_IN_SUN       = auto()
    HEAL_HALF_REMOVE_FLYING_TYPE= auto()
    REST                        = auto()
    RECOVER_HALF_DAMAGE_DEALT   = auto()
    DOUBLE_POWER_WHEN_STATUSED  = auto()   # Facade
    DECREASE_POWER_WITH_LESS_USER_HP = auto()  # Water Spout / Eruption
    SKIP_CHARGE_TURN_IN_SUN     = auto()   # Solar Beam
    WEATHER_RAIN                = auto()
    WEATHER_SUN                 = auto()
    WEATHER_SANDSTORM           = auto()
    WEATHER_HAIL                = auto()
    FORESIGHT                   = auto()
    METAL_BURST                 = auto()

# Items (only those needed for the bugs under test)
class Item(Enum):
    NONE        = auto()
    SHINY_STONE = auto()   # incorrectly checked instead of Lagging Tail
    LAGGING_TAIL= auto()   # what SHOULD be checked for Metal Burst
    POWER_HERB  = auto()

class HeldItemEffect(Enum):
    NONE             = auto()
    PRIORITY_DOWN    = auto()   # Lagging Tail / Full Incense effect
    STALL_EFFECT     = auto()   # not a real constant, placeholder

# Moves (only those explicitly named)
class Move(Enum):
    NONE         = auto()
    FISSURE      = auto()
    HORN_DRILL   = auto()
    THUNDER_WAVE = auto()

# Gender
class Gender(Enum):
    MALE      = auto()
    FEMALE    = auto()
    GENDERLESS= auto()

# Battle stat IDs
class BattleStat(Enum):
    ATTACK    = auto()
    DEFENSE   = auto()
    SPEED     = auto()
    SP_ATTACK = auto()
    SP_DEFENSE= auto()
    ACCURACY  = auto()
    EVASION   = auto()

# Speed comparison results
class SpeedCompare(Enum):
    FASTER = auto()
    SLOWER = auto()
    TIE    = auto()
