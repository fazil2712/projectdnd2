import json
import asyncio
import re
from typing import Dict, Any, Optional
from .client import ollama_client


DEFAULT_THEMES = {
    "fantasy": {
        "keywords": [
            "forgotten realms", "sword coast", "faerun", "d&d", "dnd", "5e", "high fantasy",
            "toril", "waterdeep", "baldur", "neverwinter", "dungeon", "dragon", "harpers",
            "zhentarim", "netherese", "phandalin", "goblinoid", "high fantasy & heroic epic"
        ],
        "campaign_name": "Shadows over the Sword Coast: The Netherese Cipher",
        "narrative_tone": "Authentic D&D 5e High Fantasy Adventure. Ancient Netherese ruins, perilous wilderness trails, and high-stakes faction intrigue with visceral danger and tactical realism.",
        "starting_location_name": "The Crag of Whispers - Netherese Excavation Site",
        "starting_location_description": "Rain-slicked grey granite ruins jut from the pine-shrouded ridge of the Sword Mountains. Fallen columns carved with floating Netherese glyphs lie half-buried in brambles, while a collapsed stone stairway descends into a subterranean burial vault.",
        "main_storyline": {
            "central_conflict": "A rogue faction of Zhentarim mercenaries has unsealed a buried Netherese vault beneath the Sword Coast, seeking an ancient mythallar cipher capable of siphoning magic from regional leylines.",
            "antagonist": "Varek Stonegaze, a ruthless Zhentarim spellblade leading the excavation.",
            "active_threat": "Hobgoblin reavers patrolling the perimeter ridge and unstable arcane leyline surges discharging from the lower vault.",
            "act_1": "Breach the outer perimeter of the Crag, neutralize the sentries, and secure the vault threshold.",
            "act_2": "Navigate the trapped Netherese labyrinth, solve the arcane lockstones, and prevent the cipher's extraction.",
            "act_3": "Confront Varek Stonegaze atop the ancient skyward dais before he activates the Netherese siphon."
        },
        "opening_narrative": (
            "Cold mountain wind sweeps across the crag, carrying the acrid smell of burnt pitch and wet granite. "
            "Ahead, half-concealed beneath the crumbling stone archway of a forgotten Netherese excavation, two hobgoblin scouts clad in banded mail examine a shattered warding stone with iron lanterns. "
            "One of them snarls in Goblin and raises a barbed spear as a stray pebble rolls beneath your boot.\n\n"
            "Behind you lies the steep, mud-choked descent to the Trade Way. What do you do?"
        )
    },
    "jjk": {
        "keywords": ["jujutsu", "jujutsu kaisen", "cursed spirit", "cursed energy", "cursed womb", "sukuna", "gojo", "itadori", "shibuya", "shinigami", "jujutsu high", "curse user"],
        "campaign_name": "Cursed Threshold: Shibuya Incursion",
        "narrative_tone": "Dark Supernatural Action & Psychological Horror. Tension is thick, cursed energy feels heavy and suffocating, danger is lethal and sudden.",
        "starting_location_name": "Quarantined Eizan Academy - West Wing Corridors",
        "starting_location_description": "Flickering fluorescent lights hum erratically against cracked tiles and peeling warning signs. A foul, metallic stench of rotten ozone permeates the humid air. The entire perimeter is enclosed by an impenetrable semi-translucent Cursed Veil that blocks cellular signal and outside moonlight.",
        "main_storyline": {
            "central_conflict": "A nascent Special Grade cursed womb has materialized in the quarantined facility's sub-levels, attracting renegade curse users seeking to harvest its core before Jujutsu High sorcerers can exorcise it.",
            "antagonist": "Arata Kuroda, a renegade curse user manipulating residual curses to breach the containment seal.",
            "active_threat": "Corridor-stalking Grade 2 fly-head swarms and the pulsating cursed womb rapidly completing its gestation.",
            "act_1": "Breach the outer veil corridors, rescue trapped non-sorcerers, and locate the cursed womb before metamorphosis completes.",
            "act_2": "Infiltrate the flooded basement generator vault, battle Kuroda's shikigami, and disable the ritual barrier.",
            "act_3": "Climactic confrontation against the fully awakened Special Grade curse and Kuroda before the veil expands across Tokyo."
        },
        "opening_narrative": (
            "The air inside the veil drops ten degrees, tasting of bitter iron and ozone. "
            "Above your head, fluorescent tubes flicker and burst in rhythmic succession as heavy cursed energy saturates the corridor. "
            "From the ceiling ventilation shafts thirty feet ahead, the chitinous scrape of claws echoes—a cluster of bloated Grade 2 fly-head curses drop silently to the linoleum floor, their multi-jointed limbs twitching as their composite eyes lock onto your presence.\n\n"
            "The cursed womb pulses somewhere deeper in the dark below, its heartbeat rattling the windowpanes. You are cut off from Jujutsu High reinforcement. What do you do?"
        )
    },
    "souls": {
        "keywords": ["dark souls", "elden ring", "bloodborne", "ash", "undead", "hollow", "bonfire", "abyss", "grace", "tarnished"],
        "campaign_name": "Ashes of the Forgotten Hegemony",
        "narrative_tone": "Bleak, atmospheric, and unforgiving grimdark fantasy. Melancholy silence punctuated by violent, heavy clashes and decaying majesty.",
        "starting_location_name": "The Sunken Bastion of Cael-Morn",
        "starting_location_description": "A perpetual grey drizzle falls upon crumbling basalt buttresses. Piles of calcified armor and ancient banners lie half-buried in cold mud, while a single dying brazier gutters weakly against the freezing wind.",
        "main_storyline": {
            "central_conflict": "The sovereign flame has fractured, unleashing an abyssal blight that hollows the minds of the realm's last defenders while an ancient warlord seeks to consume the remaining embers.",
            "antagonist": "The Ashen Castellan, a hulking hollow knight bound to an unquenchable oath.",
            "active_threat": "Mad sentinels patrolling the outer ramparts and black rot rising from the moat.",
            "act_1": "Ascend the sunken lower bailey, breach the portcullis, and rekindle the central beacon.",
            "act_2": "Delve beneath the crypts of the drowned knights to recover the Seal of the Embers.",
            "act_3": "Defeat the Ashen Castellan atop the high throne ramparts before the final light is extinguished."
        },
        "opening_narrative": (
            "Ash clings like damp grey snow to the ridges of your armor. "
            "A gust of wind sweeps across the ruined parapet of Cael-Morn, carrying the sharp scent of dried blood and rusted iron. "
            "Ahead, blocking the only stone archway into the interior keep, a hollowed knight in pitted chainmail leans heavily on a notched greatsword. "
            "As your boots crunch against shattered slate, its gauntleted head snaps toward you with a sickening jerk, and a low, dry rasp escapes its rotted throat. It raises its blade in both hands.\n\n"
            "The descent behind you has collapsed. What do you do?"
        )
    },
    "cyber": {
        "keywords": ["cyberpunk", "cyber", "neon", "corp", "megacorp", "hacker", "synth", "chrome", "implants", "neo-tokyo", "night city"],
        "campaign_name": "Neon Syndicate: Protocol Breach",
        "narrative_tone": "High-tech noir, gritty and kinetic. Slick rain-slicked asphalt, vibrant neon glare, brutal corpo politics, and street-level desperation.",
        "starting_location_name": "Sector 4 Underbelly - Chiba Back-Alley",
        "starting_location_description": "Rain streams down towering holographic billboards advertising synthetic stims and cybernetic augments. The air hums with electromagnetic interference, smell of ozone, and fried synthetic noodles.",
        "main_storyline": {
            "central_conflict": "A rogue AI fragment stolen from Arasaka/OmniCorp has been smuggled into the lower wards, triggering a lethal purge by black-ops kill teams and street syndicates.",
            "antagonist": "Director Vance Thorne and the OmniCorp Black-Ops Tactical Unit.",
            "active_threat": "Corpo hunter-killer drones scanning the alleyway and syndicate scavengers closing in.",
            "act_1": "Evade the initial corporate ambush, decrypt the stolen datashard, and find safe refuge.",
            "act_2": "Infiltrate the high-altitude corporate data relay tower to broadcast the syndicate conspiracy.",
            "act_3": "Climactic extraction or confrontation atop the corpo helipad against Thorne's gunship."
        },
        "opening_narrative": (
            "Acid rain hisses against the pavement, reflecting the flickering magenta glare of a neon noodle sign above. "
            "Your com-link crackles with violent static—the encryption key just failed. "
            "Down at the mouth of the narrow alleyway, the high-pitched whine of twin rotor turbines cuts through the rain: a stealth surveillance drone hovers into view, its red targeting laser sweeping the wet garbage and brickwork, stopping six inches from your boots.\n\n"
            "Behind you is a padlocked chainlink gate. What do you do?"
        )
    },
    "gothic": {
        "keywords": ["barovia", "vampire", "strahd", "gothic", "horror", "castle", "fog", "dread", "undead", "werewolf", "gothic horror"],
        "campaign_name": "Dread Over the Sanguine Valley",
        "narrative_tone": "Oppressive gothic horror steeped in psychological dread, macabre omens, cold mist, and inescapable isolation.",
        "starting_location_name": "The Gallows Crossroads",
        "starting_location_description": "A choking white fog clings knee-high to the sodden loam. An ancient wooden gallows creaks slowly in the freezing draft, beside a moldering wooden signpost pointing into the black woods.",
        "main_storyline": {
            "central_conflict": "The realm is trapped beneath perpetual thunderheads by an ancient vampire lord who toys with trapped outsiders.",
            "antagonist": "Count Vane von Kross, the ancient sovereign of the high castle.",
            "active_threat": "Dire wolves circling the mist-shrouded roads and shadowy specters haunting the crossroad.",
            "act_1": "Survive the night on the misty Svalich road and escort surviving villagers to the fortified abbey.",
            "act_2": "Locate the ancient relics needed to pierce the vampire's warding stones.",
            "act_3": "Storm the spire of Castle Ravenkross for a final life-or-death confrontation."
        },
        "opening_narrative": (
            "The mist wraps around you like a wet burial shroud, deadening the sound of your own breathing. "
            "Beside the road, a solitary wooden gallows creaks in the freezing wind. "
            "From the thick, thorn-choked treeline to your left comes the snap of a branch, followed immediately by the deep, guttural growl of a predator far larger than any natural wolf. "
            "Yellow eyes reflect from the darkness between the twisted pines.\n\n"
            "The road ahead disappears into the dense fog. What do you do?"
        )
    }
}


