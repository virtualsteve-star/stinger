#!/usr/bin/env python3
"""
API Key Management CLI

Secure tool for managing API keys for testing and development.
"""

import argparse
import getpass
import sys
from src.core.api_key_manager import APIKeyManager


def main():
    parser = argparse.ArgumentParser(description='Manage API keys securely')
    parser.add_argument('action', choices=['set', 'get', 'list', 'test', 'clear'], 
                       help='Action to perform')
    parser.add_argument('--service', '-s', default='openai', 
                       help='Service name (default: openai)')
    parser.add_argument('--key', '-k', help='API key (for set action)')
    
    args = parser.parse_args()
    
    manager = APIKeyManager()
    
    if args.action == 'set':
        # Get key from argument or prompt
        key = args.key
        if not key:
            key = getpass.getpass(f'Enter {args.service} API key: ')
        
        if not key:
            print("❌ No key provided")
            sys.exit(1)
        
        # Validate key format
        if not manager.validate_key(args.service, key):
            print(f"❌ Invalid {args.service} API key format")
            sys.exit(1)
        
        # Save to secure storage
        if manager.save_to_secure_storage(args.service, key):
            print(f"✅ {args.service} API key saved to secure storage")
            print(f"   Location: {manager.get_secure_storage_path()}")
        else:
            print(f"❌ Failed to save {args.service} API key")
            sys.exit(1)
    
    elif args.action == 'get':
        key = manager.get_key(args.service)
        if key:
            # Show masked version for security
            masked_key = key[:8] + '*' * (len(key) - 12) + key[-4:]
            print(f"✅ {args.service} API key found: {masked_key}")
        else:
            print(f"❌ No {args.service} API key found")
            sys.exit(1)
    
    elif args.action == 'list':
        services = manager.list_services()
        if services:
            print("📋 Available API keys:")
            for service in services:
                key = manager.get_key(service)
                if key:
                    masked_key = key[:8] + '*' * (len(key) - 12) + key[-4:]
                    print(f"  {service}: {masked_key}")
        else:
            print("📋 No API keys found")
    
    elif args.action == 'test':
        key = manager.get_key(args.service)
        if not key:
            print(f"❌ No {args.service} API key found")
            sys.exit(1)
        
        print(f"🧪 Testing {args.service} API key...")
        
        if args.service == 'openai':
            try:
                from src.adapters.openai_adapter import OpenAIAdapter
                adapter = OpenAIAdapter(key)
                
                # Test health check
                import asyncio
                health = asyncio.run(adapter.health_check())
                
                if health.available:
                    print(f"✅ {args.service} API key is valid and working")
                    if health.response_time_ms:
                        print(f"   Response time: {health.response_time_ms:.1f}ms")
                else:
                    print(f"❌ {args.service} API key test failed: {health.error_message}")
                    sys.exit(1)
                    
            except Exception as e:
                print(f"❌ {args.service} API test failed: {e}")
                sys.exit(1)
        else:
            print(f"✅ {args.service} API key format is valid")
    
    elif args.action == 'clear':
        # Clear from memory (secure storage remains)
        manager.clear_keys()
        print("✅ API keys cleared from memory")
        print("   Note: Secure storage file remains. Use 'rm ~/.stinger/api_keys.enc' to delete it.")


if __name__ == "__main__":
    main() 