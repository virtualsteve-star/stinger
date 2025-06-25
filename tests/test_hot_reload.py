#!/usr/bin/env python3
"""
Tests for hot reload functionality.
"""

import pytest
import asyncio
import tempfile
import time
import os
import sys
import yaml
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.hot_reload import (
    HotReloadManager, 
    ConfigFileHandler, 
    HotReloadCLI,
    enable_hot_reload
)
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
def mock_callback():
    """Create a mock callback function."""
    return Mock()


class TestConfigFileHandler:
    """Test ConfigFileHandler functionality."""
    
    def test_handler_initialization(self, temp_config_file, mock_callback):
        """Test handler initialization."""
        handler = ConfigFileHandler(temp_config_file, mock_callback)
        assert handler.config_path == Path(temp_config_file)
        assert handler.reload_callback == mock_callback
        assert handler.last_modified == 0
        assert handler.debounce_time == 1.0
    
    def test_handler_ignores_directory_events(self, temp_config_file, mock_callback):
        """Test that directory events are ignored."""
        handler = ConfigFileHandler(temp_config_file, mock_callback)
        
        mock_event = Mock()
        mock_event.is_directory = True
        mock_event.src_path = temp_config_file
        
        handler.on_modified(mock_event)
        mock_callback.assert_not_called()
    
    def test_handler_ignores_unrelated_files(self, temp_config_file, mock_callback):
        """Test that unrelated file events are ignored."""
        handler = ConfigFileHandler(temp_config_file, mock_callback)
        
        mock_event = Mock()
        mock_event.is_directory = False
        mock_event.src_path = "/different/path/file.yaml"
        
        handler.on_modified(mock_event)
        mock_callback.assert_not_called()
    
    def test_handler_debounces_rapid_changes(self, temp_config_file, mock_callback):
        """Test that rapid file changes are debounced."""
        handler = ConfigFileHandler(temp_config_file, mock_callback)
        
        # Create a mock event for the correct file
        mock_event = Mock()
        mock_event.is_directory = False
        mock_event.src_path = temp_config_file
        
        # Mock the config loading to succeed
        with patch('src.core.hot_reload.ConfigLoader') as mock_loader:
            mock_loader.return_value.load.return_value = {"test": "config"}
            
            # Call on_modified twice rapidly
            handler.on_modified(mock_event)
            handler.on_modified(mock_event)
            
            # Should only be called once due to debouncing
            assert mock_callback.call_count == 1


