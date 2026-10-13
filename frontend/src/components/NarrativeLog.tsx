import React, { useEffect, useRef } from 'react';
import { User, Sparkles, AlertOctagon, Compass, MapPin, Users, Bookmark, Info } from 'lucide-react';
import { NarrativeEntry } from '../types/game';
import { DiceTray } from './DiceTray';
import { EnemyAttackCard, HazardDamageCard, EncounterBanner } from './CombatCard';

interface NarrativeLogProps {
  entries: NarrativeEntry[];
  streamingText: string;
  isStreaming: boolean;
  campaignName: string;
  locationName: string;
}

export const NarrativeLog: React.FC<NarrativeLogProps> = ({
  entries,
  streamingText,
  isStreaming,
  campaignName,
  locationName,
}) => {
  const scrollRef = useRef<HTMLDivElement>(null);
  const isAutoScroll = useRef<boolean>(true);

  const scrollToBottom = () => {
    if (isAutoScroll.current && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [entries, streamingText]);

  const handleScroll = () => {
    if (scrollRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;
      const atBottom = scrollHeight - (scrollTop + clientHeight) < 40;
      isAutoScroll.current = atBottom;
    }
  };

  return (
    <div
      ref={scrollRef}
      onScroll={handleScroll}
      className="narrative-scroll-area"
    >
      {/* Scene Header */}
      <div
        style={{
          textAlign: 'center',
          padding: '16px',
          borderBottom: '1px solid var(--border-subtle)',
          marginBottom: '8px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', color: 'var(--accent-gold)', marginBottom: '4px' }}>
          <Compass size={16} />
          <span style={{ fontSize: '11px', fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase' }}>
            {campaignName}
          </span>
        </div>
        <h1
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: '20px',
            fontWeight: 700,
            color: 'var(--text-primary)',
          }}
        >
          {locationName || 'The Adventure Begins'}
        </h1>
      </div>

      {/* Narrative Entries */}
      {entries.map((entry) => {
        if (entry.role === 'player') {
          return (
            <div
              key={entry.id}
              className="narrative-entry-anim"
              style={{
                alignSelf: 'flex-end',
                maxWidth: '85%',
                backgroundColor: 'var(--bg-card)',
                border: '1px solid var(--border-accent)',
                borderRadius: 'var(--radius-md) var(--radius-md) 0 var(--radius-md)',
                padding: '12px 16px',
                boxShadow: '0 2px 8px rgba(0, 0, 0, 0.25)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
                <User size={13} color="var(--accent-cyan)" />
                <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--accent-cyan)', textTransform: 'uppercase' }}>
                  You
                </span>
                <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
                  {entry.timestamp}
                </span>
              </div>
              <div style={{ fontSize: '14px', color: 'var(--text-primary)', lineHeight: 1.5 }}>
                {entry.content}
              </div>
            </div>
          );
        }

        if (entry.role === 'rejection') {
          return (
            <div
              key={entry.id}
              className="narrative-entry-anim"
              style={{
                alignSelf: 'stretch',
                backgroundColor: 'var(--accent-crimson-dim)',
                border: '1px solid var(--accent-crimson)',
                borderRadius: 'var(--radius-md)',
                padding: '14px 18px',
                display: 'flex',
                gap: '12px',
                alignItems: 'flex-start',
                boxShadow: '0 2px 8px rgba(217, 83, 79, 0.15)',
              }}
            >
              <AlertOctagon size={20} color="var(--accent-crimson)" style={{ flexShrink: 0, marginTop: '2px' }} />
              <div>
                <div style={{ fontWeight: 700, fontSize: '13px', color: 'var(--accent-crimson)', textTransform: 'uppercase', marginBottom: '2px' }}>
                  Action Rejected by Dungeon Master
                </div>
                <div style={{ fontSize: '13px', color: 'var(--text-primary)', lineHeight: 1.4 }}>
                  {entry.content}
                </div>
              </div>
            </div>
          );
        }

        if (entry.metadata?.roll) {
          return (
            <div key={entry.id} className="narrative-entry-anim" style={{ alignSelf: 'stretch' }}>
              <DiceTray resolution={entry.metadata.roll} damage={entry.metadata.damage} />
            </div>
          );
        }

        if (entry.metadata?.enemy_attack) {
          return (
            <div key={entry.id} className="narrative-entry-anim" style={{ alignSelf: 'stretch' }}>
              <EnemyAttackCard attack={entry.metadata.enemy_attack} />
            </div>
          );
        }

        if (entry.metadata?.player_damage) {
          return (
            <div key={entry.id} className="narrative-entry-anim" style={{ alignSelf: 'stretch' }}>
              <HazardDamageCard damage={entry.metadata.player_damage} />
            </div>
          );
        }

        if (entry.metadata?.encounter) {
          return (
            <div key={entry.id} className="narrative-entry-anim" style={{ alignSelf: 'stretch' }}>
              <EncounterBanner enemy={entry.metadata.encounter} />
            </div>
          );
        }

        if (entry.metadata?.location) {
          return (
            <div
              key={entry.id}
              className="narrative-entry-anim"
              style={{
                alignSelf: 'stretch',
                backgroundColor: 'var(--bg-card)',
                borderLeft: '3px solid var(--accent-cyan)',
                borderRadius: '0 var(--radius-sm) var(--radius-sm) 0',
                padding: '10px 14px',
                margin: '8px 0',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--accent-cyan)', marginBottom: '2px' }}>
                <MapPin size={14} />
                <span style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Location Discovered: {entry.metadata.location.name}
                </span>
                <span
                  style={{
                    fontSize: '10px',
                    padding: '1px 5px',
                    borderRadius: '3px',
                    backgroundColor: 'var(--bg-surface)',
                    color: 'var(--text-secondary)',
                    marginLeft: 'auto',
                  }}
                >
                  Threat: {entry.metadata.location.threat_level}
                </span>
              </div>
              {entry.metadata.location.description && (
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                  {entry.metadata.location.description}
                </div>
              )}
            </div>
          );
        }

        if (entry.metadata?.story_progress) {
          return (
            <div
              key={entry.id}
              className="narrative-entry-anim"
              style={{
                alignSelf: 'stretch',
                backgroundColor: 'var(--bg-card)',
                borderLeft: '3px solid var(--accent-gold)',
                borderRadius: '0 var(--radius-sm) var(--radius-sm) 0',
                padding: '10px 14px',
                margin: '8px 0',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--accent-gold)', marginBottom: '2px' }}>
                <Bookmark size={14} />
                <span style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Act {entry.metadata.story_progress.act} Progression · Villain Tension: {entry.metadata.story_progress.tension_clock}/10
                </span>
              </div>
              {entry.metadata.story_progress.milestone && (
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                  {entry.metadata.story_progress.milestone}
                </div>
              )}
            </div>
          );
        }

        if (entry.metadata?.npc) {
          return (
            <div
              key={entry.id}
              className="narrative-entry-anim"
              style={{
                alignSelf: 'stretch',
                backgroundColor: 'var(--bg-card)',
                borderLeft: '3px solid var(--accent-cyan)',
                borderRadius: '0 var(--radius-sm) var(--radius-sm) 0',
                padding: '10px 14px',
                margin: '8px 0',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--accent-cyan)', marginBottom: '2px' }}>
                <Users size={14} />
                <span style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  NPC Noted: {entry.metadata.npc.name} ({entry.metadata.npc.role || 'Inhabitant'})
                </span>
                <span
                  style={{
                    fontSize: '10px',
                    padding: '1px 5px',
                    borderRadius: '3px',
                    backgroundColor: 'var(--bg-surface)',
                    color: 'var(--text-secondary)',
                    textTransform: 'capitalize',
                    marginLeft: 'auto',
                  }}
                >
                  {entry.metadata.npc.attitude}
                </span>
              </div>
              {entry.metadata.npc.note && (
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                  {entry.metadata.npc.note}
                </div>
              )}
            </div>
          );
        }

        if (entry.role === 'system') {
          return (
            <div
              key={entry.id}
              className="narrative-entry-anim"
              style={{
                alignSelf: 'center',
                backgroundColor: 'var(--bg-card)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                padding: '8px 14px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                fontSize: '12px',
                color: 'var(--text-secondary)',
                margin: '6px 0',
              }}
            >
              <Info size={14} color="var(--accent-gold)" />
              <span>{entry.content}</span>
            </div>
          );
        }

        // Default: DM narrative
        return (
          <div
            key={entry.id}
            className="narrative-entry-anim"
            style={{
              alignSelf: 'flex-start',
              maxWidth: '92%',
              backgroundColor: 'var(--bg-surface)',
              borderLeft: '3px solid var(--accent-gold)',
              borderRadius: '0 var(--radius-md) var(--radius-md) 0',
              padding: '16px 20px',
              boxShadow: '0 2px 12px rgba(0, 0, 0, 0.3)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
              <Sparkles size={13} color="var(--accent-gold)" />
              <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--accent-gold)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Dungeon Master
              </span>
              <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
                {entry.timestamp}
              </span>
            </div>
            <div
              style={{
                fontFamily: 'var(--font-narrative)',
                fontSize: '15px',
                lineHeight: 1.7,
                color: 'var(--text-primary)',
                whiteSpace: 'pre-line',
              }}
            >
              {entry.content}
            </div>
          </div>
        );
      })}

      {/* Active Streaming Chunk */}
      {isStreaming && (
        <div
          className="narrative-entry-anim"
          style={{
            alignSelf: 'flex-start',
            maxWidth: '92%',
            backgroundColor: 'var(--bg-surface)',
            borderLeft: '3px solid var(--accent-gold)',
            borderRadius: '0 var(--radius-md) var(--radius-md) 0',
            padding: '16px 20px',
            boxShadow: '0 2px 12px rgba(0, 0, 0, 0.3)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
            <Sparkles size={13} color="var(--accent-gold)" />
            <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--accent-gold)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Dungeon Master (Narrating...)
            </span>
          </div>
          <div
            style={{
              fontFamily: 'var(--font-narrative)',
              fontSize: '15px',
              lineHeight: 1.7,
              color: 'var(--text-primary)',
              whiteSpace: 'pre-line',
            }}
          >
            {streamingText}
            <span
              style={{
                display: 'inline-block',
                width: '7px',
                height: '14px',
                backgroundColor: 'var(--accent-gold)',
                marginLeft: '4px',
                verticalAlign: 'middle',
                animation: 'pulse 1s infinite',
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
};
