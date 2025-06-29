import React from 'react';
import { render, screen, waitFor, fireEvent, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import App from './App';
import { apiService } from './services/apiService';

// Mock the API service
jest.mock('./services/apiService');

// Mock child components to simplify testing
jest.mock('./components/ChatInterface', () => {
  return function MockChatInterface({ onSendMessage, conversation }) {
    const React = require('react');
    const [inputValue, setInputValue] = React.useState('');
    
    return (
      <div data-testid="chat-interface">
        <input 
          data-testid="chat-input" 
          placeholder="Type your message here..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter' && inputValue) {
              onSendMessage(inputValue);
              setInputValue('');
            }
          }}
        />
        <button onClick={() => {
          if (inputValue) {
            onSendMessage(inputValue);
            setInputValue('');
          }
        }}>Send</button>
        <div>Conversation: {conversation?.conversation_id || 'none'}</div>
      </div>
    );
  };
});

jest.mock('./components/SettingsPanel', () => {
  return function MockSettingsPanel({ settings, onSettingsChange, onPresetChange }) {
    return (
      <div data-testid="settings-panel">
        <button onClick={() => onSettingsChange({ test: 'settings' })}>Update Settings</button>
        <button onClick={() => onPresetChange('test-preset')}>Change Preset</button>
      </div>
    );
  };
});

jest.mock('./components/AuditLogViewer', () => {
  return function MockAuditLogViewer() {
    return <div data-testid="audit-log-viewer">Audit Log</div>;
  };
});

jest.mock('./components/Header', () => {
  return function MockHeader({ onToggleSettings, systemStatus, onResetConversation }) {
    return (
      <div data-testid="header">
        <h1>Stinger Guardrails</h1>
        <button onClick={onToggleSettings}>Toggle Settings</button>
        <button onClick={onResetConversation}>Reset</button>
        <div>Status: {systemStatus?.status || 'loading'}</div>
      </div>
    );
  };
});

jest.mock('./components/StatusBar', () => {
  return function MockStatusBar({ systemStatus }) {
    return (
      <div data-testid="status-bar">
        <div>Pipeline Status: {systemStatus?.pipeline_loaded ? 'Loaded' : 'Not Loaded'}</div>
        <div>{systemStatus?.enabled_guardrails || 0} of {systemStatus?.total_guardrails || 0} guardrails active</div>
      </div>
    );
  };
});

