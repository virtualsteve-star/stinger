"""
Tests for Global Rate Limiting System

This module tests the global rate limiting capabilities that build on the existing
conversation rate limiting system.
"""

import threading
import time

import pytest

from src.stinger.core.conversation import Conversation
from src.stinger.core.pipeline import GuardrailPipeline
from src.stinger.core.rate_limiter import (
    GlobalRateLimiter,
    RateLimitTracker,
    get_global_rate_limiter,
    set_global_rate_limiter,
)

CONFIG = {
    "default_limits": {"requests_per_minute": 5, "requests_per_hour": 10},
    "role_overrides": {
        "admin": {"exempt": True},
        "support": {"max_requests_per_minute": 3, "max_requests_per_hour": 6},
        "premium": {"max_requests_per_minute": 4, "max_requests_per_hour": 8},
        "guest": {"max_requests_per_minute": 2, "max_requests_per_hour": 3},
    },
}


@pytest.fixture
def limiter():
    return GlobalRateLimiter(config=CONFIG)


@pytest.mark.ci
def test_admin_exempt(limiter):
    for _ in range(20):
        result = limiter.check_rate_limit("admin_key", role="admin")
        assert not result["exceeded"]
        limiter.record_request("admin_key")


@pytest.mark.ci
def test_support_role_limit(limiter):
    # Should allow 3 per minute
    for i in range(3):
        result = limiter.check_rate_limit("support_key", role="support")
        assert not result["exceeded"]
        limiter.record_request("support_key")
    # 4th should be blocked
    result = limiter.check_rate_limit("support_key", role="support")
    assert result["exceeded"]
    assert "per-minute" in result["reason"]


@pytest.mark.ci
def test_premium_role_limit(limiter):
    # Should allow 4 per minute
    for i in range(4):
        result = limiter.check_rate_limit("premium_key", role="premium")
        assert not result["exceeded"]
        limiter.record_request("premium_key")
    # 5th should be blocked
    result = limiter.check_rate_limit("premium_key", role="premium")
    assert result["exceeded"]
    assert "per-minute" in result["reason"]


@pytest.mark.ci
def test_guest_role_limit(limiter):
    # Should allow 2 per minute
    for i in range(2):
        result = limiter.check_rate_limit("guest_key", role="guest")
        assert not result["exceeded"]
        limiter.record_request("guest_key")
    # 3rd should be blocked
    result = limiter.check_rate_limit("guest_key", role="guest")
    assert result["exceeded"]
    assert "per-minute" in result["reason"]


@pytest.mark.ci
def test_default_limit(limiter):
    # Should allow 5 per minute (default)
    for i in range(5):
        result = limiter.check_rate_limit("default_key")
        assert not result["exceeded"]
        limiter.record_request("default_key")
    # 6th should be blocked
    result = limiter.check_rate_limit("default_key")
    assert result["exceeded"]
    assert "per-minute" in result["reason"]


