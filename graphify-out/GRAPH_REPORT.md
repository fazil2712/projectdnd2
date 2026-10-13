# Graph Report - projectdnd2  (2026-10-14)

## Corpus Check
- 80 files · ~85,742 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 12 file(s) not represented in the graph (top: (none) 4, .bak 1, .hermes 1)

## Summary
- 665 nodes · 1083 edges · 63 communities (41 shown, 20 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 36 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e57bf6dc`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- post
- game.ts
- test_engine.py
- package.json
- StreamParser
- compilerOptions
- OllamaClient
- ChronicleManager
- CompendiumManager
- StateManager
- LoreManager
- get
- BaseModel
- compilerOptions
- engine/__init__.py
- app/__init__.py
- llm/__init__.py
- memory/__init__.py
- tests/__init__.py
- What You Must Do When Invoked
- What You Must Do When Invoked
- What You Must Do When Invoked
- main.py
- compendium.py
- AI-Powered D&D 5e Dungeon Master System
- graphify reference: extra exports and benchmark
- execute_player_action
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
- campaign_generator.py
- create_campaign_endpoint
- .set_hit_dice_defaults
- manual_level_up
- remove_spell_endpoint

## God Nodes (most connected - your core abstractions)
1. `Character` - 62 edges
2. `LoreManager` - 21 edges
3. `StateManager` - 20 edges
4. `StreamParser` - 19 edges
5. `atomic_write_json()` - 19 edges
6. `ChronicleManager` - 16 edges
7. `compilerOptions` - 16 edges
8. `roll_dice()` - 15 edges
9. `resolve_check()` - 15 edges
10. `resolve_spell_cast()` - 15 edges

## Surprising Connections (you probably didn't know these)
- `CompendiumManager` --uses--> `InventoryItem`  [INFERRED]
  backend/app/engine/compendium.py → backend/app/engine/character.py
- `validate_inventory_item()` --uses--> `InventoryItem`  [INFERRED]
  backend/app/engine/rules.py → backend/app/engine/character.py
- `create_campaign_endpoint()` --uses--> `InventoryItem`  [INFERRED]
  backend/app/main.py → backend/app/engine/character.py
- `create_campaign_endpoint()` --uses--> `SpellSlotLevel`  [INFERRED]
  backend/app/main.py → backend/app/engine/character.py
- `create_campaign_endpoint()` --uses--> `SpellSlots`  [INFERRED]
  backend/app/main.py → backend/app/engine/character.py

## Import Cycles
- None detected.

## Communities (63 total, 20 thin omitted)

### Community 0 - "post"
Cohesion: 0.14
Nodes (14): ItemToggleRequest, ModelSelectRequest, modify_character_hp(), Adjusts HP for damage or healing., Toggles equipped status of an inventory item., Resets game state to campaign default., Sets active model for future dialogue turns., Manually triggers or retries background downloads of models. (+6 more)

### Community 1 - "game.ts"
Cohesion: 0.06
Nodes (58): App(), ActionInput(), ActionInputProps, QUICK_ACTIONS, BACKSTORY_SEEDS, CampaignSetupModal(), CampaignSetupModalProps, CLASS_DEFAULT_SPELLS (+50 more)

### Community 2 - "test_engine.py"
Cohesion: 0.07
Nodes (59): AbilityScores, Character, Consumes an item from character inventory. If it's a potion, applies…, Roll a deterministic 20-sided die with advantage, disadvantage, or straight. If…, Roll arbitrary dice formula (e.g. '1d8+3', '2d6', '8d6', '1d10-1'). If…, roll_d20(), roll_dice(), apply_damage() (+51 more)

### Community 3 - "package.json"
Cohesion: 0.08
Nodes (24): dependencies, lucide-react, react, react-dom, devDependencies, @types/react, @types/react-dom, typescript (+16 more)

### Community 4 - "StreamParser"
Cohesion: 0.08
Nodes (16): Any, Extracts key-value pairs from attribute string. Supports single quotes, double…, Consumes raw token stream and yields structured events: - {"type": "token",…, Parses LLM streaming tokens in real-time, buffering potential markup tags and…, StreamParser, Verify unclosed '<' does not hang the stream and flushes as normal token., Verify single-quoted attributes and multiple inline tags in one stream., Verify StreamParser detects <SPELL_LEARN .../> tag and yields spell_learned… (+8 more)

### Community 5 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+10 more)

### Community 6 - "OllamaClient"
Cohesion: 0.16
Nodes (8): OllamaClient, High-fidelity 5e DM simulation engine. Generates realistic atmospheric…, Async client for Ollama LLM inference with fallback simulation and background…, Starts background download of all 5 supported models in sequence., Sequential download worker., Checks if local Ollama daemon is reachable., Fetches list of downloaded model tags from Ollama., Streams response tokens. Falls back to Simulation DM if model not locally…

### Community 7 - "ChronicleManager"
Cohesion: 0.09
Nodes (19): ChronicleManager, Any, Path, Tier 3 Rolling Chat History & Persistent Chronicle. Maintains a persistent…, Returns the rolling buffer of the latest N turns for LLM prompt context., Reads the summary chronicle.md file., Internal helper to append milestone without acquiring self._lock (prevents…, Appends a new canonical milestone to chronicle.md atomically. (+11 more)

### Community 8 - "CompendiumManager"
Cohesion: 0.17
Nodes (11): CompendiumManager, find_spell_in_catalog(), Any, InventoryItem, Validates if a character meets 5e rules to learn/prepare a spell: 1. Spell…, Saves a new custom item invented by the AI DM into items_catalog.json., Adds an item to the character's inventory. If the item is not in the base…, Applies standard D&D 5e leveling rules: - Updates level (clamped 1-20) -… (+3 more)

### Community 9 - "StateManager"
Cohesion: 0.13
Nodes (10): Any, Path, Toggle used slots at given spell level., Tier 1 Active State Manager. Handles thread-safe persistence and validation of…, Adds a spell to the character's prepared / known spell list., Removes a spell from the character's prepared / known spell list., Sets the character's prepared / known spell list., Adjusts HP. Positive adds, negative damages. (+2 more)

### Community 10 - "LoreManager"
Cohesion: 0.12
Nodes (10): LoreManager, Any, Path, Tier 2 Targeted Lore Indexer. Loads campaign lore and selectively formats the…, Builds a compact targeted context string containing only the current location,…, atomic_write_json(), Any, Serializes data to formatted JSON and atomically writes it to filepath via… (+2 more)

### Community 11 - "get"
Cohesion: 0.20
Nodes (10): get_compendium_items(), get_compendium_spells(), get_game_state(), get_models_status(), Returns the persistent catalog of standard 5e items and custom relics., Returns the catalog of 5e spells., Returns complete game state: Character sheet, location lore, chronicle, chat…, Returns download status and readiness of all 5 supported models. (+2 more)

### Community 12 - "BaseModel"
Cohesion: 0.13
Nodes (15): CheckResolveRequest, ConditionToggleRequest, DamageInflictRequest, GrantItemRequest, manual_grant_item(), modify_character_condition(), BaseModel, Toggles used spell slots at specified level. (+7 more)

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

### Community 24 - "main.py"
Cohesion: 0.29
Nodes (6): asyncio, learn_spell_endpoint(), Validates spell against 5e class and spell slot constraints, then…, SpellLearnRequest, startup_event(), on_event

### Community 25 - "compendium.py"
Cohesion: 0.26
Nodes (11): DeathSaves, InventoryItem, BaseModel, SpellSlotLevel, SpellSlots, can_character_learn_spell(), Module-level wrapper for compendium_manager.can_character_learn_spell., Verify equipping a new armor or shield automatically unequips previous ones in… (+3 more)

### Community 26 - "AI-Powered D&D 5e Dungeon Master System"
Cohesion: 0.20
Nodes (9): 1. Start the Combined Server, 2. Remote Access via Tunnel (ngrok / Cloudflare / localtunnel), 3. Ollama Setup & Custom Modelfiles, 3. Running Unit Tests, AI-Powered D&D 5e Dungeon Master System, 🏛️ Core Architectural Mandate: Separation of Concerns, 🚀 Quickstart Guide, 📁 Repository Structure (+1 more)

### Community 27 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 28 - "execute_player_action"
Cohesion: 0.17
Nodes (9): build_messages_payload(), build_system_prompt(), Builds the comprehensive system prompt including game state., Builds the messages array for Ollama chat API., ActionRequest, execute_player_action(), recovery_stream(), Primary action endpoint: Streams narrative from Ollama/Simulation DM,… (+1 more)

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

### Community 58 - "campaign_generator.py"
Cohesion: 0.39
Nodes (8): _call_ollama_json(), generate_campaign_world_and_storyline(), generate_fallback_campaign(), _match_archetype(), Any, Dynamically generates campaign title, tone, starting location, 3-act storyline,…, Helper to stream/collect LLM response and parse JSON., test_backstory_storyline_and_auto_tone()

### Community 59 - "create_campaign_endpoint"
Cohesion: 0.40
Nodes (5): Enforces D&D 5e standard ability score constraints: - Minimum score is 3. - Max…, validate_and_clamp_character_stats(), CampaignCreationRequest, create_campaign_endpoint(), Customizes world setting, narrative tone, starting location, and creates a new…

### Community 61 - "manual_level_up"
Cohesion: 0.67
Nodes (3): LevelUpRequest, manual_level_up(), Applies standard 5e leveling rules to the active character sheet.

### Community 62 - "remove_spell_endpoint"
Cohesion: 0.67
Nodes (3): Removes a spell from the prepared/known spell list., remove_spell_endpoint(), SpellRemoveRequest

## Knowledge Gaps
- **203 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+198 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 363 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **20 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Character` connect `test_engine.py` to `post`, `CompendiumManager`, `StateManager`, `execute_player_action`, `main.py`, `compendium.py`, `create_campaign_endpoint`, `.set_hit_dice_defaults`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Why does `ChronicleManager` connect `ChronicleManager` to `main.py`, `test_engine.py`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Why does `OllamaClient` connect `OllamaClient` to `main.py`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Are the 17 inferred relationships involving `Character` (e.g. with `can_character_learn_spell()` and `CompendiumManager`) actually correct?**
  _`Character` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `StateManager` (e.g. with `Character` and `test_equipment_slot_exclusivity()`) actually correct?**
  _`StateManager` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `StreamParser` (e.g. with `execute_player_action()` and `resolve_check_endpoint()`) actually correct?**
  _`StreamParser` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `private`, `version` to the rest of the system?**
  _203 weakly-connected nodes found - possible documentation gaps or missing edges._