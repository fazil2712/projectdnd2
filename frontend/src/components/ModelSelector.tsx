import React, { useState, useEffect } from 'react';
import { Bot, ChevronDown, Download, Check, Sparkles, AlertCircle, RefreshCw } from 'lucide-react';
import { ModelInfo } from '../types/game';

interface ModelSelectorProps {
  activeModel: string;
  onSelectModel: (modelId: string) => void;
}

export const ModelSelector: React.FC<ModelSelectorProps> = ({ activeModel, onSelectModel }) => {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [ollamaOnline, setOllamaOnline] = useState<boolean>(true);
  const [isPulling, setIsPulling] = useState<boolean>(false);

  const fetchModels = async () => {
    try {
      const res = await fetch('/api/models');
      if (res.ok) {
        const data = await res.json();
        setModels(data.models || []);
        setOllamaOnline(data.ollama_online);
      }
    } catch {
      setOllamaOnline(false);
    }
  };

  useEffect(() => {
    fetchModels();
    const interval = setInterval(fetchModels, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleTriggerPull = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsPulling(true);
    try {
      await fetch('/api/models/pull', { method: 'POST' });
      await fetchModels();
    } catch (err) {
      console.error(err);
    } finally {
      setTimeout(() => setIsPulling(false), 2000);
    }
  };

  const activeModelObj = models.find((m) => m.id === activeModel);

  return (
    <div style={{ position: 'relative' }}>
      <button
        type="button"
        className="btn btn-secondary"
        onClick={() => setIsOpen(!isOpen)}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '6px 12px',
          border: '1px solid var(--border-accent)',
          background: 'var(--bg-card)',
          borderRadius: 'var(--radius-sm)',
          cursor: 'pointer',
        }}
      >
        <Bot size={16} color="var(--accent-gold)" />
        <span style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '13px', maxWidth: '120px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {activeModelObj ? activeModelObj.name : activeModel}
        </span>
        {activeModelObj && (
          <span
            style={{
              fontSize: '10px',
              padding: '2px 6px',
              borderRadius: '3px',
              backgroundColor:
                activeModelObj.status === 'ready'
                  ? 'var(--accent-green-dim)'
                  : activeModelObj.status === 'downloading'
                  ? 'var(--accent-cyan-dim)'
                  : 'var(--accent-gold-dim)',
              color:
                activeModelObj.status === 'ready'
                  ? 'var(--accent-green)'
                  : activeModelObj.status === 'downloading'
                  ? 'var(--accent-cyan)'
                  : 'var(--accent-gold)',
            }}
          >
            {activeModelObj.status === 'ready'
              ? 'Ready'
              : activeModelObj.status === 'downloading'
              ? `${activeModelObj.progress}%`
              : 'Simulation'}
          </span>
        )}
        <ChevronDown size={14} color="var(--text-muted)" />
      </button>

      {isOpen && (
        <>
          <div
            style={{ position: 'fixed', inset: 0, zIndex: 40 }}
            onClick={() => setIsOpen(false)}
          />
          <div
            className="model-dropdown-menu"
            style={{
              padding: '12px',
            }}
          >
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                paddingBottom: '8px',
                marginBottom: '8px',
                borderBottom: '1px solid var(--border-subtle)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Sparkles size={14} color="var(--accent-gold)" />
                <span style={{ fontWeight: 700, fontSize: '12px', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
                  Select Dungeon Master Model
                </span>
              </div>
              <button
                type="button"
                onClick={handleTriggerPull}
                title="Download all models"
                className="btn btn-ghost"
                style={{ fontSize: '11px', padding: '2px 6px' }}
              >
                <Download size={12} />
                {isPulling ? 'Pulling...' : 'Pull All'}
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '360px', overflowY: 'auto' }}>
              {models.map((model) => {
                const isSelected = model.id === activeModel;
                return (
                  <div
                    key={model.id}
                    onClick={() => {
                      onSelectModel(model.id);
                      setIsOpen(false);
                    }}
                    style={{
                      padding: '10px',
                      borderRadius: 'var(--radius-sm)',
                      backgroundColor: isSelected ? 'var(--bg-card-active)' : 'var(--bg-card)',
                      border: isSelected ? '1px solid var(--accent-gold)' : '1px solid var(--border-subtle)',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '4px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <span style={{ fontWeight: 600, fontSize: '13px', color: 'var(--text-primary)' }}>
                          {model.name}
                        </span>
                        {isSelected && <Check size={14} color="var(--accent-gold)" />}
                      </div>
                      <span
                        style={{
                          fontSize: '10px',
                          padding: '1px 5px',
                          borderRadius: '3px',
                          backgroundColor:
                            model.status === 'ready'
                              ? 'var(--accent-green-dim)'
                              : model.status === 'downloading'
                              ? 'var(--accent-cyan-dim)'
                              : 'rgba(255,255,255,0.06)',
                          color:
                            model.status === 'ready'
                              ? 'var(--accent-green)'
                              : model.status === 'downloading'
                              ? 'var(--accent-cyan)'
                              : 'var(--text-muted)',
                        }}
                      >
                        {model.status === 'ready'
                          ? 'Installed'
                          : model.status === 'downloading'
                          ? `Downloading ${model.progress}%`
                          : 'Fallback Ready'}
                      </span>
                    </div>

                    <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '6px', lineHeight: 1.4 }}>
                      {model.description}
                    </p>

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '10px', color: 'var(--text-muted)' }}>
                      <span>VRAM: {model.vram_approx}</span>
                      <span>{model.message || (model.status === 'ready' ? 'Ready on local GPU' : 'Simulation active')}</span>
                    </div>

                    {model.status === 'downloading' && (
                      <div style={{ marginTop: '6px', height: '3px', backgroundColor: 'var(--border-subtle)', borderRadius: '2px', overflow: 'hidden' }}>
                        <div
                          style={{
                            height: '100%',
                            width: `${model.progress}%`,
                            backgroundColor: 'var(--accent-cyan)',
                            transition: 'width 0.3s ease',
                          }}
                        />
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            <div
              style={{
                marginTop: '10px',
                paddingTop: '8px',
                borderTop: '1px solid var(--border-subtle)',
                fontSize: '11px',
                color: 'var(--text-muted)',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
              }}
            >
              <AlertCircle size={12} color={ollamaOnline ? 'var(--accent-green)' : 'var(--accent-crimson)'} />
              <span>Ollama Daemon: {ollamaOnline ? 'Online (localhost:11434)' : 'Offline (Simulation Active)'}</span>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