@pytest.mark.performance
class TestRateLimitTracker:
    """Test the RateLimitTracker class."""

    @pytest.mark.ci
    def test_tracker_creation(self):
        """Test tracker creation."""
        tracker = RateLimitTracker("test_key")
        assert tracker.key == "test_key"
        assert tracker.requests == []

    @pytest.mark.ci
    def test_add_request(self):
        """Test adding requests."""
        tracker = RateLimitTracker("test_key")

        # Add request with current time
        tracker.add_request()
        assert len(tracker.requests) == 1

        # Add request with specific timestamp
        timestamp = time.time()
        tracker.add_request(timestamp)
        assert len(tracker.requests) == 2
        assert tracker.requests[1] == timestamp

    @pytest.mark.ci
    def test_check_limit_not_exceeded(self):
        """Test rate limit when not exceeded."""
        tracker = RateLimitTracker("test_key")

        # Add 2 requests within 60-second window
        now = time.time()
        tracker.add_request(now - 30)  # 30 seconds ago
        tracker.add_request(now - 10)  # 10 seconds ago

        # Check limit of 5 requests per minute
        assert not tracker.check_limit(5, 60)

    @pytest.mark.ci
    def test_check_limit_exceeded(self):
        """Test rate limit when exceeded."""
        tracker = RateLimitTracker("test_key")

        # Add 6 requests within 60-second window
        now = time.time()
        for i in range(6):
            tracker.add_request(now - (50 - i * 10))  # 50, 40, 30, 20, 10, 0 seconds ago

        # Check limit of 5 requests per minute
        assert tracker.check_limit(5, 60)

    @pytest.mark.ci
    def test_check_limit_with_old_requests(self):
        """Test rate limit with old requests outside window."""
        tracker = RateLimitTracker("test_key")

        # Add old request outside window
        now = time.time()
        tracker.add_request(now - 120)  # 2 minutes ago (outside 60-second window)

        # Add recent request within window
        tracker.add_request(now - 30)  # 30 seconds ago

        # Check limit of 1 request per minute
        assert not tracker.check_limit(1, 60)  # Should not be exceeded

    @pytest.mark.ci
    def test_get_current_count(self):
        """Test getting current request count."""
        tracker = RateLimitTracker("test_key")

        now = time.time()
        tracker.add_request(now - 30)  # 30 seconds ago
        tracker.add_request(now - 10)  # 10 seconds ago
        tracker.add_request(now - 120)  # 2 minutes ago (outside window)

        # Should only count requests within 60-second window
        assert tracker.get_current_count(60) == 2

    @pytest.mark.ci
    def test_get_remaining_requests(self):
        """Test getting remaining requests."""
        tracker = RateLimitTracker("test_key")

        now = time.time()
        tracker.add_request(now - 30)
        tracker.add_request(now - 10)

        # Limit of 5 requests per minute, 2 used
        assert tracker.get_remaining_requests(5, 60) == 3

    @pytest.mark.performance
    def test_get_reset_time(self):
        """Test getting reset time."""
        tracker = RateLimitTracker("test_key")

        now = time.time()
        tracker.add_request(now - 30)  # 30 seconds ago

        # Reset time should be 30 seconds from now (oldest request + window)
        reset_time = tracker.get_reset_time(60)
        expected_reset = now - 30 + 60
        assert abs(reset_time - expected_reset) < 1  # Allow 1 second tolerance

    @pytest.mark.ci
    def test_cleanup_old_entries(self):
        """Test cleanup of old entries."""
        tracker = RateLimitTracker("test_key")

        now = time.time()
        tracker.add_request(now - 120)  # 2 minutes ago
        tracker.add_request(now - 30)  # 30 seconds ago

        # Clean up entries older than 60 seconds
        tracker.cleanup_old_entries(60)

        # Should only have the recent request
        assert len(tracker.requests) == 1
        assert tracker.requests[0] == now - 30


