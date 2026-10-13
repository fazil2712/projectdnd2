import React, { useState, useEffect, useMemo } from 'react';
import {
  X,
  Sparkles,
  BookOpen,
  Search,
  Filter,
  Check,
  Plus,
  Trash2,
  AlertTriangle,
  Flame,
  Shield,
  Zap,
  Clock,
  Crosshair,
  Info
} from 'lucide-react';
import { Character, SpellCatalogItem, SpellsCatalog } from '../types/game';

interface SpellManagerModalProps {
  isOpen: boolean;
  character: Character;
  onClose: () => void;
  onCharacterUpdated: (updatedChar: Character) => void;
}

export const SpellManagerModal: React.FC<SpellManagerModalProps> = ({
  isOpen,
  character,
  onClose,
  onCharacterUpdated,
}) => {
  const [catalog, setCatalog] = useState<SpellCatalogItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedLevel, setSelectedLevel] = useState<number | 'all'>('all');
  const [enforceClassFilter, setEnforceClassFilter] = useState<boolean>(true);
  const [showPreparedOnly, setShowPreparedOnly] = useState<boolean>(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [processingSpell, setProcessingSpell] = useState<string | null>(null);

  // Fetch spells catalog on mount
  useEffect(() => {
    if (!isOpen) return;

    const fetchSpells = async () => {
      setIsLoading(true);
      try {
        const res = await fetch('/api/compendium/spells');
        if (res.ok) {
          const data: SpellsCatalog = await res.json();
          const allSpells: SpellCatalogItem[] = [];
          Object.values(data).forEach((list) => {
            if (Array.isArray(list)) {
              allSpells.push(...list);
            }
          });
          // Sort spells by level then alphabetically by name
          allSpells.sort((a, b) => a.level - b.level || a.name.localeCompare(b.name));
          setCatalog(allSpells);
        }
      } catch (err) {
        console.error('Failed to fetch spells catalog:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchSpells();
  }, [isOpen]);

  // Determine highest available spell slot level for the character
  const maxSlotLevel = useMemo(() => {
    let maxLvl = 0;
    if (character.spell_slots) {
      for (let lvl = 1; lvl <= 9; lvl++) {
        const key = `level_${lvl}` as keyof typeof character.spell_slots;
        const slot = character.spell_slots[key];
        if (slot && slot.max_slots > 0) {
          maxLvl = Math.max(maxLvl, lvl);
        }
      }
    }
    return maxLvl;
  }, [character.spell_slots]);

  const charClass = character.character_class || 'Fighter';
  const preparedSet = useMemo(() => new Set(character.known_spells.map((s) => s.toLowerCase())), [character.known_spells]);

  // Filter catalog based on search, level, class filter, and prepared tab
  const filteredSpells = useMemo(() => {
    return catalog.filter((spell) => {
      // 1. Prepared only filter
      const isPrepared = preparedSet.has(spell.name.toLowerCase());
      if (showPreparedOnly && !isPrepared) return false;

      // 2. Search query filter
      if (searchTerm.trim()) {
        const q = searchTerm.toLowerCase();
        const matchesName = spell.name.toLowerCase().includes(q);
        const matchesSchool = spell.school.toLowerCase().includes(q);
        const matchesDesc = spell.description.toLowerCase().includes(q);
        if (!matchesName && !matchesSchool && !matchesDesc) return false;
      }

      // 3. Level tab filter
      if (selectedLevel !== 'all' && spell.level !== selectedLevel) {
        return false;
      }

      // 4. 5e Class constraint filter
      if (enforceClassFilter && !showPreparedOnly) {
        const allowed = (spell.classes || []).map((c) => c.toLowerCase());
        const clsLower = charClass.toLowerCase();

        const matchesClass = allowed.some((c) => clsLower.includes(c));
        const isArcaneTrickster = (clsLower.includes('rogue') || clsLower.includes('fighter')) && allowed.includes('wizard');

        if (!matchesClass && !isArcaneTrickster) {
          return false;
        }
      }

      return true;
    });
  }, [catalog, searchTerm, selectedLevel, enforceClassFilter, showPreparedOnly, preparedSet, charClass]);

  const handleLearnSpell = async (spell: SpellCatalogItem) => {
    setProcessingSpell(spell.name);
    setActionError(null);
    try {
      const res = await fetch('/api/game/character/spells/learn', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          spell_name: spell.name,
          bypass_class_limit: !enforceClassFilter,
        }),
      });

      const data = await res.json();
      if (!res.ok) {
        setActionError(data.detail || data.message || `Failed to prepare ${spell.name}`);
        return;
      }

      if (data.character) {
        onCharacterUpdated(data.character);
      }
    } catch (err: any) {
      setActionError(err.message || `Error preparing ${spell.name}`);
    } finally {
      setProcessingSpell(null);
    }
  };

  const handleRemoveSpell = async (spellName: string) => {
    setProcessingSpell(spellName);
    setActionError(null);
    try {
      const res = await fetch('/api/game/character/spells/remove', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ spell_name: spellName }),
      });

      const data = await res.json();
      if (!res.ok) {
        setActionError(data.detail || data.message || `Failed to unprepare ${spellName}`);
        return;
      }

      if (data.character) {
        onCharacterUpdated(data.character);
      }
    } catch (err: any) {
      setActionError(err.message || `Error unpreparing ${spellName}`);
    } finally {
      setProcessingSpell(null);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-backdrop" onClick={onClose} style={{ zIndex: 1200 }}>
      <div
        className="modal-container"
        onClick={(e) => e.stopPropagation()}
        style={{
          maxWidth: '850px',
          width: '94vw',
          maxHeight: '90vh',
          display: 'flex',
          flexDirection: 'column',
          backgroundColor: 'var(--bg-surface)',
          border: '1px solid var(--border-accent)',
          borderRadius: 'var(--radius-md)',
          boxShadow: 'var(--shadow-lg)',
          overflow: 'hidden',
          padding: 0,
        }}
      >
        {/* Modal Header */}
        <div
          style={{
            padding: '16px 20px',
            borderBottom: '1px solid var(--border-subtle)',
            backgroundColor: 'var(--bg-canvas)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div
              style={{
                width: '36px',
                height: '36px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'var(--accent-gold-dim)',
                border: '1px solid var(--accent-gold)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--accent-gold)',
              }}
            >
              <BookOpen size={20} />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <h2 style={{ fontSize: '18px', fontWeight: 700, margin: 0, color: 'var(--text-primary)' }}>
                  Grimoire & Spellbook
                </h2>
                <span
                  style={{
                    fontSize: '11px',
                    fontWeight: 600,
                    padding: '2px 8px',
                    borderRadius: '12px',
                    backgroundColor: 'var(--accent-cyan-dim)',
                    color: 'var(--accent-cyan)',
                    border: '1px solid var(--accent-cyan)',
                  }}
                >
                  {charClass} (Lv {character.level})
                </span>
              </div>
              <p style={{ margin: '2px 0 0', fontSize: '12px', color: 'var(--text-secondary)' }}>
                Customize your prepared spells according to official D&D 5e rules.
              </p>
            </div>
          </div>

          <button
            type="button"
            className="icon-btn"
            onClick={onClose}
            aria-label="Close"
            style={{
              padding: '6px',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              borderRadius: 'var(--radius-sm)',
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Status / Alert Bar */}
        {actionError && (
          <div
            style={{
              padding: '10px 16px',
              backgroundColor: 'var(--accent-crimson-dim)',
              color: 'var(--accent-crimson)',
              borderBottom: '1px solid var(--accent-crimson)',
              fontSize: '12px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}
          >
            <AlertTriangle size={15} />
            <span>{actionError}</span>
          </div>
        )}

        {/* Controls Bar (Search, Level tabs, Filters) */}
        <div
          style={{
            padding: '12px 20px',
            backgroundColor: 'var(--bg-card)',
            borderBottom: '1px solid var(--border-subtle)',
            display: 'flex',
            flexDirection: 'column',
            gap: '10px',
          }}
        >
          {/* Search Row & Class Toggle */}
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                backgroundColor: 'var(--bg-surface)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                padding: '6px 10px',
                flex: '1 1 240px',
                gap: '8px',
              }}
            >
              <Search size={15} color="var(--text-muted)" />
              <input
                type="text"
                placeholder="Search spell name, school, description..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  outline: 'none',
                  color: 'var(--text-primary)',
                  fontSize: '13px',
                  width: '100%',
                }}
              />
              {searchTerm && (
                <button
                  type="button"
                  onClick={() => setSearchTerm('')}
                  style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
                >
                  <X size={14} />
                </button>
              )}
            </div>

            {/* 5e Class Constraint Toggle */}
            <button
              type="button"
              className={enforceClassFilter ? 'btn btn-primary' : 'btn btn-secondary'}
              onClick={() => setEnforceClassFilter(!enforceClassFilter)}
              style={{ fontSize: '12px', padding: '6px 12px', display: 'flex', alignItems: 'center', gap: '6px' }}
              title={enforceClassFilter ? 'Enforcing 5e class spell list' : 'Class restrictions bypassed (Homebrew mode)'}
            >
              <Filter size={13} />
              <span>{enforceClassFilter ? `5e ${charClass} List Only` : 'All 5e Spells (Unlocked)'}</span>
            </button>

            {/* Prepared Only Switcher */}
            <button
              type="button"
              className={showPreparedOnly ? 'btn btn-primary' : 'btn btn-secondary'}
              onClick={() => setShowPreparedOnly(!showPreparedOnly)}
              style={{ fontSize: '12px', padding: '6px 12px', display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              <Sparkles size={13} />
              <span>Prepared Only ({character.known_spells.length})</span>
            </button>
          </div>

          {/* Spell Level Filter Pills */}
          <div
            style={{
              display: 'flex',
              gap: '6px',
              overflowX: 'auto',
              paddingBottom: '2px',
            }}
          >
            <button
              type="button"
              className={selectedLevel === 'all' ? 'badge badge-primary' : 'badge badge-neutral'}
              onClick={() => setSelectedLevel('all')}
              style={{ cursor: 'pointer', padding: '4px 10px', fontSize: '11px' }}
            >
              All Levels
            </button>
            <button
              type="button"
              className={selectedLevel === 0 ? 'badge badge-primary' : 'badge badge-neutral'}
              onClick={() => setSelectedLevel(0)}
              style={{ cursor: 'pointer', padding: '4px 10px', fontSize: '11px' }}
            >
              Cantrips (0)
            </button>
            {Array.from({ length: 9 }, (_, i) => i + 1).map((lvl) => {
              const hasSlots = maxSlotLevel >= lvl;
              return (
                <button
                  key={lvl}
                  type="button"
                  className={selectedLevel === lvl ? 'badge badge-primary' : 'badge badge-neutral'}
                  onClick={() => setSelectedLevel(lvl)}
                  style={{
                    cursor: 'pointer',
                    padding: '4px 10px',
                    fontSize: '11px',
                    opacity: hasSlots || !enforceClassFilter ? 1 : 0.6,
                    border: hasSlots ? '1px solid var(--accent-cyan)' : undefined,
                  }}
                  title={hasSlots ? `You have Level ${lvl} spell slots` : `No Level ${lvl} spell slots unlocked yet`}
                >
                  Lv {lvl} {hasSlots ? '•' : ''}
                </button>
              );
            })}
          </div>
        </div>

        {/* Spell Cards Body */}
        <div
          style={{
            flex: 1,
            overflowY: 'auto',
            padding: '16px 20px',
            display: 'flex',
            flexDirection: 'column',
            gap: '10px',
          }}
        >
          {isLoading ? (
            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
              <div className="spinner" style={{ margin: '0 auto 12px' }} />
              <p style={{ fontSize: '13px' }}>Consulting the 5e Arcane Compendium...</p>
            </div>
          ) : filteredSpells.length === 0 ? (
            <div
              style={{
                textAlign: 'center',
                padding: '40px 20px',
                backgroundColor: 'var(--bg-card)',
                borderRadius: 'var(--radius-sm)',
                border: '1px dashed var(--border-subtle)',
              }}
            >
              <Info size={28} color="var(--text-muted)" style={{ margin: '0 auto 8px' }} />
              <div style={{ fontWeight: 600, fontSize: '14px', color: 'var(--text-primary)' }}>
                No matching spells found
              </div>
              <p style={{ fontSize: '12px', color: 'var(--text-secondary)', maxWidth: '400px', margin: '4px auto 0' }}>
                {enforceClassFilter
                  ? `No spells match your filters for the ${charClass} class. Try turning off "5e ${charClass} List Only" or selecting "All Levels".`
                  : 'Try adjusting your search keywords or level filter.'}
              </p>
            </div>
          ) : (
            filteredSpells.map((spell) => {
              const isPrepared = preparedSet.has(spell.name.toLowerCase());
              const isProcessing = processingSpell === spell.name;
              const hasSlotForSpell = spell.level === 0 || maxSlotLevel >= spell.level;

              return (
                <div
                  key={spell.name}
                  style={{
                    backgroundColor: isPrepared ? 'var(--bg-canvas)' : 'var(--bg-card)',
                    border: isPrepared ? '1px solid var(--accent-cyan)' : '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-sm)',
                    padding: '12px 14px',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '8px',
                    transition: 'all 0.15s ease',
                  }}
                >
                  {/* Top Bar: Name, Level, School, and Action */}
                  <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '8px' }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                        <span style={{ fontWeight: 700, fontSize: '14px', color: 'var(--text-primary)' }}>
                          {spell.name}
                        </span>
                        <span
                          style={{
                            fontSize: '10px',
                            fontWeight: 700,
                            padding: '2px 6px',
                            borderRadius: '4px',
                            textTransform: 'uppercase',
                            backgroundColor:
                              spell.level === 0
                                ? 'var(--accent-gold-dim)'
                                : 'var(--accent-cyan-dim)',
                            color:
                              spell.level === 0
                                ? 'var(--accent-gold)'
                                : 'var(--accent-cyan)',
                          }}
                        >
                          {spell.level === 0 ? 'Cantrip' : `Level ${spell.level}`}
                        </span>
                        <span
                          style={{
                            fontSize: '11px',
                            color: 'var(--text-muted)',
                            fontStyle: 'italic',
                          }}
                        >
                          {spell.school}
                        </span>
                      </div>

                      {/* Spell Tags */}
                      <div
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '12px',
                          fontSize: '11px',
                          color: 'var(--text-secondary)',
                          marginTop: '4px',
                          flexWrap: 'wrap',
                        }}
                      >
                        {spell.casting_time && (
                          <span style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
                            <Clock size={11} color="var(--text-muted)" /> {spell.casting_time}
                          </span>
                        )}
                        {spell.range && (
                          <span style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
                            <Crosshair size={11} color="var(--text-muted)" /> {spell.range}
                          </span>
                        )}
                        {spell.duration && <span>Duration: {spell.duration}</span>}
                        {spell.damage && (
                          <span style={{ color: 'var(--accent-crimson)', fontWeight: 600 }}>
                            {spell.damage}
                          </span>
                        )}
                        {spell.healing && (
                          <span style={{ color: 'var(--accent-green)', fontWeight: 600 }}>
                            {spell.healing}
                          </span>
                        )}
                        {spell.save && (
                          <span style={{ color: 'var(--accent-gold)' }}>
                            {spell.save} Save
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Action Button */}
                    <div>
                      {isPrepared ? (
                        <button
                          type="button"
                          className="btn btn-secondary"
                          onClick={() => handleRemoveSpell(spell.name)}
                          disabled={isProcessing}
                          style={{
                            fontSize: '11px',
                            padding: '4px 10px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '4px',
                            color: 'var(--accent-crimson)',
                            borderColor: 'var(--accent-crimson-dim)',
                          }}
                        >
                          <Trash2 size={12} />
                          <span>Unprepare</span>
                        </button>
                      ) : (
                        <button
                          type="button"
                          className={hasSlotForSpell ? 'btn btn-primary' : 'btn btn-secondary'}
                          onClick={() => handleLearnSpell(spell)}
                          disabled={isProcessing}
                          style={{
                            fontSize: '11px',
                            padding: '4px 12px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '4px',
                          }}
                          title={
                            !hasSlotForSpell
                              ? `Warning: Character has no Level ${spell.level} spell slots`
                              : 'Prepare this spell'
                          }
                        >
                          <Plus size={12} />
                          <span>Prepare</span>
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Description */}
                  <p
                    style={{
                      margin: 0,
                      fontSize: '12px',
                      lineHeight: '1.45',
                      color: 'var(--text-secondary)',
                    }}
                  >
                    {spell.description}
                  </p>

                  {/* Class availability badges */}
                  {spell.classes && spell.classes.length > 0 && (
                    <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap', marginTop: '2px' }}>
                      <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>Classes:</span>
                      {spell.classes.map((c) => (
                        <span
                          key={c}
                          style={{
                            fontSize: '10px',
                            padding: '1px 5px',
                            borderRadius: '3px',
                            backgroundColor: 'var(--bg-surface)',
                            color: 'var(--text-secondary)',
                            border: '1px solid var(--border-subtle)',
                          }}
                        >
                          {c}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>

        {/* Modal Footer */}
        <div
          style={{
            padding: '12px 20px',
            backgroundColor: 'var(--bg-canvas)',
            borderTop: '1px solid var(--border-subtle)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
            Prepared Spells:{' '}
            <strong style={{ color: 'var(--accent-cyan)' }}>
              {character.known_spells.length}
            </strong>
          </div>
          <button
            type="button"
            className="btn btn-primary"
            onClick={onClose}
            style={{ fontSize: '12px', padding: '6px 18px' }}
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
};
