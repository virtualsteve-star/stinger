import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { FiActivity, FiRefreshCw, FiEye, FiClock, FiUser, FiMessageSquare } from 'react-icons/fi';
import { format } from 'date-fns';
import { apiService } from '../services/apiService';

const ViewerContainer = styled.div`
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

const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: between;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
`;

const Title = styled.h3`
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1a202c;
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
`;

const RefreshButton = styled.button`
  padding: 8px 12px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #64748b;
  transition: all 0.2s ease;
  
  &:hover {
    background: #f1f5f9;
    border-color: #cbd5e1;
  }
  
  &:disabled {
    cursor: not-allowed;
    opacity: 0.5;
  }
`;

const StatsContainer = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 20px;
`;

const StatCard = styled.div`
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 12px;
  text-align: center;
`;

const StatValue = styled.div`
  font-size: 20px;
  font-weight: 600;
  color: #1a202c;
  margin-bottom: 4px;
`;

const StatLabel = styled.div`
  font-size: 12px;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const LogEntry = styled.div`
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  font-size: 13px;
  transition: all 0.2s ease;
  
  &:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
`;

const LogHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
`;

const EventType = styled.div`
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: ${props => {
    switch (props.type) {
      case 'user_prompt': return '#dbeafe';
      case 'llm_response': return '#dcfce7';
      case 'guardrail_decision': return '#fef3c7';
      case 'audit_trail_enabled': return '#f3e8ff';
      default: return '#f1f5f9';
    }
  }};
  color: ${props => {
    switch (props.type) {
      case 'user_prompt': return '#1e40af';
      case 'llm_response': return '#166534';
      case 'guardrail_decision': return '#92400e';
      case 'audit_trail_enabled': return '#7c3aed';
      default: return '#475569';
    }
  }};
`;

const Timestamp = styled.div`
  color: #64748b;
  font-size: 11px;
  display: flex;
  align-items: center;
  gap: 4px;
`;

const LogContent = styled.div`
  color: #374151;
  line-height: 1.5;
`;

const UserInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 8px 0;
  font-size: 11px;
  color: #64748b;
`;

const DecisionBadge = styled.span`
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 500;
  text-transform: uppercase;
  background: ${props => {
    switch (props.decision) {
      case 'block': return '#fee2e2';
      case 'allow': return '#dcfce7';
      case 'warn': return '#fef3c7';
      default: return '#f1f5f9';
    }
  }};
  color: ${props => {
    switch (props.decision) {
      case 'block': return '#991b1b';
      case 'allow': return '#166534';
      case 'warn': return '#92400e';
      default: return '#475569';
    }
  }};
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #64748b;
  text-align: center;
  gap: 12px;
`;

const LoadingState = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  gap: 12px;
  color: #64748b;
`;

const Spinner = styled.div`
  width: 20px;
  height: 20px;
  border: 2px solid #e2e8f0;
  border-top: 2px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

