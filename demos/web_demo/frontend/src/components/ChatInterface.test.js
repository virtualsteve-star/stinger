import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import ChatInterface from './ChatInterface';

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
  FaPaperPlane: () => <div data-testid="send-icon">Send</div>,
  FaRobot: () => <div data-testid="robot-icon">Robot</div>,
  FaUser: () => <div data-testid="user-icon">User</div>,
  FaExclamationTriangle: () => <div data-testid="warning-icon">Warning</div>,
  FaShieldAlt: () => <div data-testid="shield-icon">Shield</div>
}));

describe('ChatInterface Component', () => {
  const mockOnSendMessage = jest.fn();
  const mockMessages = [
    {
      id: 1,
      type: 'user',
      content: 'Hello there!',
      timestamp: new Date('2023-01-01T10:00:00Z')
    },
    {
      id: 2,
      type: 'assistant',
      content: 'Hello! How can I help you today?',
      timestamp: new Date('2023-01-01T10:00:01Z'),
      blocked: false,
      warnings: [],
      reasons: []
    }
  ];

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders chat interface correctly', () => {
    render(
      <ChatInterface
        messages={mockMessages}
        onSendMessage={mockOnSendMessage}
        isLoading={false}
      />
    );

    expect(screen.getByPlaceholderText(/Type your message here/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
  });

  test('displays messages correctly', () => {
    render(
      <ChatInterface
        messages={mockMessages}
        onSendMessage={mockOnSendMessage}
        isLoading={false}
      />
    );

    expect(screen.getByText('Hello there!')).toBeInTheDocument();
    expect(screen.getByText('Hello! How can I help you today?')).toBeInTheDocument();
  });

  test('sends message when send button is clicked', async () => {
    render(
      <ChatInterface
        messages={[]}
        onSendMessage={mockOnSendMessage}
        isLoading={false}
      />
    );

    const input = screen.getByPlaceholderText(/Type your message here/i);
    const sendButton = screen.getByRole('button', { name: /send/i });

    await userEvent.type(input, 'Test message');
    fireEvent.click(sendButton);

    expect(mockOnSendMessage).toHaveBeenCalledWith('Test message');
  });

  test('sends message when Enter key is pressed', async () => {
    render(
      <ChatInterface
        messages={[]}
        onSendMessage={mockOnSendMessage}
        isLoading={false}
      />
    );

    const input = screen.getByPlaceholderText(/Type your message here/i);
    
    await userEvent.type(input, 'Test message{enter}');

    expect(mockOnSendMessage).toHaveBeenCalledWith('Test message');
  });

  test('prevents sending empty messages', async () => {
    render(
      <ChatInterface
        messages={[]}
        onSendMessage={mockOnSendMessage}
        isLoading={false}
      />
    );

    const sendButton = screen.getByRole('button', { name: /send/i });
    fireEvent.click(sendButton);

    expect(mockOnSendMessage).not.toHaveBeenCalled();
  });

  test('clears input after sending message', async () => {
    render(
      <ChatInterface
        messages={[]}
        onSendMessage={mockOnSendMessage}
        isLoading={false}
      />
    );

    const input = screen.getByPlaceholderText(/Type your message here/i);
    const sendButton = screen.getByRole('button', { name: /send/i });

    await userEvent.type(input, 'Test message');
    fireEvent.click(sendButton);

    expect(input.value).toBe('');
  });

  test('shows loading state correctly', () => {
    render(
      <ChatInterface
        messages={[]}
        onSendMessage={mockOnSendMessage}
        isLoading={true}
      />
    );

    const sendButton = screen.getByRole('button', { name: /send/i });
    expect(sendButton).toBeDisabled();
  });

  test('displays blocked messages correctly', () => {
    const blockedMessages = [
      {
        id: 1,
        type: 'user',
        content: 'My SSN is 123-45-6789',
        timestamp: new Date()
      },
      {
        id: 2,
        type: 'assistant',
        content: 'Message blocked due to PII',
        timestamp: new Date(),
        blocked: true,
        warnings: ['PII detected'],
        reasons: ['Social Security Number found']
      }
    ];

    render(
      <ChatInterface
        messages={blockedMessages}
        onSendMessage={mockOnSendMessage}
        isLoading={false}
      />
    );

    expect(screen.getByText(/blocked/i)).toBeInTheDocument();
    expect(screen.getByText(/PII detected/i)).toBeInTheDocument();
  });

  test('displays warnings correctly', () => {
    const warningMessages = [
      {
        id: 1,
        type: 'user',
        content: 'I hate this service',
        timestamp: new Date()
      },
      {
        id: 2,
        type: 'assistant',
        content: 'I apologize for the frustration.',
        timestamp: new Date(),
        blocked: false,
        warnings: ['Sentiment: Negative'],
        reasons: []
      }
    ];

    render(
      <ChatInterface
        messages={warningMessages}
        onSendMessage={mockOnSendMessage}
        isLoading={false}
      />
    );

    expect(screen.getByText(/Sentiment: Negative/i)).toBeInTheDocument();
  });

  test('handles long messages correctly', async () => {
    const longMessage = 'A'.repeat(1000);
    
    render(
      <ChatInterface
        messages={[]}
        onSendMessage={mockOnSendMessage}
        isLoading={false}
      />
    );

    const input = screen.getByPlaceholderText(/Type your message here/i);
    
    await userEvent.type(input, longMessage);
    fireEvent.click(screen.getByRole('button', { name: /send/i }));

    expect(mockOnSendMessage).toHaveBeenCalledWith(longMessage);
  });

  test('auto-scrolls to bottom when new messages arrive', () => {
    const { rerender } = render(
      <ChatInterface
        messages={mockMessages}
        onSendMessage={mockOnSendMessage}
        isLoading={false}
      />
    );

    // Mock scrollIntoView
    const mockScrollIntoView = jest.fn();
    Element.prototype.scrollIntoView = mockScrollIntoView;

    const newMessages = [
      ...mockMessages,
      {
        id: 3,
        type: 'user',
        content: 'New message',
        timestamp: new Date()
      }
    ];

    rerender(
      <ChatInterface
        messages={newMessages}
        onSendMessage={mockOnSendMessage}
        isLoading={false}
      />
    );

    // Should scroll to bottom when new message is added
    expect(mockScrollIntoView).toHaveBeenCalled();
  });

  test('handles special characters in messages', async () => {
    const specialMessage = 'Hello 🌟 world! Special chars: áéíóú çñü';
    
    render(
      <ChatInterface
        messages={[]}
        onSendMessage={mockOnSendMessage}
        isLoading={false}
      />
    );

    const input = screen.getByPlaceholderText(/Type your message here/i);
    
    await userEvent.type(input, specialMessage);
    fireEvent.click(screen.getByRole('button', { name: /send/i }));

    expect(mockOnSendMessage).toHaveBeenCalledWith(specialMessage);
  });

  test('keyboard shortcuts work correctly', async () => {
    render(
      <ChatInterface
        messages={[]}
        onSendMessage={mockOnSendMessage}
        isLoading={false}
      />
    );

    const input = screen.getByPlaceholderText(/Type your message here/i);
    
    // Test Ctrl+Enter (should also send message)
    await userEvent.type(input, 'Test message');
    fireEvent.keyDown(input, { key: 'Enter', ctrlKey: true });

    expect(mockOnSendMessage).toHaveBeenCalledWith('Test message');
  });

  test('message timestamps are displayed correctly', () => {
    const messageWithTimestamp = [
      {
        id: 1,
        type: 'user',
        content: 'Hello',
        timestamp: new Date('2023-01-01T10:00:00Z')
      }
    ];

    render(
      <ChatInterface
        messages={messageWithTimestamp}
        onSendMessage={mockOnSendMessage}
        isLoading={false}
      />
    );

    // Check that timestamp is displayed (format may vary)
    expect(screen.getByText(/10:00/)).toBeInTheDocument();
  });
});