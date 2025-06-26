"""
Tech Support Demo - Interactive LLM Screening

This demo shows Stinger screening real LLM conversations.
Uses demo_utils for all boilerplate - focuses purely on Stinger functionality.
"""

import sys
import time
from pathlib import Path

# Add src directory to path so we can import stinger
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from stinger import GuardrailPipeline
from demo_utils import (
    print_header, call_llm, load_prompts,
    print_conversation, print_safety_results, print_outcome, print_guardrail_status
)

# Configuration
PROMPTS_FILE = Path(__file__).parent / 'prompts.txt'
CONFIG_FILE = Path(__file__).parent / 'config.yaml'


def main():
    """Main demo function - screens real LLM conversations."""
    # Print header
    print_header("STINGER: Interactive LLM Screening", 
                "Watch Stinger screen real AI conversations...")
    
    # Load prompts
    prompts = load_prompts(str(PROMPTS_FILE))
    print(f"📋 Loaded {len(prompts)} test prompts")
    
    # Initialize guardrail pipeline
    print("🔧 Initializing guardrail pipeline...")
    pipeline = GuardrailPipeline(str(CONFIG_FILE))
    
    # Show pipeline status with detailed guardrail names
    status = pipeline.get_guardrail_status()
    print_guardrail_status(status)
    print()
    
    # Process each prompt
    summary = {"PASS": 0, "BLOCK": 0, "WARN": 0}
    
    for idx, prompt in enumerate(prompts, 1):
        print(f"📝 PROMPT #{idx}")
        print("=" * 50)
        
        # Check input
        prompt_result = pipeline.check_input(prompt)
        
        # Generate response if input passes
        if prompt_result['blocked']:
            response = "[INPUT BLOCKED BY GUARDRAILS]"
            response_result = {'blocked': False, 'warnings': [], 'reasons': []}
        else:
            response = call_llm(prompt)
            response_result = pipeline.check_output(response)
        
        # Show conversation and results
        print_conversation(prompt, response)
        print_safety_results(prompt_result, response_result)
        print_outcome(prompt_result, response_result)
        
        # Update summary
        if prompt_result['blocked'] or response_result['blocked']:
            summary['BLOCK'] += 1
        elif prompt_result['warnings'] or response_result['warnings']:
            summary['WARN'] += 1
        else:
            summary['PASS'] += 1
        
        time.sleep(0.1)  # For readability
    
    # Final summary
    print("=" * 50)
    print("📊 FINAL SUMMARY")
    print("=" * 50)
    print(f"📝 Total prompts processed: {len(prompts)}")
    print(f"✅ Passed: {summary['PASS']}")
    print(f"⚠️  Warnings: {summary['WARN']}")
    print(f"❌ Blocked: {summary['BLOCK']}")
    print(f"\n🎉 Demo complete! Guardrails are working perfectly! 🎉")


if __name__ == "__main__":
    main() 