function AuditLogViewer() {
  const [auditData, setAuditData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const intervalRef = useRef(null);

  useEffect(() => {
    loadAuditLog();
    
    // Auto-refresh every 5 seconds
    intervalRef.current = setInterval(loadAuditLog, 5000);
    
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  const loadAuditLog = async (isRefresh = false) => {
    try {
      if (isRefresh) {
        setRefreshing(true);
      } else if (loading) {
        setLoading(true);
      }
      
      setError(null);
      const data = await apiService.getAuditLog();
      setAuditData(data);
      
    } catch (err) {
      console.error('Failed to load audit log:', err);
      setError(err.message);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    loadAuditLog(true);
  };

  const formatTimestamp = (timestamp) => {
    try {
      const date = new Date(timestamp);
      return format(date, 'HH:mm:ss.SSS');
    } catch {
      return timestamp;
    }
  };

  const renderLogEntry = (record, index) => {
    const eventType = record.event_type || 'unknown';
    
    return (
      <LogEntry key={index}>
        <LogHeader>
          <EventType type={eventType}>
            {eventType === 'user_prompt' && <FiMessageSquare size={10} />}
            {eventType === 'llm_response' && <FiMessageSquare size={10} />}
            {eventType === 'guardrail_decision' && <FiEye size={10} />}
            {eventType === 'audit_trail_enabled' && <FiActivity size={10} />}
            {eventType.replace('_', ' ')}
          </EventType>
          <Timestamp>
            <FiClock size={10} />
            {formatTimestamp(record.timestamp)}
          </Timestamp>
        </LogHeader>

        {(record.user_id || record.conversation_id) && (
          <UserInfo>
            <FiUser size={10} />
            {record.user_id && `User: ${record.user_id}`}
            {record.conversation_id && ` | Conv: ${record.conversation_id.slice(-8)}`}
          </UserInfo>
        )}

        <LogContent>
          {eventType === 'user_prompt' && (
            <div>
              <strong>Prompt:</strong> {record.prompt || 'N/A'}
            </div>
          )}
          
          {eventType === 'llm_response' && (
            <div>
              <strong>Response:</strong> {record.response || 'N/A'}
              {record.model_used && (
                <div style={{ marginTop: '4px', fontSize: '11px', color: '#64748b' }}>
                  Model: {record.model_used}
                </div>
              )}
            </div>
          )}
          
          {eventType === 'guardrail_decision' && (
            <div>
              <div style={{ marginBottom: '6px' }}>
                <strong>Filter:</strong> {record.filter_name || 'N/A'} 
                <DecisionBadge decision={record.decision} style={{ marginLeft: '8px' }}>
                  {record.decision || 'unknown'}
                </DecisionBadge>
              </div>
              {record.reason && (
                <div style={{ fontSize: '11px', color: '#64748b' }}>
                  <strong>Reason:</strong> {record.reason}
                </div>
              )}
              {record.confidence && (
                <div style={{ fontSize: '11px', color: '#64748b' }}>
                  <strong>Confidence:</strong> {(record.confidence * 100).toFixed(1)}%
                </div>
              )}
            </div>
          )}
          
          {eventType === 'audit_trail_enabled' && (
            <div>
              <div><strong>Destination:</strong> {record.destination || 'N/A'}</div>
              <div><strong>PII Redaction:</strong> {record.redact_pii ? 'Enabled' : 'Disabled'}</div>
            </div>
          )}
        </LogContent>
      </LogEntry>
    );
  };

  if (loading) {
    return (
      <ViewerContainer>
        <LoadingState>
          <Spinner />
          Loading audit log...
        </LoadingState>
      </ViewerContainer>
    );
  }

  if (error) {
    return (
      <ViewerContainer>
        <Header>
          <Title>
            <FiActivity />
            Audit Log
          </Title>
          <RefreshButton onClick={handleRefresh} disabled={refreshing}>
            <FiRefreshCw style={{ animation: refreshing ? 'spin 1s linear infinite' : 'none' }} />
            Retry
          </RefreshButton>
        </Header>
        <EmptyState>
          <div style={{ color: '#ef4444', fontSize: '24px' }}>⚠️</div>
          <div>
            <strong>Error loading audit log</strong>
            <div style={{ fontSize: '12px', marginTop: '4px' }}>{error}</div>
          </div>
        </EmptyState>
      </ViewerContainer>
    );
  }

  const totalRecords = auditData?.total_records || 0;
  const recentRecords = auditData?.recent_records || [];

  return (
    <ViewerContainer>
      <Header>
        <Title>
          <FiActivity />
          Audit Log
        </Title>
        <RefreshButton onClick={handleRefresh} disabled={refreshing}>
          <FiRefreshCw style={{ animation: refreshing ? 'spin 1s linear infinite' : 'none' }} />
          Refresh
        </RefreshButton>
      </Header>

      <StatsContainer>
        <StatCard>
          <StatValue>{totalRecords}</StatValue>
          <StatLabel>Total Events</StatLabel>
        </StatCard>
        <StatCard>
          <StatValue>{recentRecords.length}</StatValue>
          <StatLabel>Recent Events</StatLabel>
        </StatCard>
      </StatsContainer>

      {recentRecords.length === 0 ? (
        <EmptyState>
          <FiActivity size={32} style={{ opacity: 0.3 }} />
          <div>
            <strong>No audit events yet</strong>
            <div style={{ fontSize: '12px', marginTop: '4px' }}>
              Start a conversation to see audit trail events appear here
            </div>
          </div>
        </EmptyState>
      ) : (
        <div>
          {recentRecords.map(renderLogEntry)}
          {totalRecords > recentRecords.length && (
            <div style={{ 
              textAlign: 'center', 
              padding: '16px', 
              color: '#64748b', 
              fontSize: '12px' 
            }}>
              Showing {recentRecords.length} of {totalRecords} total events
            </div>
          )}
        </div>
      )}
    </ViewerContainer>
  );
}

export default AuditLogViewer;