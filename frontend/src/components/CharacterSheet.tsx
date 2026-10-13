import React, { useState } from 'react';
import {
  Shield,
  Heart,
  Zap,
  Eye,
  Crosshair,
  Backpack,
  Sparkles,
  BookOpen,
  Plus,
  Minus,
  CheckCircle2,
  XCircle,
  Sword,
  Feather,
  Moon,
  Sun,
  X,
} from 'lucide-react';
import { Character, InventoryItem } from '../types/game';
import { SpellManagerModal } from './SpellManagerModal';

const STANDARD_CONDITIONS = [
  'Blinded',
  'Charmed',
  'Deafened',
  'Frightened',
  'Grappled',
  'Incapacitated',
  'Invisible',
  'Paralyzed',
  'Petrified',
  'Poisoned',
  'Prone',
  'Restrained',
  'Stunned',
  'Unconscious',
  'Exhaustion',
];

interface CharacterSheetProps {
  character: Character | null;
  onModifyHp: (delta: number) => Promise<void>;
  onToggleSlot: (level: number, slotIndex: number) => Promise<void>;
  onToggleItem: (itemId: string) => Promise<void>;
  onCharacterUpdated?: (updatedChar: Character) => void;
  onSendAction?: (actionText: string) => void;
  isStreaming?: boolean;
  hasActiveCheck?: boolean;
}

