import React, { useState, useEffect, useMemo } from 'react';
import {
  Sparkles,
  Compass,
  Shield,
  User,
  X,
  Dices,
  Wand2,
  BookOpen,
  AlertCircle,
  Loader2,
  Search,
  Check,
  Trash2,
  RotateCcw,
  Filter,
} from 'lucide-react';
import { SpellCatalogItem, SpellsCatalog } from '../types/game';

const CLASS_DEFAULT_SPELLS: Record<string, string[]> = {
  Wizard: ['Fire Bolt', 'Mage Hand', 'Magic Missile', 'Shield'],
  Sorcerer: ['Fire Bolt', 'Ray of Frost', 'Burning Hands', 'Shield'],
  Cleric: ['Sacred Flame', 'Guidance', 'Cure Wounds', 'Bless'],
  Druid: ['Thorn Whip', 'Guidance', 'Healing Word', 'Entangle'],
  Bard: ['Vicious Mockery', 'Mage Hand', 'Dissonant Whispers', 'Healing Word'],
  Warlock: ['Eldritch Blast', 'Minor Illusion', 'Hex', 'Armor of Agathys'],
  Paladin: ['Bless', 'Cure Wounds'],
  Ranger: ["Hunter's Mark", 'Cure Wounds'],
  Fighter: [],
  Barbarian: [],
  Rogue: [],
  Monk: [],
};

const GROUNDED_NAMES_GENERAL = [
  'Dunstan Clayhanger',
  'Wymarc of the Low Fen',
  'Hildegard of Dunwich',
  'Morcar Ashford',
  'Cynethryth Coldwater',
  'Branoc the Red',
  'Radim of the High Moor',
  'Godric Fletcher',
  'Euphemia Skagastol',
  'Torstein Ironbark',
  'Osric Oakhaven',
  'Sigurd Wulfgard',
  'Ysolde of the Barrow',
  'Cadoc of Gwent',
  'Gwyneira of the High Crag',
];

const GROUNDED_NAMES_ANIME = [
  'Nobuhiro Sato',
  'Kuroda Ren',
  'Megumi Inuzuka',
  'Kazuki Hayashi',
  'Satoru Minamoto',
  'Ryohei Takahashi',
  'Aoi Sakamoto',
  'Shinya Fujimoto',
  'Haruto Shindo',
  'Kenshiro Moriyama',
];

const GROUNDED_NAMES_CYBER = [
  'Jax Mercer',
  'Silas Vance',
  'Nova Chen',
  'Yuri Kovacs',
  'Vane Sterling',
  'Dex Castillo',
  'Radek Holt',
  'Mara Cross',
];

const QUICK_SETTINGS = [
  {
    label: 'Forgotten Realms Classic 5e',
    genre: 'High Fantasy & Heroic Epic',
    setting:
      'The perilous Sword Coast filled with ancient Netherese ruins, encroaching goblinoid warbands, and secretive factions like the Harpers and the Zhentarim vying for power.',
    defaultName: 'Dunstan Clayhanger',
    defaultBackstory:
      'Seeking vengeance against the ruthless Zhentarim mercenaries who raided my family homestead on the Trade Way.',
  },
  {
    label: 'Jujutsu Kaisen (Tokyo Curses)',
    genre: 'Dark Supernatural Action',
    setting:
      'Modern Tokyo where negative human emotions manifest as dangerous Cursed Spirits. Jujutsu High sorcerers use cursed energy, shikigami, and innate techniques to exorcise lethal curses behind semi-permeable veils.',
    defaultName: 'Kazuki Hayashi',
    defaultBackstory:
      'Seeking vengeance against the renegade curse user who annihilated my ancestral shrine and slaughtered my clan.',
  },
  {
    label: 'Dark Souls / Elden Ring',
    genre: 'Grimdark & Visceral',
    setting:
      'A desolate, ash-covered realm where ancient lords have decayed into hollow madness, dying bonfires gutter in the wind, and survival is unforgiving and earned with blood.',
    defaultName: 'Torstein Ironbark',
    defaultBackstory:
      'An undying ash wanderer seeking the scattered embers of a fallen lord to rekindle the dying hearth of my order.',
  },
  {
    label: 'Cyber-Arcane Neo-Tokyo',
    genre: 'Cyberpunk Arcane Noir',
    setting:
      'Neo-Tokyo 2099 where megacorporations rule through cybernetic chrome augmentations, black-market neural implants, and illicit blood sorcery practiced in the neon rain of the lower wards.',
    defaultName: 'Jax Mercer',
    defaultBackstory:
      'Ex-corporate security operative hunted by black-ops kill teams after stealing an experimental encrypted cyber-relic.',
  },
  {
    label: 'Gothic Barovia & Vampires',
    genre: 'Gothic Horror & Dread',
    setting:
      'A mist-shrouded domain trapped under perpetual gloom and thunderheads, stalked by werewolf packs and ruled from a high spire by an ancient, brooding vampire sovereign.',
    defaultName: 'Hildegard of Dunwich',
    defaultBackstory:
      'Monster hunter drawn through the choking Svalich mists after my mentor vanished while investigating the vampire lord of the high spire.',
  },
];

const STANDARD_ARRAYS: Record<string, { str: number; dex: number; con: number; int: number; wis: number; cha: number }> = {
  Wizard: { str: 8, dex: 14, con: 13, int: 15, wis: 12, cha: 10 },
  Sorcerer: { str: 8, dex: 14, con: 13, int: 10, wis: 12, cha: 15 },
  Warlock: { str: 8, dex: 14, con: 13, int: 12, wis: 10, cha: 15 },
  Fighter: { str: 15, dex: 13, con: 14, int: 8, wis: 12, cha: 10 },
  Barbarian: { str: 15, dex: 14, con: 14, int: 8, wis: 12, cha: 8 },
  Paladin: { str: 15, dex: 10, con: 13, int: 8, wis: 12, cha: 14 },
  Rogue: { str: 8, dex: 15, con: 13, int: 12, wis: 14, cha: 10 },
  Ranger: { str: 10, dex: 15, con: 13, int: 8, wis: 14, cha: 12 },
  Cleric: { str: 13, dex: 10, con: 14, int: 8, wis: 15, cha: 12 },
  Druid: { str: 8, dex: 13, con: 14, int: 12, wis: 15, cha: 10 },
  Bard: { str: 8, dex: 14, con: 13, int: 10, wis: 12, cha: 15 },
  Monk: { str: 10, dex: 15, con: 13, int: 8, wis: 14, cha: 12 },
};

