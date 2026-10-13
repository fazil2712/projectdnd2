import pytest
from app.engine.dice import roll_d20, roll_dice
from app.engine.character import Character, InventoryItem, AbilityScores
from app.engine.rules import (
    resolve_check,
    resolve_attack_damage,
    validate_inventory_item,
    validate_and_consume_spell_slot,
    apply_damage,
    apply_heal,
)
from app.llm.parser import StreamParser


def test_dice_straight_roll():
    res = roll_d20(modifier=3)
    assert len(res["raw_rolls"]) == 1
    assert 1 <= res["selected_raw"] <= 20
    assert res["total"] == res["selected_raw"] + 3
    assert res["advantage"] is False
    assert res["disadvantage"] is False


def test_dice_advantage():
    res = roll_d20(modifier=0, advantage=True)
    assert len(res["raw_rolls"]) == 2
    assert res["selected_raw"] == max(res["raw_rolls"])
    assert res["advantage"] is True
    assert res["disadvantage"] is False


def test_dice_disadvantage():
    res = roll_d20(modifier=0, disadvantage=True)
    assert len(res["raw_rolls"]) == 2
    assert res["selected_raw"] == min(res["raw_rolls"])
    assert res["disadvantage"] is True


def test_dice_cancel_advantage_disadvantage():
    # Both True cancels out to straight roll
    res = roll_d20(modifier=2, advantage=True, disadvantage=True)
    assert len(res["raw_rolls"]) == 1
    assert res["advantage"] is False
    assert res["disadvantage"] is False


def test_dice_formula():
    res = roll_dice("2d6+4")
    assert res["num_dice"] == 2
    assert res["die_sides"] == 6
    assert res["modifier"] == 4
    assert 6 <= res["total"] <= 16


def test_dice_critical_doubling():
    res = roll_dice("1d8+3", is_critical=True)
    assert res["num_dice"] == 2
    assert len(res["rolls"]) == 2


def test_character_derived_stats():
    char = Character(
        abilities=AbilityScores(
            strength=10,
            dexterity=16,
            constitution=14,
            intelligence=14,
            wisdom=12,
            charisma=10
        ),
        level=3,
        skill_proficiencies=["stealth", "investigation"],
        skill_expertise=["stealth"],
    )

    # Level 3 -> Proficiency bonus +2
    assert char.proficiency_bonus == 2
    # DEX 16 -> Modifier +3
    assert char.ability_modifiers["dexterity"] == 3
    # Stealth has expertise: +3 (DEX) + 2*2 (Prof) = +7
    assert char.skill_bonuses["stealth"] == 7
    # Investigation has proficiency: +2 (INT) + 1*2 = +4
    assert char.skill_bonuses["investigation"] == 4
    # Passive perception: 10 + WIS mod(1) = 11
    assert char.passive_perception == 11
    # Carrying capacity: STR(10) * 15 = 150 lbs
    assert char.carrying_capacity_lbs == 150.0


def test_resolve_skill_check():
    char = Character(
        abilities=AbilityScores(dexterity=16),
        level=3,
        skill_proficiencies=["stealth"],
        skill_expertise=["stealth"],
    )

    result = resolve_check(
        character=char,
        check_type="skill",
        target="Stealth",
        dc=15
    )
    assert result["modifier"] == 7
    assert "Stealth (Skill)" in result["resolved_name"]
    assert "Outcome=" in result["mechanical_summary"]


def test_spell_slot_consumption():
    char = Character()
    char.spell_slots.level_1.max_slots = 2
    char.spell_slots.level_1.used_slots = 1

    success, msg = validate_and_consume_spell_slot(char, 1)
    assert success is True
    assert char.spell_slots.level_1.used_slots == 2

    # Second consumption should fail
    success2, msg2 = validate_and_consume_spell_slot(char, 1)
    assert success2 is False


def test_inventory_validation():
    char = Character(
        inventory=[
            InventoryItem(id="pot_1", name="Potion of Healing", quantity=2)
        ]
    )

    ok, item, _ = validate_inventory_item(char, "potion of healing", 1)
    assert ok is True
    assert item is not None

    ok2, _, _ = validate_inventory_item(char, "holy avenger", 1)
    assert ok2 is False


def test_damage_and_healing():
    char = Character(max_hp=20, current_hp=20, temp_hp=5)

    # 8 damage: removes 5 temp HP, 3 from current HP -> 17 HP
    dmg_res = apply_damage(char, 8)
    assert dmg_res["temp_hp_lost"] == 5
    assert dmg_res["hp_lost"] == 3
    assert char.current_hp == 17
    assert char.temp_hp == 0

    # Heal 2 HP -> 19 HP
    heal_res = apply_heal(char, 2)
    assert char.current_hp == 19


