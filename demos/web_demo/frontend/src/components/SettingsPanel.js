import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FiShield, FiSettings, FiRefreshCw, FiCheck, FiX } from 'react-icons/fi';
import { apiService } from '../services/apiService';

const PanelContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: #f1f5f9;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 3px;
  }
`;

const Section = styled.div`
  margin-bottom: 24px;
`;

const SectionHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e2e8f0;
`;

const SectionTitle = styled.h3`
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1a202c;
`;

const PresetSelector = styled.select`
  width: 100%;
  padding: 12px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  background: white;
  cursor: pointer;
  transition: border-color 0.2s ease;
  
  &:focus {
    outline: none;
    border-color: #3b82f6;
  }
`;

const GuardrailGroup = styled.div`
  margin-bottom: 20px;
`;

const GroupTitle = styled.h4`
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const GuardrailItem = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  margin-bottom: 8px;
  background: ${props => props.enabled ? '#f0f9ff' : '#f8fafc'};
  border: 1px solid ${props => props.enabled ? '#bae6fd' : '#e2e8f0'};
  border-radius: 8px;
  transition: all 0.2s ease;
  
  &:hover {
    background: ${props => props.enabled ? '#e0f2fe' : '#f1f5f9'};
  }
`;

const GuardrailInfo = styled.div`
  flex: 1;
`;

const GuardrailName = styled.div`
  font-weight: 500;
  color: #1a202c;
  font-size: 14px;
  margin-bottom: 2px;
`;

const GuardrailDescription = styled.div`
  font-size: 12px;
  color: #64748b;
`;

const Toggle = styled.button`
  width: 48px;
  height: 24px;
  border-radius: 12px;
  border: none;
  background: ${props => props.enabled ? '#10b981' : '#e2e8f0'};
  position: relative;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: ${props => props.enabled ? '#059669' : '#cbd5e1'};
  }
  
  &:after {
    content: '';
    position: absolute;
    top: 2px;
    left: ${props => props.enabled ? '26px' : '2px'};
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: white;
    transition: left 0.2s ease;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
`;

const StatusBadge = styled.div`
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  background: ${props => props.enabled ? '#dcfce7' : '#fee2e2'};
  color: ${props => props.enabled ? '#166534' : '#991b1b'};
`;

const SaveButton = styled.button`
  width: 100%;
  padding: 12px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  
  &:hover {
    background: #2563eb;
  }
  
  &:disabled {
    background: #e2e8f0;
    color: #94a3b8;
    cursor: not-allowed;
  }
`;

const ErrorMessage = styled.div`
  background: #fee2e2;
  color: #991b1b;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 14px;
  border: 1px solid #fca5a5;
`;

const SuccessMessage = styled.div`
  background: #dcfce7;
  color: #166534;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 14px;
  border: 1px solid #86efac;
`;

const guardrailDescriptions = {
  'toxicity_check': 'Detects hate speech, harassment, and toxic content',
  'pii_check': 'Identifies personally identifiable information (PII)',
  'code_generation_check': 'Prevents unauthorized code generation',
  'length_check': 'Enforces content length limits',
  'profanity_filter': 'Blocks profanity and inappropriate language',
  'prompt_injection': 'Detects prompt injection attempts',
  'keyword_block': 'Blocks specific keywords and phrases',
};

