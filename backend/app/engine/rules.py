from typing import Dict, List, Optional, Tuple, Any
from .character import Character, InventoryItem, SKILL_TO_ABILITY
from .dice import roll_d20, roll_dice

DC_BENCHMARKS = {
    "Very Easy": 5,
    "Easy": 10,
    "Medium": 15,
    "Hard": 20,
    "Very Hard": 25,
    "Nearly Impossible": 30,
}


def normalize_identifier(text: str) -> str:
    return text.strip().lower().replace(" ", "_").replace("-", "_")


def resolve_check(
    character: Character,
    check_type: str,  # "skill", "save", "ability", "attack"
    target: str,       # e.g., "Stealth", "Dexterity", "Rapier"
    dc: int,
    advantage: bool = False,
    disadvantage: bool = False,
) -> Dict[str, Any]:
    """
    Deterministically resolves a check against a DC or AC.
    Returns roll details, success flag, margin, and mechanical prompt summary for the LLM.
    """
    clean_target = normalize_identifier(target)
    modifier = 0
    resolved_name = target

    if check_type == "skill":
        if clean_target in character.skill_bonuses:
            modifier = character.skill_bonuses[clean_target]
            resolved_name = clean_target.replace("_", " ").title() + " (Skill)"
        else:
            # Fallback: check if target is an ability name
            if clean_target in character.ability_modifiers:
                modifier = character.ability_modifiers[clean_target]
                resolved_name = clean_target.title() + " (Ability)"
            else:
                modifier = 0

    elif check_type == "save":
        if clean_target in character.saving_throw_bonuses:
            modifier = character.saving_throw_bonuses[clean_target]
            resolved_name = clean_target.title() + " Saving Throw"
        else:
            modifier = character.ability_modifiers.get(clean_target, 0)
            resolved_name = clean_target.title() + " Save"

    elif check_type == "attack":
        # Check equipped weapon
        weapon = next(
            (i for i in character.inventory if normalize_identifier(i.name) == clean_target and i.item_type == "weapon"),
            None
        )
        if not weapon:
            # First equipped weapon
            weapon = next((i for i in character.inventory if i.item_type == "weapon" and i.equipped), None)

        if weapon:
            is_finesse_or_ranged = any(p.lower() in ["finesse", "ranged", "range"] for p in weapon.properties)
            if is_finesse_or_ranged:
                mod_stat = max(character.ability_modifiers["strength"], character.ability_modifiers["dexterity"])
            else:
                mod_stat = character.ability_modifiers["strength"]
            modifier = mod_stat + character.proficiency_bonus
            resolved_name = f"{weapon.name} Attack"
        else:
            # Unarmed strike
            modifier = character.ability_modifiers["strength"] + character.proficiency_bonus
            resolved_name = "Unarmed Strike"

    else:  # Raw ability
        modifier = character.ability_modifiers.get(clean_target, 0)
        resolved_name = clean_target.title() + " Check"

    # Check for innate racial advantages (silent mechanical benefits)
    race_lower = (character.race or "").lower()
    racial_advantage = False
    racial_reason = None

    if check_type == "save":
        if "dwarf" in race_lower and ("poison" in clean_target or "toxic" in clean_target):
            racial_advantage = True
            racial_reason = "Dwarven Resilience (Advantage vs Poison)"
        elif any(r in race_lower for r in ["elf", "half_elf", "half-elf"]) and ("charm" in clean_target or "sleep" in clean_target):
            racial_advantage = True
            racial_reason = "Fey Ancestry (Advantage vs Charm)"
        elif "halfling" in race_lower and ("frighten" in clean_target or "fear" in clean_target):
            racial_advantage = True
            racial_reason = "Brave (Advantage vs Frightened)"
        elif "gnome" in race_lower and any(stat in clean_target for stat in ["intelligence", "wisdom", "charisma", "magic"]):
            racial_advantage = True
            racial_reason = "Gnome Cunning (Advantage on INT/WIS/CHA saves vs magic)"

    effective_advantage = advantage or racial_advantage

    roll_result = roll_d20(modifier=modifier, advantage=effective_advantage, disadvantage=disadvantage)
    if racial_reason:
        roll_result["racial_advantage"] = racial_reason

    total = roll_result["total"]
    raw = roll_result["selected_raw"]

    # Halfling Lucky trait: If rolled a natural 1, reroll die once
    if "halfling" in race_lower and raw == 1:
        reroll_res = roll_d20(modifier=modifier, advantage=False, disadvantage=False)
        roll_result["lucky_reroll"] = True
        roll_result["prior_raw"] = raw
        roll_result["raw_rolls"].append(reroll_res["selected_raw"])
        roll_result["selected_raw"] = reroll_res["selected_raw"]
        roll_result["total"] = reroll_res["total"]
        raw = reroll_res["selected_raw"]
        total = reroll_res["total"]
        roll_result["notation"] += f" [Halfling Lucky: rerolled nat 1 to {raw}]"

    if check_type == "attack":
        if raw == 20:
            success = True
            crit_note = "CRITICAL HIT"
        elif raw == 1:
            success = False
            crit_note = "CRITICAL MISS"
        else:
            success = total >= dc
            crit_note = None
    else:
        if raw == 20:
            success = True
            crit_note = "NATURAL 20"
        elif raw == 1:
            success = False
            crit_note = "NATURAL 1"
        else:
            success = total >= dc
            crit_note = None

    margin = total - dc
    outcome_str = "SUCCESS" if success else "FAILURE"
    if crit_note:
        outcome_str = f"{crit_note} ({outcome_str})"

    # Structured summary for LLM injection
    mechanical_summary = (
        f"[MECHANICAL RESOLUTION: Check={resolved_name} | DC/AC={dc} | "
        f"Roll={roll_result['notation']} | Outcome={outcome_str} (Margin: {margin:+d})]"
    )

    return {
        "check_type": check_type,
        "target": target,
        "resolved_name": resolved_name,
        "dc": dc,
        "modifier": modifier,
        "roll": roll_result,
        "success": success,
        "margin": margin,
        "crit_note": crit_note,
        "mechanical_summary": mechanical_summary,
    }


