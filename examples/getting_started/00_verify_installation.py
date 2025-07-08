#!/usr/bin/env python3
"""
Verify Stinger Installation - Stinger Guardrails

First thing to run after pip install to verify everything is working.
This script checks that Stinger is properly installed and all core
components are accessible.
"""

import sys
import subprocess
from pathlib import Path


def check_stinger_package():
    """Check if Stinger package is installed and get version."""
    print("🔍 Checking Stinger package installation...")
    
    try:
        import stinger
        version = stinger.__version__
        print(f"✅ Stinger {version} is installed")
        return True, version
    except ImportError as e:
        print(f"❌ Stinger is not installed: {e}")
        print("\nTo install:")
        print("   pip install stinger-guardrails-alpha")
        return False, None


def check_core_imports():
    """Test that core imports work correctly."""
    print("\n🔍 Testing core imports...")
    
    imports_to_test = [
        ("stinger.GuardrailPipeline", "Main pipeline class"),
        ("stinger.core.audit", "Audit trail functionality"),
        ("stinger.Conversation", "Conversation tracking"),
        ("stinger.core.health_monitor.HealthMonitor", "Health monitoring")
    ]
    
    all_good = True
    for import_path, description in imports_to_test:
        try:
            module_path, class_name = import_path.rsplit('.', 1) if '.' in import_path else (import_path, None)
            
            if class_name:
                module = __import__(module_path, fromlist=[class_name])
                getattr(module, class_name)
            else:
                __import__(module_path)
                
            print(f"   ✅ {description:<30} ({import_path})")
        except Exception as e:
            print(f"   ❌ {description:<30} ({import_path})")
            print(f"      Error: {e}")
            all_good = False
    
    return all_good


def check_cli_command():
    """Check if the stinger CLI command is available."""
    print("\n🔍 Checking CLI command availability...")
    
    try:
        result = subprocess.run(
            ['stinger', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print(f"✅ CLI command is available")
            print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ CLI command failed with code {result.returncode}")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            return False
            
    except FileNotFoundError:
        print("❌ 'stinger' command not found in PATH")
        print("   This might be normal if installed in development mode")
        print("   Try: python -m stinger.cli --version")
        return False
    except subprocess.TimeoutExpired:
        print("❌ CLI command timed out")
        return False
    except Exception as e:
        print(f"❌ Error checking CLI: {e}")
        return False


def check_preset_availability():
    """Check if preset configurations are available."""
    print("\n🔍 Checking preset configurations...")
    
    try:
        from stinger import GuardrailPipeline
        
        presets = ['basic', 'customer_service', 'medical', 'financial']
        all_good = True
        
        for preset in presets:
            try:
                pipeline = GuardrailPipeline.from_preset(preset)
                print(f"   ✅ {preset:<20} preset available")
            except Exception as e:
                print(f"   ❌ {preset:<20} preset failed: {e}")
                all_good = False
                
        return all_good
        
    except Exception as e:
        print(f"❌ Error checking presets: {e}")
        return False


def check_api_key_setup():
    """Check if API keys are configured (optional)."""
    print("\n🔍 Checking API key configuration (optional)...")
    
    import os
    
    if os.environ.get('OPENAI_API_KEY'):
        print("✅ OPENAI_API_KEY environment variable is set")
        print("   AI-powered guardrails will be available")
    else:
        print("ℹ️  OPENAI_API_KEY not found")
        print("   This is optional - basic guardrails will still work")
        print("   To enable AI features, set: export OPENAI_API_KEY='your-key'")
    
    return True  # Not a failure if missing


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("🚀 STINGER INSTALLATION VERIFICATION")
    print("=" * 60)
    
    # Track overall status
    all_checks_passed = True
    
    # Run checks
    package_ok, version = check_stinger_package()
    all_checks_passed &= package_ok
    
    if package_ok:
        imports_ok = check_core_imports()
        all_checks_passed &= imports_ok
        
        cli_ok = check_cli_command()
        # CLI might not work in dev mode, so don't fail overall check
        
        presets_ok = check_preset_availability()
        all_checks_passed &= presets_ok
        
        check_api_key_setup()  # Just informational
    
    # Summary
    print("\n" + "=" * 60)
    if all_checks_passed:
        print("🎉 VERIFICATION COMPLETE - All core checks passed!")
        print("\nNext steps:")
        print("1. Run example: python 01_basic_installation.py")
        print("2. Try the demo: stinger demo")
        print("3. Check out the getting started guide")
    else:
        print("❌ VERIFICATION FAILED - Some checks did not pass")
        print("\nTroubleshooting:")
        print("1. Ensure you installed: pip install stinger-guardrails-alpha")
        print("2. Check you're in the correct Python environment")
        print("3. For development, run from the repo root with PYTHONPATH set")
        print("4. See troubleshooting guide for more help")
    
    print("=" * 60)
    
    return 0 if all_checks_passed else 1


if __name__ == "__main__":
    sys.exit(main())