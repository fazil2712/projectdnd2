import json
import asyncio
import re
from typing import AsyncGenerator, Dict, Any, List, Optional
import httpx
from ..config import (
    OLLAMA_BASE_URL,
    DEFAULT_MODEL,
    CONTEXT_WINDOW,
    TEMPERATURE,
    TOP_P,
    REPEAT_PENALTY,
    SUPPORTED_MODELS,
)


class OllamaClient:
    """
    Async client for Ollama LLM inference with fallback simulation and background model puller.
    """

    def __init__(self, base_url: str = OLLAMA_BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.active_model = DEFAULT_MODEL
        self.model_download_status: Dict[str, Dict[str, Any]] = {
            m_id: {"status": "available", "progress": 0.0, "total": 0, "completed": 0, "message": ""}
            for m_id in SUPPORTED_MODELS.keys()
        }
        self._pull_lock = asyncio.Lock()
        self._current_pull_task: Optional[asyncio.Task] = None

    async def check_health(self) -> bool:
        """Checks if local Ollama daemon is reachable."""
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False

    async def get_installed_models(self) -> List[str]:
        """Fetches list of downloaded model tags from Ollama."""
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                if resp.status_code == 200:
                    data = resp.json()
                    return [m.get("name", "") for m in data.get("models", [])]
        except Exception:
            pass
        return []

    async def is_model_ready(self, model_name: str) -> bool:
        installed = await self.get_installed_models()
        # Direct match or without tag suffix (e.g. 'llama3.1:8b' or 'llama3.1:latest')
        target_base = model_name.split(":")[0]
        return any(model_name == m or m.startswith(f"{target_base}:") for m in installed)

    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Streams response tokens. Falls back to Simulation DM if model not locally present.
        """
        chosen_model = model or self.active_model
        is_ready = await self.is_model_ready(chosen_model)

        if not is_ready:
            # Fallback Simulation DM for seamless instant gameplay while models download
            async for token in self._simulate_dm_stream(messages, chosen_model):
                yield token
            return

        payload = {
            "model": chosen_model,
            "messages": messages,
            "stream": True,
            "options": {
                "num_ctx": CONTEXT_WINDOW,
                "temperature": TEMPERATURE,
                "top_p": TOP_P,
                "repeat_penalty": REPEAT_PENALTY,
            }
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/chat",
                    json=payload
                ) as response:
                    if response.status_code != 200:
                        async for token in self._simulate_dm_stream(messages, chosen_model):
                            yield token
                        return

                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue
                        try:
                            chunk = json.loads(line)
                            msg = chunk.get("message", {})
                            content = msg.get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
        except Exception:
            # On connection drops or timeout, fallback seamlessly
            async for token in self._simulate_dm_stream(messages, chosen_model):
                yield token

    async def _simulate_dm_stream(
        self,
        messages: List[Dict[str, str]],
        model_name: str
    ) -> AsyncGenerator[str, None]:
        """
        High-fidelity 5e DM simulation engine. Generates realistic atmospheric narrative,
        halts for checks, and rejects impossible actions without hallucinating mechanics.
        """
        last_user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user_msg = m.get("content", "")
                break

        # Check if this is continuing after a mechanical resolution
        if "[MECHANICAL RESOLUTION:" in last_user_msg:
            simulated_response = self._generate_resolution_narrative(last_user_msg)
        else:
            simulated_response = self._generate_action_narrative(last_user_msg)

        # Stream out tokens with natural typing cadences
        words = re.findall(r'\S+|\n|\s+', simulated_response)
        for w in words:
            yield w
            await asyncio.sleep(0.015)

    def _generate_action_narrative(self, action: str) -> str:
        clean = action.lower()

        # Check for physically impossible actions
        if any(w in clean for w in ["fly", "jump 80", "jump 100", "teleport across", "walk through wall"]):
            return (
                '<ACTION_REJECT reason="Mortal physics and lack of wings prevent jumping dozens of feet or flying without magical propulsion."/>\n'
                "You evaluate the impossible leap, but the vast expanse of empty air and gravity firmly assert themselves. "
                "You pull back from the ledge before plunging into disaster. What do you do instead?"
            )

        if "kill everyone" in clean or "destroy the mountain" in clean:
            return (
                '<ACTION_REJECT reason="Such a catastrophic feat exceeds your current mortal capabilities."/>\n'
                "The sheer scale of the environment renders such an instantaneous collapse impossible. What is your actual strategy?"
            )

        # Check for checks: Stealth / Hiding
        if any(w in clean for w in ["sneak", "stealth", "shadow", "slip past", "creep", "stalk"]):
            return (
                "You drop into a low crouch, pulling your dark cloak tight around your shoulders. "
                "The damp limestone underfoot is slick, and every dripping droplet threatens to betray your approach.\n\n"
                '<CHECK_REQUEST type="skill" target="Stealth" dc="13" reason="slipping past the watchful sentries in dim light"/>'
            )

        # Check for lockpicking / sleight of hand
        if any(w in clean for w in ["pick lock", "lockpick", "thieves' tools", "disarm trap", "disable trap"]):
            return (
                "Kneeling before the mechanism, you extract your fine steel tension wrench and slender pick from your tools. "
                "The brass tumblers inside are stiffened by cave moisture.\n\n"
                '<CHECK_REQUEST type="skill" target="Sleight of Hand" dc="14" reason="picking the rusted tumbler lock"/>'
            )

        # Check for Athletics / Climbing
        if any(w in clean for w in ["climb", "scale", "leap", "jump", "swim"]):
            return (
                "You reach for the jagged handholds along the cavern rock. The cold surface is coated in slick wet moss, offering treacherous grip.\n\n"
                '<CHECK_REQUEST type="skill" target="Athletics" dc="14" reason="scaling the moss-covered limestone cliff"/>'
            )

        # Check for Perception / Investigation
        if any(w in clean for w in ["search", "investigate", "look around", "examine", "listen", "inspect"]):
            return (
                "You pause, steadying your breathing as you cast your senses into the damp shadows. "
                "You scrutinize the stone threshold for tripwires, signs of passage, or hidden ambushers.\n\n"
                '<CHECK_REQUEST type="skill" target="Perception" dc="13" reason="searching for concealed hazards and sentries"/>'
            )

        # Check for Attack
        if any(w in clean for w in ["attack", "strike", "shoot", "stab", "slash", "fire"]):
            return (
                "You draw steel with fluid grace, shifting your weight forward into a predatory stance as you line up your strike against your foe!\n\n"
                '<CHECK_REQUEST type="attack" target="Fine Rapier" dc="14" reason="striking at the sentry guard"/>'
            )

        # General exploratory / atmospheric response
        return (
            f"You proceed with caution. The cavern air grows chilled against your skin as condensation patters steadily from the ceiling. "
            f"In the dim light ahead, the rough silhouettes of the rocky passage twist deeper into the subterranean dark. "
            f"A faint draught stirs your hair, bearing the distant scent of woodsmoke and damp earth.\n\n"
            f"The way ahead lies open, but silence is your best ally. How do you wish to proceed?"
        )

    def _generate_resolution_narrative(self, prompt: str) -> str:
        is_success = "Outcome=SUCCESS" in prompt or "NATURAL 20" in prompt or "CRITICAL HIT" in prompt
        is_crit_hit = "CRITICAL HIT" in prompt or "NATURAL 20" in prompt
        is_crit_fail = "CRITICAL MISS" in prompt or "NATURAL 1" in prompt

        if is_crit_hit:
            return (
                "With supernatural precision, you execute the maneuver flawlessly! "
                "Your movements are virtually silent as your blade finds the exact vulnerability in your enemy's defense, "
                "driving true with devastating force. The strike lands cleanly, sending a shudder through your foe!\n\n"
                "The battlefield tilts heavily in your favor. What do you do next?"
            )
        elif is_crit_fail:
            return (
                "Disaster strikes your attempt! A loose stone betrays your footing with a sharp crack that echoes violently "
                "through the cavern. The shock jars your balance, leaving you exposed and immediately alerting nearby ears to your exact position!\n\n"
                "The shadows offer no shelter now. How do you respond?"
            )
        elif is_success:
            return (
                "You execute your action with deft skill and confidence. Your timing proves true, overcoming the resistance of the obstacle. "
                "You gain the upper hand without alerting the surrounding dangers or losing your footing.\n\n"
                "The immediate hurdle is cleared. What is your next move?"
            )
        else:
            return (
                "Despite your best efforts, the challenge proves unforgiving. The slick limestone slips from beneath your fingers, "
                "or the locking mechanism resists your pick with an unyielding metallic groan. You manage to steady yourself before suffering worse injury, "
                "but your attempt has failed.\n\n"
                "You remain in a tense standoff with the environment. What do you do?"
            )

    async def start_sequential_downloads(self) -> None:
        """Starts background download of all 5 supported models in sequence."""
        async with self._pull_lock:
            if self._current_pull_task and not self._current_pull_task.done():
                return
            self._current_pull_task = asyncio.create_task(self._download_worker())

    async def _download_worker(self) -> None:
        """Sequential download worker."""
        # Download order: fast/smaller models first
        order = ["llama3.1:8b", "hermes3:8b", "mistral-nemo:12b", "HammerAI/wayfarer", "qwen2.5:14b"]

        for model_name in order:
            # Check if already installed
            installed = await self.get_installed_models()
            if any(model_name == m or m.startswith(f"{model_name.split(':')[0]}:") for m in installed):
                self.model_download_status[model_name] = {
                    "status": "ready",
                    "progress": 100.0,
                    "total": 0,
                    "completed": 0,
                    "message": "Installed & Ready",
                }
                continue

            self.model_download_status[model_name] = {
                "status": "downloading",
                "progress": 0.0,
                "total": 0,
                "completed": 0,
                "message": "Initiating pull...",
            }

            try:
                async with httpx.AsyncClient(timeout=None) as client:
                    async with client.stream(
                        "POST",
                        f"{self.base_url}/api/pull",
                        json={"name": model_name, "stream": True}
                    ) as response:
                        if response.status_code != 200:
                            self.model_download_status[model_name]["status"] = "failed"
                            self.model_download_status[model_name]["message"] = f"HTTP {response.status_code}"
                            continue

                        async for line in response.aiter_lines():
                            if not line.strip():
                                continue
                            try:
                                data = json.loads(line)
                                status_str = data.get("status", "")
                                total = data.get("total", 0)
                                completed = data.get("completed", 0)
                                progress = (completed / total * 100) if total > 0 else 0.0

                                self.model_download_status[model_name].update({
                                    "status": "downloading" if completed < total or total == 0 else "ready",
                                    "progress": round(progress, 1),
                                    "total": total,
                                    "completed": completed,
                                    "message": status_str,
                                })
                            except Exception:
                                continue

                        self.model_download_status[model_name]["status"] = "ready"
                        self.model_download_status[model_name]["message"] = "Installed & Ready"
            except Exception as e:
                self.model_download_status[model_name]["status"] = "failed"
                self.model_download_status[model_name]["message"] = str(e)


# Global instance
ollama_client = OllamaClient()
