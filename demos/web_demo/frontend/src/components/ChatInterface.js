import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { FiSend, FiUser, FiCpu, FiShield, FiAlertTriangle } from 'react-icons/fi';

const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  flex: 1;
  background: white;
  margin: 16px;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  overflow: hidden;
`;

const MessagesArea = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  
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
  
  &::-webkit-scrollbar-thumb:hover {
    background: #94a3b8;
  }
`;

const MessageBubble = styled.div`
  max-width: 80%;
  padding: 16px 20px;
  border-radius: 18px;
  font-size: 14px;
  line-height: 1.5;
  align-self: ${props => props.sender === 'user' ? 'flex-end' : 'flex-start'};
  background: ${props => {
    if (props.blocked) return '#fee2e2';
    return props.sender === 'user' ? '#3b82f6' : '#f8fafc';
  }};
  color: ${props => {
    if (props.blocked) return '#991b1b';
    return props.sender === 'user' ? 'white' : '#1a202c';
  }};
  border: ${props => props.sender === 'user' ? 'none' : '1px solid #e2e8f0'};
  position: relative;
  
  ${props => props.blocked && `
    border: 2px solid #fca5a5;
  `}
`;

const MessageHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 12px;
  font-weight: 500;
  opacity: 0.8;
`;

const MessageIcon = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
`;

const BlockedMessage = styled.div`
  background: #fee2e2;
  border: 2px solid #fca5a5;
  border-radius: 12px;
  padding: 16px;
  margin: 16px 0;
  color: #991b1b;
`;

const BlockedHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  margin-bottom: 8px;
`;

const ReasonsList = styled.ul`
  margin: 8px 0 0 20px;
  padding: 0;
  
  li {
    margin: 4px 0;
    font-size: 13px;
  }
`;

const WarningsList = styled.div`
  background: #fef3c7;
  border: 1px solid #f59e0b;
  border-radius: 8px;
  padding: 12px;
  margin: 8px 0;
  color: #92400e;
  font-size: 13px;
`;

const InputArea = styled.div`
  padding: 20px;
  border-top: 1px solid #e2e8f0;
  background: #f8fafc;
`;

const InputContainer = styled.div`
  display: flex;
  gap: 12px;
  align-items: flex-end;
`;

const MessageInput = styled.textarea`
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 14px;
  font-family: inherit;
  resize: none;
  min-height: 44px;
  max-height: 120px;
  outline: none;
  transition: border-color 0.2s ease;
  
  &:focus {
    border-color: #3b82f6;
  }
  
  &:disabled {
    background: #f1f5f9;
    color: #64748b;
    cursor: not-allowed;
  }
  
  &::placeholder {
    color: #94a3b8;
  }
`;

const SendButton = styled.button`
  padding: 12px;
  background: ${props => props.disabled ? '#e2e8f0' : '#3b82f6'};
  color: ${props => props.disabled ? '#94a3b8' : 'white'};
  border: none;
  border-radius: 12px;
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 44px;
  height: 44px;
  transition: all 0.2s ease;
  
  &:hover:not(:disabled) {
    background: #2563eb;
    transform: translateY(-1px);
  }
  
  &:active:not(:disabled) {
    transform: translateY(0);
  }
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  color: #64748b;
  text-align: center;
  gap: 16px;
`;

const LoadingIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  color: #64748b;
  font-size: 14px;
  margin: 16px 0;
`;

const Spinner = styled.div`
  width: 16px;
  height: 16px;
  border: 2px solid #e2e8f0;
  border-top: 2px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

function ChatInterface({ onSendMessage, conversation }) {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      sender: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await onSendMessage(inputValue);
      
      // Add assistant response
      const assistantMessage = {
        id: Date.now() + 1,
        sender: 'assistant',
        content: response.content,
        timestamp: new Date(),
        blocked: response.blocked,
        warnings: response.warnings,
        reasons: response.reasons,
        processingDetails: response.processing_details,
      };

      setMessages(prev => [...prev, assistantMessage]);

    } catch (error) {
      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        sender: 'system',
        content: `Error: ${error.message}`,
        timestamp: new Date(),
        isError: true,
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const renderMessage = (message) => {
    if (message.sender === 'system') {
      return (
        <BlockedMessage key={message.id}>
          <BlockedHeader>
            <FiAlertTriangle />
            System Message
          </BlockedHeader>
          {message.content}
        </BlockedMessage>
      );
    }

    return (
      <div key={message.id}>
        <MessageBubble 
          sender={message.sender} 
          blocked={message.blocked}
        >
          <MessageHeader>
            <MessageIcon>
              {message.sender === 'user' ? <FiUser /> : <FiCpu />}
            </MessageIcon>
            {message.sender === 'user' ? 'You' : 'Assistant'}
          </MessageHeader>
          {message.content}
        </MessageBubble>
        
        {message.blocked && (
          <BlockedMessage>
            <BlockedHeader>
              <FiShield />
              Message Blocked by Guardrails
            </BlockedHeader>
            {message.reasons && message.reasons.length > 0 && (
              <div>
                <strong>Reasons:</strong>
                <ReasonsList>
                  {message.reasons.map((reason, index) => (
                    <li key={index}>{reason}</li>
                  ))}
                </ReasonsList>
              </div>
            )}
          </BlockedMessage>
        )}
        
        {message.warnings && message.warnings.length > 0 && (
          <WarningsList>
            <strong>⚠️ Warnings:</strong>
            <ul style={{ margin: '4px 0 0 16px', padding: 0 }}>
              {message.warnings.map((warning, index) => (
                <li key={index}>{warning}</li>
              ))}
            </ul>
          </WarningsList>
        )}
      </div>
    );
  };

  return (
    <ChatContainer>
      <MessagesArea>
        {messages.length === 0 ? (
          <EmptyState>
            <FiCpu size={48} style={{ opacity: 0.3 }} />
            <div>
              <h3 style={{ margin: '0 0 8px 0', color: '#1a202c' }}>
                Welcome to Stinger Guardrails Demo
              </h3>
              <p style={{ margin: 0, fontSize: '14px' }}>
                Send a message to see how Stinger's safety guardrails work in real-time.
                <br />
                Try sending messages with PII, toxic content, or other sensitive information.
              </p>
            </div>
          </EmptyState>
        ) : (
          messages.map(renderMessage)
        )}
        
        {isLoading && (
          <LoadingIndicator>
            <Spinner />
            Processing through guardrails...
          </LoadingIndicator>
        )}
        
        <div ref={messagesEndRef} />
      </MessagesArea>

      <InputArea>
        <InputContainer>
          <MessageInput
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message here... (Try: 'My SSN is 123-45-6789' or 'I hate everyone')"
            disabled={isLoading}
            rows={1}
            style={{
              height: Math.min(120, Math.max(44, inputValue.split('\n').length * 20 + 24))
            }}
          />
          <SendButton 
            onClick={handleSend}
            disabled={!inputValue.trim() || isLoading}
          >
            <FiSend />
          </SendButton>
        </InputContainer>
      </InputArea>
    </ChatContainer>
  );
}

export default ChatInterface;