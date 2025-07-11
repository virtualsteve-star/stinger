"""
Pytest configuration for API tests.
"""

import pytest
import os
from typing import Generator
from unittest.mock import patch


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Set up test environment variables."""
    # Set a test API key if not already set
    if not os.environ.get("OPENAI_API_KEY"):
        monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
    
    # Ensure we're in test mode
    monkeypatch.setenv("STINGER_ENV", "test")


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for tests that don't need real API calls."""
    with patch("openai.OpenAI") as mock:
        # Configure mock responses as needed
        yield mock


@pytest.fixture
def disable_rate_limiting(monkeypatch):
    """Disable rate limiting for tests."""
    monkeypatch.setenv("STINGER_DISABLE_RATE_LIMIT", "true")


@pytest.fixture
def test_preset_config():
    """Provide a test preset configuration."""
    return {
        "input_pipeline": [
            {
                "type": "simple_pii_detection",
                "enabled": True,
                "config": {}
            }
        ],
        "output_pipeline": [
            {
                "type": "simple_pii_detection",
                "enabled": True,
                "config": {}
            }
        ]
    }