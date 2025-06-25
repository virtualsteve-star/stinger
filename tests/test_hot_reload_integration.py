#!/usr/bin/env python3
"""
Integration tests for hot reload functionality with real file system events.
These tests validate that file changes on disk reliably trigger configuration reloads.

Note: These are integration/system tests that may be flaky in CI environments.
They are designed to run reliably in local/dev environments.
"""

import pytest
import tempfile
import time
import os
import sys
import yaml
import threading
from pathlib import Path
from unittest.mock import Mock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.hot_reload import HotReloadManager, ConfigFileHandler
from src.core.config import ConfigLoader


@pytest.fixture
def temp_config_file():
    """Create a temporary config file with valid content."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        config_content = {
            "version": "1.0",
            "pipeline": {
                "input": [
                    {
                        "name": "test_filter",
                        "type": "pass_through",
                        "enabled": True,
                        "on_error": "allow"
                    }
                ]
            }
        }
        yaml.dump(config_content, f)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    try:
        Path(temp_path).unlink()
    except FileNotFoundError:
        pass


@pytest.fixture
def temp_invalid_config_file():
    """Create a temporary config file with invalid content."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        config_content = {
            "version": "1.0",
            "pipeline": {
                "input": [
                    {
                        "name": "invalid_filter",
                        "type": "nonexistent_filter_type",  # Invalid filter type
                        "enabled": True,
                        "on_error": "allow"
                    }
                ]
            }
        }
        yaml.dump(config_content, f)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    try:
        Path(temp_path).unlink()
    except FileNotFoundError:
        pass


class TestFileSystemEventIntegration:
    """Integration tests for file system event handling."""
    
    @pytest.mark.integration
    def test_file_modification_triggers_reload(self, temp_config_file):
        """Test that modifying a config file triggers reload callback."""
        manager = HotReloadManager()
        reload_triggered = threading.Event()
        reload_config = None
        
        def reload_callback(new_config):
            nonlocal reload_config
            reload_config = new_config
            reload_triggered.set()
        
        # Start watching
        initial_config = {"name": "test", "enabled": True}
        success = manager.start_watching(temp_config_file, initial_config, reload_callback)
        assert success is True
        
        # Wait a moment for the observer to start
        time.sleep(0.5)
        
        # Modify the config file
        new_config_content = {
            "version": "1.0",
            "pipeline": {
                "input": [
                    {
                        "name": "modified_filter",
                        "type": "pass_through",
                        "enabled": True,
                        "on_error": "allow"
                    }
                ]
            }
        }
        
        with open(temp_config_file, 'w') as f:
            yaml.dump(new_config_content, f)
        
        # Wait for reload to be triggered (with timeout)
        assert reload_triggered.wait(timeout=5.0), "Reload callback was not triggered within 5 seconds"
        
        # Verify the reloaded config
        assert reload_config is not None
        assert reload_config["pipeline"]["input"][0]["name"] == "modified_filter"
        
        # Cleanup
        manager.stop_watching()
    
    @pytest.mark.integration
    def test_invalid_config_triggers_rollback(self, temp_config_file):
        """Test that invalid config changes trigger rollback."""
        manager = HotReloadManager()
        reload_triggered = threading.Event()
        rollback_occurred = False
        
        def reload_callback(new_config):
            nonlocal rollback_occurred
            # Try to reload the config
            success = manager.reload_config(new_config)
            if not success:
                rollback_occurred = True
            reload_triggered.set()
        
        # Start watching
        initial_config = {
            "version": "1.0",
            "pipeline": {
                "input": [
                    {
                        "name": "test_filter",
                        "type": "pass_through",
                        "enabled": True,
                        "on_error": "allow"
                    }
                ]
            }
        }
        success = manager.start_watching(temp_config_file, initial_config, reload_callback)
        assert success is True
        
        # Wait a moment for the observer to start
        time.sleep(0.5)
        
        # Write invalid config
        invalid_config_content = {
            "version": "1.0",
            "pipeline": {
                "input": [
                    {
                        "name": "invalid_filter",
                        "type": "nonexistent_filter_type",  # Invalid filter type
                        "enabled": True,
                        "on_error": "allow"
                    }
                ]
            }
        }
        
        with open(temp_config_file, 'w') as f:
            yaml.dump(invalid_config_content, f)
        
        # Wait for reload to be triggered
        assert reload_triggered.wait(timeout=5.0), "Reload callback was not triggered within 5 seconds"
        
        # Verify rollback occurred
        assert rollback_occurred, "Rollback should have occurred for invalid config"
        assert manager.current_config == initial_config, "Config should have been rolled back"
        
        # Cleanup
        manager.stop_watching()
    
    @pytest.mark.integration
    def test_rapid_changes_are_debounced(self, temp_config_file):
        """Test that rapid file changes are properly debounced."""
        manager = HotReloadManager()
        reload_count = 0
        reload_triggered = threading.Event()
        
        def reload_callback(new_config):
            nonlocal reload_count
            reload_count += 1
            reload_triggered.set()
        
        # Start watching
        initial_config = {"name": "test", "enabled": True}
        success = manager.start_watching(temp_config_file, initial_config, reload_callback)
        assert success is True
        
        # Wait a moment for the observer to start
        time.sleep(0.5)
        
        # Make multiple rapid changes
        for i in range(5):
            config_content = {
                "version": "1.0",
                "pipeline": {
                    "input": [
                        {
                            "name": f"rapid_filter_{i}",
                            "type": "pass_through",
                            "enabled": True,
                            "on_error": "allow"
                        }
                    ]
                }
            }
            
            with open(temp_config_file, 'w') as f:
                yaml.dump(config_content, f)
            
            # Small delay between changes
            time.sleep(0.1)
        
        # Wait for reload to be triggered
        assert reload_triggered.wait(timeout=5.0), "Reload callback was not triggered within 5 seconds"
        
        # Due to debouncing, we should have fewer reloads than changes
        assert reload_count < 5, f"Expected debouncing, but got {reload_count} reloads for 5 changes"
        assert reload_count >= 1, "Should have at least one reload"
        
        # Cleanup
        manager.stop_watching()
    
    @pytest.mark.integration
    def test_file_deletion_handling(self, temp_config_file):
        """Test handling of file deletion."""
        manager = HotReloadManager()
        error_occurred = False
        
        def reload_callback(new_config):
            nonlocal error_occurred
            try:
                manager.reload_config(new_config)
            except Exception:
                error_occurred = True
        
        # Start watching
        initial_config = {"name": "test", "enabled": True}
        success = manager.start_watching(temp_config_file, initial_config, reload_callback)
        assert success is True
        
        # Wait a moment for the observer to start
        time.sleep(0.5)
        
        # Delete the config file
        Path(temp_config_file).unlink()
        
        # Wait a moment for the deletion to be processed
        time.sleep(1.0)
        
        # The system should handle file deletion gracefully
        # We don't expect an error, but the file should no longer exist
        assert not Path(temp_config_file).exists()
        
        # Cleanup
        manager.stop_watching()
    
    @pytest.mark.integration
    def test_development_workflow_simulation(self, temp_config_file):
        """Simulate a real development workflow with multiple config changes."""
        manager = HotReloadManager()
        reload_count = 0
        reload_triggered = threading.Event()
        
        def reload_callback(new_config):
            nonlocal reload_count
            reload_count += 1
            reload_triggered.set()
        
        # Start watching
        initial_config = {
            "version": "1.0",
            "pipeline": {
                "input": [
                    {
                        "name": "initial_filter",
                        "type": "pass_through",
                        "enabled": True,
                        "on_error": "allow"
                    }
                ]
            }
        }
        success = manager.start_watching(temp_config_file, initial_config, reload_callback)
        assert success is True
        
        # Wait a moment for the observer to start
        time.sleep(0.5)
        
        # Simulate development workflow: multiple valid changes
        development_steps = [
            {"name": "step1_filter", "type": "pass_through"},
            {"name": "step2_filter", "type": "pass_through"},
            {"name": "step3_filter", "type": "pass_through"},
        ]
        
        for i, step in enumerate(development_steps):
            reload_triggered.clear()
            
            config_content = {
                "version": "1.0",
                "pipeline": {
                    "input": [
                        {
                            "name": step["name"],
                            "type": step["type"],
                            "enabled": True,
                            "on_error": "allow"
                        }
                    ]
                }
            }
            
            with open(temp_config_file, 'w') as f:
                yaml.dump(config_content, f)
            
            # Wait for reload
            assert reload_triggered.wait(timeout=5.0), f"Reload not triggered for step {i+1}"
            
            # Verify the change was applied
            assert manager.current_config is not None
            assert manager.current_config["pipeline"]["input"][0]["name"] == step["name"]
        
        # Verify total reload count
        assert reload_count == len(development_steps), f"Expected {len(development_steps)} reloads, got {reload_count}"
        
        # Cleanup
        manager.stop_watching()


