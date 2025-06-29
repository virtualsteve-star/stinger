import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FiShield, FiSettings, FiRefreshCw, FiActivity, FiMessageCircle } from 'react-icons/fi';
import apiService from '../services/apiService';

const HeaderContainer = styled.header`
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  color: white;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 100;
`;

const LeftSection = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 700;
`;

const LogoIcon = styled.div`
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const ConversationInfo = styled.div`
  background: rgba(255, 255, 255, 0.1);
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  backdrop-filter: blur(10px);
`;

const StatusDot = styled.div`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: ${props => props.active ? '#10b981' : '#64748b'};
  flex-shrink: 0;
`;

const RightSection = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const StatusIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  font-size: 12px;
  backdrop-filter: blur(10px);
`;

const ActionButton = styled.button`
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.2s ease;
  backdrop-filter: blur(10px);
  
  &:hover {
    background: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.3);
  }
  
  @media (max-width: 768px) {
    padding: 8px;
    
    span {
      display: none;
    }
  }
`;

const MobileMenuButton = styled.button`
  background: transparent;
  border: none;
  color: white;
  padding: 8px;
  border-radius: 6px;
  cursor: pointer;
  display: none;
  align-items: center;
  justify-content: center;
  transition: background 0.2s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
  }
  
  @media (max-width: 768px) {
    display: flex;
  }
`;

const ConnectionStatus = styled.div`
  background: rgba(255, 255, 255, 0.1);
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  backdrop-filter: blur(10px);
`;

const ConversationBadge = styled.div`
  background: ${props => props.inactive ? '#64748b' : '#10b981'};
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  color: white;
`;

const ConversationStats = styled.div`
  font-size: 12px;
  color: #64748b;
`;

const ResetButton = styled.button`
  background: transparent;
  border: none;
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.2s ease;
  backdrop-filter: blur(10px);
  
  &:hover {
    background: rgba(255, 255, 255, 0.2);
  }
  
  @media (max-width: 768px) {
    padding: 8px;
    
    span {
      display: none;
    }
  }
`;

const GuardrailStatus = styled.div`
  background: rgba(255, 255, 255, 0.1);
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  backdrop-filter: blur(10px);
`;

const SettingsButton = styled.button`
  background: transparent;
  border: none;
  color: white;
  padding: 8px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
  }
  
  @media (max-width: 768px) {
    display: flex;
  }
`;

function Header({ onToggleSettings, systemStatus, conversation, onResetConversation }) {
  const [connectionStatus, setConnectionStatus] = useState('connected');
  
  // Monitor connection status
  useEffect(() => {
    const checkConnection = async () => {
      try {
        await apiService.getSystemStatus();
        setConnectionStatus('connected');
      } catch (err) {
        setConnectionStatus('disconnected');
      }
    };
    
    // Check connection every 10 seconds
    const interval = setInterval(checkConnection, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <HeaderContainer>
      <LeftSection>
        <Logo>
          <FiShield size={24} />
          <span>Stinger Guardrails</span>
        </Logo>
        
        {/* Connection status indicator */}
        <ConnectionStatus>
          <div style={{ 
            width: '8px', 
            height: '8px', 
            borderRadius: '50%', 
            background: connectionStatus === 'connected' ? '#10b981' : '#ef4444',
            marginRight: '6px'
          }} />
          {connectionStatus === 'connected' ? 'Connected' : 'Disconnected'}
        </ConnectionStatus>
      </LeftSection>
      
      <RightSection>
        <ConversationInfo>
          {conversation ? (
            <>
              <ConversationBadge>
                <FiMessageCircle size={14} />
                Conversation Active
              </ConversationBadge>
              <ConversationStats>
                {conversation.turn_count || 0} turns • {conversation.duration || 0}s
              </ConversationStats>
              <ResetButton onClick={onResetConversation}>
                <FiRefreshCw size={14} />
                Reset
              </ResetButton>
            </>
          ) : (
            <ConversationBadge inactive>
              <FiMessageCircle size={14} />
              No Active Conversation
            </ConversationBadge>
          )}
        </ConversationInfo>
        
        <GuardrailStatus>
          <FiShield size={16} />
          {systemStatus?.enabled_guardrails || 0}/{systemStatus?.total_guardrails || 0} active
        </GuardrailStatus>
        
        <SettingsButton onClick={onToggleSettings}>
          <FiSettings size={18} />
        </SettingsButton>

        <MobileMenuButton onClick={onToggleSettings}>
          <FiSettings size={18} />
        </MobileMenuButton>
      </RightSection>
    </HeaderContainer>
  );
}

export default Header;