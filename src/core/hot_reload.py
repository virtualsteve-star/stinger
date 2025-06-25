"""
Hot reload functionality for Stinger configuration files.
Watches for changes and automatically reloads configurations with validation.
"""

import os
import time
import threading
import yaml
from pathlib import Path
from typing import Dict, Any, Callable, Optional, List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.core.config import ConfigLoader
from src.utils.exceptions import FilterError


class ConfigFileHandler(FileSystemEventHandler):
    """Handles file system events for configuration files."""
    
    def __init__(self, config_path: str, reload_callback: Callable[[Dict[str, Any]], None]):
        self.config_path = Path(config_path)
        self.reload_callback = reload_callback
        self.last_modified = 0
        self.debounce_time = 1.0  # Debounce reloads by 1 second
        
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
            
        if Path(str(event.src_path)) != self.config_path:
            return
            
        print(f"[HotReload] File event detected: {event.src_path}")
        
        # Debounce rapid file changes
        current_time = time.time()
        if current_time - self.last_modified < self.debounce_time:
            print(f"[HotReload] Debouncing rapid change (last: {self.last_modified}, current: {current_time})")
            return
            
        self.last_modified = current_time
        print(f"🔄 Configuration file changed: {self.config_path}")
        
        try:
            # Load and validate the new configuration
            config_loader = ConfigLoader()
            new_config = config_loader.load(str(self.config_path))
            
            # Call the reload callback with the new config
            self.reload_callback(new_config)
            print(f"✅ Configuration reloaded successfully")
            
        except Exception as e:
            print(f"❌ Failed to reload configuration: {e}")
            print(f"   Keeping previous configuration active")


class HotReloadManager:
    """Manages hot reload functionality for configuration files."""
    
    def __init__(self):
        self.observer = Observer()
        self.handlers: List[ConfigFileHandler] = []
        self.current_config: Optional[Dict[str, Any]] = None
        self.backup_config: Optional[Dict[str, Any]] = None
        self.is_watching = False
        self.reload_count = 0
        self._watched_directories = set()  # Track watched directories
        
    def start_watching(self, config_path: str, initial_config: Dict[str, Any], 
                      reload_callback: Callable[[Dict[str, Any]], None]) -> bool:
        """Start watching a configuration file for changes."""
        try:
            config_path_obj = Path(config_path)
            if not config_path_obj.exists():
                print(f"❌ Configuration file not found: {config_path}")
                return False
                
            # Store initial configuration
            self.current_config = initial_config.copy()
            self.backup_config = initial_config.copy()
            
            # Create file handler
            handler = ConfigFileHandler(config_path, reload_callback)
            self.handlers.append(handler)
            
            # Get the directory to watch
            watch_directory = str(config_path_obj.parent)
            
            # Only schedule the directory if we haven't watched it before
            if watch_directory not in self._watched_directories:
                self.observer.schedule(handler, watch_directory, recursive=False)
                self._watched_directories.add(watch_directory)
                print(f"[HotReload] Scheduled watch for directory: {watch_directory}")
            
            if not self.is_watching:
                self.observer.start()
                self.is_watching = True
                # Give the observer a moment to start up
                time.sleep(0.1)
                
            print(f"👀 Hot reload enabled for: {config_path}")
            print(f"   Changes will be automatically detected and reloaded")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start hot reload: {e}")
            return False
    
    def stop_watching(self):
        """Stop watching all configuration files."""
        if self.is_watching:
            self.observer.stop()
            self.observer.join()
            self.is_watching = False
            self.handlers.clear()
            print("🛑 Hot reload stopped")
    
    def reload_config(self, new_config: Dict[str, Any]) -> bool:
        """Reload configuration with validation and rollback."""
        try:
            # Validate the new configuration by trying to build filters
            config_loader = ConfigLoader()
            config_loader.build_filters(new_config)
            
            # Backup current config before applying new one
            if self.current_config:
                self.backup_config = self.current_config.copy()
            
            # Apply new configuration
            self.current_config = new_config.copy()
            self.reload_count += 1
            
            print(f"✅ Configuration reloaded (reload #{self.reload_count})")
            return True
            
        except Exception as e:
            print(f"❌ Configuration validation failed: {e}")
            self.rollback_config()
            return False
    
    def rollback_config(self):
        """Rollback to the previous working configuration."""
        if self.backup_config:
            self.current_config = self.backup_config.copy()
            print(f"🔄 Rolled back to previous configuration")
        else:
            print(f"⚠️  No backup configuration available for rollback")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current hot reload status."""
        return {
            "is_watching": self.is_watching,
            "watched_files": len(self.handlers),
            "reload_count": self.reload_count,
            "current_config": self.current_config is not None,
            "backup_config": self.backup_config is not None
        }
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_watching()


class HotReloadCLI:
    """CLI interface for hot reload functionality."""
    
    def __init__(self):
        self.manager = HotReloadManager()
    
    def run_with_hot_reload(self, config_path: str, initial_config: Dict[str, Any], 
                           main_function: Callable[[Dict[str, Any]], None]):
        """Run the main application with hot reload enabled."""
        print("🚀 Starting Stinger with hot reload enabled...")
        
        # Start watching the configuration file
        def reload_callback(new_config: Dict[str, Any]) -> None:
            self.manager.reload_config(new_config)
        
        if not self.manager.start_watching(config_path, initial_config, reload_callback):
            print("❌ Failed to start hot reload, running without hot reload")
            main_function(initial_config)
            return
        
        try:
            # Run the main function with the initial config
            main_function(initial_config)
            
            # Keep the application running to watch for changes
            print("👀 Watching for configuration changes...")
            print("   Press Ctrl+C to stop")
            
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping hot reload...")
        finally:
            self.manager.stop_watching()
    
    def get_status(self) -> Dict[str, Any]:
        """Get hot reload status for CLI display."""
        return self.manager.get_status()


def enable_hot_reload(config_path: str, initial_config: Dict[str, Any], 
                     main_function: Callable[[Dict[str, Any]], None]):
    """Convenience function to enable hot reload for a configuration."""
    cli = HotReloadCLI()
    cli.run_with_hot_reload(config_path, initial_config, main_function) 