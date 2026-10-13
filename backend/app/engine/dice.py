import random
import re
from typing import Dict, List, Optional, Tuple


def roll_d20(
    modifier: int = 0,
    advantage: bool = False,
    disadvantage: bool = False
) -> Dict:
    """
    Roll a deterministic 20-sided die with advantage, disadvantage, or straight.
    If both advantage and disadvantage are True, they cancel out into a straight roll.
    """
    is_advantage = advantage and not disadvantage
    is_disadvantage = disadvantage and not advantage

    if is_advantage or is_disadvantage:
        roll1 = random.randint(1, 20)
        roll2 = random.randint(1, 20)
        raw_rolls = [roll1, roll2]
        if is_advantage:
            selected_raw = max(roll1, roll2)
            dropped_raw = min(roll1, roll2)
        else:
            selected_raw = min(roll1, roll2)
            dropped_raw = max(roll1, roll2)
    else:
        roll1 = random.randint(1, 20)
        raw_rolls = [roll1]
        selected_raw = roll1
        dropped_raw = None

    total = selected_raw + modifier
    is_critical_success = selected_raw == 20
    is_critical_failure = selected_raw == 1

    mod_str = f"+{modifier}" if modifier >= 0 else f"{modifier}"
    if dropped_raw is not None:
        type_str = "ADV" if is_advantage else "DIS"
        notation = f"2d20 ({raw_rolls[0]}, {raw_rolls[1]} [{type_str}: took {selected_raw}]) {mod_str} = {total}"
    else:
        notation = f"1d20 ({selected_raw}) {mod_str} = {total}"

    return {
        "raw_rolls": raw_rolls,
        "selected_raw": selected_raw,
        "dropped_raw": dropped_raw,
        "modifier": modifier,
        "total": total,
        "advantage": is_advantage,
        "disadvantage": is_disadvantage,
        "is_critical_success": is_critical_success,
        "is_critical_failure": is_critical_failure,
        "notation": notation,
    }


def roll_dice(expression: str, is_critical: bool = False) -> Dict:
    """
    Roll arbitrary dice formula (e.g. '1d8+3', '2d6', '8d6', '1d10-1').
    If is_critical is True, doubles the number of dice rolled (5e critical hit rule).
    """
    cleaned = expression.replace(" ", "").lower()
    pattern = r"^(\d+)?d(\d+)([+-]\d+)?$"
    match = re.match(pattern, cleaned)

    if not match:
        raise ValueError(f"Invalid dice expression: '{expression}'")

    num_dice_str, die_sides_str, mod_str = match.groups()
    num_dice = int(num_dice_str) if num_dice_str else 1
    die_sides = int(die_sides_str)
    modifier = int(mod_str) if mod_str else 0

    if is_critical:
        num_dice *= 2

    rolls: List[int] = [random.randint(1, die_sides) for _ in range(num_dice)]
    dice_sum = sum(rolls)
    total = dice_sum + modifier

    mod_display = f"+{modifier}" if modifier > 0 else (f"{modifier}" if modifier < 0 else "")
    crit_tag = " (CRIT)" if is_critical else ""
    notation = f"{num_dice}d{die_sides}{crit_tag} {rolls} {mod_display}".strip() + f" = {total}"

    return {
        "expression": expression,
        "is_critical": is_critical,
        "num_dice": num_dice,
        "die_sides": die_sides,
        "rolls": rolls,
        "dice_sum": dice_sum,
        "modifier": modifier,
        "total": total,
        "notation": notation,
    }
