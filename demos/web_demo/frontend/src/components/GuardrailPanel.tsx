import React, { useState, useEffect } from 'react';
import './GuardrailPanel.css';

interface GuardrailInfo {
  name: string;
  type: string;
  enabled: boolean;
  display_name: string;
  description: string;
  category: 'ai' | 'local' | 'custom';
  guardrail_type: 'privacy' | 'safety' | 'security' | 'filter';
}

interface GuardrailDetails {
  input_guardrails: GuardrailInfo[];
  output_guardrails: GuardrailInfo[];
}

interface GuardrailPanelProps {
  isOpen: boolean;
  onClose: () => void;
  onGuardrailToggle: (name: string, type: 'input' | 'output', enabled: boolean) => void;
}

export const GuardrailPanel: React.FC<GuardrailPanelProps> = ({ 
  isOpen, 
  onClose,
  onGuardrailToggle 
}) => {
  const [guardrails, setGuardrails] = useState<GuardrailDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'input' | 'output'>('input');

  useEffect(() => {
    if (isOpen) {
      loadGuardrailDetails();
    }
  }, [isOpen]);

  const loadGuardrailDetails = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/guardrails/details');
      if (response.ok) {
        const data = await response.json();
        setGuardrails(data);
      }
    } catch (error) {
      console.error('Failed to load guardrail details:', error);
    } finally {
      setLoading(false);
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'ai': return '🤖';
      case 'local': return '⚡';
      default: return '🔧';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'privacy': return '🔒';
      case 'safety': return '🛡️';
      case 'security': return '🔐';
      case 'filter': return '🔍';
      default: return '📋';
    }
  };

  const renderGuardrails = (guardrailList: GuardrailInfo[], type: 'input' | 'output') => {
    // Group by category
    const grouped = guardrailList.reduce((acc, g) => {
      const cat = g.category || 'custom';
      if (!acc[cat]) acc[cat] = [];
      acc[cat].push(g);
      return acc;
    }, {} as Record<string, GuardrailInfo[]>);

    const categoryOrder = ['ai', 'local', 'custom'];
    const categoryLabels = {
      'ai': 'AI-Powered Guardrails',
      'local': 'Local Pattern Matching',
      'custom': 'Custom Guardrails'
    };

    return (
      <div className="guardrails-list">
        {categoryOrder.map(category => {
          const items = grouped[category];
          if (!items || items.length === 0) return null;

          return (
            <div key={category} className="guardrail-category">
              <h4 className="category-header">
                {getCategoryIcon(category)} {categoryLabels[category]}
              </h4>
              {items.map(guardrail => (
                <div key={guardrail.name} className="guardrail-item">
                  <label className="guardrail-toggle">
                    <input
                      type="checkbox"
                      checked={guardrail.enabled}
                      onChange={(e) => onGuardrailToggle(guardrail.name, type, e.target.checked)}
                    />
                    <span className="toggle-slider"></span>
                  </label>
                  <div className="guardrail-info">
                    <div className="guardrail-name">
                      {getTypeIcon(guardrail.guardrail_type)} {guardrail.display_name}
                    </div>
                    <div className="guardrail-description">
                      {guardrail.description}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <>
      {/* Backdrop */}
      {isOpen && <div className="panel-backdrop" onClick={onClose} />}
      
      {/* Panel */}
      <div className={`slide-panel guardrail-panel ${isOpen ? 'open' : ''}`}>
        <div className="panel-header">
          <h2>🛡️ Guardrail Configuration</h2>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        {loading ? (
          <div className="panel-loading">Loading guardrails...</div>
        ) : guardrails ? (
          <>
            <div className="panel-tabs">
              <button 
                className={`tab ${activeTab === 'input' ? 'active' : ''}`}
                onClick={() => setActiveTab('input')}
              >
                Input Guardrails ({guardrails.input_guardrails.filter(g => g.enabled).length}/{guardrails.input_guardrails.length})
              </button>
              <button 
                className={`tab ${activeTab === 'output' ? 'active' : ''}`}
                onClick={() => setActiveTab('output')}
              >
                Output Guardrails ({guardrails.output_guardrails.filter(g => g.enabled).length}/{guardrails.output_guardrails.length})
              </button>
            </div>

            <div className="panel-content">
              {activeTab === 'input' 
                ? renderGuardrails(guardrails.input_guardrails, 'input')
                : renderGuardrails(guardrails.output_guardrails, 'output')
              }
            </div>
          </>
        ) : (
          <div className="panel-error">Failed to load guardrails</div>
        )}
      </div>
    </>
  );
};