import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import SettingsPanel from './SettingsPanel';

// Mock styled-components
jest.mock('styled-components', () => {
  const actual = jest.requireActual('styled-components');
  return {
    ...actual,
    ThemeProvider: ({ children }) => children,
  };
});

// Mock react-icons
jest.mock('react-icons/fa', () => ({
  FaCog: () => <div data-testid="cog-icon">Settings</div>,
  FaShieldAlt: () => <div data-testid="shield-icon">Shield</div>,
  FaToggleOn: () => <div data-testid="toggle-on-icon">On</div>,
  FaToggleOff: () => <div data-testid="toggle-off-icon">Off</div>
}));

describe('SettingsPanel Component', () => {
  const mockOnSettingsChange = jest.fn();
  const mockOnPresetChange = jest.fn();
  
  const mockSettings = {
    input_guardrails: [
      { name: 'length_check', enabled: true },
      { name: 'pii_detection', enabled: false },
      { name: 'prompt_injection', enabled: true }
    ],
    output_guardrails: [
      { name: 'content_filter', enabled: true },
      { name: 'toxicity_check', enabled: false }
    ],
    preset: 'customer_service',
    use_conversation_aware_prompt_injection: false
  };

  const mockPresets = {
    'customer_service': 'Customer Service',
    'content_moderation': 'Content Moderation',
    'basic_pipeline': 'Basic Pipeline'
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders settings panel correctly', () => {
    render(
      <SettingsPanel
        settings={mockSettings}
        presets={mockPresets}
        onSettingsChange={mockOnSettingsChange}
        onPresetChange={mockOnPresetChange}
      />
    );

    expect(screen.getByText(/Guardrails Configuration/i)).toBeInTheDocument();
    expect(screen.getByText(/Input Guardrails/i)).toBeInTheDocument();
    expect(screen.getByText(/Output Guardrails/i)).toBeInTheDocument();
  });

  test('displays input guardrails correctly', () => {
    render(
      <SettingsPanel
        settings={mockSettings}
        presets={mockPresets}
        onSettingsChange={mockOnSettingsChange}
        onPresetChange={mockOnPresetChange}
      />
    );

    expect(screen.getByText(/length_check/i)).toBeInTheDocument();
    expect(screen.getByText(/pii_detection/i)).toBeInTheDocument();
    expect(screen.getByText(/prompt_injection/i)).toBeInTheDocument();
  });

  test('displays output guardrails correctly', () => {
    render(
      <SettingsPanel
        settings={mockSettings}
        presets={mockPresets}
        onSettingsChange={mockOnSettingsChange}
        onPresetChange={mockOnPresetChange}
      />
    );

    expect(screen.getByText(/content_filter/i)).toBeInTheDocument();
    expect(screen.getByText(/toxicity_check/i)).toBeInTheDocument();
  });

  test('toggles input guardrail correctly', async () => {
    render(
      <SettingsPanel
        settings={mockSettings}
        presets={mockPresets}
        onSettingsChange={mockOnSettingsChange}
        onPresetChange={mockOnPresetChange}
      />
    );

    // Find the toggle for pii_detection (currently disabled)
    const piiToggle = screen.getByLabelText(/pii_detection/i);
    fireEvent.click(piiToggle);

    await waitFor(() => {
      expect(mockOnSettingsChange).toHaveBeenCalledWith({
        ...mockSettings,
        input_guardrails: [
          { name: 'length_check', enabled: true },
          { name: 'pii_detection', enabled: true }, // Should be toggled
          { name: 'prompt_injection', enabled: true }
        ]
      });
    });
  });

  test('toggles output guardrail correctly', async () => {
    render(
      <SettingsPanel
        settings={mockSettings}
        presets={mockPresets}
        onSettingsChange={mockOnSettingsChange}
        onPresetChange={mockOnPresetChange}
      />
    );

    // Find the toggle for toxicity_check (currently disabled)
    const toxicityToggle = screen.getByLabelText(/toxicity_check/i);
    fireEvent.click(toxicityToggle);

    await waitFor(() => {
      expect(mockOnSettingsChange).toHaveBeenCalledWith({
        ...mockSettings,
        output_guardrails: [
          { name: 'content_filter', enabled: true },
          { name: 'toxicity_check', enabled: true } // Should be toggled
        ]
      });
    });
  });

  test('changes preset correctly', async () => {
    render(
      <SettingsPanel
        settings={mockSettings}
        presets={mockPresets}
        onSettingsChange={mockOnSettingsChange}
        onPresetChange={mockOnPresetChange}
      />
    );

    const presetSelect = screen.getByRole('combobox');
    await userEvent.selectOptions(presetSelect, 'content_moderation');

    expect(mockOnPresetChange).toHaveBeenCalledWith('content_moderation');
  });

  test('displays current preset correctly', () => {
    render(
      <SettingsPanel
        settings={mockSettings}
        presets={mockPresets}
        onSettingsChange={mockOnSettingsChange}
        onPresetChange={mockOnPresetChange}
      />
    );

    const presetSelect = screen.getByRole('combobox');
    expect(presetSelect.value).toBe('customer_service');
  });

  test('toggles conversation aware prompt injection', async () => {
    render(
      <SettingsPanel
        settings={mockSettings}
        presets={mockPresets}
        onSettingsChange={mockOnSettingsChange}
        onPresetChange={mockOnPresetChange}
      />
    );

    const conversationToggle = screen.getByLabelText(/conversation aware/i);
    fireEvent.click(conversationToggle);

    await waitFor(() => {
      expect(mockOnSettingsChange).toHaveBeenCalledWith({
        ...mockSettings,
        use_conversation_aware_prompt_injection: true
      });
    });
  });

  test('handles empty guardrail lists', () => {
    const emptySettings = {
      input_guardrails: [],
      output_guardrails: [],
      preset: 'basic_pipeline',
      use_conversation_aware_prompt_injection: false
    };

    render(
      <SettingsPanel
        settings={emptySettings}
        presets={mockPresets}
        onSettingsChange={mockOnSettingsChange}
        onPresetChange={mockOnPresetChange}
      />
    );

    expect(screen.getByText(/Input Guardrails/i)).toBeInTheDocument();
    expect(screen.getByText(/Output Guardrails/i)).toBeInTheDocument();
    // Should show some indication that no guardrails are available
  });

  test('shows guardrail counts', () => {
    render(
      <SettingsPanel
        settings={mockSettings}
        presets={mockPresets}
        onSettingsChange={mockOnSettingsChange}
        onPresetChange={mockOnPresetChange}
      />
    );

    // Check that enabled/total counts are shown
    const enabledInputCount = mockSettings.input_guardrails.filter(g => g.enabled).length;
    const totalInputCount = mockSettings.input_guardrails.length;
    
    expect(screen.getByText(new RegExp(`${enabledInputCount}.*${totalInputCount}`))).toBeInTheDocument();
  });

  test('handles preset loading error gracefully', () => {
    const emptyPresets = {};

    render(
      <SettingsPanel
        settings={mockSettings}
        presets={emptyPresets}
        onSettingsChange={mockOnSettingsChange}
        onPresetChange={mockOnPresetChange}
      />
    );

    // Should still render without crashing
    expect(screen.getByText(/Guardrails Configuration/i)).toBeInTheDocument();
  });

  test('displays toggle states correctly', () => {
    render(
      <SettingsPanel
        settings={mockSettings}
        presets={mockPresets}
        onSettingsChange={mockOnSettingsChange}
        onPresetChange={mockOnPresetChange}
      />
    );

    // Check enabled guardrails show as enabled
    const lengthToggle = screen.getByLabelText(/length_check/i);
    expect(lengthToggle).toBeChecked();

    // Check disabled guardrails show as disabled
    const piiToggle = screen.getByLabelText(/pii_detection/i);
    expect(piiToggle).not.toBeChecked();
  });

  test('maintains focus after toggle interactions', async () => {
    render(
      <SettingsPanel
        settings={mockSettings}
        presets={mockPresets}
        onSettingsChange={mockOnSettingsChange}
        onPresetChange={mockOnPresetChange}
      />
    );

    const toggle = screen.getByLabelText(/length_check/i);
    
    // Click the toggle
    fireEvent.click(toggle);
    
    // Focus should remain on the toggle
    expect(toggle).toHaveFocus();
  });

  test('keyboard navigation works correctly', async () => {
    render(
      <SettingsPanel
        settings={mockSettings}
        presets={mockPresets}
        onSettingsChange={mockOnSettingsChange}
        onPresetChange={mockOnPresetChange}
      />
    );

    const firstToggle = screen.getByLabelText(/length_check/i);
    
    // Focus the first toggle
    firstToggle.focus();
    expect(firstToggle).toHaveFocus();
    
    // Use Space to toggle
    fireEvent.keyDown(firstToggle, { key: ' ' });
    
    await waitFor(() => {
      expect(mockOnSettingsChange).toHaveBeenCalled();
    });
  });

  test('shows guardrail descriptions when available', () => {
    const settingsWithDescriptions = {
      ...mockSettings,
      input_guardrails: [
        { name: 'length_check', enabled: true, description: 'Checks message length' },
        { name: 'pii_detection', enabled: false, description: 'Detects personal information' }
      ]
    };

    render(
      <SettingsPanel
        settings={settingsWithDescriptions}
        presets={mockPresets}
        onSettingsChange={mockOnSettingsChange}
        onPresetChange={mockOnPresetChange}
      />
    );

    expect(screen.getByText(/Checks message length/i)).toBeInTheDocument();
    expect(screen.getByText(/Detects personal information/i)).toBeInTheDocument();
  });
});