const RACES_5E = [
  { name: 'Human', traits: 'Versatile Adaptation, Resourceful' },
  { name: 'Elf', traits: 'Darkvision 60ft, Keen Senses (Perception), Fey Ancestry (adv vs charm, immune to sleep), Trance' },
  { name: 'Dwarf', traits: 'Darkvision 60ft, Dwarven Resilience (adv vs poison, poison resistance), Stonecunning' },
  { name: 'Halfling', traits: 'Lucky (reroll nat 1s), Brave (adv vs fear), Halfling Nimbleness' },
  { name: 'Dragonborn', traits: 'Elemental Damage Resistance, Draconic Breath Weapon' },
  { name: 'Gnome', traits: 'Darkvision 60ft, Gnome Cunning (adv on INT/WIS/CHA saves vs magic)' },
  { name: 'Half-Elf', traits: 'Darkvision 60ft, Fey Ancestry (adv vs charm, immune to sleep), Skill Versatility' },
  { name: 'Half-Orc', traits: 'Darkvision 60ft, Relentless Endurance (drop to 1 HP once), Savage Attacks (+1 crit die), Menacing' },
  { name: 'Tiefling', traits: 'Darkvision 60ft, Hellish Resistance (fire resistance), Infernal Legacy' },
];

const BACKSTORY_SEEDS = [
  'Seeking vengeance against the renegade who slaughtered my sworn clan',
  'Bearer of a sealed forbidden relic that relentless hunter-killers are tracking',
  'Exiled knight bound by an ancient oath of redemption',
  'Disgraced soldier framed for treason by corrupt commanding officers',
  'Occult investigator pursuing an apocalyptic curse omen across the border',
];

interface CampaignSetupModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCampaignCreated: (data: any) => void;
}

