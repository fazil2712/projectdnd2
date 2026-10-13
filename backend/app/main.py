import asyncio
import json
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from .config import SUPPORTED_MODELS, DEFAULT_MODEL, BASE_DIR, CHRONICLE_FILE
from .memory.state_manager import state_manager
from .memory.lore_manager import lore_manager
from .memory.chronicle import chronicle_manager
from .engine.character import Character
from .engine.rules import (
    resolve_check,
    resolve_attack_damage,
    validate_inventory_item,
    validate_and_consume_spell_slot,
    validate_and_clamp_character_stats,
    RACES_5E,
    RACE_TRAITS_5E,
)
from .llm.client import ollama_client
from .llm.parser import StreamParser
from .llm.prompts import build_system_prompt, build_messages_payload
from .llm.campaign_generator import generate_campaign_world_and_storyline
from .engine.compendium import compendium_manager


app = FastAPI(title="D&D 5e AI DM Engine", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ActionRequest(BaseModel):
    action: str
    model: Optional[str] = None


class CheckResolveRequest(BaseModel):
    check_type: str = "skill"  # skill, save, attack, ability
    target: str = "Stealth"
    dc: int = 15
    modifier: Optional[int] = None
    advantage: bool = False
    disadvantage: bool = False
    action_context: Optional[str] = None
    player_action: Optional[str] = None
    model: Optional[str] = None


class DamageInflictRequest(BaseModel):
    target: str
    amount: int
    damage_type: str = "slashing"
    is_critical: bool = False


class SpellSlotToggleRequest(BaseModel):
    level: int
    slot_index: int


class ItemToggleRequest(BaseModel):
    item_id: str


class ModelSelectRequest(BaseModel):
    model: str


class GrantItemRequest(BaseModel):
    name: str
    item_type: str = "gear"
    quantity: int = 1
    weight_lbs: float = 1.0
    damage: Optional[str] = None
    damage_type: Optional[str] = None
    armor_base: Optional[int] = None
    armor_category: Optional[str] = None
    properties: Optional[list] = None
    description: Optional[str] = None


class LevelUpRequest(BaseModel):
    target_level: int
    reason: Optional[str] = None


class CampaignCreationRequest(BaseModel):
    world_setting: str
    genre: Optional[str] = None
    campaign_name: Optional[str] = None
    character_name: str = "Dunstan Clayhanger"
    character_race: str = "Human"
    character_class: str = "Fighter"
    subclass: Optional[str] = None
    backstory: Optional[str] = ""
    level: int = 3
    background: str = "Soldier"
    alignment: str = "Neutral Good"
    strength: int = 15
    dexterity: int = 14
    constitution: int = 14
    intelligence: int = 10
    wisdom: int = 12
    charisma: int = 10
    # Optional manual overrides
    narrative_tone: Optional[str] = None
    starting_location_name: Optional[str] = None
    starting_location_description: Optional[str] = None



@app.on_event("startup")
async def startup_event():
    # Start background model downloads automatically
    asyncio.create_task(ollama_client.start_sequential_downloads())


@app.get("/api/game/state")
async def get_game_state():
    """Returns complete game state: Character sheet, location lore, chronicle, and chat history."""
    char = await state_manager.get_character()
    lore = await lore_manager.get_raw_lore()
    location = await lore_manager.get_current_location()
    chronicle_text = await chronicle_manager.get_chronicle_markdown()
    recent_turns = await chronicle_manager.get_recent_turns()
    chat_history = await chronicle_manager.get_chat_history()

    return {
        "character": char.model_dump(),
        "location": location,
        "campaign_name": lore.get("campaign_name", "D&D 5e Adventure"),
        "chronicle_text": chronicle_text,
        "recent_turns": recent_turns,
        "chat_history": chat_history,
        "active_model": ollama_client.active_model,
        "supported_models": SUPPORTED_MODELS,
    }


@app.get("/api/models")
async def get_models_status():
    """Returns download status and readiness of all 5 supported models."""
    installed = await ollama_client.get_installed_models()
    models_info = []

    for model_id, meta in SUPPORTED_MODELS.items():
        base_id = model_id.split(":")[0]
        is_inst = any(model_id == m or m.startswith(f"{base_id}:") for m in installed)
        status_data = ollama_client.model_download_status.get(model_id, {})

        if is_inst:
            display_status = "ready"
            progress = 100.0
            msg = "Ready on GPU / Disk"
        else:
            display_status = status_data.get("status", "available")
            progress = status_data.get("progress", 0.0)
            msg = status_data.get("message", "Available to pull")

        models_info.append({
            "id": model_id,
            "name": meta["name"],
            "description": meta["description"],
            "vram_approx": meta["vram_approx"],
            "status": display_status,
            "progress": progress,
            "message": msg,
            "is_active": model_id == ollama_client.active_model,
        })

    return {
        "active_model": ollama_client.active_model,
        "models": models_info,
        "ollama_online": await ollama_client.check_health(),
    }


@app.post("/api/models/select")
async def select_active_model(req: ModelSelectRequest):
    """Sets active model for future dialogue turns."""
    if req.model not in SUPPORTED_MODELS:
        raise HTTPException(status_code=400, detail=f"Unsupported model: {req.model}")
    ollama_client.active_model = req.model
    return {"active_model": ollama_client.active_model}


@app.post("/api/models/pull")
async def trigger_model_pull():
    """Manually triggers or retries background downloads of models."""
    asyncio.create_task(ollama_client.start_sequential_downloads())
    return {"message": "Background model pull initiated."}


@app.post("/api/game/action")
async def execute_player_action(req: ActionRequest, request: Request):
    """
    Primary action endpoint: Streams narrative from Ollama/Simulation DM,
    intercepting check requests and action rejections via SSE.
    """
    character = await state_manager.get_character()
    action_text = req.action.strip()

    # Pre-validation 1: Unconscious check
    if "unconscious" in character.conditions or character.current_hp <= 0:
        async def unconscious_stream():
            rejection = {
                "type": "action_rejected",
                "rejection": {
                    "reason": "You are currently unconscious at 0 HP. You cannot take actions until revived or stabilized."
                }
            }
            yield {"event": "action_rejected", "data": json.dumps(rejection)}
            yield {
                "event": "token",
                "data": json.dumps({
                    "content": "You drift in the dark abyss of unconsciousness. The world fades, and only the rhythm of your failing heartbeat remains..."
                })
            }
            yield {"event": "done", "data": json.dumps({"narrative": "You are unconscious."})}

        return EventSourceResponse(unconscious_stream())

    # Assemble Prompts & Context
    targeted_lore = await lore_manager.format_targeted_context()
    chronicle_summary = await chronicle_manager.get_chronicle_markdown()
    recent_turns = await chronicle_manager.get_recent_turns()

    system_prompt = build_system_prompt(character, targeted_lore, chronicle_summary)
    messages = build_messages_payload(
        system_prompt=system_prompt,
        recent_turns=recent_turns,
        current_action=action_text
    )

    chosen_model = req.model or ollama_client.active_model

    async def event_generator():
        parser = StreamParser()
        raw_stream = ollama_client.stream_chat(messages, model=chosen_model)

        accumulated_narrative = ""

        async for parsed_event in parser.process_token_stream(raw_stream):
            if await request.is_disconnected():
                break

            event_type = parsed_event["type"]

            if event_type == "token":
                accumulated_narrative += parsed_event["content"]
                yield {
                    "event": "token",
                    "data": json.dumps({"content": parsed_event["content"]})
                }

            elif event_type == "check_required":
                check_info = parsed_event["check"]
                # Compute player's bonus for frontend display
                res = resolve_check(
                    character=character,
                    check_type=check_info.get("type", "skill"),
                    target=check_info.get("target", "Stealth"),
                    dc=check_info.get("dc", 15),
                )
                check_info["modifier"] = res["modifier"]
                check_info["resolved_name"] = res["resolved_name"]

                yield {
                    "event": "check_required",
                    "data": json.dumps({"check": check_info, "pre_text": accumulated_narrative})
                }

            elif event_type == "action_rejected":
                yield {
                    "event": "action_rejected",
                    "data": json.dumps({"rejection": parsed_event["rejection"]})
                }

            elif event_type == "item_granted":
                char, granted_item, is_custom = await compendium_manager.grant_item_to_character(character, parsed_event["item"])
                await state_manager.save_character(char)
                yield {
                    "event": "item_granted",
                    "data": json.dumps({
                        "item": granted_item.model_dump(),
                        "is_custom": is_custom,
                        "character": char.model_dump(),
                    })
                }

            elif event_type == "item_consumed":
                consume_info = parsed_event["consumption"]
                char, success, summary = await compendium_manager.consume_item_from_character(
                    character,
                    consume_info.get("name", ""),
                    int(consume_info.get("quantity", 1))
                )
                if success:
                    await state_manager.save_character(char)
                yield {
                    "event": "item_consumed",
                    "data": json.dumps({
                        "summary": summary,
                        "success": success,
                        "character": char.model_dump(),
                    })
                }

            elif event_type == "level_up":
                lvl_info = parsed_event["level_up"]
                lvl_num = int(lvl_info.get("level", character.level + 1))
                res = compendium_manager.apply_level_up(character, lvl_num, lvl_info.get("reason"))
                if res["success"]:
                    await state_manager.save_character(character)
                yield {
                    "event": "level_up",
                    "data": json.dumps({
                        "level_up": res,
                        "character": character.model_dump(),
                    })
                }

            elif event_type == "done":
                final_narrative = parsed_event.get("narrative", accumulated_narrative)
                if not parser.check_triggered and not parser.rejection_triggered:
                    # Save normal dialogue turn to chronicle
                    await chronicle_manager.add_turn(action_text, final_narrative)

                yield {
                    "event": "done",
                    "data": json.dumps({"narrative": final_narrative})
                }


    return EventSourceResponse(event_generator())


@app.post("/api/game/resolve-check")
async def resolve_check_endpoint(req: CheckResolveRequest, request: Request):
    """
    Resolves an interrupted check deterministically, computes damage if applicable,
    and streams the DM's narrative continuation.
    """
    character = await state_manager.get_character()

    # 1. Deterministic Engine Resolution
    check_result = resolve_check(
        character=character,
        check_type=req.check_type,
        target=req.target,
        dc=req.dc,
        advantage=req.advantage,
        disadvantage=req.disadvantage,
    )

    # 2. If it was a successful attack, resolve damage mechanically
    damage_info = None
    if req.check_type == "attack" and check_result["success"]:
        damage_info = resolve_attack_damage(
            character=character,
            weapon_name=req.target,
            is_critical=check_result["roll"]["is_critical_success"]
        )
        check_result["mechanical_summary"] += f" | Damage Dealt: {damage_info['summary']}"

    # 3. Assemble prompt with mechanical resolution
    targeted_lore = await lore_manager.format_targeted_context()
    chronicle_summary = await chronicle_manager.get_chronicle_markdown()
    recent_turns = await chronicle_manager.get_recent_turns()

    action_text = (req.player_action or req.action_context or f"{req.target} Check").strip()
    system_prompt = build_system_prompt(character, targeted_lore, chronicle_summary)
    messages = build_messages_payload(
        system_prompt=system_prompt,
        recent_turns=recent_turns,
        current_action=action_text,
        mechanical_resolution=check_result["mechanical_summary"]
    )

    chosen_model = req.model or ollama_client.active_model

    async def continuation_stream():
        # First emit the roll outcome details to the frontend
        yield {
            "event": "roll_resolved",
            "data": json.dumps({
                "check_result": check_result,
                "damage_info": damage_info,
            })
        }

        # Stream DM continuation narrative
        parser = StreamParser()
        raw_stream = ollama_client.stream_chat(messages, model=chosen_model)
        full_continuation = ""

        async for parsed_event in parser.process_token_stream(raw_stream):
            if await request.is_disconnected():
                break

            if parsed_event["type"] == "token":
                full_continuation += parsed_event["content"]
                yield {
                    "event": "token",
                    "data": json.dumps({"content": parsed_event["content"]})
                }
            elif parsed_event["type"] == "item_granted":
                char, granted_item, is_custom = await compendium_manager.grant_item_to_character(character, parsed_event["item"])
                await state_manager.save_character(char)
                yield {
                    "event": "item_granted",
                    "data": json.dumps({
                        "item": granted_item.model_dump(),
                        "is_custom": is_custom,
                        "character": char.model_dump(),
                    })
                }
            elif parsed_event["type"] == "item_consumed":
                consume_info = parsed_event["consumption"]
                char, success, summary = await compendium_manager.consume_item_from_character(
                    character,
                    consume_info.get("name", ""),
                    int(consume_info.get("quantity", 1))
                )
                if success:
                    await state_manager.save_character(char)
                yield {
                    "event": "item_consumed",
                    "data": json.dumps({
                        "summary": summary,
                        "success": success,
                        "character": char.model_dump(),
                    })
                }
            elif parsed_event["type"] == "level_up":
                lvl_info = parsed_event["level_up"]
                lvl_num = int(lvl_info.get("level", character.level + 1))
                res = compendium_manager.apply_level_up(character, lvl_num, lvl_info.get("reason"))
                if res["success"]:
                    await state_manager.save_character(character)
                yield {
                    "event": "level_up",
                    "data": json.dumps({
                        "level_up": res,
                        "character": character.model_dump(),
                    })
                }
            elif parsed_event["type"] == "done":
                narrative = parsed_event.get("narrative", full_continuation)
                # Record the full resolved action, mechanical roll result, & continuation narrative
                full_action_record = f"{action_text} (Roll: {check_result['roll']['notation']} -> {'SUCCESS' if check_result['success'] else 'FAILURE'})"
                await chronicle_manager.add_turn(
                    full_action_record,
                    narrative,
                    roll_metadata={
                        "check_result": check_result,
                        "damage_info": damage_info
                    }
                )

                yield {
                    "event": "done",
                    "data": json.dumps({"narrative": narrative})
                }

    return EventSourceResponse(continuation_stream())



@app.post("/api/game/character/modify-hp")
async def modify_character_hp(req: HpModifyRequest):
    """Adjusts HP for damage or healing."""
    result = await state_manager.modify_hp(req.delta)
    char = await state_manager.get_character()
    return {"result": result, "character": char.model_dump()}


@app.post("/api/game/character/toggle-slot")
async def toggle_slot(req: SpellSlotToggleRequest):
    """Toggles used spell slots at specified level."""
    slot_info = await state_manager.toggle_spell_slot(req.level, req.slot_index)
    char = await state_manager.get_character()
    return {"slot_info": slot_info, "character": char.model_dump()}


@app.post("/api/game/character/toggle-item")
async def toggle_item(req: ItemToggleRequest):
    """Toggles equipped status of an inventory item."""
    equipped = await state_manager.toggle_item_equipped(req.item_id)
    char = await state_manager.get_character()
    return {"item_id": req.item_id, "equipped": equipped, "character": char.model_dump()}


@app.get("/api/compendium/items")
async def get_compendium_items():
    """Returns the persistent catalog of standard 5e items and custom relics."""
    return compendium_manager.get_all_items()


@app.get("/api/compendium/spells")
async def get_compendium_spells():
    """Returns the catalog of 5e spells."""
    return compendium_manager.get_all_spells()


@app.post("/api/compendium/grant-item")
async def manual_grant_item(req: GrantItemRequest):
    """Grants an item (standard or custom) to the active character sheet."""
    char = await state_manager.get_character()
    char, granted, is_custom = await compendium_manager.grant_item_to_character(char, req.model_dump())
    await state_manager.save_character(char)
    return {"granted_item": granted.model_dump(), "is_custom": is_custom, "character": char.model_dump()}


@app.post("/api/compendium/level-up")
async def manual_level_up(req: LevelUpRequest):
    """Applies standard 5e leveling rules to the active character sheet."""
    char = await state_manager.get_character()
    res = compendium_manager.apply_level_up(char, req.target_level, req.reason)
    if not res["success"]:
        raise HTTPException(status_code=400, detail=res["message"])
    await state_manager.save_character(char)
    return {"result": res, "character": char.model_dump()}


@app.post("/api/game/reset")
async def reset_game():
    """Resets game state to campaign default."""
    default_char = Character()
    await state_manager.save_character(default_char)
    default_prologue = (
        "# Campaign Chronicle\n\n## Chapter 1: The Adventure Begins\n- The journey commenced.\n"
    )
    default_dm = (
        "Cold twilight hangs heavy over the foothills of the Neverwinter Wood. "
        "Before you, veiled behind a curtain of dripping stalactites, the cavernous mouth of the Weeping Maw opens into pitch-black subterranean depths. "
        "Forty feet ahead near the threshold, a cowardly goblin sentry fidgets beneath a makeshift leather canopy, while a hulking bugbear guard rests lazily upon a wooden crate, sharpening a notched blade.\n\n"
        "The damp moss silences your footsteps, but the darkness ahead is treacherous. What do you do?"
    )
    await chronicle_manager.reset_chronicle(default_prologue, initial_dm_narrative=default_dm)
    return {"message": "Game reset to default."}


@app.post("/api/game/create-campaign")
async def create_campaign_endpoint(req: CampaignCreationRequest):
    """
    Customizes world setting, narrative tone, starting location, and creates
    a new 5e character sheet with deterministic modifiers, 5e stat clamping,
    and dynamic campaign storyline generation.
    """
    from .engine.character import Character, AbilityScores, InventoryItem, SpellSlots, SpellSlotLevel

    # 1. 5e Ability Score Validation & Clamping (Anti-100 STR rule)
    raw_abilities = {
        "strength": req.strength,
        "dexterity": req.dexterity,
        "constitution": req.constitution,
        "intelligence": req.intelligence,
        "wisdom": req.wisdom,
        "charisma": req.charisma,
    }
    stats = validate_and_clamp_character_stats(req.level, raw_abilities)

    level = max(1, min(20, req.level))
    con_mod = (stats["constitution"] - 10) // 2
    cls_lower = req.character_class.lower()

    # 2. Authentic 5e Class Equipment & Hit Points
    if "barbarian" in cls_lower:
        hit_die = "d12"
        base_hp = 12 + con_mod + (level - 1) * max(1, 7 + con_mod)
        items = [
            InventoryItem(id="item_gs", name="Greatsword", quantity=1, weight_lbs=6.0, item_type="weapon", equipped=True, damage="2d6", damage_type="slashing", properties=["heavy", "two-handed"]),
            InventoryItem(id="item_ha", name="Handaxe", quantity=2, weight_lbs=2.0, item_type="weapon", equipped=True, damage="1d6", damage_type="slashing", properties=["light", "thrown"]),
            InventoryItem(id="item_pot", name="Potion of Healing", quantity=1, weight_lbs=0.5, item_type="potion", properties=["consumable"]),
        ]
        spell_slots = SpellSlots()
    elif "wizard" in cls_lower or "sorcerer" in cls_lower:
        hit_die = "d6"
        base_hp = 6 + con_mod + (level - 1) * max(1, 4 + con_mod)
        items = [
            InventoryItem(id="item_staff", name="Arcane Quarterstaff", quantity=1, weight_lbs=4.0, item_type="weapon", equipped=True, damage="1d6", damage_type="bludgeoning", properties=["versatile"]),
            InventoryItem(id="item_robes", name="Scholar's Robes", quantity=1, weight_lbs=3.0, item_type="gear", equipped=True),
            InventoryItem(id="item_focus", name="Crystal Arcane Focus", quantity=1, weight_lbs=1.0, item_type="gear", equipped=True),
            InventoryItem(id="item_pot", name="Potion of Healing", quantity=2, weight_lbs=0.5, item_type="potion", properties=["consumable"]),
        ]
        spell_slots = SpellSlots(
            level_1=SpellSlotLevel(max_slots=4 if level >= 3 else (2 if level == 1 else 3), used_slots=0),
            level_2=SpellSlotLevel(max_slots=2 if level >= 3 else 0, used_slots=0)
        )
    elif "cleric" in cls_lower or "paladin" in cls_lower:
        hit_die = "d10" if "paladin" in cls_lower else "d8"
        base_die = 10 if "paladin" in cls_lower else 8
        base_hp = base_die + con_mod + (level - 1) * max(1, (base_die // 2 + 1) + con_mod)
        items = [
            InventoryItem(id="item_mace", name="Warhammer", quantity=1, weight_lbs=4.0, item_type="weapon", equipped=True, damage="1d8", damage_type="bludgeoning", properties=["versatile"]),
            InventoryItem(id="item_shield", name="Steel Kite Shield", quantity=1, weight_lbs=6.0, item_type="shield", equipped=True),
            InventoryItem(id="item_scale", name="Scale Mail Armor", quantity=1, weight_lbs=45.0, item_type="armor", equipped=True, armor_base=14, armor_category="medium"),
            InventoryItem(id="item_symbol", name="Silver Holy Symbol", quantity=1, weight_lbs=1.0, item_type="gear", equipped=True),
            InventoryItem(id="item_pot", name="Potion of Healing", quantity=2, weight_lbs=0.5, item_type="potion", properties=["consumable"]),
        ]
        spell_slots = SpellSlots(level_1=SpellSlotLevel(max_slots=3 if level >= 2 else 2, used_slots=0))
    elif "rogue" in cls_lower:
        hit_die = "d8"
        base_hp = 8 + con_mod + (level - 1) * max(1, 5 + con_mod)
        items = [
            InventoryItem(id="item_rapier", name="Fine Rapier", quantity=1, weight_lbs=2.0, item_type="weapon", equipped=True, damage="1d8", damage_type="piercing", properties=["finesse"]),
            InventoryItem(id="item_shortbow", name="Shortbow", quantity=1, weight_lbs=2.0, item_type="weapon", equipped=True, damage="1d6", damage_type="piercing", properties=["range", "two-handed"]),
            InventoryItem(id="item_leather", name="Studded Leather Armor", quantity=1, weight_lbs=13.0, item_type="armor", equipped=True, armor_base=12, armor_category="light"),
            InventoryItem(id="item_thieves", name="Thieves' Tools", quantity=1, weight_lbs=1.0, item_type="tool"),
            InventoryItem(id="item_pot", name="Potion of Healing", quantity=2, weight_lbs=0.5, item_type="potion", properties=["consumable"]),
        ]
        spell_slots = SpellSlots()
    else:  # Fighter / Default
        hit_die = "d10"
        base_hp = 10 + con_mod + (level - 1) * max(1, 6 + con_mod)
        items = [
            InventoryItem(id="item_sword", name="Longsword", quantity=1, weight_lbs=3.0, item_type="weapon", equipped=True, damage="1d8", damage_type="slashing", properties=["versatile"]),
            InventoryItem(id="item_shield", name="Iron Shield", quantity=1, weight_lbs=6.0, item_type="shield", equipped=True),
            InventoryItem(id="item_chain", name="Chain Shirt Armor", quantity=1, weight_lbs=20.0, item_type="armor", equipped=True, armor_base=13, armor_category="medium"),
            InventoryItem(id="item_crossbow", name="Light Crossbow", quantity=1, weight_lbs=5.0, item_type="weapon", equipped=False, damage="1d8", damage_type="piercing", properties=["range", "two-handed"]),
            InventoryItem(id="item_pot", name="Potion of Healing", quantity=2, weight_lbs=0.5, item_type="potion", properties=["consumable"]),
        ]
        spell_slots = SpellSlots()

    race_key = req.character_race if req.character_race in RACE_TRAITS_5E else "Human"
    race_data = RACE_TRAITS_5E.get(race_key, RACE_TRAITS_5E["Human"])

    new_char = Character(
        name=req.character_name,
        character_class=req.character_class,
        subclass=None,
        level=level,
        race=race_key,
        alignment=req.alignment,
        background=req.background,
        backstory=req.backstory or "",
        racial_traits=race_data.get("traits", []),
        speed_feet=race_data.get("speed", 30),
        darkvision_feet=race_data.get("darkvision", 0),
        abilities=AbilityScores(
            strength=stats["strength"],
            dexterity=stats["dexterity"],
            constitution=stats["constitution"],
            intelligence=stats["intelligence"],
            wisdom=stats["wisdom"],
            charisma=stats["charisma"],
        ),
        max_hp=max(6, base_hp),
        current_hp=max(6, base_hp),
        temp_hp=0,
        hit_dice_max=level,
        hit_dice_current=level,
        hit_die_type=hit_die,
        inventory=items,
        spell_slots=spell_slots,
    )

    # 3. Save character to Tier 1 persistence
    await state_manager.save_character(new_char)

    # 4. Dynamically generate Campaign Storyline, Location, Tone, and Opening
    char_summary_dict = {
        "name": new_char.name,
        "race": new_char.race,
        "character_class": new_char.character_class,
        "level": new_char.level,
        "background": new_char.background,
        "backstory": new_char.backstory,
        "racial_traits": new_char.racial_traits,
    }
    generated = await generate_campaign_world_and_storyline(
        world_setting=req.world_setting,
        genre=req.genre,
        character_info=char_summary_dict,
        chosen_model=ollama_client.active_model
    )

    campaign_name = req.campaign_name or generated.get("campaign_name", "D&D 5e Campaign")
    narrative_tone = req.narrative_tone or generated.get("narrative_tone", "Atmospheric 5e Adventure")
    location_name = req.starting_location_name or generated.get("starting_location_name", "The Threshold")
    location_desc = req.starting_location_description or generated.get("starting_location_description", "Peril and mystery lie ahead.")
    main_storyline = generated.get("main_storyline", {})
    opening_narrative = generated.get("opening_narrative", f"You stand at {location_name}. {location_desc} What do you do?")

    # 5. Update Tier 2 World Lore with Storyline and Location
    await lore_manager.update_campaign_setting(
        campaign_name=campaign_name,
        narrative_tone=narrative_tone,
        world_setting=req.world_setting,
        starting_location_name=location_name,
        starting_location_description=location_desc,
        main_storyline=main_storyline
    )

    # 6. Reset & Initialize Tier 3 Chronicle
    genre_display = req.genre if req.genre else "AI-Determined Dynamic Atmosphere"
    backstory_block = f"- Character Backstory: {new_char.backstory}\n" if new_char.backstory else ""
    racial_block = f"- Racial Traits: {', '.join(new_char.racial_traits)}\n" if new_char.racial_traits else ""
    prologue = (
        f"# Chronicle of {new_char.name}\n\n"
        f"## Setting: {campaign_name} ({genre_display})\n"
        f"- World: {req.world_setting}\n"
        f"- Narrative Tone Directive: {narrative_tone}\n"
        f"- Starting Location: {location_name}\n"
        f"- Location Atmosphere: {location_desc}\n"
        f"{racial_block}"
        f"{backstory_block}\n"
        f"### Overarching Storyline Arc:\n"
        f"- Central Conflict: {main_storyline.get('central_conflict', 'None')}\n"
        f"- Primary Antagonist: {main_storyline.get('antagonist', 'None')}\n"
        f"- Active Threat: {main_storyline.get('active_threat', 'None')}\n"
        f"- Act 1: {main_storyline.get('act_1', 'None')}\n"
        f"- Act 2: {main_storyline.get('act_2', 'None')}\n"
        f"- Act 3: {main_storyline.get('act_3', 'None')}\n"
    )
    await chronicle_manager.reset_chronicle(prologue, initial_dm_narrative=opening_narrative)

    return {
        "character": new_char.model_dump(),
        "campaign_name": campaign_name,
        "location_name": location_name,
        "narrative_tone": narrative_tone,
        "main_storyline": main_storyline,
        "opening_narrative": opening_narrative,
    }




# Mount Frontend Dist if available
frontend_dist = BASE_DIR.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = frontend_dist / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dist / "index.html")
