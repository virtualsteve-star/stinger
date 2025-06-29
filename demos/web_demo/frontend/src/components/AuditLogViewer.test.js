import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import AuditLogViewer from './AuditLogViewer';

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
  FaClipboardList: () => <div data-testid="clipboard-icon">Clipboard</div>,
  FaRefresh: () => <div data-testid="refresh-icon">Refresh</div>,
  FaFilter: () => <div data-testid="filter-icon">Filter</div>,
  FaDownload: () => <div data-testid="download-icon">Download</div>,
  FaExclamationCircle: () => <div data-testid="exclamation-icon">Exclamation</div>,
  FaShieldAlt: () => <div data-testid="shield-icon">Shield</div>,
  FaEye: () => <div data-testid="eye-icon">Eye</div>
}));

// Mock date-fns
jest.mock('date-fns', () => ({
  format: jest.fn((date) => '2023-01-01 10:00:00'),
  parseISO: jest.fn((dateString) => new Date(dateString))
}));

describe('AuditLogViewer Component', () => {
  const mockOnRefresh = jest.fn();
  
  const mockAuditData = {
    status: 'active',
    total_records: 150,
    recent_records: [
      {
        id: 1,
        timestamp: '2023-01-01T10:00:00Z',
        event_type: 'chat_message',
        user_id: 'user123',
        content: 'Hello world',
        guardrail_results: {
          blocked: false,
          warnings: [],
          reasons: []
        },
        processing_time_ms: 250
      },
      {
        id: 2,
        timestamp: '2023-01-01T10:01:00Z',
        event_type: 'chat_message',
        user_id: 'user123',
        content: 'My SSN is 123-45-6789',
        guardrail_results: {
          blocked: true,
          warnings: ['PII detected'],
          reasons: ['Social Security Number found']
        },
        processing_time_ms: 340
      },
      {
        id: 3,
        timestamp: '2023-01-01T10:02:00Z',
        event_type: 'settings_change',
        user_id: 'admin',
        content: 'Enabled PII detection',
        guardrail_results: null,
        processing_time_ms: 10
      }
    ]
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders audit log viewer correctly', () => {
    render(
      <AuditLogViewer
        auditData={mockAuditData}
        onRefresh={mockOnRefresh}
        isLoading={false}
      />
    );

    expect(screen.getByText(/Audit Log/i)).toBeInTheDocument();
    expect(screen.getByText(/Total Records: 150/i)).toBeInTheDocument();
  });

  test('displays audit records correctly', () => {
    render(
      <AuditLogViewer
        auditData={mockAuditData}
        onRefresh={mockOnRefresh}
        isLoading={false}
      />
    );

    expect(screen.getByText(/Hello world/i)).toBeInTheDocument();
    expect(screen.getByText(/My SSN is 123-45-6789/i)).toBeInTheDocument();
    expect(screen.getByText(/Enabled PII detection/i)).toBeInTheDocument();
  });

  test('shows blocked messages with correct styling', () => {
    render(
      <AuditLogViewer
        auditData={mockAuditData}
        onRefresh={mockOnRefresh}
        isLoading={false}
      />
    );

    expect(screen.getByText(/blocked/i)).toBeInTheDocument();
    expect(screen.getByText(/PII detected/i)).toBeInTheDocument();
  });

  test('displays processing times', () => {
    render(
      <AuditLogViewer
        auditData={mockAuditData}
        onRefresh={mockOnRefresh}
        isLoading={false}
      />
    );

    expect(screen.getByText(/250ms/i)).toBeInTheDocument();
    expect(screen.getByText(/340ms/i)).toBeInTheDocument();
  });

  test('calls onRefresh when refresh button is clicked', () => {
    render(
      <AuditLogViewer
        auditData={mockAuditData}
        onRefresh={mockOnRefresh}
        isLoading={false}
      />
    );

    const refreshButton = screen.getByRole('button', { name: /refresh/i });
    fireEvent.click(refreshButton);

    expect(mockOnRefresh).toHaveBeenCalled();
  });

  test('shows loading state correctly', () => {
    render(
      <AuditLogViewer
        auditData={mockAuditData}
        onRefresh={mockOnRefresh}
        isLoading={true}
      />
    );

    const refreshButton = screen.getByRole('button', { name: /refresh/i });
    expect(refreshButton).toBeDisabled();
  });

  test('handles empty audit data', () => {
    const emptyAuditData = {
      status: 'active',
      total_records: 0,
      recent_records: []
    };

    render(
      <AuditLogViewer
        auditData={emptyAuditData}
        onRefresh={mockOnRefresh}
        isLoading={false}
      />
    );

    expect(screen.getByText(/No audit records/i)).toBeInTheDocument();
  });

  test('filters records by event type', async () => {
    render(
      <AuditLogViewer
        auditData={mockAuditData}
        onRefresh={mockOnRefresh}
        isLoading={false}
      />
    );

    // Find and use filter dropdown
    const filterSelect = screen.getByLabelText(/filter by event type/i);
    await userEvent.selectOptions(filterSelect, 'chat_message');

    // Should show only chat messages
    expect(screen.getByText(/Hello world/i)).toBeInTheDocument();
    expect(screen.getByText(/My SSN is 123-45-6789/i)).toBeInTheDocument();
    expect(screen.queryByText(/Enabled PII detection/i)).not.toBeInTheDocument();
  });

  test('auto-refreshes data periodically', () => {
    jest.useFakeTimers();

    render(
      <AuditLogViewer
        auditData={mockAuditData}
        onRefresh={mockOnRefresh}
        isLoading={false}
        autoRefresh={true}
      />
    );

    // Clear initial calls
    jest.clearAllMocks();

    // Fast-forward time to trigger auto-refresh
    jest.advanceTimersByTime(5000); // 5 seconds

    expect(mockOnRefresh).toHaveBeenCalled();

    jest.useRealTimers();
  });

  test('displays timestamps in readable format', () => {
    render(
      <AuditLogViewer
        auditData={mockAuditData}
        onRefresh={mockOnRefresh}
        isLoading={false}
      />
    );

    // Timestamps should be formatted (mocked to return consistent format)
    expect(screen.getAllByText(/2023-01-01 10:00:00/)).toHaveLength(3);
  });

  test('handles different event types correctly', () => {
    render(
      <AuditLogViewer
        auditData={mockAuditData}
        onRefresh={mockOnRefresh}
        isLoading={false}
      />
    );

    expect(screen.getByText(/chat_message/i)).toBeInTheDocument();
    expect(screen.getByText(/settings_change/i)).toBeInTheDocument();
  });

  test('shows warning indicators for messages with warnings', () => {
    render(
      <AuditLogViewer
        auditData={mockAuditData}
        onRefresh={mockOnRefresh}
        isLoading={false}
      />
    );

    // Should show warning indicators for records with warnings
    expect(screen.getByText(/PII detected/i)).toBeInTheDocument();
  });

  test('handles long content with truncation', () => {
    const longContentData = {
      ...mockAuditData,
      recent_records: [
        {
          id: 1,
          timestamp: '2023-01-01T10:00:00Z',
          event_type: 'chat_message',
          user_id: 'user123',
          content: 'A'.repeat(200), // Very long content
          guardrail_results: {
            blocked: false,
            warnings: [],
            reasons: []
          },
          processing_time_ms: 250
        }
      ]
    };

    render(
      <AuditLogViewer
        auditData={longContentData}
        onRefresh={mockOnRefresh}
        isLoading={false}
      />
    );

    // Content should be truncated or have expand/collapse functionality
    const longContent = screen.getByText(/A{50,}/); // At least 50 A's
    expect(longContent).toBeInTheDocument();
  });

  test('exports audit data when export button is clicked', () => {
    // Mock URL.createObjectURL and link click
    const mockCreateObjectURL = jest.fn();
    const mockClick = jest.fn();
    const mockRevokeObjectURL = jest.fn();

    global.URL.createObjectURL = mockCreateObjectURL;
    global.URL.revokeObjectURL = mockRevokeObjectURL;

    // Mock document.createElement to return a mock link
    const originalCreateElement = document.createElement;
    document.createElement = jest.fn((tagName) => {
      if (tagName === 'a') {
        return {
          href: '',
          download: '',
          click: mockClick,
          style: {}
        };
      }
      return originalCreateElement.call(document, tagName);
    });

    render(
      <AuditLogViewer
        auditData={mockAuditData}
        onRefresh={mockOnRefresh}
        isLoading={false}
      />
    );

    const exportButton = screen.getByRole('button', { name: /export/i });
    fireEvent.click(exportButton);

    expect(mockCreateObjectURL).toHaveBeenCalled();
    expect(mockClick).toHaveBeenCalled();

    // Restore original createElement
    document.createElement = originalCreateElement;
  });

  test('keyboard navigation works correctly', () => {
    render(
      <AuditLogViewer
        auditData={mockAuditData}
        onRefresh={mockOnRefresh}
        isLoading={false}
      />
    );

    const refreshButton = screen.getByRole('button', { name: /refresh/i });
    
    // Test keyboard activation
    refreshButton.focus();
    fireEvent.keyDown(refreshButton, { key: 'Enter' });

    expect(mockOnRefresh).toHaveBeenCalled();
  });

  test('shows audit status correctly', () => {
    render(
      <AuditLogViewer
        auditData={mockAuditData}
        onRefresh={mockOnRefresh}
        isLoading={false}
      />
    );

    expect(screen.getByText(/Status: active/i)).toBeInTheDocument();
  });

  test('handles audit system errors gracefully', () => {
    const errorAuditData = {
      status: 'error',
      total_records: 0,
      recent_records: [],
      error: 'Audit system unavailable'
    };

    render(
      <AuditLogViewer
        auditData={errorAuditData}
        onRefresh={mockOnRefresh}
        isLoading={false}
      />
    );

    expect(screen.getByText(/error/i)).toBeInTheDocument();
    expect(screen.getByText(/Audit system unavailable/i)).toBeInTheDocument();
  });
});