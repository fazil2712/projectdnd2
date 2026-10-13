import React, { useState, useEffect } from 'react';
import { Shield, RotateCcw, Flame, Compass, PlusCircle, Sword } from 'lucide-react';
import {
  Character,
  NarrativeEntry,
  CheckRequestData,
  CheckResolution,
  DamageResolution,
} from './types/game';
import { CharacterSheet } from './components/CharacterSheet';
import { NarrativeLog } from './components/NarrativeLog';
import { ActionInput } from './components/ActionInput';
import { CheckModal } from './components/CheckModal';
import { ModelSelector } from './components/ModelSelector';
import { CampaignSetupModal } from './components/CampaignSetupModal';
import './styles/theme.css';

export const App: React.FC = () => {
  const [character, setCharacter] = useState<Character | null>(null);
  const [campaignName, setCampaignName] = useState<string>('Shadows over Cragmaw');
  const [locationName, setLocationName] = useState<string>('The Weeping Maw');
  const [activeModel, setActiveModel] = useState<string>('llama3.1:8b');
  const [mobileTab, setMobileTab] = useState<'adventure' | 'character'>('adventure');

  const [entries, setEntries] = useState<NarrativeEntry[]>(() => {
    try {
      const saved = localStorage.getItem('dnd_saved_entries');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) return parsed;
      }
    } catch (e) {}
    return [];
  });
  const [streamingText, setStreamingText] = useState<string>('');
  const [isStreaming, setIsStreaming] = useState<boolean>(false);

  const [activeCheck, setActiveCheck] = useState<CheckRequestData | null>(null);
  const [rollOutcome, setRollOutcome] = useState<{
    resolution: CheckResolution;
    damage?: DamageResolution;
  } | null>(null);
  const [rollError, setRollError] = useState<string | null>(null);
  const [pendingPlayerAction, setPendingPlayerAction] = useState<string>('');
  const [isRolling, setIsRolling] = useState<boolean>(false);
  const [isSetupOpen, setIsSetupOpen] = useState<boolean>(false);

  // Sync entries to localStorage whenever they change
  useEffect(() => {
    if (entries.length > 0) {
      try {
        localStorage.setItem('dnd_saved_entries', JSON.stringify(entries));
      } catch (e) {}
    }
  }, [entries]);

  // Initial State Fetch
  const fetchGameState = async () => {
    try {
      const res = await fetch('/api/game/state');
      if (res.ok) {
        const data = await res.json();
        setCharacter(data.character);
        setCampaignName(data.campaign_name || 'D&D 5e Adventure');
        if (data.location) {
          setLocationName(typeof data.location === 'string' ? data.location : (data.location.name || ''));
        }
        if (data.active_model) {
          setActiveModel(data.active_model);
        }

        // Restore persistent chat history from backend if present
        if (data.chat_history && Array.isArray(data.chat_history) && data.chat_history.length > 0) {
          setEntries(data.chat_history);
        } else {
          setEntries((prev) => {
            if (prev.length > 0) return prev;
            return [
              {
                id: 'init-1',
                role: 'dm',
                content:
                  'Cold twilight hangs heavy over the foothills of the Neverwinter Wood. ' +
                  'Before you, veiled behind a curtain of dripping stalactites, the cavernous mouth of the Weeping Maw opens into pitch-black subterranean depths. ' +
                  'Forty feet ahead near the threshold, a cowardly goblin sentry fidgets beneath a makeshift leather canopy, while a hulking bugbear guard rests lazily upon a wooden crate, sharpening a notched blade.\n\n' +
                  'The damp moss silences your footsteps, but the darkness ahead is treacherous. What do you do?',
                timestamp: 'Prologue',
              },
            ];
          });
        }

        // Restore pending check state across page reloads
        if (data.pending_check && data.pending_check.check) {
          setActiveCheck(data.pending_check.check);
          setPendingPlayerAction(data.pending_check.action_text || '');
          setRollOutcome(null);
          setRollError(null);
          setIsRolling(false);
          if (data.pending_check.pre_text) {
            setEntries((prev) => {
              const hasPre = prev.some((e) => e.content === data.pending_check.pre_text);
              const toAdd: NarrativeEntry[] = [];
              if (data.pending_check.action_text && !prev.some((e) => e.content === data.pending_check.action_text)) {
                toAdd.push({
                  id: `player-restored-${Date.now()}`,
                  role: 'player',
                  content: data.pending_check.action_text,
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                });
              }
              if (!hasPre && data.pending_check.pre_text) {
                toAdd.push({
                  id: `dm-pre-restored-${Date.now()}`,
                  role: 'dm',
                  content: data.pending_check.pre_text,
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                });
              }
              return toAdd.length > 0 ? [...prev, ...toAdd] : prev;
            });
          }
        }
      }
    } catch (err) {
      console.error('Failed to load initial state:', err);
    }
  };

  useEffect(() => {
    fetchGameState();
  }, []);

  const handleSelectModel = async (modelId: string) => {
    setActiveModel(modelId);
    try {
      await fetch('/api/models/select', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model: modelId }),
      });
    } catch (err) {
      console.error('Failed to select model:', err);
    }
  };

  // Submit Player Action -> SSE Stream
  const handleSubmitAction = async (actionText: string) => {
    if (isStreaming || activeCheck) return;

    // Add Player Entry
    const playerEntry: NarrativeEntry = {
      id: `player-${Date.now()}`,
      role: 'player',
      content: actionText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
    setEntries((prev) => [...prev, playerEntry]);
    setPendingPlayerAction(actionText);
    setIsStreaming(true);
    setStreamingText('');

    try {
      const response = await fetch('/api/game/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: actionText, model: activeModel }),
      });

      if (!response.body) {
        setIsStreaming(false);
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let currentEvent = 'token';
      let buffer = '';
      let accumulatedDmText = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith('event:')) {
            currentEvent = trimmed.replace('event:', '').trim();
          } else if (trimmed.startsWith('data:')) {
            const jsonStr = trimmed.replace('data:', '').trim();
            if (!jsonStr) continue;

            try {
              const data = JSON.parse(jsonStr);

              if (currentEvent === 'token') {
                accumulatedDmText += data.content || '';
                setStreamingText((prev) => prev + (data.content || ''));
              } else if (currentEvent === 'check_required') {
                setActiveCheck(data.check);
                setRollOutcome(null);
                setRollError(null);
                setIsRolling(false);
                setIsStreaming(false);
                if (accumulatedDmText.trim()) {
                  const dmEntry: NarrativeEntry = {
                    id: `dm-pre-${Date.now()}`,
                    role: 'dm',
                    content: accumulatedDmText.trim(),
                    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                  };
                  setEntries((prev) => [...prev, dmEntry]);
                }
                setStreamingText('');
                return;
              } else if (currentEvent === 'action_rejected') {
                const rejEntry: NarrativeEntry = {
                  id: `rej-${Date.now()}`,
                  role: 'rejection',
                  content: data.rejection.reason,
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                };
                setEntries((prev) => [...prev, rejEntry]);
              } else if (currentEvent === 'item_granted') {
                if (data.character) setCharacter(data.character);
                const sysEntry: NarrativeEntry = {
                  id: `item-grant-${Date.now()}`,
                  role: 'system',
                  content: `Item Acquired: ${data.item.name}`,
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                };
                setEntries((prev) => [...prev, sysEntry]);
              } else if (currentEvent === 'item_consumed') {
                if (data.character) setCharacter(data.character);
                const sysEntry: NarrativeEntry = {
                  id: `item-consume-${Date.now()}`,
                  role: 'system',
                  content: data.summary,
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                };
                setEntries((prev) => [...prev, sysEntry]);
              } else if (currentEvent === 'level_up') {
                if (data.character) setCharacter(data.character);
                const sysEntry: NarrativeEntry = {
                  id: `level-up-${Date.now()}`,
                  role: 'system',
                  content: `Level Up! Reached Level ${data.level_up.level}. ${data.level_up.notes?.join(', ') || ''}`,
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                };
                setEntries((prev) => [...prev, sysEntry]);
              } else if (currentEvent === 'spell_learned') {
                if (data.character) setCharacter(data.character);
                const sysEntry: NarrativeEntry = {
                  id: `spell-learned-${Date.now()}`,
                  role: 'system',
                  content: `✨ Learned Spell: ${data.spell.name} (Level ${data.spell.level})${data.reason ? ` - ${data.reason}` : ''}`,
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                };
                setEntries((prev) => [...prev, sysEntry]);
              } else if (currentEvent === 'location_changed') {
                if (data.location?.name) setLocationName(data.location.name);
                const locEntry: NarrativeEntry = {
                  id: `loc-${Date.now()}`,
                  role: 'system',
                  content: `Discovered: ${data.location.name}`,
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                  metadata: { location: data.location },
                };
                setEntries((prev) => [...prev, locEntry]);
              } else if (currentEvent === 'npc_updated') {
                const npcEntry: NarrativeEntry = {
                  id: `npc-${Date.now()}`,
                  role: 'system',
                  content: `NPC: ${data.npc.name} (${data.npc.role || 'Inhabitant'})`,
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                  metadata: { npc: data.npc },
                };
                setEntries((prev) => [...prev, npcEntry]);
              } else if (currentEvent === 'story_progress') {
                const storyEntry: NarrativeEntry = {
                  id: `story-${Date.now()}`,
                  role: 'system',
                  content: `Story Progress: Act ${data.act} (Tension: ${data.tension_clock}/10)`,
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                  metadata: { story_progress: data },
                };
                setEntries((prev) => [...prev, storyEntry]);
              } else if (currentEvent === 'encounter_started') {
                const encEntry: NarrativeEntry = {
                  id: `encounter-${Date.now()}`,
                  role: 'system',
                  content: `Encounter Started: ${data.enemy.name}`,
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                  metadata: { encounter: data.enemy },
                };
                setEntries((prev) => [...prev, encEntry]);
              } else if (currentEvent === 'enemy_attack_resolved') {
                if (data.character) setCharacter(data.character);
                const atkEntry: NarrativeEntry = {
                  id: `enemy-atk-${Date.now()}`,
                  role: 'system',
                  content: data.attack.summary,
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                  metadata: { enemy_attack: data.attack },
                };
                setEntries((prev) => [...prev, atkEntry]);
              } else if (currentEvent === 'player_damaged') {
                if (data.character) setCharacter(data.character);
                const dmgEntry: NarrativeEntry = {
                  id: `player-dmg-${Date.now()}`,
                  role: 'system',
                  content: `Took ${data.damage.amount} ${data.damage.damage_type} damage: ${data.damage.reason}`,
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                  metadata: { player_damage: data.damage },
                };
                setEntries((prev) => [...prev, dmgEntry]);
              } else if (currentEvent === 'rest_resolved') {
                if (data.character) setCharacter(data.character);
                const restEntry: NarrativeEntry = {
                  id: `rest-${Date.now()}`,
                  role: 'system',
                  content: data.rest.summary || `Rest Completed: ${data.rest.rest_type === 'long' ? 'Long Rest' : 'Short Rest'}`,
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                  metadata: { rest: data.rest },
                };
                setEntries((prev) => [...prev, restEntry]);
              } else if (currentEvent === 'spell_cast_resolved') {
                if (data.character) setCharacter(data.character);
                const scEntry: NarrativeEntry = {
                  id: `spell-cast-${Date.now()}`,
                  role: 'system',
                  content: data.spell_cast.summary,
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                  metadata: { spell_cast: data.spell_cast },
                };
                setEntries((prev) => [...prev, scEntry]);
              } else if (currentEvent === 'condition_updated') {
                if (data.character) setCharacter(data.character);
                const condEntry: NarrativeEntry = {
                  id: `cond-${Date.now()}`,
                  role: 'system',
                  content: `Condition ${data.update.action === 'remove' ? 'Removed' : 'Afflicted'}: ${data.update.condition}${data.update.reason ? ` (${data.update.reason})` : ''}`,
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                  metadata: { condition: data.update },
                };
                setEntries((prev) => [...prev, condEntry]);
              } else if (currentEvent === 'done') {
                if (accumulatedDmText.trim()) {
                  const dmEntry: NarrativeEntry = {
                    id: `dm-${Date.now()}`,
                    role: 'dm',
                    content: accumulatedDmText.trim(),
                    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                  };
                  setEntries((prev) => [...prev, dmEntry]);
                }
                setStreamingText('');
              }
            } catch {
              // Non-JSON line
            }
          }
        }
      }
    } catch (err) {
      console.error('Error in action stream:', err);
    } finally {
      setIsStreaming(false);
    }
  };

  // Resolve Interrupted Check
  const handleResolveCheck = async (advantage: boolean, disadvantage: boolean) => {
    if (!activeCheck) return;
    setIsRolling(true);
    setRollError(null);

    try {
      const response = await fetch('/api/game/resolve-check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          check_type: activeCheck.type,
          target: activeCheck.target,
          dc: activeCheck.dc,
          modifier: activeCheck.modifier,
          advantage,
          disadvantage,
          player_action: pendingPlayerAction,
          model: activeModel,
        }),
      });

      if (!response.ok) {
        let errMsg = 'Failed to resolve check with the deterministic engine.';
        try {
          const errData = await response.json();
          errMsg = errData.detail || errData.message || errMsg;
        } catch (e) {}
        setRollError(errMsg);
        setIsRolling(false);
        return;
      }

      if (!response.body) {
        setIsRolling(false);
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let currentEvent = 'token';
      let buffer = '';
      let accumulatedContinuation = '';

      setIsStreaming(true);
      setStreamingText('');

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith('event:')) {
            currentEvent = trimmed.replace('event:', '').trim();
          } else if (trimmed.startsWith('data:')) {
            const jsonStr = trimmed.replace('data:', '').trim();
            if (!jsonStr) continue;

            try {
              const data = JSON.parse(jsonStr);

              if (currentEvent === 'roll_resolved') {
                const outcome = {
                  resolution: data.check_result as CheckResolution,
                  damage: data.damage_info as DamageResolution,
                };
                if (data.character) setCharacter(data.character);
                setRollOutcome(outcome);
                setIsRolling(false);
                setRollError(null);

                // Post mechanical roll result entry into permanent chat history
                const rollEntry: NarrativeEntry = {
                  id: `roll-${Date.now()}`,
                  role: 'system',
                  content: data.enemy_status
                    ? `${data.check_result.mechanical_summary} • ${data.enemy_status}`
                    : data.check_result.mechanical_summary,
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                  metadata: {
                    roll: outcome.resolution,
                    damage: outcome.damage,
                  },
                };
                setEntries((prev) => [...prev, rollEntry]);
              } else if (currentEvent === 'token') {
                accumulatedContinuation += data.content || '';
                setStreamingText((prev) => prev + (data.content || ''));
              } else if (currentEvent === 'check_required') {
                // Chained check interrupt during continuation stream
                setActiveCheck(data.check);
                setRollOutcome(null);
                setRollError(null);
                setIsRolling(false);
                setIsStreaming(false);
                if (accumulatedContinuation.trim()) {
                  const dmEntry: NarrativeEntry = {
                    id: `dm-chain-${Date.now()}`,
                    role: 'dm',
                    content: accumulatedContinuation.trim(),
                    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                  };
                  setEntries((prev) => [...prev, dmEntry]);
                }
                setStreamingText('');
                return;
              } else if (currentEvent === 'item_granted') {
                if (data.character) setCharacter(data.character);
                const sysEntry: NarrativeEntry = {
                  id: `item-grant-${Date.now()}`,
                  role: 'system',
                  content: `Item Acquired: ${data.item.name}`,
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                };
                setEntries((prev) => [...prev, sysEntry]);
              } else if (currentEvent === 'item_consumed') {
                if (data.character) setCharacter(data.character);
                const sysEntry: NarrativeEntry = {
                  id: `item-consume-${Date.now()}`,
                  role: 'system',
                  content: data.summary,
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                };
                setEntries((prev) => [...prev, sysEntry]);
              } else if (currentEvent === 'level_up') {
                if (data.character) setCharacter(data.character);
                const sysEntry: NarrativeEntry = {
                  id: `level-up-${Date.now()}`,
                  role: 'system',
                  content: `Level Up! Reached Level ${data.level_up.level}. ${data.level_up.notes?.join(', ') || ''}`,
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                };
                setEntries((prev) => [...prev, sysEntry]);
              } else if (currentEvent === 'spell_learned') {
                if (data.character) setCharacter(data.character);
                const sysEntry: NarrativeEntry = {
                  id: `spell-learned-${Date.now()}`,
                  role: 'system',
                  content: `✨ Learned Spell: ${data.spell.name} (Level ${data.spell.level})${data.reason ? ` - ${data.reason}` : ''}`,
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                };
                setEntries((prev) => [...prev, sysEntry]);
              } else if (currentEvent === 'location_changed') {
                if (data.location?.name) setLocationName(data.location.name);
                const locEntry: NarrativeEntry = {
                  id: `loc-${Date.now()}`,
                  role: 'system',
                  content: `Discovered: ${data.location.name}`,
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                  metadata: { location: data.location },
                };
                setEntries((prev) => [...prev, locEntry]);
              } else if (currentEvent === 'npc_updated') {
                const npcEntry: NarrativeEntry = {
                  id: `npc-${Date.now()}`,
                  role: 'system',
                  content: `NPC: ${data.npc.name} (${data.npc.role || 'Inhabitant'})`,
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                  metadata: { npc: data.npc },
                };
                setEntries((prev) => [...prev, npcEntry]);
              } else if (currentEvent === 'story_progress') {
                const storyEntry: NarrativeEntry = {
                  id: `story-${Date.now()}`,
                  role: 'system',
                  content: `Story Progress: Act ${data.act} (Tension: ${data.tension_clock}/10)`,
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                  metadata: { story_progress: data },
                };
                setEntries((prev) => [...prev, storyEntry]);
              } else if (currentEvent === 'encounter_started') {
                const encEntry: NarrativeEntry = {
                  id: `encounter-${Date.now()}`,
                  role: 'system',
                  content: `Encounter Started: ${data.enemy.name}`,
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                  metadata: { encounter: data.enemy },
                };
                setEntries((prev) => [...prev, encEntry]);
              } else if (currentEvent === 'enemy_attack_resolved') {
                if (data.character) setCharacter(data.character);
                const atkEntry: NarrativeEntry = {
                  id: `enemy-atk-${Date.now()}`,
                  role: 'system',
                  content: data.attack.summary,
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                  metadata: { enemy_attack: data.attack },
                };
                setEntries((prev) => [...prev, atkEntry]);
              } else if (currentEvent === 'player_damaged') {
                if (data.character) setCharacter(data.character);
                const dmgEntry: NarrativeEntry = {
                  id: `player-dmg-${Date.now()}`,
                  role: 'system',
                  content: `Took ${data.damage.amount} ${data.damage.damage_type} damage: ${data.damage.reason}`,
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                  metadata: { player_damage: data.damage },
                };
                setEntries((prev) => [...prev, dmgEntry]);
              } else if (currentEvent === 'rest_resolved') {
                if (data.character) setCharacter(data.character);
                const restEntry: NarrativeEntry = {
                  id: `rest-${Date.now()}`,
                  role: 'system',
                  content: data.rest.summary || `Rest Completed: ${data.rest.rest_type === 'long' ? 'Long Rest' : 'Short Rest'}`,
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                  metadata: { rest: data.rest },
                };
                setEntries((prev) => [...prev, restEntry]);
              } else if (currentEvent === 'spell_cast_resolved') {
                if (data.character) setCharacter(data.character);
                const scEntry: NarrativeEntry = {
                  id: `spell-cast-${Date.now()}`,
                  role: 'system',
                  content: data.spell_cast.summary,
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                  metadata: { spell_cast: data.spell_cast },
                };
                setEntries((prev) => [...prev, scEntry]);
              } else if (currentEvent === 'condition_updated') {
                if (data.character) setCharacter(data.character);
                const condEntry: NarrativeEntry = {
                  id: `cond-${Date.now()}`,
                  role: 'system',
                  content: `Condition ${data.update.action === 'remove' ? 'Removed' : 'Afflicted'}: ${data.update.condition}${data.update.reason ? ` (${data.update.reason})` : ''}`,
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                  metadata: { condition: data.update },
                };
                setEntries((prev) => [...prev, condEntry]);
              } else if (currentEvent === 'done') {
                if (accumulatedContinuation.trim()) {
                  const dmEntry: NarrativeEntry = {
                    id: `dm-res-${Date.now()}`,
                    role: 'dm',
                    content: accumulatedContinuation.trim(),
                    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                  };
                  setEntries((prev) => [...prev, dmEntry]);
                }
                setStreamingText('');
              }
            } catch {
              // Non-JSON line
            }
          }
        }
      }

      // Refresh character sheet in case damage/slots changed
      await fetchGameState();
    } catch (err: any) {
      console.error('Error resolving check:', err);
      setRollError(err?.message || 'Network error resolving check');
    } finally {
      setIsRolling(false);
      setIsStreaming(false);
    }
  };

  const handleProceedFromCheck = () => {
    setActiveCheck(null);
    setRollOutcome(null);
    setRollError(null);
  };

  // State Updates
  const handleModifyHp = async (delta: number) => {
    try {
      const res = await fetch('/api/game/character/modify-hp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ delta }),
      });
      if (res.ok) {
        const data = await res.json();
        setCharacter(data.character);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleToggleSlot = async (level: number, slotIndex: number) => {
    try {
      const res = await fetch('/api/game/character/toggle-slot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ level, slot_index: slotIndex }),
      });
      if (res.ok) {
        const data = await res.json();
        setCharacter(data.character);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleToggleItem = async (itemId: string) => {
    try {
      const res = await fetch('/api/game/character/toggle-item', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item_id: itemId }),
      });
      if (res.ok) {
        const data = await res.json();
        setCharacter(data.character);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleResetGame = async () => {
    if (confirm('Reset campaign and restore character to default state?')) {
      try {
        localStorage.removeItem('dnd_saved_entries');
      } catch (e) {}
      setEntries([]);
      await fetch('/api/game/reset', { method: 'POST' });
      await fetchGameState();
    }
  };

  const handleCampaignCreated = (data: any) => {
    setCharacter(data.character);
    setCampaignName(data.campaign_name);
    setLocationName(data.location_name);
    const newEntry: NarrativeEntry = {
      id: `init-${Date.now()}`,
      role: 'dm',
      content: data.opening_narrative,
      timestamp: 'Prologue',
    };
    setEntries([newEntry]);
    try {
      localStorage.setItem('dnd_saved_entries', JSON.stringify([newEntry]));
    } catch (e) {}
  };

  return (
    <div className="app-layout">
      {/* Top Header */}
      <header className="app-header">
        <div className="brand">
          <Flame size={20} className="brand-icon" />
          <span className="brand-title">D&amp;D 5e AI DM</span>
          <span className="brand-badge">5e Core</span>
        </div>

        <div className="header-actions">
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => setIsSetupOpen(true)}
            style={{ fontSize: '12px', padding: '6px 10px' }}
            title="Create New Campaign & Character"
          >
            <Compass size={14} color="var(--accent-gold)" />
            <span className="btn-label-desktop">New Campaign</span>
          </button>

          <ModelSelector activeModel={activeModel} onSelectModel={handleSelectModel} />

          <button
            type="button"
            className="btn btn-ghost"
            onClick={handleResetGame}
            title="Reset Campaign State"
            style={{ fontSize: '12px', padding: '6px 8px' }}
          >
            <RotateCcw size={14} />
            <span className="btn-label-desktop">Reset</span>
          </button>
        </div>
      </header>

      {/* Mobile Segmented Switcher (Shown only on mobile viewports) */}
      <nav className="mobile-tab-bar" aria-label="View Switcher">
        <button
          type="button"
          className={`mobile-tab-btn ${mobileTab === 'adventure' ? 'active' : ''}`}
          onClick={() => setMobileTab('adventure')}
        >
          <Sword size={15} />
          <span>Adventure</span>
        </button>
        <button
          type="button"
          className={`mobile-tab-btn ${mobileTab === 'character' ? 'active' : ''}`}
          onClick={() => setMobileTab('character')}
        >
          <Shield size={15} />
          <span>Character</span>
          {character && (
            <span
              className="mobile-hp-pill"
              style={{
                color:
                  character.current_hp > character.max_hp * 0.5
                    ? 'var(--accent-green)'
                    : character.current_hp > character.max_hp * 0.2
                    ? 'var(--accent-gold)'
                    : 'var(--accent-crimson)',
              }}
            >
              {character.current_hp}/{character.max_hp} HP
            </span>
          )}
        </button>
      </nav>

      {/* Main Layout Grid */}
      <div className="main-grid">
        {/* Left: Character Sheet */}
        <aside className={`sidebar-panel ${mobileTab !== 'character' ? 'mobile-hidden' : ''}`}>
          <CharacterSheet
            character={character}
            onModifyHp={handleModifyHp}
            onToggleSlot={handleToggleSlot}
            onToggleItem={handleToggleItem}
            onCharacterUpdated={(updatedChar) => setCharacter(updatedChar)}
            onSendAction={handleSubmitAction}
            isStreaming={isStreaming}
            hasActiveCheck={activeCheck !== null}
          />
        </aside>

        {/* Right: Narrative Feed + Action Bar */}
        <main className={`adventure-panel ${mobileTab !== 'adventure' ? 'mobile-hidden' : ''}`}>
          <NarrativeLog
            entries={entries}
            streamingText={streamingText}
            isStreaming={isStreaming}
            campaignName={campaignName}
            locationName={locationName}
          />

          <ActionInput
            onSubmitAction={handleSubmitAction}
            isDisabled={isStreaming || activeCheck !== null}
          />
        </main>
      </div>

      {/* Check Interrupt Modal */}
      {activeCheck && (
        <CheckModal
          checkData={activeCheck}
          onResolve={handleResolveCheck}
          isRolling={isRolling}
          rollOutcome={rollOutcome}
          rollError={rollError}
          onProceed={handleProceedFromCheck}
          onRetry={() => handleResolveCheck(false, false)}
        />
      )}

      {/* Campaign & Character Setup Modal */}
      <CampaignSetupModal
        isOpen={isSetupOpen}
        onClose={() => setIsSetupOpen(false)}
        onCampaignCreated={handleCampaignCreated}
      />

    </div>
  );
};

