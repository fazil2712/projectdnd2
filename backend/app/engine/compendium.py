import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from ..config import DATA_DIR
from .character import Character, InventoryItem, SpellSlots, SpellSlotLevel
from .rules import apply_heal
from .dice import roll_dice

ITEMS_CATALOG_FILE = DATA_DIR / "items_catalog.json"
SPELLS_CATALOG_FILE = DATA_DIR / "spells_catalog.json"

# 5e Full Caster Spell Slot Table: Level -> {level_1: max, level_2: max, ...}
FULL_CASTER_SLOTS = {
    1: {1: 2},
    2: {1: 3},
    3: {1: 4, 2: 2},
    4: {1: 4, 2: 3},
    5: {1: 4, 2: 3, 3: 2},
    6: {1: 4, 2: 3, 3: 3},
    7: {1: 4, 2: 3, 3: 3, 4: 1},
    8: {1: 4, 2: 3, 3: 3, 4: 2},
    9: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
    10: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
    11: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
    12: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
    13: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
    14: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
    15: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
    16: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
    17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1},
    18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1},
    19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 2, 7: 1, 8: 1, 9: 1},
    20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 2, 7: 2, 8: 1, 9: 1},
}

HALF_CASTER_SLOTS = {
    1: {},
    2: {1: 2},
    3: {1: 3},
    4: {1: 3},
    5: {1: 4, 2: 2},
    6: {1: 4, 2: 2},
    7: {1: 4, 2: 3},
    8: {1: 4, 2: 3},
    9: {1: 4, 2: 3, 3: 2},
    10: {1: 4, 2: 3, 3: 2},
    11: {1: 4, 2: 3, 3: 3},
    12: {1: 4, 2: 3, 3: 3},
    13: {1: 4, 2: 3, 3: 3, 4: 1},
    14: {1: 4, 2: 3, 3: 3, 4: 1},
    15: {1: 4, 2: 3, 3: 3, 4: 2},
    16: {1: 4, 2: 3, 3: 3, 4: 2},
    17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
    18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
    19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
    20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
}


