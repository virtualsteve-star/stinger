#!/usr/bin/env python3
"""
Medical Bot Integration Test Runner

This script runs the medical bot integration tests to validate
that the moderation framework can effectively handle PII and medical terms
while allowing normal interactions.
"""

import asyncio
import argparse
import sys
import os

# Ensure src and tests are in sys.path for absolute imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SRC_PATH = os.path.join(PROJECT_ROOT, "src")
TESTS_PATH = os.path.join(PROJECT_ROOT, "tests")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)
if TESTS_PATH not in sys.path:
    sys.path.insert(0, TESTS_PATH)

try:
    from tests.shared.base_runner import BaseConversationSimulator, load_jsonl
except ImportError:
    from shared.base_runner import BaseConversationSimulator, load_jsonl


async def run_medical_bot_test(
    show_conversation: bool = True, show_transcript: bool = False, debug: bool = False
):
    """Run the medical bot integration test."""
    print("🩺 MEDICAL BOT INTEGRATION TEST")
    print("=" * 60)
    print("Testing moderation of medical advice and sensitive information in conversations")
    print("=" * 60)

    # Use env vars if set, otherwise default
    config_path = os.environ.get(
        "STINGER_CONFIG",
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
            "src",
            "scenarios",
            "medical_bot",
            "config.yaml",
        ),
    )
    test_data_path = os.environ.get(
        "STINGER_TEST_DATA", os.path.join(os.path.dirname(__file__), "test_data.jsonl")
    )
    test_cases = load_jsonl(test_data_path)

    simulator = BaseConversationSimulator(config_path, debug=debug)

    if not test_cases:
        print("❌ No test cases found!")
        return False

    # Run tests based on mode
    if show_transcript:
        await simulator.print_transcript(test_cases)
    else:
        results = await simulator.simulate_conversation(test_cases, show_conversation, debug=debug)
        simulator.print_summary(results)

    return True


async def main():
    """Main entry point with command line options."""
    parser = argparse.ArgumentParser(
        description="Medical Bot Integration Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 test_runner.py                    # Run full test with conversation details
  python3 test_runner.py --quiet            # Run test with summary only
  python3 test_runner.py --transcript       # Show conversation transcript
  python3 test_runner.py --debug            # Show detailed filter debug output
        """,
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
    parser.add_argument("--debug", action="store_true", help="Show detailed filter debug output")

    args = parser.parse_args()

    # Validate arguments
    if args.quiet and args.transcript:
        print("❌ Error: Cannot use --quiet and --transcript together")
        sys.exit(1)

    # Run the test
    success = await run_medical_bot_test(
        show_conversation=not args.quiet, show_transcript=args.transcript, debug=args.debug
    )

    if success:
        print("\n✅ Medical bot test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Medical bot test failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
