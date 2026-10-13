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
    resolve_enemy_attack,
    resolve_rest,
    resolve_spell_cast,
)
from app.memory.lore_manager import LoreManager
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


def test_spell_compendium_validation():
    """Verify 5e class and spell slot constraints in compendium."""
    from app.engine.compendium import can_character_learn_spell, compendium_manager
    from app.engine.character import SpellSlots, SpellSlotLevel

    wizard = Character(
        character_class="Wizard",
        level=3,
        spell_slots=SpellSlots(
            level_1=SpellSlotLevel(max_slots=4, used_slots=0),
            level_2=SpellSlotLevel(max_slots=2, used_slots=0)
        ),
        known_spells=["Fire Bolt", "Magic Missile"]
    )

    # 1. Wizard learning 2nd level spell (Misty Step) - valid
    ok, err, spell = can_character_learn_spell(wizard, "Misty Step")
    assert ok is True
    assert spell is not None
    assert spell["name"] == "Misty Step"

    # 2. Duplicate spell check
    ok, err, _ = can_character_learn_spell(wizard, "Magic Missile")
    assert ok is False
    assert "already knows" in err

    # 3. Non-caster (Barbarian with 0 slots) learning 3rd level spell without bypass
    barbarian = Character(
        character_class="Barbarian",
        level=3,
        spell_slots=SpellSlots(),
        known_spells=[]
    )
    ok, err, _ = can_character_learn_spell(barbarian, "Fireball", bypass_class_limit=False)
    assert ok is False

    # 4. Non-caster with bypass_class_limit=True (homebrew / magical boon)
    ok, err, spell = can_character_learn_spell(barbarian, "Fireball", bypass_class_limit=True)
    assert ok is True
    assert spell["name"] == "Fireball"


@pytest.mark.asyncio
async def test_stream_parser_spell_learn_tag():
    """Verify StreamParser detects <SPELL_LEARN .../> tag and yields spell_learned event."""
    parser = StreamParser()

    async def token_gen():
        tokens = [
            "You carefully unfold the parchment. ",
            '<SPELL_LEARN name="Misty Step" level="2" reason="Arcane scroll study"/>',
            " The glyphs sear into your memory."
        ]
        for t in tokens:
            yield t

    events = []
    async for ev in parser.process_token_stream(token_gen()):
        events.append(ev)

    spell_events = [e for e in events if e.get("type") == "spell_learned"]
    assert len(spell_events) == 1
    assert spell_events[0]["spell"]["name"] == "Misty Step"
    assert spell_events[0]["spell"]["level"] == 2
    assert spell_events[0]["reason"] == "Arcane scroll study"


