# Simple Conversation Tracking in API

The existing `/v1/check` endpoint now supports identifying conversation participants through the context field.

## Usage

```json
POST /v1/check
{
  "text": "How do I reset my password?",
  "kind": "prompt",
  "context": {
    "userId": "bob@example.com",
    "botId": "chatgpt",
    "sessionId": "browser-ext-12345",
    "userName": "Bob Smith",
    "botName": "ChatGPT",
    "botModel": "gpt-4",
    
    // Conversation types (optional, defaults shown)
    "userType": "human",    // Options: human, bot, agent, ai_model
    "botType": "ai_model"   // Options: human, bot, agent, ai_model
  }
}
```

## Conversation Types

The API supports different types of conversations:

- **human <-> ai_model** (default): User chatting with AI
- **agent <-> agent**: Two AI agents talking
- **bot <-> human**: Automated bot talking to human
- **agent <-> ai_model**: Agent orchestrating AI

Examples:

```json
// Customer service bot talking to human
{
  "userId": "support-bot-1",
  "userType": "bot",
  "botId": "customer@email.com", 
  "botType": "human"
}

// Two AI agents collaborating
{
  "userId": "research-agent",
  "userType": "agent",
  "botId": "writing-agent",
  "botType": "agent"
}
```

## What Gets Logged

The audit trail will now show conversation types:
```
Default (human <-> ai_model):
Participants: bob@example.com (human) <-> chatgpt (ai_model)
Event: Checking prompt "How do I reset my password?"
Decision: Allowed

Agent collaboration:
Participants: research-agent (agent) <-> writing-agent (agent)
Event: Checking prompt "Analyze this data..."
Decision: Allowed

Bot to human:
Participants: support-bot-1 (bot) <-> customer@email.com (human)
Event: Checking response "Your ticket has been created..."
Decision: Allowed
```

## Minimal Example

At minimum, provide userId and botId:
```json
{
  "text": "test prompt",
  "context": {
    "userId": "user123",
    "botId": "claude"
  }
}
```

## Browser Extension Example

```javascript
const result = await fetch('http://localhost:8888/v1/check', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    text: userInput,
    kind: 'prompt',
    context: {
      userId: getCurrentUser(),  // e.g., "bob@example.com"
      botId: getAISystem(),      // e.g., "chatgpt"
      sessionId: getSessionId(),
      // Any other context
      browser: 'Chrome',
      extensionVersion: '1.0.0'
    }
  })
});
```

This simple enhancement ensures the audit logs clearly show WHO is involved in each conversation without adding API versioning complexity.