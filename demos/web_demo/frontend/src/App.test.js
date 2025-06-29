import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import App from './App';
import { apiService } from './services/apiService';

// Mock the API service
jest.mock('./services/apiService');

// Mock styled-components to avoid issues in tests
jest.mock('styled-components', () => {
  const actual = jest.requireActual('styled-components');
  return {
    ...actual,
    ThemeProvider: ({ children }) => children,
  };
});

describe('App Component', () => {
  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();
    
    // Default mock implementations
    apiService.getHealth.mockResolvedValue({
      status: 'healthy',
      pipeline_loaded: true,
      audit_enabled: true,
      enabled_guardrails: 5,
      total_guardrails: 5
    });
    
    apiService.getGuardrails.mockResolvedValue({
      input_guardrails: [],
      output_guardrails: [],
      preset: 'customer_service',
      use_conversation_aware_prompt_injection: false
    });
  });

  test('renders main app components', async () => {
    render(<App />);
    
    // Check for main components
    expect(screen.getByText(/Stinger Guardrails/i)).toBeInTheDocument();
    
    // Wait for status to load
    await waitFor(() => {
      expect(screen.getByText(/Pipeline Status:/i)).toBeInTheDocument();
    });
  });

  test('loads system status on mount', async () => {
    render(<App />);
    
    await waitFor(() => {
      expect(apiService.getHealth).toHaveBeenCalled();
      expect(apiService.getGuardrails).toHaveBeenCalled();
    });
  });

  test('handles API errors gracefully', async () => {
    apiService.getHealth.mockRejectedValue(new Error('API Error'));
    
    render(<App />);
    
    // Should not crash and should show some error state
    await waitFor(() => {
      expect(screen.getByText(/Stinger Guardrails/i)).toBeInTheDocument();
    });
  });

  test('responsive layout works', () => {
    render(<App />);
    
    // Check that main containers exist
    const appContainer = document.querySelector('div'); // styled div
    expect(appContainer).toBeInTheDocument();
  });

  test('updates system status periodically', async () => {
    jest.useFakeTimers();
    
    render(<App />);
    
    // Clear initial calls
    jest.clearAllMocks();
    
    // Fast-forward time to trigger interval
    jest.advanceTimersByTime(10000); // 10 seconds
    
    await waitFor(() => {
      expect(apiService.getHealth).toHaveBeenCalled();
    });
    
    jest.useRealTimers();
  });

  test('system status shows correct information', async () => {
    apiService.getHealth.mockResolvedValue({
      status: 'healthy',
      pipeline_loaded: true,
      audit_enabled: true,
      enabled_guardrails: 3,
      total_guardrails: 5
    });
    
    render(<App />);
    
    await waitFor(() => {
      expect(screen.getByText(/3 of 5 guardrails active/i)).toBeInTheDocument();
    });
  });

  test('handles guardrail settings updates', async () => {
    const mockSettings = {
      input_guardrails: [
        { name: 'length_check', enabled: true },
        { name: 'pii_detection', enabled: false }
      ],
      output_guardrails: [
        { name: 'content_filter', enabled: true }
      ],
      preset: 'customer_service',
      use_conversation_aware_prompt_injection: true
    };
    
    apiService.getGuardrails.mockResolvedValue(mockSettings);
    
    render(<App />);
    
    await waitFor(() => {
      expect(apiService.getGuardrails).toHaveBeenCalled();
    });
  });

  test('maintains conversation state', async () => {
    apiService.sendMessage.mockResolvedValue({
      content: 'Test response',
      blocked: false,
      warnings: [],
      reasons: [],
      conversation_id: 'test-conversation-123',
      processing_details: {}
    });
    
    render(<App />);
    
    // Find and interact with chat input
    const chatInput = screen.getByPlaceholderText(/Type your message here/i);
    await userEvent.type(chatInput, 'Hello world');
    
    const sendButton = screen.getByRole('button', { name: /send/i });
    fireEvent.click(sendButton);
    
    await waitFor(() => {
      expect(apiService.sendMessage).toHaveBeenCalledWith('Hello world');
    });
  });

  test('shows warnings and blocking correctly', async () => {
    apiService.sendMessage.mockResolvedValue({
      content: 'Message blocked',
      blocked: true,
      warnings: ['Contains PII'],
      reasons: ['PII detected: SSN'],
      conversation_id: 'test-conversation-123',
      processing_details: {}
    });
    
    render(<App />);
    
    const chatInput = screen.getByPlaceholderText(/Type your message here/i);
    await userEvent.type(chatInput, 'My SSN is 123-45-6789');
    
    const sendButton = screen.getByRole('button', { name: /send/i });
    fireEvent.click(sendButton);
    
    await waitFor(() => {
      expect(screen.getByText(/blocked/i)).toBeInTheDocument();
    });
  });
});