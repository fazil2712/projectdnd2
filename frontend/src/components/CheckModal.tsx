import React, { useState, useEffect } from 'react';
import { Dices, ShieldAlert, Sparkles, Skull, CheckCircle2, XCircle, ArrowRight, AlertTriangle, RefreshCw } from 'lucide-react';
import { CheckRequestData, CheckResolution, DamageResolution } from '../types/game';

interface CheckModalProps {
  checkData: CheckRequestData;
  onResolve: (advantage: boolean, disadvantage: boolean) => void;
  isRolling: boolean;
  rollOutcome?: {
    resolution: CheckResolution;
    damage?: DamageResolution;
  } | null;
  rollError?: string | null;
  onProceed?: () => void;
  onRetry?: () => void;
}

export const CheckModal: React.FC<CheckModalProps> = ({
  checkData,
  onResolve,
  isRolling,
  rollOutcome,
  rollError,
  onProceed,
  onRetry,
}) => {
  const [rollMode, setRollMode] = useState<'normal' | 'advantage' | 'disadvantage'>('normal');
  const [tumblerValue, setTumblerValue] = useState<number>(10);

  const modifier = checkData.modifier ?? 0;
  const modStr = modifier >= 0 ? `+${modifier}` : `${modifier}`;

  // Suspense rolling number cycle
  useEffect(() => {
    if (isRolling && !rollOutcome) {
      const interval = setInterval(() => {
        setTumblerValue(Math.floor(Math.random() * 20) + 1);
      }, 70);
      return () => clearInterval(interval);
    }
  }, [isRolling, rollOutcome]);

  // Auto-proceed timer after roll outcome is revealed
  useEffect(() => {
    if (rollOutcome && onProceed) {
      const timer = setTimeout(() => {
        onProceed();
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [rollOutcome, onProceed]);

  const handleRoll = () => {
    const isAdv = rollMode === 'advantage';
    const isDis = rollMode === 'disadvantage';
    onResolve(isAdv, isDis);
  };

  const resolution = rollOutcome?.resolution;
  const roll = resolution?.roll;
  const isCritHit = roll?.is_critical_success;
  const isCritFail = roll?.is_critical_failure;
  const isSuccess = resolution?.success;

  return (
    <div className="modal-overlay">
      <div className="modal-card">
        {/* Header */}
        <div
          style={{
            padding: '16px 20px',
            backgroundColor: 'var(--bg-card)',
            borderBottom: '1px solid var(--border-subtle)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div
              style={{
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                backgroundColor: 'var(--accent-gold-dim)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--accent-gold)',
                border: '1px solid var(--border-gold)',
              }}
            >
              <ShieldAlert size={18} />
            </div>
            <div>
              <h2
                style={{
                  fontFamily: 'var(--font-display)',
                  fontSize: '15px',
                  fontWeight: 700,
                  fontStyle: 'normal',
                  color: 'var(--text-primary)',
                  letterSpacing: '0.04em',
                }}
              >
                {rollOutcome ? 'Outcome Resolved' : 'Check Required'}
              </h2>
              <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                {rollOutcome
                  ? 'Deterministic outcome calculated and recorded.'
                  : 'The Dungeon Master paused the action for mechanical resolution.'}
              </div>
            </div>
          </div>

          <span
            style={{
              fontSize: '12px',
              fontWeight: 700,
              padding: '2px 8px',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: 'var(--bg-surface)',
              border: '1px solid var(--border-gold)',
              color: 'var(--accent-gold)',
            }}
          >
            DC {checkData.dc}
          </span>
        </div>

        {/* Body Content */}
        <div style={{ padding: '20px' }}>
          {/* Error Recovery State */}
          {rollError ? (
            <div
              style={{
                padding: '16px',
                backgroundColor: 'var(--accent-crimson-dim)',
                border: '1px solid var(--accent-crimson)',
                borderRadius: 'var(--radius-md)',
                marginBottom: '16px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', color: 'var(--accent-crimson)', fontWeight: 700 }}>
                <AlertTriangle size={18} />
                <span>Resolution Error</span>
              </div>
              <p style={{ fontSize: '13px', color: 'var(--text-primary)', marginBottom: '14px', lineHeight: 1.4 }}>
                {rollError}
              </p>
              <button
                type="button"
                className="btn btn-danger"
                style={{ width: '100%', gap: '8px' }}
                onClick={onRetry || handleRoll}
              >
                <RefreshCw size={16} /> Retry Roll
              </button>
            </div>
          ) : isRolling && !rollOutcome ? (
            /* Rolling Suspense State */
            <div
              className="dice-tumbler"
              style={{
                padding: '30px 20px',
                textAlign: 'center',
                backgroundColor: 'var(--bg-card)',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border-accent)',
              }}
            >
              <div
                style={{
                  width: '72px',
                  height: '72px',
                  margin: '0 auto 16px auto',
                  borderRadius: '16px',
                  backgroundColor: 'var(--bg-surface)',
                  border: '2px solid var(--accent-gold)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: 'var(--shadow-glow-gold)',
                }}
              >
                <span
                  style={{
                    fontFamily: 'var(--font-display)',
                    fontSize: '32px',
                    fontWeight: 800,
                    color: 'var(--accent-gold)',
                  }}
                >
                  {tumblerValue}
                </span>
              </div>
              <div
                style={{
                  fontFamily: 'var(--font-display)',
                  fontSize: '15px',
                  fontWeight: 700,
                  color: 'var(--text-primary)',
                  marginBottom: '6px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                }}
              >
                <Dices size={18} className="dice-tumbler-icon" color="var(--accent-gold)" />
                Rolling 1d20 {modStr} vs DC {checkData.dc}...
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                Evaluating mechanical modifiers and deterministic rules.
              </div>
            </div>
          ) : rollOutcome && resolution && roll ? (
            /* Roll Outcome Reveal State */
            <div className="roll-outcome-card">
              {/* Outcome Banner */}
              <div
                style={{
                  padding: '12px 16px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: isSuccess ? 'var(--accent-green-dim)' : 'var(--accent-crimson-dim)',
                  border: `1px solid ${isSuccess ? 'var(--accent-green)' : 'var(--accent-crimson)'}`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: '16px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  {isSuccess ? (
                    <CheckCircle2 size={20} color="var(--accent-green)" />
                  ) : (
                    <XCircle size={20} color="var(--accent-crimson)" />
                  )}
                  <span
                    style={{
                      fontFamily: 'var(--font-display)',
                      fontWeight: 800,
                      fontSize: '15px',
                      color: isSuccess ? 'var(--accent-green)' : 'var(--accent-crimson)',
                      letterSpacing: '0.04em',
                    }}
                  >
                    {isCritHit
                      ? 'NATURAL 20 · CRITICAL SUCCESS'
                      : isCritFail
                      ? 'NATURAL 1 · CRITICAL FAILURE'
                      : isSuccess
                      ? 'SUCCESS'
                      : 'FAILURE'}
                  </span>
                </div>
                <span
                  style={{
                    fontSize: '12px',
                    fontWeight: 700,
                    color: 'var(--text-primary)',
                    padding: '2px 8px',
                    borderRadius: 'var(--radius-sm)',
                    backgroundColor: 'var(--bg-surface)',
                  }}
                >
                  {resolution.margin >= 0 ? `+${resolution.margin}` : `${resolution.margin}`} Margin
                </span>
              </div>

              {/* Main Dice Math Display */}
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '16px',
                  padding: '16px',
                  backgroundColor: 'var(--bg-card)',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--border-subtle)',
                  marginBottom: '16px',
                }}
              >
                <div
                  style={{
                    position: 'relative',
                    width: '60px',
                    height: '60px',
                    borderRadius: '14px',
                    backgroundColor: isCritHit ? 'var(--accent-gold)' : isCritFail ? 'var(--accent-crimson)' : 'var(--bg-surface)',
                    border: `2px solid ${isSuccess ? 'var(--accent-green)' : 'var(--accent-crimson)'}`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                    boxShadow: isCritHit ? 'var(--shadow-glow-gold)' : isCritFail ? 'var(--shadow-glow-crimson)' : 'none',
                  }}
                >
                  <span
                    style={{
                      fontFamily: 'var(--font-display)',
                      fontSize: '26px',
                      fontWeight: 800,
                      color: isCritHit || isCritFail ? '#0c0e12' : 'var(--text-primary)',
                    }}
                  >
                    {roll.selected_raw}
                  </span>
                  {isCritHit && (
                    <Sparkles size={16} color="var(--accent-gold)" style={{ position: 'absolute', top: -6, right: -6 }} />
                  )}
                  {isCritFail && (
                    <Skull size={16} color="var(--accent-crimson)" style={{ position: 'absolute', top: -6, right: -6 }} />
                  )}
                </div>

                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '14px', color: 'var(--text-primary)', marginBottom: '4px' }}>
                    <strong>{roll.selected_raw}</strong> (d20){' '}
                    {resolution.modifier >= 0 ? `+ ${resolution.modifier}` : `- ${Math.abs(resolution.modifier)}`} (Mod) ={' '}
                    <strong style={{ fontSize: '18px', color: isSuccess ? 'var(--accent-green)' : 'var(--accent-crimson)' }}>
                      {roll.total}
                    </strong>{' '}
                    vs DC {resolution.dc}
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                    {resolution.mechanical_summary}
                  </div>
                </div>
              </div>

              {/* Damage Info if available */}
              {rollOutcome.damage && (
                <div
                  style={{
                    padding: '10px 14px',
                    backgroundColor: 'var(--bg-surface)',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--border-accent)',
                    marginBottom: '16px',
                    fontSize: '12px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}
                >
                  <span style={{ color: 'var(--text-secondary)' }}>Damage Inflicted:</span>
                  <span style={{ fontWeight: 700, color: 'var(--accent-gold)' }}>
                    {rollOutcome.damage.summary}
                  </span>
                </div>
              )}

              {/* Proceed Button */}
              <button
                type="button"
                className="btn btn-primary"
                style={{
                  width: '100%',
                  padding: '12px',
                  fontSize: '14px',
                  fontWeight: 700,
                  letterSpacing: '0.03em',
                  gap: '8px',
                }}
                onClick={onProceed}
              >
                Proceed to DM Story <ArrowRight size={16} />
              </button>
            </div>
          ) : (
            /* Initial Challenge Setup State */
            <>
              {/* Challenge Description */}
              <div
                style={{
                  padding: '12px 14px',
                  backgroundColor: 'var(--bg-card)',
                  border: '1px solid var(--border-accent)',
                  borderRadius: 'var(--radius-sm)',
                  marginBottom: '16px',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <span style={{ fontWeight: 700, fontSize: '14px', color: 'var(--accent-gold)' }}>
                    {checkData.resolved_name || `${checkData.target} Check`}
                  </span>
                  <span
                    style={{
                      fontSize: '12px',
                      fontWeight: 700,
                      padding: '2px 8px',
                      borderRadius: 'var(--radius-sm)',
                      backgroundColor: 'var(--bg-surface)',
                      border: '1px solid var(--border-gold)',
                      color: 'var(--text-primary)',
                    }}
                  >
                    DC {checkData.dc}
                  </span>
                </div>
                <p style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                  {checkData.reason}
                </p>
              </div>

              {/* Modifier Display */}
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '10px 14px',
                  backgroundColor: 'var(--bg-card)',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--border-subtle)',
                  marginBottom: '16px',
                }}
              >
                <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                  Your Character Modifier:
                </span>
                <span style={{ fontSize: '16px', fontWeight: 800, color: 'var(--accent-green)' }}>
                  {modStr}
                </span>
              </div>

              {/* Advantage / Disadvantage Selector */}
              <div style={{ marginBottom: '20px' }}>
                <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>
                  Roll Mode
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '6px' }}>
                  <button
                    type="button"
                    className={`btn ${rollMode === 'normal' ? 'btn-primary' : 'btn-secondary'}`}
                    style={{ padding: '8px 4px', fontSize: '12px' }}
                    onClick={() => setRollMode('normal')}
                  >
                    Straight
                  </button>
                  <button
                    type="button"
                    className={`btn ${rollMode === 'advantage' ? 'btn-primary' : 'btn-secondary'}`}
                    style={{
                      padding: '8px 4px',
                      fontSize: '12px',
                      color: rollMode === 'advantage' ? '#0c0e12' : 'var(--accent-green)',
                    }}
                    onClick={() => setRollMode('advantage')}
                  >
                    Advantage
                  </button>
                  <button
                    type="button"
                    className={`btn ${rollMode === 'disadvantage' ? 'btn-primary' : 'btn-secondary'}`}
                    style={{
                      padding: '8px 4px',
                      fontSize: '12px',
                      color: rollMode === 'disadvantage' ? '#0c0e12' : 'var(--accent-crimson)',
                    }}
                    onClick={() => setRollMode('disadvantage')}
                  >
                    Disadvantage
                  </button>
                </div>
              </div>

              {/* Roll Button */}
              <button
                type="button"
                className="btn btn-primary"
                style={{
                  width: '100%',
                  padding: '12px',
                  fontSize: '14px',
                  fontWeight: 700,
                  letterSpacing: '0.03em',
                }}
                onClick={handleRoll}
                disabled={isRolling}
              >
                <Dices size={18} />
                Roll 1d20 {modStr} vs DC {checkData.dc}
              </button>
            </>
          )}
        </div>

        {/* Countdown bar when showing outcome */}
        {rollOutcome && <div className="auto-countdown-bar" />}
      </div>
    </div>
  );
};
