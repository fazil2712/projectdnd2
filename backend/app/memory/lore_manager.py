import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from ..config import LORE_FILE


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
            }

    async def get_raw_lore(self) -> Dict[str, Any]:
        async with self._lock:
            return self._lore

    async def get_current_location(self) -> Optional[Dict[str, Any]]:
        async with self._lock:
            loc_id = self._lore.get("current_location_id")
            return self._lore.get("locations", {}).get(loc_id)

    async def set_current_location(self, location_id: str) -> bool:
        async with self._lock:
            if location_id in self._lore.get("locations", {}):
                self._lore["current_location_id"] = location_id
                with open(self.filepath, "w", encoding="utf-8") as f:
                    json.dump(self._lore, f, indent=2)
                return True
            return False

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
            if main_storyline:
                self._lore["main_storyline"] = main_storyline
            self._lore["locations"][loc_id] = {
                "id": loc_id,
                "name": starting_location_name,
                "region": "Primary Adventure Hub",
                "environment": starting_location_description,
                "sensory_details": starting_location_description,
                "lighting": "Atmospheric ambient lighting",
                "visible_npcs": [],
                "exits": ["outer_realm", "interior_quarters"]
            }
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self._lore, f, indent=2)

    async def format_targeted_context(self) -> str:
        """
        Builds a compact targeted context string containing only the current
        location, tone, visible NPCs, and the overarching campaign storyline.
        """
        async with self._lock:
            loc_id = self._lore.get("current_location_id")
            location = self._lore.get("locations", {}).get(loc_id, {})
            npcs = self._lore.get("npcs", {})
            tone = self._lore.get("narrative_tone", "Atmospheric, gritty dark fantasy with visceral second-person descriptions.")
            setting = self._lore.get("world_setting", "D&D 5e Tabletop World")
            storyline = self._lore.get("main_storyline", {})

            lines = [
                "=== CAMPAIGN WORLD SETTING & NARRATIVE TONE ===",
                f"Campaign: {self._lore.get('campaign_name', 'D&D Campaign')}",
                f"World Setting: {setting}",
                f"Narrative Tone & Style: {tone}",
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
                f"Sensory & Atmosphere: {location.get('sensory_details', '')}",
                f"Lighting: {location.get('lighting', 'Dim light')}",
            ])

            visible_npc_ids = location.get("visible_npcs", [])
            if visible_npc_ids:
                lines.append("\nPresent Entities / NPCs:")
                for npc_id in visible_npc_ids:
                    npc = npcs.get(npc_id)
                    if npc:
                        lines.append(
                            f"- {npc.get('name')} ({npc.get('race', 'Unknown')}, HP: {npc.get('hp')}, AC: {npc.get('ac')}): "
                            f"{npc.get('description')} [Disposition: {npc.get('disposition', 'Neutral')}]"
                        )

            if location.get("hidden_elements"):
                lines.append(f"Secret Notes (DM Only): {location.get('hidden_elements')}")

            return "\n".join(lines)




# Global instance
lore_manager = LoreManager()
