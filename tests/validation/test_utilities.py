"""
Common test utilities and helper functions for Stinger tests.
"""

import json
import os
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import pytest
import yaml


@pytest.mark.ci
class TestDataGenerator:
    """Generate test data for various scenarios."""

    @staticmethod
    def generate_pii_samples() -> List[str]:
        """Generate various PII test samples."""
        return [
            "My SSN is 123-45-6789",
            "Credit card: 4111-1111-1111-1111",
            "Call me at (555) 123-4567",
            "Email: test@example.com",
            "My passport number is A12345678",
            "Driver's license: D123-4567-8901",
            "IP address: 192.168.1.1",
            "Account number: 12345678901234",
        ]

    @staticmethod
    def generate_toxic_samples() -> List[str]:
        """Generate toxic content samples for testing."""
        return [
            "You are stupid!",
            "I hate you",
            "Go kill yourself",  # Severe
            "You're worthless",
            "Shut up idiot",
            "Nobody likes you",
        ]

    @staticmethod
    def generate_safe_samples() -> List[str]:
        """Generate safe content samples."""
        return [
            "Hello, how can I help you?",
            "Thank you for your patience",
            "I appreciate your feedback",
            "Have a great day!",
            "Let me assist you with that",
            "Could you please provide more details?",
        ]

    @staticmethod
    def generate_edge_cases() -> List[str]:
        """Generate edge case samples."""
        return [
            "",  # Empty string
            " ",  # Whitespace only
            "a" * 10000,  # Very long string
            "🚀🎉😊",  # Emojis only
            "!@#$%^&*()",  # Special characters
            "\n\n\n",  # Newlines only
            "NULL",  # Null-like string
            "<script>alert('xss')</script>",  # HTML/JS
        ]


class GuardrailTestHelper:
    """Helper functions for testing guardrails."""

    @staticmethod
    def assert_blocks_all(guardrail, test_samples: List[str]):
        """Assert that guardrail blocks all samples."""
        for sample in test_samples:
            result = guardrail.check(sample)
            assert result.blocked, f"Expected to block: '{sample}'"

    @staticmethod
    def assert_allows_all(guardrail, test_samples: List[str]):
        """Assert that guardrail allows all samples."""
        for sample in test_samples:
            result = guardrail.check(sample)
            assert not result.blocked, f"Expected to allow: '{sample}'"

    @staticmethod
    def assert_performance(guardrail, sample: str, max_time: float = 0.1):
        """Assert guardrail performance is within limits."""
        start = time.time()
        guardrail.check(sample)
        elapsed = time.time() - start
        assert elapsed < max_time, f"Check took {elapsed:.3f}s, max allowed: {max_time}s"

    @pytest.mark.ci
    @staticmethod
    def test_guardrail_consistency(guardrail, sample: str, iterations: int = 10):
        """Test that guardrail gives consistent results."""
        results = []
        for _ in range(iterations):
            result = guardrail.check(sample)
            results.append(result.blocked)

        # All results should be the same
        assert all(r == results[0] for r in results), "Inconsistent results"


