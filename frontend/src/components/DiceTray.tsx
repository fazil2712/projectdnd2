import React from 'react';
import { Sparkles, Skull, CheckCircle, XCircle } from 'lucide-react';
import { CheckResolution, DamageResolution } from '../types/game';

interface DiceTrayProps {
  resolution: CheckResolution;
  damage?: DamageResolution;
}

export const DiceTray: React.FC<DiceTrayProps> = ({ resolution, damage }) => {
  const { roll, success, dc, modifier, resolved_name, crit_note, margin } = resolution;

  const isAdv = roll.advantage;
  const isDis = roll.disadvantage;
  const isCritHit = roll.is_critical_success;
  const isCritFail = roll.is_critical_failure;

  return (
    <div
      className="roll-outcome-card"
      style={{
        margin: '12px 0',
        padding: '14px 18px',
        backgroundColor: 'var(--bg-card)',
        border: isCritHit
          ? '2px solid var(--accent-gold)'
          : isCritFail
          ? '2px solid var(--accent-crimson)'
          : '1px solid var(--border-accent)',
        borderRadius: 'var(--radius-md)',
        boxShadow: isCritHit ? 'var(--shadow-glow-gold)' : isCritFail ? 'var(--shadow-glow-crimson)' : 'var(--shadow-card)',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontWeight: 700, fontSize: '13px', color: 'var(--text-primary)', textTransform: 'uppercase' }}>
            {resolved_name}
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
            Target DC/AC: {dc}
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          {success ? (
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                color: 'var(--accent-green)',
                fontWeight: 700,
                fontSize: '13px',
              }}
            >
              <CheckCircle size={16} /> SUCCESS
            </span>
          ) : (
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                color: 'var(--accent-crimson)',
                fontWeight: 700,
                fontSize: '13px',
              }}
            >
              <XCircle size={16} /> FAILURE
            </span>
          )}
        </div>
      </div>

      {/* Main Dice Visual & Arithmetic */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
        {/* Dice Visual Hexagon/Badge */}
        <div
          style={{
            position: 'relative',
            width: '54px',
            height: '54px',
            backgroundColor: isCritHit ? 'var(--accent-gold)' : isCritFail ? 'var(--accent-crimson)' : 'var(--bg-surface)',
            border: '2px solid var(--border-accent)',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}
        >
          <span
            style={{
              fontSize: '22px',
              fontWeight: 800,
              fontFamily: 'var(--font-display)',
              color: isCritHit || isCritFail ? '#0c0e12' : 'var(--accent-gold)',
            }}
          >
            {roll.selected_raw}
          </span>
          {isCritHit && (
            <div style={{ position: 'absolute', top: -6, right: -6 }}>
              <Sparkles size={16} color="var(--accent-gold)" />
            </div>
          )}
          {isCritFail && (
            <div style={{ position: 'absolute', top: -6, right: -6 }}>
              <Skull size={16} color="var(--accent-crimson)" />
            </div>
          )}
        </div>

        {/* Breakdown Text */}
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
            {isAdv && (
              <span style={{ color: 'var(--accent-green)', fontWeight: 600, marginRight: '6px' }}>
                [Advantage: rolled {roll.raw_rolls.join(', ')}]
              </span>
            )}
            {isDis && (
              <span style={{ color: 'var(--accent-crimson)', fontWeight: 600, marginRight: '6px' }}>
                [Disadvantage: rolled {roll.raw_rolls.join(', ')}]
              </span>
            )}
            <span>
              d20 ({roll.selected_raw}) {modifier >= 0 ? `+ ${modifier}` : `- ${Math.abs(modifier)}`} ={' '}
              <strong style={{ color: 'var(--text-primary)', fontSize: '15px' }}>{roll.total}</strong>
            </span>
          </div>

          <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
            {crit_note && <strong style={{ color: isCritHit ? 'var(--accent-gold)' : 'var(--accent-crimson)', marginRight: '6px' }}>{crit_note}</strong>}
            <span>Margin: {margin >= 0 ? `+${margin}` : `${margin}`}</span>
          </div>
        </div>
      </div>

      {/* Damage Details if attack hit */}
      {damage && (
        <div
          style={{
            marginTop: '10px',
            paddingTop: '8px',
            borderTop: '1px solid var(--border-subtle)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            fontSize: '12px',
          }}
        >
          <span style={{ color: 'var(--text-secondary)' }}>
            ⚔️ <strong>{damage.weapon_name}</strong> Damage:
          </span>
          <span style={{ color: 'var(--accent-crimson)', fontWeight: 700 }}>
            {damage.summary}
          </span>
        </div>
      )}
    </div>
  );
};
