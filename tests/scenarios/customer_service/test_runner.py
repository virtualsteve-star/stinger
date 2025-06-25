#!/usr/bin/env python3
"""
Customer Service Bot Integration Test Runner

This script runs the customer service bot integration tests to validate
that the moderation framework can effectively handle toxic customer language
while allowing normal interactions.
"""

import asyncio
import argparse
import sys
import os

# Add the shared directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

# Add src to path for hot reload
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))
from core.pipeline import HotReloadPipeline

from base_runner import BaseConversationSimulator, load_jsonl

def use_hot_reload():
    return (
        '--hot-reload' in sys.argv or
        os.environ.get('STINGER_HOT_RELOAD') == '1'
    )

async def run_customer_service_test(show_conversation: bool = True, show_transcript: bool = False, debug: bool = False):
    """Run the customer service bot integration test."""
    print("🤖 CUSTOMER SERVICE BOT INTEGRATION TEST")
    print("=" * 60)
    print("Testing moderation of toxic customer language in support conversations")
    print("=" * 60)
    
    # Use env vars if set, otherwise default
    config_path = os.environ.get(
        'STINGER_CONFIG',
        os.path.join(os.path.dirname(__file__), '..', '..', '..', 'configs', 'customer_service.yaml')
    )
    test_data_path = os.environ.get(
        'STINGER_TEST_DATA',
        os.path.join(os.path.dirname(__file__), 'test_data.jsonl')
    )
    test_cases = load_jsonl(test_data_path)
    
    # Use hot reload pipeline if enabled
    if use_hot_reload():
        print("[HotReload] Using HotReloadPipeline for config changes.")
        pipeline = HotReloadPipeline(config_path, debug=debug)
        simulator = BaseConversationSimulator(config_path, debug=debug, pipeline_override=pipeline)
    else:
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
        description='Customer Service Bot Integration Test Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 test_runner.py                    # Run full test with conversation details
  python3 test_runner.py --quiet            # Run test with summary only
  python3 test_runner.py --transcript       # Show conversation transcript
  python3 test_runner.py --debug            # Show detailed filter debug output
        """
    )
    
    parser.add_argument('--quiet', action='store_true',
                       help='Run without showing conversation details (summary only)')
    parser.add_argument('--transcript', action='store_true',
                       help='Show conversation transcript with inline moderation tags')
    parser.add_argument('--debug', action='store_true',
                       help='Show detailed filter debug output')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.quiet and args.transcript:
        print("❌ Error: Cannot use --quiet and --transcript together")
        sys.exit(1)
    
    # Run the test
    success = await run_customer_service_test(
        show_conversation=not args.quiet,
        show_transcript=args.transcript,
        debug=args.debug
    )
    
    if success:
        print("\n✅ Customer service test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Customer service test failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 