import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from './App';

// Mock fetch for testing
global.fetch = jest.fn();

const mockFetch = fetch as jest.MockedFunction<typeof fetch>;

beforeEach(() => {
  mockFetch.mockClear();
});

test('renders Stinger Guardrails Demo title', () => {
  // Mock the initial API calls
  mockFetch.mockResolvedValue({
    ok: true,
    json: () => Promise.resolve({
      status: 'healthy',
      enabled_guardrails: 3,
      total_guardrails: 4
    })
  } as Response);

  render(<App />);
  const titleElement = screen.getByRole('heading', { name: /🛡️ Stinger Guardrails Demo/i });
  expect(titleElement).toBeInTheDocument();
});

test('renders welcome message when no messages', async () => {
  // Mock the initial API calls
  mockFetch.mockResolvedValue({
    ok: true,
    json: () => Promise.resolve({
      status: 'healthy',
      enabled_guardrails: 3,
      total_guardrails: 4
    })
  } as Response);

  render(<App />);
  
  await waitFor(() => {
    const welcomeElement = screen.getByText(/Welcome to Stinger Guardrails Demo/i);
    expect(welcomeElement).toBeInTheDocument();
  });
});

test('has chat input and send button', async () => {
  // Mock the initial API calls
  mockFetch.mockResolvedValue({
    ok: true,
    json: () => Promise.resolve({
      status: 'healthy',
      enabled_guardrails: 3,
      total_guardrails: 4
    })
  } as Response);

  render(<App />);
  
  await waitFor(() => {
    const inputElement = screen.getByPlaceholderText(/Type your message/i);
    const sendButton = screen.getByRole('button', { name: /Send/i });
    
    expect(inputElement).toBeInTheDocument();
    expect(sendButton).toBeInTheDocument();
  });
});

test('shows settings panel when settings button clicked', async () => {
  // Mock the initial API calls
  mockFetch
    .mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        status: 'healthy',
        enabled_guardrails: 3,
        total_guardrails: 4
      })
    } as Response)
    .mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        input_guardrails: ['pii_filter'],
        output_guardrails: ['content_filter']
      })
    } as Response);

  render(<App />);
  
  await waitFor(() => {
    const settingsButton = screen.getByText(/Show Settings/i);
    fireEvent.click(settingsButton);
  });

  await waitFor(() => {
    const settingsPanel = screen.getByText(/Guardrail Settings/i);
    expect(settingsPanel).toBeInTheDocument();
  });
});

test('displays error when backend is not available', async () => {
  // Mock fetch to throw an error
  mockFetch.mockRejectedValue(new Error('Network error'));

  render(<App />);
  
  await waitFor(() => {
    const errorElement = screen.getByText(/Failed to connect to backend/i);
    expect(errorElement).toBeInTheDocument();
  });
});