export const CharacterSheet: React.FC<CharacterSheetProps> = ({
  character,
  onModifyHp,
  onToggleSlot,
  onToggleItem,
  onCharacterUpdated,
  onSendAction,
  isStreaming = false,
  hasActiveCheck = false,
}) => {
  const [activeTab, setActiveTab] = useState<'inventory' | 'spells' | 'skills' | 'traits'>('inventory');
  const [hpInput, setHpInput] = useState<string>('1');
  const [isSpellManagerOpen, setIsSpellManagerOpen] = useState<boolean>(false);

  if (!character) {
    return (
      <div style={{ padding: '24px', color: 'var(--text-muted)', textAlign: 'center' }}>
        Loading character sheet...
      </div>
    );
  }

  const hpPercent = Math.max(0, Math.min(100, (character.current_hp / character.max_hp) * 100));
  const hpColor =
    hpPercent > 50
      ? 'var(--accent-green)'
      : hpPercent > 20
      ? 'var(--accent-gold)'
      : 'var(--accent-crimson)';

  const formatMod = (val?: number) => {
    if (val === undefined) return '+0';
    return val >= 0 ? `+${val}` : `${val}`;
  };

  const handleCustomHp = (isDamage: boolean) => {
    const val = parseInt(hpInput, 10);
    if (!isNaN(val) && val > 0) {
      onModifyHp(isDamage ? -val : val);
    }
  };

  const handleConditionChange = async (condition: string, action: 'add' | 'remove') => {
    try {
      const res = await fetch('/api/game/character/conditions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ condition, action }),
      });
      if (res.ok) {
        const data = await res.json();
        if (data.character && onCharacterUpdated) {
          onCharacterUpdated(data.character);
        }
      }
    } catch (err) {
      console.error('Failed to update condition:', err);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Header Profile */}
      <div
        style={{
          padding: '16px 20px',
          borderBottom: '1px solid var(--border-subtle)',
          backgroundColor: 'var(--bg-card)',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h2
              style={{
                fontFamily: 'var(--font-display)',
                fontSize: '18px',
                fontWeight: 700,
                color: 'var(--accent-gold)',
                letterSpacing: '0.02em',
              }}
            >
              {character.name}
            </h2>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '2px' }}>
              Level {character.level} {character.race} {character.character_class}{' '}
              {character.subclass ? `(${character.subclass})` : ''}
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              {character.alignment} • {character.background}
            </div>
          </div>
          <div
            style={{
              textAlign: 'right',
              background: 'var(--bg-surface)',
              padding: '4px 8px',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-subtle)',
            }}
          >
            <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
              Speed
            </div>
            <div style={{ fontWeight: 700, fontSize: '13px' }}>{character.speed_feet} ft</div>
          </div>
        </div>

        {/* Vital Badges Row */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(4, 1fr)',
            gap: '8px',
            marginTop: '14px',
          }}
        >
          <div
            style={{
              backgroundColor: 'var(--bg-surface)',
              border: '1px solid var(--border-accent)',
              borderRadius: 'var(--radius-sm)',
              padding: '8px 4px',
              textAlign: 'center',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '4px', color: 'var(--accent-gold)' }}>
              <Shield size={14} />
              <span style={{ fontSize: '11px', fontWeight: 600 }}>AC</span>
            </div>
            <div style={{ fontSize: '18px', fontWeight: 700, marginTop: '2px' }}>
              {character.armor_class}
            </div>
          </div>

          <div
            style={{
              backgroundColor: 'var(--bg-surface)',
              border: '1px solid var(--border-accent)',
              borderRadius: 'var(--radius-sm)',
              padding: '8px 4px',
              textAlign: 'center',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '4px', color: 'var(--accent-cyan)' }}>
              <Zap size={14} />
              <span style={{ fontSize: '11px', fontWeight: 600 }}>INIT</span>
            </div>
            <div style={{ fontSize: '18px', fontWeight: 700, marginTop: '2px' }}>
              {formatMod(character.ability_modifiers?.dexterity)}
            </div>
          </div>

          <div
            style={{
              backgroundColor: 'var(--bg-surface)',
              border: '1px solid var(--border-accent)',
              borderRadius: 'var(--radius-sm)',
              padding: '8px 4px',
              textAlign: 'center',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '4px', color: 'var(--accent-green)' }}>
              <Eye size={14} />
              <span style={{ fontSize: '11px', fontWeight: 600 }}>PERC</span>
            </div>
            <div style={{ fontSize: '18px', fontWeight: 700, marginTop: '2px' }}>
              {character.passive_perception}
            </div>
          </div>

          <div
            style={{
              backgroundColor: 'var(--bg-surface)',
              border: '1px solid var(--border-accent)',
              borderRadius: 'var(--radius-sm)',
              padding: '8px 4px',
              textAlign: 'center',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '4px', color: 'var(--text-secondary)' }}>
              <Crosshair size={14} />
              <span style={{ fontSize: '11px', fontWeight: 600 }}>PROF</span>
            </div>
            <div style={{ fontSize: '18px', fontWeight: 700, marginTop: '2px' }}>
              +{character.proficiency_bonus}
            </div>
          </div>
        </div>

        {/* Hit Points Bar & Controls */}
        <div
          style={{
            marginTop: '14px',
            backgroundColor: 'var(--bg-surface)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-sm)',
            padding: '10px',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Heart size={14} color={hpColor} />
              <span style={{ fontWeight: 600, fontSize: '12px', textTransform: 'uppercase' }}>Hit Points</span>
            </div>
            <div style={{ fontSize: '13px', fontWeight: 700 }}>
              <span style={{ color: hpColor }}>{character.current_hp}</span> / {character.max_hp}
              {character.temp_hp > 0 && (
                <span style={{ color: 'var(--accent-cyan)', marginLeft: '6px' }}>
                  (+{character.temp_hp} Temp)
                </span>
              )}
            </div>
          </div>

          <div
            style={{
              height: '8px',
              backgroundColor: 'var(--bg-canvas)',
              borderRadius: '4px',
              overflow: 'hidden',
              marginBottom: '10px',
              border: '1px solid var(--border-subtle)',
            }}
          >
            <div
              style={{
                height: '100%',
                width: `${hpPercent}%`,
                backgroundColor: hpColor,
                transition: 'width 0.3s ease, background-color 0.3s ease',
              }}
            />
          </div>

          <div style={{ display: 'flex', gap: '4px', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', gap: '4px' }}>
              <button
                type="button"
                className="btn btn-danger"
                style={{ padding: '2px 8px', fontSize: '11px' }}
                onClick={() => onModifyHp(-5)}
                title="Deal 5 damage"
              >
                -5
              </button>
              <button
                type="button"
                className="btn btn-danger"
                style={{ padding: '2px 8px', fontSize: '11px' }}
                onClick={() => onModifyHp(-1)}
                title="Deal 1 damage"
              >
                -1
              </button>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <input
                type="number"
                min="1"
                max="99"
                value={hpInput}
                onChange={(e) => setHpInput(e.target.value)}
                style={{
                  width: '42px',
                  textAlign: 'center',
                  background: 'var(--bg-canvas)',
                  border: '1px solid var(--border-accent)',
                  color: 'var(--text-primary)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '12px',
                  padding: '2px',
                }}
              />
              <button
                type="button"
                className="btn btn-secondary"
                style={{ padding: '2px 6px', fontSize: '11px' }}
                onClick={() => handleCustomHp(true)}
              >
                Dmg
              </button>
              <button
                type="button"
                className="btn btn-secondary"
                style={{ padding: '2px 6px', fontSize: '11px' }}
                onClick={() => handleCustomHp(false)}
              >
                Heal
              </button>
            </div>

            <div style={{ display: 'flex', gap: '4px' }}>
              <button
                type="button"
                className="btn btn-secondary"
                style={{ padding: '2px 8px', fontSize: '11px', color: 'var(--accent-green)' }}
                onClick={() => onModifyHp(1)}
                title="Heal 1 HP"
              >
                +1
              </button>
              <button
                type="button"
                className="btn btn-secondary"
                style={{ padding: '2px 8px', fontSize: '11px', color: 'var(--accent-green)' }}
                onClick={() => onModifyHp(5)}
                title="Heal 5 HP"
              >
                +5
              </button>
            </div>
          </div>
        </div>

        {/* Rest & Hit Dice Bar */}
        <div
          style={{
            marginTop: '10px',
            backgroundColor: 'var(--bg-surface)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-sm)',
            padding: '8px 10px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '8px',
            flexWrap: 'wrap',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
              Hit Dice:
            </span>
            <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--accent-gold)' }}>
              {character.hit_dice_remaining ?? character.level} / {character.hit_dice_max ?? character.level}
            </span>
            <span style={{ fontSize: '10px', color: 'var(--text-secondary)' }}>
              ({character.hit_dice || 'd8'})
            </span>
          </div>

          <div style={{ display: 'flex', gap: '6px' }}>
            <button
              type="button"
              className="btn btn-secondary"
              style={{
                padding: '3px 8px',
                fontSize: '11px',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                color: 'var(--accent-cyan)',
              }}
              disabled={isStreaming || hasActiveCheck}
              onClick={() => onSendAction?.('[REST REQUEST: SHORT] I look for a defensible spot to take a 1-hour Short Rest and tend to my wounds.')}
              title="Take a 1-hour Short Rest (spends Hit Dice to heal)"
            >
              <Moon size={12} />
              <span>Short Rest (1h)</span>
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              style={{
                padding: '3px 8px',
                fontSize: '11px',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                color: 'var(--accent-gold)',
              }}
              disabled={isStreaming || hasActiveCheck}
              onClick={() => onSendAction?.('[REST REQUEST: LONG] I attempt to make camp and take an 8-hour Long Rest.')}
              title="Take an 8-hour Long Rest (restores HP, spell slots, half Hit Dice)"
            >
              <Sun size={12} />
              <span>Long Rest (8h)</span>
            </button>
          </div>
        </div>

        {/* Active Conditions Section */}
        <div
          style={{
            marginTop: '10px',
            backgroundColor: 'var(--bg-surface)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-sm)',
            padding: '8px 10px',
          }}
        >
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: character.conditions && character.conditions.length > 0 ? '6px' : 0,
            }}
          >
            <span style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-secondary)' }}>
              Conditions {character.conditions?.length ? `(${character.conditions.length})` : ''}
            </span>
            <select
              value=""
              onChange={(e) => {
                if (e.target.value) {
                  handleConditionChange(e.target.value, 'add');
                }
              }}
              style={{
                fontSize: '10px',
                padding: '2px 6px',
                backgroundColor: 'var(--bg-canvas)',
                border: '1px solid var(--border-subtle)',
                color: 'var(--text-secondary)',
                borderRadius: 'var(--radius-sm)',
                cursor: 'pointer',
              }}
            >
              <option value="">+ Add Condition</option>
              {STANDARD_CONDITIONS.filter(
                (c) => !(character.conditions || []).map((x) => x.toLowerCase()).includes(c.toLowerCase())
              ).map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>

          {character.conditions && character.conditions.length > 0 && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
              {character.conditions.map((cond) => (
                <span
                  key={cond}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '4px',
                    fontSize: '11px',
                    padding: '2px 6px',
                    backgroundColor: 'var(--accent-crimson-dim)',
                    color: 'var(--accent-crimson)',
                    border: '1px solid var(--accent-crimson)',
                    borderRadius: '10px',
                    fontWeight: 600,
                  }}
                >
                  {cond}
                  <button
                    type="button"
                    onClick={() => handleConditionChange(cond, 'remove')}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: 'var(--accent-crimson)',
                      cursor: 'pointer',
                      padding: 0,
                      fontSize: '12px',
                      lineHeight: 1,
                      display: 'flex',
                      alignItems: 'center',
                    }}
                    title={`Remove ${cond}`}
                  >
                    <X size={11} />
                  </button>
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Ability Scores Grid */}
        <div className="ability-scores-grid">
          {Object.entries(character.abilities).map(([stat, score]) => {
            const mod = character.ability_modifiers?.[stat];
            const shortName = stat.substring(0, 3).toUpperCase();
            return (
              <div
                key={stat}
                style={{
                  backgroundColor: 'var(--bg-surface)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '6px 2px',
                  textAlign: 'center',
                }}
              >
                <div style={{ fontSize: '10px', color: 'var(--text-muted)', fontWeight: 700 }}>
                  {shortName}
                </div>
                <div
                  style={{
                    fontSize: '16px',
                    fontWeight: 700,
                    color: 'var(--text-primary)',
                    marginTop: '1px',
                  }}
                >
                  {formatMod(mod)}
                </div>
                <div style={{ fontSize: '10px', color: 'var(--text-secondary)' }}>{score}</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Tabs Header */}
      <div
        style={{
          display: 'flex',
          borderBottom: '1px solid var(--border-subtle)',
          backgroundColor: 'var(--bg-surface)',
        }}
      >
        <button
          type="button"
          onClick={() => setActiveTab('inventory')}
          style={{
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '6px',
            padding: '10px',
            fontSize: '12px',
            fontWeight: 600,
            background: 'none',
            border: 'none',
            borderBottom: activeTab === 'inventory' ? '2px solid var(--accent-gold)' : '2px solid transparent',
            color: activeTab === 'inventory' ? 'var(--accent-gold)' : 'var(--text-secondary)',
            cursor: 'pointer',
          }}
        >
          <Backpack size={14} />
          Inventory ({character.inventory.length})
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('spells')}
          style={{
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '6px',
            padding: '10px',
            fontSize: '12px',
            fontWeight: 600,
            background: 'none',
            border: 'none',
            borderBottom: activeTab === 'spells' ? '2px solid var(--accent-gold)' : '2px solid transparent',
            color: activeTab === 'spells' ? 'var(--accent-gold)' : 'var(--text-secondary)',
            cursor: 'pointer',
          }}
        >
          <Sparkles size={14} />
          Spells
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('skills')}
          style={{
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '6px',
            padding: '10px',
            fontSize: '12px',
            fontWeight: 600,
            background: 'none',
            border: 'none',
            borderBottom: activeTab === 'skills' ? '2px solid var(--accent-gold)' : '2px solid transparent',
            color: activeTab === 'skills' ? 'var(--accent-gold)' : 'var(--text-secondary)',
            cursor: 'pointer',
          }}
        >
          <BookOpen size={14} />
          Skills &amp; Saves
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('traits')}
          style={{
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '6px',
            padding: '10px 4px',
            fontSize: '12px',
            fontWeight: 600,
            background: 'none',
            border: 'none',
            borderBottom: activeTab === 'traits' ? '2px solid var(--accent-gold)' : '2px solid transparent',
            color: activeTab === 'traits' ? 'var(--accent-gold)' : 'var(--text-secondary)',
            cursor: 'pointer',
          }}
        >
          <Feather size={14} />
          Bio &amp; Traits
        </button>
      </div>

      {/* Tab Contents */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px' }}>
        {activeTab === 'inventory' && (
          <div className="tab-pane-anim">
            {/* Carrying Capacity */}
            <div
              style={{
                marginBottom: '12px',
                padding: '8px 12px',
                backgroundColor: 'var(--bg-card)',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--border-subtle)',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                <span>Weight: {character.total_weight_carried.toFixed(1)} lbs</span>
                <span>Max: {character.carrying_capacity_lbs} lbs</span>
              </div>
              <div style={{ height: '4px', backgroundColor: 'var(--bg-canvas)', borderRadius: '2px', overflow: 'hidden' }}>
                <div
                  style={{
                    height: '100%',
                    width: `${Math.min(100, (character.total_weight_carried / character.carrying_capacity_lbs) * 100)}%`,
                    backgroundColor: character.is_encumbered ? 'var(--accent-crimson)' : 'var(--accent-gold)',
                  }}
                />
              </div>
            </div>

            {/* Inventory List */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {character.inventory.map((item) => (
                <div
                  key={item.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '8px 12px',
                    backgroundColor: item.equipped ? 'var(--bg-card-active)' : 'var(--bg-card)',
                    border: item.equipped ? '1px solid var(--accent-gold-dim)' : '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-sm)',
                  }}
                >
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{ fontWeight: 600, fontSize: '13px', color: 'var(--text-primary)' }}>
                        {item.name}
                      </span>
                      {item.quantity > 1 && (
                        <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                          x{item.quantity}
                        </span>
                      )}
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
                      {item.damage && <span>Damage: {item.damage} {item.damage_type || ''} • </span>}
                      {item.armor_base && <span>Base AC: {item.armor_base} • </span>}
                      <span>{item.weight_lbs * item.quantity} lbs</span>
                    </div>
                  </div>

                  <button
                    type="button"
                    className={item.equipped ? 'btn btn-primary' : 'btn btn-secondary'}
                    style={{ fontSize: '11px', padding: '3px 8px' }}
                    onClick={() => onToggleItem(item.id)}
                  >
                    {item.equipped ? 'Equipped' : 'Equip'}
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'spells' && (
          <div className="tab-pane-anim">
            {/* Spellcasting Header */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(2, 1fr)',
                gap: '8px',
                marginBottom: '16px',
              }}
            >
              <div
                style={{
                  padding: '8px',
                  backgroundColor: 'var(--bg-card)',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--border-subtle)',
                  textAlign: 'center',
                }}
              >
                <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                  Spell Save DC
                </div>
                <div style={{ fontSize: '18px', fontWeight: 700, color: 'var(--accent-gold)' }}>
                  {character.spell_save_dc || 'N/A'}
                </div>
              </div>
              <div
                style={{
                  padding: '8px',
                  backgroundColor: 'var(--bg-card)',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--border-subtle)',
                  textAlign: 'center',
                }}
              >
                <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                  Spell Attack
                </div>
                <div style={{ fontSize: '18px', fontWeight: 700, color: 'var(--accent-cyan)' }}>
                  {formatMod(character.spell_attack_bonus)}
                </div>
              </div>
            </div>

            {/* Spell Slots Matrix */}
            <div style={{ marginBottom: '16px' }}>
              <div style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                Spell Slots Matrix (Level 1–9)
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {Array.from({ length: 9 }, (_, i) => i + 1).map((lvl) => {
                  const key = `level_${lvl}` as keyof typeof character.spell_slots;
                  const slotObj = character.spell_slots[key];
                  if (!slotObj || slotObj.max_slots === 0) return null;

                  return (
                    <div
                      key={lvl}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        padding: '8px 12px',
                        backgroundColor: 'var(--bg-card)',
                        borderRadius: 'var(--radius-sm)',
                        border: '1px solid var(--border-subtle)',
                      }}
                    >
                      <span style={{ fontSize: '12px', fontWeight: 600 }}>Level {lvl}</span>
                      <div style={{ display: 'flex', gap: '6px' }}>
                        {Array.from({ length: slotObj.max_slots }, (_, idx) => {
                          const isUsed = idx < slotObj.used_slots;
                          return (
                            <button
                              key={idx}
                              type="button"
                              onClick={() => onToggleSlot(lvl, idx)}
                              title={isUsed ? 'Restore slot' : 'Expend slot'}
                              style={{
                                width: '22px',
                                height: '22px',
                                borderRadius: '50%',
                                border: isUsed ? '1px solid var(--border-accent)' : '1px solid var(--accent-cyan)',
                                backgroundColor: isUsed ? 'transparent' : 'var(--accent-cyan-dim)',
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                              }}
                            >
                              <div
                                style={{
                                  width: '10px',
                                  height: '10px',
                                  borderRadius: '50%',
                                  backgroundColor: isUsed ? 'transparent' : 'var(--accent-cyan)',
                                }}
                              />
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Known Spells */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <div style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-secondary)' }}>
                  Prepared / Known Spells
                </div>
                <button
                  type="button"
                  onClick={() => setIsSpellManagerOpen(true)}
                  className="btn btn-secondary"
                  style={{
                    fontSize: '11px',
                    padding: '3px 8px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    borderColor: 'var(--border-gold)',
                    color: 'var(--accent-gold)',
                  }}
                >
                  <Sparkles size={12} />
                  Manage Spells
                </button>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {character.known_spells && character.known_spells.length > 0 ? (
                  character.known_spells.map((spell) => (
                    <div
                      key={spell}
                      style={{
                        padding: '6px 10px',
                        backgroundColor: 'var(--bg-card)',
                        borderRadius: 'var(--radius-sm)',
                        fontSize: '12px',
                        color: 'var(--text-primary)',
                        border: '1px solid var(--border-subtle)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                      }}
                    >
                      <span>✨ {spell}</span>
                      <button
                        type="button"
                        className="btn btn-secondary"
                        style={{
                          fontSize: '10px',
                          padding: '2px 8px',
                          color: 'var(--accent-cyan)',
                          borderColor: 'var(--accent-cyan-dim)',
                        }}
                        disabled={isStreaming || hasActiveCheck}
                        onClick={() => onSendAction?.(`[SPELL CAST] I cast ${spell}!`)}
                        title="Cast this spell"
                      >
                        Cast
                      </button>
                    </div>
                  ))
                ) : (
                  <div
                    style={{
                      padding: '12px',
                      backgroundColor: 'var(--bg-card)',
                      borderRadius: 'var(--radius-sm)',
                      fontSize: '12px',
                      color: 'var(--text-muted)',
                      border: '1px dashed var(--border-subtle)',
                      textAlign: 'center',
                    }}
                  >
                    No spells prepared or known. Click &quot;Manage Spells&quot; to choose spells.
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'skills' && (
          <div className="tab-pane-anim">
            {/* Saving Throws */}
            <div style={{ marginBottom: '16px' }}>
              <div style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                Saving Throws
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px' }}>
                {Object.entries(character.saving_throw_bonuses || {}).map(([stat, bonus]) => {
                  const isProf = character.saving_throw_proficiencies.includes(stat.toLowerCase());
                  return (
                    <div
                      key={stat}
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        padding: '6px 10px',
                        backgroundColor: 'var(--bg-card)',
                        borderRadius: 'var(--radius-sm)',
                        fontSize: '12px',
                      }}
                    >
                      <span style={{ color: isProf ? 'var(--accent-gold)' : 'var(--text-secondary)' }}>
                        {isProf ? '● ' : '○ '}
                        {stat.substring(0, 3).toUpperCase()}
                      </span>
                      <span style={{ fontWeight: 700 }}>{formatMod(bonus)}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* 18 Skills List */}
            <div>
              <div style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                Skills
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                {Object.entries(character.skill_bonuses || {}).map(([skill, bonus]) => {
                  const isExpert = character.skill_expertise?.includes(skill);
                  const isProf = character.skill_proficiencies?.includes(skill);
                  const mark = isExpert ? '★ ' : isProf ? '● ' : '○ ';

                  return (
                    <div
                      key={skill}
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        padding: '5px 10px',
                        backgroundColor: 'var(--bg-card)',
                        borderRadius: 'var(--radius-sm)',
                        fontSize: '12px',
                      }}
                    >
                      <span
                        style={{
                          color: isExpert
                            ? 'var(--accent-gold)'
                            : isProf
                            ? 'var(--text-primary)'
                            : 'var(--text-muted)',
                        }}
                      >
                        {mark}
                        {skill.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                      </span>
                      <span style={{ fontWeight: 700 }}>{formatMod(bonus)}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'traits' && (
          <div className="tab-pane-anim" style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {/* Racial Traits & Advantages */}
            <div
              style={{
                padding: '14px',
                backgroundColor: 'var(--bg-card)',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border-subtle)',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <div style={{ fontWeight: 700, fontSize: '13px', color: 'var(--accent-gold)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  {character.race} Traits &amp; Senses
                </div>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                  Darkvision: {character.darkvision_feet} ft
                </div>
              </div>

              {character.racial_traits && character.racial_traits.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {character.racial_traits.map((trait, idx) => (
                    <div
                      key={idx}
                      style={{
                        fontSize: '12px',
                        lineHeight: 1.5,
                        color: 'var(--text-secondary)',
                        padding: '6px 10px',
                        backgroundColor: 'var(--bg-surface)',
                        borderRadius: 'var(--radius-sm)',
                        borderLeft: '2px solid var(--accent-gold)',
                      }}
                    >
                      {trait}
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                  Standard D&amp;D 5e traits apply.
                </div>
              )}
            </div>

            {/* Backstory & Personal Drive */}
            <div
              style={{
                padding: '14px',
                backgroundColor: 'var(--bg-card)',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border-subtle)',
              }}
            >
              <div style={{ fontWeight: 700, fontSize: '13px', color: 'var(--accent-gold)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>
                Backstory &amp; Personal Drive
              </div>
              {character.backstory ? (
                <div
                  style={{
                    fontFamily: 'var(--font-narrative)',
                    fontSize: '13px',
                    lineHeight: 1.6,
                    color: 'var(--text-primary)',
                    fontStyle: 'italic',
                    whiteSpace: 'pre-line',
                  }}
                >
                  &ldquo;{character.backstory}&rdquo;
                </div>
              ) : (
                <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                  No personal backstory recorded.
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Spellbook / Spells Manager Modal */}
      {isSpellManagerOpen && (
        <SpellManagerModal
          isOpen={isSpellManagerOpen}
          character={character}
          onClose={() => setIsSpellManagerOpen(false)}
          onCharacterUpdated={(updatedChar) => {
            if (onCharacterUpdated) {
              onCharacterUpdated(updatedChar);
            }
          }}
          onCastSpell={(spellName) => {
            setIsSpellManagerOpen(false);
            onSendAction?.(`[SPELL CAST] I cast ${spellName}!`);
          }}
          isStreaming={isStreaming}
          hasActiveCheck={hasActiveCheck}
        />
      )}
    </div>
  );
};