def resolve_attack_damage(
    character: Character,
    weapon_name: Optional[str] = None,
    is_critical: bool = False
) -> Dict[str, Any]:
    """
    Rolls damage for an equipped weapon or unarmed strike.
    Doubles damage dice on critical hit.
    """
    weapon = None
    if weapon_name:
        clean_name = normalize_identifier(weapon_name)
        weapon = next((i for i in character.inventory if normalize_identifier(i.name) == clean_name), None)

    if not weapon:
        weapon = next((i for i in character.inventory if i.item_type == "weapon" and i.equipped), None)

    if weapon and weapon.damage:
        dmg_formula = weapon.damage
        dmg_type = weapon.damage_type or "physical"
        is_finesse_or_ranged = any(p.lower() in ["finesse", "ranged", "range"] for p in weapon.properties)
        stat_mod = (
            max(character.ability_modifiers["strength"], character.ability_modifiers["dexterity"])
            if is_finesse_or_ranged else character.ability_modifiers["strength"]
        )
        mod_sign = f"+{stat_mod}" if stat_mod >= 0 else f"{stat_mod}"
        expr = f"{dmg_formula}{mod_sign}"
        name = weapon.name
    else:
        # Unarmed strike: 1 + STR mod bludgeoning
        str_mod = character.ability_modifiers["strength"]
        expr = f"1d1+{str_mod}"
        dmg_type = "bludgeoning"
        name = "Unarmed Strike"

    dmg_roll = roll_dice(expr, is_critical=is_critical)
    dmg_total = max(1, dmg_roll["total"])

    return {
        "weapon_name": name,
        "damage_type": dmg_type,
        "damage_total": dmg_total,
        "dice_breakdown": dmg_roll["notation"],
        "is_critical": is_critical,
        "summary": f"{dmg_total} {dmg_type} damage ({dmg_roll['notation']})",
    }


def validate_inventory_item(
    character: Character,
    item_query: str,
    required_quantity: int = 1
) -> Tuple[bool, Optional[InventoryItem], str]:
    """
    Verifies that the character has the requested item in sufficient quantity.
    """
    clean_query = normalize_identifier(item_query)
    found = next(
        (i for i in character.inventory if clean_query in normalize_identifier(i.name)),
        None
    )
    if not found:
        return False, None, f"You do not possess '{item_query}' in your inventory."

    if found.quantity < required_quantity:
        return False, found, f"You only have {found.quantity} of '{found.name}', but {required_quantity} is required."

    return True, found, f"Item '{found.name}' verified ({found.quantity} available)."


def validate_and_consume_spell_slot(
    character: Character,
    slot_level: int
) -> Tuple[bool, str]:
    """
    Checks if a spell slot of level 1..9 is available, and consumes one if available.
    """
    if slot_level < 1 or slot_level > 9:
        return False, f"Invalid spell slot level: {slot_level}. Must be between 1 and 9."

    attr_name = f"level_{slot_level}"
    slot_obj = getattr(character.spell_slots, attr_name, None)
    if not slot_obj:
        return False, f"No slot matrix found for level {slot_level}."

    if slot_obj.used_slots >= slot_obj.max_slots:
        return False, f"No level {slot_level} spell slots remaining ({slot_obj.used_slots}/{slot_obj.max_slots} used)."

    slot_obj.used_slots += 1
    return True, f"Consumed 1 Level {slot_level} spell slot ({slot_obj.used_slots}/{slot_obj.max_slots} now used)."


