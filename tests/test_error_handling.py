#!/usr/bin/env python3
"""
Tests for Production Error Handling

Verifies secure error message handling and environment detection.
"""

import os
from unittest.mock import patch

import pytest

from src.stinger.core.error_handling import (
    ProductionErrorHandler,
    is_production,
    safe_error_message,
    sanitize_error_details,
    sanitize_path,
)


class TestEnvironmentDetection:
    """Test production environment detection."""

    def test_production_environment_detection(self):
        """Test various production environment indicators."""
        # Test explicit production environment variables
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            handler = ProductionErrorHandler()
            assert handler.is_production() is True

        with patch.dict(os.environ, {"ENV": "prod"}):
            handler = ProductionErrorHandler()
            assert handler.is_production() is True

        with patch.dict(os.environ, {"STAGE": "production"}):
            handler = ProductionErrorHandler()
            assert handler.is_production() is True

    def test_development_environment_detection(self):
        """Test development environment detection."""
        with patch.dict(os.environ, {"DEBUG": "1", "DEVELOPMENT": "1"}, clear=True):
            handler = ProductionErrorHandler()
            assert handler.is_production() is False

        with patch.dict(os.environ, {"ENV": "development"}, clear=True):
            handler = ProductionErrorHandler()
            assert handler.is_production() is False

    def test_cloud_provider_detection(self):
        """Test cloud provider environment detection."""
        # Heroku
        with patch.dict(os.environ, {"DYNO": "web.1"}, clear=True):
            handler = ProductionErrorHandler()
            assert handler.is_production() is True

        # AWS
        with patch.dict(os.environ, {"AWS_EXECUTION_ENV": "AWS_ECS_FARGATE"}, clear=True):
            handler = ProductionErrorHandler()
            assert handler.is_production() is True

        # Google Cloud
        with patch.dict(os.environ, {"GOOGLE_CLOUD_PROJECT": "my-project"}, clear=True):
            handler = ProductionErrorHandler()
            assert handler.is_production() is True

    def test_default_environment_detection(self):
        """Test default to development when environment is unclear."""
        with patch.dict(os.environ, {}, clear=True):
            handler = ProductionErrorHandler()
            assert handler.is_production() is False


class TestErrorMessageSanitization:
    """Test error message sanitization functionality."""

    def test_development_error_messages(self):
        """Test that development shows full error details."""
        with patch.dict(os.environ, {"DEBUG": "1"}, clear=True):
            handler = ProductionErrorHandler()

            error = ValueError("Database connection failed: host not found")
            message = handler.safe_error_message(error, "database operation")

            assert "Database connection failed: host not found" in message
            assert "database operation failed" in message

    def test_production_error_messages(self):
        """Test that production sanitizes error messages."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=True):
            handler = ProductionErrorHandler()

            error = ValueError("Database connection failed: host secret-db.internal not found")
            message = handler.safe_error_message(error, "database operation")

            assert "secret-db.internal" not in message
            assert "database operation failed" in message
            assert "Error ID:" in message
            assert len(message.split("Error ID: ")[1].split("]")[0]) == 8  # 8-char error ID

    def test_error_type_inclusion(self):
        """Test optional error type inclusion."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=True):
            handler = ProductionErrorHandler()

            error = ValueError("Some error")
            message = handler.safe_error_message(error, "operation", include_type=True)

            assert "ValueError" in message
            assert "operation failed (ValueError)" in message

    def test_error_id_generation(self):
        """Test error ID generation and tracking."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=True):
            handler = ProductionErrorHandler()

            error = ValueError("Test error")
            message1 = handler.safe_error_message(error, "operation")
            message2 = handler.safe_error_message(error, "operation")

            # Extract error IDs
            id1 = message1.split("Error ID: ")[1].split("]")[0]
            id2 = message2.split("Error ID: ")[1].split("]")[0]

            # Should be different error IDs
            assert id1 != id2
            assert len(id1) == 8
            assert len(id2) == 8

            # Should be able to retrieve original error
            assert handler.get_error_by_id(id1) == "Test error"
            assert handler.get_error_by_id(id2) == "Test error"


class TestPathSanitization:
    """Test file path sanitization."""

    def test_development_path_handling(self):
        """Test that development shows full paths."""
        with patch.dict(os.environ, {"DEBUG": "1"}, clear=True):
            handler = ProductionErrorHandler()

            path = "/home/user/secret/config/database.yaml"
            sanitized = handler.sanitize_path(path)

            assert sanitized == path  # Full path in development

    def test_production_path_sanitization(self):
        """Test that production only shows filenames."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=True):
            handler = ProductionErrorHandler()

            path = "/home/user/secret/config/database.yaml"
            sanitized = handler.sanitize_path(path)

            assert sanitized == "database.yaml"  # Only filename in production
            assert "/home/user/secret" not in sanitized

    def test_invalid_path_handling(self):
        """Test handling of invalid path strings."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=True):
            handler = ProductionErrorHandler()

            # Test path with backslash
            backslash_path = "C:\\temp\\config.txt"
            sanitized = handler.sanitize_path(backslash_path)
            assert sanitized == "config.txt"

            # Test path with no separators (returns as-is or generic)
            no_separator_path = "config.txt"
            sanitized = handler.sanitize_path(no_separator_path)
            assert sanitized == "config.txt"  # Should return filename part


class TestErrorDetailsSanitization:
    """Test error details dictionary sanitization."""

    def test_development_details_preservation(self):
        """Test that development preserves all details."""
        with patch.dict(os.environ, {"DEBUG": "1"}, clear=True):
            handler = ProductionErrorHandler()

            details = {
                "error": "Database connection failed",
                "path": "/secret/config.yaml",
                "stack_trace": 'File "/app/main.py", line 42',
                "api_key": "sk-1234567890abcdef",
            }

            sanitized = handler.sanitize_error_details(details)
            assert sanitized == details  # No sanitization in development

    def test_production_details_sanitization(self):
        """Test that production sanitizes sensitive details."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=True):
            handler = ProductionErrorHandler()

            details = {
                "error": "Database connection failed to host secret-db.internal",
                "config_path": "/secret/config.yaml",
                "stack_trace": 'File "/app/main.py", line 42',
                "api_key": "sk-1234567890abcdef",
                "timestamp": "2024-01-01T12:00:00Z",
                "context": "database_init",
            }

            sanitized = handler.sanitize_error_details(details)

            # Safe keys preserved
            assert sanitized["timestamp"] == "2024-01-01T12:00:00Z"
            assert sanitized["context"] == "database_init"

            # Error messages sanitized
            assert "secret-db.internal" not in sanitized["error"]

            # Paths sanitized
            assert sanitized["config_path"] == "config.yaml"

            # Sensitive keys redacted
            assert sanitized["api_key"] == "[redacted]"
            assert sanitized["stack_trace"] == "[redacted]"


