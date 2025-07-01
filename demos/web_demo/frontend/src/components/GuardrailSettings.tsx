import React from 'react';

export interface GuardrailSettingsData {
  input_guardrails: { name: string; enabled: boolean; }[];
  output_guardrails: { name: string; enabled: boolean; }[];
}

interface GuardrailSettingsProps {
  settings: GuardrailSettingsData | null;
  onToggle: (type: 'input' | 'output', guardrail: string, enabled: boolean) => void;
}

export const GuardrailSettings: React.FC<GuardrailSettingsProps> = ({ settings, onToggle }) => {
  const formatGuardrailName = (name: string) => {
    if (!name) return 'Unknown Guardrail';
    
    const nameMap: { [key: string]: string } = {
      'pii_check': 'PII Detection (AI)',
      'toxicity_check': 'Toxicity Detection (Local)', 
      'length_check': 'Length Filter (Local)',
      'code_generation_check': 'Code Generation (AI)',
      'prompt_injection_check': 'Prompt Injection (AI)'
    };
    return nameMap[name] || name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  if (!settings) {
    return <div className="loading">Loading settings...</div>;
  }

  return (
    <div className="settings-panel">
      <h3>⚙️ Guardrail Settings</h3>
      
      <div className="guardrail-section">
        <h4>Input Guardrails (Process User Messages)</h4>
        {settings.input_guardrails.map((g) => (
          <label key={g.name} className="guardrail-toggle">
            <input
              type="checkbox"
              checked={g.enabled}
              onChange={(e) => onToggle('input', g.name, e.target.checked)}
            />
            <span>{formatGuardrailName(g.name)}</span>
          </label>
        ))}
      </div>

      <div className="guardrail-section">
        <h4>Output Guardrails (Process AI Responses)</h4>
        {settings.output_guardrails.map((g) => (
          <label key={g.name} className="guardrail-toggle">
            <input
              type="checkbox"
              checked={g.enabled}
              onChange={(e) => onToggle('output', g.name, e.target.checked)}
            />
            <span>{formatGuardrailName(g.name)}</span>
          </label>
        ))}
      </div>
    </div>
  );
};