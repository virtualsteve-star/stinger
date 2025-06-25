#!/usr/bin/env python3
"""
Stinger Unified CLI/Test Runner

Run any scenario, all scenarios, or custom config/test data with unified options.
"""

import argparse
import sys
import os
import subprocess
from pathlib import Path
import asyncio

def get_available_scenarios():
    """Get list of available test scenarios."""
    scenarios_dir = Path(__file__).parent / 'tests' / 'scenarios'
    scenarios = []
    for item in scenarios_dir.iterdir():
        if item.is_dir() and item.name not in ['shared', '__pycache__']:
            test_runner = item / 'test_runner.py'
            if test_runner.exists():
                scenarios.append(item.name)
    return sorted(scenarios)

def get_scenario_description(scenario_name):
    """Get the first line of the scenario README as description."""
    readme = Path(__file__).parent / 'tests' / 'scenarios' / scenario_name / 'README.md'
    if readme.exists():
        try:
            with open(readme, 'r') as f:
                first_line = f.readline().strip()
                return first_line.replace('# ', '')
        except:
            return "No description available"
    return "No description available"

async def run_scenario(scenario_name, quiet=False, transcript=False, debug=False, config=None, test_data=None):
    """Run a specific test scenario, optionally with custom config/test data."""
    scenario_dir = Path(__file__).parent / 'tests' / 'scenarios' / scenario_name
    test_runner = scenario_dir / 'test_runner.py'
    if not test_runner.exists():
        print(f"❌ Test runner not found for scenario: {scenario_name}")
        return False
    cmd = ['python3', str(test_runner)]
    if quiet:
        cmd.append('--quiet')
    if transcript:
        cmd.append('--transcript')
    if debug:
        cmd.append('--debug')
    # Pass custom config/test data as env vars if provided
    env = os.environ.copy()
    if config:
        env['STINGER_CONFIG'] = config
    if test_data:
        env['STINGER_TEST_DATA'] = test_data
    try:
        result = subprocess.run(cmd, env=env, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running {scenario_name}: {e}")
        return False

def main():
    available_scenarios = get_available_scenarios()
    parser = argparse.ArgumentParser(
        description='Stinger Unified CLI/Test Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Available scenarios: {', '.join(available_scenarios)}

Examples:
  python3 stinger.py --all                       # Run all scenarios
  python3 stinger.py --scenario customer_service # Run specific scenario
  python3 stinger.py --scenario medical_bot --debug
  python3 stinger.py --list                      # List scenarios
  python3 stinger.py --scenario customer_service --config configs/customer_service.yaml --test-data tests/scenarios/customer_service/test_data.jsonl
        """
    )
    parser.add_argument('--scenario', choices=available_scenarios, help='Run specific scenario only')
    parser.add_argument('--all', action='store_true', help='Run all scenarios')
    parser.add_argument('--quiet', action='store_true', help='Summary only (no conversation details)')
    parser.add_argument('--transcript', action='store_true', help='Show conversation transcript')
    parser.add_argument('--debug', action='store_true', help='Show detailed filter debug output')
    parser.add_argument('--list', action='store_true', help='List available scenarios and exit')
    parser.add_argument('--config', type=str, help='Custom config YAML file (overrides scenario default)')
    parser.add_argument('--test-data', type=str, help='Custom test data file (overrides scenario default)')
    args = parser.parse_args()
    if args.list:
        print("Available test scenarios:")
        for scenario in available_scenarios:
            desc = get_scenario_description(scenario)
            print(f"  {scenario}: {desc}")
        return
    if args.quiet and args.transcript:
        print("❌ Error: Cannot use --quiet and --transcript together")
        sys.exit(1)
    if not args.scenario and not args.all:
        print("❌ Please specify --scenario <name> or --all")
        sys.exit(1)
    scenarios_to_run = available_scenarios if args.all else [args.scenario]
    print("\n🚀 STINGER UNIFIED TEST RUNNER")
    print("=" * 60)
    print(f"Running {len(scenarios_to_run)} scenario(s): {', '.join(scenarios_to_run)}")
    print("=" * 60)
    results = {}
    async def run_all():
        for scenario in scenarios_to_run:
            print(f"\n📋 Running scenario: {scenario}")
            print("-" * 40)
            success = await run_scenario(
                scenario,
                quiet=args.quiet,
                transcript=args.transcript,
                debug=args.debug,
                config=args.config,
                test_data=args.test_data
            )
            results[scenario] = success
            if success:
                print(f"✅ {scenario}: PASSED")
            else:
                print(f"❌ {scenario}: FAILED")
    asyncio.run(run_all())
    print("\n" + "=" * 60)
    print("STINGER TEST SUMMARY")
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
    main() 