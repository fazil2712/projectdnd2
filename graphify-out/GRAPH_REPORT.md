# Graph Report - projectdnd2  (2026-10-14)

## Corpus Check
- 80 files · ~81,561 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 12 file(s) not represented in the graph (top: (none) 4, .bak 1, .hermes 1)

## Summary
- 643 nodes · 1020 edges · 54 communities (33 shown, 19 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 33 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `915b9af1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- post
- game.ts
- main.py
- package.json
- StreamParser
- compilerOptions
- OllamaClient
- ChronicleManager
- CompendiumManager
- StateManager
- LoreManager
- get
- compilerOptions
- engine/__init__.py
- app/__init__.py
- llm/__init__.py
- memory/__init__.py
- tests/__init__.py
- What You Must Do When Invoked
- What You Must Do When Invoked
- What You Must Do When Invoked
- AI-Powered D&D 5e Dungeon Master System
- graphify reference: extra exports and benchmark
- graphify reference: extra exports and benchmark
- graphify reference: extra exports and benchmark
- graphify reference: query, path, explain
- graphify reference: query, path, explain
- graphify reference: query, path, explain
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- Chronicle of HALP
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- rules/graphify.md
- .agents/skills/graphify/references/extraction-spec.md
- workflows/graphify.md
- CLAUDE.md
- .claude/CLAUDE.md
- .claude/skills/graphify/references/extraction-spec.md
- GEMINI.md
- .gemini/skills/graphify/references/extraction-spec.md

## God Nodes (most connected - your core abstractions)
1. `Character` - 53 edges
2. `LoreManager` - 21 edges
3. `StateManager` - 20 edges
4. `atomic_write_json()` - 19 edges
5. `StreamParser` - 18 edges
6. `ChronicleManager` - 16 edges
7. `compilerOptions` - 16 edges
8. `CompendiumManager` - 14 edges
9. `resolve_check()` - 14 edges
10. `apply_damage()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `CompendiumManager` --uses--> `InventoryItem`  [INFERRED]
  backend/app/engine/compendium.py → backend/app/engine/character.py
- `CompendiumManager` --uses--> `Character`  [INFERRED]
  backend/app/engine/compendium.py → backend/app/engine/character.py
- `reset_game()` --uses--> `Character`  [INFERRED]
  backend/app/main.py → backend/app/engine/character.py
- `StateManager` --uses--> `Character`  [INFERRED]
  backend/app/memory/state_manager.py → backend/app/engine/character.py
- `resolve_check_endpoint()` --uses--> `StreamParser`  [INFERRED]
  backend/app/main.py → backend/app/llm/parser.py

## Import Cycles
- None detected.

## Communities (54 total, 19 thin omitted)

### Community 0 - "post"
Cohesion: 0.07
Nodes (35): ActionRequest, DamageInflictRequest, GrantItemRequest, ItemToggleRequest, learn_spell_endpoint(), LevelUpRequest, manual_grant_item(), manual_level_up() (+27 more)

### Community 1 - "game.ts"
Cohesion: 0.06
Nodes (54): App(), ActionInput(), ActionInputProps, QUICK_ACTIONS, BACKSTORY_SEEDS, CampaignSetupModal(), CampaignSetupModalProps, CLASS_DEFAULT_SPELLS (+46 more)

### Community 2 - "main.py"
Cohesion: 0.06
Nodes (73): AbilityScores, Character, DeathSaves, InventoryItem, BaseModel, SpellSlotLevel, SpellSlots, can_character_learn_spell() (+65 more)

### Community 3 - "package.json"
Cohesion: 0.08
Nodes (24): dependencies, lucide-react, react, react-dom, devDependencies, @types/react, @types/react-dom, typescript (+16 more)

### Community 4 - "StreamParser"
Cohesion: 0.07
Nodes (18): Any, Extracts key-value pairs from attribute string. Supports single quotes, double…, Consumes raw token stream and yields structured events: - {"type": "token",…, Parses LLM streaming tokens in real-time, buffering potential markup tags and…, StreamParser, execute_player_action(), recovery_stream(), Primary action endpoint: Streams narrative from Ollama/Simulation DM,… (+10 more)

### Community 5 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+10 more)

### Community 6 - "OllamaClient"
Cohesion: 0.16
Nodes (8): OllamaClient, High-fidelity 5e DM simulation engine. Generates realistic atmospheric…, Async client for Ollama LLM inference with fallback simulation and background…, Starts background download of all 5 supported models in sequence., Sequential download worker., Checks if local Ollama daemon is reachable., Fetches list of downloaded model tags from Ollama., Streams response tokens. Falls back to Simulation DM if model not locally…

### Community 7 - "ChronicleManager"
Cohesion: 0.09
Nodes (16): ChronicleManager, Any, Path, Tier 3 Rolling Chat History & Persistent Chronicle. Maintains a persistent…, Returns the rolling buffer of the latest N turns for LLM prompt context., Reads the summary chronicle.md file., Internal helper to append milestone without acquiring self._lock (prevents…, Appends a new canonical milestone to chronicle.md atomically. (+8 more)

### Community 8 - "CompendiumManager"
Cohesion: 0.17
Nodes (11): CompendiumManager, find_spell_in_catalog(), Any, InventoryItem, Validates if a character meets 5e rules to learn/prepare a spell: 1. Spell…, Saves a new custom item invented by the AI DM into items_catalog.json., Adds an item to the character's inventory. If the item is not in the base…, Applies standard D&D 5e leveling rules: - Updates level (clamped 1-20) -… (+3 more)

### Community 9 - "StateManager"
Cohesion: 0.13
Nodes (10): Any, Path, Toggle used slots at given spell level., Tier 1 Active State Manager. Handles thread-safe persistence and validation of…, Adds a spell to the character's prepared / known spell list., Removes a spell from the character's prepared / known spell list., Sets the character's prepared / known spell list., Adjusts HP. Positive adds, negative damages. (+2 more)

### Community 10 - "LoreManager"
Cohesion: 0.08
Nodes (22): asyncio, _call_ollama_json(), generate_campaign_world_and_storyline(), generate_fallback_campaign(), _match_archetype(), Any, Dynamically generates campaign title, tone, starting location, 3-act storyline,…, Helper to stream/collect LLM response and parse JSON. (+14 more)

### Community 11 - "get"
Cohesion: 0.20
Nodes (10): get_compendium_items(), get_compendium_spells(), get_game_state(), get_models_status(), Returns complete game state: Character sheet, location lore, chronicle, chat…, Returns download status and readiness of all 5 supported models., Returns the persistent catalog of standard 5e items and custom relics., Returns the catalog of 5e spells. (+2 more)

### Community 13 - "compilerOptions"
Cohesion: 0.25
Nodes (7): compilerOptions, allowSyntheticDefaultImports, composite, module, moduleResolution, skipLibCheck, include

### Community 21 - "What You Must Do When Invoked"
Cohesion: 0.07
Nodes (26): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+18 more)

### Community 22 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 23 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 26 - "AI-Powered D&D 5e Dungeon Master System"
Cohesion: 0.20
Nodes (9): 1. Start the Combined Server, 2. Remote Access via Tunnel (ngrok / Cloudflare / localtunnel), 3. Ollama Setup & Custom Modelfiles, 3. Running Unit Tests, AI-Powered D&D 5e Dungeon Master System, 🏛️ Core Architectural Mandate: Separation of Concerns, 🚀 Quickstart Guide, 📁 Repository Structure (+1 more)

### Community 27 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 29 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 30 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 31 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 32 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 33 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 34 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 35 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 36 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 37 - "Chronicle of HALP"
Cohesion: 0.50
Nodes (3): Chronicle of HALP, Overarching Storyline Arc:, Setting: Shadows over the Sword Coast: The Netherese Cipher (AI-Determined Dynamic Atmosphere)

### Community 38 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 39 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 40 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 41 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 42 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 43 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

## Knowledge Gaps
- **199 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+194 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 353 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Character` connect `main.py` to `CompendiumManager`, `post`, `LoreManager`, `StateManager`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Why does `ChronicleManager` connect `ChronicleManager` to `LoreManager`, `main.py`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Why does `OllamaClient` connect `OllamaClient` to `LoreManager`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `Character` (e.g. with `can_character_learn_spell()` and `CompendiumManager`) actually correct?**
  _`Character` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `StateManager` (e.g. with `Character` and `test_equipment_slot_exclusivity()`) actually correct?**
  _`StateManager` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `StreamParser` (e.g. with `execute_player_action()` and `resolve_check_endpoint()`) actually correct?**
  _`StreamParser` has 8 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `private`, `version` to the rest of the system?**
  _199 weakly-connected nodes found - possible documentation gaps or missing edges._