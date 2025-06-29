"""
Tests for async buffering functionality in the security audit trail system.

Tests the performance improvements and async processing capabilities.
"""

import pytest
import tempfile
import json
import os
import sys
import time
import threading
from pathlib import Path
from unittest.mock import patch

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import stinger
from stinger.core import audit
from stinger.core.conversation import Conversation


class TestAsyncBuffering:
    """Test async buffering functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        # Disable audit trail before each test
        if audit.is_enabled():
            try:
                audit.disable()
            except RuntimeError:
                # Can't disable in production - reset the global instance
                audit._audit_trail = audit.AuditTrail()
    
    def test_async_buffering_setup(self):
        """Test that async buffering is properly initialized."""
        with tempfile.TemporaryDirectory() as temp_dir:
            audit_file = os.path.join(temp_dir, "async_test.log")
            
            # Enable with custom buffer settings
            audit.enable(audit_file, buffer_size=500, flush_interval=2.0)
            
            # Check that async components are setup
            trail = audit._audit_trail
            assert trail._log_queue is not None
            assert trail._writer_thread is not None
            assert trail._writer_thread.is_alive()
            assert trail._shutdown_event is not None
            assert trail._buffer_size == 500
            assert trail._flush_interval == 2.0
            
            audit.disable()
            
            # Check that async components are cleaned up
            assert trail._log_queue is None
            assert trail._writer_thread is None or not trail._writer_thread.is_alive()
            assert trail._shutdown_event is None
    
    def test_async_buffering_performance(self):
        """Test that async buffering improves performance under load."""
        with tempfile.TemporaryDirectory() as temp_dir:
            audit_file = os.path.join(temp_dir, "performance_test.log")
            
            # Enable audit trail with async buffering
            audit.enable(audit_file, buffer_size=1000, flush_interval=1.0)
            
            # Measure performance of many audit events
            start_time = time.time()
            
            # Generate many audit events quickly
            for i in range(100):
                audit.log_prompt(
                    f"Test prompt {i}",
                    user_id=f"user_{i}",
                    conversation_id=f"conv_{i}",
                    request_id=f"req_{i}"
                )
                
                audit.log_guardrail_decision(
                    "test_filter",
                    "allow",
                    f"Test reason {i}",
                    user_id=f"user_{i}",
                    conversation_id=f"conv_{i}",
                    request_id=f"req_{i}"
                )
                
                audit.log_response(
                    f"Test response {i}",
                    user_id=f"user_{i}",
                    conversation_id=f"conv_{i}",
                    request_id=f"req_{i}"
                )
            
            # Should complete very quickly due to async buffering
            end_time = time.time()
            async_time = end_time - start_time
            
            # Should be very fast since events are queued, not written synchronously
            assert async_time < 1.0, f"Async buffering should be fast but took {async_time}s"
            
            # Give background thread time to process
            time.sleep(2.0)
            
            audit.disable()
            
            # Verify all events were written
            with open(audit_file, 'r') as f:
                lines = f.readlines()
            
            # Should have enable event + 300 audit events (100 * 3 types)
            assert len(lines) >= 300, f"Expected at least 300 events, got {len(lines)}"
            
            # Verify events are properly formatted
            records = [json.loads(line) for line in lines if line.strip()]
            prompt_events = [r for r in records if r["event_type"] == "user_prompt"]
            decision_events = [r for r in records if r["event_type"] == "guardrail_decision"]
            response_events = [r for r in records if r["event_type"] == "llm_response"]
            
            assert len(prompt_events) == 100
            assert len(decision_events) == 100  
            assert len(response_events) == 100
    
    def test_async_buffering_stats(self):
        """Test async buffering statistics tracking."""
        with tempfile.TemporaryDirectory() as temp_dir:
            audit_file = os.path.join(temp_dir, "stats_test.log")
            
            # Enable audit trail
            audit.enable(audit_file, buffer_size=100, flush_interval=0.5)
            
            # Log some events
            for i in range(10):
                audit.log_prompt(f"Test prompt {i}", user_id=f"user_{i}")
            
            # Check stats
            stats = audit.get_stats()
            assert "queued" in stats
            assert "written" in stats
            assert "dropped" in stats
            assert "queue_size" in stats
            
            # Should have queued events
            assert stats["queued"] >= 10
            
            # Give time for background processing
            time.sleep(1.0)
            
            # Check stats after processing
            final_stats = audit.get_stats()
            assert final_stats["written"] > 0
            
            audit.disable()
    
    def test_queue_full_fallback(self):
        """Test fallback to synchronous write when queue is full."""
        with tempfile.TemporaryDirectory() as temp_dir:
            audit_file = os.path.join(temp_dir, "fallback_test.log")
            
            # Enable with very small buffer to trigger fallback
            audit.enable(audit_file, buffer_size=5, flush_interval=10.0)  # Long flush interval
            
            # Fill the queue beyond capacity
            for i in range(20):  # More than buffer size
                audit.log_prompt(f"Test prompt {i}", user_id=f"user_{i}")
            
            # Should have used fallback for some events
            stats = audit.get_stats()
            assert stats["queued"] > 0
            
            audit.disable()
            
            # Verify events were still written (via fallback)
            with open(audit_file, 'r') as f:
                lines = f.readlines()
            
            # Should have events from both queue and fallback
            assert len(lines) >= 15  # Some events should be written
    
    def test_background_thread_batching(self):
        """Test that background thread properly batches writes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            audit_file = os.path.join(temp_dir, "batching_test.log")
            
            # Enable with specific batching settings
            audit.enable(audit_file, buffer_size=1000, flush_interval=0.2)
            
            # Log events rapidly
            for i in range(25):  # Just under typical batch size of 50
                audit.log_prompt(f"Rapid prompt {i}", user_id=f"user_{i}")
            
            # Wait for flush interval to trigger batch write
            time.sleep(0.5)
            
            # Add more events to trigger size-based batching
            for i in range(30):  # Should trigger batch size limit
                audit.log_prompt(f"Batch prompt {i}", user_id=f"batch_user_{i}")
            
            # Give time for background processing
            time.sleep(0.5)
            
            audit.disable()
            
            # Verify events were written in batches
            with open(audit_file, 'r') as f:
                lines = f.readlines()
            
            # Should have most/all events written
            assert len(lines) >= 50
    
    def test_graceful_shutdown(self):
        """Test graceful shutdown of async buffering."""
        with tempfile.TemporaryDirectory() as temp_dir:
            audit_file = os.path.join(temp_dir, "shutdown_test.log")
            
            # Enable audit trail
            audit.enable(audit_file, buffer_size=100, flush_interval=5.0)
            
            # Add events to queue
            for i in range(10):
                audit.log_prompt(f"Shutdown test {i}", user_id=f"user_{i}")
            
            # Disable should flush remaining events
            audit.disable()
            
            # Verify events were flushed during shutdown
            with open(audit_file, 'r') as f:
                lines = f.readlines()
            
            # Should have enable event + 10 prompt events
            assert len(lines) >= 11  # enable + 10 prompts
            
            # Verify all prompt events are present
            records = [json.loads(line) for line in lines if line.strip()]
            prompt_events = [r for r in records if r["event_type"] == "user_prompt"]
            assert len(prompt_events) == 10
    
    def test_async_buffering_error_handling(self):
        """Test error handling in async buffering."""
        with tempfile.TemporaryDirectory() as temp_dir:
            audit_file = os.path.join(temp_dir, "error_test.log")
            
            # Enable audit trail
            audit.enable(audit_file)
            
            # Simulate file system error by removing file permissions
            # This tests the error handling in background writer
            trail = audit._audit_trail
            
            # Log an event normally first
            audit.log_prompt("Normal event", user_id="user1")
            
            # Give time for processing
            time.sleep(0.5)
            
            # Simulate error by making file unwritable
            os.chmod(audit_file, 0o000)
            
            try:
                # Log more events - should handle errors gracefully
                for i in range(5):
                    audit.log_prompt(f"Error test {i}", user_id=f"user_{i}")
                
                # Give time for error handling
                time.sleep(0.5)
                
                # Should still be enabled and not crash
                assert audit.is_enabled()
                
                # Check stats for dropped events due to errors
                stats = audit.get_stats()
                # Some events may be dropped due to write failures
                
            finally:
                # Restore permissions for cleanup
                os.chmod(audit_file, 0o644)
                audit.disable()
    
    def test_concurrent_logging(self):
        """Test concurrent logging from multiple threads."""
        with tempfile.TemporaryDirectory() as temp_dir:
            audit_file = os.path.join(temp_dir, "concurrent_test.log")
            
            # Enable audit trail
            audit.enable(audit_file, buffer_size=1000)
            
            # Function to log events from multiple threads
            def log_worker(worker_id, count):
                for i in range(count):
                    audit.log_prompt(
                        f"Worker {worker_id} prompt {i}",
                        user_id=f"worker_{worker_id}",
                        conversation_id=f"conv_{worker_id}_{i}"
                    )
            
            # Start multiple threads logging concurrently
            threads = []
            for worker_id in range(5):
                thread = threading.Thread(target=log_worker, args=(worker_id, 10))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # Give time for async processing
            time.sleep(1.0)
            
            audit.disable()
            
            # Verify all events were logged
            with open(audit_file, 'r') as f:
                lines = f.readlines()
            
            # Should have enable event + 50 prompt events (5 workers * 10 events)
            assert len(lines) >= 50
            
            # Parse and verify events
            records = [json.loads(line) for line in lines if line.strip()]
            prompt_events = [r for r in records if r["event_type"] == "user_prompt"]
            
            # Should have exactly 50 prompt events
            assert len(prompt_events) == 50
            
            # Verify events from all workers
            worker_events = {}
            for event in prompt_events:
                user_id = event["user_id"]
                worker_id = user_id.split("_")[1]
                worker_events[worker_id] = worker_events.get(worker_id, 0) + 1
            
            # Each worker should have 10 events
            assert len(worker_events) == 5
            for count in worker_events.values():
                assert count == 10


if __name__ == "__main__":
    pytest.main([__file__])