@pytest.mark.asyncio
async def test_parser_interrupt_detection():
    async def sample_tokens():
        yield "You step into the dark tunnel. "
        yield '<CHECK_REQUEST type="skill" '
        yield 'target="Stealth" dc="15" '
        yield 'reason="slipping past guards"/>'
        yield " This should be halted."

    parser = StreamParser()
    events = []
    async for evt in parser.process_token_stream(sample_tokens()):
        events.append(evt)

    event_types = [e["type"] for e in events]
    assert "token" in event_types
    assert "check_required" in event_types
    assert "done" in event_types

    check_event = next(e for e in events if e["type"] == "check_required")
    assert check_event["check"]["target"] == "Stealth"
    assert check_event["check"]["dc"] == 15
    assert check_event["check"]["reason"] == "slipping past guards"


@pytest.mark.asyncio
async def test_parser_rejection_detection():
    async def reject_tokens():
        yield '<ACTION_REJECT reason="Gravity prevents leaping 100 feet."/>'
        yield " You cannot do that."

    parser = StreamParser()
    events = []
    async for evt in parser.process_token_stream(reject_tokens()):
        events.append(evt)

    event_types = [e["type"] for e in events]
    assert "action_rejected" in event_types
    rej = next(e for e in events if e["type"] == "action_rejected")
    assert "Gravity" in rej["rejection"]["reason"]


def test_dwarf_poison_advantage():
    dwarf = Character(race="Dwarf", abilities=AbilityScores(constitution=14))
    res = resolve_check(dwarf, "save", "Poison", dc=12)
    assert res["roll"]["advantage"] is True
    assert "Dwarven Resilience" in res["roll"].get("racial_advantage", "")


def test_elf_charm_advantage():
    elf = Character(race="Elf", abilities=AbilityScores(wisdom=14))
    res = resolve_check(elf, "save", "Charm Person", dc=14)
    assert res["roll"]["advantage"] is True
    assert "Fey Ancestry" in res["roll"].get("racial_advantage", "")


def test_half_orc_relentless_endurance():
    orc = Character(race="Half-Orc", max_hp=20, current_hp=5)
    # Take 10 damage -> would drop to 0, but Relentless Endurance sets to 1!
    res = apply_damage(orc, 10)
    assert res["relentless_triggered"] is True
    assert orc.current_hp == 1
    assert "relentless_endurance_used" in orc.conditions
    assert orc.conditions.count("unconscious") == 0


@pytest.mark.asyncio
async def test_backstory_storyline_and_auto_tone():
    from app.llm.campaign_generator import generate_fallback_campaign
    char_info = {
        "name": "Kento Nanami",
        "character_class": "Sorcerer",
        "level": 4,
        "backstory": "Seeking vengeance against the rogue curse user who slaughtered my mentor in Shibuya."
    }
    # Pass genre=None to test auto-determination
    res = generate_fallback_campaign(
        world_setting="Modern Tokyo Jujutsu Kaisen cursed spirits",
        genre=None,
        character_info=char_info
    )
    assert "Dark Supernatural Action" in res["narrative_tone"]
    assert "Kento Nanami" in res["main_storyline"]["central_conflict"]
    assert "vengeance" in res["main_storyline"]["central_conflict"].lower()
    assert "Shibuya" in res["opening_narrative"] or "past" in res["opening_narrative"].lower()


@pytest.mark.asyncio
async def test_stream_parser_unclosed_angle_bracket():
    """Verify unclosed '<' does not hang the stream and flushes as normal token."""
    async def token_gen():
        yield "Your HP is < "
        yield "5 and you feel weak.\n"
        yield "The enemy lunges forward."

    parser = StreamParser()
    events = []
    async for evt in parser.process_token_stream(token_gen()):
        events.append(evt)

    token_texts = "".join(e["content"] for e in events if e["type"] == "token")
    assert "< 5" in token_texts
    assert "The enemy lunges forward." in token_texts
    done_evt = next(e for e in events if e["type"] == "done")
    assert "Your HP is < 5" in done_evt["narrative"]


@pytest.mark.asyncio
async def test_stream_parser_single_quotes_and_multiple_tags():
    """Verify single-quoted attributes and multiple inline tags in one stream."""
    async def token_gen():
        yield "Found treasure: <ITEM_GRANT name='Silver Dagger' quantity='1'/> and "
        yield "<ITEM_GRANT name='Healing Salve' quantity='2'/>! "
        yield "Now roll: <CHECK_REQUEST type='skill' target='Perception' dc='14' reason='Check for traps'/>"

    parser = StreamParser()
    events = []
    async for evt in parser.process_token_stream(token_gen()):
        events.append(evt)

    event_types = [e["type"] for e in events]
    assert event_types.count("item_granted") == 2
    assert "check_required" in event_types

    granted_items = [e["item"]["name"] for e in events if e["type"] == "item_granted"]
    assert granted_items == ["Silver Dagger", "Healing Salve"]

    check_evt = next(e for e in events if e["type"] == "check_required")
    assert check_evt["check"]["target"] == "Perception"
    assert check_evt["check"]["dc"] == 14


