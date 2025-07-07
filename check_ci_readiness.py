#!/usr/bin/env python3
"""Check CI readiness before pushing."""
import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"\nChecking: {description}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description}: PASSED")
            return True
        else:
            print(f"❌ {description}: FAILED")
            if result.stderr:
                print(f"   Error: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"❌ {description}: ERROR - {e}")
        return False

def main():
    """Run CI readiness checks."""
    print("🔍 Checking CI Readiness...")
    print("=" * 50)
    
    checks_passed = []
    
    # 1. Check for uncommitted changes
    result = run_command("git status --porcelain", "Git status")
    if result:
        output = subprocess.check_output("git status --porcelain", shell=True, text=True)
        if output.strip():
            print(f"   Warning: Uncommitted changes found:\n{output[:500]}")
            checks_passed.append(False)
        else:
            checks_passed.append(True)
    
    # 2. Check Black formatting
    checks_passed.append(
        run_command("python3 -m black --check src/ tests/ 2>/dev/null", "Black formatting")
    )
    
    # 3. Check import ordering
    checks_passed.append(
        run_command("python3 -m isort --check-only src/ tests/ 2>/dev/null", "Import ordering")
    )
    
    # 4. Run a quick test
    checks_passed.append(
        run_command("python3 -m pytest tests/test_simple_pii_detection_guardrail.py -q", "Sample test")
    )
    
    # 5. Check current branch
    branch = subprocess.check_output("git branch --show-current", shell=True, text=True).strip()
    print(f"\nCurrent branch: {branch}")
    if branch != "dev":
        print("⚠️  Warning: Not on dev branch")
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY:")
    total = len(checks_passed)
    passed = sum(1 for x in checks_passed if x)
    
    print(f"Checks passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ Ready for CI!")
        return 0
    else:
        print("\n❌ Not ready for CI - fix issues above")
        return 1

if __name__ == "__main__":
    sys.exit(main())