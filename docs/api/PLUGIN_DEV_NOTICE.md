# 📢 Notice to Plugin Developers: API Enhancement for Conversation Tracking

**Date**: July 12, 2025  
**API Version**: 0.1.0a5 (no breaking changes)  
**Enhancement**: Conversation participant tracking

## Why We Built This

Previously, when your plugin submitted content for checking, the audit logs would show:
```
User checked prompt: "How do I hack the system?"
Decision: Blocked
```

This raised an important question: **Which user? Talking to which AI?**

For security forensics and compliance, we need to know exactly WHO was involved. Now the audit logs show:
```
bob@example.com <-> ChatGPT checked prompt: "How do I hack the system?"
Decision: Blocked
```

This enhancement ensures complete accountability and traceability for every security decision.

## How to Use It

Simply add user and bot identification to your existing API calls:

### Before (still works, but limited)
```javascript
fetch('http://localhost:8888/v1/check', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    text: userInput,
    kind: 'prompt'
  })
})
```

### After (enhanced tracking)
```javascript
fetch('http://localhost:8888/v1/check', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    text: userInput,
    kind: 'prompt',
    context: {
      // Required for tracking
      userId: 'bob@example.com',     // User's email or unique ID
      botId: 'chatgpt',              // AI system identifier
      
      // Optional but recommended
      userName: 'Bob Smith',         // Human-readable name
      botName: 'ChatGPT',           // AI display name
      botModel: 'gpt-4',            // Specific model version
      sessionId: 'ext-12345',       // Your session tracking
      
      // Any additional context
      browser: 'Chrome',
      extensionVersion: '1.0.0'
    }
  })
})
```

## What Gets Logged

The Stinger audit trail now captures:
- **Who**: bob@example.com (Bob Smith)
- **Talking to**: ChatGPT (gpt-4)
- **When**: Timestamp
- **What**: The actual content checked
- **Decision**: Allow/Warn/Block with reasons
- **Context**: Browser, extension version, etc.

## Real Browser Extension Example

```javascript
// Detect current user and AI system
const currentUser = await chrome.storage.local.get('userEmail');
const aiSystem = detectAISystem(); // Your logic to detect ChatGPT/Claude/etc

// Submit for checking with full context
const result = await stingerAPI.check({
  text: interceptedPrompt,
  kind: 'prompt',
  context: {
    userId: currentUser.email || 'anonymous',
    userName: currentUser.name,
    botId: aiSystem.id,
    botName: aiSystem.name,
    botModel: aiSystem.model,
    sessionId: `${chrome.runtime.id}-${Date.now()}`,
    
    // Extension metadata
    browser: navigator.userAgentData?.brands[0]?.brand || 'Unknown',
    extensionVersion: chrome.runtime.getManifest().version,
    url: window.location.hostname
  }
});
```

## Benefits for Your Plugin

1. **Accountability**: Know exactly which user triggered which guardrail
2. **Debugging**: Quickly identify problematic user/AI combinations
3. **Analytics**: Track usage patterns per user and AI system
4. **Compliance**: Meet audit requirements for user attribution
5. **Support**: Help users by seeing their exact conversation context

## Where to Find This

- **Endpoint**: POST `/v1/check` (same endpoint, enhanced context)
- **Documentation**: `/docs/api/CONVERSATION_TRACKING.md`
- **API Docs**: `http://localhost:8888/docs` (interactive Swagger UI)
- **No Breaking Changes**: Old requests still work, just add context when ready

## Migration Checklist

- [ ] Identify how to get current user (email, ID, etc.)
- [ ] Detect which AI system is being used
- [ ] Add context object to your API calls
- [ ] Test that audit logs show correct participants
- [ ] Consider adding session tracking for related checks

## Questions?

This is a backward-compatible enhancement - your existing code will continue to work. When you're ready to add tracking, simply include the context object.

For questions or issues, please file on GitHub: https://github.com/virtualsteve-star/stinger/issues

---

**Remember**: The goal is to answer "Who said what to which AI?" - help us make the audit trail as useful as possible for security and debugging!