def _match_archetype(world_setting: str, genre: Optional[str] = None, backstory: Optional[str] = None) -> Optional[Dict[str, Any]]:
    ws_lower = world_setting.lower().strip()
    genre_lower = (genre or "").lower().strip()
    backstory_lower = (backstory or "").lower().strip()

    # 1. Primary Priority: Match explicit world setting first
    for theme_key, data in DEFAULT_THEMES.items():
        if any(kw in ws_lower for kw in data["keywords"]):
            return data

    # 2. Secondary Priority: Match genre if specified
    if genre_lower:
        for theme_key, data in DEFAULT_THEMES.items():
            if any(kw in genre_lower for kw in data["keywords"]):
                return data

    # 3. Tertiary Priority: Combined world setting + genre
    combined_setting = f"{ws_lower} {genre_lower}".strip()
    for theme_key, data in DEFAULT_THEMES.items():
        if any(kw in combined_setting for kw in data["keywords"]):
            return data

    # 4. Quaternary Priority: Check backstory only if strong thematic signature
    for theme_key, data in DEFAULT_THEMES.items():
        if any(kw in backstory_lower for kw in data["keywords"]):
            return data

    return DEFAULT_THEMES["fantasy"]


def generate_fallback_campaign(world_setting: str, genre: Optional[str], character_info: Dict[str, Any]) -> Dict[str, Any]:
    backstory = character_info.get("backstory", "").strip()
    matched = _match_archetype(world_setting, genre, backstory) or DEFAULT_THEMES["fantasy"]
    char_name = character_info.get("name", "The Adventurer")
    char_cls = character_info.get("character_class", "Hero")
    char_lvl = character_info.get("level", 1)

    # Auto-deduce genre / tone if not provided
    effective_genre = genre.strip() if (genre and genre.strip()) else None
    if not effective_genre:
        ws_lower = world_setting.lower()
        if any(k in ws_lower for k in ["jujutsu", "cursed spirit", "cursed energy", "shibuya", "shinigami"]):
            effective_genre = "Dark Supernatural Action"
        elif any(k in ws_lower for k in ["cyber", "neon", "corp", "synth", "chrome", "hacker"]):
            effective_genre = "Cyberpunk Arcane Noir"
        elif any(k in ws_lower for k in ["vampire", "strahd", "barovia", "gothic", "dread"]):
            effective_genre = "Gothic Horror & Dread"
        elif any(k in ws_lower for k in ["ash", "soul", "hollow", "decay", "elden", "grim"]):
            effective_genre = "Grimdark & Visceral"
        else:
            effective_genre = "High Fantasy & Heroic Epic"

    if matched:
        base_storyline = dict(matched["main_storyline"])
        opening = matched["opening_narrative"]
        # Blend in backstory if provided
        if backstory:
            base_storyline["central_conflict"] = (
                f"{base_storyline['central_conflict']} "
                f"For {char_name}, this crisis is deeply personal: {backstory}."
            )
            base_storyline["act_1"] = f"{base_storyline['act_1']} Driven by your past ({backstory[:60]}...), you press forward."
            opening = f"Memories of your past linger heavily—{backstory[:90]}... \n\n{opening}"

        return {
            "campaign_name": matched["campaign_name"],
            "narrative_tone": matched["narrative_tone"],
            "starting_location_name": matched["starting_location_name"],
            "starting_location_description": matched["starting_location_description"],
            "main_storyline": base_storyline,
            "opening_narrative": opening,
        }

    # General tailored high-stakes fantasy/custom world
    clean_setting = world_setting.strip() if world_setting.strip() else "A realm scarred by ancient calamity"
    backstory_snippet = f" Having endured: '{backstory}'," if backstory else ""
    conflict_core = f"An escalating crisis in {clean_setting} threatens total catastrophe."
    if backstory:
        conflict_core = f"{conflict_core} Deeply intertwined with {char_name}'s history ({backstory}), the struggle has become personal."

    return {
        "campaign_name": f"Chronicles of {clean_setting[:30].title()}",
        "narrative_tone": f"Immersive {effective_genre}. Atmospheric, visceral, and uncompromising. High stakes with real danger, shaped by character history.",
        "starting_location_name": "The Ruined Bastion Threshold",
        "starting_location_description": f"In {clean_setting}, cold wind howls across cracked masonry. The air is charged with tension, carrying the scent of smoke, ancient stone, and brewing conflict.",
        "main_storyline": {
            "central_conflict": conflict_core,
            "antagonist": "Lord Malrik the Oathbreaker, rallying ruthless warbands to seize the regional stronghold.",
            "active_threat": "An advance vanguard closing in on your position with orders to leave no witnesses.",
            "act_1": f"Survive the initial encirclement and secure the breach.{' Take the first step toward settling your past.' if backstory else ''}",
            "act_2": "Infiltrate the occupied outer fortifications and sabotage the siege engines.",
            "act_3": "Confront Malrik atop the breached citadel ramparts before the stronghold falls."
        },
        "opening_narrative": (
            f"The wind cuts through the ruined stone ramparts, carrying the sharp scent of pitch and distant fire.{backstory_snippet} "
            f"as {char_name}, a level {char_lvl} {char_cls}, you stand in the shadow of the threshold. "
            f"Thirty yards ahead, three scout sentries clad in blackened iron armor fan out across the rubble, their torches casting long, flickering shadows. "
            f"One of them spots movement and whistles sharply, drawing a notched broadsword.\n\n"
            f"There is no retreat behind you. What do you do?"
        )
    }


