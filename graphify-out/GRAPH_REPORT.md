# Graph Report - projectdnd2  (2026-10-14)

## Corpus Check
- 77 files · ~66,134 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 3, .bak 1, .hermes 1)

## Summary
- 546 nodes · 784 edges · 58 communities (37 shown, 19 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 21 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- BaseModel
- App.tsx
- Character
- package.json
- StreamParser
- compilerOptions
- OllamaClient
- ChronicleManager
- CompendiumManager
- StateManager
- LoreManager
- get
- campaign_generator.py
- compilerOptions
- engine/__init__.py
- app/__init__.py
- llm/__init__.py
- memory/__init__.py
- tests/__init__.py
- What You Must Do When Invoked
- What You Must Do When Invoked
- What You Must Do When Invoked
- resolve_check_endpoint
- post
- AI-Powered D&D 5e Dungeon Master System
- graphify reference: extra exports and benchmark
- main.py
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
1. `Character` - 44 edges
2. `compilerOptions` - 16 edges
3. `CompendiumManager` - 13 edges
4. `resolve_check()` - 13 edges
5. `StreamParser` - 13 edges
6. `ChronicleManager` - 13 edges
7. `InventoryItem` - 12 edges
8. `OllamaClient` - 12 edges
9. `StateManager` - 12 edges
10. `What You Must Do When Invoked` - 12 edges

## Surprising Connections (you probably didn't know these)
- `CompendiumManager` --uses--> `InventoryItem`  [INFERRED]
  backend/app/engine/compendium.py → backend/app/engine/character.py
- `CompendiumManager` --uses--> `Character`  [INFERRED]
  backend/app/engine/compendium.py → backend/app/engine/character.py
- `build_system_prompt()` --uses--> `Character`  [INFERRED]
  backend/app/llm/prompts.py → backend/app/engine/character.py
- `reset_game()` --uses--> `Character`  [INFERRED]
  backend/app/main.py → backend/app/engine/character.py
- `StateManager` --uses--> `Character`  [INFERRED]
  backend/app/memory/state_manager.py → backend/app/engine/character.py

## Import Cycles
- None detected.

## Communities (58 total, 19 thin omitted)

### Community 0 - "BaseModel"
Cohesion: 0.15
Nodes (13): ActionRequest, CampaignCreationRequest, DamageInflictRequest, GrantItemRequest, LevelUpRequest, manual_grant_item(), manual_level_up(), BaseModel (+5 more)

### Community 1 - "App.tsx"
Cohesion: 0.09
Nodes (37): App(), ActionInput(), ActionInputProps, QUICK_ACTIONS, BACKSTORY_SEEDS, CampaignSetupModal(), CampaignSetupModalProps, GROUNDED_NAMES_ANIME (+29 more)

### Community 2 - "Character"
Cohesion: 0.08
Nodes (45): AbilityScores, Character, DeathSaves, InventoryItem, BaseModel, SpellSlotLevel, SpellSlots, Consumes an item from character inventory. If it's a potion, applies… (+37 more)

### Community 3 - "package.json"
Cohesion: 0.08
Nodes (24): dependencies, lucide-react, react, react-dom, devDependencies, @types/react, @types/react-dom, typescript (+16 more)

### Community 4 - "StreamParser"
Cohesion: 0.18
Nodes (6): Any, Consumes raw token stream, yields structured events: - {"type": "token",…, Parses LLM streaming tokens in real-time, buffering potential markup tags and…, StreamParser, test_parser_interrupt_detection(), test_parser_rejection_detection()

### Community 5 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+10 more)

### Community 6 - "OllamaClient"
Cohesion: 0.16
Nodes (8): OllamaClient, High-fidelity 5e DM simulation engine. Generates realistic atmospheric…, Async client for Ollama LLM inference with fallback simulation and background…, Starts background download of all 5 supported models in sequence., Sequential download worker., Checks if local Ollama daemon is reachable., Fetches list of downloaded model tags from Ollama., Streams response tokens. Falls back to Simulation DM if model not locally…

### Community 7 - "ChronicleManager"
Cohesion: 0.11
Nodes (13): ChronicleManager, Any, Path, Tier 3 Rolling Chat History & Persistent Chronicle. Maintains a persistent chat…, Returns the rolling buffer of recent turns., Reads the summary chronicle.md file., Appends a new canonical milestone to chronicle.md., Flushes turn history, resets chat entries with the new prologue, and rewrites… (+5 more)

### Community 8 - "CompendiumManager"
Cohesion: 0.21
Nodes (7): CompendiumManager, Any, InventoryItem, Saves a new custom item invented by the AI DM into items_catalog.json., Adds an item to the character's inventory. If the item is not in the base…, Applies standard D&D 5e leveling rules: - Updates level (clamped 1-20) -…, Manages loading, searching, and dynamically expanding items & spells. Allows…

### Community 9 - "StateManager"
Cohesion: 0.22
Nodes (6): Any, Path, Tier 1 Active State Manager. Handles thread-safe persistence and validation of…, Adjusts HP. Positive adds, negative damages., Toggle used slots at given spell level., StateManager

### Community 10 - "LoreManager"
Cohesion: 0.21
Nodes (5): LoreManager, Any, Path, Builds a compact targeted context string containing only the current location,…, Tier 2 Targeted Lore Indexer. Loads campaign lore and selectively formats the…

### Community 11 - "get"
Cohesion: 0.20
Nodes (10): get_compendium_items(), get_compendium_spells(), get_game_state(), get_models_status(), Returns complete game state: Character sheet, location lore, chronicle, and…, Returns download status and readiness of all 5 supported models., Returns the persistent catalog of standard 5e items and custom relics., Returns the catalog of 5e spells. (+2 more)

### Community 12 - "campaign_generator.py"
Cohesion: 0.39
Nodes (8): _call_ollama_json(), generate_campaign_world_and_storyline(), generate_fallback_campaign(), _match_archetype(), Any, Dynamically generates campaign title, tone, starting location, 3-act storyline,…, Helper to stream/collect LLM response and parse JSON., test_backstory_storyline_and_auto_tone()

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

### Community 24 - "resolve_check_endpoint"
Cohesion: 0.18
Nodes (12): build_messages_payload(), build_system_prompt(), Builds the messages array for Ollama chat API., Builds the comprehensive system prompt including game state., CheckResolveRequest, execute_player_action(), event_generator(), Primary action endpoint: Streams narrative from Ollama/Simulation DM,… (+4 more)

### Community 25 - "post"
Cohesion: 0.14
Nodes (14): ItemToggleRequest, ModelSelectRequest, modify_character_hp(), Sets active model for future dialogue turns., Manually triggers or retries background downloads of models., Adjusts HP for damage or healing., Toggles equipped status of an inventory item., Resets game state to campaign default. (+6 more)

### Community 26 - "AI-Powered D&D 5e Dungeon Master System"
Cohesion: 0.20
Nodes (9): 1. Start the Combined Server, 2. Remote Access via Tunnel (ngrok / Cloudflare / localtunnel), 3. Ollama Setup & Custom Modelfiles, 3. Running Unit Tests, AI-Powered D&D 5e Dungeon Master System, 🏛️ Core Architectural Mandate: Separation of Concerns, 🚀 Quickstart Guide, 📁 Repository Structure (+1 more)

### Community 27 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 28 - "main.py"
Cohesion: 0.44
Nodes (3): asyncio, startup_event(), on_event

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
- **195 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+190 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 312 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Character` connect `Character` to `CompendiumManager`, `StateManager`, `resolve_check_endpoint`, `post`, `main.py`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Why does `ChronicleManager` connect `ChronicleManager` to `main.py`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Why does `OllamaClient` connect `OllamaClient` to `main.py`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `Character` (e.g. with `CompendiumManager` and `apply_damage()`) actually correct?**
  _`Character` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `CompendiumManager` (e.g. with `Character` and `InventoryItem`) actually correct?**
  _`CompendiumManager` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `StreamParser` (e.g. with `execute_player_action()` and `resolve_check_endpoint()`) actually correct?**
  _`StreamParser` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `private`, `version` to the rest of the system?**
  _195 weakly-connected nodes found - possible documentation gaps or missing edges._