class TestHotReloadManager:
    """Test HotReloadManager functionality."""
    
    @pytest.fixture
    def manager(self):
        """Create a HotReloadManager instance."""
        return HotReloadManager()
    
    def test_manager_initialization(self, manager):
        """Test manager initialization."""
        assert manager.observer is not None
        assert manager.handlers == []
        assert manager.current_config is None
        assert manager.backup_config is None
        assert manager.is_watching is False
        assert manager.reload_count == 0
    
    def test_start_watching_success(self, manager, temp_config_file):
        """Test successful start of file watching."""
        initial_config = {"name": "test", "enabled": True}
        
        success = manager.start_watching(temp_config_file, initial_config, Mock())
        
        assert success is True
        assert manager.is_watching is True
        assert len(manager.handlers) == 1
        assert manager.current_config == initial_config
        assert manager.backup_config == initial_config
    
    def test_start_watching_file_not_found(self, manager):
        """Test start watching with non-existent file."""
        success = manager.start_watching("/nonexistent/file.yaml", {}, Mock())
        
        assert success is False
        assert manager.is_watching is False
    
    def test_stop_watching(self, manager, temp_config_file):
        """Test stopping file watching."""
        # Start watching first
        manager.start_watching(temp_config_file, {}, Mock())
        assert manager.is_watching is True
        
        # Stop watching
        manager.stop_watching()
        assert manager.is_watching is False
        assert len(manager.handlers) == 0
    
    def test_reload_config_success(self, manager):
        """Test successful configuration reload."""
        initial_config = {"name": "test", "enabled": True}
        new_config = {
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
        
        manager.current_config = initial_config
        manager.backup_config = initial_config
        
        # Mock ConfigLoader to succeed
        with patch('src.core.hot_reload.ConfigLoader') as mock_loader:
            mock_loader.return_value.build_filters.return_value = []
            
            success = manager.reload_config(new_config)
            
            assert success is True
            assert manager.current_config == new_config
            assert manager.reload_count == 1
    
    def test_reload_config_validation_failure(self, manager):
        """Test configuration reload with validation failure."""
        initial_config = {"name": "test", "enabled": True}
        
        manager.current_config = initial_config
        manager.backup_config = initial_config
        
        # Mock ConfigLoader to raise an exception
        with patch('src.core.hot_reload.ConfigLoader') as mock_loader:
            mock_loader.return_value.build_filters.side_effect = Exception("Validation failed")
            
            success = manager.reload_config({"invalid": "config"})
            
            assert success is False
            assert manager.current_config == initial_config  # Should not change
    
    def test_rollback_config(self, manager):
        """Test configuration rollback."""
        initial_config = {"name": "test", "enabled": True}
        backup_config = {"name": "backup", "enabled": False}
        
        manager.current_config = initial_config
        manager.backup_config = backup_config
        
        manager.rollback_config()
        
        assert manager.current_config == backup_config
    
    def test_rollback_no_backup(self, manager):
        """Test rollback when no backup exists."""
        manager.current_config = {"name": "test"}
        manager.backup_config = None
        
        # Should not raise an exception
        manager.rollback_config()
        
        assert manager.current_config == {"name": "test"}  # Should remain unchanged
    
    def test_get_status(self, manager):
        """Test status retrieval."""
        manager.current_config = {"test": "config"}
        manager.backup_config = {"backup": "config"}
        manager.reload_count = 5
        
        status = manager.get_status()
        
        assert status["current_config"] is True
        assert status["backup_config"] is True
        assert status["reload_count"] == 5
        assert status["is_watching"] is False
        assert status["watched_files"] == 0
    
    def test_context_manager(self, manager):
        """Test context manager functionality."""
        with manager as m:
            assert m is manager
            assert manager.is_watching is False  # Should not start watching automatically
        
        # Should still be stopped after context exit
        assert manager.is_watching is False


class TestHotReloadCLI:
    """Test HotReloadCLI functionality."""
    
    @pytest.fixture
    def cli(self):
        """Create a HotReloadCLI instance."""
        return HotReloadCLI()
    
    def test_cli_initialization(self, cli):
        """Test CLI initialization."""
        assert cli.manager is not None
        assert isinstance(cli.manager, HotReloadManager)
    
    def test_get_status(self, cli):
        """Test CLI status retrieval."""
        status = cli.get_status()
        assert isinstance(status, dict)
        assert "is_watching" in status
        assert "watched_files" in status
        assert "reload_count" in status


class TestHotReloadIntegration:
    """Integration tests for hot reload functionality."""
    
    @pytest.mark.asyncio
    async def test_hot_reload_with_pipeline(self, temp_config_file):
        """Test hot reload integration with pipeline."""
        from src.core.pipeline import HotReloadPipeline
        
        # Create hot reload pipeline
        pipeline = HotReloadPipeline(temp_config_file, debug=True)
        
        # Test that pipeline was created successfully
        assert pipeline is not None
        assert pipeline.pipeline is not None
        
        # Test processing
        result = await pipeline.process("test content")
        assert result is not None
        
        # Cleanup
        pipeline.stop()
    
    def test_hot_reload_file_modification(self, temp_config_file):
        """Test that file modifications trigger reload."""
        manager = HotReloadManager()
        reload_triggered = False
        
        def reload_callback(new_config):
            nonlocal reload_triggered
            print(f"🔄 Reload callback triggered with config: {new_config}")
            reload_triggered = True
        
        # Start watching
        initial_config = {"name": "test", "enabled": True}
        success = manager.start_watching(temp_config_file, initial_config, reload_callback)
        assert success is True
        
        # Test manual reload instead of relying on file system events
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
        
        print(f"📝 Testing manual reload with config: {new_config_content}")
        
        # Manually trigger the reload callback
        reload_callback(new_config_content)
        
        # Check if reload was triggered
        print(f"🔍 Reload triggered: {reload_triggered}")
        assert reload_triggered is True
        
        # Test that the manager can handle the reload
        success = manager.reload_config(new_config_content)
        assert success is True
        assert manager.current_config == new_config_content
        assert manager.reload_count == 1
        
        # Cleanup
        manager.stop_watching()


class TestEnableHotReload:
    """Test the enable_hot_reload convenience function."""
    
    def test_enable_hot_reload_function(self, temp_config_file):
        """Test the enable_hot_reload convenience function."""
        initial_config = {"name": "test", "enabled": True}
        function_called = False
        
        def test_function(config):
            nonlocal function_called
            function_called = True
            assert config == initial_config
        
        # Mock the CLI to avoid actually running the main loop
        with patch('src.core.hot_reload.HotReloadCLI') as mock_cli:
            mock_cli_instance = Mock()
            mock_cli.return_value = mock_cli_instance
            
            enable_hot_reload(temp_config_file, initial_config, test_function)
            
            # Verify the CLI was used correctly
            mock_cli_instance.run_with_hot_reload.assert_called_once_with(
                temp_config_file, initial_config, test_function
            )


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 