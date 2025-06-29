import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import ChatInterface from './components/ChatInterface';
import SettingsPanel from './components/SettingsPanel';
import AuditLogViewer from './components/AuditLogViewer';
import Header from './components/Header';
import StatusBar from './components/StatusBar';
import { apiService } from './services/apiService';

const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  font-family: 'Inter', sans-serif;
`;

const MainContent = styled.div`
  display: flex;
  flex: 1;
  overflow: hidden;
`;

const LeftPanel = styled.div`
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
`;

const RightPanel = styled.div`
  width: 350px;
  background: white;
  border-left: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  
  @media (max-width: 768px) {
    position: fixed;
    top: 0;
    right: ${props => props.isOpen ? '0' : '-350px'};
    width: 300px;
    height: 100vh;
    z-index: 1000;
    transition: right 0.3s ease;
    box-shadow: ${props => props.isOpen ? '-4px 0 20px rgba(0,0,0,0.1)' : 'none'};
  }
`;

const MobileOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
  display: ${props => props.show ? 'block' : 'none'};
  
  @media (min-width: 769px) {
    display: none;
  }
`;

const TabContainer = styled.div`
  display: flex;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
`;

const Tab = styled.button`
  flex: 1;
  padding: 12px 16px;
  border: none;
  background: ${props => props.active ? 'white' : 'transparent'};
  color: ${props => props.active ? '#1a202c' : '#64748b'};
  font-weight: ${props => props.active ? '600' : '400'};
  font-size: 14px;
  cursor: pointer;
  border-bottom: 2px solid ${props => props.active ? '#3b82f6' : 'transparent'};
  transition: all 0.2s ease;
  
  &:hover {
    background: ${props => props.active ? 'white' : '#f1f5f9'};
    color: ${props => props.active ? '#1a202c' : '#475569'};
  }
`;