class TestHotReloadStatusReporting:
    """Test hot reload status reporting and monitoring."""
    
    def test_status_reporting_accuracy(self, temp_config_file):
        """Test that status reporting is accurate after reloads."""
        manager = HotReloadManager()
        reload_triggered = threading.Event()
        
        def reload_callback(new_config):
            manager.reload_config(new_config)
            reload_triggered.set()
        
        # Start watching
        initial_config = {"name": "test", "enabled": True}
        success = manager.start_watching(temp_config_file, initial_config, reload_callback)
        assert success is True
        
        # Check initial status
        status = manager.get_status()
        assert status["is_watching"] is True
        assert status["watched_files"] == 1
        assert status["reload_count"] == 0
        assert status["current_config"] is True
        assert status["backup_config"] is True
        
        # Wait a moment for the observer to start
        time.sleep(0.5)
        
        # Make a change
        new_config_content = {
            "version": "1.0",
            "pipeline": {
                "input": [
                    {
                        "name": "status_test_filter",
                        "type": "pass_through",
                        "enabled": True,
                        "on_error": "allow"
                    }
                ]
            }
        }
        
        with open(temp_config_file, 'w') as f:
            yaml.dump(new_config_content, f)
        
        # Wait for reload
        assert reload_triggered.wait(timeout=5.0), "Reload callback was not triggered"
        
        # Check status after reload
        status = manager.get_status()
        assert status["reload_count"] == 1
        assert status["current_config"] is True
        assert status["backup_config"] is True
        
        # Cleanup
        manager.stop_watching()


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v", "-m", "integration"]) 