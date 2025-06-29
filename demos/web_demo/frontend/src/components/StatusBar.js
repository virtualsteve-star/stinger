import React from 'react';
import styled from 'styled-components';
import { FiWifi, FiShield, FiActivity, FiCheck, FiX } from 'react-icons/fi';

const StatusContainer = styled.div`
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
  padding: 12px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  color: #64748b;
`;

const StatusGroup = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`;

const StatusItem = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
`;

const StatusIcon = styled.div`
  color: ${props => {
    switch (props.status) {
      case 'healthy': return '#10b981';
      case 'warning': return '#f59e0b';
      case 'error': return '#ef4444';
      default: return '#64748b';
    }
  }};
`;

const StatusText = styled.span`
  font-weight: 500;
`;

const Badge = styled.span`
  background: ${props => props.active ? '#dcfce7' : '#fee2e2'};
  color: ${props => props.active ? '#166534' : '#991b1b'};
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

function StatusBar({ systemStatus }) {
  if (!systemStatus) {
    return (
      <StatusContainer>
        <StatusGroup>
          <StatusItem>
            <StatusIcon status="loading">
              <FiActivity />
            </StatusIcon>
            <StatusText>Loading system status...</StatusText>
          </StatusItem>
        </StatusGroup>
      </StatusContainer>
    );
  }

  const isHealthy = systemStatus.status === 'healthy';
  const pipelineLoaded = systemStatus.pipeline_loaded;
  const auditEnabled = systemStatus.audit_enabled;

  return (
    <StatusContainer>
      <StatusGroup>
        <StatusItem>
          <StatusIcon status={isHealthy ? 'healthy' : 'error'}>
            <FiWifi />
          </StatusIcon>
          <StatusText>Backend</StatusText>
          <Badge active={isHealthy}>
            {isHealthy ? 'Online' : 'Offline'}
          </Badge>
        </StatusItem>

        <StatusItem>
          <StatusIcon status={pipelineLoaded ? 'healthy' : 'error'}>
            <FiShield />
          </StatusIcon>
          <StatusText>Guardrails</StatusText>
          <Badge active={pipelineLoaded}>
            {pipelineLoaded ? 'Loaded' : 'Error'}
          </Badge>
        </StatusItem>

        <StatusItem>
          <StatusIcon status={auditEnabled ? 'healthy' : 'warning'}>
            <FiActivity />
          </StatusIcon>
          <StatusText>Audit Trail</StatusText>
          <Badge active={auditEnabled}>
            {auditEnabled ? 'Active' : 'Disabled'}
          </Badge>
        </StatusItem>
      </StatusGroup>

      <StatusGroup>
        <StatusItem>
          <StatusText>
            {systemStatus.enabled_guardrails || 0} of {systemStatus.total_guardrails || 0} guardrails active
          </StatusText>
        </StatusItem>
      </StatusGroup>
    </StatusContainer>
  );
}

export default StatusBar;