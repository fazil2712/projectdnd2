from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, computed_field, model_validator

SKILL_TO_ABILITY: Dict[str, str] = {
    "athletics": "strength",
    "acrobatics": "dexterity",
    "sleight_of_hand": "dexterity",
    "stealth": "dexterity",
    "arcana": "intelligence",
    "history": "intelligence",
    "investigation": "intelligence",
    "nature": "intelligence",
    "religion": "intelligence",
    "animal_handling": "wisdom",
    "insight": "wisdom",
    "medicine": "wisdom",
    "perception": "wisdom",
    "survival": "wisdom",
    "deception": "charisma",
    "intimidation": "charisma",
    "performance": "charisma",
    "persuasion": "charisma",
}

class InventoryItem(BaseModel):
    id: str
    name: str
    quantity: int = 1
    weight_lbs: float = 1.0
    item_type: str = "gear"  # weapon, armor, shield, potion, scroll, gear, tool, treasure
    equipped: bool = False
    damage: Optional[str] = None  # e.g., "1d8", "1d6"
    damage_type: Optional[str] = None  # slashing, piercing, bludgeoning, fire, etc.
    armor_base: Optional[int] = None  # e.g., 11 for leather, 14 for scale mail, 18 for plate
    armor_category: Optional[str] = None  # light, medium, heavy, shield
    properties: List[str] = Field(default_factory=list)  # finesse, versatile, range, light, heavy
    description: Optional[str] = None


class SpellSlotLevel(BaseModel):
    max_slots: int = 0
    used_slots: int = 0


class SpellSlots(BaseModel):
    level_1: SpellSlotLevel = Field(default_factory=SpellSlotLevel)
    level_2: SpellSlotLevel = Field(default_factory=SpellSlotLevel)
    level_3: SpellSlotLevel = Field(default_factory=SpellSlotLevel)
    level_4: SpellSlotLevel = Field(default_factory=SpellSlotLevel)
    level_5: SpellSlotLevel = Field(default_factory=SpellSlotLevel)
    level_6: SpellSlotLevel = Field(default_factory=SpellSlotLevel)
    level_7: SpellSlotLevel = Field(default_factory=SpellSlotLevel)
    level_8: SpellSlotLevel = Field(default_factory=SpellSlotLevel)
    level_9: SpellSlotLevel = Field(default_factory=SpellSlotLevel)


class AbilityScores(BaseModel):
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10


class DeathSaves(BaseModel):
    successes: int = 0
    failures: int = 0