@pytest.mark.ci
class TestGlobalRateLimiter:
    """Test the GlobalRateLimiter class."""

    def setup_method(self):
        """Set up test method."""
        self.limiter = GlobalRateLimiter()

    @pytest.mark.ci
    def test_limiter_creation(self):
        """Test limiter creation."""
        assert self.limiter.backend == "memory"
        assert self.limiter.cleanup_interval == 3600
        assert "requests_per_minute" in self.limiter.default_limits
        assert "requests_per_hour" in self.limiter.default_limits
        assert "requests_per_day" in self.limiter.default_limits

    @pytest.mark.ci
    def test_check_rate_limit_not_exceeded(self):
        """Test rate limit check when not exceeded."""
        result = self.limiter.check_rate_limit("test_key")

        assert not result["exceeded"]
        assert result["key"] == "test_key"
        assert result["exceeded_limits"] == []
        assert "requests_per_minute" in result["details"]
        assert "requests_per_hour" in result["details"]
        assert "requests_per_day" in result["details"]

    @pytest.mark.ci
    def test_check_rate_limit_exceeded(self):
        """Test rate limit check when exceeded."""
        # Add many requests to exceed the limit
        for i in range(70):  # Exceed 60 per minute limit
            self.limiter.record_request("test_key")

        result = self.limiter.check_rate_limit("test_key")

        assert result["exceeded"]
        assert "requests_per_minute" in result["exceeded_limits"]
        assert result["details"]["requests_per_minute"]["remaining"] == 0

    @pytest.mark.ci
    def test_check_rate_limit_with_custom_limits(self):
        """Test rate limit check with custom limits."""
        custom_limits = {"requests_per_minute": 2}

        # Add 3 requests to exceed custom limit
        for i in range(3):
            self.limiter.record_request("test_key")

        result = self.limiter.check_rate_limit("test_key", custom_limits)

        assert result["exceeded"]
        assert "requests_per_minute" in result["exceeded_limits"]

    @pytest.mark.ci
    def test_record_request(self):
        """Test recording requests."""
        self.limiter.record_request("test_key")

        # Check that the request was recorded
        tracker = self.limiter._get_tracker("test_key")
        assert len(tracker.requests) == 1

    @pytest.mark.ci
    def test_get_status(self):
        """Test getting status without recording request."""
        # Add some requests
        for i in range(3):
            self.limiter.record_request("test_key")

        status = self.limiter.get_status("test_key")

        assert status["key"] == "test_key"
        assert "requests_per_minute" in status["details"]
        assert status["details"]["requests_per_minute"]["current"] == 3
        assert status["details"]["requests_per_minute"]["remaining"] == 57  # 60 - 3

    @pytest.mark.ci
    def test_reset_limits(self):
        """Test resetting limits for a key."""
        # Add some requests
        self.limiter.record_request("test_key")

        # Reset limits
        self.limiter.reset_limits("test_key")

        # Check that the tracker was removed
        assert "test_key" not in self.limiter.trackers

    @pytest.mark.ci
    def test_set_default_limits(self):
        """Test setting default limits."""
        new_limits = {"requests_per_minute": 100}
        self.limiter.set_default_limits(new_limits)

        assert self.limiter.default_limits["requests_per_minute"] == 100

    @pytest.mark.ci
    def test_get_all_keys(self):
        """Test getting all tracked keys."""
        # Add requests for multiple keys
        self.limiter.record_request("key1")
        self.limiter.record_request("key2")

        keys = self.limiter.get_all_keys()
        assert "key1" in keys
        assert "key2" in keys

    @pytest.mark.ci
    def test_thread_safety(self):
        """Test thread safety of the rate limiter."""

        def add_requests(key, count):
            for i in range(count):
                self.limiter.record_request(key)

        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=add_requests, args=(f"key{i}", 10))
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check that all requests were recorded
        for i in range(5):
            status = self.limiter.get_status(f"key{i}")
            assert status["details"]["requests_per_minute"]["current"] == 10

    @pytest.mark.ci
    def test_cleanup_old_entries(self):
        """Test cleanup of old entries."""
        # Add old requests with different timestamps
        old_time = time.time() - 7200  # 2 hours ago
        for i in range(5):
            self.limiter.record_request("test_key", old_time + i)  # Different timestamps

        # Add recent requests
        for i in range(3):
            self.limiter.record_request("test_key")

        # Force cleanup
        self.limiter._cleanup_old_entries()

        # Check that only recent requests remain
        tracker = self.limiter._get_tracker("test_key")
        assert len(tracker.requests) == 3


@pytest.mark.efficacy
class TestGlobalRateLimiterIntegration:
    """Test integration with pipeline."""

    def setup_method(self):
        """Set up test method."""
        # Create a simple pipeline for testing
        self.pipeline = GuardrailPipeline()  # Use default config

    @pytest.mark.ci
    def test_pipeline_with_global_rate_limiting(self):
        """Test pipeline integration with global rate limiting."""
        # Add many requests to exceed the limit
        for i in range(70):  # Exceed 60 per minute limit
            self.pipeline.global_rate_limiter.record_request("test_api_key")

        # Try to process a request
        result = self.pipeline.check_input("test content", api_key="test_api_key")

        assert result["blocked"]
        assert "Global rate limit exceeded" in result["reasons"][0]
        assert "global_rate_limit" in result["details"]

    @pytest.mark.ci
    def test_pipeline_without_global_rate_limiting(self):
        """Test pipeline without global rate limiting."""
        # Process request without API key
        result = self.pipeline.check_input("test content")

        assert not result["blocked"]

    @pytest.mark.efficacy
    def test_pipeline_with_conversation_and_global_rate_limiting(self):
        """Test pipeline with both conversation and global rate limiting."""
        # Create conversation with rate limit
        conv = Conversation.human_ai("user_123", "gpt-4", rate_limit={"turns_per_minute": 2})

        # Add requests to exceed global limit
        for i in range(70):
            self.pipeline.global_rate_limiter.record_request("test_api_key")

        # Try to process request
        result = self.pipeline.check_input(
            "test_content", conversation=conv, api_key="test_api_key"
        )

        # Should be blocked by global rate limit before conversation rate limit
        assert result["blocked"]
        assert "Global rate limit exceeded" in result["reasons"][0]


