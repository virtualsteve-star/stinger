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
    "botModel": "gpt-4"
  }
}
```

## What Gets Logged

The audit trail will now show:
```
User: bob@example.com <-> chatgpt
Event: Checking prompt "How do I reset my password?"
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