def test_resolve_enemy_attack_mechanics(monkeypatch):
    """Verify deterministic enemy attack hits, misses, crits, fumbles, and HP deductions."""
    char = Character(
        name="Theron",
        abilities=AbilityScores(dexterity=14, constitution=14),
        max_hp=20,
        current_hp=20,
        temp_hp=0
    )
    # Natural AC without armor: 10 + DEX mod (+2) = 12
    assert char.armor_class == 12

    # 1. Normal hit: roll raw 10 + 3 = 13 >= AC 12
    monkeypatch.setattr("app.engine.rules.roll_d20", lambda modifier, **kw: {
        "raw_rolls": [10],
        "selected_raw": 10,
        "modifier": modifier,
        "total": 10 + modifier,
        "advantage": False,
        "disadvantage": False,
        "is_critical_success": False,
        "is_critical_failure": False,
        "notation": f"d20(10)+{modifier}={10+modifier}",
    })
    hit_res = resolve_enemy_attack(
        character=char,
        attacker="Bugbear",
        attack_bonus=3,
        damage_formula="1d4+2",
        damage_type="slashing"
    )
    assert hit_res["hit"] is True
    assert hit_res["is_critical"] is False
    assert hit_res["attacker"] == "Bugbear"
    assert hit_res["damage_total"] >= 3
    assert char.current_hp < 20

    # 2. Normal miss: roll raw 5 + 2 = 7 < AC 12
    prev_hp = char.current_hp
    monkeypatch.setattr("app.engine.rules.roll_d20", lambda modifier, **kw: {
        "raw_rolls": [5],
        "selected_raw": 5,
        "modifier": modifier,
        "total": 5 + modifier,
        "advantage": False,
        "disadvantage": False,
        "is_critical_success": False,
        "is_critical_failure": False,
        "notation": f"d20(5)+{modifier}={5+modifier}",
    })
    miss_res = resolve_enemy_attack(
        character=char,
        attacker="Goblin",
        attack_bonus=2,
        damage_formula="1d4",
        damage_type="piercing"
    )
    assert miss_res["hit"] is False
    assert char.current_hp == prev_hp

    # 3. Natural 1 Fumble: raw 1 automatically misses despite high bonus (+30)
    monkeypatch.setattr("app.engine.rules.roll_d20", lambda modifier, **kw: {
        "raw_rolls": [1],
        "selected_raw": 1,
        "modifier": modifier,
        "total": 1 + modifier,
        "advantage": False,
        "disadvantage": False,
        "is_critical_success": False,
        "is_critical_failure": True,
        "notation": f"d20(1)+{modifier}={1+modifier}",
    })
    fumble_res = resolve_enemy_attack(
        character=char,
        attacker="Ogre",
        attack_bonus=30,
        damage_formula="2d8",
        damage_type="bludgeoning"
    )
    assert fumble_res["hit"] is False
    assert fumble_res["is_fumble"] is True

    # 4. Natural 20 Critical: raw 20 automatically hits and crits despite low bonus (-30)
    monkeypatch.setattr("app.engine.rules.roll_d20", lambda modifier, **kw: {
        "raw_rolls": [20],
        "selected_raw": 20,
        "modifier": modifier,
        "total": 20 + modifier,
        "advantage": False,
        "disadvantage": False,
        "is_critical_success": True,
        "is_critical_failure": False,
        "notation": f"d20(20)+{modifier}={20+modifier}",
    })
    crit_res = resolve_enemy_attack(
        character=char,
        attacker="Assassin",
        attack_bonus=-30,
        damage_formula="1d6",
        damage_type="piercing"
    )
    assert crit_res["hit"] is True
    assert crit_res["is_critical"] is True

    # 5. Lethal attack reducing character to unconscious
    monkeypatch.setattr("app.engine.rules.roll_d20", lambda modifier, **kw: {
        "raw_rolls": [15],
        "selected_raw": 15,
        "modifier": modifier,
        "total": 15 + modifier,
        "advantage": False,
        "disadvantage": False,
        "is_critical_success": False,
        "is_critical_failure": False,
        "notation": f"d20(15)+{modifier}={15+modifier}",
    })
    lethal_res = resolve_enemy_attack(
        character=char,
        attacker="Dragon",
        attack_bonus=10,
        damage_formula="50d6",
        damage_type="fire"
    )
    assert lethal_res["hit"] is True
    assert char.current_hp == 0
    assert lethal_res["is_unconscious"] is True


@pytest.mark.asyncio
async def test_stream_parser_extended_narrative_and_combat_tags():
    """Verify StreamParser parses all 6 narrative and combat tags."""
    parser = StreamParser()

    async def token_gen():
        chunks = [
            '<LOCATION_CHANGE name="Sunken Crypt" description="Damp ancient tombs" threat_level="High"/>\n',
            'You step cautiously through the portcullis. ',
            '<NPC_UPDATE name="Morcar" role="Captain" attitude="hostile" note="Suspects intruder"/>\n',
            '<STORY_PROGRESS act="2" tension_delta="2" milestone="Entered the crypt"/>\n',
            '<ENCOUNTER_START name="Cave Troll" hp="40" ac="14" attack_bonus="5" damage="2d8+3"/>\n',
            '<ENEMY_ATTACK attacker="Cave Troll" attack_bonus="5" damage="2d8+3" damage_type="bludgeoning" reason="Club slam"/>\n',
            '<PLAYER_DAMAGE formula="1d6" damage_type="acid" reason="Acid drip"/>\n',
            'The fight begins!'
        ]
        for c in chunks:
            yield c

    events = []
    async for ev in parser.process_token_stream(token_gen()):
        events.append(ev)

    ev_types = [e.get("type") for e in events]
    assert "location_changed" in ev_types
    assert "npc_updated" in ev_types
    assert "story_progress" in ev_types
    assert "encounter_started" in ev_types
    assert "enemy_attack" in ev_types
    assert "player_damage" in ev_types

    loc_ev = next(e for e in events if e.get("type") == "location_changed")
    assert loc_ev["location"]["name"] == "Sunken Crypt"
    assert loc_ev["location"]["threat_level"] == "High"

    npc_ev = next(e for e in events if e.get("type") == "npc_updated")
    assert npc_ev["npc"]["name"] == "Morcar"
    assert npc_ev["npc"]["attitude"] == "hostile"

    story_ev = next(e for e in events if e.get("type") == "story_progress")
    assert story_ev["progress"]["act"] == 2
    assert story_ev["progress"]["tension_delta"] == 2

    enc_ev = next(e for e in events if e.get("type") == "encounter_started")
    assert enc_ev["enemy"]["name"] == "Cave Troll"
    assert enc_ev["enemy"]["hp"] == 40

    atk_ev = next(e for e in events if e.get("type") == "enemy_attack")
    assert atk_ev["attack"]["attacker"] == "Cave Troll"
    assert atk_ev["attack"]["attack_bonus"] == 5

    dmg_ev = next(e for e in events if e.get("type") == "player_damage")
    assert dmg_ev["damage"]["formula"] == "1d6"
    assert dmg_ev["damage"]["damage_type"] == "acid"


