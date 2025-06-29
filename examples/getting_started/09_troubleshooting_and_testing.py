#!/usr/bin/env python3
"""
Troubleshooting and Testing Example - Stinger Guardrails

Demonstrates running tests and common troubleshooting steps.
Follows the Testing and Troubleshooting sections from the Getting Started guide.
"""

import subprocess
import sys
from pathlib import Path
from stinger import GuardrailPipeline


def main():
    print("🧪 Troubleshooting and Testing Example")
    print("=" * 40)
    
    # Step 1: Basic installation verification
    print("\n1. Basic installation verification:")
    print("-" * 35)
    
    try:
        # Test basic import
        from stinger import GuardrailPipeline
        print("   ✅ Stinger imports successfully")
        
        # Test pipeline creation
        pipeline = GuardrailPipeline.from_preset('customer_service')
        print("   ✅ Pipeline creation works")
        
        # Test basic functionality
        result = pipeline.check_input("Hello world")
        print("   ✅ Basic guardrail check works")
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        print("   💡 Solution: Check PYTHONPATH and installation")
        return
    except Exception as e:
        print(f"   ❌ Setup error: {e}")
        print("   💡 Solution: Check configuration and dependencies")
        return
    
    # Step 2: API key verification
    print("\n2. API key verification:")
    print("-" * 20)
    
    try:
        # This would normally check API keys
        print("   ℹ️  API key status: Check with 'python manage_api_keys.py list'")
        print("   💡 If no keys: Run 'python manage_api_keys.py add openai'")
    except Exception as e:
        print(f"   ❌ API key error: {e}")
    
    # Step 3: Health check simulation
    print("\n3. Health check simulation:")
    print("-" * 25)
    
    try:
        from stinger.core.health_monitor import HealthMonitor
        
        monitor = HealthMonitor()
        health = monitor.get_system_health()
        
        print(f"   Overall status: {health.overall_status}")
        print(f"   Pipeline: {'✅ OK' if health.pipeline_status.get('available', False) else '❌ Error'}")
        print(f"   API Keys: {'✅ OK' if health.api_keys_status else '❌ Error'}")
        print(f"   Rate Limiter: {'✅ OK' if health.rate_limiter_status.get('available', False) else '❌ Error'}")
        
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Step 4: Test suite simulation
    print("\n4. Test suite simulation:")
    print("-" * 25)
    
    test_commands = [
        ("python -m pytest tests/ -v", "Run all tests"),
        ("python -m pytest tests/test_simple.py -v", "Run basic tests"),
        ("python tests/scenarios/run_all_tests.py", "Run scenario tests"),
        ("python -m pytest tests/test_integration.py -v", "Run integration tests")
    ]
    
    print("   Available test commands:")
    for command, description in test_commands:
        print(f"   {command}")
        print(f"      → {description}")
    
    # Step 5: Common troubleshooting scenarios
    print("\n5. Common troubleshooting scenarios:")
    print("-" * 35)
    
    scenarios = [
        {
            "issue": "Import Errors",
            "symptoms": "ModuleNotFoundError or ImportError",
            "solutions": [
                "Check PYTHONPATH: export PYTHONPATH=src:$PYTHONPATH",
                "Verify installation: pip install -r requirements.txt",
                "Check working directory: cd Stinger"
            ]
        },
        {
            "issue": "API Key Issues", 
            "symptoms": "Authentication errors or missing keys",
            "solutions": [
                "Check keys: python manage_api_keys.py list",
                "Add key: python manage_api_keys.py add openai",
                "Test key: python manage_api_keys.py test openai"
            ]
        },
        {
            "issue": "Configuration Errors",
            "symptoms": "Pipeline creation fails or preset errors",
            "solutions": [
                "Check health: python -m stinger.cli health",
                "Verify configs: Check YAML syntax",
                "Use debug: python demos/conversation_demo.py --debug"
            ]
        }
    ]
    
    for scenario in scenarios:
        print(f"\n   🚨 {scenario['issue']}:")
        print(f"      Symptoms: {scenario['symptoms']}")
        print(f"      Solutions:")
        for solution in scenario['solutions']:
            print(f"         • {solution}")
    
    # Step 6: Performance testing
    print("\n6. Performance testing:")
    print("-" * 20)
    
    try:
        import time
        
        # Test response time
        start_time = time.time()
        for i in range(10):
            result = pipeline.check_input(f"Test message {i}")
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 10 * 1000  # Convert to ms
        print(f"   Average response time: {avg_time:.2f}ms per request")
        
        if avg_time < 100:
            print("   ✅ Performance: Good")
        elif avg_time < 500:
            print("   ⚠️  Performance: Acceptable")
        else:
            print("   ❌ Performance: Slow - check system resources")
            
    except Exception as e:
        print(f"   ❌ Performance test error: {e}")
    
    # Step 7: Getting help
    print("\n7. Getting help:")
    print("-" * 15)
    
    help_resources = [
        ("Documentation", "docs/ directory"),
        ("Examples", "examples/ and demos/ directories"), 
        ("Tests", "tests/ directory"),
        ("Health Monitor", "python -m stinger.cli health"),
        ("CLI Help", "python -m stinger.cli --help")
    ]
    
    for resource, location in help_resources:
        print(f"   📚 {resource}: {location}")
    
    print("\n🎉 Troubleshooting and testing complete! System is ready for use.")


if __name__ == "__main__":
    main() 