import json
import asyncio
import sys
import os
from collections import defaultdict
from typing import Dict, List, Optional
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.stinger.core.config import ConfigLoader
from src.stinger.core.pipeline import GuardrailPipeline
from src.stinger.guardrails.pass_through import PassThroughGuardrail
from src.stinger.guardrails.keyword_block import KeywordBlockGuardrail
from src.stinger.guardrails.regex_guardrail import RegexGuardrail
from src.stinger.guardrails.length_guardrail import LengthGuardrail
from src.stinger.guardrails.url_guardrail import URLGuardrail

def load_jsonl(path):
    """Load test cases from JSONL file."""
    try:
        with open(path, 'r') as f:
            return [json.loads(line) for line in f if line.strip()]
    except FileNotFoundError:
        print(f"⚠️ Test corpus not found: {path}")
        return []

GUARDRAIL_REGISTRY = {
    'pass_through': PassThroughGuardrail,
    'keyword_block': KeywordBlockGuardrail,
    'regex_filter': RegexGuardrail,
    'length_filter': LengthGuardrail,
    'url_filter': URLGuardrail,
}

class ConversationSimulator:
    """Simulates realistic bot conversations with moderation."""
    
    def __init__(self, config_path: str):
        self.config_loader = ConfigLoader()
        self.config = self.config_loader.load(config_path)
        self.pipeline = GuardrailPipeline(config_path)
        
    async def simulate_conversation(self, test_cases: List[dict], show_conversation: bool = True) -> Dict:
        """Simulate a conversation and return results."""
        conversations = defaultdict(list)
        results = {
            'total_messages': 0,
            'blocked_messages': 0,
            'warned_messages': 0,
            'allowed_messages': 0,
            'conversations': {}
        }
        
        # Group test cases by conversation
        for case in test_cases:
            conv_id = case.get('conversation_id', 'unknown')
            conversations[conv_id].append(case)
        
        # Process each conversation
        for conv_id, messages in conversations.items():
            conv_results = {
                'messages': [],
                'blocked_count': 0,
                'warned_count': 0,
                'allowed_count': 0
            }
            
            if show_conversation:
                print(f"\n{'='*60}")
                print(f"CONVERSATION: {conv_id}")
                print(f"{'='*60}")
            
            for i, case in enumerate(messages, 1):
                test_input = case.get('input')
                expected = case.get('expected')
                description = case.get('description', 'No description')
                speaker = case.get('speaker', 'unknown')
                turn = case.get('turn', i)
                
                # Process through pipeline
                try:
                    result = await self.pipeline.check_input_async(test_input)
                    # Convert PipelineResult to action string
                    if result['blocked']:
                        action = 'block'
                    elif result['warnings']:
                        action = 'warn'
                    else:
                        action = 'allow'
                    reason = '; '.join(result['reasons']) if result['reasons'] else 'no match'
                except Exception as e:
                    action = "error"
                    reason = f"Error: {str(e)}"
                
                # Track results
                results['total_messages'] += 1
                conv_results['messages'].append({
                    'turn': turn,
                    'speaker': speaker,
                    'input': test_input,
                    'action': action,
                    'reason': reason,
                    'expected': expected,
                    'description': description
                })
                
                if action == 'block':
                    results['blocked_messages'] += 1
                    conv_results['blocked_count'] += 1
                elif action == 'warn':
                    results['warned_messages'] += 1
                    conv_results['warned_count'] += 1
                else:
                    results['allowed_messages'] += 1
                    conv_results['allowed_count'] += 1
                
                # Display conversation if requested
                if show_conversation:
                    self._display_message(turn, speaker, test_input, action, reason, expected)
            
            results['conversations'][conv_id] = conv_results
            
            if show_conversation:
                print(f"\n📊 Conversation Summary: {conv_results['allowed_count']} allowed, "
                      f"{conv_results['warned_count']} warned, {conv_results['blocked_count']} blocked")
        
        return results
    
    def _display_message(self, turn: int, speaker: str, content: str, action: str, reason: str, expected: str):
        """Display a single message with moderation results."""
        # Determine action emoji and color
        if action == 'block':
            action_emoji = "🚫"
            action_color = "RED"
        elif action == 'warn':
            action_emoji = "⚠️"
            action_color = "YELLOW"
        else:
            action_emoji = "✅"
            action_color = "GREEN"
        
        # Format speaker label
        speaker_label = f"[{speaker.upper()}]" if speaker else "[UNKNOWN]"
        
        # Display message
        print(f"\n{action_emoji} Turn {turn:2d} {speaker_label}")
        print(f"   Content: {content}")
        print(f"   Action: {action_emoji} {action.upper()}")
        if reason and reason != "no match":
            print(f"   Reason: {reason}")
        if expected != action:
            print(f"   ⚠️ Expected: {expected.upper()}, Got: {action.upper()}")
    
    def print_summary(self, results: Dict):
        """Print overall test summary."""
        total = results['total_messages']
        blocked = results['blocked_messages']
        warned = results['warned_messages']
        allowed = results['allowed_messages']
        
        print(f"\n{'='*60}")
        print(f"INTEGRATION TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total Messages: {total}")
        print(f"✅ Allowed: {allowed} ({allowed/total*100:.1f}%)")
        print(f"⚠️ Warned: {warned} ({warned/total*100:.1f}%)")
        print(f"🚫 Blocked: {blocked} ({blocked/total*100:.1f}%)")
        
        # Conversation breakdown
        print(f"\nConversation Breakdown:")
        for conv_id, conv_data in results['conversations'].items():
            conv_total = len(conv_data['messages'])
            print(f"  {conv_id}: {conv_data['allowed_count']}✅ {conv_data['warned_count']}⚠️ {conv_data['blocked_count']}🚫")

    async def print_transcript(self, test_cases: List[dict]):
        """Print the entire conversation as a transcript with inline moderation tags."""
        conversations = defaultdict(list)
        for case in test_cases:
            conv_id = case.get('conversation_id', 'unknown')
            conversations[conv_id].append(case)
        print("\n==================== TRANSCRIPT MODE ====================")
        for conv_id, messages in conversations.items():
            print(f"\n--- Conversation: {conv_id} ---")
            for i, case in enumerate(messages, 1):
                speaker = case.get('speaker', 'unknown')
                turn = case.get('turn', i)
                test_input = case.get('input')
                expected = case.get('expected')
                # Run moderation
                try:
                    result = await self.pipeline.check_input_async(test_input)
                    # Convert PipelineResult to action string
                    if result['blocked']:
                        action = 'block'
                    elif result['warnings']:
                        action = 'warn'
                    else:
                        action = 'allow'
                except Exception as e:
                    action = "error"
                tag = {
                    'block': '[BLOCKED]',
                    'warn': '[WARNED]',
                    'allow': '[ALLOWED]',
                    'error': '[ERROR]'
                }.get(action, '[UNKNOWN]')
                print(f"{turn:2d}. {speaker.title()}: {test_input} {tag}")
            print("")

