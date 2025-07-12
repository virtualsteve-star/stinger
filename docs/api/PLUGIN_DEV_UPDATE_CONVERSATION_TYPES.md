# 📢 Plugin Developer Update: Conversation Type Support

**Date**: July 12, 2025  
**Enhancement**: Specify conversation participant types  
**No Breaking Changes**: Defaults ensure backward compatibility

## Why We Added This

We realized that "bob@example.com <-> chatgpt" doesn't tell the whole story. Consider these scenarios:

1. **Customer Service Bot**: A bot responding to a human customer
2. **Agent Collaboration**: Two AI agents working together  
3. **AI Orchestration**: An agent managing multiple AI models
4. **Human-to-Human**: Support staff chatting (with AI monitoring)

The audit trail now captures WHAT TYPE of participants are involved:
```
Before: bob@example.com <-> support-system
After:  bob@example.com (human) <-> support-system (bot)
```

This helps you understand:
- Is this human-to-AI or agent-to-agent?
- Should different guardrails apply to bot responses vs human responses?
- Are two AI systems talking to each other (potential feedback loops)?

## How to Implement

Add `userType` and `botType` to your context:

```javascript
// Browser extension detecting conversation type
const context = {
  userId: getCurrentUser(),
  botId: getAISystem(),
  
  // NEW: Specify participant types
  userType: 'human',      // Options: human, bot, agent, ai_model
  botType: 'ai_model',    // Options: human, bot, agent, ai_model
  
  // Rest of your context...
  sessionId: sessionId
};
```

## Real-World Examples

### 1. Standard Human Using ChatGPT (Default)
```javascript
{
  userId: "alice@company.com",
  botId: "chatgpt",
  // userType defaults to 'human'
  // botType defaults to 'ai_model'
}
// Audit: alice@company.com (human) <-> chatgpt (ai_model)
```

### 2. Customer Service Bot
```javascript
{
  userId: "helpdesk-bot-1",
  userType: "bot",
  botId: "customer-12345",
  botType: "human",
  
  // The bot is sending a response to the human
  kind: "response"
}
// Audit: helpdesk-bot-1 (bot) <-> customer-12345 (human)
```

### 3. AI Agents Collaborating
```javascript
{
  userId: "research-agent",
  userType: "agent",
  botId: "writing-agent",
  botType: "agent",
  
  metadata: {
    task: "Generate research report",
    orchestrator: "AutoGPT"
  }
}
// Audit: research-agent (agent) <-> writing-agent (agent)
```

### 4. Agent Managing Multiple AIs
```javascript
{
  userId: "orchestrator-agent",
  userType: "agent",
  botId: "gpt-4",
  botType: "ai_model",
  
  metadata: {
    workflow: "multi-model-consensus",
    step: 3
  }
}
// Audit: orchestrator-agent (agent) <-> gpt-4 (ai_model)
```

## Browser Extension Implementation

```javascript
class ConversationDetector {
  detectParticipantTypes() {
    // Detect if user is human or automated
    const userType = this.isAutomatedUser() ? 'bot' : 'human';
    
    // Detect AI system type
    const aiInfo = this.detectAISystem();
    const botType = aiInfo.isAgent ? 'agent' : 'ai_model';
    
    return { userType, botType };
  }
  
  isAutomatedUser() {
    // Your logic to detect bots/agents
    return window.location.search.includes('automated=true') ||
           document.querySelector('[data-testid="automation-banner"]');
  }
  
  detectAISystem() {
    const hostname = window.location.hostname;
    
    // Standard AI models
    if (hostname.includes('chat.openai.com')) {
      return { id: 'chatgpt', type: 'ai_model', isAgent: false };
    }
    
    // AI agents
    if (hostname.includes('autogpt.') || hostname.includes('agent.')) {
      return { id: 'autogpt', type: 'agent', isAgent: true };
    }
    
    // Customer service bots
    if (hostname.includes('support.') || hostname.includes('help.')) {
      return { id: 'support-bot', type: 'bot', isAgent: false };
    }
    
    return { id: 'unknown', type: 'ai_model', isAgent: false };
  }
}
```

## Benefits for Your Plugin

1. **Smarter Filtering**: Apply different rules for human-to-AI vs agent-to-agent
2. **Loop Detection**: Identify when AI systems are talking to each other
3. **Compliance**: Some regulations treat bot-to-human differently
4. **Analytics**: Understand usage patterns by conversation type
5. **Debugging**: Quickly spot unusual conversation patterns

## Quick Test

```bash
# Test human to AI (default)
curl -X POST http://localhost:8888/v1/check \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello AI",
    "context": {
      "userId": "test-user",
      "botId": "test-ai"
    }
  }'

# Test agent to agent
curl -X POST http://localhost:8888/v1/check \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Process dataset XYZ",
    "context": {
      "userId": "agent-1",
      "userType": "agent",
      "botId": "agent-2",
      "botType": "agent"
    }
  }'
```

## Migration Checklist

- [ ] No changes required - defaults maintain current behavior
- [ ] Consider detecting automated users (bots/agents)
- [ ] Add logic to identify AI agents vs models
- [ ] Test audit logs show correct participant types
- [ ] Update analytics to track conversation types

## Summary

This enhancement helps answer: **"What KIND of conversation is this?"**
- Human asking ChatGPT? (human <-> ai_model)
- Bot responding to customer? (bot <-> human)  
- Agents collaborating? (agent <-> agent)
- Agent orchestrating AI? (agent <-> ai_model)

Your existing code continues to work. When ready, add `userType` and `botType` for richer audit trails and better security decisions.