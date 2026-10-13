import os
from pathlib import Path
from pydantic import BaseModel
from typing import Dict, List

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
CONTEXT_WINDOW = int(os.getenv("CONTEXT_WINDOW", "16384"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.75"))
TOP_P = float(os.getenv("TOP_P", "0.90"))
REPEAT_PENALTY = float(os.getenv("REPEAT_PENALTY", "1.15"))

SUPPORTED_MODELS: Dict[str, Dict[str, str]] = {
    "llama3.1:8b": {
        "id": "llama3.1:8b",
        "name": "Llama 3.1 8B Instruct",
        "description": "Fast, high-fidelity narrative DM with 128k native capability (locked to 16k for GTX 1080 Ti)",
        "vram_approx": "5.2 GB",
    },
    "mistral-nemo:12b": {
        "id": "mistral-nemo:12b",
        "name": "Mistral NeMo 12B",
        "description": "Rich descriptive vocabulary and immersive roleplay nuances",
        "vram_approx": "7.8 GB",
    },
    "hermes3:8b": {
        "id": "hermes3:8b",
        "name": "Hermes 3 8B Instruct",
        "description": "Uncensored, steerable narrative engine built by Nous Research",
        "vram_approx": "5.2 GB",
    },
    "qwen2.5:14b": {
        "id": "qwen2.5:14b",
        "name": "Qwen 2.5 14B Instruct",
        "description": "Exceptional reasoning, rich roleplay dialogue, and strict tag following",
        "vram_approx": "9.5 GB",
    },
    "HammerAI/wayfarer": {
        "id": "HammerAI/wayfarer",
        "name": "Wayfarer 12B (RPG Fine-tune)",
        "description": "Specialized tabletop and adventure fiction fine-tune of Mistral NeMo",
        "vram_approx": "7.8 GB",
    },
}

CHARACTER_FILE = DATA_DIR / "character.json"
LORE_FILE = DATA_DIR / "world_lore.json"
CHRONICLE_FILE = DATA_DIR / "chronicle.md"
CHAT_HISTORY_FILE = DATA_DIR / "chat_history.json"