function App() {
  const [conversation, setConversation] = useState(null);
  const [settings, setSettings] = useState(null);
  const [systemStatus, setSystemStatus] = useState(null);
  const [rightPanelOpen, setRightPanelOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('settings');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);
  const [isRetrying, setIsRetrying] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('connecting'); // 'connecting', 'connected', 'disconnected'

  // Initialize app
  useEffect(() => {
    initializeApp();
  }, []);

  // Auto-retry connection every 5 seconds if disconnected
  useEffect(() => {
    if (connectionStatus === 'disconnected' && !loading && !isRetrying) {
      const timer = setTimeout(() => {
        console.log('🔄 Auto-retrying connection...');
        handleRetry();
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [connectionStatus, loading, isRetrying]);

  const initializeApp = async () => {
    try {
      setLoading(true);
      setError(null);
      setConnectionStatus('connecting');
      
      // Load initial data
      const [statusData, settingsData] = await Promise.all([
        apiService.getSystemStatus(),
        apiService.getGuardrailSettings()
      ]);
      
      setSystemStatus(statusData);
      setSettings(settingsData);
      setConnectionStatus('connected');
      setRetryCount(0); // Reset retry count on success
      
    } catch (err) {
      console.error('Failed to initialize app:', err);
      setConnectionStatus('disconnected');
      
      // Provide specific error messages based on error type
      let errorMessage = 'Failed to connect to Stinger backend.';
      
      if (err.message.includes('Network error') || err.message.includes('ECONNREFUSED')) {
        errorMessage = 'Cannot connect to the backend server. Please ensure the backend is running on port 8000.';
      } else if (err.message.includes('timeout')) {
        errorMessage = 'Connection timed out. The backend may be overloaded or not responding.';
      } else if (err.message.includes('SSL') || err.message.includes('certificate')) {
        errorMessage = 'SSL certificate error. Please accept the self-signed certificate in your browser.';
      } else if (err.message.includes('404')) {
        errorMessage = 'Backend API not found. The backend may be running but not serving the expected endpoints.';
      } else if (err.message.includes('500')) {
        errorMessage = 'Backend server error. The server may have crashed or encountered an internal error.';
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = async () => {
    if (isRetrying) return;
    
    setIsRetrying(true);
    setRetryCount(prev => prev + 1);
    
    try {
      await initializeApp();
    } catch (err) {
      console.error('Retry failed:', err);
    } finally {
      setIsRetrying(false);
    }
  };

  const handleSendMessage = async (message) => {
    try {
      const response = await apiService.sendChatMessage({
        content: message,
        conversation_id: conversation?.conversation_id
      });
      
      // Update conversation info
      const conversationInfo = await apiService.getConversationInfo();
      setConversation(conversationInfo);
      
      return response;
    } catch (err) {
      console.error('Failed to send message:', err);
      // Check if this is a connection error
      if (err.message.includes('Network error') || err.message.includes('ECONNREFUSED')) {
        setConnectionStatus('disconnected');
        setError('Lost connection to backend. Please check if the server is still running.');
      }
      throw err;
    }
  };

  const handleSettingsChange = async (newSettings) => {
    console.log('🚀 handleSettingsChange called with:', newSettings);
    try {
      console.log('🚀 Calling apiService.updateGuardrailSettings...');
      await apiService.updateGuardrailSettings(newSettings);

      // Wait a moment to ensure backend updates are processed
      setTimeout(async () => {
        console.log('🚀 Refreshing settings and status...');
        const [settingsData, statusData] = await Promise.all([
          apiService.getGuardrailSettings(),
          apiService.getSystemStatus()
        ]);
        setSettings(settingsData);
        setSystemStatus(statusData);
      }, 300); // 300ms delay
    } catch (err) {
      console.error('🚀 Failed to update settings:', err);
      // Check if this is a connection error
      if (err.message.includes('Network error') || err.message.includes('ECONNREFUSED')) {
        setConnectionStatus('disconnected');
        setError('Lost connection to backend while saving settings. Please check if the server is still running.');
      }
      throw err;
    }
  };

  const handlePresetChange = async (preset) => {
    try {
      await apiService.loadPreset({ preset });
      
      // Refresh settings and status
      const [settingsData, statusData] = await Promise.all([
        apiService.getGuardrailSettings(),
        apiService.getSystemStatus()
      ]);
      
      setSettings(settingsData);
      setSystemStatus(statusData);
      
    } catch (err) {
      console.error('Failed to load preset:', err);
      throw err;
    }
  };

  const handleResetConversation = async () => {
    try {
      await apiService.resetConversation();
      setConversation(null);
    } catch (err) {
      console.error('Failed to reset conversation:', err);
      throw err;
    }
  };

  const toggleRightPanel = () => {
    setRightPanelOpen(!rightPanelOpen);
  };

  if (loading) {
    return (
      <AppContainer>
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: '100vh',
          flexDirection: 'column',
          gap: '16px'
        }}>
          <div style={{ 
            width: '40px', 
            height: '40px', 
            border: '4px solid #e2e8f0', 
            borderTop: '4px solid #3b82f6',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite'
          }} />
          <p style={{ color: '#64748b', fontSize: '14px' }}>Loading Stinger Web Demo...</p>
        </div>
      </AppContainer>
    );
  }

  if (error) {
    return (
      <AppContainer>
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: '100vh',
          flexDirection: 'column',
          gap: '16px',
          padding: '20px',
          textAlign: 'center'
        }}>
          <div style={{ 
            color: '#ef4444', 
            fontSize: '48px',
            marginBottom: '8px'
          }}>⚠️</div>
          <h2 style={{ color: '#1a202c', margin: '0 0 8px 0' }}>Connection Error</h2>
          <p style={{ color: '#64748b', margin: '0 0 16px 0', maxWidth: '500px' }}>{error}</p>
          
          {/* Connection status and retry info */}
          <div style={{ 
            background: '#f8fafc', 
            padding: '12px 16px', 
            borderRadius: '8px', 
            border: '1px solid #e2e8f0',
            marginBottom: '16px',
            fontSize: '14px',
            color: '#64748b'
          }}>
            <div>Status: <strong style={{ color: connectionStatus === 'connected' ? '#059669' : '#dc2626' }}>
              {connectionStatus === 'connected' ? 'Connected' : 'Disconnected'}
            </strong></div>
            {retryCount > 0 && (
              <div>Retry attempts: <strong>{retryCount}</strong></div>
            )}
            {connectionStatus === 'disconnected' && !isRetrying && (
              <div style={{ marginTop: '8px', fontSize: '12px' }}>
                Auto-retrying in 5 seconds...
              </div>
            )}
          </div>
          
          {/* Action buttons */}
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', justifyContent: 'center' }}>
            <button 
              onClick={handleRetry}
              disabled={isRetrying}
              style={{
                padding: '12px 24px',
                background: isRetrying ? '#e2e8f0' : '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: isRetrying ? 'not-allowed' : 'pointer',
                fontSize: '14px',
                fontWeight: '500',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              {isRetrying ? (
                <>
                  <div style={{ 
                    width: '16px', 
                    height: '16px', 
                    border: '2px solid #ffffff', 
                    borderTop: '2px solid transparent',
                    borderRadius: '50%',
                    animation: 'spin 1s linear infinite'
                  }} />
                  Retrying...
                </>
              ) : (
                'Retry Connection'
              )}
            </button>
            
            <button 
              onClick={() => window.location.reload()}
              style={{
                padding: '12px 24px',
                background: '#f8fafc',
                color: '#374151',
                border: '1px solid #d1d5db',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '500'
              }}
            >
              Reload Page
            </button>
          </div>
          
          {/* Troubleshooting tips */}
          <div style={{ 
            marginTop: '24px', 
            padding: '16px', 
            background: '#fef3c7', 
            border: '1px solid #f59e0b',
            borderRadius: '8px',
            maxWidth: '500px',
            textAlign: 'left'
          }}>
            <h4 style={{ margin: '0 0 8px 0', color: '#92400e' }}>Troubleshooting Tips:</h4>
            <ul style={{ margin: '0', paddingLeft: '20px', color: '#92400e', fontSize: '14px' }}>
              <li>Ensure the backend server is running on port 8000</li>
              <li>Check if the backend crashed or encountered an error</li>
              <li>Accept any SSL certificate warnings in your browser</li>
              <li>Try refreshing the page or restarting the backend</li>
            </ul>
          </div>
        </div>
      </AppContainer>
    );
  }

  return (
    <AppContainer>
      <Header 
        onToggleSettings={toggleRightPanel}
        systemStatus={systemStatus}
        conversation={conversation}
        onResetConversation={handleResetConversation}
      />
      
      <MainContent>
        <LeftPanel>
          <ChatInterface 
            onSendMessage={handleSendMessage}
            conversation={conversation}
          />
          <StatusBar systemStatus={systemStatus} />
        </LeftPanel>
        
        <RightPanel isOpen={rightPanelOpen}>
          <TabContainer>
            <Tab 
              active={activeTab === 'settings'} 
              onClick={() => setActiveTab('settings')}
            >
              Settings
            </Tab>
            <Tab 
              active={activeTab === 'audit'} 
              onClick={() => setActiveTab('audit')}
            >
              Audit Log
            </Tab>
          </TabContainer>
          
          {activeTab === 'settings' && (
            <SettingsPanel 
              settings={settings}
              onSettingsChange={handleSettingsChange}
              onPresetChange={handlePresetChange}
            />
          )}
          
          {activeTab === 'audit' && (
            <AuditLogViewer />
          )}
        </RightPanel>
      </MainContent>
      
      <MobileOverlay 
        show={rightPanelOpen} 
        onClick={() => setRightPanelOpen(false)}
      />
      
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </AppContainer>
  );
}

export default App;