class ConfigTestHelper:
    """Helper functions for configuration testing."""

    @staticmethod
    @contextmanager
    def temporary_config(config_dict: Dict[str, Any], format: str = "yaml"):
        """Create a temporary config file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=f".{format}", delete=False) as f:
            if format == "yaml":
                yaml.dump(config_dict, f)
            elif format == "json":
                json.dump(config_dict, f)
            else:
                raise ValueError(f"Unsupported format: {format}")

            temp_path = Path(f.name)

        try:
            yield temp_path
        finally:
            if temp_path.exists():
                temp_path.unlink()

    @staticmethod
    def create_invalid_configs() -> Dict[str, Dict[str, Any]]:
        """Create various invalid configurations for testing."""
        return {
            "missing_type": {"keywords": ["test"]},
            "invalid_type": {"type": "nonexistent_guardrail"},
            "missing_required": {
                "type": "keyword_list"
                # Missing required 'keywords'
            },
            "wrong_type": {"type": "length", "max_length": "not_a_number"},
            "negative_value": {"type": "length", "max_length": -100},
        }


class MockHelper:
    """Helper for creating mock objects and responses."""

    @staticmethod
    def mock_api_response(status_code: int = 200, json_data: Optional[Dict] = None):
        """Create a mock API response."""

        class MockResponse:
            def __init__(self, status_code, json_data):
                self.status_code = status_code
                self._json_data = json_data or {}

            def json(self):
                return self._json_data

            @property
            def text(self):
                return json.dumps(self._json_data)

            @property
            def ok(self):
                return 200 <= self.status_code < 300

        return MockResponse(status_code, json_data)

    @staticmethod
    @contextmanager
    def mock_environment_variable(key: str, value: str):
        """Temporarily set an environment variable."""
        original = os.environ.get(key)
        os.environ[key] = value

        try:
            yield
        finally:
            if original is not None:
                os.environ[key] = original
            else:
                os.environ.pop(key, None)


class AssertionHelper:
    """Enhanced assertion helpers."""

    @staticmethod
    def assert_dict_contains(actual: Dict, expected: Dict):
        """Assert actual dict contains all expected key-value pairs."""
        for key, value in expected.items():
            assert key in actual, f"Key '{key}' not found in {actual.keys()}"
            assert actual[key] == value, f"Expected {key}={value}, got {actual[key]}"

    @staticmethod
    def assert_lists_equal_unordered(list1: List, list2: List):
        """Assert two lists contain the same elements (order doesn't matter)."""
        assert len(list1) == len(list2), f"Different lengths: {len(list1)} vs {len(list2)}"
        assert set(list1) == set(list2), f"Different elements: {set(list1)} vs {set(list2)}"

    @staticmethod
    def assert_exception_message(exception, expected_message: str):
        """Assert exception contains expected message."""
        actual_message = str(exception.value) if hasattr(exception, "value") else str(exception)
        assert (
            expected_message in actual_message
        ), f"Expected '{expected_message}' in '{actual_message}'"

    @staticmethod
    def assert_performance(
        func: Callable,
        args: tuple = (),
        kwargs: dict = None,
        max_time: float = 1.0,
        iterations: int = 1,
    ):
        """Assert function performance is within limits."""
        kwargs = kwargs or {}
        times = []

        for _ in range(iterations):
            start = time.time()
            func(*args, **kwargs)
            elapsed = time.time() - start
            times.append(elapsed)

        avg_time = sum(times) / len(times)
        max_measured = max(times)

        assert max_measured < max_time, f"Max time {max_measured:.3f}s exceeds limit {max_time}s"
        return avg_time


class PipelineTestHelper:
    """Helper for testing guardrail pipelines."""

    @staticmethod
    def count_active_guardrails(pipeline) -> Dict[str, int]:
        """Count active guardrails in a pipeline."""
        input_count = sum(1 for g in pipeline.input_guardrails if g.enabled)
        output_count = sum(1 for g in pipeline.output_guardrails if g.enabled)

        return {"input": input_count, "output": output_count, "total": input_count + output_count}

    @pytest.mark.ci
    @staticmethod
    def test_pipeline_with_samples(pipeline, samples: Dict[str, List[str]]):
        """Test pipeline with categorized samples."""
        results = {"blocked": [], "allowed": [], "warnings": []}

        for category, messages in samples.items():
            for message in messages:
                result = pipeline.check_input(message)

                if result["blocked"]:
                    results["blocked"].append((category, message))
                elif result.get("warnings"):
                    results["warnings"].append((category, message))
                else:
                    results["allowed"].append((category, message))

        return results


# Decorators for common test patterns


def retry_on_failure(max_attempts: int = 3, delay: float = 0.5):
    """Decorator to retry flaky tests."""

    def decorator(test_func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return test_func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
            raise last_exception

        return wrapper

    return decorator


def requires_api_key(test_func):
    """Decorator to skip tests that require an API key."""

    def wrapper(*args, **kwargs):
        if not os.environ.get("OPENAI_API_KEY"):
            pytest.skip("Test requires OPENAI_API_KEY")
        return test_func(*args, **kwargs)

    return wrapper


def time_limit(seconds: float):
    """Decorator to enforce time limits on tests."""

    def decorator(test_func):
        def wrapper(*args, **kwargs):
            start = time.time()
            result = test_func(*args, **kwargs)
            elapsed = time.time() - start
            assert elapsed < seconds, f"Test took {elapsed:.2f}s, limit is {seconds}s"
            return result

        return wrapper

    return decorator
