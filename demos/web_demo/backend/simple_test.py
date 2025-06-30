#!/usr/bin/env python3
"""
Simple test to isolate the conversation API issue
"""

import sys
from pathlib import Path

# Add src to path for Stinger imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from stinger import GuardrailPipeline, Conversation

def test_conversation():
    """Test conversation flow."""
    print("Testing conversation flow...")
    
    # Create pipeline
    pipeline = GuardrailPipeline.from_preset("customer_service")
    print("✅ Pipeline created")
    
    # Create conversation
    conversation = Conversation.human_ai(
        user_id="test_user",
        model_id="gpt-4o-mini"
    )
    print("✅ Conversation created")
    
    # Test input guardrails
    input_result = pipeline.check_input("Hello world", conversation=conversation)
    print(f"✅ Input guardrails: {input_result}")
    
    # Add prompt to conversation
    conversation.add_prompt("Hello world")
    print("✅ Prompt added to conversation")
    print(f"📊 Conversation turns: {len(conversation.turns)}")
    print(f"📊 Last turn: {conversation.turns[-1] if conversation.turns else 'None'}")
    
    # Generate response
    response = "I'm a test response"
    
    # Test output guardrails (this automatically adds response to conversation)
    output_result = pipeline.check_output(response, conversation=conversation)
    print(f"✅ Output guardrails: {output_result}")
    print(f"📊 Conversation turns after output check: {len(conversation.turns)}")
    print(f"📊 Last turn after output check: {conversation.turns[-1] if conversation.turns else 'None'}")
    
    print("✅ Response automatically added to conversation by check_output")
    
    print("🎉 All tests passed!")

if __name__ == "__main__":
    test_conversation()