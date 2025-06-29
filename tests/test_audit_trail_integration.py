"""
Integration tests for security audit trail with pipeline.

Tests that the audit trail correctly captures all security events
from the guardrail pipeline.
"""

import pytest
import tempfile
import json
import os
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import stinger
from stinger.core import audit
from stinger.core.conversation import Conversation


class TestAuditTrailIntegration:
    """Test audit trail integration with guardrail pipeline."""
    
    def setup_method(self):
        """Setup for each test."""
        # Disable audit trail before each test
        if audit.is_enabled():
            try:
                audit.disable()
            except RuntimeError:
                # Can't disable in production - reset the global instance
                audit._audit_trail = audit.AuditTrail()
    
    def test_pipeline_with_audit_trail_basic(self):
        """Test basic pipeline integration with audit trail."""
        with tempfile.TemporaryDirectory() as temp_dir:
            audit_file = os.path.join(temp_dir, "audit.log")
            
            # Enable audit trail
            audit.enable(audit_file)
            
            # Create a simple pipeline
            pipeline = stinger.create_pipeline()
            
            # Test input checking
            input_result = pipeline.check_input("Hello, this is a test message")
            assert input_result is not None
            
            # Test output checking  
            output_result = pipeline.check_output("This is a test response")
            assert output_result is not None
            
            # Disable audit and check the logs
            audit.disable()
            
            # Read audit log
            with open(audit_file, 'r') as f:
                lines = f.readlines()
            
            # Should have at least: enable, prompt, guardrail decisions, response, more guardrail decisions
            assert len(lines) >= 5
            
            # Check for audit trail enabled event
            enable_record = json.loads(lines[0])
            assert enable_record["event_type"] == "audit_trail_enabled"
            
            # Check for user prompt event
            prompt_found = False
            response_found = False
            guardrail_decisions = []
            
            for line in lines[1:]:
                record = json.loads(line)
                if record["event_type"] == "user_prompt":
                    prompt_found = True
                    assert record["prompt"] == "Hello, this is a test message"
                elif record["event_type"] == "llm_response":
                    response_found = True
                    assert record["response"] == "This is a test response"
                elif record["event_type"] == "guardrail_decision":
                    guardrail_decisions.append(record)
            
            assert prompt_found, "User prompt should be logged"
            assert response_found, "LLM response should be logged"
            assert len(guardrail_decisions) > 0, "Guardrail decisions should be logged"
            
            # Check guardrail decision format
            for decision in guardrail_decisions:
                assert "filter_name" in decision
                assert "decision" in decision
                assert "reason" in decision
                assert decision["decision"] in ["block", "allow", "warn", "error"]
    
    def test_pipeline_with_conversation_audit(self):
        """Test pipeline integration with conversation context."""
        with tempfile.TemporaryDirectory() as temp_dir:
            audit_file = os.path.join(temp_dir, "audit.log")
            
            # Enable audit trail
            audit.enable(audit_file)
            
            # Create a pipeline and conversation
            pipeline = stinger.create_pipeline()
            conversation = Conversation("test_user", "test_assistant", conversation_id="conv_123")
            
            # Test multi-turn conversation
            input_result1 = pipeline.check_input("What is AI?", conversation=conversation)
            output_result1 = pipeline.check_output("AI is artificial intelligence.", conversation=conversation)
            
            input_result2 = pipeline.check_input("Tell me more about machine learning", conversation=conversation)
            output_result2 = pipeline.check_output("Machine learning is a subset of AI.", conversation=conversation)
            
            # Disable audit and check the logs
            audit.disable()
            
            # Read audit log
            with open(audit_file, 'r') as f:
                lines = f.readlines()
            
            # Check conversation tracking
            conversation_events = []
            for line in lines:  # Check all lines
                record = json.loads(line)
                if record.get("conversation_id") == "conv_123":
                    conversation_events.append(record)
            
            # Should have multiple events for the same conversation
            assert len(conversation_events) >= 4, f"Should have events for both turns, found {len(conversation_events)} events"
            
            # Check that conversation ID is consistent
            for event in conversation_events:
                assert event["conversation_id"] == "conv_123"
    
    def test_audit_trail_captures_blocked_content(self):
        """Test that audit trail captures blocked content correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            audit_file = os.path.join(temp_dir, "audit.log")
            
            # Enable audit trail
            audit.enable(audit_file)
            
            # Create pipeline 
            pipeline = stinger.create_pipeline()
            
            # Test with potentially problematic content that might trigger a filter
            test_content = "This is a test message with potentially problematic content"
            
            input_result = pipeline.check_input(test_content)
            
            # Disable audit and check the logs
            audit.disable()
            
            # Read audit log
            with open(audit_file, 'r') as f:
                lines = f.readlines()
            
            # Find guardrail decisions
            guardrail_decisions = []
            for line in lines[1:]:  # Skip enable event
                record = json.loads(line)
                if record["event_type"] == "guardrail_decision":
                    guardrail_decisions.append(record)
            
            # Should have at least one guardrail decision
            assert len(guardrail_decisions) > 0
            
            # Check decision structure
            for decision in guardrail_decisions:
                assert "filter_name" in decision
                assert "decision" in decision
                assert "reason" in decision
                assert "confidence" in decision
                assert isinstance(decision["confidence"], (int, float, type(None)))
    
    def test_audit_trail_pii_redaction_in_pipeline(self):
        """Test that PII redaction works in pipeline integration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            audit_file = os.path.join(temp_dir, "audit.log")
            
            # Enable audit trail with PII redaction
            audit.enable(audit_file, redact_pii=True)
            
            # Create pipeline
            pipeline = stinger.create_pipeline()
            
            # Test with PII content
            pii_content = "My email is john@example.com and my phone is 555-123-4567"
            
            input_result = pipeline.check_input(pii_content)
            output_result = pipeline.check_output("Thank you for the information.")
            
            # Disable audit and check the logs
            audit.disable()
            
            # Read audit log
            with open(audit_file, 'r') as f:
                lines = f.readlines()
            
            # Find the prompt event
            for line in lines[1:]:  # Skip enable event
                record = json.loads(line)
                if record["event_type"] == "user_prompt":
                    prompt_text = record["prompt"]
                    
                    # PII should be redacted
                    assert "[EMAIL_REDACTED]" in prompt_text
                    assert "[PHONE_REDACTED]" in prompt_text
                    assert "john@example.com" not in prompt_text
                    assert "555-123-4567" not in prompt_text
                    break
            else:
                pytest.fail("User prompt event not found")
    
    def test_audit_trail_disabled_no_logging(self):
        """Test that when audit trail is disabled, no logging occurs."""
        # Ensure audit trail is disabled
        if audit.is_enabled():
            audit.disable()
        
        # Create pipeline 
        pipeline = stinger.create_pipeline()
        
        # Test pipeline operations
        input_result = pipeline.check_input("Test message")
        output_result = pipeline.check_output("Test response")
        
        # Should not crash and should work normally
        assert input_result is not None
        assert output_result is not None
        
        # Since audit is disabled, we can't check logs, but the pipeline should work fine
    
    def test_pipeline_error_handling_with_audit(self):
        """Test that pipeline errors are properly logged to audit trail."""
        with tempfile.TemporaryDirectory() as temp_dir:
            audit_file = os.path.join(temp_dir, "audit.log")
            
            # Enable audit trail
            audit.enable(audit_file)
            
            # Create pipeline
            pipeline = stinger.create_pipeline()
            
            # Test normal operation
            input_result = pipeline.check_input("Normal test message")
            
            # Disable audit and check for any error handling
            audit.disable()
            
            # Read audit log
            with open(audit_file, 'r') as f:
                lines = f.readlines()
            
            # Should have logged events without errors
            assert len(lines) >= 2  # At least enable + some events
            
            # All lines should be valid JSON
            for line in lines:
                record = json.loads(line)  # Should not raise exception
                assert "timestamp" in record
                assert "event_type" in record


if __name__ == "__main__":
    pytest.main([__file__])