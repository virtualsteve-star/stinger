import React from 'react';
import './LogPanel.css';

interface AuditLogEntry {
  timestamp: string;
  conversation_id?: string;
  event_type: 'user_prompt' | 'llm_response' | 'guardrail_decision' | 'audit_trail_enabled';
  user_id?: string;
  prompt?: string;
  response?: string;
  filter_name?: string;
  decision?: string;
  reason?: string;
  confidence?: number;
  [key: string]: any;
}

interface LogPanelProps {
  isOpen: boolean;
  onClose: () => void;
  logs: AuditLogEntry[];
  onRefresh: () => void;
}

export const LogPanel: React.FC<LogPanelProps> = ({ 
  isOpen, 
  onClose, 
  logs,
  onRefresh 
}) => {
  const getEventIcon = (eventType: string) => {
    switch (eventType) {
      case 'user_prompt': return '👤';
      case 'llm_response': return '🤖';
      case 'guardrail_decision': return '🛡️';
      case 'audit_trail_enabled': return '📋';
      default: return '📝';
    }
  };

  const getDecisionColor = (decision?: string) => {
    switch (decision) {
      case 'block': return '#f44336';
      case 'warn': return '#ff9800';
      case 'allow': return '#4caf50';
      default: return '#666';
    }
  };

  const formatLogEntry = (log: AuditLogEntry) => {
    if (log.event_type === 'guardrail_decision') {
      return (
        <div className="log-guardrail-decision">
          <div className="decision-header">
            <span className="guardrail-name">{log.filter_name}</span>
            <span 
              className="decision-badge" 
              style={{ backgroundColor: getDecisionColor(log.decision) }}
            >
              {log.decision}
            </span>
          </div>
          {log.reason && <div className="decision-reason">{log.reason}</div>}
          {log.confidence && (
            <div className="decision-confidence">
              Confidence: {(log.confidence * 100).toFixed(0)}%
            </div>
          )}
        </div>
      );
    }

    if (log.event_type === 'user_prompt' && log.prompt) {
      return (
        <div className="log-message">
          <div className="message-preview">{log.prompt}</div>
        </div>
      );
    }

    if (log.event_type === 'llm_response' && log.response) {
      return (
        <div className="log-message">
          <div className="message-preview">{log.response}</div>
        </div>
      );
    }

    return <div className="log-generic">Event recorded</div>;
  };

  return (
    <>
      {/* Backdrop */}
      {isOpen && <div className="panel-backdrop" onClick={onClose} />}
      
      {/* Panel */}
      <div className={`slide-panel log-panel ${isOpen ? 'open' : ''}`}>
        <div className="panel-header">
          <h2>📋 Conversation Logs</h2>
          <div className="panel-header-controls">
            <button onClick={onRefresh} className="refresh-btn" title="Refresh">
              🔄
            </button>
            <button className="close-btn" onClick={onClose}>✕</button>
          </div>
        </div>

        <div className="panel-content">
          {logs.length === 0 ? (
            <div className="no-logs">
              <p>No logs for current conversation.</p>
              <p>Send a message to see activity logs.</p>
            </div>
          ) : (
            <div className="logs-timeline">
              {logs.map((log, index) => (
                <div key={index} className={`log-entry ${log.event_type}`}>
                  <div className="log-icon">
                    {getEventIcon(log.event_type)}
                  </div>
                  <div className="log-content">
                    <div className="log-header">
                      <span className="log-type">
                        {log.event_type.replace(/_/g, ' ')}
                      </span>
                      <span className="log-time">
                        {new Date(log.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    {formatLogEntry(log)}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
};