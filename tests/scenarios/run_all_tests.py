#!/usr/bin/env python3
"""
Master Test Runner for All Integration Test Scenarios

This script runs all available integration test scenarios to provide
comprehensive validation of the LLM Guardrails Framework.
"""

import argparse
import asyncio
import os
import subprocess
import sys
from pathlib import Path


def get_available_scenarios():
    """Get list of available test scenarios."""
    scenarios_dir = Path(__file__).parent
    scenarios = []

    for item in scenarios_dir.iterdir():
        if item.is_dir() and item.name not in ["shared", "__pycache__"]:
            test_runner = item / "test_runner.py"
            if test_runner.exists():
                scenarios.append(item.name)

    return sorted(scenarios)


async def run_scenario(scenario_name: str, quiet: bool = False, transcript: bool = False):
    """Run a specific test scenario."""
    scenario_dir = Path(__file__).parent / scenario_name
    test_runner = scenario_dir / "test_runner.py"

    if not test_runner.exists():
        print(f"❌ Test runner not found for scenario: {scenario_name}")
        return False

    # Build command
    cmd = ["python3", str(test_runner)]
    if quiet:
        cmd.append("--quiet")
    if transcript:
        cmd.append("--transcript")

    # Run the test
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running {scenario_name}: {e}")
        return False


async def main():
    """Main entry point."""
    available_scenarios = get_available_scenarios()

    parser = argparse.ArgumentParser(
        description="Master Test Runner for All Integration Test Scenarios",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Available scenarios: {', '.join(available_scenarios)}

Examples:
  python3 run_all_tests.py                           # Run all scenarios
  python3 run_all_tests.py --scenario customer_service  # Run specific scenario
  python3 run_all_tests.py --quiet                   # Run all with summary only
  python3 run_all_tests.py --transcript              # Show all transcripts
        """,
    )

    parser.add_argument(
        "--scenario", choices=available_scenarios, help="Run specific scenario only"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Run without showing conversation details (summary only)",
    )
    parser.add_argument(
        "--transcript",
        action="store_true",
        help="Show conversation transcript with inline moderation tags",
    )
    parser.add_argument("--list", action="store_true", help="List available scenarios and exit")

    args = parser.parse_args()

    # List scenarios if requested
    if args.list:
        print("Available test scenarios:")
        for scenario in available_scenarios:
            scenario_dir = Path(__file__).parent / scenario
            readme = scenario_dir / "README.md"
            if readme.exists():
                # Extract first line of README for description
                try:
                    with open(readme, "r") as f:
                        first_line = f.readline().strip()
                        description = first_line.replace("# ", "")
                except:
                    description = "No description available"
            else:
                description = "No description available"

            print(f"  {scenario}: {description}")
        return

    # Validate arguments
    if args.quiet and args.transcript:
        print("❌ Error: Cannot use --quiet and --transcript together")
        sys.exit(1)

    # Determine which scenarios to run
    if args.scenario:
        scenarios_to_run = [args.scenario]
    else:
        scenarios_to_run = available_scenarios

    if not scenarios_to_run:
        print("❌ No test scenarios found!")
        sys.exit(1)

    # Run tests
    print("🚀 MASTER INTEGRATION TEST RUNNER")
    print("=" * 60)
    print(f"Running {len(scenarios_to_run)} test scenario(s): {', '.join(scenarios_to_run)}")
    print("=" * 60)

    results = {}
    for scenario in scenarios_to_run:
        print(f"\n📋 Running scenario: {scenario}")
        print("-" * 40)

        success = await run_scenario(scenario, args.quiet, args.transcript)
        results[scenario] = success

        if success:
            print(f"✅ {scenario}: PASSED")
        else:
            print(f"❌ {scenario}: FAILED")

    # Summary
    print("\n" + "=" * 60)
    print("MASTER TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for success in results.values() if success)
    total = len(results)

    for scenario, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{scenario}: {status}")

    print(f"\nOverall: {passed}/{total} scenarios passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print(f"\n💥 {total - passed} test(s) failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
