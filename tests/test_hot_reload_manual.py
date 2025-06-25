#!/usr/bin/env python3
"""
Manual tests for hot reload functionality.
These tests validate hot reload logic without relying on file system events,
which can be unreliable in test environments.
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


class TestHotReloadManual:
    """Manual tests for hot reload functionality."""
    
    def test_manual_reload_workflow(self, temp_config_file):
        """Test manual reload workflow without file system events."""
        manager = HotReloadManager()
        reload_count = 0
        
        def reload_callback(new_config):
            nonlocal reload_count
            reload_count += 1
            print(f"[Manual] Reload callback triggered #{reload_count}")
            success = manager.reload_config(new_config)
            print(f"[Manual] Reload success: {success}")
        
        # Start watching (but don't rely on file events)
        initial_config = {"name": "test", "enabled": True}
        success = manager.start_watching(temp_config_file, initial_config, reload_callback)
        assert success is True
        
        # Manually trigger reload with valid config
        valid_config = {
            "version": "1.0",
            "pipeline": {
                "input": [
                    {
                        "name": "manual_filter",
                        "type": "pass_through",
                        "enabled": True,
                        "on_error": "allow"
                    }
                ]
            }
        }
        
        print(f"[Manual] Testing valid config reload")
        reload_callback(valid_config)
        
        # Verify reload was successful
        assert reload_count == 1
        assert manager.current_config == valid_config
        assert manager.reload_count == 1
        
        # Test invalid config rollback
        invalid_config = {
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
        
        print(f"[Manual] Testing invalid config rollback")
        reload_callback(invalid_config)
        
        # Verify rollback occurred
        assert reload_count == 2
        assert manager.current_config == initial_config  # Should have rolled back to initial config
        assert manager.reload_count == 1  # Should not have incremented
        
        # Cleanup
        manager.stop_watching()
    
    def test_development_workflow_simulation(self, temp_config_file):
        """Simulate a real development workflow with manual reloads."""
        manager = HotReloadManager()
        reload_count = 0
        
        def reload_callback(new_config):
            nonlocal reload_count
            reload_count += 1
            print(f"[Dev] Reload #{reload_count}: {new_config['pipeline']['input'][0]['name']}")
            success = manager.reload_config(new_config)
            print(f"[Dev] Success: {success}")
        
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
        
        # Simulate development workflow: multiple valid changes
        development_steps = [
            {"name": "step1_filter", "type": "pass_through"},
            {"name": "step2_filter", "type": "pass_through"},
            {"name": "step3_filter", "type": "pass_through"},
        ]
        
        for i, step in enumerate(development_steps):
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
            
            print(f"[Dev] Applying step {i+1}: {step['name']}")
            reload_callback(config_content)
            
            # Verify the change was applied
            assert manager.current_config is not None
            assert manager.current_config["pipeline"]["input"][0]["name"] == step["name"]
        
        # Verify total reload count
        assert reload_count == len(development_steps), f"Expected {len(development_steps)} reloads, got {reload_count}"
        assert manager.reload_count == len(development_steps)
        
        # Cleanup
        manager.stop_watching()
    
    def test_error_handling_and_recovery(self, temp_config_file):
        """Test error handling and recovery scenarios."""
        manager = HotReloadManager()
        reload_count = 0
        
        def reload_callback(new_config):
            nonlocal reload_count
            reload_count += 1
            print(f"[Error] Reload #{reload_count}")
            success = manager.reload_config(new_config)
            print(f"[Error] Success: {success}")
        
        # Start with valid config
        initial_config = {
            "version": "1.0",
            "pipeline": {
                "input": [
                    {
                        "name": "valid_filter",
                        "type": "pass_through",
                        "enabled": True,
                        "on_error": "allow"
                    }
                ]
            }
        }
        success = manager.start_watching(temp_config_file, initial_config, reload_callback)
        assert success is True
        
        # Test sequence: valid -> invalid -> valid
        print(f"[Error] Step 1: Valid config")
        reload_callback(initial_config)
        assert manager.current_config == initial_config
        assert manager.reload_count == 1
        
        # Invalid config
        invalid_config = {
            "version": "1.0",
            "pipeline": {
                "input": [
                    {
                        "name": "invalid_filter",
                        "type": "nonexistent_filter_type",
                        "enabled": True,
                        "on_error": "allow"
                    }
                ]
            }
        }
        
        print(f"[Error] Step 2: Invalid config (should rollback)")
        reload_callback(invalid_config)
        assert manager.current_config == initial_config  # Should rollback
        assert manager.reload_count == 1  # Should not increment
        
        # Back to valid config
        new_valid_config = {
            "version": "1.0",
            "pipeline": {
                "input": [
                    {
                        "name": "recovered_filter",
                        "type": "pass_through",
                        "enabled": True,
                        "on_error": "allow"
                    }
                ]
            }
        }
        
        print(f"[Error] Step 3: Valid config (should work)")
        reload_callback(new_valid_config)
        assert manager.current_config == new_valid_config
        assert manager.reload_count == 2
        
        # Cleanup
        manager.stop_watching()
    
    def test_status_reporting_accuracy(self, temp_config_file):
        """Test that status reporting is accurate throughout the process."""
        manager = HotReloadManager()
        
        def reload_callback(new_config):
            manager.reload_config(new_config)
        
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
        
        reload_callback(new_config_content)
        
        # Check status after reload
        status = manager.get_status()
        assert status["reload_count"] == 1
        assert status["current_config"] is True
        assert status["backup_config"] is True
        
        # Cleanup
        manager.stop_watching()


class TestHotReloadCLI:
    """Test CLI functionality for hot reload."""
    
    def test_cli_status_reporting(self, temp_config_file):
        """Test CLI status reporting functionality."""
        from src.core.hot_reload import HotReloadCLI
        
        cli = HotReloadCLI()
        
        # Test initial status
        status = cli.get_status()
        assert isinstance(status, dict)
        assert "is_watching" in status
        assert "watched_files" in status
        assert "reload_count" in status
        assert "current_config" in status
        assert "backup_config" in status
        
        # All should be False/0 initially
        assert status["is_watching"] is False
        assert status["watched_files"] == 0
        assert status["reload_count"] == 0
        assert status["current_config"] is False
        assert status["backup_config"] is False


if __name__ == "__main__":
    # Run manual tests
    pytest.main([__file__, "-v", "-s"]) 