export const CampaignSetupModal: React.FC<CampaignSetupModalProps> = ({
  isOpen,
  onClose,
  onCampaignCreated,
}) => {
  const [tab, setTab] = useState<'world' | 'character' | 'spells'>('world');
  const [customSpells, setCustomSpells] = useState<string[]>([]);
  const [catalogSpells, setCatalogSpells] = useState<SpellCatalogItem[]>([]);
  const [spellSearch, setSpellSearch] = useState<string>('');
  const [spellLevelFilter, setSpellLevelFilter] = useState<number | 'all'>('all');
  const [onlyClassSpells, setOnlyClassSpells] = useState<boolean>(true);

  // Fetch spells catalog when modal is open
  useEffect(() => {
    if (!isOpen) return;
    const fetchSpells = async () => {
      try {
        const res = await fetch('/api/compendium/spells');
        if (res.ok) {
          const data: SpellsCatalog = await res.json();
          const all: SpellCatalogItem[] = [];
          Object.values(data).forEach((list) => {
            if (Array.isArray(list)) all.push(...list);
          });
          all.sort((a, b) => a.level - b.level || a.name.localeCompare(b.name));
          setCatalogSpells(all);
        }
      } catch (e) {}
    };
    fetchSpells();
  }, [isOpen]);

  // World Setting Inputs
  const [worldSetting, setWorldSetting] = useState(QUICK_SETTINGS[0].setting);
  const [genre, setGenre] = useState('');
  const [campaignTitle, setCampaignTitle] = useState('');

  // Character Inputs
  const [charName, setCharName] = useState(QUICK_SETTINGS[0].defaultName);
  const [charRace, setCharRace] = useState('Human');
  const [charClass, setCharClass] = useState('Fighter');
  const [backstory, setBackstory] = useState(QUICK_SETTINGS[0].defaultBackstory);
  const [level, setLevel] = useState<number | string>(3);
  const [background, setBackground] = useState('Soldier');
  const [alignment, setAlignment] = useState('Neutral Good');

  // Abilities (Standard 5e bounds: 3-18 at lv 1-3, 3-20 at lv 4+)
  const [str, setStr] = useState<number | string>(15);
  const [dex, setDex] = useState<number | string>(13);
  const [con, setCon] = useState<number | string>(14);
  const [intScore, setIntScore] = useState<number | string>(8);
  const [wis, setWis] = useState<number | string>(12);
  const [cha, setCha] = useState<number | string>(10);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');

  const filteredCatalogSpells = useMemo(() => {
    return catalogSpells.filter((sp) => {
      if (spellSearch && !sp.name.toLowerCase().includes(spellSearch.toLowerCase())) {
        return false;
      }
      if (spellLevelFilter !== 'all' && sp.level !== spellLevelFilter) {
        return false;
      }
      if (onlyClassSpells) {
        const cls = charClass.toLowerCase();
        const allowed = (sp.classes || []).map((c) => c.toLowerCase());
        const hasDirect = allowed.includes(cls);
        const hasWizardFallback =
          (cls === 'rogue' || cls === 'fighter') && allowed.includes('wizard');
        if (!hasDirect && !hasWizardFallback) {
          return false;
        }
      }
      return true;
    });
  }, [catalogSpells, spellSearch, spellLevelFilter, onlyClassSpells, charClass]);

  if (!isOpen) return null;

  const numericLevel = typeof level === 'number' ? level : parseInt(String(level), 10) || 1;
  const maxAllowedStat = numericLevel >= 4 ? 20 : 18;

  const clampStatWithMax = (val: number | string, maxLimit: number) => {
    const num = typeof val === 'number' ? val : parseInt(String(val), 10);
    if (isNaN(num)) return 10;
    return Math.max(3, Math.min(maxLimit, num));
  };

  const clampStat = (val: number | string) => {
    return clampStatWithMax(val, maxAllowedStat);
  };

  const getModifier = (score: number | string) => {
    const num = typeof score === 'number' ? score : parseInt(String(score), 10);
    if (isNaN(num)) return '+0';
    const mod = Math.floor((num - 10) / 2);
    return mod >= 0 ? `+${mod}` : `${mod}`;
  };

  const handleStatChange = (
    setter: React.Dispatch<React.SetStateAction<number | string>>,
    rawVal: string
  ) => {
    if (rawVal === '') {
      setter('');
      return;
    }
    const clean = rawVal.replace(/[^0-9]/g, '');
    if (clean.length <= 2) {
      setter(clean);
    }
  };

  const handleStatBlur = (
    getter: number | string,
    setter: React.Dispatch<React.SetStateAction<number | string>>
  ) => {
    if (getter === '') {
      setter(10);
      return;
    }
    const parsed = parseInt(String(getter), 10);
    if (isNaN(parsed)) {
      setter(10);
    } else {
      setter(clampStat(parsed));
    }
  };

  const handleStepStat = (
    getter: number | string,
    setter: React.Dispatch<React.SetStateAction<number | string>>,
    delta: number
  ) => {
    const current = typeof getter === 'number' ? getter : parseInt(String(getter), 10);
    const base = isNaN(current) ? 10 : current;
    const next = clampStat(base + delta);
    setter(next);
  };

  const handleLevelChange = (rawVal: string) => {
    if (rawVal === '') {
      setLevel('');
      return;
    }
    const clean = rawVal.replace(/[^0-9]/g, '');
    if (clean.length <= 2) {
      setLevel(clean);
    }
  };

  const handleLevelBlur = () => {
    if (level === '') {
      setLevel(1);
      return;
    }
    const parsed = parseInt(String(level), 10);
    const clamped = isNaN(parsed) || parsed < 1 ? 1 : parsed > 20 ? 20 : parsed;
    setLevel(clamped);
    if (clamped < 4) {
      setStr((prev) => clampStatWithMax(prev, 18));
      setDex((prev) => clampStatWithMax(prev, 18));
      setCon((prev) => clampStatWithMax(prev, 18));
      setIntScore((prev) => clampStatWithMax(prev, 18));
      setWis((prev) => clampStatWithMax(prev, 18));
      setCha((prev) => clampStatWithMax(prev, 18));
    }
  };

  const handleStepLevel = (delta: number) => {
    const current = typeof level === 'number' ? level : parseInt(String(level), 10);
    const base = isNaN(current) ? 1 : current;
    const next = Math.max(1, Math.min(20, base + delta));
    setLevel(next);
    if (next < 4) {
      setStr((prev) => clampStatWithMax(prev, 18));
      setDex((prev) => clampStatWithMax(prev, 18));
      setCon((prev) => clampStatWithMax(prev, 18));
      setIntScore((prev) => clampStatWithMax(prev, 18));
      setWis((prev) => clampStatWithMax(prev, 18));
      setCha((prev) => clampStatWithMax(prev, 18));
    }
  };

  const handleRandomizeName = () => {
    const lowerSetting = worldSetting.toLowerCase();
    let pool = GROUNDED_NAMES_GENERAL;
    if (lowerSetting.includes('jujutsu') || lowerSetting.includes('anime') || lowerSetting.includes('tokyo') || lowerSetting.includes('curse')) {
      pool = GROUNDED_NAMES_ANIME;
    } else if (lowerSetting.includes('cyber') || lowerSetting.includes('neon') || lowerSetting.includes('corp')) {
      pool = GROUNDED_NAMES_CYBER;
    }
    const chosen = pool[Math.floor(Math.random() * pool.length)];
    setCharName(chosen);
  };

  const handleApplyQuickSetting = (item: (typeof QUICK_SETTINGS)[0]) => {
    setWorldSetting(item.setting);
    setGenre(item.genre);
    if (item.defaultName) {
      setCharName(item.defaultName);
    }
    if (item.defaultBackstory) {
      setBackstory(item.defaultBackstory);
    }
    if (!campaignTitle) {
      setCampaignTitle('');
    }
  };

  const handleApplyStandardArray = (clsName: string) => {
    const array = STANDARD_ARRAYS[clsName] || STANDARD_ARRAYS['Fighter'];
    setStr(clampStat(array.str));
    setDex(clampStat(array.dex));
    setCon(clampStat(array.con));
    setIntScore(clampStat(array.int));
    setWis(clampStat(array.wis));
    setCha(clampStat(array.cha));
  };

  const handleClassChange = (newClass: string) => {
    setCharClass(newClass);
    handleApplyStandardArray(newClass);
    if (CLASS_DEFAULT_SPELLS[newClass]) {
      setCustomSpells([...CLASS_DEFAULT_SPELLS[newClass]]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setStatusMessage('The AI Dungeon Master is generating your campaign storyline, locations, and opening crisis...');

    try {
      const payload = {
        world_setting: worldSetting,
        genre: genre.trim() ? genre.trim() : undefined,
        campaign_name: campaignTitle.trim() ? campaignTitle.trim() : undefined,
        character_name: charName,
        character_race: charRace,
        character_class: charClass,
        backstory: backstory.trim() ? backstory.trim() : undefined,
        level: numericLevel,
        background: background,
        alignment: alignment,
        strength: clampStat(str),
        dexterity: clampStat(dex),
        constitution: clampStat(con),
        intelligence: clampStat(intScore),
        wisdom: clampStat(wis),
        charisma: clampStat(cha),
        custom_spells: customSpells.length > 0 ? customSpells : undefined,
      };

      const res = await fetch('/api/game/create-campaign', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const data = await res.json();
        onCampaignCreated(data);
        onClose();
      } else {
        const errData = await res.json().catch(() => ({}));
        alert(`Failed to create campaign: ${errData.detail || 'Server error'}`);
      }
    } catch (err) {
      console.error('Failed to create campaign:', err);
      alert('Network error connecting to campaign engine.');
    } finally {
      setIsSubmitting(false);
      setStatusMessage('');
    }
  };

  return (
    <div className="modal-overlay" style={{ zIndex: 200 }}>
      <div className="setup-modal-container">
        {/* Loading Overlay */}
        {isSubmitting && (
          <div
            style={{
              position: 'absolute',
              inset: 0,
              backgroundColor: 'rgba(18, 21, 29, 0.95)',
              zIndex: 300,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '2rem',
              textAlign: 'center',
            }}
          >
            <Loader2 size={44} className="spin" style={{ color: 'var(--accent-gold)', marginBottom: '1.25rem' }} />
            <h3 style={{ fontFamily: 'var(--font-display)', color: 'var(--accent-gold)', marginBottom: '0.5rem', fontSize: '1.25rem' }}>
              Forging Campaign Narrative
            </h3>
            <p style={{ color: 'var(--text-secondary)', maxWidth: '480px', lineHeight: 1.6, fontSize: '0.9rem' }}>
              {statusMessage}
            </p>
          </div>
        )}

        {/* Header */}
        <div
          style={{
            padding: '1.25rem 1.5rem',
            borderBottom: '1px solid var(--border-subtle)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            backgroundColor: 'var(--bg-card)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <Compass size={22} style={{ color: 'var(--accent-gold)' }} />
            <div>
              <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.2rem', color: 'var(--text-primary)' }}>
                New Campaign Setup
              </h2>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Configure your world setting and 5e character sheet. The AI Dungeon Master will direct the rest.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            disabled={isSubmitting}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              padding: '0.4rem',
              display: 'flex',
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Step Navigation Tabs */}
        <div
          style={{
            display: 'flex',
            borderBottom: '1px solid var(--border-subtle)',
            backgroundColor: 'var(--bg-surface)',
          }}
        >
          <button
            type="button"
            onClick={() => setTab('world')}
            style={{
              flex: 1,
              padding: '0.75rem',
              background: tab === 'world' ? 'var(--bg-card)' : 'transparent',
              border: 'none',
              borderBottom: tab === 'world' ? '2px solid var(--accent-gold)' : '2px solid transparent',
              color: tab === 'world' ? 'var(--accent-gold)' : 'var(--text-secondary)',
              fontWeight: tab === 'world' ? 600 : 400,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.5rem',
              fontSize: '0.875rem',
            }}
          >
            <BookOpen size={16} />
            1. World Setting &amp; Genre
          </button>
          <button
            type="button"
            onClick={() => setTab('character')}
            style={{
              flex: 1,
              padding: '0.75rem',
              background: tab === 'character' ? 'var(--bg-card)' : 'transparent',
              border: 'none',
              borderBottom: tab === 'character' ? '2px solid var(--accent-gold)' : '2px solid transparent',
              color: tab === 'character' ? 'var(--accent-gold)' : 'var(--text-secondary)',
              fontWeight: tab === 'character' ? 600 : 400,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.5rem',
              fontSize: '0.875rem',
            }}
          >
            <User size={16} />
            2. Character Sheet (D&amp;D 5e)
          </button>
          <button
            type="button"
            onClick={() => setTab('spells')}
            style={{
              flex: 1,
              padding: '0.75rem',
              background: tab === 'spells' ? 'var(--bg-card)' : 'transparent',
              border: 'none',
              borderBottom: tab === 'spells' ? '2px solid var(--accent-gold)' : '2px solid transparent',
              color: tab === 'spells' ? 'var(--accent-gold)' : 'var(--text-secondary)',
              fontWeight: tab === 'spells' ? 600 : 400,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.5rem',
              fontSize: '0.875rem',
            }}
          >
            <Sparkles size={16} />
            3. Spells (Optional)
            {customSpells.length > 0 && (
              <span
                style={{
                  fontSize: '10px',
                  backgroundColor: 'var(--accent-gold-dim)',
                  color: 'var(--accent-gold)',
                  padding: '1px 6px',
                  borderRadius: '10px',
                  fontWeight: 700,
                }}
              >
                {customSpells.length}
              </span>
            )}
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', flex: 1, overflow: 'hidden' }}>
          <div style={{ padding: '1.5rem', overflowY: 'auto', flex: 1 }}>
            {/* TAB 1: World & Setting */}
            {tab === 'world' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                {/* AI DM Notice */}
                <div
                  style={{
                    backgroundColor: 'rgba(200, 155, 60, 0.08)',
                    border: '1px solid var(--border-gold)',
                    borderRadius: 'var(--radius-md)',
                    padding: '0.85rem 1rem',
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '0.75rem',
                  }}
                >
                  <Sparkles size={18} style={{ color: 'var(--accent-gold)', marginTop: '2px', flexShrink: 0 }} />
                  <div style={{ fontSize: '0.825rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                    <strong style={{ color: 'var(--accent-gold)' }}>AI Tabletop Master Directs the Story: </strong>
                    You only need to define your world concept and character. The AI DM dynamically generates the starting location, environmental atmosphere, primary villain, and overarching 3-act storyline.
                  </div>
                </div>

                {/* Quick Setting Inspiration Chips */}
                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Quick World Presets:
                  </label>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                    {QUICK_SETTINGS.map((item) => (
                      <button
                        key={item.label}
                        type="button"
                        onClick={() => handleApplyQuickSetting(item)}
                        style={{
                          backgroundColor: worldSetting === item.setting ? 'var(--accent-gold-dim)' : 'var(--bg-card)',
                          color: worldSetting === item.setting ? 'var(--accent-gold)' : 'var(--text-secondary)',
                          border: `1px solid ${worldSetting === item.setting ? 'var(--accent-gold)' : 'var(--border-subtle)'}`,
                          borderRadius: 'var(--radius-sm)',
                          padding: '0.35rem 0.75rem',
                          fontSize: '0.8rem',
                          cursor: 'pointer',
                          transition: 'all 0.15s ease',
                        }}
                      >
                        {item.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* World Setting Description */}
                <div>
                  <label style={{ display: 'block', fontSize: '0.875rem', color: 'var(--text-primary)', marginBottom: '0.4rem', fontWeight: 500 }}>
                    World Setting &amp; Lore Lore <span style={{ color: 'var(--accent-gold)' }}>*</span>
                  </label>
                  <textarea
                    rows={4}
                    value={worldSetting}
                    onChange={(e) => setWorldSetting(e.target.value)}
                    placeholder="e.g. Jujutsu Kaisen modern Tokyo where cursed energy manifests into monstrous spirits, or Dark Souls decaying world of ash..."
                    required
                    style={{
                      width: '100%',
                      backgroundColor: 'var(--bg-card)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 'var(--radius-md)',
                      color: 'var(--text-primary)',
                      padding: '0.75rem',
                      fontFamily: 'var(--font-body)',
                      fontSize: '0.875rem',
                      lineHeight: 1.5,
                      resize: 'vertical',
                    }}
                  />
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    Describe your world lore, factions, magic/technology, and power systems. The DM will craft the narrative to match.
                  </span>
                </div>

                {/* Genre & Narrative Atmosphere */}
                <div className="setup-grid-2col">
                  <div>
                    <label style={{ display: 'block', fontSize: '0.875rem', color: 'var(--text-primary)', marginBottom: '0.4rem', fontWeight: 500 }}>
                      Genre / Tone Style <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>(Optional)</span>
                    </label>
                    <select
                      value={genre}
                      onChange={(e) => setGenre(e.target.value)}
                      style={{
                        width: '100%',
                        backgroundColor: 'var(--bg-card)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: 'var(--radius-md)',
                        color: 'var(--text-primary)',
                        padding: '0.6rem 0.75rem',
                        fontSize: '0.875rem',
                      }}
                    >
                      <option value="">Auto-Determine (AI crafts tone from setting &amp; backstory)</option>
                      <option value="Dark Supernatural Action">Dark Supernatural Action (Anime / Curses)</option>
                      <option value="Grimdark &amp; Visceral">Grimdark &amp; Visceral (Souls / Ashes)</option>
                      <option value="Gothic Horror &amp; Dread">Gothic Horror &amp; Dread (Vampires / Fog)</option>
                      <option value="Cyberpunk Arcane Noir">Cyberpunk Arcane Noir (Chrome &amp; Neon)</option>
                      <option value="High Fantasy &amp; Heroic Epic">High Fantasy &amp; Heroic Epic</option>
                      <option value="Eldritch Cosmic Mystery">Eldritch Cosmic Mystery</option>
                    </select>
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '0.875rem', color: 'var(--text-primary)', marginBottom: '0.4rem', fontWeight: 500 }}>
                      Campaign Title <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>(Optional)</span>
                    </label>
                    <input
                      type="text"
                      value={campaignTitle}
                      onChange={(e) => setCampaignTitle(e.target.value)}
                      placeholder="Leave blank for AI DM to generate"
                      style={{
                        width: '100%',
                        backgroundColor: 'var(--bg-card)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: 'var(--radius-md)',
                        color: 'var(--text-primary)',
                        padding: '0.6rem 0.75rem',
                        fontSize: '0.875rem',
                      }}
                    />
                  </div>
                </div>
              </div>
            )}

            {/* TAB 2: Character Sheet */}
            {tab === 'character' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                {/* Name, Race, Class Row */}
                <div className="setup-grid-3col">
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                      <label style={{ fontSize: '0.875rem', color: 'var(--text-primary)', fontWeight: 500 }}>
                        Character Name <span style={{ color: 'var(--accent-gold)' }}>*</span>
                      </label>
                      <button
                        type="button"
                        onClick={handleRandomizeName}
                        style={{
                          background: 'none',
                          border: 'none',
                          color: 'var(--accent-gold)',
                          fontSize: '0.75rem',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.25rem',
                        }}
                      >
                        <Dices size={13} /> Randomize
                      </button>
                    </div>
                    <input
                      type="text"
                      value={charName}
                      onChange={(e) => setCharName(e.target.value)}
                      required
                      style={{
                        width: '100%',
                        backgroundColor: 'var(--bg-card)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: 'var(--radius-md)',
                        color: 'var(--text-primary)',
                        padding: '0.6rem 0.75rem',
                        fontSize: '0.875rem',
                      }}
                    />
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '0.875rem', color: 'var(--text-primary)', marginBottom: '0.4rem', fontWeight: 500 }}>
                      Race (D&amp;D 5e)
                    </label>
                    <select
                      value={charRace}
                      onChange={(e) => setCharRace(e.target.value)}
                      style={{
                        width: '100%',
                        backgroundColor: 'var(--bg-card)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: 'var(--radius-md)',
                        color: 'var(--text-primary)',
                        padding: '0.6rem 0.75rem',
                        fontSize: '0.875rem',
                      }}
                    >
                      {RACES_5E.map((r) => (
                        <option key={r.name} value={r.name}>
                          {r.name}
                        </option>
                      ))}
                    </select>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.25rem', lineHeight: 1.3 }}>
                      <span style={{ color: 'var(--accent-gold)', fontWeight: 600 }}>Traits: </span>
                      {RACES_5E.find((r) => r.name === charRace)?.traits}
                    </div>
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '0.875rem', color: 'var(--text-primary)', marginBottom: '0.4rem', fontWeight: 500 }}>
                      Class
                    </label>
                    <select
                      value={charClass}
                      onChange={(e) => handleClassChange(e.target.value)}
                      style={{
                        width: '100%',
                        backgroundColor: 'var(--bg-card)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: 'var(--radius-md)',
                        color: 'var(--text-primary)',
                        padding: '0.6rem 0.75rem',
                        fontSize: '0.875rem',
                      }}
                    >
                      <option value="Fighter">Fighter</option>
                      <option value="Wizard">Wizard</option>
                      <option value="Rogue">Rogue</option>
                      <option value="Cleric">Cleric</option>
                      <option value="Barbarian">Barbarian</option>
                      <option value="Paladin">Paladin</option>
                      <option value="Sorcerer">Sorcerer</option>
                      <option value="Warlock">Warlock</option>
                      <option value="Ranger">Ranger</option>
                      <option value="Druid">Druid</option>
                      <option value="Monk">Monk</option>
                      <option value="Bard">Bard</option>
                    </select>
                  </div>
                </div>

                {/* Level, Background, Alignment */}
                <div className="setup-grid-3col">
                  <div>
                    <label style={{ display: 'block', fontSize: '0.875rem', color: 'var(--text-primary)', marginBottom: '0.4rem', fontWeight: 500 }}>
                      Level (1-20)
                    </label>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <button
                        type="button"
                        onClick={() => handleStepLevel(-1)}
                        disabled={numericLevel <= 1}
                        style={{
                          width: '34px',
                          height: '36px',
                          backgroundColor: 'var(--bg-card)',
                          border: '1px solid var(--border-subtle)',
                          borderRadius: 'var(--radius-sm)',
                          color: numericLevel <= 1 ? 'var(--text-muted)' : 'var(--text-primary)',
                          cursor: numericLevel <= 1 ? 'not-allowed' : 'pointer',
                          fontSize: '16px',
                          fontWeight: 'bold',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          flexShrink: 0,
                          transition: 'all 0.15s ease',
                        }}
                        aria-label="Decrease level"
                      >
                        -
                      </button>
                      <input
                        type="text"
                        inputMode="numeric"
                        pattern="[0-9]*"
                        maxLength={2}
                        value={level}
                        onChange={(e) => handleLevelChange(e.target.value)}
                        onBlur={handleLevelBlur}
                        style={{
                          flex: 1,
                          backgroundColor: 'var(--bg-card)',
                          border: '1px solid var(--border-subtle)',
                          borderRadius: 'var(--radius-sm)',
                          color: 'var(--text-primary)',
                          padding: '0.6rem 0.5rem',
                          fontSize: '0.95rem',
                          fontWeight: 700,
                          textAlign: 'center',
                        }}
                      />
                      <button
                        type="button"
                        onClick={() => handleStepLevel(1)}
                        disabled={numericLevel >= 20}
                        style={{
                          width: '34px',
                          height: '36px',
                          backgroundColor: 'var(--bg-card)',
                          border: '1px solid var(--border-subtle)',
                          borderRadius: 'var(--radius-sm)',
                          color: numericLevel >= 20 ? 'var(--text-muted)' : 'var(--text-primary)',
                          cursor: numericLevel >= 20 ? 'not-allowed' : 'pointer',
                          fontSize: '16px',
                          fontWeight: 'bold',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          flexShrink: 0,
                          transition: 'all 0.15s ease',
                        }}
                        aria-label="Increase level"
                      >
                        +
                      </button>
                    </div>
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '0.875rem', color: 'var(--text-primary)', marginBottom: '0.4rem', fontWeight: 500 }}>
                      Background
                    </label>
                    <input
                      type="text"
                      value={background}
                      onChange={(e) => setBackground(e.target.value)}
                      placeholder="e.g. Soldier, Scholar"
                      style={{
                        width: '100%',
                        backgroundColor: 'var(--bg-card)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: 'var(--radius-md)',
                        color: 'var(--text-primary)',
                        padding: '0.6rem 0.75rem',
                        fontSize: '0.875rem',
                      }}
                    />
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '0.875rem', color: 'var(--text-primary)', marginBottom: '0.4rem', fontWeight: 500 }}>
                      Alignment
                    </label>
                    <input
                      type="text"
                      value={alignment}
                      onChange={(e) => setAlignment(e.target.value)}
                      placeholder="e.g. Neutral Good"
                      style={{
                        width: '100%',
                        backgroundColor: 'var(--bg-card)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: 'var(--radius-md)',
                        color: 'var(--text-primary)',
                        padding: '0.6rem 0.75rem',
                        fontSize: '0.875rem',
                      }}
                    />
                  </div>
                </div>

                {/* Character Backstory & Motivation */}
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                    <label style={{ fontSize: '0.875rem', color: 'var(--text-primary)', fontWeight: 500 }}>
                      Character Backstory &amp; Motivation <span style={{ color: 'var(--accent-gold)' }}>*</span>
                    </label>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      Weaves directly into the campaign storyline &amp; central villain
                    </span>
                  </div>
                  <textarea
                    rows={3}
                    value={backstory}
                    onChange={(e) => setBackstory(e.target.value)}
                    placeholder="e.g. Seeking vengeance against the rogue curse user who slaughtered my clan, carrying a sealed forbidden relic, or bound by an unbreakable blood debt..."
                    required
                    style={{
                      width: '100%',
                      backgroundColor: 'var(--bg-card)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 'var(--radius-md)',
                      color: 'var(--text-primary)',
                      padding: '0.75rem',
                      fontFamily: 'var(--font-body)',
                      fontSize: '0.875rem',
                      lineHeight: 1.5,
                      resize: 'vertical',
                    }}
                  />
                  <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '0.35rem', marginTop: '0.4rem' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginRight: '4px' }}>Ideas:</span>
                    {BACKSTORY_SEEDS.map((seed, idx) => (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => setBackstory(seed)}
                        style={{
                          background: backstory === seed ? 'var(--accent-gold-dim)' : 'var(--bg-card)',
                          color: backstory === seed ? 'var(--accent-gold)' : 'var(--text-secondary)',
                          border: `1px solid ${backstory === seed ? 'var(--accent-gold)' : 'var(--border-subtle)'}`,
                          borderRadius: '12px',
                          padding: '0.2rem 0.6rem',
                          fontSize: '0.72rem',
                          cursor: 'pointer',
                          transition: 'all 0.15s ease',
                        }}
                      >
                        {seed}
                      </button>
                    ))}
                  </div>
                </div>

                {/* 5e Stat Distribution & Level Bounds Rule */}
                <div
                  style={{
                    backgroundColor: 'var(--bg-card)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-md)',
                    padding: '1rem',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.75rem' }}>
                    <div>
                      <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                        Ability Scores (D&amp;D 5e Standard Range: 8–{maxAllowedStat})
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {numericLevel < 4
                          ? 'Starting Level 1-3 scores naturally cap at 18 with racial bonuses.'
                          : 'Level 4+ characters can reach the mortal cap of 20 via Ability Score Improvements.'}
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={() => handleApplyStandardArray(charClass)}
                      style={{
                        backgroundColor: 'var(--accent-gold-dim)',
                        border: '1px solid var(--border-gold)',
                        borderRadius: 'var(--radius-sm)',
                        color: 'var(--accent-gold)',
                        padding: '0.35rem 0.65rem',
                        fontSize: '0.75rem',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.35rem',
                      }}
                    >
                      <Wand2 size={13} /> Auto-Optimize for {charClass}
                    </button>
                  </div>

                  {/* 6 Stats Grid */}
                  <div className="setup-grid-6col">
                    {[
                      { label: 'STR', val: str, set: setStr },
                      { label: 'DEX', val: dex, set: setDex },
                      { label: 'CON', val: con, set: setCon },
                      { label: 'INT', val: intScore, set: setIntScore },
                      { label: 'WIS', val: wis, set: setWis },
                      { label: 'CHA', val: cha, set: setCha },
                    ].map((s) => {
                      const numVal = typeof s.val === 'number' ? s.val : parseInt(String(s.val), 10);
                      const isAtMin = !isNaN(numVal) && numVal <= 3;
                      const isAtMax = !isNaN(numVal) && numVal >= maxAllowedStat;

                      return (
                        <div
                          key={s.label}
                          style={{
                            backgroundColor: 'var(--bg-surface)',
                            border: '1px solid var(--border-subtle)',
                            borderRadius: 'var(--radius-sm)',
                            padding: '0.5rem 0.25rem',
                            textAlign: 'center',
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                          }}
                        >
                          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
                            {s.label}
                          </div>

                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '100%', gap: '2px' }}>
                            <button
                              type="button"
                              onClick={() => handleStepStat(s.val, s.set, -1)}
                              disabled={isAtMin}
                              style={{
                                width: '22px',
                                height: '26px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                backgroundColor: 'var(--bg-card)',
                                border: '1px solid var(--border-subtle)',
                                borderRadius: '3px',
                                color: isAtMin ? 'var(--text-muted)' : 'var(--text-primary)',
                                cursor: isAtMin ? 'not-allowed' : 'pointer',
                                fontSize: '13px',
                                fontWeight: 'bold',
                                padding: 0,
                                lineHeight: 1,
                                flexShrink: 0,
                                transition: 'all 0.15s ease',
                              }}
                              aria-label={`Decrease ${s.label}`}
                            >
                              -
                            </button>

                            <input
                              type="text"
                              inputMode="numeric"
                              pattern="[0-9]*"
                              maxLength={2}
                              value={s.val}
                              onChange={(e) => handleStatChange(s.set, e.target.value)}
                              onBlur={() => handleStatBlur(s.val, s.set)}
                              placeholder="10"
                              style={{
                                width: '36px',
                                backgroundColor: 'transparent',
                                border: 'none',
                                color: 'var(--text-primary)',
                                fontSize: '1.1rem',
                                fontWeight: 700,
                                textAlign: 'center',
                                outline: 'none',
                                padding: '0 2px',
                              }}
                            />

                            <button
                              type="button"
                              onClick={() => handleStepStat(s.val, s.set, 1)}
                              disabled={isAtMax}
                              style={{
                                width: '22px',
                                height: '26px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                backgroundColor: 'var(--bg-card)',
                                border: '1px solid var(--border-subtle)',
                                borderRadius: '3px',
                                color: isAtMax ? 'var(--text-muted)' : 'var(--text-primary)',
                                cursor: isAtMax ? 'not-allowed' : 'pointer',
                                fontSize: '13px',
                                fontWeight: 'bold',
                                padding: 0,
                                lineHeight: 1,
                                flexShrink: 0,
                                transition: 'all 0.15s ease',
                              }}
                              aria-label={`Increase ${s.label}`}
                            >
                              +
                            </button>
                          </div>

                          <div
                            style={{
                              fontSize: '0.75rem',
                              color: 'var(--accent-gold)',
                              fontWeight: 600,
                              marginTop: '0.25rem',
                            }}
                          >
                            {getModifier(s.val)}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Link to Spells Tab */}
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '0.75rem 1rem',
                    backgroundColor: 'var(--bg-card)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-md)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Sparkles size={16} style={{ color: 'var(--accent-gold)' }} />
                    <span style={{ fontSize: '0.85rem', color: 'var(--text-primary)' }}>
                      Starting Spells: <strong style={{ color: 'var(--accent-gold)' }}>{customSpells.length} configured</strong>
                    </span>
                  </div>
                  <button
                    type="button"
                    onClick={() => setTab('spells')}
                    style={{
                      backgroundColor: 'transparent',
                      border: '1px solid var(--border-gold)',
                      borderRadius: 'var(--radius-sm)',
                      color: 'var(--accent-gold)',
                      padding: '0.35rem 0.75rem',
                      fontSize: '0.75rem',
                      cursor: 'pointer',
                    }}
                  >
                    Customize Spells &rarr;
                  </button>
                </div>
              </div>
            )}

            {/* TAB 3: Spells Selection */}
            {tab === 'spells' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div
                  style={{
                    backgroundColor: 'rgba(200, 155, 60, 0.08)',
                    border: '1px solid var(--border-gold)',
                    borderRadius: 'var(--radius-md)',
                    padding: '0.75rem 1rem',
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '0.75rem',
                  }}
                >
                  <Sparkles size={18} style={{ color: 'var(--accent-gold)', marginTop: '2px', flexShrink: 0 }} />
                  <div style={{ fontSize: '0.825rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                    <strong style={{ color: 'var(--accent-gold)' }}>Starting Spells for {charClass} (Level {numericLevel}): </strong>
                    Select cantrips and prepared spells for your campaign. By default, authentic 5e spell lists for {charClass} are displayed, or unlock all 5e spells to choose homebrew abilities.
                  </div>
                </div>

                {/* Filter and Search Bar */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', gap: '0.5rem', flex: 1, minWidth: '220px' }}>
                    <div style={{ position: 'relative', flex: 1 }}>
                      <Search size={14} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                      <input
                        type="text"
                        placeholder="Search spells by name..."
                        value={spellSearch}
                        onChange={(e) => setSpellSearch(e.target.value)}
                        style={{
                          width: '100%',
                          padding: '0.45rem 0.75rem 0.45rem 2rem',
                          backgroundColor: 'var(--bg-card)',
                          border: '1px solid var(--border-subtle)',
                          borderRadius: 'var(--radius-sm)',
                          fontSize: '0.8rem',
                          color: 'var(--text-primary)',
                        }}
                      />
                    </div>
                  </div>

                  <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                    <button
                      type="button"
                      onClick={() => setOnlyClassSpells(!onlyClassSpells)}
                      style={{
                        padding: '0.4rem 0.75rem',
                        fontSize: '0.75rem',
                        borderRadius: 'var(--radius-sm)',
                        border: `1px solid ${onlyClassSpells ? 'var(--accent-gold)' : 'var(--border-subtle)'}`,
                        backgroundColor: onlyClassSpells ? 'var(--accent-gold-dim)' : 'var(--bg-card)',
                        color: onlyClassSpells ? 'var(--accent-gold)' : 'var(--text-secondary)',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.35rem',
                      }}
                    >
                      <Filter size={12} />
                      {onlyClassSpells ? `${charClass} List Only` : 'All 5e Spells (Unlocked)'}
                    </button>
                    {CLASS_DEFAULT_SPELLS[charClass] && (
                      <button
                        type="button"
                        onClick={() => setCustomSpells([...(CLASS_DEFAULT_SPELLS[charClass] || [])])}
                        style={{
                          padding: '0.4rem 0.65rem',
                          fontSize: '0.75rem',
                          borderRadius: 'var(--radius-sm)',
                          border: '1px solid var(--border-subtle)',
                          backgroundColor: 'var(--bg-card)',
                          color: 'var(--text-muted)',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.25rem',
                        }}
                        title="Reset to class standard starter spells"
                      >
                        <RotateCcw size={12} />
                        Reset
                      </button>
                    )}
                    {customSpells.length > 0 && (
                      <button
                        type="button"
                        onClick={() => setCustomSpells([])}
                        style={{
                          padding: '0.4rem 0.65rem',
                          fontSize: '0.75rem',
                          borderRadius: 'var(--radius-sm)',
                          border: '1px solid var(--border-subtle)',
                          backgroundColor: 'var(--bg-card)',
                          color: 'var(--accent-crimson)',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.25rem',
                        }}
                        title="Clear all selected spells"
                      >
                        <Trash2 size={12} />
                        Clear
                      </button>
                    )}
                  </div>
                </div>

                {/* Level Filter Pills */}
                <div style={{ display: 'flex', gap: '0.35rem', overflowX: 'auto', paddingBottom: '2px' }}>
                  {(['all', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9] as const).map((lvl) => (
                    <button
                      key={String(lvl)}
                      type="button"
                      onClick={() => setSpellLevelFilter(lvl)}
                      style={{
                        padding: '0.25rem 0.55rem',
                        fontSize: '0.72rem',
                        borderRadius: 'var(--radius-sm)',
                        border: `1px solid ${spellLevelFilter === lvl ? 'var(--accent-gold)' : 'var(--border-subtle)'}`,
                        backgroundColor: spellLevelFilter === lvl ? 'var(--accent-gold-dim)' : 'var(--bg-card)',
                        color: spellLevelFilter === lvl ? 'var(--accent-gold)' : 'var(--text-secondary)',
                        cursor: 'pointer',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {lvl === 'all' ? 'All Levels' : lvl === 0 ? 'Cantrips' : `Lvl ${lvl}`}
                    </button>
                  ))}
                </div>

                {/* Selected Spells Badge List */}
                {customSpells.length > 0 && (
                  <div
                    style={{
                      padding: '0.6rem 0.75rem',
                      backgroundColor: 'var(--bg-card)',
                      borderRadius: 'var(--radius-sm)',
                      border: '1px solid var(--border-subtle)',
                    }}
                  >
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>
                      Selected Spells ({customSpells.length}):
                    </div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                      {customSpells.map((sName) => (
                        <span
                          key={sName}
                          style={{
                            fontSize: '0.72rem',
                            padding: '2px 8px',
                            borderRadius: '12px',
                            backgroundColor: 'var(--accent-gold-dim)',
                            color: 'var(--accent-gold)',
                            border: '1px solid var(--border-gold)',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '4px',
                          }}
                        >
                          ✨ {sName}
                          <button
                            type="button"
                            onClick={() => setCustomSpells(customSpells.filter((n) => n !== sName))}
                            style={{
                              background: 'none',
                              border: 'none',
                              color: 'var(--accent-gold)',
                              cursor: 'pointer',
                              padding: 0,
                              lineHeight: 1,
                              display: 'flex',
                            }}
                          >
                            <X size={10} />
                          </button>
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Spells List */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '350px', overflowY: 'auto' }}>
                  {filteredCatalogSpells.map((spell) => {
                    const isSelected = customSpells.includes(spell.name);
                    return (
                      <div
                        key={spell.name}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          padding: '0.6rem 0.85rem',
                          backgroundColor: isSelected ? 'rgba(200, 155, 60, 0.05)' : 'var(--bg-card)',
                          borderRadius: 'var(--radius-sm)',
                          border: `1px solid ${isSelected ? 'var(--border-gold)' : 'var(--border-subtle)'}`,
                          gap: '0.75rem',
                        }}
                      >
                        <div style={{ flex: 1 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: isSelected ? 'var(--accent-gold)' : 'var(--text-primary)' }}>
                              {spell.name}
                            </span>
                            <span
                              style={{
                                fontSize: '0.68rem',
                                padding: '1px 5px',
                                borderRadius: '4px',
                                backgroundColor: spell.level === 0 ? 'var(--accent-cyan-dim)' : 'var(--bg-surface)',
                                color: spell.level === 0 ? 'var(--accent-cyan)' : 'var(--text-muted)',
                              }}
                            >
                              {spell.level === 0 ? 'Cantrip' : `Level ${spell.level}`}
                            </span>
                            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                              {spell.school}
                            </span>
                          </div>
                          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                            {spell.casting_time} • {spell.range} {spell.damage ? `• ${spell.damage}` : ''}
                          </div>
                        </div>

                        <button
                          type="button"
                          onClick={() => {
                            if (isSelected) {
                              setCustomSpells(customSpells.filter((n) => n !== spell.name));
                            } else {
                              setCustomSpells([...customSpells, spell.name]);
                            }
                          }}
                          className={isSelected ? 'btn btn-primary' : 'btn btn-secondary'}
                          style={{
                            fontSize: '0.75rem',
                            padding: '4px 10px',
                            minWidth: '85px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '4px',
                          }}
                        >
                          {isSelected ? (
                            <>
                              <Check size={12} /> Selected
                            </>
                          ) : (
                            '+ Select'
                          )}
                        </button>
                      </div>
                    );
                  })}
                  {filteredCatalogSpells.length === 0 && (
                    <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.825rem' }}>
                      No spells found matching the active filters.
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Footer with Actions */}
          <div
            style={{
              padding: '1rem 1.5rem',
              borderTop: '1px solid var(--border-subtle)',
              backgroundColor: 'var(--bg-card)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '0.75rem',
            }}
          >
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              {tab === 'world'
                ? 'Step 1 of 3: World & Theme'
                : tab === 'character'
                ? 'Step 2 of 3: Character Sheet'
                : 'Step 3 of 3: Spells & Spellbook'}
            </div>

            <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
              {tab === 'world' ? (
                <button
                  type="button"
                  onClick={() => setTab('character')}
                  style={{
                    backgroundColor: 'var(--accent-gold)',
                    color: '#0a0c10',
                    border: 'none',
                    borderRadius: 'var(--radius-md)',
                    padding: '0.6rem 1.25rem',
                    fontWeight: 600,
                    fontSize: '0.875rem',
                    cursor: 'pointer',
                  }}
                >
                  Next: Character Sheet &rarr;
                </button>
              ) : tab === 'character' ? (
                <>
                  <button
                    type="button"
                    onClick={() => setTab('world')}
                    style={{
                      backgroundColor: 'transparent',
                      color: 'var(--text-secondary)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 'var(--radius-md)',
                      padding: '0.6rem 1rem',
                      fontSize: '0.875rem',
                      cursor: 'pointer',
                    }}
                  >
                    &larr; Back to World
                  </button>
                  <button
                    type="button"
                    onClick={() => setTab('spells')}
                    style={{
                      backgroundColor: 'transparent',
                      color: 'var(--accent-gold)',
                      border: '1px solid var(--border-gold)',
                      borderRadius: 'var(--radius-md)',
                      padding: '0.6rem 1rem',
                      fontSize: '0.875rem',
                      cursor: 'pointer',
                    }}
                  >
                    Next: Spells (Optional) &rarr;
                  </button>
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    style={{
                      backgroundColor: 'var(--accent-gold)',
                      color: '#0a0c10',
                      border: 'none',
                      borderRadius: 'var(--radius-md)',
                      padding: '0.6rem 1.5rem',
                      fontWeight: 600,
                      fontSize: '0.875rem',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                    }}
                  >
                    <Sparkles size={16} />
                    Launch Campaign
                  </button>
                </>
              ) : (
                <>
                  <button
                    type="button"
                    onClick={() => setTab('character')}
                    style={{
                      backgroundColor: 'transparent',
                      color: 'var(--text-secondary)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 'var(--radius-md)',
                      padding: '0.6rem 1rem',
                      fontSize: '0.875rem',
                      cursor: 'pointer',
                    }}
                  >
                    &larr; Back to Character
                  </button>
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    style={{
                      backgroundColor: 'var(--accent-gold)',
                      color: '#0a0c10',
                      border: 'none',
                      borderRadius: 'var(--radius-md)',
                      padding: '0.6rem 1.5rem',
                      fontWeight: 600,
                      fontSize: '0.875rem',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                    }}
                  >
                    <Sparkles size={16} />
                    Launch Campaign ({customSpells.length} Spells)
                  </button>
                </>
              )}
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};
