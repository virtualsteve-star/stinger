"""
Basic tests for security audit trail system.

Tests the ultra-simple API and basic functionality.
"""

import json
import os
import sys
import tempfile
from unittest.mock import patch

import pytest

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import stinger
from stinger.core import audit


class TestAuditTrailBasic:
    """Test basic audit trail functionality."""

    def setup_method(self):
        """Setup for each test."""
        # Disable audit trail before each test
        if audit.is_enabled():
            try:
                audit.disable()
            except RuntimeError:
                # Can't disable in production - reset the global instance
                audit._audit_trail = audit.AuditTrail()

    def test_zero_config_enable(self):
        """Test that audit.enable() works with no configuration."""
        # Should work without any arguments
        audit.enable()

        assert audit.is_enabled() == True

        # Clean up
        audit.disable()

    def test_enable_with_stdout_destination(self):
        """Test enabling audit with stdout destination."""
        audit.enable("stdout")

        assert audit.is_enabled() == True
        assert audit._audit_trail._destination == "stdout"

        # Clean up
        audit.disable()

    def test_enable_with_file_destination(self):
        """Test enabling audit with file destination."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test_audit.log")

            audit.enable(log_file)

            assert audit.is_enabled() == True
            assert audit._audit_trail._destination == log_file

            # Clean up
            audit.disable()

    def test_enable_with_redact_pii(self):
        """Test enabling audit with PII redaction."""
        audit.enable("stdout", redact_pii=True)

        assert audit.is_enabled() == True
        assert audit._audit_trail._redact_pii == True

        # Clean up
        audit.disable()

    def test_disable_in_development(self):
        """Test that disable works in development environment."""
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
            audit.enable("stdout")
            assert audit.is_enabled() == True

            audit.disable()
            assert audit.is_enabled() == False

    def test_cannot_disable_in_production(self):
        """Test that disable raises error in production environment."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            audit.enable("stdout")
            assert audit.is_enabled() == True

            with pytest.raises(RuntimeError, match="Cannot disable audit trail in production"):
                audit.disable()

    def test_smart_environment_detection_dev(self):
        """Test smart environment detection in development."""
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
            audit.enable()  # No destination specified

            # Should choose stdout for development
            assert audit._audit_trail._destination == "stdout"
            assert audit._audit_trail._redact_pii == False  # No redaction in dev

            audit.disable()

    def test_smart_environment_detection_prod(self):
        """Test smart environment detection in production."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            audit.enable()  # No destination specified

            # Should choose file for production
            assert audit._audit_trail._destination == "./audit.log"
            assert audit._audit_trail._redact_pii == True  # Redaction in prod

            # Can't disable in prod, so reset manually
            audit._audit_trail = audit.AuditTrail()

    def test_log_prompt_basic(self):
        """Test basic prompt logging functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test_audit.log")

            audit.enable(log_file)

            # Log a prompt
            audit.log_prompt(
                prompt="What is the weather?",
                user_id="user_123",
                conversation_id="conv_456",
                request_id="req_789",
            )

            audit.disable()

            # Check the log file
            with open(log_file, "r") as f:
                lines = f.readlines()

            # Should have 2 lines: enable event + prompt event
            assert len(lines) == 2

            # Check the prompt record
            prompt_record = json.loads(lines[1])
            assert prompt_record["event_type"] == "user_prompt"
            assert prompt_record["prompt"] == "What is the weather?"
            assert prompt_record["user_id"] == "user_123"
            assert prompt_record["conversation_id"] == "conv_456"
            assert prompt_record["request_id"] == "req_789"
            assert "timestamp" in prompt_record

    def test_log_response_basic(self):
        """Test basic response logging functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test_audit.log")

            audit.enable(log_file)

            # Log a response
            audit.log_response(
                response="It's sunny today!",
                user_id="user_123",
                conversation_id="conv_456",
                request_id="req_789",
                model_used="gpt-4.1-nano",
                processing_time_ms=150,
            )

            audit.disable()

            # Check the log file
            with open(log_file, "r") as f:
                lines = f.readlines()

            # Should have 2 lines: enable event + response event
            assert len(lines) == 2

            # Check the response record
            response_record = json.loads(lines[1])
            assert response_record["event_type"] == "llm_response"
            assert response_record["response"] == "It's sunny today!"
            assert response_record["user_id"] == "user_123"
            assert response_record["model_used"] == "gpt-4.1-nano"
            assert response_record["processing_time_ms"] == 150

    def test_log_guardrail_decision_basic(self):
        """Test basic guardrail decision logging functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test_audit.log")

            audit.enable(log_file)

            # Log a guardrail decision
            audit.log_guardrail_decision(
                guardrail_name="content_moderation",
                decision="block",
                reason="Content violates policy",
                user_id="user_123",
                conversation_id="conv_456",
                request_id="req_789",
                confidence=0.95,
                rule_triggered="violence_detection",
            )

            audit.disable()

            # Check the log file
            with open(log_file, "r") as f:
                lines = f.readlines()

            # Should have 2 lines: enable event + decision event
            assert len(lines) == 2

            # Check the decision record
            decision_record = json.loads(lines[1])
            assert decision_record["event_type"] == "guardrail_decision"
            assert decision_record["guardrail_name"] == "content_moderation"
            assert decision_record["decision"] == "block"
            assert decision_record["reason"] == "Content violates policy"
            assert decision_record["confidence"] == 0.95
            assert decision_record["rule_triggered"] == "violence_detection"

    def test_pii_redaction_basic(self):
        """Test basic PII redaction functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test_audit.log")

            audit.enable(log_file, redact_pii=True)

            # Log a prompt with PII
            audit.log_prompt(
                prompt="My email is john@example.com and my phone is 555-123-4567",
                user_id="user_123",
            )

            audit.disable()

            # Check the log file
            with open(log_file, "r") as f:
                lines = f.readlines()

            # Check the prompt record
            prompt_record = json.loads(lines[1])
            prompt_text = prompt_record["prompt"]

            # PII should be redacted
            assert "[EMAIL_REDACTED]" in prompt_text
            assert "[PHONE_REDACTED]" in prompt_text
            assert "john@example.com" not in prompt_text
            assert "555-123-4567" not in prompt_text

    def test_stinger_audit_import(self):
        """Test that audit can be imported from main stinger package."""
        # Should be able to access audit module
        assert hasattr(stinger, "audit")
        assert hasattr(stinger.audit, "enable")
        assert hasattr(stinger.audit, "disable")
        assert hasattr(stinger.audit, "is_enabled")

    def test_file_creation(self):
        """Test that audit log file and directories are created automatically."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Use a nested directory that doesn't exist
            log_file = os.path.join(temp_dir, "nested", "dir", "audit.log")

            audit.enable(log_file)

            # File should be created
            assert os.path.exists(log_file)

            audit.disable()


if __name__ == "__main__":
    pytest.main([__file__])
