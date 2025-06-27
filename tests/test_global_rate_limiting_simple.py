"""
Simple test for Global Rate Limiting System
"""

import pytest
import time
from src.stinger.core.rate_limiter import RateLimitTracker, GlobalRateLimiter


def test_rate_limit_tracker_creation():
    """Test basic tracker creation."""
    tracker = RateLimitTracker("test_key")
    assert tracker.key == "test_key"
    assert tracker.requests == []


def test_rate_limit_tracker_add_request():
    """Test adding requests."""
    tracker = RateLimitTracker("test_key")
    tracker.add_request()
    assert len(tracker.requests) == 1


def test_global_rate_limiter_creation():
    """Test global rate limiter creation."""
    limiter = GlobalRateLimiter()
    assert limiter.backend == "memory"
    assert "requests_per_minute" in limiter.default_limits


def test_global_rate_limiter_check_limit():
    """Test rate limit checking."""
    limiter = GlobalRateLimiter()
    result = limiter.check_rate_limit("test_key")
    assert not result["exceeded"]
    assert result["key"] == "test_key" 