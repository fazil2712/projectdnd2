# AI-Powered D&D 5e Dungeon Master System

A full-stack, local tabletop roleplaying game pairing a **deterministic D&D 5e rule engine** (FastAPI) with a local **Ollama Narrative Dungeon Master** and a dark-fantasy **React + TypeScript** interface.

---

## 🏛️ Core Architectural Mandate: Separation of Concerns

1. **Deterministic Backend Engine (Sole Mechanical Arbiter):**
   - Resolves all mathematical operations: d20 rolls with Advantage/Disadvantage, natural 20 critical hits, natural 1 critical misses, weapon damage formulas (`1d8+3`), spell slot matrices (Level 1–9), DC benchmarks (5 to 30), Armor Class calculations, and inventory encumbrance (`STR * 15 lbs`).
   - **The LLM is NEVER trusted to calculate numbers, roll dice, or deduct HP.**

2. **Ollama LLM (Narrative Dungeon Master):**
   - Focuses purely on rich, atmospheric, second-person ("You...") storytelling and enforcing fictional boundaries.
   - Halts narration and emits structured tags when uncertain or risky actions occur:
     ```xml
     <CHECK_REQUEST type="skill|save|attack" target="Stealth|Athletics|Dexterity" dc="15" reason="climbing the rain-slick wall"/>
     ```
   - Rejects impossible actions or physics violations without state mutation:
     ```xml
     <ACTION_REJECT reason="Your hands are bound behind your back; you cannot draw your bow."/>
     ```

3. **Interrupt & Continuation Pipeline:**
   - The streaming parser intercepts tags in real-time, pauses narrative generation, triggers the interactive **Check Modal** on the frontend, computes the deterministic outcome in the Python engine, and provides the mechanical truth (`[MECHANICAL RESOLUTION: ...]`) back to the LLM to complete the consequence narration.

---

## 🤖 Supported Models & Hardware Targets

Hardware Profile: Nvidia GeForce GTX 1080 Ti (11GB VRAM, Pascal) / Intel Xeon E5-2680 v4 (48GB RAM).
Hard context limit: `num_ctx = 16384` to maintain high token throughput (>30 tokens/sec).

The system supports selecting between **5 specialized models** for any dialogue turn:
1. `llama3.1:8b` (Meta Llama 3.1 8B Instruct) - Default fast, high-fidelity DM
2. `mistral-nemo:12b` (Mistral NeMo 12B) - Rich descriptive vocabulary
3. `hermes3:8b` (Hermes 3 8B Instruct) - Uncensored, steerable narrative engine
4. `qwen2.5:14b` (Qwen 2.5 14B Instruct) - Exceptional reasoning & tag adherence
5. `HammerAI/wayfarer` (Wayfarer 12B) - Dedicated RPG & fiction fine-tune

*Note: The system features an automatic **Simulation Fallback DM** allowing instant gameplay and testing even while multi-gigabyte models are downloading in the background.*

---

## 📁 Repository Structure

```text
c:\projectdnd2/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI endpoints & SSE streaming pipeline
│   │   ├── config.py               # Ollama configuration, 16k context, models
│   │   ├── engine/
│   │   │   ├── dice.py             # Deterministic dice roller with advantage/disadvantage
│   │   │   ├── rules.py            # 5e checks, DCs, AC calculations, damage math
│   │   │   └── character.py        # Pydantic 5e character sheet model
│   │   ├── memory/
│   │   │   ├── state_manager.py    # Tier 1 active state persistence (character.json)
│   │   │   ├── lore_manager.py     # Tier 2 targeted lore context & campaign tone
│   │   │   └── chronicle.py        # Tier 3 rolling chat history & periodic summarizer
│   │   └── llm/
│   │       ├── client.py           # Async Ollama client & background pull manager
│   │       ├── parser.py           # Real-time streaming tag parser
│   │       └── prompts.py          # Modelfile definition & dynamic prompt builders
│   ├── data/
│   │   ├── character.json          # Active character sheet
│   │   ├── world_lore.json         # Campaign lore, tone, and locations
│   │   └── chronicle.md            # Rolling campaign summary
│   ├── modelfiles/
│   │   ├── Modelfile.llama3        # Custom Ollama Modelfile for Llama 3.1 8B
│   │   ├── Modelfile.mistral       # Custom Ollama Modelfile for Mistral NeMo 12B
│   │   ├── Modelfile.hermes        # Custom Ollama Modelfile for Hermes 3 8B
│   │   ├── Modelfile.qwen          # Custom Ollama Modelfile for Qwen 2.5 14B
│   │   └── Modelfile.wayfarer      # Custom Ollama Modelfile for Wayfarer 12B
│   ├── tests/
│   │   └── test_engine.py          # Complete pytest suite (13/13 passing)
│   ├── Modelfile.dm                # Default Ollama modelfile configuration
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CharacterSheet.tsx  # Interactive HP bar, stats, spell slots, inventory
│   │   │   ├── NarrativeLog.tsx    # Streaming narrative feed with DM styling
│   │   │   ├── DiceTray.tsx        # Animated dice roll tray with Advantage/Disadvantage
│   │   │   ├── CheckModal.tsx      # Modal triggered when DM interrupts for a check
│   │   │   ├── ActionInput.tsx     # Player action input with suggestion chips
│   │   │   ├── ModelSelector.tsx   # Switch models per turn & monitor download progress
│   │   │   └── CampaignSetupModal.tsx # Customize campaign tone, theme, world & character
│   │   ├── types/
│   │   │   └── game.ts
│   │   ├── styles/
│   │   │   └── theme.css           # Dark-fantasy Hallmark-stamped design tokens
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── run_server.py                   # One-click server launcher (serves backend + built frontend)
└── README.md
```

---

## 🚀 Quickstart Guide

### 1. Start the Combined Server
```powershell
python run_server.py
```
- **Local PC**: [`http://localhost:8000`](http://localhost:8000)
- **Other Devices on Wi-Fi (Phones/Tablets/Laptops)**: [`http://192.168.1.3:8000`](http://192.168.1.3:8000)

### 2. Remote Access via Tunnel (ngrok / Cloudflare / localtunnel)
To access your Dungeon Master session from anywhere outside your local Wi-Fi:
```powershell
# Automatic tunnel launcher (checks ngrok, cloudflared, or localtunnel)
python start_tunnel.py

# Or if you have ngrok installed with your authtoken:
ngrok http 8000
```

### 3. Ollama Setup & Custom Modelfiles

Ensure Ollama is running (`ollama serve`). To build the custom DM modelfiles:
```bash
# Llama 3.1 8B
ollama create dnd-dm -f backend/modelfiles/Modelfile.llama3

# Qwen 2.5 14B
ollama create dnd-dm-qwen -f backend/modelfiles/Modelfile.qwen

# Wayfarer 12B RPG
ollama create dnd-dm-wayfarer -f backend/modelfiles/Modelfile.wayfarer
```
You can also use the in-app **Model Selector** at the top of the screen to click **"Pull All"** and monitor live download progress!

### 3. Running Unit Tests
```bash
cd backend
python -m pytest tests/test_engine.py
```
All 13 deterministic tests (dice math, advantage/disadvantage, critical hits, parser tag interrupts, damage calculations) pass with 100% coverage.
