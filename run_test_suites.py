#!/usr/bin/env python3
"""
Test Suite Runner for Stinger Guardrails

This script provides easy access to different test suites based on the two-tier strategy:

Tier 1: Quick Sanity Tests (Regular Suite)
- Purpose: Verify AI guardrails are working and responding
- Performance: <30 seconds total for all AI sanity checks
- Frequency: Run on every PR, every development cycle

Tier 2: Comprehensive Efficacy Suite
- Purpose: Measure detection accuracy, false positive rates, edge cases
- Performance: 5-10 minutes for thorough validation
- Frequency: Run in CI on main branch, before releases
"""

import subprocess
import sys
import time
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n🚀 {description}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 60)
    
    start_time = time.time()
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        elapsed = time.time() - start_time
        print(f"\n✅ {description} completed in {elapsed:.1f}s")
        return True
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start_time
        print(f"\n❌ {description} failed after {elapsed:.1f}s")
        return False


def run_sanity_tests():
    """Run quick sanity tests for AI guardrails"""
    cmd = [sys.executable, "-m", "pytest", "tests/ai_sanity_tests.py", "-v"]
    return run_command(cmd, "Running AI Guardrail Sanity Tests")


def run_efficacy_tests():
    """Run comprehensive efficacy tests"""
    cmd = [sys.executable, "-m", "pytest", "tests/efficacy/", "-v", "-m", "efficacy"]
    return run_command(cmd, "Running AI Guardrail Efficacy Tests")


def run_fast_tests():
    """Run all fast tests (excludes slow and efficacy tests)"""
    cmd = [sys.executable, "-m", "pytest", "-v", "-m", "not slow and not efficacy"]
    return run_command(cmd, "Running Fast Test Suite")


def run_all_tests():
    """Run all tests including efficacy tests"""
    cmd = [sys.executable, "-m", "pytest", "-v"]
    return run_command(cmd, "Running Complete Test Suite")


def run_integration_tests():
    """Run integration tests"""
    cmd = [sys.executable, "-m", "pytest", "-v", "-m", "integration"]
    return run_command(cmd, "Running Integration Tests")


def run_behavioral_tests():
    """Run behavioral tests"""
    cmd = [sys.executable, "-m", "pytest", "tests/behavioral/", "-v"]
    return run_command(cmd, "Running Behavioral Tests")


def main():
    parser = argparse.ArgumentParser(description="Stinger Guardrails Test Suite Runner")
    parser.add_argument(
        "suite",
        choices=["sanity", "efficacy", "fast", "all", "integration", "behavioral"],
        help="Test suite to run"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,  # 10 minutes default
        help="Timeout in seconds for test execution"
    )
    
    args = parser.parse_args()
    
    print("🧪 Stinger Guardrails Test Suite Runner")
    print("=" * 50)
    
    # Validate test files exist
    if args.suite == "sanity" and not Path("tests/ai_sanity_tests.py").exists():
        print("❌ Sanity tests not found: tests/ai_sanity_tests.py")
        sys.exit(1)
    
    if args.suite == "efficacy" and not Path("tests/efficacy/").exists():
        print("❌ Efficacy tests not found: tests/efficacy/")
        sys.exit(1)
    
    # Run selected test suite
    success = False
    if args.suite == "sanity":
        success = run_sanity_tests()
    elif args.suite == "efficacy":
        success = run_efficacy_tests()
    elif args.suite == "fast":
        success = run_fast_tests()
    elif args.suite == "all":
        success = run_all_tests()
    elif args.suite == "integration":
        success = run_integration_tests()
    elif args.suite == "behavioral":
        success = run_behavioral_tests()
    
    if success:
        print(f"\n🎉 {args.suite.title()} test suite completed successfully!")
        sys.exit(0)
    else:
        print(f"\n💥 {args.suite.title()} test suite failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 