describe('App Component', () => {
  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();
    
    // Default mock implementations
    apiService.getSystemStatus.mockResolvedValue({
      status: 'healthy',
      pipeline_loaded: true,
      audit_enabled: true,
      enabled_guardrails: 5,
      total_guardrails: 5
    });
    
    apiService.getGuardrailSettings.mockResolvedValue({
      input_guardrails: [],
      output_guardrails: [],
      preset: 'customer_service',
      use_conversation_aware_prompt_injection: false
    });
  });

  test('renders loading state initially', () => {
    // Mock API calls to never resolve
    apiService.getSystemStatus.mockImplementation(() => new Promise(() => {}));
    apiService.getGuardrailSettings.mockImplementation(() => new Promise(() => {}));

    act(() => {
      render(<App />);
    });
    
    expect(screen.getByText('Loading Stinger Web Demo...')).toBeInTheDocument();
  });

  test('renders main app components after loading', async () => {
    await act(async () => {
      render(<App />);
    });
    
    // Wait for app to load
    await waitFor(() => {
      expect(screen.getByText(/Stinger Guardrails/i)).toBeInTheDocument();
    });
    
    expect(screen.getByTestId('chat-interface')).toBeInTheDocument();
    expect(screen.getByTestId('header')).toBeInTheDocument();
    expect(screen.getByTestId('settings-panel')).toBeInTheDocument();
    expect(screen.getByTestId('status-bar')).toBeInTheDocument();
  });

  test('loads system status on mount', async () => {
    await act(async () => {
      render(<App />);
    });
    
    await waitFor(() => {
      expect(apiService.getSystemStatus).toHaveBeenCalled();
      expect(apiService.getGuardrailSettings).toHaveBeenCalled();
    });
  });

  test('handles API errors gracefully', async () => {
    apiService.getSystemStatus.mockRejectedValue(new Error('Network error'));
    apiService.getGuardrailSettings.mockRejectedValue(new Error('Network error'));
    
    await act(async () => {
      render(<App />);
    });
    
    await waitFor(() => {
      expect(screen.getByText('Connection Error')).toBeInTheDocument();
    });

    expect(screen.getByText(/Cannot connect to the backend server/)).toBeInTheDocument();
    expect(screen.getByText('Retry Connection')).toBeInTheDocument();
  });

  test('displays correct system status information', async () => {
    apiService.getSystemStatus.mockResolvedValue({
      status: 'healthy',
      pipeline_loaded: true,
      audit_enabled: true,
      enabled_guardrails: 3,
      total_guardrails: 5
    });
    
    render(<App />);
    
    await waitFor(() => {
      expect(screen.getByText('3 of 5 guardrails active')).toBeInTheDocument();
      expect(screen.getByText('Pipeline Status: Loaded')).toBeInTheDocument();
      expect(screen.getByText('Status: healthy')).toBeInTheDocument();
    });
  });

  test('handles message sending', async () => {
    const mockResponse = { content: 'Test response', blocked: false };
    const mockConversation = { conversation_id: 'test-123', active: true };

    apiService.sendChatMessage.mockResolvedValue(mockResponse);
    apiService.getConversationInfo.mockResolvedValue(mockConversation);
    
    render(<App />);
    
    await waitFor(() => {
      expect(screen.getByTestId('chat-interface')).toBeInTheDocument();
    });

    const chatInput = screen.getByTestId('chat-input');
    await userEvent.type(chatInput, 'Hello world');
    
    const sendButton = screen.getByText('Send');
    fireEvent.click(sendButton);
    
    await waitFor(() => {
      expect(apiService.sendChatMessage).toHaveBeenCalledWith({
        content: 'Hello world',
        conversation_id: undefined
      });
    });
  });

  test('handles settings updates', async () => {
    render(<App />);
    
    await waitFor(() => {
      expect(screen.getByTestId('settings-panel')).toBeInTheDocument();
    });

    apiService.updateGuardrailSettings.mockResolvedValue();
    apiService.getGuardrailSettings.mockResolvedValue({ input_guardrails: [], output_guardrails: [] });
    apiService.getSystemStatus.mockResolvedValue({ status: 'healthy', pipeline_loaded: true });

    fireEvent.click(screen.getByText('Update Settings'));

    await waitFor(() => {
      expect(apiService.updateGuardrailSettings).toHaveBeenCalledWith({ test: 'settings' });
    });
  });

  test('handles preset changes', async () => {
    render(<App />);
    
    await waitFor(() => {
      expect(screen.getByTestId('settings-panel')).toBeInTheDocument();
    });

    apiService.loadPreset.mockResolvedValue();
    apiService.getGuardrailSettings.mockResolvedValue({ input_guardrails: [], output_guardrails: [] });
    apiService.getSystemStatus.mockResolvedValue({ status: 'healthy', pipeline_loaded: true });

    fireEvent.click(screen.getByText('Change Preset'));

    await waitFor(() => {
      expect(apiService.loadPreset).toHaveBeenCalledWith({ preset: 'test-preset' });
    });
  });

  test('handles conversation reset', async () => {
    render(<App />);
    
    await waitFor(() => {
      expect(screen.getByTestId('header')).toBeInTheDocument();
    });

    apiService.resetConversation.mockResolvedValue();

    fireEvent.click(screen.getByText('Reset'));

    await waitFor(() => {
      expect(apiService.resetConversation).toHaveBeenCalled();
    });
  });

  test('toggles between settings and audit tabs', async () => {
    render(<App />);
    
    await waitFor(() => {
      expect(screen.getByTestId('settings-panel')).toBeInTheDocument();
    });

    // Settings tab should be active by default
    expect(screen.getByTestId('settings-panel')).toBeInTheDocument();
    expect(screen.queryByTestId('audit-log-viewer')).not.toBeInTheDocument();

    // Click audit tab
    fireEvent.click(screen.getByText('Audit Log'));

    expect(screen.getByTestId('audit-log-viewer')).toBeInTheDocument();
    expect(screen.queryByTestId('settings-panel')).not.toBeInTheDocument();
  });

  test('handles retry functionality', async () => {
    // First call fails
    apiService.getSystemStatus.mockRejectedValueOnce(new Error('Network error'));
    apiService.getGuardrailSettings.mockRejectedValueOnce(new Error('Network error'));

    // Second call succeeds
    const mockStatus = { status: 'healthy', pipeline_loaded: true };
    const mockSettings = { input_guardrails: [], output_guardrails: [] };
    apiService.getSystemStatus.mockResolvedValue(mockStatus);
    apiService.getGuardrailSettings.mockResolvedValue(mockSettings);

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText('Connection Error')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Retry Connection'));

    await waitFor(() => {
      expect(screen.getByTestId('chat-interface')).toBeInTheDocument();
    });
  });
});