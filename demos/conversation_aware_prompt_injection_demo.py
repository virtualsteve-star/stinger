"""
Conversation-Aware Prompt Injection Detection Demo

This demo showcases the enhanced prompt injection detection with conversation context,
demonstrating multi-turn pattern detection, context strategies, and real-world scenarios.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from stinger.guardrails.prompt_injection_filter import PromptInjectionGuardrail
from conversation_aware_prompt_injection_helpers import (
    get_demo_scenarios,
    print_conversation_summary,
    test_context_strategies,
    print_context_strategy_results,
    print_analysis_result
)


class ConversationAwarePromptInjectionDemo:
    """Demo class for conversation-aware prompt injection detection."""
    
    def __init__(self):
        """Initialize the demo with configuration."""
        self.config = {
            'enabled': True,
            'risk_threshold': 70,
            'block_levels': ['high', 'critical'],
            'warn_levels': ['medium'],
            'on_error': 'allow',
            'conversation_awareness': {
                'enabled': True,
                'context_strategy': 'mixed',
                'max_context_turns': 5,
                'max_context_tokens': 2000,
                'suspicious_indicators': [
                    'ignore', 'forget', 'pretend', 'trust', 'friend', 'you are', 'act as',
                    'bypass', 'safety', 'rules', 'jailbreak', 'system prompt', 'override'
                ]
            },
            'pattern_detection': {
                'trust_building_weight': 0.3,
                'role_playing_weight': 0.25,
                'context_manipulation_weight': 0.25,
                'instruction_evolution_weight': 0.2
            },
            'legacy_mode': False
        }
        
        self.filter = PromptInjectionGuardrail("demo_filter", self.config)
    
    async def run_scenario(self, scenario_name: str, factory_func):
        """Run a single demo scenario."""
        # Create conversation and injection prompt
        conversation, prompt = factory_func()
        
        # Print summary
        print_conversation_summary(conversation, prompt, scenario_name)
        
        # Test context strategies
        strategy_results = test_context_strategies(self.filter, conversation)
        print_context_strategy_results(strategy_results)
        
        # Analyze with conversation context
        try:
            result = await self.filter.analyze(prompt, conversation)
            print_analysis_result(result, scenario_name)
            return result
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    async def run_demo(self):
        """Run the complete demo."""
        print("CONVERSATION-AWARE PROMPT INJECTION DETECTION DEMO")
        print("="*60)
        print("Multi-turn pattern detection with context strategies")
        
        # Run all scenarios
        scenarios = get_demo_scenarios()
        results = []
        
        for scenario_name, factory_func in scenarios:
            result = await self.run_scenario(scenario_name, factory_func)
            results.append((scenario_name, result))
        
        # Summary
        print(f"\n{'='*20} SUMMARY {'='*20}")
        blocked_count = sum(1 for _, result in results if result and result.blocked)
        print(f"Scenarios: {len(scenarios)}")
        print(f"Blocked: {blocked_count}")
        print(f"Allowed: {len(scenarios) - blocked_count}")
        print("✓ Multi-turn pattern detection")
        print("✓ Context strategy selection")
        print("✓ Enhanced risk assessment")


async def main():
    """Main function to run the demo."""
    demo = ConversationAwarePromptInjectionDemo()
    await demo.run_demo()


if __name__ == "__main__":
    asyncio.run(main()) 