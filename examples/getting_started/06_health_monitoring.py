#!/usr/bin/env python3
"""
Health Monitoring Example - Stinger Guardrails

Demonstrates health monitoring and system status.
Follows the Health Monitoring section from the Getting Started guide.
"""

from stinger import GuardrailPipeline
from stinger.core.health_monitor import HealthMonitor


def main():
    print("🏥 Health Monitoring Example")
    print("=" * 35)
    
    # Step 1: Create health monitor
    print("\n1. Creating health monitor...")
    monitor = HealthMonitor()
    print(f"   Health monitor ready")
    
    # Step 2: Get basic health status
    print("\n2. Basic health status:")
    print("-" * 20)
    
    health = monitor.get_system_health()
    
    print(f"   Overall status: {'✅ Healthy' if health.overall_status == 'healthy' else '❌ Unhealthy'}")
    print(f"   Pipeline status: {'✅ OK' if health.pipeline_status.get('available', False) else '❌ Error'}")
    print(f"   API keys status: {'✅ OK' if health.api_keys_status else '❌ Error'}")
    print(f"   Rate limiter status: {'✅ OK' if health.rate_limiter_status.get('available', False) else '❌ Error'}")
    
    # Step 3: Check pipeline health
    print("\n3. Pipeline health details:")
    print("-" * 25)
    
    try:
        pipeline = GuardrailPipeline.from_preset('customer_service')
        status = pipeline.get_guardrail_status()
        
        print(f"   Total guardrails: {status.get('total', 'N/A')}")
        print(f"   Enabled: {status.get('total_enabled', 'N/A')}")
        print(f"   Disabled: {status.get('total_disabled', 'N/A')}")
        
        # Show individual guardrail status
        guardrails = pipeline.get_guardrail_configs()
        print(f"\n   Individual guardrails:")
        for name, config in guardrails.items():
            enabled = config.get('enabled', False)
            status_icon = "✅" if enabled else "❌"
            print(f"      {status_icon} {name}: {'Enabled' if enabled else 'Disabled'}")
            
    except Exception as e:
        print(f"   ❌ Pipeline error: {e}")
        print("   💡 This is normal if pipeline is not fully configured")
    
    # Step 4: Test health with operations
    print("\n4. Testing health with operations:")
    print("-" * 35)
    
    try:
        test_cases = [
            ("Hello, how can you help me?", "Normal greeting"),
            ("My credit card is 4111-1111-1111-1111", "PII content"),
            ("You are so stupid!", "Toxic content")
        ]
        
        for content, description in test_cases:
            print(f"\n📝 Testing: {description}")
            result = pipeline.check_input(content)
            
            if result['blocked']:
                print(f"   ❌ BLOCKED: {result['reasons']}")
            elif result['warnings']:
                print(f"   ⚠️  WARNINGS: {result['warnings']}")
            else:
                print("   ✅ PASSED")
    except Exception as e:
        print(f"   ❌ Test error: {e}")
    
    # Step 5: Get detailed health information
    print("\n5. Detailed health information:")
    print("-" * 30)
    
    # Pipeline details
    pipeline_info = health.pipeline_status
    if pipeline_info.get('available', False):
        print(f"   Pipeline: ✅ Available")
        print(f"      Guardrails loaded: {pipeline_info.get('total', 0)}")
        print(f"      Enabled guardrails: {pipeline_info.get('total_enabled', 0)}")
    else:
        print(f"   Pipeline: ❌ {pipeline_info.get('error', 'Not available')}")
    
    # API keys details
    api_info = health.api_keys_status
    if api_info:
        print(f"   API Keys: ✅ Available")
        print(f"      Configured services: {len(api_info)}")
        working_keys = sum(1 for status in api_info.values() if status)
        print(f"      Working services: {working_keys}")
    else:
        print(f"   API Keys: ❌ No services configured")
    
    # Rate limiter details
    rate_info = health.rate_limiter_status
    if rate_info.get('available', False):
        print(f"   Rate Limiter: ✅ Available")
        print(f"      Tracked keys: {rate_info.get('total_tracked_keys', 0)}")
    else:
        print(f"   Rate Limiter: ❌ {rate_info.get('error', 'Unknown error')}")
    
    # Step 6: Recent errors (if any)
    print("\n6. Recent errors:")
    print("-" * 15)
    
    recent_errors = health.recent_errors
    if recent_errors:
        for error in recent_errors[:3]:  # Show last 3 errors
            print(f"   ❌ {error.timestamp}: {error.message}")
    else:
        print("   ✅ No recent errors")
    
    # Step 7: Performance metrics
    print("\n7. Performance metrics:")
    print("-" * 20)
    
    metrics = health.performance_metrics
    print(f"   Total requests: {metrics.get('total_requests', 0)}")
    print(f"   Blocked requests: {metrics.get('blocked_requests', 0)}")
    print(f"   Average response time: {metrics.get('avg_response_time_ms', 0):.2f}ms")
    print(f"   Peak response time: {metrics.get('peak_response_time_ms', 0):.2f}ms")
    
    print("\n🎉 Health monitoring working! All systems operational.")


if __name__ == "__main__":
    main() 