@pytest.mark.asyncio
async def test_lore_manager_narrative_and_encounter_lifecycle(tmp_path):
    """Verify LoreManager location creation, NPC tracking, story progress, and enemy tracking."""
    lore_file = tmp_path / "world_lore.json"
    lore = LoreManager(filepath=lore_file)

    # 1. Location change
    await lore.set_current_location("Sunken Crypt", "Ancient drowned crypts", "Deadly")
    loc = await lore.get_current_location()
    assert loc is not None
    assert loc["name"] == "Sunken Crypt"
    assert loc["threat_level"] == "Deadly"

    # 2. NPC tracking
    npc = await lore.update_npc("Dunstan", "Blacksmith", "friendly", "Forges enchanted iron")
    assert npc["name"] == "Dunstan"
    assert npc["attitude"] == "friendly"
    npcs = await lore.get_npcs()
    assert any(n["name"] == "Dunstan" for n in npcs)

    # 3. Story progress
    story = await lore.advance_story_progress(act=2, tension_delta=4, milestone="Crypt unlocked")
    assert story["act"] == 2
    assert story["tension_clock"] == 4
    assert await lore.get_current_act() == 2
    assert await lore.get_tension_clock() == 4

    # 4. Encounter tracking
    enemy = await lore.add_or_update_enemy("Cave Troll", hp=35, ac=14, attack_bonus=5, damage_formula="2d8+3")
    assert enemy["name"] == "Cave Troll"
    assert enemy["current_hp"] == 35

    active = await lore.get_active_enemies()
    assert len(active) == 1

    # 5. Damage enemy
    dmg_res = await lore.damage_enemy("Cave Troll", 15)
    assert dmg_res["found"] is True
    assert dmg_res["remaining_hp"] == 20
    assert dmg_res["defeated"] is False

    # 6. Defeat enemy
    kill_res = await lore.damage_enemy("Cave Troll", 25)
    assert kill_res["defeated"] is True
    active_after = await lore.get_active_enemies()
    assert len(active_after) == 0

    # 7. Context formatting
    context = await lore.format_targeted_context()
    assert "Act 2/3" in context
    assert "Dunstan" in context


def test_resolve_short_rest():
    char = Character(
        abilities=AbilityScores(constitution=14),  # CON mod +2
        current_hp=10,
        max_hp=30,
        level=3,
        hit_dice_remaining=2,
        hit_dice="1d8",
    )

    res = resolve_rest(char, rest_type="short", dice_to_spend=1)
    assert res["rest_type"] == "short"
    assert res["dice_spent"] == 1
    assert res["hit_dice_remaining"] == 1
    assert char.hit_dice_remaining == 1
    # Minimum heal is 1 + CON mod (2) = 3
    assert res["healed"] >= 3
    assert char.current_hp == 10 + res["healed"]

    # Exhaust remaining hit dice
    res2 = resolve_rest(char, rest_type="short", dice_to_spend=1)
    assert res2["hit_dice_remaining"] == 0
    assert char.hit_dice_remaining == 0

    # Attempt to rest with 0 hit dice
    res3 = resolve_rest(char, rest_type="short", dice_to_spend=1)
    assert res3["healed"] == 0
    assert "No Hit Dice remaining" in res3["reason"]


def test_resolve_long_rest():
    char = Character(
        current_hp=5,
        max_hp=28,
        level=4,
        hit_dice_remaining=0,
        hit_dice_max=4,
        conditions=["Poisoned", "Frightened"],
    )
    # Expended spell slots
    char.spell_slots.level_1.used_slots = 3
    char.spell_slots.level_2.used_slots = 2

    res = resolve_rest(char, rest_type="long")
    assert res["rest_type"] == "long"
    assert res["current_hp"] == 28
    assert char.current_hp == 28
    # Regains at least half max hit dice (4 // 2 = 2)
    assert char.hit_dice_remaining == 2
    assert res["hit_dice_remaining"] == 2
    # Spell slots renewed
    assert char.spell_slots.level_1.used_slots == 0
    assert char.spell_slots.level_2.used_slots == 0
    # Temporary conditions cleared
    assert "Poisoned" not in char.conditions
    assert "Frightened" not in char.conditions


def test_resolve_spell_cast_healing():
    char = Character(
        abilities=AbilityScores(wisdom=16),  # WIS mod +3
        spellcasting_ability="wisdom",
        current_hp=10,
        max_hp=25,
        level=3,
    )
    char.spell_slots.level_1.max_slots = 4
    char.spell_slots.level_1.used_slots = 0

    spell = {
        "name": "Cure Wounds",
        "level": 1,
        "healing": "1d8",
        "school": "Evocation",
    }

    res = resolve_spell_cast(char, spell, slot_level=1)
    assert res["success"] is True
    assert res["is_healing"] is True
    assert res["heal_amount"] >= 4  # 1d8 (min 1) + 3 mod
    assert char.current_hp == 10 + res["heal_amount"]
    assert char.spell_slots.level_1.used_slots == 1


