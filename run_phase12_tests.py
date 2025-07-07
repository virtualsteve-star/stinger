#!/usr/bin/env python3
"""
Phase 12 Test Runner - Python version
"""
import subprocess
import sys
import os
from pathlib import Path

# Colors
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
NC = '\033[0m'  # No Color

def print_header():
    print(f"{CYAN}{'='*80}{NC}")
    print(f"{CYAN}{'PHASE 12 AUTOMATED TEST SUITE':^80}{NC}")
    print(f"{CYAN}{'='*80}{NC}")
    print(f"\n{YELLOW}Running all Phase 12 tests to verify PyPI publishing readiness...{NC}\n")

def run_test(test_name, test_func):
    """Run a test and return success status."""
    print(f"\n{BLUE}{'='*80}{NC}")
    print(f"{BLUE}Testing: {test_name}{NC}")
    print(f"{BLUE}{'='*80}{NC}")
    
    try:
        success, message = test_func()
        if success:
            print(f"\n{GREEN}✅ {test_name}: PASSED{NC}")
            if message:
                print(f"   {message}")
        else:
            print(f"\n{RED}❌ {test_name}: FAILED{NC}")
            if message:
                print(f"   {message}")
        return success
    except Exception as e:
        print(f"\n{RED}❌ {test_name}: FAILED with exception{NC}")
        print(f"   {str(e)}")
        return False

def test_version_consistency():
    """Check version consistency across files."""
    files_to_check = {
        'pyproject.toml': 'version = "',
        'src/stinger/__init__.py': '__version__ = "',
        '.bumpversion.cfg': 'current_version = '
    }
    
    versions = {}
    for filepath, pattern in files_to_check.items():
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                for line in content.split('\n'):
                    if pattern in line:
                        # Extract version
                        if filepath == '.bumpversion.cfg':
                            version = line.split('=')[1].strip()
                        else:
                            version = line.split('"')[1]
                        versions[filepath] = version
                        print(f"  {filepath}: {version}")
                        break
        except Exception as e:
            return False, f"Error reading {filepath}: {e}"
    
    # Check if all versions match
    unique_versions = set(versions.values())
    if len(unique_versions) == 1:
        return True, f"All files have version: {list(unique_versions)[0]}"
    else:
        return False, f"Version mismatch: {versions}"

def test_imports():
    """Test that local imports work."""
    test_code = """
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

try:
    from stinger import GuardrailPipeline, audit, Conversation
    print("✅ Imports successful")
    
    # Test basic functionality
    pipeline = GuardrailPipeline.from_preset('basic')
    result = pipeline.check_input("My SSN is 123-45-6789")
    if result['blocked']:
        print("✅ PII detection works")
    else:
        print("❌ PII detection failed")
        sys.exit(1)
    
    # Test safe content
    result = pipeline.check_input("Hello world")
    if not result['blocked']:
        print("✅ Safe content passes")
    else:
        print("❌ Safe content incorrectly blocked")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Import test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""
    
    result = subprocess.run([sys.executable, '-c', test_code], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        return True, result.stdout.strip()
    else:
        return False, f"Import test failed:\n{result.stderr}"

def test_cli():
    """Test CLI functionality."""
    cli_result = subprocess.run(
        [sys.executable, '-m', 'stinger.cli', '--help'],
        capture_output=True, text=True, cwd=os.getcwd()
    )
    
    if cli_result.returncode == 0:
        # Test actual functionality
        test_result = subprocess.run(
            [sys.executable, '-m', 'stinger.cli', 'check-prompt', 'My SSN is 123-45-6789'],
            capture_output=True, text=True, cwd=os.getcwd()
        )
        
        if 'BLOCKED' in test_result.stdout or 'blocked' in test_result.stdout:
            return True, "CLI works and guardrails function correctly"
        else:
            return False, f"CLI runs but guardrails not working properly:\n{test_result.stdout}"
    else:
        return False, f"CLI help failed:\n{cli_result.stderr}"

def test_package_structure():
    """Verify package structure is correct."""
    required_files = [
        'pyproject.toml',
        'README.md',
        'LICENSE',
        'CHANGELOG.md',
        'src/stinger/__init__.py',
        'src/stinger/cli.py',
        'src/stinger/core/pipeline.py',
        'src/stinger/core/guardrail_interface.py'
    ]
    
    missing = []
    for filepath in required_files:
        if not os.path.exists(filepath):
            missing.append(filepath)
    
    if missing:
        return False, f"Missing files: {', '.join(missing)}"
    
    # Check data directories
    data_dirs = ['src/stinger/data', 'src/stinger/guardrails/configs']
    missing_dirs = []
    for dirpath in data_dirs:
        if not os.path.isdir(dirpath):
            missing_dirs.append(dirpath)
    
    if missing_dirs:
        return False, f"Missing directories: {', '.join(missing_dirs)}"
    
    return True, "All required files and directories present"

def test_build_capability():
    """Test if we can build the package."""
    # Check if build module is available
    try:
        import build
        has_build = True
    except ImportError:
        has_build = False
        
    try:
        import twine
        has_twine = True
    except ImportError:
        has_twine = False
    
    if not has_build or not has_twine:
        missing = []
        if not has_build:
            missing.append('build')
        if not has_twine:
            missing.append('twine')
        return False, f"Missing required packages: {', '.join(missing)}. Run: pip install {' '.join(missing)}"
    
    # Check if dist directory exists (from previous builds)
    if os.path.exists('dist') and os.listdir('dist'):
        files = os.listdir('dist')
        return True, f"Found existing build artifacts: {', '.join(files)}"
    else:
        return True, "Build tools available (no existing builds found)"

def test_guardrail_presets():
    """Test all guardrail presets load correctly."""
    test_code = """
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from stinger import GuardrailPipeline

