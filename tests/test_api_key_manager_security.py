#!/usr/bin/env python3
"""
Security tests for API Key Manager

Tests cover encryption key management vulnerabilities and security constraints.
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.stinger.core.api_key_manager import APIKeyManager, SecurityError


class TestAPIKeyManagerSecurity:
    """Security-focused tests for API key management."""

    def test_encryption_key_failure_modes(self):
        """Test secure failure when encryption unavailable."""
        with patch("src.stinger.core.api_key_manager.ENCRYPTION_AVAILABLE", False):
            # Should create manager but with no encryption capability
            manager = APIKeyManager()

            # Verify encryption key is None (secure fallback)
            assert manager.encryption_key is None

            # Verify fernet is None (no encryption)
            assert manager._fernet is None

            # Should still work with environment variables
            test_key = "sk-test-key-12345"
            with patch.dict(os.environ, {"OPENAI_API_KEY": test_key}, clear=True):
                # Create fresh manager to test environment loading
                manager_fresh = APIKeyManager()
                assert manager_fresh.get_openai_key() == test_key

    def test_key_export_production_block(self):
        """Test key export blocked in production."""
        # Create manager in controlled way to avoid initialization issues
        with patch("src.stinger.core.api_key_manager.ENCRYPTION_AVAILABLE", True), patch(
            "src.stinger.core.api_key_manager.Fernet"
        ) as mock_fernet, patch(
            "sys.argv", ["stinger"]
        ):  # Non-test argv

            # Mock Fernet properly
            test_key = "test-encryption-key-123"
            mock_fernet.generate_key.return_value.decode.return_value = test_key
            mock_fernet_instance = MagicMock()
            mock_fernet.return_value = mock_fernet_instance

            # Remove pytest module temporarily to avoid development detection
            pytest_module = sys.modules.pop("pytest", None)
            try:
                # Create manager with clean environment
                with patch.dict(os.environ, {"STINGER_ENV": "production"}, clear=True):
                    manager = APIKeyManager()

                    # Verify production environment is detected
                    assert manager._is_development() == False

                    # Test that key export is blocked
                    with pytest.raises(SecurityError, match="Key export not allowed in production"):
                        manager.export_encryption_key()
            finally:
                if pytest_module:
                    sys.modules["pytest"] = pytest_module

    def test_key_export_development_allowed(self):
        """Test key export allowed in development."""
        with patch("src.stinger.core.api_key_manager.ENCRYPTION_AVAILABLE", True), patch(
            "src.stinger.core.api_key_manager.Fernet"
        ) as mock_fernet:

            # Mock Fernet to work properly
            test_key = "test-encryption-key"
            mock_fernet.generate_key.return_value.decode.return_value = test_key
            mock_fernet_instance = MagicMock()
            mock_fernet.return_value = mock_fernet_instance

            manager = APIKeyManager()

            # Test development environment
            with patch.dict(os.environ, {"STINGER_ENV": "development"}):
                exported_key = manager.export_encryption_key()
                assert exported_key == test_key

    def test_environment_detection_methods(self):
        """Test various environment detection methods."""
        with patch("src.stinger.core.api_key_manager.ENCRYPTION_AVAILABLE", True), patch(
            "src.stinger.core.api_key_manager.Fernet"
        ) as mock_fernet:

            mock_fernet.generate_key.return_value.decode.return_value = "test-key"
            mock_fernet_instance = MagicMock()
            mock_fernet.return_value = mock_fernet_instance

            manager = APIKeyManager()

            # Test STINGER_ENV=development
            with patch.dict(os.environ, {"STINGER_ENV": "development"}):
                assert manager._is_development() == True

            # Test DEVELOPMENT=1
            with patch.dict(os.environ, {"DEVELOPMENT": "1"}):
                assert manager._is_development() == True

            # Test DEBUG=true
            with patch.dict(os.environ, {"DEBUG": "true"}):
                assert manager._is_development() == True

            # Test pytest detection
            if "pytest" in sys.modules:
                assert manager._is_development() == True

            # Test production environment - patch sys.argv to avoid test detection
            with patch.dict(os.environ, {}, clear=True), patch(
                "sys.argv", ["stinger"]
            ):  # Non-test argv
                # Remove pytest from modules temporarily for this test
                pytest_module = sys.modules.pop("pytest", None)
                try:
                    assert manager._is_development() == False
                finally:
                    if pytest_module:
                        sys.modules["pytest"] = pytest_module

    def test_no_encryption_key_export_fails(self):
        """Test export fails when no encryption key available."""
        # Create manager without encryption
        with patch("src.stinger.core.api_key_manager.ENCRYPTION_AVAILABLE", False):
            # This should create a manager with environment variables only
            manager = APIKeyManager()
            manager.encryption_key = None  # Explicitly set to None

            with patch.dict(os.environ, {"STINGER_ENV": "development"}):
                with pytest.raises(SecurityError, match="No encryption key available"):
                    manager.export_encryption_key()

    def test_caller_info_logging(self):
        """Test that caller information is logged for security events."""
        with patch("src.stinger.core.api_key_manager.ENCRYPTION_AVAILABLE", True), patch(
            "src.stinger.core.api_key_manager.Fernet"
        ) as mock_fernet:

            mock_fernet.generate_key.return_value.decode.return_value = "test-key"
            mock_fernet_instance = MagicMock()
            mock_fernet.return_value = mock_fernet_instance

            manager = APIKeyManager()

            # Test caller info is generated
            caller_info = manager._get_caller_info()
            assert isinstance(caller_info, str)
            assert len(caller_info) > 0

    def test_environment_variable_only_mode(self):
        """Test that manager works with environment variables when encryption unavailable."""
        with patch("src.stinger.core.api_key_manager.ENCRYPTION_AVAILABLE", False):
            # Set environment variable
            test_key = "sk-test-key-12345"
            with patch.dict(os.environ, {"OPENAI_API_KEY": test_key}):
                manager = APIKeyManager()

                # Should still be able to get keys from environment
                assert manager.get_openai_key() == test_key
                assert manager.encryption_key is None

    def test_encrypted_storage_requires_encryption(self):
        """Test that encrypted storage operations fail safely without encryption."""
        with patch("src.stinger.core.api_key_manager.ENCRYPTION_AVAILABLE", False):
            manager = APIKeyManager()

            # Trying to save to encrypted storage should fail gracefully
            result = manager.save_to_secure_storage("test_service", "test_key")
            assert result == False

    def test_secure_initialization_with_existing_key(self):
        """Test initialization with existing encryption key."""
        with patch("src.stinger.core.api_key_manager.ENCRYPTION_AVAILABLE", True), patch(
            "src.stinger.core.api_key_manager.Fernet"
        ) as mock_fernet:

            existing_key = "existing-encryption-key"
            mock_fernet_instance = MagicMock()
            mock_fernet.return_value = mock_fernet_instance

            # Initialize with existing key (should not generate new one)
            manager = APIKeyManager(encryption_key=existing_key)

            assert manager.encryption_key == existing_key
            # Should not have called generate_key since we provided one
            mock_fernet.generate_key.assert_not_called()

    def test_security_error_inheritance(self):
        """Test that SecurityError is proper exception type."""
        assert issubclass(SecurityError, Exception)

        # Test raising and catching
        with pytest.raises(SecurityError):
            raise SecurityError("Test security error")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
