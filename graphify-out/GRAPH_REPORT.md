# Graph Report - projectdnd2  (2026-10-14)

## Corpus Check
- 78 files · ~68,418 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 12 file(s) not represented in the graph (top: (none) 4, .bak 1, .hermes 1)

## Summary
- 579 nodes · 869 edges · 53 communities (32 shown, 19 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 28 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4178c207`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- main.py
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
1. `Character` - 48 edges
2. `StateManager` - 17 edges
3. `StreamParser` - 16 edges
4. `ChronicleManager` - 16 edges
5. `compilerOptions` - 16 edges
6. `resolve_check()` - 14 edges
7. `execute_player_action()` - 14 edges
8. `atomic_write_json()` - 14 edges
9. `InventoryItem` - 13 edges
10. `CompendiumManager` - 13 edges

## Surprising Connections (you probably didn't know these)
- `CompendiumManager` --uses--> `InventoryItem`  [INFERRED]
  backend/app/engine/compendium.py → backend/app/engine/character.py
- `create_campaign_endpoint()` --uses--> `InventoryItem`  [INFERRED]
  backend/app/main.py → backend/app/engine/character.py
- `create_campaign_endpoint()` --uses--> `SpellSlotLevel`  [INFERRED]
  backend/app/main.py → backend/app/engine/character.py
- `create_campaign_endpoint()` --uses--> `SpellSlots`  [INFERRED]
  backend/app/main.py → backend/app/engine/character.py
- `create_campaign_endpoint()` --uses--> `AbilityScores`  [INFERRED]
  backend/app/main.py → backend/app/engine/character.py

## Import Cycles
- None detected.

## Communities (53 total, 19 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.05
Nodes (59): asyncio, Enforces D&D 5e standard ability score constraints: - Minimum score is 3. - Max…, validate_and_clamp_character_stats(), _call_ollama_json(), generate_campaign_world_and_storyline(), generate_fallback_campaign(), _match_archetype(), Any (+51 more)

### Community 1 - "App.tsx"
Cohesion: 0.09
Nodes (37): App(), ActionInput(), ActionInputProps, QUICK_ACTIONS, BACKSTORY_SEEDS, CampaignSetupModal(), CampaignSetupModalProps, GROUNDED_NAMES_ANIME (+29 more)

### Community 2 - "Character"
Cohesion: 0.08
Nodes (49): AbilityScores, Character, DeathSaves, InventoryItem, BaseModel, SpellSlotLevel, SpellSlots, Consumes an item from character inventory. If it's a potion, applies… (+41 more)

### Community 3 - "package.json"
Cohesion: 0.08
Nodes (24): dependencies, lucide-react, react, react-dom, devDependencies, @types/react, @types/react-dom, typescript (+16 more)

### Community 4 - "StreamParser"
Cohesion: 0.07
Nodes (23): Any, Parses LLM streaming tokens in real-time, buffering potential markup tags and…, Extracts key-value pairs from attribute string. Supports single quotes, double…, Consumes raw token stream and yields structured events: - {"type": "token",…, StreamParser, build_messages_payload(), build_system_prompt(), Builds the messages array for Ollama chat API. (+15 more)

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
Cohesion: 0.21
Nodes (7): CompendiumManager, Any, InventoryItem, Saves a new custom item invented by the AI DM into items_catalog.json., Adds an item to the character's inventory. If the item is not in the base…, Applies standard D&D 5e leveling rules: - Updates level (clamped 1-20) -…, Manages loading, searching, and dynamically expanding items & spells. Allows…

### Community 9 - "StateManager"
Cohesion: 0.17
Nodes (7): Any, Path, Toggle used slots at given spell level., Tier 1 Active State Manager. Handles thread-safe persistence and validation of…, Adjusts HP. Positive adds, negative damages., Toggles equipped status of an inventory item. Enforces 5e equipment slot…, StateManager

### Community 10 - "LoreManager"
Cohesion: 0.21
Nodes (5): LoreManager, Any, Path, Tier 2 Targeted Lore Indexer. Loads campaign lore and selectively formats the…, Builds a compact targeted context string containing only the current location,…

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
- **195 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+190 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 329 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Character` connect `Character` to `CompendiumManager`, `main.py`, `StreamParser`, `StateManager`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Why does `ChronicleManager` connect `ChronicleManager` to `main.py`, `Character`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Why does `OllamaClient` connect `OllamaClient` to `main.py`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `Character` (e.g. with `CompendiumManager` and `apply_damage()`) actually correct?**
  _`Character` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `StateManager` (e.g. with `Character` and `test_equipment_slot_exclusivity()`) actually correct?**
  _`StateManager` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `StreamParser` (e.g. with `execute_player_action()` and `resolve_check_endpoint()`) actually correct?**
  _`StreamParser` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `private`, `version` to the rest of the system?**
  _195 weakly-connected nodes found - possible documentation gaps or missing edges._