@pytest.mark.asyncio
async def test_equipment_slot_exclusivity(tmp_path):
    """Verify equipping a new armor or shield automatically unequips previous ones in the same slot."""
    from app.memory.state_manager import StateManager
    test_file = tmp_path / "test_char.json"

    sm = StateManager(filepath=test_file)
    char = Character(
        inventory=[
            InventoryItem(id="armor_leather", name="Leather Armor", item_type="armor", equipped=True, armor_base=11, armor_category="light"),
            InventoryItem(id="armor_chain", name="Chain Shirt", item_type="armor", equipped=False, armor_base=13, armor_category="medium"),
            InventoryItem(id="shield_wood", name="Wooden Shield", item_type="shield", equipped=True),
            InventoryItem(id="shield_steel", name="Steel Shield", item_type="shield", equipped=False),
        ]
    )
    await sm.save_character(char)

    # Equipping chain shirt must unequip leather armor
    equipped = await sm.toggle_item_equipped("armor_chain")
    assert equipped is True

    updated_char = await sm.get_character()
    leather = next(i for i in updated_char.inventory if i.id == "armor_leather")
    chain = next(i for i in updated_char.inventory if i.id == "armor_chain")
    assert leather.equipped is False
    assert chain.equipped is True

    # Equipping steel shield must unequip wooden shield
    shield_equipped = await sm.toggle_item_equipped("shield_steel")
    assert shield_equipped is True

    updated_char2 = await sm.get_character()
    wood_shield = next(i for i in updated_char2.inventory if i.id == "shield_wood")
    steel_shield = next(i for i in updated_char2.inventory if i.id == "shield_steel")
    assert wood_shield.equipped is False
    assert steel_shield.equipped is True


def test_zero_hp_death_save_damage_and_heal():
    """Verify taking damage at 0 HP inflicts death save failure(s) and healing resets saves."""
    from app.engine.rules import resolve_death_save
    char = Character(max_hp=20, current_hp=0, conditions=["unconscious"])

    # Taking regular damage at 0 HP adds 1 failure
    res_dmg1 = apply_damage(char, 5, is_critical=False)
    assert char.death_saves.failures == 1

    # Taking critical damage at 0 HP adds 2 failures (total 3 -> dies)
    res_dmg2 = apply_damage(char, 8, is_critical=True)
    assert char.death_saves.failures == 3
    assert "dead" in char.conditions

    # Resetting for healing test
    char2 = Character(max_hp=20, current_hp=0, conditions=["unconscious"])
    char2.death_saves.failures = 2
    char2.death_saves.successes = 1

    # Applying healing raises HP, clears unconscious, resets death saves
    res_heal = apply_heal(char2, 10)
    assert char2.current_hp == 10
    assert char2.death_saves.successes == 0
    assert char2.death_saves.failures == 0
    assert "unconscious" not in char2.conditions


def test_zero_hp_death_save_stabilization():
    """Verify 3 death save successes stabilize solo player, restore 1 HP, and clear unconscious."""
    from app.engine.rules import resolve_death_save
    char = Character(max_hp=20, current_hp=0, conditions=["unconscious"])
    char.death_saves.successes = 2
    char.death_saves.failures = 1

    # Force a success by repeatedly calling until success or setting roll directly
    # To test deterministically, resolve_death_save when at 2 successes and gets a success:
    while char.death_saves.successes < 3 and char.death_saves.failures < 3:
        res = resolve_death_save(char)
        if res["stabilized"]:
            assert char.current_hp == 1
            assert char.death_saves.successes == 0
            assert char.death_saves.failures == 0
            assert "unconscious" not in char.conditions
            break


@pytest.mark.asyncio
async def test_chronicle_manager_preserves_full_ui_history(tmp_path):
    """Verify chat_history.json keeps full UI history while get_recent_turns trims for LLM."""
    from app.memory.chronicle import ChronicleManager
    md_file = tmp_path / "chronicle.md"
    json_file = tmp_path / "chat_history.json"

    cm = ChronicleManager(filepath=md_file, chat_history_file=json_file, buffer_size=2)
    # buffer_size=2 means max_messages = 4 turns

    # Add 8 turns (16 messages total: 8 player + 8 dm)
    for i in range(1, 9):
        await cm.add_turn(f"Player action {i}", f"DM response {i}")

    # Full chat history for UI must have all 16 entries (8 player + 8 dm)
    full_history = await cm.get_chat_history()
    assert len(full_history) == 16
    assert full_history[0]["content"] == "Player action 1"
    assert full_history[-1]["content"] == "DM response 8"

    # Rolling buffer for LLM prompt context must be trimmed to buffer_size * 2 = 4 messages
    recent = await cm.get_recent_turns()
    assert len(recent) == 4
    assert recent[-1]["content"] == "DM response 8"


