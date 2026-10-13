import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from ..config import CHRONICLE_FILE, CHAT_HISTORY_FILE
from .storage import atomic_write_text, atomic_write_json


class ChronicleManager:
    """
    Tier 3 Rolling Chat History & Persistent Chronicle.
    Maintains a persistent append-only chat log (chat_history.json) for full UI restoration,
    a rolling memory buffer for DM prompts, and a summary chronicle.md file for campaign milestones.
    """

    def __init__(self, filepath: Optional[Path] = None, chat_history_file: Optional[Path] = None, buffer_size: int = 6):
        self.filepath = filepath or CHRONICLE_FILE
        self.chat_history_file = chat_history_file or CHAT_HISTORY_FILE
        self.buffer_size = buffer_size
        self._lock = asyncio.Lock()
        self._turn_history: List[Dict[str, str]] = []  # [{"role": "player"|"dm", "content": "..."}]
        self._chat_entries: List[Dict[str, Any]] = []  # Full persistent UI narrative entries
        self._turn_count: int = 0
        self._last_summarized_index: int = 0
        self._ensure_file()
        self._load_chat_history()

    def _ensure_file(self) -> None:
        if not self.filepath.exists():
            atomic_write_text(
                self.filepath,
                "# Campaign Chronicle\n\n## Chapter 1: The Adventure Begins\n- The journey commenced.\n"
            )

    def _load_chat_history(self) -> None:
        """Loads persistent chat history from JSON on startup."""
        if self.chat_history_file.exists():
            try:
                with open(self.chat_history_file, "r", encoding="utf-8") as f:
                    entries = json.load(f)
                    if isinstance(entries, list):
                        self._chat_entries = entries
                        # In-memory turn history for DM prompts
                        self._turn_history = [
                            {"role": e["role"], "content": e["content"]}
                            for e in entries
                            if e.get("role") in ("player", "dm") and e.get("content")
                        ]
                        self._turn_count = len([e for e in entries if e.get("role") == "player"])
                        self._last_summarized_index = max(0, len(self._turn_history) - (self.buffer_size * 2))
            except Exception as e:
                print("Failed to load chat history:", e)
                self._chat_entries = []

    def _save_chat_history_sync(self) -> None:
        """Saves persistent chat entries to JSON atomically."""
        try:
            atomic_write_json(self.chat_history_file, self._chat_entries)
        except Exception as e:
            print("Failed to save chat history:", e)

    async def get_chat_history(self) -> List[Dict[str, Any]]:
        """Returns the full chronological narrative history for UI restoration (never trimmed)."""
        async with self._lock:
            return list(self._chat_entries)

    async def add_turn(
        self,
        player_action: str,
        dm_narrative: str,
        roll_metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Appends a player turn and DM narrative to persistent chat and memory buffer."""
        async with self._lock:
            now_str = datetime.now().strftime("%H:%M")
            ms_now = int(time.time() * 1000)

            # 1. Player Entry
            player_entry = {
                "id": f"player-{ms_now}",
                "role": "player",
                "content": player_action,
                "timestamp": now_str,
            }
            self._chat_entries.append(player_entry)
            self._turn_history.append({"role": "player", "content": player_action})

            # 2. Optional System Roll Entry
            if roll_metadata and "check_result" in roll_metadata:
                check = roll_metadata["check_result"]
                roll_entry = {
                    "id": f"roll-{ms_now + 1}",
                    "role": "system",
                    "content": check.get("mechanical_summary", "Dice Check Resolved"),
                    "timestamp": now_str,
                    "metadata": {
                        "roll": check,
                        "damage": roll_metadata.get("damage_info")
                    }
                }
                self._chat_entries.append(roll_entry)

            # 3. DM Response Entry
            dm_entry = {
                "id": f"dm-{ms_now + 2}",
                "role": "dm",
                "content": dm_narrative,
                "timestamp": now_str,
            }
            self._chat_entries.append(dm_entry)
            self._turn_history.append({"role": "dm", "content": dm_narrative})

            self._turn_count += 1
            self._save_chat_history_sync()

            # Check if summarization is needed (every 10 turns and backlog exceeds buffer)
            max_messages = self.buffer_size * 2
            if self._turn_count % 10 == 0 and len(self._turn_history) > (max_messages + self._last_summarized_index):
                asyncio.create_task(self._summarize_old_turns())

    async def get_recent_turns(self) -> List[Dict[str, str]]:
        """Returns the rolling buffer of the latest N turns for LLM prompt context."""
        async with self._lock:
            max_messages = self.buffer_size * 2
            return list(self._turn_history[-max_messages:])

    async def get_chronicle_markdown(self) -> str:
        """Reads the summary chronicle.md file."""
        if self.filepath.exists():
            with open(self.filepath, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def _append_milestone_locked(self, bullet_point: str) -> None:
        """Internal helper to append milestone without acquiring self._lock (prevents deadlock)."""
        clean_bullet = bullet_point.strip()
        if not clean_bullet.startswith("-"):
            clean_bullet = f"- {clean_bullet}"
        existing = ""
        if self.filepath.exists():
            with open(self.filepath, "r", encoding="utf-8") as f:
                existing = f.read()
        new_content = f"{existing}\n{clean_bullet}\n" if existing else f"{clean_bullet}\n"
        atomic_write_text(self.filepath, new_content)

    async def append_milestone(self, bullet_point: str) -> None:
        """Appends a new canonical milestone to chronicle.md atomically."""
        async with self._lock:
            self._append_milestone_locked(bullet_point)

    async def reset_chronicle(self, initial_markdown: str = "", initial_dm_narrative: Optional[str] = None) -> None:
        """Flushes turn history, resets chat entries with the new prologue, and rewrites chronicle markdown."""
        async with self._lock:
            self._turn_history.clear()
            self._chat_entries.clear()
            self._turn_count = 0
            self._last_summarized_index = 0

            if initial_dm_narrative:
                self._turn_history.append({"role": "dm", "content": initial_dm_narrative})
                self._chat_entries.append({
                    "id": f"init-{int(time.time() * 1000)}",
                    "role": "dm",
                    "content": initial_dm_narrative,
                    "timestamp": "Prologue"
                })

            self._save_chat_history_sync()
            atomic_write_text(self.filepath, initial_markdown)

    async def _summarize_old_turns(self) -> None:
        """Summarizes newly evicted conversation turns to chronicle.md without re-locking deadlock."""
        async with self._lock:
            max_messages = self.buffer_size * 2
            eviction_cutoff = len(self._turn_history) - max_messages
            if eviction_cutoff <= self._last_summarized_index:
                return

            to_summarize = self._turn_history[self._last_summarized_index:eviction_cutoff]
            self._last_summarized_index = eviction_cutoff

            summary_lines = []
            for item in to_summarize:
                prefix = "Player" if item["role"] == "player" else "DM"
                short = item["content"][:120].replace("\n", " ")
                summary_lines.append(f"{prefix}: {short}...")

            timestamp_str = f"Turn {self._turn_count}"
            milestone = f"**{timestamp_str}**: Recent developments - " + "; ".join(summary_lines[-4:])
            self._append_milestone_locked(milestone)


# Global instance
chronicle_manager = ChronicleManager()
