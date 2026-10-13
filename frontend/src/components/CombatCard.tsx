import React from 'react';
import { Sword, Shield, Heart, Skull, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';
import { EnemyAttackData, PlayerDamageData, EnemyData } from '../types/game';

interface EnemyAttackCardProps {
  attack: EnemyAttackData;
}

export const EnemyAttackCard: React.FC<EnemyAttackCardProps> = ({ attack }) => {
  const {
    attacker,
    attack_bonus,
    target_ac,
    roll,
    hit,
    is_critical_hit,
    is_critical_miss,
    damage_total,
    damage_type,
    damage_breakdown,
    current_hp,
    max_hp,
    is_unconscious,
  } = attack;

  return (
    <div
      className="roll-outcome-card"
      style={{
        margin: '10px 0',
        padding: '12px 16px',
        backgroundColor: 'var(--bg-card)',
        border: is_critical_hit
          ? '2px solid var(--accent-crimson)'
          : hit
          ? '1px solid var(--accent-crimson)'
          : '1px solid var(--border-accent)',
        borderRadius: 'var(--radius-md)',
        boxShadow: is_critical_hit ? 'var(--shadow-glow-crimson)' : 'var(--shadow-card)',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Sword size={15} color="var(--accent-crimson)" />
          <span style={{ fontWeight: 700, fontSize: '13px', color: 'var(--text-primary)', textTransform: 'uppercase' }}>
            {attacker} Attacks You
          </span>
          <span
            style={{
              fontSize: '11px',
              padding: '2px 6px',
              backgroundColor: 'var(--bg-surface)',
              borderRadius: '3px',
              color: 'var(--text-secondary)',
              border: '1px solid var(--border-subtle)',
            }}
          >
            Your AC: {target_ac}
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          {hit ? (
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                color: 'var(--accent-crimson)',
                fontWeight: 700,
                fontSize: '12px',
              }}
            >
              <CheckCircle size={15} /> {is_critical_hit ? 'CRITICAL HIT' : 'HIT'}
            </span>
          ) : (
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                color: 'var(--accent-green)',
                fontWeight: 700,
                fontSize: '12px',
              }}
            >
              <XCircle size={15} /> {is_critical_miss ? 'FUMBLE (MISS)' : 'MISS'}
            </span>
          )}
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '14px', flexWrap: 'wrap' }}>
        {/* Die Visual */}
        <div
          style={{
            position: 'relative',
            width: '46px',
            height: '46px',
            backgroundColor: is_critical_hit ? 'var(--accent-crimson)' : 'var(--bg-surface)',
            border: '2px solid var(--border-accent)',
            borderRadius: '10px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}
        >
          <span
            style={{
              fontSize: '20px',
              fontWeight: 800,
              fontFamily: 'var(--font-display)',
              color: is_critical_hit ? '#ffffff' : 'var(--text-primary)',
            }}
          >
            {roll.selected_raw}
          </span>
        </div>

        {/* Math & Damage Breakdown */}
        <div style={{ flex: 1, minWidth: '160px' }}>
          <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
            Attack Roll: d20({roll.selected_raw}) {attack_bonus >= 0 ? `+ ${attack_bonus}` : `- ${Math.abs(attack_bonus)}`} ={' '}
            <strong style={{ color: 'var(--text-primary)', fontSize: '14px' }}>{roll.total}</strong>
          </div>

          {hit && (
            <div style={{ marginTop: '4px', display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '12px', color: 'var(--accent-crimson)', fontWeight: 600 }}>
                💥 {damage_total} {damage_type} damage
              </span>
              {damage_breakdown && (
                <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                  ({damage_breakdown})
                </span>
              )}
            </div>
          )}
        </div>

        {/* Player Status Badge */}
        {hit && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 10px',
              backgroundColor: is_unconscious ? 'var(--accent-crimson-dim)' : 'var(--bg-surface)',
              borderRadius: 'var(--radius-sm)',
              border: is_unconscious ? '1px solid var(--accent-crimson)' : '1px solid var(--border-subtle)',
            }}
          >
            {is_unconscious ? <Skull size={15} color="var(--accent-crimson)" /> : <Heart size={15} color="var(--accent-crimson)" />}
            <span style={{ fontSize: '11px', fontWeight: 700, color: is_unconscious ? 'var(--accent-crimson)' : 'var(--text-secondary)' }}>
              {is_unconscious ? 'UNCONSCIOUS (0 HP)' : `HP: ${current_hp} / ${max_hp}`}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

interface HazardDamageCardProps {
  damage: PlayerDamageData;
}

export const HazardDamageCard: React.FC<HazardDamageCardProps> = ({ damage }) => {
  const { amount, damage_type, reason, current_hp, max_hp, is_unconscious } = damage;

  return (
    <div
      className="roll-outcome-card"
      style={{
        margin: '10px 0',
        padding: '12px 16px',
        backgroundColor: 'var(--bg-card)',
        border: '1px solid var(--accent-crimson)',
        borderRadius: 'var(--radius-md)',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <AlertTriangle size={15} color="var(--accent-crimson)" />
          <span style={{ fontWeight: 700, fontSize: '13px', color: 'var(--text-primary)', textTransform: 'uppercase' }}>
            Environmental Hazard / Trap
          </span>
        </div>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '3px 8px',
            backgroundColor: is_unconscious ? 'var(--accent-crimson-dim)' : 'var(--bg-surface)',
            borderRadius: 'var(--radius-sm)',
            border: is_unconscious ? '1px solid var(--accent-crimson)' : '1px solid var(--border-subtle)',
          }}
        >
          {is_unconscious ? <Skull size={14} color="var(--accent-crimson)" /> : <Heart size={14} color="var(--accent-crimson)" />}
          <span style={{ fontSize: '11px', fontWeight: 700, color: is_unconscious ? 'var(--accent-crimson)' : 'var(--text-secondary)' }}>
            {is_unconscious ? '0 HP' : `${current_hp} / ${max_hp} HP`}
          </span>
        </div>
      </div>

      <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '4px' }}>
        {reason}
      </div>

      <div style={{ fontSize: '13px', color: 'var(--accent-crimson)', fontWeight: 600 }}>
        Took {amount} {damage_type} damage
      </div>
    </div>
  );
};

interface EncounterBannerProps {
  enemy: EnemyData;
}

export const EncounterBanner: React.FC<EncounterBannerProps> = ({ enemy }) => {
  return (
    <div
      style={{
        margin: '10px 0',
        padding: '10px 14px',
        backgroundColor: 'var(--bg-card)',
        borderLeft: '3px solid var(--accent-crimson)',
        borderRadius: '0 var(--radius-sm) var(--radius-sm) 0',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '8px',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <Sword size={14} color="var(--accent-crimson)" />
        <span style={{ fontWeight: 700, fontSize: '12px', color: 'var(--text-primary)', textTransform: 'uppercase' }}>
          Engaged in Combat: {enemy.name}
        </span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '11px', color: 'var(--text-secondary)' }}>
        <span>HP: <strong style={{ color: 'var(--text-primary)' }}>{enemy.current_hp}/{enemy.max_hp}</strong></span>
        <span>AC: <strong style={{ color: 'var(--text-primary)' }}>{enemy.ac}</strong></span>
        <span>Atk: <strong style={{ color: 'var(--text-primary)' }}>+{enemy.attack_bonus}</strong> ({enemy.damage_formula})</span>
      </div>
    </div>
  );
};