class Character(BaseModel):
    name: str = "Valerius Shadowbane"
    character_class: str = "Rogue"
    subclass: Optional[str] = None
    level: int = 3
    race: str = "Human"
    alignment: str = "Neutral Good"
    background: str = "Soldier"
    backstory: str = ""
    racial_traits: List[str] = Field(default_factory=list)

    abilities: AbilityScores = Field(default_factory=AbilityScores)

    # HP and Hit Dice
    max_hp: int = 24
    current_hp: int = 24
    temp_hp: int = 0
    hit_dice_max: int = 3
    hit_dice_current: int = 3
    hit_dice_remaining: int = 3
    hit_die_type: str = "d8"
    hit_dice: str = "d8"

    @model_validator(mode="before")
    @classmethod
    def set_hit_dice_defaults(cls, data: Any) -> Any:
        if isinstance(data, dict):
            lvl = data.get("level", 1)
            if "hit_dice_remaining" not in data:
                data["hit_dice_remaining"] = data.get("hit_dice_current", lvl)
            if "hit_dice_current" not in data:
                data["hit_dice_current"] = data.get("hit_dice_remaining", lvl)
            if "hit_dice_max" not in data:
                data["hit_dice_max"] = lvl
            if "hit_die_type" not in data and "hit_dice" in data:
                data["hit_die_type"] = data["hit_dice"]
            elif "hit_dice" not in data and "hit_die_type" in data:
                data["hit_dice"] = data["hit_die_type"]
        return data

    death_saves: DeathSaves = Field(default_factory=DeathSaves)

    # Proficiencies
    saving_throw_proficiencies: List[str] = Field(default_factory=lambda: ["dexterity", "intelligence"])
    skill_proficiencies: List[str] = Field(default_factory=lambda: ["stealth", "sleight_of_hand", "investigation", "perception", "deception"])
    skill_expertise: List[str] = Field(default_factory=lambda: ["stealth", "sleight_of_hand"])

    # Spellcasting
    spellcasting_ability: Optional[str] = "intelligence"  # intelligence, wisdom, charisma
    known_spells: List[str] = Field(default_factory=lambda: ["Mage Hand Legerdemain", "Disguise Self", "Charm Person"])
    spell_slots: SpellSlots = Field(default_factory=lambda: SpellSlots(level_1=SpellSlotLevel(max_slots=2, used_slots=0)))

    # Inventory
    inventory: List[InventoryItem] = Field(default_factory=list)

    # Active conditions (poisoned, blinded, prone, etc.)
    conditions: List[str] = Field(default_factory=list)

    # Speed & Senses
    speed_feet: int = 30
    darkvision_feet: int = 60

    @computed_field
    @property
    def proficiency_bonus(self) -> int:
        return (self.level - 1) // 4 + 2

    @computed_field
    @property
    def ability_modifiers(self) -> Dict[str, int]:
        return {
            "strength": (self.abilities.strength - 10) // 2,
            "dexterity": (self.abilities.dexterity - 10) // 2,
            "constitution": (self.abilities.constitution - 10) // 2,
            "intelligence": (self.abilities.intelligence - 10) // 2,
            "wisdom": (self.abilities.wisdom - 10) // 2,
            "charisma": (self.abilities.charisma - 10) // 2,
        }

    @computed_field
    @property
    def saving_throw_bonuses(self) -> Dict[str, int]:
        bonuses = {}
        for ability, mod in self.ability_modifiers.items():
            bonus = mod
            if ability.lower() in [s.lower() for s in self.saving_throw_proficiencies]:
                bonus += self.proficiency_bonus
            bonuses[ability] = bonus
        return bonuses

    @computed_field
    @property
    def skill_bonuses(self) -> Dict[str, int]:
        bonuses = {}
        for skill, ability in SKILL_TO_ABILITY.items():
            base_mod = self.ability_modifiers[ability]
            mult = 0
            if skill in self.skill_expertise:
                mult = 2
            elif skill in self.skill_proficiencies:
                mult = 1
            bonuses[skill] = base_mod + (mult * self.proficiency_bonus)
        return bonuses

    @computed_field
    @property
    def passive_perception(self) -> int:
        return 10 + self.skill_bonuses.get("perception", self.ability_modifiers["wisdom"])

    @computed_field
    @property
    def armor_class(self) -> int:
        dex_mod = self.ability_modifiers["dexterity"]
        equipped_armor = next(
            (item for item in self.inventory if item.item_type == "armor" and item.equipped),
            None
        )
        equipped_shield = next(
            (item for item in self.inventory if item.item_type == "shield" and item.equipped),
            None
        )

        shield_bonus = 2 if equipped_shield else 0

        if not equipped_armor:
            return 10 + dex_mod + shield_bonus

        category = (equipped_armor.armor_category or "light").lower()
        base = equipped_armor.armor_base or 11

        if category == "light":
            return base + dex_mod + shield_bonus
        elif category == "medium":
            return base + min(dex_mod, 2) + shield_bonus
        elif category == "heavy":
            return base + shield_bonus
        else:
            return 10 + dex_mod + shield_bonus

    @computed_field
    @property
    def spell_save_dc(self) -> Optional[int]:
        if not self.spellcasting_ability:
            return None
        mod = self.ability_modifiers.get(self.spellcasting_ability.lower(), 0)
        return 8 + self.proficiency_bonus + mod

    @computed_field
    @property
    def spell_attack_bonus(self) -> Optional[int]:
        if not self.spellcasting_ability:
            return None
        mod = self.ability_modifiers.get(self.spellcasting_ability.lower(), 0)
        return self.proficiency_bonus + mod

    @computed_field
    @property
    def total_weight_carried(self) -> float:
        return sum(item.weight_lbs * item.quantity for item in self.inventory)

    @computed_field
    @property
    def carrying_capacity_lbs(self) -> float:
        return self.abilities.strength * 15.0

    @computed_field
    @property
    def is_encumbered(self) -> bool:
        return self.total_weight_carried > self.carrying_capacity_lbs