presets = ['basic', 'customer_service', 'medical', 'educational', 'financial', 'content_moderation']
failed = []

for preset in presets:
    try:
        pipeline = GuardrailPipeline.from_preset(preset)
        print(f"✅ Preset '{preset}' loads")
    except Exception as e:
        print(f"❌ Preset '{preset}' failed: {e}")
        failed.append(preset)

if failed:
    sys.exit(1)
"""
    
    result = subprocess.run([sys.executable, '-c', test_code], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        return True, "All presets load successfully"
    else:
        return False, f"Some presets failed:\n{result.stdout}\n{result.stderr}"

def main():
    """Run all tests."""
    print_header()
    
    tests = [
        ("Version Consistency", test_version_consistency),
        ("Package Structure", test_package_structure),
        ("Local Imports", test_imports),
        ("CLI Functionality", test_cli),
        ("Build Capability", test_build_capability),
        ("Guardrail Presets", test_guardrail_presets),
    ]
    
    results = []
    for test_name, test_func in tests:
        success = run_test(test_name, test_func)
        results.append((test_name, success))
    
    # Summary
    print(f"\n{CYAN}{'='*80}{NC}")
    print(f"{CYAN}{'FINAL TEST SUMMARY':^80}{NC}")
    print(f"{CYAN}{'='*80}{NC}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\nTotal Tests: {BLUE}{total}{NC}")
    print(f"Passed: {GREEN}{passed}{NC}")
    print(f"Failed: {RED}{total - passed}{NC}")
    
    print("\nDetailed Results:")
    for test_name, success in results:
        status = f"{GREEN}PASSED{NC}" if success else f"{RED}FAILED{NC}"
        print(f"  {test_name}: {status}")
    
    if passed == total:
        print(f"\n{GREEN}🎉 ALL TESTS PASSED! Ready for PyPI publishing.{NC}")
        print(f"\n{YELLOW}Next Steps:{NC}")
        print("1. Run: ./scripts/build_package.sh")
        print("2. Upload to Test PyPI: ./scripts/upload_to_pypi.sh (option 1)")
        print("3. Test: ./scripts/test_pypi_package.sh (option 1)")
        print("4. Upload to PyPI: ./scripts/upload_to_pypi.sh (option 2)")
        print("5. Create GitHub Release: v0.1.0a3")
        return 0
    else:
        print(f"\n{RED}❌ Some tests failed. Please fix issues before publishing.{NC}")
        return 1

if __name__ == "__main__":
    sys.exit(main())