async def generate_campaign_world_and_storyline(
    world_setting: str,
    genre: Optional[str] = None,
    character_info: Optional[Dict[str, Any]] = None,
    chosen_model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Dynamically generates campaign title, tone, starting location, 3-act storyline,
    and opening narrative based on user's world setting, optional genre, and character backstory.
    Attempts Ollama LLM generation first with strict JSON structure; falls back to
    curated high-stakes archetypes if offline or malformed.
    """
    character_info = character_info or {}
    model = chosen_model or ollama_client.active_model
    char_name = character_info.get("name", "The Adventurer")
    char_race = character_info.get("race", "Human")
    char_cls = character_info.get("character_class", "Fighter")
    char_lvl = character_info.get("level", 1)
    backstory = character_info.get("backstory", "").strip()

    genre_instruction = (
        f"GENRE SPECIFIED: {genre}"
        if genre and genre.strip()
        else "GENRE / TONE: The user left the genre optional. You MUST analyze the world setting and character backstory to deduce and craft the most authentic, grounded genre and narrative tone (e.g. Grimdark, Dark Supernatural Action, High Fantasy, Cyberpunk Noir, Gothic Dread)."
    )

    system_prompt = (
        "You are an expert tabletop Dungeon Master creating an authentic, immersive campaign. "
        "Your task is to generate the campaign title, narrative tone, starting location, overarching 3-act storyline, "
        "and an evocative opening dilemma for the player.\n\n"
        "CORE RULES:\n"
        "1. SETTING ACCURACY: Deeply incorporate the specific lore, factions, magic/technology, and flavor of the player's world setting.\n"
        "2. BACKSTORY & PERSONAL STAKES INTEGRATION: Combine the world setting AND the character's backstory. The central conflict, primary antagonist, and active threat MUST directly connect to the character's personal history, revenge, debts, or vows from their backstory.\n"
        "3. DEDUCE TONE IF OPTIONAL: If no genre is specified, infer the ideal atmosphere from the setting and character history.\n"
        "4. ZERO PLOT ARMOR: Present real, unyielding danger. No convenient rescues or silly enemy mistakes.\n"
        "5. NON-CLICHÉ NAMES: Absolutely NO Kaelen, Vess, Valerius, Shadowbane, Malakor. Use culturally textured names matching the world setting.\n"
        "6. STRICT JSON OUTPUT ONLY: Output nothing outside the JSON object.\n\n"
        "Required JSON schema:\n"
        "{\n"
        '  "campaign_name": "Evocative Title",\n'
        '  "narrative_tone": "Specific tone and sensory guidance for DM narration",\n'
        '  "starting_location_name": "Specific starting location name",\n'
        '  "starting_location_description": "2-3 rich sensory sentences describing environment, sounds, lighting, smells",\n'
        '  "main_storyline": {\n'
        '    "central_conflict": "Core conflict driving the campaign, weaving the world crisis with the character backstory",\n'
        '    "antagonist": "Name and motives of primary antagonist (connected to the character or setting crisis)",\n'
        '    "active_threat": "Immediate danger escalating right now",\n'
        '    "act_1": "Act 1 objective",\n'
        '    "act_2": "Act 2 escalation",\n'
        '    "act_3": "Act 3 climax"\n'
        "  },\n"
        '  "opening_narrative": "Visceral, second-person opening scene placing the player immediately in front of the active threat, referencing their motivation/backstory. Conclude with \'What do you do?\'"\n'
        "}"
    )

    user_prompt = (
        f"WORLD SETTING: {world_setting}\n"
        f"{genre_instruction}\n"
        f"PLAYER CHARACTER: {char_name}, Level {char_lvl} {char_race} {char_cls}\n"
        f"CHARACTER BACKSTORY: {backstory if backstory else 'A determined wanderer seeking their destiny'}\n\n"
        f"Generate the full backstory-integrated campaign storyline, starting location, and opening scene in valid JSON now."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    try:
        generator_task = asyncio.create_task(_call_ollama_json(messages, model))
        result = await asyncio.wait_for(generator_task, timeout=10.0)
        if result and isinstance(result, dict) and "starting_location_name" in result and "main_storyline" in result:
            return result
    except Exception:
        pass

    return generate_fallback_campaign(world_setting, genre, character_info)


async def _call_ollama_json(messages: list, model: str) -> Optional[Dict[str, Any]]:
    """Helper to stream/collect LLM response and parse JSON."""
    collected = ""
    async for token in ollama_client.stream_chat(messages, model=model, format="json"):
        collected += token

    json_match = re.search(r"\{[\s\S]*\}", collected)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except Exception:
            return None
    return None