def apply_damage(character: Character, amount: int, is_critical: bool = False) -> Dict[str, Any]:
    """
    Deduct damage from temporary HP first, then current HP.
    Tracks if character drops to 0 HP and becomes unconscious.
    If taking damage while already at 0 HP, suffers 1 death save failure (2 on critical hit).
    """
    was_at_zero = character.current_hp <= 0
    damage_remaining = max(0, amount)
    temp_lost = 0
    hp_lost = 0

    if character.temp_hp > 0:
        if character.temp_hp >= damage_remaining:
            character.temp_hp -= damage_remaining
            temp_lost = damage_remaining
            damage_remaining = 0
        else:
            damage_remaining -= character.temp_hp
            temp_lost = character.temp_hp
            character.temp_hp = 0

    if damage_remaining > 0:
        hp_lost = min(character.current_hp, damage_remaining)
        character.current_hp -= hp_lost

    became_unconscious = False
    race_lower = (character.race or "").lower()
    relentless_triggered = False

    if character.current_hp <= 0:
        if ("half_orc" in race_lower or "half-orc" in race_lower) and "relentless_endurance_used" not in character.conditions:
            character.current_hp = 1
            character.conditions.append("relentless_endurance_used")
            relentless_triggered = True
        else:
            became_unconscious = "unconscious" not in character.conditions
            if "unconscious" not in character.conditions:
                character.conditions.append("unconscious")

            # 5e rule: Taking damage at 0 HP inflicts 1 death save failure (or 2 on a critical hit)
            if was_at_zero and amount > 0:
                failures_added = 2 if is_critical else 1
                character.death_saves.failures = min(3, character.death_saves.failures + failures_added)
                if character.death_saves.failures >= 3 and "dead" not in character.conditions:
                    character.conditions.append("dead")

    return {
        "damage_taken": amount,
        "temp_hp_lost": temp_lost,
        "hp_lost": hp_lost,
        "current_hp": character.current_hp,
        "temp_hp": character.temp_hp,
        "unconscious": character.current_hp <= 0,
        "became_unconscious": became_unconscious,
        "relentless_triggered": relentless_triggered,
        "death_save_failures": character.death_saves.failures,
        "dead": "dead" in character.conditions,
    }


def apply_heal(character: Character, amount: int) -> Dict[str, Any]:
    """
    Heal current HP up to max HP. Clears unconsciousness and resets death saves if HP rises above 0.
    """
    heal_amount = max(0, amount)
    prior_hp = character.current_hp
    character.current_hp = min(character.max_hp, character.current_hp + heal_amount)
    actual_healed = character.current_hp - prior_hp

    revived = False
    if character.current_hp > 0:
        if "unconscious" in character.conditions:
            character.conditions.remove("unconscious")
        character.death_saves.successes = 0
        character.death_saves.failures = 0
        if prior_hp == 0:
            revived = True

    return {
        "amount_healed": actual_healed,
        "current_hp": character.current_hp,
        "max_hp": character.max_hp,
        "revived": revived,
    }


