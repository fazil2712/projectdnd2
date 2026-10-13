import json
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from ..config import CHARACTER_FILE
from ..engine.character import Character, InventoryItem
from .storage import atomic_write_text, atomic_write_json


class StateManager:
    """
    Tier 1 Active State Manager.
    Handles thread-safe persistence and validation of active character sheet,
    equipment slot exclusivity, and pending check states.
    """

    def __init__(self, filepath: Optional[Path] = None):
        self.filepath = filepath or CHARACTER_FILE
        self.pending_check_file = self.filepath.parent / "pending_check.json"
        self._lock = asyncio.Lock()
        self._character: Optional[Character] = None
        self._pending_check: Optional[Dict[str, Any]] = None
        self._load_initial()

    def _load_initial(self) -> None:
        if self.filepath.exists():
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._character = Character(**data)
            except Exception:
                self._character = Character()
                self._save_sync()
        else:
            self._character = Character()
            self._save_sync()

        if self.pending_check_file.exists():
            try:
                with open(self.pending_check_file, "r", encoding="utf-8") as f:
                    self._pending_check = json.load(f)
            except Exception:
                self._pending_check = None

    def _save_sync(self) -> None:
        atomic_write_text(self.filepath, self._character.model_dump_json(indent=2))

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
        """
        Toggles equipped status of an inventory item.
        Enforces 5e equipment slot exclusivity: equipping body armor or shield
        automatically unequips any previously equipped item in that slot category.
        """
        async with self._lock:
            target_item = next((i for i in self._character.inventory if i.id == item_id), None)
            if not target_item:
                return False

            new_status = not target_item.equipped
            target_item.equipped = new_status

            if new_status:
                if target_item.item_type == "armor":
                    # Unequip other body armor
                    for item in self._character.inventory:
                        if item.id != target_item.id and item.item_type == "armor":
                            item.equipped = False
                elif target_item.item_type == "shield":
                    # Unequip other shield
                    for item in self._character.inventory:
                        if item.id != target_item.id and item.item_type == "shield":
                            item.equipped = False

            self._save_sync()
            return target_item.equipped

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

    # Pending Check persistence
    async def get_pending_check(self) -> Optional[Dict[str, Any]]:
        async with self._lock:
            return self._pending_check

    async def set_pending_check(self, pending_data: Dict[str, Any]) -> None:
        async with self._lock:
            self._pending_check = pending_data
            atomic_write_json(self.pending_check_file, pending_data)

    async def clear_pending_check(self) -> None:
        async with self._lock:
            self._pending_check = None
            if self.pending_check_file.exists():
                try:
                    self.pending_check_file.unlink()
                except OSError:
                    pass


# Global instance
state_manager = StateManager()