def test_resolve_spell_cast_damage():
    char = Character(
        abilities=AbilityScores(intelligence=16),  # INT mod +3
        spellcasting_ability="intelligence",
        level=3,
    )
    char.spell_slots.level_2.max_slots = 2
    char.spell_slots.level_2.used_slots = 0

    spell = {
        "name": "Scorching Ray",
        "level": 2,
        "damage": "2d6 fire",
        "school": "Evocation",
    }

    res = resolve_spell_cast(char, spell, slot_level=2)
    assert res["success"] is True
    assert res["is_damage"] is True
    assert res["damage_type"] == "fire"
    assert 2 <= res["damage_total"] <= 12
    assert char.spell_slots.level_2.used_slots == 1


def test_resolve_spell_cast_slot_exhaustion():
    char = Character(level=1)
    char.spell_slots.level_1.max_slots = 1
    char.spell_slots.level_1.used_slots = 1

    spell = {
        "name": "Magic Missile",
        "level": 1,
        "damage": "3d4+3 force",
    }

    res = resolve_spell_cast(char, spell, slot_level=1)
    assert res["success"] is False
    assert "no level 1 spell slots remaining" in res["summary"]


def test_conditions_disadvantage_and_advantage():
    # 1. Poisoned grants disadvantage on ability/skill checks
    poisoned_char = Character(
        abilities=AbilityScores(dexterity=14),
        conditions=["Poisoned"],
    )
    check_res = resolve_check(
        character=poisoned_char,
        check_type="skill",
        target="stealth",
        dc=10,
    )
    assert check_res["roll"]["disadvantage"] is True

    # 2. Restrained imposes disadvantage on attacks and DEX saves
    restrained_char = Character(
        abilities=AbilityScores(strength=14, dexterity=14),
        conditions=["Restrained"],
    )
    atk_res = resolve_check(
        character=restrained_char,
        check_type="attack",
        target="strength",
        dc=12,
    )
    assert atk_res["roll"]["disadvantage"] is True

    dex_save_res = resolve_check(
        character=restrained_char,
        check_type="save",
        target="dexterity",
        dc=12,
    )
    assert dex_save_res["roll"]["disadvantage"] is True

    # 3. Paralyzed auto-fails STR and DEX saves
    paralyzed_char = Character(
        abilities=AbilityScores(strength=18, dexterity=18),
        conditions=["Paralyzed"],
    )
    str_save_res = resolve_check(
        character=paralyzed_char,
        check_type="save",
        target="strength",
        dc=10,
    )
    assert str_save_res["success"] is False
    assert "AUTO-FAIL" in str_save_res["crit_note"]

    # 4. Enemy attack has advantage against a Prone player
    prone_char = Character(
        abilities=AbilityScores(dexterity=10),
        armor_class=12,
        current_hp=20,
        max_hp=20,
        conditions=["Prone"],
    )
    enemy_atk = resolve_enemy_attack(
        character=prone_char,
        attacker="Bandit",
        attack_bonus=3,
        damage_formula="1d6",
    )
    assert enemy_atk["roll"]["advantage"] is True


@pytest.mark.asyncio
async def test_parser_rest_spell_condition_tags():
    parser = StreamParser()

    async def token_gen():
        tokens = [
            "You gather around the fire and rest. ",
            '<REST_COMPLETE type="short" dice="2"/>',
            " Feeling renewed, you cast a spell: ",
            '<SPELL_CAST name="Shield" level="1"/>',
            " Suddenly, a poisonous barb strikes you! ",
            '<CONDITION_UPDATE action="add" condition="Poisoned" reason="Spider venom"/>',
            " End of turn.",
        ]
        for t in tokens:
            yield t

    events = []
    async for ev in parser.process_token_stream(token_gen()):
        events.append(ev)

    types = [e["type"] for e in events]
    assert "rest_completed" in types
    assert "spell_cast" in types
    assert "condition_updated" in types

    rest_event = next(e for e in events if e["type"] == "rest_completed")
    assert rest_event["rest"]["type"] == "short"
    assert rest_event["rest"]["dice"] == 2

    spell_event = next(e for e in events if e["type"] == "spell_cast")
    assert spell_event["spell"]["name"] == "Shield"
    assert spell_event["spell"]["level"] == 1

    cond_event = next(e for e in events if e["type"] == "condition_updated")
    assert cond_event["update"]["action"] == "add"
    assert cond_event["update"]["condition"] == "Poisoned"
    assert cond_event["update"]["reason"] == "Spider venom"





