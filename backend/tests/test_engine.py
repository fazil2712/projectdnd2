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

