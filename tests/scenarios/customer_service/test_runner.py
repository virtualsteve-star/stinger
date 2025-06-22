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

from base_runner import BaseConversationSimulator, load_jsonl

async def run_customer_service_test(show_conversation: bool = True, show_transcript: bool = False):
    """Run the customer service bot integration test."""
    print("🤖 CUSTOMER SERVICE BOT INTEGRATION TEST")
    print("=" * 60)
    print("Testing moderation of toxic customer language in support conversations")
    print("=" * 60)
    
    # Initialize simulator with customer service config
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    simulator = BaseConversationSimulator(config_path)
    
    # Load test data
    test_data_path = os.path.join(os.path.dirname(__file__), 'test_data.jsonl')
    test_cases = load_jsonl(test_data_path)
    
    if not test_cases:
        print("❌ No test cases found!")
        return False
    
    # Run tests based on mode
    if show_transcript:
        await simulator.print_transcript(test_cases)
    else:
        results = await simulator.simulate_conversation(test_cases, show_conversation)
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
        """
    )
    
    parser.add_argument('--quiet', action='store_true',
                       help='Run without showing conversation details (summary only)')
    parser.add_argument('--transcript', action='store_true',
                       help='Show conversation transcript with inline moderation tags')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.quiet and args.transcript:
        print("❌ Error: Cannot use --quiet and --transcript together")
        sys.exit(1)
    
    # Run the test
    success = await run_customer_service_test(
        show_conversation=not args.quiet,
        show_transcript=args.transcript
    )
    
    if success:
        print("\n✅ Customer service test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Customer service test failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 