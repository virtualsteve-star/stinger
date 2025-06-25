#!/usr/bin/env python3
"""
Hot Reload CLI Demonstration

This script demonstrates how the hot reload functionality works in the CLI.
"""

import tempfile
import yaml
import time
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.hot_reload import HotReloadCLI, HotReloadManager
from src.core.config import ConfigLoader


def create_temp_config(content):
    """Create a temporary config file with the given content."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(content, f)
        return f.name


def demo_basic_cli():
    """Demonstrate basic CLI functionality."""
    print("🔧 HOT RELOAD CLI DEMONSTRATION")
    print("=" * 50)
    
    # Create a temporary config file
    initial_config = {
        "version": "1.0",
        "pipeline": {
            "input": [
                {
                    "name": "demo_filter",
                    "type": "pass_through",
                    "enabled": True,
                    "on_error": "allow"
                }
            ]
        }
    }
    
    config_path = create_temp_config(initial_config)
    print(f"📁 Created temporary config: {config_path}")
    
    try:
        # Create CLI instance
        cli = HotReloadCLI()
        
        # Show initial status
        print("\n📊 Initial Status:")
        status = cli.get_status()
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        # Demonstrate status reporting
        print("\n✅ CLI Status Reporting Working")
        
        # Cleanup
        os.unlink(config_path)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if os.path.exists(config_path):
            os.unlink(config_path)


def demo_hot_reload_manager():
    """Demonstrate HotReloadManager functionality."""
    print("\n🔄 HOT RELOAD MANAGER DEMONSTRATION")
    print("=" * 50)
    
    # Create a temporary config file
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
    
    config_path = create_temp_config(initial_config)
    print(f"📁 Created temporary config: {config_path}")
    
    try:
        # Create manager
        manager = HotReloadManager()
        
        # Mock callback
        def reload_callback(new_config):
            print(f"🔄 Reload callback triggered with config: {new_config['pipeline']['input'][0]['name']}")
            success = manager.reload_config(new_config)
            print(f"✅ Reload success: {success}")
        
        # Start watching
        print("\n👀 Starting hot reload...")
        success = manager.start_watching(config_path, initial_config, reload_callback)
        assert success is True
        
        # Show status
        print("\n📊 Status after starting:")
        status = manager.get_status()
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        # Test valid config reload
        print("\n🔄 Testing valid config reload...")
        valid_config = {
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
        reload_callback(valid_config)
        
        # Test invalid config rollback
        print("\n🔄 Testing invalid config rollback...")
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
        reload_callback(invalid_config)
        
        # Show final status
        print("\n📊 Final status:")
        status = manager.get_status()
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        # Cleanup
        manager.stop_watching()
        os.unlink(config_path)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if os.path.exists(config_path):
            os.unlink(config_path)


def demo_cli_usage():
    """Show how to use the CLI with hot reload."""
    print("\n💻 CLI USAGE EXAMPLES")
    print("=" * 50)
    
    print("""
# Basic usage
python3 stinger.py --scenario customer_service

# With hot reload enabled
python3 stinger.py --scenario customer_service --hot-reload

# With debug output
python3 stinger.py --scenario customer_service --hot-reload --debug

# With custom config
python3 stinger.py --scenario customer_service --hot-reload --config configs/custom.yaml

# List available scenarios
python3 stinger.py --list

# Run all scenarios with hot reload
python3 stinger.py --all --hot-reload
""")


def main():
    """Run all demonstrations."""
    print("🚀 STINGER HOT RELOAD CLI DEMONSTRATION")
    print("=" * 60)
    
    # Demo 1: Basic CLI functionality
    demo_basic_cli()
    
    # Demo 2: HotReloadManager functionality
    demo_hot_reload_manager()
    
    # Demo 3: CLI usage examples
    demo_cli_usage()
    
    print("\n" + "=" * 60)
    print("✅ DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("""
Key Features Demonstrated:
✅ CLI status reporting
✅ Hot reload manager functionality
✅ Configuration validation and rollback
✅ Error handling
✅ Status tracking

Next Steps for Phase 4b:
1. Add CLI status command (--hot-reload-status)
2. Add documentation for hot reload usage
3. Add troubleshooting guide
4. Mark integration tests for CI skipping
""")


if __name__ == "__main__":
    main() 