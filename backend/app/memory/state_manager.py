import json
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from ..config import CHARACTER_FILE
from ..engine.character import Character, InventoryItem


class StateManager:
    """
    Tier 1 Active State Manager.
    Handles thread-safe persistence and validation of active character sheet.
    """

    def __init__(self, filepath: Optional[Path] = None):
        self.filepath = filepath or CHARACTER_FILE
        self._lock = asyncio.Lock()
        self._character: Optional[Character] = None
        self._load_initial()

    def _load_initial(self) -> None:
        if self.filepath.exists():
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._character = Character(**data)
        else:
            self._character = Character()
            self._save_sync()

    def _save_sync(self) -> None:
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(self.filepath, "w", encoding="utf-8") as f:
            f.write(self._character.model_dump_json(indent=2))

    async def get_character(self) -> Character:
        async with self._lock:
            if self._character is None:
                self._load_initial()
            return self._character

    async def save_character(self, character: Character) -> None:
        async with self._lock:
            self._character = character
            self._save_sync()

    async def update_from_dict(self, data: Dict[str, Any]) -> Character:
        async with self._lock:
            self._character = Character(**data)
            self._save_sync()
            return self._character

    async def modify_hp(self, delta: int) -> Dict[str, Any]:
        """Adjusts HP. Positive adds, negative damages."""
        async with self._lock:
            from ..engine.rules import apply_damage, apply_heal
            if delta < 0:
                res = apply_damage(self._character, abs(delta))
            else:
                res = apply_heal(self._character, delta)
            self._save_sync()
            return res

    async def toggle_item_equipped(self, item_id: str) -> bool:
        async with self._lock:
            for item in self._character.inventory:
                if item.id == item_id:
                    item.equipped = not item.equipped
                    self._save_sync()
                    return item.equipped
            return False

    async def toggle_spell_slot(self, level: int, slot_index: int) -> Dict[str, int]:
        """Toggle used slots at given spell level."""
        async with self._lock:
            attr = f"level_{level}"
            slot_level = getattr(self._character.spell_slots, attr, None)
            if slot_level:
                if slot_level.used_slots > slot_index:
                    slot_level.used_slots = slot_index
                else:
                    slot_level.used_slots = min(slot_level.max_slots, slot_index + 1)
                self._save_sync()
                return {"level": level, "used": slot_level.used_slots, "max": slot_level.max_slots}
            return {"level": level, "used": 0, "max": 0}


# Global instance
state_manager = StateManager()
