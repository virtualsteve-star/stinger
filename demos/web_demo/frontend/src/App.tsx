import React, { useState, useEffect } from 'react';
import './App.css';

interface ChatMessage {
  content: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
}

interface SystemStatus {
  status: string;
  enabled_guardrails: number;
  total_guardrails: number;
}

interface GuardrailSettings {
  input_guardrails: { name: string; enabled: boolean; }[];
  output_guardrails: { name: string; enabled: boolean; }[];
}

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
  [key: string]: any; // For any additional fields
}

interface AuditLogResponse {
  status: string;
  recent_records: AuditLogEntry[];
  total_records: number;
  message?: string;
  error?: string;
}

function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [settings, setSettings] = useState<GuardrailSettings | null>(null);
  const [auditLogs, setAuditLogs] = useState<AuditLogEntry[]>([]);
  const [showLogs, setShowLogs] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSystemData();
  }, []);

  const loadSystemData = async () => {
    try {
      const [statusRes, settingsRes] = await Promise.all([
        fetch('/api/health'),
        fetch('/api/guardrails')
      ]);
      
      if (statusRes.ok) {
        setSystemStatus(await statusRes.json());
      }
      
      if (settingsRes.ok) {
        setSettings(await settingsRes.json());
      }
      
      setError(null);
    } catch (err) {
      setError('Failed to connect to backend. Please ensure the server is running on port 8000.');
    }
  };

  const loadAuditLogs = async () => {
    try {
      const response = await fetch('/api/audit_log');
      if (response.ok) {
        const auditData: AuditLogResponse = await response.json();
        if (auditData.status === 'enabled') {
          setAuditLogs(auditData.recent_records || []);
        } else {
          setAuditLogs([]);
        }
      }
    } catch (err) {
      console.error('Failed to load audit logs:', err);
      setAuditLogs([]);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || loading) return;

    const userMessage: ChatMessage = {
      content: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: inputMessage })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      
      const assistantMessage: ChatMessage = {
        content: data.content || 'No response received',
        sender: 'assistant',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      if (data.warnings && data.warnings.length > 0) {
        console.log('Guardrail warnings:', data.warnings);
      }

      // Refresh audit logs after sending a message
      loadAuditLogs();
      
    } catch (err) {
      setError(`Failed to send message: ${err instanceof Error ? err.message : 'Unknown error'}`);
      
      const errorMessage: ChatMessage = {
        content: 'Sorry, I encountered an error processing your message.',
        sender: 'assistant',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const resetConversation = async () => {
    try {
      await fetch('/api/conversation/reset', { method: 'POST' });
      setMessages([]);
      setError(null);
    } catch (err) {
      setError('Failed to reset conversation');
    }
  };

  const toggleGuardrail = async (guardrail: string, type: 'input' | 'output', enabled: boolean) => {
    try {
      const currentSettings = settings!;
      const newSettings = { ...currentSettings };
      
      if (type === 'input') {
        newSettings.input_guardrails = newSettings.input_guardrails.map(g => 
          g.name === guardrail ? { ...g, enabled } : g
        );
      } else {
        newSettings.output_guardrails = newSettings.output_guardrails.map(g => 
          g.name === guardrail ? { ...g, enabled } : g
        );
      }

      const response = await fetch('/api/guardrails', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newSettings)
      });

      if (response.ok) {
        setSettings(newSettings);
        loadSystemData(); // Refresh status
      }
    } catch (err) {
      setError('Failed to update guardrail settings');
    }
  };

  const formatGuardrailName = (name: string) => {
    const nameMap: { [key: string]: string } = {
      'pii_check': 'PII Detection',
      'toxicity_check': 'Content Filter', 
      'length_check': 'Length Validation',
      'code_generation_check': 'Code Generation Filter'
    };
    return nameMap[name] || name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  return (
    <div className="app">
      <header className="header">
        <h1>🛡️ Stinger Guardrails Demo</h1>
        <div className="header-controls">
          <button onClick={() => { setShowLogs(true); loadAuditLogs(); }} className="logs-btn">
            Audit Logs
          </button>
          <button onClick={resetConversation} className="reset-btn">
            Reset Chat
          </button>
        </div>
      </header>

      {error && (
        <div className="error">
          ⚠️ {error}
          <button onClick={loadSystemData}>Retry</button>
        </div>
      )}

      <div className="main">
        {/* Main Chat Interface */}
        <div className="chat-container">
          <div className="messages">
            {messages.length === 0 && (
              <div className="welcome">
                <h2>Welcome to Stinger Guardrails Demo</h2>
                <p>Try sending a message to see how guardrails protect your conversations.</p>
                <p>Examples:</p>
                <ul>
                  <li>"My email is test@example.com" (PII detection)</li>
                  <li>"How do I hack a system?" (Content filter)</li>
                  <li>"Tell me something inappropriate" (Content filter)</li>
                  <li>"Write code to delete files" (Code generation filter)</li>
                </ul>
              </div>
            )}
            
            {messages.map((message, index) => (
              <div key={index} className={`message ${message.sender}`}>
                <div className="message-content">{message.content}</div>
                <div className="message-time">
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>
            ))}
            
            {loading && (
              <div className="message assistant">
                <div className="message-content typing">Thinking...</div>
              </div>
            )}
          </div>

          <div className="input-area">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Type your message..."
              disabled={loading}
            />
            <button onClick={sendMessage} disabled={loading || !inputMessage.trim()}>
              Send
            </button>
          </div>
        </div>

        {/* Fixed Guardrails Sidebar */}
        <div className="guardrails-sidebar">
          <div className="sidebar-header">
            <h2>Guardrails</h2>
            {systemStatus && (
              <span className="status-badge">
                {systemStatus.enabled_guardrails}/{systemStatus.total_guardrails} active
              </span>
            )}
          </div>
          
          {!settings ? (
            <div className="loading-message">Loading...</div>
          ) : (
            <div className="sidebar-content">
              <div className="filter-section">
                <h3>▼ Input Filters</h3>
                <div className="filters">
                  {settings.input_guardrails?.map(guardrail => (
                    <label key={guardrail.name} className="filter-toggle">
                      <input
                        type="checkbox"
                        checked={guardrail.enabled}
                        onChange={(e) => toggleGuardrail(guardrail.name, 'input', e.target.checked)}
                      />
                      <span className="filter-name">{formatGuardrailName(guardrail.name)}</span>
                    </label>
                  )) || <p>No input filters</p>}
                </div>
              </div>

              <div className="filter-section">
                <h3>▼ Output Filters</h3>
                <div className="filters">
                  {settings.output_guardrails?.map(guardrail => (
                    <label key={guardrail.name} className="filter-toggle">
                      <input
                        type="checkbox"
                        checked={guardrail.enabled}
                        onChange={(e) => toggleGuardrail(guardrail.name, 'output', e.target.checked)}
                      />
                      <span className="filter-name">{formatGuardrailName(guardrail.name)}</span>
                    </label>
                  )) || <p>No output filters</p>}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Audit Logs Slide-out Panel */}
      <div className={`slide-panel logs-panel ${showLogs ? 'open' : ''}`}>
        <div className="panel-header">
          <h2>📋 Audit Logs</h2>
          <div className="panel-header-controls">
            <button onClick={loadAuditLogs} className="refresh-btn">
              🔄 Refresh
            </button>
            <button className="close-btn" onClick={() => setShowLogs(false)}>
              ✕
            </button>
          </div>
        </div>
        
        <div className="panel-content">
          {auditLogs.length === 0 ? (
            <div className="no-logs">
              <p>No audit logs available.</p>
              <p>Send a message to generate audit entries.</p>
            </div>
          ) : (
            <div className="logs-list">
              {auditLogs.map((log, index) => (
                <div key={index} className={`log-entry ${log.event_type}`}>
                  <div className="log-header">
                    <span className="log-type">{log.event_type.replace('_', ' ')}</span>
                    <span className="log-time">
                      {new Date(log.timestamp).toLocaleString()}
                    </span>
                  </div>
                  <div className="log-content">
                    {log.prompt && (
                      <div className="log-message">
                        <strong>User Message:</strong> {log.prompt}
                      </div>
                    )}
                    {log.response && (
                      <div className="log-message">
                        <strong>AI Response:</strong> {log.response.length > 100 ? log.response.substring(0, 100) + '...' : log.response}
                      </div>
                    )}
                    {log.filter_name && (
                      <div className="log-meta">
                        <strong>Filter:</strong> {formatGuardrailName(log.filter_name)} 
                        <span className={`decision ${log.decision}`}>
                          ({log.decision})
                        </span>
                      </div>
                    )}
                    {log.reason && (
                      <div className="log-meta">
                        <strong>Reason:</strong> {log.reason}
                      </div>
                    )}
                    {log.confidence !== undefined && (
                      <div className="log-meta">
                        <strong>Confidence:</strong> {(log.confidence * 100).toFixed(1)}%
                      </div>
                    )}
                    {log.conversation_id && (
                      <div className="log-meta">
                        <strong>Conversation:</strong> {log.conversation_id.substring(0, 8)}...
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Overlay when panels are open */}
      {showLogs && (
        <div 
          className="panel-overlay" 
          onClick={() => setShowLogs(false)}
        />
      )}
    </div>
  );
}

export default App;