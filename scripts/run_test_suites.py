#!/usr/bin/env python3
"""
Test Suite Runner for Stinger Guardrails

Implements the three-tier testing strategy:
- CI: Fast tests (<30s) for development
- Efficacy: AI behavior validation (5-10 min)
- Performance: Load and scale testing (10-30 min)
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path


def run_ci_tests():
    """Run Tier 1: Fast CI tests (<30s)"""
    print("🚀 Running CI Tests (Tier 1: Fast Tests)")
    print("=" * 50)
    start = time.time()
    
    result = subprocess.run([
        "pytest", "-m", "ci", "--durations=10", "-v"
    ])
    
    elapsed = time.time() - start
    print(f"\n⏱️  CI tests completed in {elapsed:.1f}s")
    
    if elapsed > 30:
        print("⚠️  WARNING: CI tests took >30s, consider moving slow tests to efficacy tier")
    
    return result.returncode == 0


def run_efficacy_tests():
    """Run Tier 2: Comprehensive efficacy tests (5-10 minutes)"""
    print("🧪 Running Efficacy Tests (Tier 2: AI Behavior Testing)")
    print("=" * 50)
    print("ℹ️  These tests validate real AI behavior and may take 5-10 minutes")
    print("ℹ️  Requires OPENAI_API_KEY to be set")
    
    # Check for API key
    import os
    if not os.environ.get('OPENAI_API_KEY'):
        print("\n❌ ERROR: OPENAI_API_KEY not set!")
        print("Please set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-key-here'")
        return False
    
    start = time.time()
    result = subprocess.run([
        "pytest", "-m", "efficacy", "--durations=20", "-v"
    ])
    
    elapsed = time.time() - start
    print(f"\n⏱️  Efficacy tests completed in {elapsed/60:.1f} minutes")
    
    return result.returncode == 0


def run_performance_tests():
    """Run Tier 3: Performance and scalability tests (10-30 minutes)"""
    print("📊 Running Performance Tests (Tier 3: Scalability Testing)")
    print("=" * 50)
    print("ℹ️  These tests validate performance under load and may take 10-30 minutes")
    
    start = time.time()
    result = subprocess.run([
        "pytest", "-m", "performance", "--durations=20", "-v"
    ])
    
    elapsed = time.time() - start
    print(f"\n⏱️  Performance tests completed in {elapsed/60:.1f} minutes")
    
    return result.returncode == 0


def run_failed_only():
    """Run only previously failed tests"""
    print("🔄 Running Previously Failed Tests")
    print("=" * 50)
    
    result = subprocess.run([
        "pytest", "--lf", "-v"
    ])
    
    return result.returncode == 0


def run_changed_only():
    """Run tests for changed files only"""
    print("📝 Running Tests for Changed Files")
    print("=" * 50)
    
    # Get changed files
    git_diff = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        capture_output=True, text=True
    )
    changed_files = git_diff.stdout.strip().split('\n')
    
    # Find related test files
    test_files = []
    for file in changed_files:
        if file.startswith('src/'):
            # Convert src file to test file
            test_file = file.replace('src/', 'tests/').replace('.py', '_test.py')
            if Path(test_file).exists():
                test_files.append(test_file)
        elif file.startswith('tests/') and file.endswith('_test.py'):
            test_files.append(file)
    
    if test_files:
        print(f"Found {len(test_files)} test files for changed code")
        result = subprocess.run(["pytest"] + test_files + ["-v"])
        return result.returncode == 0
    else:
        print("No test files found for changed files")
        return True


def run_all_tests():
    """Run all tests across all tiers"""
    print("🎯 Running All Tests (All Tiers)")
    print("=" * 50)
    print("ℹ️  This will run CI, Efficacy, and Performance tests")
    print("ℹ️  Total time: 15-45 minutes")
    print("ℹ️  REQUIRED before pushing to main!")
    
    # Check for API key
    import os
    if not os.environ.get('OPENAI_API_KEY'):
        print("\n❌ ERROR: OPENAI_API_KEY not set!")
        print("This is an AI product - we MUST test AI behavior before release!")
        print("Please set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-key-here'")
        return False
    
    start = time.time()
    result = subprocess.run([
        "pytest", "--durations=50", "-v"
    ])
    
    elapsed = time.time() - start
    print(f"\n⏱️  All tests completed in {elapsed/60:.1f} minutes")
    
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(
        description="Stinger Test Suite Runner - Three-tier testing strategy"
    )
    parser.add_argument(
        "suite", 
        choices=["ci", "efficacy", "performance", "all", "failed", "changed"],
        help="Test suite to run"
    )
    parser.add_argument(
        "--profile", 
        action="store_true", 
        help="Profile test execution"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true", 
        help="Run with coverage reporting"
    )
    
    args = parser.parse_args()
    
    # Add coverage if requested
    if args.coverage:
        subprocess.run(["coverage", "erase"])
        # Modify pytest commands to use coverage run
    
    # Run appropriate test suite
    if args.suite == "ci":
        success = run_ci_tests()
    elif args.suite == "efficacy":
        success = run_efficacy_tests()
    elif args.suite == "performance":
        success = run_performance_tests()
    elif args.suite == "all":
        success = run_all_tests()
    elif args.suite == "failed":
        success = run_failed_only()
    elif args.suite == "changed":
        success = run_changed_only()
    
    # Generate coverage report if requested
    if args.coverage:
        subprocess.run(["coverage", "report", "-m"])
        subprocess.run(["coverage", "html"])
        print("\n📊 Coverage report generated in htmlcov/")
    
    # Exit with appropriate code
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()