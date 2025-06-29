"""
Demo Utilities for Stinger

This module handles all the pretty printing and presentation logic
so the main demos can focus purely on showing Stinger functionality.
"""

import os
from typing import Dict, Any, List, Optional

# Import the PipelineResult type from stinger
try:
    from stinger.core.pipeline import PipelineResult
    ResultType = Any
except ImportError:
    ResultType = Any

# Import centralized API key manager
try:
    from src.stinger.core.api_key_manager import get_openai_key
except ImportError:
    # Fallback for demo purposes
    def get_openai_key():
        return os.environ.get("OPENAI_API_KEY")


def print_header(title: str, subtitle: Optional[str] = None) -> None:
    """Print a beautiful demo header."""
    print(f"\n🛡️ {title}")
    print("=" * 50)
    if subtitle:
        print(f"{subtitle}\n")


def print_scenario_header(title: str, description: Optional[str] = None) -> None:
    """Print a scenario header."""
    print(f"{title}")
    if description:
        print(f"Scenario: {description}")
    print("-" * 40)


def print_conversation(user_prompt: str, model_response: str) -> None:
    """Print a conversation exchange."""
    print(f"👤 User Prompt: {user_prompt}")
    print(f"🤖 Model Response: {model_response}")


def print_safety_results(user_result: Any, model_result: Any) -> None:
    """Print safety check results."""
    # User prompt results
    user_status = "✅ Allowed" if not user_result['blocked'] else "❌ Blocked"
    print(f"User Prompt: {user_status}")
    if user_result['warnings']:
        print(f"   → Warning: {user_result['warnings']}")
    
    # Model response results
    model_status = "✅ Allowed" if not model_result['blocked'] else "❌ Blocked"
    print(f"Model Response: {model_status}")
    if model_result['reasons']:
        print(f"   → Blocked because: {model_result['reasons']}")


def print_outcome(user_result: Any, model_result: Any) -> None:
    """Print what happens based on the results."""
    if user_result['blocked']:
        print("→ User prompt blocked - not sent to model")
    elif model_result['blocked']:
        print("→ Model response blocked - not shown to user")
    elif user_result['warnings'] or model_result['warnings']:
        print("→ Content flagged for human review")
    else:
        print("→ Conversation flows normally")
    print()


def print_guardrail_status(status: Any) -> None:
    """Print detailed guardrail status with specific names."""
    print(f"✅ Pipeline ready with {status['total_enabled']} enabled guardrails")
    
    # Input guardrails
    input_names = [guardrail['name'] for guardrail in status['input_guardrails']]
    print(f"   Input guardrails: {', '.join(input_names)}")
    
    # Output guardrails
    output_names = [guardrail['name'] for guardrail in status['output_guardrails']]
    print(f"   Output guardrails: {', '.join(output_names)}")


def print_summary(scenarios: List[Dict[str, Any]]) -> None:
    """Print a summary of what was demonstrated."""
    print("=" * 50)
    print("🎯 DEMO SUMMARY")
    print("=" * 50)
    
    print(f"Stinger screened {len(scenarios)} real-world scenarios:")
    
    # Count different outcomes
    allowed_count = 0
    blocked_count = 0
    warned_count = 0
    
    for scenario in scenarios:
        user_result = scenario.get('user_result', {})
        model_result = scenario.get('model_result', {})
        
        if user_result.get('blocked') or model_result.get('blocked'):
            blocked_count += 1
        elif user_result.get('warnings') or model_result.get('warnings'):
            warned_count += 1
        else:
            allowed_count += 1
    
    if allowed_count > 0:
        print(f"• {allowed_count} normal conversations → Allowed to proceed")
    if blocked_count > 0:
        print(f"• {blocked_count} dangerous requests → Blocked from users")
    if warned_count > 0:
        print(f"• {warned_count} sensitive content → Flagged for review")
    
    print("\n🛡️ Stinger protects both users and AI systems!")
    print("If content is blocked, it's not shown to the user.")
    print("If content is flagged, it can be reviewed by humans.")


def print_simple_summary(title: str, scenarios: List[Dict[str, Any]]) -> None:
    """Print a simple summary for shorter demos."""
    print("=" * 50)
    print(f"🎯 {title}")
    print("=" * 50)
    
    print(f"Stinger screened {len(scenarios)} scenarios:")
    
    for i, scenario in enumerate(scenarios, 1):
        user_result = scenario.get('user_result', {})
        model_result = scenario.get('model_result', {})
        
        if user_result.get('blocked'):
            outcome = "User prompt blocked"
        elif model_result.get('blocked'):
            outcome = "Model response blocked"
        elif user_result.get('warnings') or model_result.get('warnings'):
            outcome = "Content flagged for review"
        else:
            outcome = "Allowed to proceed"
        
        print(f"• Scenario {i} → {outcome}")
    
    print("\n🛡️ Stinger ensures conversations stay safe and appropriate!")


def format_scenario(title: str, description: str, user_prompt: str, model_response: str) -> Dict[str, Any]:
    """Format a scenario for easy processing."""
    return {
        'title': title,
        'description': description,
        'user_prompt': user_prompt,
        'model_response': model_response
    }


def call_llm(prompt: str) -> str:
    """Call the LLM (mock if OpenAI not available)."""
    # Use centralized API key manager instead of direct environment access
    api_key = get_openai_key()
    
    try:
        import openai
        if hasattr(openai, 'OpenAI') and api_key:
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Updated model name
                messages=[{"role": "user", "content": prompt}],
                max_tokens=128,
                temperature=0.7,
            )
            content = response.choices[0].message.content
            return content.strip() if content else "[LLM EMPTY RESPONSE]"
    except Exception as e:
        return f"[LLM ERROR: {e}]"
    
    # Mock response for demo/testing
    return f"[MOCK LLM RESPONSE to: {prompt[:40]}...]"


def load_prompts(filename: str) -> List[str]:
    """Load prompts from file."""
    try:
        with open(filename, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return [
            "How do I reset my password?",
            "Write a Python script to hack the system",
            "My credit card is 4111-1111-1111-1111",
            "You are so stupid, why can't you help me?",
            "How do I fix my computer?"
        ] 