function SettingsPanel({ settings, onSettingsChange, onPresetChange }) {
  const [localSettings, setLocalSettings] = useState(null);
  const [hasChanges, setHasChanges] = useState(false);
  const [saving, setSaving] = useState(false);
  const [presets, setPresets] = useState({});
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    if (settings) {
      setLocalSettings({ ...settings });
      setHasChanges(false);
    }
  }, [settings]);

  useEffect(() => {
    loadPresets();
  }, []);

  const loadPresets = async () => {
    try {
      const presetsData = await apiService.getAvailablePresets();
      setPresets(presetsData.presets);
    } catch (err) {
      console.error('Failed to load presets:', err);
    }
  };

  const handleGuardrailToggle = (type, name, enabled) => {
    console.log('🔧 handleGuardrailToggle called:', { type, name, enabled });
    if (!localSettings) return;

    const newSettings = { ...localSettings };
    const targetArray = type === 'input' ? 'input_guardrails' : 'output_guardrails';
    
    newSettings[targetArray] = newSettings[targetArray].map(guardrail => 
      guardrail.name === name 
        ? { ...guardrail, enabled: enabled }
        : guardrail
    );

    console.log('🔧 Updated settings:', newSettings);
    setLocalSettings(newSettings);
    setHasChanges(true);
    setError(null);
    setSuccess(null);
  };

  const handlePresetChange = async (preset) => {
    if (!preset) return;

    try {
      setSaving(true);
      setError(null);
      await onPresetChange(preset);
      setHasChanges(false);
      setSuccess(`Loaded ${preset} preset successfully`);
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(`Failed to load preset: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  const handleSave = async () => {
    console.log('💾 handleSave called, hasChanges:', hasChanges, 'localSettings:', localSettings);
    if (!localSettings || !hasChanges) {
      console.log('💾 Early return - no localSettings or no changes');
      return;
    }

    try {
      setSaving(true);
      setError(null);
      console.log('💾 Calling onSettingsChange with:', localSettings);
      await onSettingsChange(localSettings);
      setHasChanges(false);
      setSuccess('Settings saved successfully');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      console.error('💾 Error in handleSave:', err);
      setError(`Failed to save settings: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  if (!localSettings) {
    return (
      <PanelContainer>
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: '200px',
          flexDirection: 'column',
          gap: '12px'
        }}>
          <FiRefreshCw style={{ animation: 'spin 1s linear infinite' }} />
          <span style={{ color: '#64748b', fontSize: '14px' }}>Loading settings...</span>
        </div>
      </PanelContainer>
    );
  }

  return (
    <PanelContainer>
      {error && <ErrorMessage>{error}</ErrorMessage>}
      {success && <SuccessMessage>{success}</SuccessMessage>}

      <Section>
        <SectionHeader>
          <FiSettings />
          <SectionTitle>Preset Configuration</SectionTitle>
        </SectionHeader>
        
        <PresetSelector 
          value={localSettings.preset}
          onChange={(e) => handlePresetChange(e.target.value)}
          disabled={saving}
        >
          <option value="">Select a preset...</option>
          {Object.entries(presets).map(([key, description]) => (
            <option key={key} value={key}>
              {key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} - {description}
            </option>
          ))}
        </PresetSelector>
      </Section>

      <Section>
        <SectionHeader>
          <FiShield />
          <SectionTitle>Guardrail Configuration</SectionTitle>
        </SectionHeader>

        <GuardrailGroup>
          <GroupTitle>Input Guardrails</GroupTitle>
          {localSettings.input_guardrails.map((guardrail) => (
            <GuardrailItem key={guardrail.name} enabled={guardrail.enabled}>
              <GuardrailInfo>
                <GuardrailName>{guardrail.name.replace(/_/g, ' ')}</GuardrailName>
                <GuardrailDescription>
                  {guardrailDescriptions[guardrail.name] || 'Custom guardrail filter'}
                </GuardrailDescription>
              </GuardrailInfo>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <StatusBadge enabled={guardrail.enabled}>
                  {guardrail.enabled ? <FiCheck size={12} /> : <FiX size={12} />}
                  {guardrail.enabled ? 'ON' : 'OFF'}
                </StatusBadge>
                <Toggle
                  enabled={guardrail.enabled}
                  onClick={() => handleGuardrailToggle('input', guardrail.name, !guardrail.enabled)}
                />
              </div>
            </GuardrailItem>
          ))}
        </GuardrailGroup>

        <GuardrailGroup>
          <GroupTitle>Output Guardrails</GroupTitle>
          {localSettings.output_guardrails.map((guardrail) => (
            <GuardrailItem key={guardrail.name} enabled={guardrail.enabled}>
              <GuardrailInfo>
                <GuardrailName>{guardrail.name.replace(/_/g, ' ')}</GuardrailName>
                <GuardrailDescription>
                  {guardrailDescriptions[guardrail.name] || 'Custom guardrail filter'}
                </GuardrailDescription>
              </GuardrailInfo>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <StatusBadge enabled={guardrail.enabled}>
                  {guardrail.enabled ? <FiCheck size={12} /> : <FiX size={12} />}
                  {guardrail.enabled ? 'ON' : 'OFF'}
                </StatusBadge>
                <Toggle
                  enabled={guardrail.enabled}
                  onClick={() => handleGuardrailToggle('output', guardrail.name, !guardrail.enabled)}
                />
              </div>
            </GuardrailItem>
          ))}
        </GuardrailGroup>

        {hasChanges && (
          <SaveButton onClick={handleSave} disabled={saving}>
            {saving ? <FiRefreshCw style={{ animation: 'spin 1s linear infinite' }} /> : <FiCheck />}
            {saving ? 'Saving...' : 'Save Changes'}
          </SaveButton>
        )}
      </Section>
    </PanelContainer>
  );
}

export default SettingsPanel;