# Phase 5f Conversation Abstraction Plan (Corrected)

**Status: ✅ COMPLETED**  
**Start Date**: 2025-06-26  
**Completion Date**: 2025-06-26  

## Overview
Add a Conversation abstraction to support multi-turn context, rate limiting, improved logging, and future multi-turn guardrails without breaking existing single-turn functionality.

## Turn Definition
A **turn** is defined as a complete prompt-response exchange in a conversation:
- **Prompt**: The initiator's input/message
- **Response**: The responder's response
- **Timestamp**: When the exchange occurred
- **Speaker/Listener**: Who said what to whom
- **Metadata**: Optional additional data about the exchange

This natural definition encapsulates the conversation concept and provides a cleaner unit for analysis.

## Participant Tracking

The conversation system needs to track both sides of the conversation, which can be:
- **Human ↔ AI Model**: Traditional user-AI conversations
- **Bot ↔ Bot**: Agent-to-agent conversations
- **Human ↔ Human**: Human conversations with moderation
- **Agent ↔ Agent**: Multi-agent system conversations

### Participant Structure
```python
participants = {
    "initiator": "user_456",           # Who started the conversation
    "responder": "gpt-4",              # Who's responding
    "initiator_type": "human",         # human, bot, agent, ai_model
    "responder_type": "ai_model"       # human, bot, agent, ai_model
}

model_info = {
    "model_id": "gpt-4",
    "model_version": "gpt-4-1106-preview", 
    "provider": "openai"
}
```

## The Problem with Current Approach

The current implementation treats turns as individual messages:
```python
# Current (confusing) approach
conversation.add_turn("Hello", "prompt")
conversation.add_turn("Hi there", "response")
conversation.add_turn("How can I help?", "prompt")
```

This doesn't match our agreed definition of a turn as a prompt-response pair.

## Proposed Solution: Clean API Design

### 1. Enhanced Conversation Class