def resolve_death_save(character: Character) -> Dict[str, Any]:
    """
    Deterministically rolls a 5e death saving throw for a character at 0 HP.
    - Natural 20: Character regains 1 HP, wakes up, and resets death saves.
    - Natural 1: Adds 2 death save failures.
    - 10-19: Adds 1 death save success.
    - 2-9: Adds 1 death save failure.
    - Reaching 3 successes: Character stabilizes, recovers to 1 HP, wakes up, and resets death saves.
    - Reaching 3 failures: Character dies.
    """
    roll = roll_d20(modifier=0, advantage=False, disadvantage=False)
    raw = roll["selected_raw"]

    # Halfling Lucky trait
    if "halfling" in (character.race or "").lower() and raw == 1:
        reroll_res = roll_d20(modifier=0, advantage=False, disadvantage=False)
        roll["lucky_reroll"] = True
        roll["raw_rolls"].append(reroll_res["selected_raw"])
        roll["selected_raw"] = reroll_res["selected_raw"]
        raw = reroll_res["selected_raw"]
        roll["notation"] += f" [Halfling Lucky: rerolled nat 1 to {raw}]"

    stabilized = False
    died = False
    summary = ""

    if raw == 20:
        character.current_hp = 1
        character.death_saves.successes = 0
        character.death_saves.failures = 0
        if "unconscious" in character.conditions:
            character.conditions.remove("unconscious")
        stabilized = True
        summary = "Natural 20! A surge of vital adrenaline shocks you back to life. You regain 1 HP and regain consciousness!"
    elif raw == 1:
        character.death_saves.failures = min(3, character.death_saves.failures + 2)
        summary = f"Critical Failure (Nat 1)! Suffer 2 death save failures ({character.death_saves.successes} successes, {character.death_saves.failures}/3 failures)."
    elif raw >= 10:
        character.death_saves.successes = min(3, character.death_saves.successes + 1)
        summary = f"Success (Rolled {raw})! ({character.death_saves.successes}/3 successes, {character.death_saves.failures}/3 failures)."
    else:
        character.death_saves.failures = min(3, character.death_saves.failures + 1)
        summary = f"Failure (Rolled {raw})! ({character.death_saves.successes}/3 successes, {character.death_saves.failures}/3 failures)."

    if not stabilized and character.death_saves.successes >= 3:
        # Solo campaign stabilization: 3 successes -> recover to 1 HP, wake up, reset saves
        character.current_hp = 1
        character.death_saves.successes = 0
        character.death_saves.failures = 0
        if "unconscious" in character.conditions:
            character.conditions.remove("unconscious")
        stabilized = True
        summary += " 3 Successes reached! You stabilize, cling to consciousness, and recover to 1 HP!"

    if character.death_saves.failures >= 3:
        died = True
        if "dead" not in character.conditions:
            character.conditions.append("dead")
        summary += " 3 Failures reached! Your life fades away..."

    return {
        "roll": roll,
        "raw": raw,
        "success": raw >= 10,
        "successes": character.death_saves.successes,
        "failures": character.death_saves.failures,
        "stabilized": stabilized,
        "died": died,
        "current_hp": character.current_hp,
        "mechanical_summary": f"[DEATH SAVING THROW: {summary}]",
        "summary": summary,
    }


STANDARD_ARRAYS_BY_CLASS = {
    "wizard": {"strength": 8, "dexterity": 14, "constitution": 13, "intelligence": 15, "wisdom": 12, "charisma": 10},
    "sorcerer": {"strength": 8, "dexterity": 14, "constitution": 13, "intelligence": 10, "wisdom": 12, "charisma": 15},
    "warlock": {"strength": 8, "dexterity": 14, "constitution": 13, "intelligence": 12, "wisdom": 10, "charisma": 15},
    "fighter": {"strength": 15, "dexterity": 13, "constitution": 14, "intelligence": 8, "wisdom": 12, "charisma": 10},
    "barbarian": {"strength": 15, "dexterity": 14, "constitution": 14, "intelligence": 8, "wisdom": 12, "charisma": 8},
    "paladin": {"strength": 15, "dexterity": 10, "constitution": 13, "intelligence": 8, "wisdom": 12, "charisma": 14},
    "rogue": {"strength": 8, "dexterity": 15, "constitution": 13, "intelligence": 12, "wisdom": 14, "charisma": 10},
    "ranger": {"strength": 10, "dexterity": 15, "constitution": 13, "intelligence": 8, "wisdom": 14, "charisma": 12},
    "cleric": {"strength": 13, "dexterity": 10, "constitution": 14, "intelligence": 8, "wisdom": 15, "charisma": 12},
    "druid": {"strength": 8, "dexterity": 13, "constitution": 14, "intelligence": 12, "wisdom": 15, "charisma": 10},
    "bard": {"strength": 8, "dexterity": 14, "constitution": 13, "intelligence": 10, "wisdom": 12, "charisma": 15},
    "monk": {"strength": 10, "dexterity": 15, "constitution": 13, "intelligence": 8, "wisdom": 14, "charisma": 12},
}


def validate_and_clamp_character_stats(level: int, abilities: Dict[str, int]) -> Dict[str, int]:
    """
    Enforces D&D 5e standard ability score constraints:
    - Minimum score is 3.
    - Max score at levels 1-3 is 18 (standard point buy + racial bonuses).
    - Max score at level 4+ is 20 (standard mortal cap with Ability Score Improvements).
    - Prevents impossible stats (e.g. 100 STR).
    """
    clamped_level = max(1, min(20, level))
    max_stat = 20 if clamped_level >= 4 else 18
    min_stat = 3

    clamped: Dict[str, int] = {}
    for stat in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
        raw_val = abilities.get(stat, 10)
        # Ensure integer
        try:
            val = int(raw_val)
        except (ValueError, TypeError):
            val = 10
        clamped[stat] = max(min_stat, min(max_stat, val))

    return clamped