class CompendiumManager:
    """
    Manages loading, searching, and dynamically expanding items & spells.
    Allows the AI DM to invent custom items and permanently catalog them.
    """

    def __init__(self):
        self._items_cache: Dict[str, Any] = {}
        self._spells_cache: Dict[str, Any] = {}
        self._lock = asyncio.Lock()
        self._load_catalogs()

    def _load_catalogs(self) -> None:
        if ITEMS_CATALOG_FILE.exists():
            with open(ITEMS_CATALOG_FILE, "r", encoding="utf-8") as f:
                self._items_cache = json.load(f)
        else:
            self._items_cache = {"armors": [], "weapons": [], "potions_and_consumables": [], "gear_and_tools": [], "custom_campaign_items": []}

        if SPELLS_CATALOG_FILE.exists():
            with open(SPELLS_CATALOG_FILE, "r", encoding="utf-8") as f:
                self._spells_cache = json.load(f)
        else:
            self._spells_cache = {"cantrips": [], "level_1": [], "level_2": [], "level_3": [], "high_level_staples": [], "custom_campaign_spells": []}

    def get_all_items(self) -> Dict[str, Any]:
        return self._items_cache

    def get_all_spells(self) -> Dict[str, Any]:
        return self._spells_cache

    def find_item_in_catalog(self, query: str) -> Optional[Dict[str, Any]]:
        clean_q = query.strip().lower()
        # Search all categories
        for cat in ["weapons", "armors", "potions_and_consumables", "gear_and_tools", "custom_campaign_items"]:
            for item in self._items_cache.get(cat, []):
                if item.get("name", "").lower() == clean_q or item.get("id", "").lower() == clean_q:
                    return item
        # Partial match
        for cat in ["weapons", "armors", "potions_and_consumables", "gear_and_tools", "custom_campaign_items"]:
            for item in self._items_cache.get(cat, []):
                if clean_q in item.get("name", "").lower():
                    return item
        return None

    async def register_custom_item(self, item_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Saves a new custom item invented by the AI DM into items_catalog.json."""
        async with self._lock:
            custom_list = self._items_cache.setdefault("custom_campaign_items", [])
            # Check if exists
            clean_name = item_dict.get("name", "Mysterious Item").strip()
            existing = next((i for i in custom_list if i.get("name", "").lower() == clean_name.lower()), None)
            if existing:
                existing.update(item_dict)
                saved_item = existing
            else:
                new_id = f"custom_{len(custom_list) + 1}_{clean_name.lower().replace(' ', '_')}"
                item_dict["id"] = item_dict.get("id") or new_id
                custom_list.append(item_dict)
                saved_item = item_dict

            with open(ITEMS_CATALOG_FILE, "w", encoding="utf-8") as f:
                json.dump(self._items_cache, f, indent=2)

            return saved_item

    async def grant_item_to_character(
        self,
        character: Character,
        item_data: Dict[str, Any]
    ) -> Tuple[Character, InventoryItem, bool]:
        """
        Adds an item to the character's inventory.
        If the item is not in the base catalog, it is registered into custom_campaign_items.
        Returns (updated_character, granted_item, is_newly_registered).
        """
        name = item_data.get("name", "Unknown Item").strip()
        matched = self.find_item_in_catalog(name)
        is_custom = False

        if not matched:
            # Register newly invented DM item
            matched = await self.register_custom_item(item_data)
            is_custom = True

        # Check if character already has this item
        existing_inv = next((i for i in character.inventory if i.name.lower() == name.lower()), None)
        qty = int(item_data.get("quantity", 1))

        if existing_inv:
            existing_inv.quantity += qty
            return character, existing_inv, is_custom

        # Build InventoryItem
        props = matched.get("properties", [])
        if isinstance(props, str):
            props = [p.strip() for p in props.split(",") if p.strip()]

        new_item = InventoryItem(
            id=matched.get("id", f"item_{len(character.inventory) + 1}"),
            name=matched.get("name", name),
            quantity=qty,
            weight_lbs=float(matched.get("weight_lbs", item_data.get("weight_lbs", 1.0))),
            item_type=matched.get("item_type", item_data.get("type", "gear")),
            equipped=bool(item_data.get("equipped", False)),
            damage=matched.get("damage", item_data.get("damage")),
            damage_type=matched.get("damage_type", item_data.get("damage_type")),
            armor_base=matched.get("armor_base", item_data.get("armor_base")),
            armor_category=matched.get("armor_category", item_data.get("armor_category")),
            properties=props,
            description=matched.get("description", item_data.get("description", "A campaign artifact.")),
        )
        character.inventory.append(new_item)
        return character, new_item, is_custom

    async def consume_item_from_character(
        self,
        character: Character,
        item_name: str,
        quantity: int = 1
    ) -> Tuple[Character, bool, str]:
        """
        Consumes an item from character inventory. If it's a potion, applies deterministic healing.
        Returns (character, success, summary_message).
        """
        clean_name = item_name.strip().lower()
        target_item = next((i for i in character.inventory if clean_name in i.name.lower()), None)

        if not target_item:
            return character, False, f"You do not possess {item_name}."

        # Handle consumption
        target_item.quantity -= quantity
        if target_item.quantity <= 0:
            character.inventory = [i for i in character.inventory if i.id != target_item.id]

        # Check if healing potion
        summary = f"Consumed {quantity}x {target_item.name}."
        if "potion of healing" in target_item.name.lower():
            # 2d4 + 2
            roll = roll_dice("2d4+2")
            heal_res = apply_heal(character, roll["total"])
            summary += f" Restored {heal_res['amount_healed']} HP (Roll: {roll['notation']} -> {roll['total']}). Current HP: {character.current_hp}/{character.max_hp}."
        elif "potion of greater healing" in target_item.name.lower():
            # 4d4 + 4
            roll = roll_dice("4d4+4")
            heal_res = apply_heal(character, roll["total"])
            summary += f" Restored {heal_res['amount_healed']} HP (Roll: {roll['notation']} -> {roll['total']}). Current HP: {character.current_hp}/{character.max_hp}."

        return character, True, summary

    def apply_level_up(
        self,
        character: Character,
        target_level: int,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Applies standard D&D 5e leveling rules:
        - Updates level (clamped 1-20)
        - Updates hit dice maximum
        - Deterministically increases max HP based on class hit die + CON mod
        - Unlocks spell slots according to 5e class progression table
        - Updates proficiency bonus
        """
        prev_level = character.level
        new_level = max(1, min(20, target_level))
        if new_level <= prev_level:
            return {"success": False, "message": f"Target level {new_level} is not higher than current level {prev_level}."}

        cls_lower = character.character_class.lower()
        con_mod = character.ability_modifiers.get("constitution", 0)

        # Hit die value
        if "barbarian" in cls_lower:
            hit_die_val = 12
        elif any(c in cls_lower for c in ["fighter", "paladin", "ranger"]):
            hit_die_val = 10
        elif any(c in cls_lower for c in ["cleric", "druid", "monk", "rogue", "warlock", "bard"]):
            hit_die_val = 8
        else:  # Wizard / Sorcerer
            hit_die_val = 6

        levels_gained = new_level - prev_level
        avg_hp_per_level = max(1, (hit_die_val // 2 + 1) + con_mod)
        hp_increase = levels_gained * avg_hp_per_level

        character.level = new_level
        character.hit_dice_max = new_level
        character.hit_dice_current = min(new_level, character.hit_dice_current + levels_gained)
        character.max_hp += hp_increase
        character.current_hp += hp_increase  # heal the gained amount

        # Spell slots update
        is_full_caster = any(c in cls_lower for c in ["wizard", "sorcerer", "cleric", "druid", "bard"])
        is_half_caster = any(c in cls_lower for c in ["paladin", "ranger"])

        if is_full_caster:
            slot_table = FULL_CASTER_SLOTS.get(new_level, {})
        elif is_half_caster:
            slot_table = HALF_CASTER_SLOTS.get(new_level, {})
        else:
            slot_table = {}

        for lvl_num in range(1, 10):
            max_s = slot_table.get(lvl_num, 0)
            slot_attr = getattr(character.spell_slots, f"level_{lvl_num}", None)
            if slot_attr:
                slot_attr.max_slots = max_s

        summary = (
            f"Level Up! {character.name} advanced from Level {prev_level} to Level {new_level} ({character.character_class}). "
            f"Max HP increased by +{hp_increase} to {character.max_hp}. "
            f"Proficiency Bonus: +{character.proficiency_bonus}. "
            f"Hit Dice: {character.hit_dice_max}{character.hit_die_type}."
        )

        return {
            "success": True,
            "prev_level": prev_level,
            "new_level": new_level,
            "hp_increase": hp_increase,
            "max_hp": character.max_hp,
            "proficiency_bonus": character.proficiency_bonus,
            "summary": summary,
            "reason": reason or "Milestone advancement",
        }


# Global instance
compendium_manager = CompendiumManager()
