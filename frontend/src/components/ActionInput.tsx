import React, { useState, KeyboardEvent } from 'react';
import { Send, Sparkles } from 'lucide-react';

interface ActionInputProps {
  onSubmitAction: (action: string) => void;
  isDisabled: boolean;
}

const QUICK_ACTIONS = [
  'Look around cautiously and observe the sentries',
  'Search the cavern threshold for traps or tripwires',
  'Sneak forward through the shadows past the guards',
  'Draw fine rapier and prepare to strike from concealment',
  'Inspect the door mechanism with thieves\' tools',
];

export const ActionInput: React.FC<ActionInputProps> = ({ onSubmitAction, isDisabled }) => {
  const [input, setInput] = useState('');

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || isDisabled) return;
    onSubmitAction(input.trim());
    setInput('');
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="action-input-container">
      {/* Quick Action Chips */}
      <div
        style={{
          display: 'flex',
          gap: '6px',
          overflowX: 'auto',
          paddingBottom: '8px',
          marginBottom: '8px',
        }}
      >
        {QUICK_ACTIONS.map((action, idx) => (
          <button
            key={idx}
            type="button"
            className="btn btn-secondary"
            style={{
              fontSize: '11px',
              padding: '3px 10px',
              whiteSpace: 'nowrap',
              borderRadius: '12px',
            }}
            disabled={isDisabled}
            onClick={() => {
              if (!isDisabled) {
                onSubmitAction(action);
              }
            }}
          >
            <Sparkles size={11} color="var(--accent-gold)" />
            {action}
          </button>
        ))}
      </div>

      {/* Main Input Bar */}
      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '10px', alignItems: 'flex-end' }}>
        <div style={{ flex: 1, position: 'relative' }}>
          <textarea
            className="action-textarea"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isDisabled}
            placeholder={
              isDisabled
                ? 'The Dungeon Master is narrating or resolving a check...'
                : 'Declare your action (e.g. "I pick the lock on the chest")...'
            }
            rows={2}
            style={{
              width: '100%',
              padding: '10px 14px',
              backgroundColor: 'var(--bg-card)',
              border: '1px solid var(--border-accent)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--text-primary)',
              fontFamily: 'var(--font-body)',
              lineHeight: 1.5,
              resize: 'none',
              outline: 'none',
            }}
          />
        </div>

        <button
          type="submit"
          className="btn btn-primary"
          style={{ height: '44px', padding: '0 18px' }}
          disabled={isDisabled || !input.trim()}
        >
          <Send size={16} />
          <span>Act</span>
        </button>
      </form>
    </div>
  );
};
