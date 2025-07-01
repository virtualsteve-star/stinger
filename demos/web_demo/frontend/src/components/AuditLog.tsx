import React from 'react';

export interface AuditLogEntry {
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

export interface AuditLogResponse {
  status: string;
  recent_records: AuditLogEntry[];
  total_records: number;
  message?: string;
  error?: string;
}

interface AuditLogProps {
  auditLogs: AuditLogResponse | null;
  onClose: () => void;
}

export const AuditLog: React.FC<AuditLogProps> = ({ auditLogs, onClose }) => {
  const formatLogEntry = (entry: AuditLogEntry) => {
    const typeEmoji: { [key: string]: string } = {
      'user_prompt': '👤',
      'llm_response': '🤖',
      'guardrail_decision': '🛡️',
      'audit_trail_enabled': '📋'
    };

    const emoji = typeEmoji[entry.event_type] || '📝';
    const time = new Date(entry.timestamp).toLocaleTimeString();
    
    let content = `${emoji} ${entry.event_type.replace(/_/g, ' ').toUpperCase()}`;
    
    if (entry.filter_name) {
      content += ` - ${entry.filter_name}`;
    }
    
    if (entry.decision) {
      content += ` - Decision: ${entry.decision}`;
    }
    
    if (entry.reason) {
      content += ` - ${entry.reason}`;
    }
    
    return { time, content, entry };
  };

  return (
    <div className="audit-logs-modal">
      <div className="modal-content">
        <div className="modal-header">
          <h2>📋 Audit Logs</h2>
          <button onClick={onClose} className="close-btn">×</button>
        </div>
        
        <div className="logs-list">
          {!auditLogs ? (
            <div className="loading">Loading audit logs...</div>
          ) : auditLogs.error ? (
            <div className="error">Error: {auditLogs.error}</div>
          ) : auditLogs.recent_records.length === 0 ? (
            <div className="no-logs">No audit logs found</div>
          ) : (
            <>
              <div className="logs-summary">
                Total Records: {auditLogs.total_records}
              </div>
              {auditLogs.recent_records.map((log, index) => {
                const { time, content, entry } = formatLogEntry(log);
                return (
                  <div key={index} className="log-entry">
                    <span className="log-time">{time}</span>
                    <span className="log-content">{content}</span>
                    {(entry.prompt || entry.response) && (
                      <div className="log-details">
                        {entry.prompt && <div>Prompt: {entry.prompt.substring(0, 100)}...</div>}
                        {entry.response && <div>Response: {entry.response.substring(0, 100)}...</div>}
                      </div>
                    )}
                  </div>
                );
              })}
            </>
          )}
        </div>
      </div>
    </div>
  );
};