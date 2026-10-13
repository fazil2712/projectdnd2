import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from ..config import LORE_FILE
from .storage import atomic_write_json


class LoreManager:
    """
    Tier 2 Targeted Lore Indexer.
    Loads campaign lore and selectively formats the prompt context for the active scene.
    """

    def __init__(self, filepath: Optional[Path] = None):
        self.filepath = filepath or LORE_FILE
        self._lock = asyncio.Lock()
        self._lore: Dict[str, Any] = {}
        self._load_initial()

    def _load_initial(self) -> None:
        if self.filepath.exists():
            with open(self.filepath, "r", encoding="utf-8") as f:
                self._lore = json.load(f)
        else:
            self._lore = {
                "campaign_name": "Default Campaign",
                "current_location_id": "starting_room",
                "locations": {},
                "npcs": {},
                "factions": {},
                "current_act": 1,
                "tension_clock": 0,
                "active_enemies": [],
            }
        self._lore.setdefault("current_act", 1)
        self._lore.setdefault("tension_clock", 0)
        self._lore.setdefault("active_enemies", [])
        self._lore.setdefault("locations", {})
        self._lore.setdefault("npcs", {})

    async def get_raw_lore(self) -> Dict[str, Any]:
        async with self._lock:
            return self._lore

    async def get_current_location(self) -> Optional[Dict[str, Any]]:
        async with self._lock:
            loc_id = self._lore.get("current_location_id")
            return self._lore.get("locations", {}).get(loc_id)

    async def set_current_location(
        self,
        name: str,
        description: str = "",
        threat_level: str = "Moderate"
    ) -> bool:
        async with self._lock:
            import re
            clean_name = name.strip()
            found_id = None
            for loc_id, loc_data in self._lore.get("locations", {}).items():
                if loc_id == clean_name or loc_data.get("name", "").lower() == clean_name.lower():
                    found_id = loc_id
                    break

            if found_id:
                self._lore["current_location_id"] = found_id
                if description:
                    self._lore["locations"][found_id]["environment"] = description
                    self._lore["locations"][found_id]["sensory_details"] = description
                if threat_level:
                    self._lore["locations"][found_id]["threat_level"] = threat_level
            else:
                slug = re.sub(r'[^a-z0-9_]', '', clean_name.lower().replace(' ', '_')) or f"loc_{len(self._lore.get('locations', {})) + 1}"
                self._lore.setdefault("locations", {})[slug] = {
                    "id": slug,
                    "name": clean_name,
                    "region": "Active Zone",
                    "environment": description or f"The area around {clean_name}.",
                    "sensory_details": description or f"Atmospheric details of {clean_name}.",
                    "threat_level": threat_level or "Moderate",
                    "lighting": "Ambient atmospheric lighting",
                    "visible_npcs": [],
                    "exits": []
                }
                self._lore["current_location_id"] = slug

            atomic_write_json(self.filepath, self._lore)
            return True

    async def update_npc(
        self,
        name: str,
        role: str = "",
        attitude: str = "neutral",
        note: str = ""
    ) -> Dict[str, Any]:
        async with self._lock:
            import re
            clean_name = name.strip()
            slug = re.sub(r'[^a-z0-9_]', '', clean_name.lower().replace(' ', '_')) or "npc_unknown"
            npcs = self._lore.setdefault("npcs", {})

            if slug in npcs:
                if role:
                    npcs[slug]["role"] = role
                if attitude:
                    npcs[slug]["disposition"] = attitude
                    npcs[slug]["attitude"] = attitude
                if note:
                    npcs[slug]["notes"] = note
                    npcs[slug]["description"] = note
            else:
                npcs[slug] = {
                    "id": slug,
                    "name": clean_name,
                    "role": role or "Adventurer / Denizen",
                    "disposition": attitude or "neutral",
                    "attitude": attitude or "neutral",
                    "description": note or f"{role} ({attitude})",
                    "notes": note,
                }

            atomic_write_json(self.filepath, self._lore)
            return npcs[slug]

    async def advance_story_progress(
        self,
        act: Optional[int] = None,
        tension_delta: int = 0,
        milestone: str = ""
    ) -> Dict[str, Any]:
        async with self._lock:
            if act is not None:
                try:
                    self._lore["current_act"] = max(1, min(3, int(act)))
                except (ValueError, TypeError):
                    pass
            current_tension = int(self._lore.get("tension_clock", 0))
            new_tension = max(0, min(10, current_tension + int(tension_delta)))
            self._lore["tension_clock"] = new_tension

            atomic_write_json(self.filepath, self._lore)
            return {
                "act": self._lore.get("current_act", 1),
                "tension_clock": new_tension,
                "milestone": milestone
            }

    async def get_npcs(self) -> list[Dict[str, Any]]:
        async with self._lock:
            return list(self._lore.get("npcs", {}).values())

    async def get_current_act(self) -> int:
        async with self._lock:
            return int(self._lore.get("current_act", 1))

    async def get_tension_clock(self) -> int:
        async with self._lock:
            return int(self._lore.get("tension_clock", 0))

    async def get_campaign_name(self) -> str:
        async with self._lock:
            return str(self._lore.get("campaign_name", "D&D 5e Adventure"))

    async def get_active_enemies(self) -> list[Dict[str, Any]]:
        async with self._lock:
            return list(self._lore.get("active_enemies", []))

    async def add_or_update_enemy(
        self,
        name: str,
        hp: int,
        ac: int = 12,
        attack_bonus: int = 3,
        damage_formula: str = "1d6+1"
    ) -> Dict[str, Any]:
        async with self._lock:
            clean_name = name.strip()
            enemies = self._lore.setdefault("active_enemies", [])
            existing = next((e for e in enemies if e.get("name", "").lower() == clean_name.lower()), None)

            if existing:
                existing["current_hp"] = int(hp)
                existing["max_hp"] = max(existing.get("max_hp", int(hp)), int(hp))
                existing["ac"] = int(ac)
                existing["attack_bonus"] = int(attack_bonus)
                existing["damage_formula"] = str(damage_formula)
                res = existing
            else:
                enemy_obj = {
                    "name": clean_name,
                    "current_hp": int(hp),
                    "max_hp": int(hp),
                    "ac": int(ac),
                    "attack_bonus": int(attack_bonus),
                    "damage_formula": str(damage_formula),
                }
                enemies.append(enemy_obj)
                res = enemy_obj

            atomic_write_json(self.filepath, self._lore)
            return res

    async def damage_enemy(self, target_name: str, damage_amount: int) -> Dict[str, Any]:
        async with self._lock:
            enemies = self._lore.setdefault("active_enemies", [])
            target = None
            if target_name:
                t_low = target_name.strip().lower()
                target = next((e for e in enemies if t_low in e.get("name", "").lower()), None)
            if not target and enemies:
                target = enemies[0]

            if not target:
                return {"found": False, "summary": f"No active target found for {target_name}."}

            target["current_hp"] = max(0, target["current_hp"] - max(0, int(damage_amount)))
            is_defeated = target["current_hp"] <= 0
            if is_defeated:
                enemies.remove(target)

            atomic_write_json(self.filepath, self._lore)
            return {
                "found": True,
                "enemy": target,
                "damage_dealt": damage_amount,
                "remaining_hp": target["current_hp"],
                "max_hp": target["max_hp"],
                "defeated": is_defeated,
                "summary": f"{target['name']} defeated (0 HP)!" if is_defeated else f"{target['name']} HP: {target['current_hp']}/{target['max_hp']}"
            }

    async def clear_enemies(self) -> None:
        async with self._lock:
            self._lore["active_enemies"] = []
            atomic_write_json(self.filepath, self._lore)

    async def update_campaign_setting(
        self,
        campaign_name: str,
        narrative_tone: str,
        world_setting: str,
        starting_location_name: str,
        starting_location_description: str,
        main_storyline: Optional[Dict[str, Any]] = None
    ) -> None:
        async with self._lock:
            loc_id = "starting_location"
            self._lore["campaign_name"] = campaign_name
            self._lore["narrative_tone"] = narrative_tone
            self._lore["world_setting"] = world_setting
            self._lore["current_location_id"] = loc_id
            self._lore["current_act"] = 1
            self._lore["tension_clock"] = 0
            self._lore["active_enemies"] = []
            if main_storyline:
                self._lore["main_storyline"] = main_storyline
            self._lore["locations"][loc_id] = {
                "id": loc_id,
                "name": starting_location_name,
                "region": "Primary Adventure Hub",
                "environment": starting_location_description,
                "sensory_details": starting_location_description,
                "threat_level": "Moderate",
                "lighting": "Atmospheric ambient lighting",
                "visible_npcs": [],
                "exits": ["outer_realm", "interior_quarters"]
            }
            atomic_write_json(self.filepath, self._lore)

    async def format_targeted_context(self) -> str:
        """
        Builds a compact targeted context string containing only the current
        location, tone, visible NPCs, 3-act story arc, and active combat encounter.
        """
        async with self._lock:
            loc_id = self._lore.get("current_location_id")
            location = self._lore.get("locations", {}).get(loc_id, {})
            npcs = self._lore.get("npcs", {})
            tone = self._lore.get("narrative_tone", "Atmospheric, gritty dark fantasy with visceral second-person descriptions.")
            setting = self._lore.get("world_setting", "D&D 5e Tabletop World")
            storyline = self._lore.get("main_storyline", {})
            current_act = self._lore.get("current_act", 1)
            tension_clock = self._lore.get("tension_clock", 0)
            active_enemies = self._lore.get("active_enemies", [])

            lines = [
                "=== CAMPAIGN WORLD SETTING & NARRATIVE TONE ===",
                f"Campaign: {self._lore.get('campaign_name', 'D&D Campaign')}",
                f"World Setting: {setting}",
                f"Narrative Tone & Style: {tone}",
                f"ACTIVE STORY ACT: Act {current_act}/3 | ANTAGONIST TENSION CLOCK: {tension_clock}/10",
                "MANDATE: Channel this exact tone and genre in all descriptions, pacing, and narrative flavor.\n",
            ]

            if storyline:
                lines.extend([
                    "=== SECRET DM CAMPAIGN STORYLINE (OVERARCHING PLOT ARC - DM EYES ONLY) ===",
                    f"Central Conflict: {storyline.get('central_conflict', 'Survive and unravel the threat.')}",
                    f"Primary Antagonist & Motive: {storyline.get('antagonist', 'A cunning adversary advancing off-screen.')}",
                    f"Current Urgent Threat: {storyline.get('active_threat', 'Immediate danger in the starting area.')}",
                    f"Act 1 Objective: {storyline.get('act_1', 'Investigate the initial disturbance.')}",
                    f"Act 2 Escalation: {storyline.get('act_2', 'Confront the antagonist lieutenant / uncover the conspiracy.')}",
                    f"Act 3 Climax: {storyline.get('act_3', 'Final confrontation to stop the catastrophe.')}",
                    "GUIDANCE: Steer events naturally toward these story milestones while adapting to player agency. If the player delays, the antagonist's plot advances in the background.\n",
                ])

            lines.extend([
                "=== CURRENT ENVIRONMENT (TIER 2 LORE) ===",
                f"Location: {location.get('name', 'Unknown Area')}",
                f"Region: {location.get('region', 'Wilds')}",
                f"Threat Level: {location.get('threat_level', 'Moderate')}",
                f"Sensory & Atmosphere: {location.get('sensory_details', '')}",
                f"Lighting: {location.get('lighting', 'Dim light')}",
            ])

            if npcs:
                lines.append("\n=== KNOWN NPCs & DISPOSITIONS ===")
                for npc_id, npc in npcs.items():
                    name = npc.get("name", npc_id)
                    role = npc.get("role", "")
                    disp = npc.get("disposition") or npc.get("attitude", "neutral")
                    notes = npc.get("notes") or npc.get("description", "")
                    role_str = f" ({role})" if role else ""
                    lines.append(f"- {name}{role_str} [Attitude: {disp}]: {notes}")

            if active_enemies:
                lines.append("\n=== ACTIVE COMBAT ENCOUNTER ===")
                lines.append("Current Enemies:")
                for e in active_enemies:
                    lines.append(
                        f"- {e.get('name')} | HP: {e.get('current_hp')}/{e.get('max_hp')} | AC: {e.get('ac')} | "
                        f"Attack Bonus: +{e.get('attack_bonus')} | Damage: {e.get('damage_formula')}"
                    )
                lines.append("COMBAT RULES: On player attacks, damage is automatically deducted from target HP.")
                lines.append("Enemies attack back using <ENEMY_ATTACK .../> with their attack bonus and damage formula!")

            if location.get("hidden_elements"):
                lines.append(f"\nSecret Notes (DM Only): {location.get('hidden_elements')}")

            return "\n".join(lines)


# Global instance
lore_manager = LoreManager()
