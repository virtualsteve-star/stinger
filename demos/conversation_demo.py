#!/usr/bin/env python3
"""
Conversation Demo - Phase 5f

This demo showcases the Conversation abstraction features:
- Multi-turn conversation management
- Per-conversation rate limiting
- Conversation-aware logging and traceability
- Integration with GuardrailPipeline

Run with: python3 demos/conversation_demo.py
"""

import sys
import time
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from stinger import GuardrailPipeline, Conversation


def setup_logging():
    """Set up logging to demonstrate conversation context in logs."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('conversation_demo.log')
        ]
    )


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)


def print_result(result: dict, pipeline_type: str):
    """Print guardrail result in a formatted way."""
    conversation_id = result.get('conversation_id', 'N/A')
    print(f"\n📋 {pipeline_type.upper()} Result (Conversation: {conversation_id}):")
    print(f"   Status: {'🚫 BLOCKED' if result['blocked'] else '✅ ALLOWED'}")
    
    if result['reasons']:
        print("   Reasons:")
        for reason in result['reasons']:
            print(f"     • {reason}")
    
    if result['warnings']:
        print("   Warnings:")
        for warning in result['warnings']:
            print(f"     ⚠️  {warning}")


def demo_basic_conversation():
    """Demo basic conversation creation and management with participant tracking."""
    print_header("BASIC CONVERSATION MANAGEMENT")
    
    # Create a human-AI conversation using the new factory method
    conv = Conversation.human_ai(
        user_id="user_123",
        model_id="gpt-4",
        model_info={
            "model_version": "gpt-4-1106-preview",
            "provider": "openai"
        }
    )
    
    print(f"✅ Created conversation: {conv.conversation_id}")
    print(f"   Initiator: {conv.initiator} ({conv.initiator_type})")
    print(f"   Responder: {conv.responder} ({conv.responder_type})")
    print(f"   Model: {conv.model_info.get('model_id', 'N/A')}")
    print(f"   Created: {conv.created_at}")
    
    # Add some complete exchanges using the new add_exchange method
    conv.add_exchange("Hello, how can I help you today?", "I'm here to assist you!")
    conv.add_exchange("I need help with my account", "What specific issue are you experiencing?")
    conv.add_exchange("I can't log in", "I can help you reset your password")
    
    print(f"\n📝 Conversation history ({conv.get_turn_count()} turns):")
    for i, turn in enumerate(conv.get_history(), 1):
        print(f"   {i}. {turn.speaker} -> {turn.listener}: {turn.prompt[:30]}... -> {turn.response[:30]}...")
    
    print(f"\n📊 Conversation stats:")
    print(f"   Duration: {conv.get_duration():.1f} seconds")
    print(f"   Complete turns: {conv.get_complete_turn_count()}")
    print(f"   Incomplete turns: {len(conv.get_incomplete_turns())}")


def demo_different_conversation_types():
    """Demo different types of conversations using factory methods."""
    print_header("DIFFERENT CONVERSATION TYPES")
    
    # Human-AI conversation using factory method
    human_ai = Conversation.human_ai(
        user_id="alice@example.com",
        model_id="gpt-4",
        model_info={
            "model_version": "gpt-4-1106-preview",
            "provider": "openai"
        }
    )
    
    # Bot-to-bot conversation using factory method
    bot_bot = Conversation.bot_to_bot(
        bot1_id="customer_service_bot",
        bot2_id="billing_bot"
    )
    
    # Human-human conversation using factory method
    human_human = Conversation.human_to_human(
        user1_id="user_123",
        user2_id="user_456"
    )
    
    # Agent-to-agent conversation using factory method
    agent_agent = Conversation.agent_to_agent(
        agent1_id="orchestrator_agent",
        agent2_id="specialist_agent"
    )
    
    conversations = [
        ("Human-AI", human_ai),
        ("Bot-Bot", bot_bot),
        ("Human-Human", human_human),
        ("Agent-Agent", agent_agent)
    ]
    
    for name, conv in conversations:
        print(f"\n{name}:")
        print(f"   {conv.initiator} ({conv.initiator_type}) -> {conv.responder} ({conv.responder_type})")
        if conv.model_info:
            print(f"   Model: {conv.model_info.get('model_id', 'N/A')}")


def demo_rate_limiting():
    """Demo conversation rate limiting."""
    print_header("RATE LIMITING")
    
    # Create conversation with rate limits using factory method
    rate_limits = {
        "turns_per_minute": 3,
        "turns_per_hour": 10
    }
    conv = Conversation.human_ai(
        user_id="user_123",
        model_id="gpt-4",
        rate_limit=rate_limits
    )
    print(f"✅ Created conversation with rate limits: {rate_limits}")
    
    # Add turns and check rate limits
    for i in range(5):
        conv.add_exchange(f"Turn {i+1}", f"Response {i+1}")
        exceeded = conv.check_rate_limit()
        print(f"   Turn {i+1}: {'🚫 RATE LIMITED' if exceeded else '✅ OK'}")
        
        if exceeded:
            break
    
    # Reset rate limits and continue
    print("\n🔄 Resetting rate limits...")
    conv.reset_rate_limit()
    conv.add_exchange("After reset", "Response after reset")
    print(f"   After reset: {'🚫 RATE LIMITED' if conv.check_rate_limit() else '✅ OK'}")


def demo_prompt_response_separation():
    """Demo adding prompts and responses separately."""
    print_header("PROMPT-RESPONSE SEPARATION")
    
    conv = Conversation.human_ai("user_123", "gpt-4")
    
    # Add first prompt
    conv.add_prompt("What's the weather like?")
    print(f"✅ Added first prompt")
    print(f"   Incomplete turns: {len(conv.get_incomplete_turns())}")
    print(f"   Complete turns: {conv.get_complete_turn_count()}")
    
    # Add response to the first prompt
    conv.add_response("It's sunny and 75°F today!")
    print(f"✅ Added response to first prompt")
    print(f"   Incomplete turns: {len(conv.get_incomplete_turns())}")
    print(f"   Complete turns: {conv.get_complete_turn_count()}")
    
    # Add second prompt
    conv.add_prompt("How do I reset my password?")
    print(f"✅ Added second prompt")
    print(f"   Incomplete turns: {len(conv.get_incomplete_turns())}")
    print(f"   Complete turns: {conv.get_complete_turn_count()}")
    
    # Add response to the second prompt
    conv.add_response("I can help you reset your password. Go to the settings page...")
    print(f"✅ Added response to second prompt")
    print(f"   Incomplete turns: {len(conv.get_incomplete_turns())}")
    print(f"   Complete turns: {conv.get_complete_turn_count()}")
    
    # Add third prompt
    conv.add_prompt("Can you help me with my account?")
    print(f"✅ Added third prompt")
    print(f"   Incomplete turns: {len(conv.get_incomplete_turns())}")
    print(f"   Complete turns: {conv.get_complete_turn_count()}")
    
    # Add response to the third prompt
    conv.add_response("Of course! I'd be happy to help with your account.")
    print(f"✅ Added response to third prompt")
    print(f"   Incomplete turns: {len(conv.get_incomplete_turns())}")
    print(f"   Complete turns: {conv.get_complete_turn_count()}")
    
    # Show final conversation
    print(f"\n📝 Final conversation:")
    for i, turn in enumerate(conv.get_history(), 1):
        print(f"   {i}. {turn.speaker} -> {turn.listener}: {turn.prompt} -> {turn.response}")


def demo_pipeline_integration():
    """Demo conversation integration with GuardrailPipeline."""
    print_header("PIPELINE INTEGRATION")
    
    # Create pipeline
    try:
        pipeline = GuardrailPipeline.from_preset("customer_service")
        print("✅ Created customer service pipeline")
    except Exception as e:
        print(f"❌ Failed to create pipeline: {e}")
        return
    
    # Create conversation using factory method
    conv = Conversation.human_ai(
        user_id="user_123",
        model_id="gpt-4",
        model_info={
            "model_version": "gpt-4-1106-preview",
            "provider": "openai"
        }
    )
    
    print(f"✅ Created conversation: {conv.conversation_id}")
    
    # Test input with conversation context
    test_inputs = [
        "Hello, I need help",
        "My account number is 123-45-6789",  # Should trigger PII detection
        "I'm very angry and want to hurt someone",  # Should trigger toxicity
    ]
    
    for i, content in enumerate(test_inputs, 1):
        print(f"\n🔄 Processing input {i}: {content[:30]}...")
        result = pipeline.check_input(content, conversation=conv)
        print_result(result, "input")
    
    # Test output with conversation context
    test_outputs = [
        "Here's your account information...",
        "I'll help you with that issue.",
    ]
    
    for i, content in enumerate(test_outputs, 1):
        print(f"\n🔄 Processing output {i}: {content[:30]}...")
        result = pipeline.check_output(content, conversation=conv)
        print_result(result, "output")
    
    print(f"\n📊 Final conversation stats:")
    print(f"   Total turns: {conv.get_turn_count()}")
    print(f"   Complete turns: {conv.get_complete_turn_count()}")
    print(f"   Duration: {conv.get_duration():.1f} seconds")


def demo_rate_limited_pipeline():
    """Demo rate limiting in pipeline context."""
    print_header("RATE LIMITED PIPELINE")
    
    # Create pipeline
    try:
        pipeline = GuardrailPipeline.from_preset("customer_service")
        print("✅ Created customer service pipeline")
    except Exception as e:
        print(f"❌ Failed to create pipeline: {e}")
        return
    
    # Create conversation with strict rate limits using factory method
    rate_limits = {"turns_per_minute": 2}
    conv = Conversation.human_ai(
        user_id="user_123",
        model_id="gpt-4",
        rate_limit=rate_limits
    )
    print(f"✅ Created conversation with rate limit: {rate_limits}")
    
    # Try to process multiple inputs quickly
    test_inputs = [
        "First message",
        "Second message", 
        "Third message (should be rate limited)",
        "Fourth message (should be rate limited)",
    ]
    
    for i, content in enumerate(test_inputs, 1):
        print(f"\n🔄 Processing input {i}: {content}")
        result = pipeline.check_input(content, conversation=conv)
        print_result(result, "input")
        
        if result['blocked'] and 'rate_limit' in result['details']:
            print("   ⏰ Rate limit hit - waiting 2 seconds...")
            time.sleep(2)
            # Try again after waiting
            result = pipeline.check_input(content, conversation=conv)
            print_result(result, "input (retry)")


def demo_conversation_serialization():
    """Demo conversation serialization and restoration."""
    print_header("CONVERSATION SERIALIZATION")
    
    # Create conversation with some turns using factory method
    conv = Conversation.human_ai(
        user_id="user_123",
        model_id="gpt-4",
        model_info={
            "model_version": "gpt-4-1106-preview",
            "provider": "openai"
        }
    )
    
    conv.add_exchange("Hello", "Hi there!")
    conv.add_exchange("How are you?", "I'm good, thanks!")
    
    print(f"✅ Created conversation: {conv.conversation_id}")
    print(f"   Turns: {conv.get_turn_count()}")
    
    # Serialize to dictionary
    conv_dict = conv.to_dict()
    print(f"\n📦 Serialized conversation:")
    print(f"   Keys: {list(conv_dict.keys())}")
    print(f"   Participants: {conv_dict['participants']}")
    print(f"   Model info: {conv_dict['model_info']}")
    print(f"   Turn count: {conv_dict['turn_count']}")
    
    # Create new conversation from dictionary
    conv_restored = Conversation.from_dict(conv_dict)
    print(f"\n🔄 Restored conversation:")
    print(f"   ID: {conv_restored.conversation_id}")
    print(f"   Initiator: {conv_restored.initiator} ({conv_restored.initiator_type})")
    print(f"   Responder: {conv_restored.responder} ({conv_restored.responder_type})")
    print(f"   Turns: {conv_restored.get_turn_count()}")
    
    # Verify history is preserved
    original_history = [(turn.prompt, turn.response) for turn in conv.get_history()]
    restored_history = [(turn.prompt, turn.response) for turn in conv_restored.get_history()]
    
    if original_history == restored_history:
        print("   ✅ History preserved correctly")
    else:
        print("   ❌ History mismatch")


def demo_forensic_analysis():
    """Demo forensic analysis capabilities."""
    print_header("FORENSIC ANALYSIS")
    
    # Create conversation and add some content using factory method
    conv = Conversation.human_ai(
        user_id="user_123",
        model_id="gpt-4",
        model_info={
            "model_version": "gpt-4-1106-preview",
            "provider": "openai"
        }
    )
    
    # Add some turns with guardrail results (simulated)
    conv.add_exchange("Hello", "Hi there!")
    conv.add_exchange("My SSN is 123-45-6789", "I understand you're having issues")  # PII
    conv.add_exchange("I'm very angry", "I'm sorry to hear that")  # Toxicity
    
    # Simulate guardrail results in metadata
    conv.turns[1].metadata['guardrail_results'] = {
        'blocked': True,
        'warnings': [],
        'reasons': ['pii_detection: SSN detected'],
        'details': {'pii_detection': {'blocked': True, 'confidence': 0.95}},
        'pipeline_type': 'input',
        'timestamp': '2024-01-15T10:30:00Z'
    }
    
    conv.turns[2].metadata['guardrail_results'] = {
        'blocked': False,
        'warnings': ['toxicity_detection: Potential threat detected'],
        'reasons': [],
        'details': {'toxicity_detection': {'blocked': False, 'confidence': 0.7}},
        'pipeline_type': 'input',
        'timestamp': '2024-01-15T10:31:00Z'
    }
    
    # Analyze conversation
    print("=== Conversation Analysis ===")
    print(f"Conversation ID: {conv.conversation_id}")
    print(f"Participants: {conv.initiator} ({conv.initiator_type}) -> {conv.responder} ({conv.responder_type})")
    print(f"Model: {conv.model_info.get('model_id', 'N/A')}")
    print(f"Duration: {conv.get_duration():.1f} seconds")
    print(f"Total turns: {conv.get_turn_count()}")
    
    # Analyze each turn
    print(f"\n=== Turn Analysis ===")
    for i, turn in enumerate(conv.get_history(), 1):
        guardrail_results = turn.metadata.get('guardrail_results', {})
        
        print(f"\nTurn {i}:")
        print(f"  {turn.speaker} -> {turn.listener}")
        print(f"  Prompt: {turn.prompt}")
        print(f"  Response: {turn.response}")
        
        if guardrail_results:
            status = "🔴 BLOCKED" if guardrail_results.get('blocked') else "🟢 APPROVED"
            print(f"  Status: {status}")
            if guardrail_results.get('reasons'):
                print(f"  Block reasons: {guardrail_results['reasons']}")
            if guardrail_results.get('warnings'):
                print(f"  Warnings: {guardrail_results['warnings']}")
            print(f"  Pipeline: {guardrail_results.get('pipeline_type')}")
        else:
            print(f"  Status: 🟢 APPROVED (no guardrail results)")
    
    # Summary statistics
    blocked_turns = [turn for turn in conv.get_history() 
                    if turn.metadata.get('guardrail_results', {}).get('blocked')]
    warned_turns = [turn for turn in conv.get_history() 
                   if turn.metadata.get('guardrail_results', {}).get('warnings')]
    
    print(f"\n=== Summary ===")
    print(f"Total turns: {conv.get_turn_count()}")
    print(f"Blocked turns: {len(blocked_turns)}")
    print(f"Warned turns: {len(warned_turns)}")


def demo_logging_context():
    """Demo conversation-aware logging."""
    print_header("LOGGING CONTEXT")
    
    # Create conversation using factory method
    conv = Conversation.human_ai(
        user_id="user_123",
        model_id="gpt-4",
        model_info={
            "model_version": "gpt-4-1106-preview",
            "provider": "openai"
        }
    )
    
    print(f"✅ Created conversation: {conv.conversation_id}")
    
    # Create pipeline
    try:
        pipeline = GuardrailPipeline.from_preset("customer_service")
        print("✅ Created pipeline")
    except Exception as e:
        print(f"❌ Failed to create pipeline: {e}")
        return
    
    # Process some content to generate logs
    print("\n🔄 Processing content (check conversation_demo.log for detailed logs)...")
    
    test_content = "This is a test message with some sensitive data like 123-45-6789"
    result = pipeline.check_input(test_content, conversation=conv)
    print_result(result, "input")
    
    result = pipeline.check_output("Here's your response", conversation=conv)
    print_result(result, "output")
    
    print(f"\n📝 Check 'conversation_demo.log' for conversation-aware logging")
    print(f"   Look for conversation ID: {conv.conversation_id}")
    print(f"   Look for participant info: {conv.initiator} -> {conv.responder}")


def demo_api_comparison():
    """Demo the before/after comparison of the API simplification."""
    print_header("API SIMPLIFICATION COMPARISON")
    
    print("🔴 BEFORE (Old API - Verbose):")
    print("```python")
    print("# Create conversation - 8 lines of boilerplate")
    print("conv = Conversation(")
    print("    participants={")
    print('        "initiator": "user_123",')
    print('        "responder": "gpt-4",')
    print('        "initiator_type": "human",')
    print('        "responder_type": "ai_model"')
    print("    },")
    print("    model_info={")
    print('        "model_id": "gpt-4",')
    print('        "model_version": "gpt-4-1106-preview",')
    print('        "provider": "openai"')
    print("    }")
    print(")")
    print("")
    print("# Add turns - multiple methods")
    print('conv.add_turn("Hello", "Hi there!")')
    print('conv.add_turn("How are you?", "I\'m good!")')
    print("```")
    
    print("\n🟢 AFTER (New API - Simplified):")
    print("```python")
    print("# Create conversation - 1 line with factory method")
    print('conv = Conversation.human_ai("user_123", "gpt-4")')
    print("")
    print("# Add exchanges - clear, single method")
    print('conv.add_exchange("Hello", "Hi there!")')
    print('conv.add_exchange("How are you?", "I\'m good!")')
    print("```")
    
    print("\n📊 IMPROVEMENTS:")
    print("  • Conversation creation: 8 lines → 1 line (87% reduction)")
    print("  • Clear intent: human_ai() vs complex dictionary")
    print("  • Consistent method: add_exchange() vs add_turn()")
    print("  • Less cognitive load: obvious what type of conversation")
    print("  • Backward compatible: old API still works")
    
    print("\n🎯 FACTORY METHODS AVAILABLE:")
    print("  • Conversation.human_ai(user_id, model_id)")
    print("  • Conversation.bot_to_bot(bot1_id, bot2_id)")
    print("  • Conversation.agent_to_agent(agent1_id, agent2_id)")
    print("  • Conversation.human_to_human(user1_id, user2_id)")
    
    print("\n🔧 CUSTOM CONVERSATIONS:")
    print("```python")
    print("# Still possible with simplified constructor")
    print("conv = Conversation(")
    print('    initiator="user_123",')
    print('    responder="gpt-4",')
    print('    initiator_type="human",')
    print('    responder_type="ai_model"')
    print(")")
    print("```")


def main():
    """Run all demos."""
    print("🚀 Stinger Conversation Demo - Phase 5f")
    print("Enhanced conversation management with simplified API and factory methods")
    
    setup_logging()
    
    try:
        demo_api_comparison()
        demo_basic_conversation()
        demo_different_conversation_types()
        demo_rate_limiting()
        demo_prompt_response_separation()
        demo_pipeline_integration()
        demo_rate_limited_pipeline()
        demo_conversation_serialization()
        demo_forensic_analysis()
        demo_logging_context()
        
        print_header("DEMO COMPLETE")
        print("✅ All demos completed successfully!")
        print("\nKey features demonstrated:")
        print("  • Simplified API with factory methods (human_ai, bot_to_bot, etc.)")
        print("  • Participant tracking (initiator/responder with types)")
        print("  • Model information for AI conversations")
        print("  • Complete prompt-response exchanges (add_exchange)")
        print("  • Rate limiting")
        print("  • Serialization")
        print("  • Pipeline integration with automatic guardrail annotation")
        print("  • Forensic analysis capabilities")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    sys.exit(main()) 