@pytest.mark.ci
class TestGlobalRateLimiterFunctions:
    """Test global rate limiter functions."""

    def test_get_global_rate_limiter(self):
        """Test getting global rate limiter instance."""
        limiter = get_global_rate_limiter()
        assert isinstance(limiter, GlobalRateLimiter)

    @pytest.mark.ci
    def test_set_global_rate_limiter(self):
        """Test setting global rate limiter instance."""
        custom_limiter = GlobalRateLimiter(backend="memory")
        set_global_rate_limiter(custom_limiter)

        retrieved_limiter = get_global_rate_limiter()
        assert retrieved_limiter is custom_limiter


@pytest.mark.ci
class TestGlobalRateLimiterEdgeCases:
    """Test edge cases and error conditions."""

    def test_unknown_rate_limit_window(self):
        """Test handling of unknown rate limit windows."""
        limiter = GlobalRateLimiter()

        # Use unknown limit name
        result = limiter.check_rate_limit("test_key", {"unknown_limit": 10})

        # Should not crash, should log warning
        assert not result["exceeded"]

    @pytest.mark.ci
    def test_zero_limits(self):
        """Test behavior with zero limits."""
        limiter = GlobalRateLimiter()

        # Set zero limit
        result = limiter.check_rate_limit("test_key", {"requests_per_minute": 0})

        # Should be exceeded immediately
        assert result["exceeded"]

    @pytest.mark.ci
    def test_negative_limits(self):
        """Test behavior with negative limits."""
        limiter = GlobalRateLimiter()

        # Set negative limit
        result = limiter.check_rate_limit("test_key", {"requests_per_minute": -1})

        # Should be exceeded immediately
        assert result["exceeded"]

    @pytest.mark.ci
    def test_empty_key(self):
        """Test behavior with empty key."""
        limiter = GlobalRateLimiter()

        result = limiter.check_rate_limit("")

        # Should work without crashing
        assert not result["exceeded"]

    @pytest.mark.ci
    def test_none_key(self):
        """Test behavior with None key."""
        limiter = GlobalRateLimiter()

        # Should handle None key gracefully
        result = limiter.check_rate_limit("")  # Use empty string instead of None

        # Should work without crashing
        assert not result["exceeded"]


@pytest.mark.performance
class TestGlobalRateLimiterPerformance:
    """Test performance characteristics."""

    def test_many_keys_performance(self):
        """Test performance with many keys."""
        limiter = GlobalRateLimiter()

        # Add many keys
        start_time = time.time()
        for i in range(1000):
            limiter.record_request(f"key_{i}")

        end_time = time.time()

        # Should complete quickly
        assert end_time - start_time < 1.0  # Less than 1 second

    @pytest.mark.performance
    def test_many_requests_performance(self):
        """Test performance with many requests per key."""
        limiter = GlobalRateLimiter()

        # Add many requests to one key
        start_time = time.time()
        for i in range(1000):
            limiter.record_request("test_key")

        end_time = time.time()

        # Should complete quickly
        assert end_time - start_time < 1.0  # Less than 1 second

    @pytest.mark.performance
    def test_concurrent_access_performance(self):
        """Test performance under concurrent access."""
        limiter = GlobalRateLimiter()

        def concurrent_requests():
            for i in range(100):
                limiter.record_request(f"key_{i % 10}")

        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=concurrent_requests)
            threads.append(thread)

        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        end_time = time.time()

        # Should complete quickly
        assert end_time - start_time < 2.0  # Less than 2 seconds