```python
@dataclass
class Turn:
    """Represents a complete prompt-response exchange in a conversation."""
    timestamp: datetime
    prompt: str
    response: Optional[str] = None  # None if response hasn't been generated yet
    speaker: str                    # Who said the prompt
    listener: str                   # Who received the prompt
    speaker_type: str = "human"     # human, bot, agent, ai_model
    listener_type: str = "ai_model" # human, bot, agent, ai_model
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if isinstance(self.timestamp, (int, float)):
            self.timestamp = datetime.fromtimestamp(self.timestamp)

class Conversation:
    """
    Manages a multi-turn conversation with rate limiting and logging context.
    
    This class provides:
    - Unique conversation ID for tracking
    - Participant tracking (initiator/responder with types)
    - Model information for AI conversations
    - Ordered conversation history (complete exchanges)
    - Per-conversation rate limiting
    - Metadata storage
    - Logging context for traceability
    
    Example:
        ```python
        # Human talking to AI
        conv = Conversation(
            participants={
                "initiator": "user_123",
                "responder": "gpt-4",
                "initiator_type": "human",
                "responder_type": "ai_model"
            },
            model_info={
                "model_id": "gpt-4",
                "model_version": "gpt-4-1106-preview",
                "provider": "openai"
            }
        )
        
        # Bot talking to bot
        conv = Conversation(
            participants={
                "initiator": "customer_service_bot",
                "responder": "billing_bot", 
                "initiator_type": "bot",
                "responder_type": "bot"
            }
        )
        
        # Add complete exchanges (turns)
        conv.add_turn("Hello, how can I help?", "I'm here to assist you!")
        conv.add_turn("I need help with my account", "What specific issue?")
        
        # Or add just a prompt (response will be added later)
        conv.add_prompt("What's your account number?")
        # Later...
        conv.add_response("My account is 123-45-6789")
        
        # Check rate limits
        if conv.check_rate_limit():
            print("Rate limit exceeded")
        
        # Get conversation history
        history = conv.get_history()
        ```
    """
    
    def __init__(
        self, 
        conversation_id: Optional[str] = None,
        participants: Optional[Dict[str, str]] = None,
        model_info: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        rate_limit: Optional[Dict[str, int]] = None
    ):
        """Initialize a conversation."""
        self.conversation_id = conversation_id or str(uuid.uuid4())
        self.participants = participants or {}
        self.model_info = model_info or {}
        self.metadata = metadata or {}
        self.turns: List[Turn] = []
        self.created_at = datetime.now()
        self.last_activity = self.created_at
        
        # Rate limiting configuration
        self.rate_limit = rate_limit or {}
        self.rate_limit_turns: List[datetime] = []
        
        # Extract participant info for convenience
        self.initiator = self.participants.get('initiator', 'unknown')
        self.responder = self.participants.get('responder', 'unknown')
        self.initiator_type = self.participants.get('initiator_type', 'unknown')
        self.responder_type = self.participants.get('responder_type', 'unknown')
        
        logger.info(f"Created conversation {self.conversation_id} between {self.initiator} ({self.initiator_type}) and {self.responder} ({self.responder_type})")
    
    def add_turn(self, prompt: str, response: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Turn:
        """
        Add a complete turn (prompt-response exchange) to the conversation.
        
        Args:
            prompt: The initiator's prompt/message
            response: The responder's response (optional, can be added later)
            metadata: Optional metadata for this turn
            
        Returns:
            The created Turn object
        """
        turn = Turn(
            timestamp=datetime.now(),
            prompt=prompt,
            response=response,
            speaker=self.initiator,
            listener=self.responder,
            speaker_type=self.initiator_type,
            listener_type=self.responder_type,
            metadata=metadata or {}
        )
        
        self.turns.append(turn)
        self.last_activity = turn.timestamp
        self.rate_limit_turns.append(turn.timestamp)
        
        # Clean up old rate limit entries
        self._cleanup_rate_limit_entries()
        
        logger.debug(f"Added turn to conversation {self.conversation_id}: {self.initiator} -> {self.responder}")
        return turn
    
    def add_prompt(self, prompt: str, metadata: Optional[Dict[str, Any]] = None) -> Turn:
        """
        Add just a prompt (for when response isn't ready yet).
        
        Args:
            prompt: The initiator's prompt/message
            metadata: Optional metadata for this turn
            
        Returns:
            The created Turn object
        """
        return self.add_turn(prompt, response=None, metadata=metadata)
    
    def add_response(self, response: str, metadata: Optional[Dict[str, Any]] = None) -> Turn:
        """
        Add a response to the most recent prompt-only turn.
        
        Args:
            response: The responder's response
            metadata: Optional metadata to merge with existing turn metadata
            
        Returns:
            The updated Turn object
            
        Raises:
            ValueError: If no prompt-only turn exists
        """
        if not self.turns or self.turns[-1].response is not None:
            raise ValueError("No prompt-only turn exists to add response to")
        
        turn = self.turns[-1]
        turn.response = response
        if metadata:
            turn.metadata.update(metadata)
        
        logger.debug(f"Added response to conversation {self.conversation_id}: {self.responder} -> {self.initiator}")
        return turn
    
    def get_history(self, limit: Optional[int] = None) -> List[Turn]:
        """
        Get conversation history (complete exchanges).
        
        Args:
            limit: Optional limit on number of turns to return
            
        Returns:
            List of turns in chronological order
        """
        if limit is None:
            return self.turns.copy()
        return self.turns[-limit:]
    
    def get_complete_turns(self) -> List[Turn]:
        """Get all complete turns (with both prompt and response)."""
        return [turn for turn in self.turns if turn.response is not None]
    
    def get_incomplete_turns(self) -> List[Turn]:
        """Get all incomplete turns (prompt only, no response yet)."""
        return [turn for turn in self.turns if turn.response is None]
    
    def get_turn_count(self) -> int:
        """Get total number of turns."""
        return len(self.turns)
    
    def get_complete_turn_count(self) -> int:
        """Get number of complete turns."""
        return len(self.get_complete_turns())
    
    def get_duration(self) -> float:
        """Get conversation duration in seconds."""
        if not self.turns:
            return 0.0
        return (self.last_activity - self.created_at).total_seconds()
    
    # ... rest of the methods remain the same ...
```

### 2. Enhanced Pipeline with Automatic Guardrail Annotation

The pipeline should handle the conversation bookkeeping automatically AND annotate guardrail results:

```python
class GuardrailPipeline:
    """Enhanced pipeline with automatic conversation management and guardrail annotation."""
    
    def check_input(self, content: str, conversation: Optional[Conversation] = None) -> PipelineResult:
        """
        Check input content through all input guardrails.
        
        Args:
            content: The input content to check
            conversation: Optional conversation context for multi-turn scenarios
            
        Returns:
            Dict with 'blocked', 'warnings', 'reasons', 'details', and 'conversation_id' keys
        """
        if content is None:
            raise ValueError("Content cannot be None")
        
        # Check conversation rate limits if provided
        if conversation and conversation.check_rate_limit():
            return {
                'blocked': True,
                'warnings': [],
                'reasons': [f"Rate limit exceeded for conversation {conversation.conversation_id}"],
                'details': {'rate_limit': 'exceeded'},
                'pipeline_type': 'input',
                'conversation_id': conversation.conversation_id
            }
        
        # Add prompt to conversation if provided
        if conversation:
            conversation.add_prompt(content)
        
        # Run pipeline and get results
        result = self._run_pipeline(self.input_pipeline, content, "input", conversation)
        
        # Annotate guardrail results into conversation if provided
        if conversation and conversation.turns:
            self._annotate_guardrail_results(conversation.turns[-1], result)
        
        return result
    
    def check_output(self, content: str, conversation: Optional[Conversation] = None) -> PipelineResult:
        """
        Check output content through all output guardrails.
        
        Args:
            content: The output content to check
            conversation: Optional conversation context for multi-turn scenarios
            
        Returns:
            Dict with 'blocked', 'warnings', 'reasons', 'details', and 'conversation_id' keys
        """
        if content is None:
            raise ValueError("Content cannot be None")
        
        # Check conversation rate limits if provided
        if conversation and conversation.check_rate_limit():
            return {
                'blocked': True,
                'warnings': [],
                'reasons': [f"Rate limit exceeded for conversation {conversation.conversation_id}"],
                'details': {'rate_limit': 'exceeded'},
                'pipeline_type': 'output',
                'conversation_id': conversation.conversation_id
            }
        
        # Add response to conversation if provided
        if conversation:
            try:
                conversation.add_response(content)
            except ValueError:
                # If no prompt exists, create a new turn with the response
                conversation.add_turn("", content)
        
        # Run pipeline and get results
        result = self._run_pipeline(self.output_pipeline, content, "output", conversation)
        
        # Annotate guardrail results into conversation if provided
        if conversation and conversation.turns:
            self._annotate_guardrail_results(conversation.turns[-1], result)
        
        return result
    
    def _annotate_guardrail_results(self, turn: Turn, result: PipelineResult) -> None:
        """
        Annotate guardrail results into turn metadata.
        
        Args:
            turn: The turn to annotate
            result: The pipeline result to annotate
        """
        # Store guardrail results in turn metadata
        turn.metadata.update({
            'guardrail_results': {
                'blocked': result['blocked'],
                'warnings': result['warnings'],
                'reasons': result['reasons'],
                'details': result['details'],
                'pipeline_type': result['pipeline_type'],
                'timestamp': datetime.now().isoformat()
            }
        })
        
        # Log annotation
        logger.debug(f"Annotated guardrail results to turn in conversation {result['conversation_id']}: blocked={result['blocked']}")
```

### 3. Enhanced Usage with Participant Tracking

#### Pattern 1: Human-AI Conversation

```python
# Human talking to AI model
pipeline = GuardrailPipeline.from_preset("customer_service")
conversation = Conversation(
    participants={
        "initiator": "user_123",
        "responder": "gpt-4",
        "initiator_type": "human",
        "responder_type": "ai_model"
    },
    model_info={
        "model_id": "gpt-4",
        "model_version": "gpt-4-1106-preview",
        "provider": "openai"
    }
)

# Check input (automatically adds prompt AND annotates results)
result = pipeline.check_input("My SSN is 123-45-6789", conversation=conversation)
if result['blocked']:
    print("Input blocked")
else:
    # Generate AI response
    ai_response = "I understand you're having issues"
    result = pipeline.check_output(ai_response, conversation=conversation)
    if result['blocked']:
        print("Output blocked")
    else:
        print("Both input and output approved")

# Conversation now has 1 complete turn with guardrail annotations
turn = conversation.get_history()[-1]
print(f"Turn: {turn.speaker} -> {turn.listener}")
print(f"Prompt: {turn.prompt}")
print(f"Response: {turn.response}")
print(f"Guardrail results: {turn.metadata.get('guardrail_results', {})}")
```

#### Pattern 2: Bot-to-Bot Conversation

```python
# Bot talking to bot
conversation = Conversation(
    participants={
        "initiator": "customer_service_bot",
        "responder": "billing_bot",
        "initiator_type": "bot",
        "responder_type": "bot"
    }
)

# Process bot conversation
pipeline.check_input("Customer needs billing info", conversation=conversation)
pipeline.check_output("Here's the billing information", conversation=conversation)

# Analyze conversation
for turn in conversation.get_history():
    print(f"{turn.speaker} ({turn.speaker_type}) -> {turn.listener} ({turn.listener_type})")
    print(f"  Prompt: {turn.prompt}")
    print(f"  Response: {turn.response}")
```

#### Pattern 3: Human-Human Conversation with Moderation

```python
# Human talking to human (with moderation)
conversation = Conversation(
    participants={
        "initiator": "user_123",
        "responder": "user_456",
        "initiator_type": "human",
        "responder_type": "human"
    }
)

# Moderate human conversation
pipeline.check_input("Hello, how are you?", conversation=conversation)
pipeline.check_output("I'm good, thanks!", conversation=conversation)

pipeline.check_input("I'm very angry at you!", conversation=conversation)  # Should trigger toxicity
pipeline.check_output("I understand you're upset", conversation=conversation)
```