class TestStringSanitization:
    """Test low-level string sanitization functions."""

    def test_file_path_removal(self):
        """Test removal of file paths from error strings."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=True):
            handler = ProductionErrorHandler()

            error_str = "Failed to open /home/user/secret/file.txt for reading"
            sanitized = handler._sanitize_error_string(error_str)

            assert "/home/user/secret/file.txt" not in sanitized
            assert "[path]" in sanitized

    def test_windows_path_removal(self):
        """Test removal of Windows file paths."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=True):
            handler = ProductionErrorHandler()

            error_str = "Cannot access C:\\Users\\admin\\secret\\config.ini"
            sanitized = handler._sanitize_error_string(error_str)

            assert "C:\\Users\\admin\\secret\\config.ini" not in sanitized
            assert "[path]" in sanitized

    def test_stack_trace_sanitization(self):
        """Test stack trace information sanitization."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=True):
            handler = ProductionErrorHandler()

            error_str = 'File "/app/src/secret_module.py", line 123, in secret_function'
            sanitized = handler._sanitize_error_string(error_str)

            assert "/app/src/secret_module.py" not in sanitized
            assert "File [path], line [number]" in sanitized

    def test_sensitive_data_removal(self):
        """Test removal of sensitive data patterns."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=True):
            handler = ProductionErrorHandler()

            test_cases = [
                "api_key=sk-1234567890abcdef failed",
                'password="secret123" not found',
                "secret: 'my-secret-token' invalid",
                "token=bearer-abc123xyz failed",
            ]

            for error_str in test_cases:
                sanitized = handler._sanitize_error_string(error_str)
                assert "[redacted]" in sanitized
                assert "sk-1234567890abcdef" not in sanitized
                assert "secret123" not in sanitized
                assert "my-secret-token" not in sanitized
                assert "bearer-abc123xyz" not in sanitized


class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    def test_safe_error_message_function(self):
        """Test convenience function for safe error messages."""
        # Reset global state
        from src.stinger.core import error_handling

        error_handling._error_handler = None

        with patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=True):
            error = ValueError("Test error")
            message = safe_error_message(error, "test operation")

            assert "test operation failed" in message
            assert "Error ID:" in message

    def test_sanitize_path_function(self):
        """Test convenience function for path sanitization."""
        # Reset global state
        from src.stinger.core import error_handling

        error_handling._error_handler = None

        with patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=True):
            path = "/secret/config.yaml"
            sanitized = sanitize_path(path)
            assert sanitized == "config.yaml"

    def test_sanitize_error_details_function(self):
        """Test convenience function for error details sanitization."""
        # Reset global state
        from src.stinger.core import error_handling

        error_handling._error_handler = None

        with patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=True):
            details = {"error": "test error", "sensitive": "secret data"}
            sanitized = sanitize_error_details(details)
            assert sanitized["sensitive"] == "[redacted]"

    def test_is_production_function(self):
        """Test convenience function for production detection."""
        # Reset global state for production test
        from src.stinger.core import error_handling

        error_handling._error_handler = None

        with patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=True):
            assert is_production() is True

        # Reset global state for development test
        error_handling._error_handler = None

        with patch.dict(os.environ, {"DEBUG": "1"}, clear=True):
            assert is_production() is False


class TestErrorLogging:
    """Test error logging functionality."""

    def test_error_logging_in_production(self):
        """Test that errors are logged with full details in production."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=True):
            handler = ProductionErrorHandler()

            with patch.object(handler.logger, "error") as mock_logger:
                error = ValueError("Test error with sensitive data")
                message = handler.safe_error_message(error, "test operation")

                # Extract error ID
                error_id = message.split("Error ID: ")[1].split("]")[0]

                # Verify logging was called with full details
                mock_logger.assert_called_once()
                log_call = mock_logger.call_args

                assert f"Error ID {error_id}" in log_call[0][0]
                assert "ValueError" in log_call[0][0]
                assert "Test error with sensitive data" in log_call[0][0]
                assert log_call[1]["extra"]["error_id"] == error_id
                assert log_call[1]["extra"]["is_production"] is True


class TestIntegrationWithExistingCode:
    """Test integration with existing codebase error handling."""

    def test_audit_log_error_handling(self):
        """Test that audit log error handling uses safe messages."""
        # This would test the actual audit.py integration
        # but requires the audit module to be importable

    def test_prompt_injection_filter_error_handling(self):
        """Test that prompt injection filter uses safe error handling."""
        # This would test the actual filter integration
        # but requires the filter to be importable and configured


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