async def run_customer_service_test(show_conversation: bool = True):
    """Run customer service bot integration test."""
    print("🤖 CUSTOMER SERVICE BOT INTEGRATION TEST")
    print("=" * 60)
    
    simulator = ConversationSimulator('../src/scenarios/customer_service/config.yaml')
    test_cases = load_jsonl('test_corpus/customer_service_bot.jsonl')
    
    if not test_cases:
        print("❌ No test cases found!")
        return False
    
    results = await simulator.simulate_conversation(test_cases, show_conversation)
    simulator.print_summary(results)
    
    return True

async def run_medical_bot_test(show_conversation: bool = True):
    """Run medical bot integration test."""
    print("🏥 MEDICAL BOT INTEGRATION TEST")
    print("=" * 60)
    
    simulator = ConversationSimulator('../src/scenarios/medical_bot/config.yaml')
    test_cases = load_jsonl('test_corpus/medical_bot.jsonl')
    
    if not test_cases:
        print("❌ No test cases found!")
        return False
    
    results = await simulator.simulate_conversation(test_cases, show_conversation)
    simulator.print_summary(results)
    
    return True

async def main():
    """Main test runner with options."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Integration Test Runner')
    parser.add_argument('--test', choices=['customer', 'medical', 'all'], default='all',
                       help='Which test to run')
    parser.add_argument('--quiet', action='store_true',
                       help='Run without showing conversation details')
    parser.add_argument('--transcript', action='store_true',
                       help='Show transcript view with inline moderation tags')
    
    args = parser.parse_args()
    
    show_conversation = not args.quiet
    
    if args.test == 'customer' or args.test == 'all':
        simulator = ConversationSimulator('../src/scenarios/customer_service/config.yaml')
        test_cases = load_jsonl('test_corpus/customer_service_bot.jsonl')
        if args.transcript:
            await simulator.print_transcript(test_cases)
        else:
            await run_customer_service_test(show_conversation)
    
    if args.test == 'medical' or args.test == 'all':
        simulator = ConversationSimulator('../src/scenarios/medical_bot/config.yaml')
        test_cases = load_jsonl('test_corpus/medical_bot.jsonl')
        if args.transcript:
            await simulator.print_transcript(test_cases)
        else:
            await run_medical_bot_test(show_conversation)

if __name__ == "__main__":
    asyncio.run(main()) 