#### Pattern 4: Agent-to-Agent Conversation

```python
# Agent talking to agent
conversation = Conversation(
    participants={
        "initiator": "orchestrator_agent",
        "responder": "specialist_agent",
        "initiator_type": "agent",
        "responder_type": "agent"
    }
)

# Process agent conversation
pipeline.check_input("Need help with customer query", conversation=conversation)
pipeline.check_output("I can help with that", conversation=conversation)
```

### 4. Forensic Analysis with Participant Context

```python
# Analyze conversation with participant context
def analyze_conversation_forensics(conversation: Conversation) -> Dict[str, Any]:
    """Analyze conversation for forensic purposes with participant context."""
    
    analysis = {
        'conversation_id': conversation.conversation_id,
        'participants': conversation.participants,
        'model_info': conversation.model_info,
        'created_at': conversation.created_at,
        'duration': conversation.get_duration(),
        'total_turns': conversation.get_turn_count(),
        'blocked_turns': [],
        'warned_turns': [],
        'guardrail_summary': {},
        'timeline': []
    }
    
    # Analyze each turn
    for i, turn in enumerate(conversation.get_history(), 1):
        guardrail_results = turn.metadata.get('guardrail_results', {})
        
        # Build timeline with participant context
        analysis['timeline'].append({
            'turn_number': i,
            'timestamp': turn.timestamp,
            'speaker': turn.speaker,
            'listener': turn.listener,
            'speaker_type': turn.speaker_type,
            'listener_type': turn.listener_type,
            'prompt': turn.prompt,
            'response': turn.response,
            'blocked': guardrail_results.get('blocked', False),
            'warnings': guardrail_results.get('warnings', []),
            'reasons': guardrail_results.get('reasons', []),
            'pipeline_type': guardrail_results.get('pipeline_type')
        })
        
        # Track blocked/warned turns
        if guardrail_results.get('blocked'):
            analysis['blocked_turns'].append(i)
        if guardrail_results.get('warnings'):
            analysis['warned_turns'].append(i)
        
        # Build guardrail summary
        for guardrail_name, details in guardrail_results.get('details', {}).items():
            if guardrail_name not in analysis['guardrail_summary']:
                analysis['guardrail_summary'][guardrail_name] = {
                    'total_firings': 0,
                    'blocks': 0,
                    'warnings': 0
                }
            
            analysis['guardrail_summary'][guardrail_name]['total_firings'] += 1
            if details.get('blocked'):
                analysis['guardrail_summary'][guardrail_name]['blocks'] += 1
            elif details.get('confidence', 0) > 0.5:
                analysis['guardrail_summary'][guardrail_name]['warnings'] += 1
    
    return analysis
```

### 5. Benefits of Enhanced Participant Tracking

1. **Flexible**: Works for any combination of participants
2. **Clear Roles**: Always know who's speaking to whom
3. **Model Tracking**: Know exactly which AI model was used
4. **Agent Support**: Works for bot-to-bot conversations
5. **Audit Trail**: Complete record of who said what to whom
6. **Forensics**: Can trace conversations across different systems
7. **Compliance**: Full participant context for regulatory requirements

### 6. Metadata Structure

The enhanced conversation structure includes:

```python
{
    'conversation_id': str,
    'participants': {
        'initiator': str,
        'responder': str,
        'initiator_type': str,  # human, bot, agent, ai_model
        'responder_type': str   # human, bot, agent, ai_model
    },
    'model_info': {
        'model_id': str,
        'model_version': str,
        'provider': str
    },
    'turns': [
        {
            'timestamp': str,
            'prompt': str,
            'response': str,
            'speaker': str,
            'listener': str,
            'speaker_type': str,
            'listener_type': str,
            'metadata': {
                'guardrail_results': {
                    'blocked': bool,
                    'warnings': List[str],
                    'reasons': List[str],
                    'details': Dict[str, Any],
                    'pipeline_type': str,
                    'timestamp': str
                }
            }
        }
    ]
}
```

### 7. Backward Compatibility

The enhanced participant tracking is backward compatible:

```python
# Old way (still works, uses defaults)
conversation = Conversation("user_123")
# Defaults to: initiator="user_123", responder="unknown", types="unknown"

# New way (with full participant context)
conversation = Conversation(
    participants={
        "initiator": "user_123",
        "responder": "gpt-4",
        "initiator_type": "human",
        "responder_type": "ai_model"
    },
    model_info={
        "model_id": "gpt-4",
        "model_version": "gpt-4-1106-preview",
        "provider": "openai"
    }
)
```

This enhancement provides comprehensive participant tracking while maintaining backward compatibility and enabling rich forensic analysis. 