RACES_5E: List[str] = [
    "Human",
    "Elf",
    "Dwarf",
    "Halfling",
    "Dragonborn",
    "Gnome",
    "Half-Elf",
    "Half-Orc",
    "Tiefling",
]

RACE_TRAITS_5E: Dict[str, Dict[str, Any]] = {
    "Human": {
        "speed": 30,
        "darkvision": 0,
        "traits": [
            "Versatile Adaptation: Extra skill proficiency and versatile training.",
            "Resourceful: Driven and ambitious, adaptable to any climate or discipline."
        ],
        "advantages": "Versatility and adaptability in diverse environments."
    },
    "Elf": {
        "speed": 30,
        "darkvision": 60,
        "traits": [
            "Darkvision: 60ft in dim light and darkness.",
            "Keen Senses: Proficiency in Perception skill.",
            "Fey Ancestry: Advantage on saving throws against being charmed, and magic cannot put you to sleep.",
            "Trance: Meditates deeply for 4 hours instead of sleeping 8 hours."
        ],
        "advantages": "Darkvision 60ft, Keen Senses, Fey Ancestry (adv vs charm, immune to magical sleep), Trance."
    },
    "Dwarf": {
        "speed": 25,
        "darkvision": 60,
        "traits": [
            "Darkvision: 60ft in dim light and darkness.",
            "Dwarven Resilience: Advantage on saving throws against poison, and resistance against poison damage.",
            "Stonecunning: Adds double proficiency bonus to History checks related to stonework."
        ],
        "advantages": "Darkvision 60ft, Dwarven Resilience (adv vs poison, poison resistance), Stonecunning."
    },
    "Halfling": {
        "speed": 25,
        "darkvision": 0,
        "traits": [
            "Lucky: When you roll a 1 on the d20 for an attack, ability check, or save, reroll the die once.",
            "Brave: Advantage on saving throws against being frightened.",
            "Halfling Nimbleness: Can move through the space of any creature larger than your size."
        ],
        "advantages": "Lucky (reroll natural 1s), Brave (adv vs frightened), Halfling Nimbleness."
    },
    "Dragonborn": {
        "speed": 30,
        "darkvision": 0,
        "traits": [
            "Draconic Ancestry: Inherited elemental breath and energy resistance.",
            "Damage Resistance: Inherent resistance to elemental damage type.",
            "Breath Weapon: Can exhale destructive elemental energy in an area."
        ],
        "advantages": "Elemental Damage Resistance, Draconic Breath Weapon."
    },
    "Gnome": {
        "speed": 25,
        "darkvision": 60,
        "traits": [
            "Darkvision: 60ft in dim light and darkness.",
            "Gnome Cunning: Advantage on all Intelligence, Wisdom, and Charisma saving throws against magic."
        ],
        "advantages": "Darkvision 60ft, Gnome Cunning (advantage on INT, WIS, and CHA saves vs magic)."
    },
    "Half-Elf": {
        "speed": 30,
        "darkvision": 60,
        "traits": [
            "Darkvision: 60ft in dim light and darkness.",
            "Fey Ancestry: Advantage on saving throws against being charmed, and magic cannot put you to sleep.",
            "Skill Versatility: Proficiency in two additional skills."
        ],
        "advantages": "Darkvision 60ft, Fey Ancestry (adv vs charm, immune to magical sleep), Skill Versatility."
    },
    "Half-Orc": {
        "speed": 30,
        "darkvision": 60,
        "traits": [
            "Darkvision: 60ft in dim light and darkness.",
            "Menacing: Proficiency in the Intimidation skill.",
            "Relentless Endurance: When reduced to 0 HP but not killed outright, drop to 1 HP instead once per long rest.",
            "Savage Attacks: Roll one extra weapon damage die when scoring a critical hit with a melee weapon."
        ],
        "advantages": "Darkvision 60ft, Relentless Endurance (drop to 1 HP once), Savage Attacks (+1 crit die), Menacing."
    },
    "Tiefling": {
        "speed": 30,
        "darkvision": 60,
        "traits": [
            "Darkvision: 60ft in dim light and darkness.",
            "Hellish Resistance: Resistance to fire damage.",
            "Infernal Legacy: Innate occult magic (Thaumaturgy, Hellish Rebuke)."
        ],
        "advantages": "Darkvision 60ft, Hellish Resistance (fire resistance), Infernal Legacy."
    }
}


