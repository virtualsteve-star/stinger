import os
import time
from pathlib import Path

from stinger.core.config import ConfigLoader
from stinger.core.guardrail_interface import GuardrailFactory, GuardrailRegistry

try:
    import openai
    # Try to use v1+ client if available
    if hasattr(openai, 'OpenAI'):
        OpenAIClient = openai.OpenAI
    else:
        OpenAIClient = None
except ImportError:
    openai = None
    OpenAIClient = None

PROMPTS_FILE = Path(__file__).parent / 'prompts.txt'
CONFIG_FILE = Path(__file__).parent / 'config.yaml'

# Load prompts from file
def load_prompts(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip()]

# Pretty print a result row
def print_result_row(idx, prompt, response, prompt_result, response_result):
    print(f"\n=== Prompt #{idx+1} ===")
    print(f"Prompt:   {prompt}")
    print(f"Prompt Guardrail:   {prompt_result['status']} | {prompt_result['reasons']}")
    print(f"Response: {response}")
    print(f"Response Guardrail: {response_result['status']} | {response_result['reasons']}")
    print("-")

# Run guardrail pipeline for a message (input or output)
def run_guardrails(factory, pipeline, message):
    reasons = []
    status = "PASS"
    for guardrail in pipeline:
        if guardrail is None:
            raise RuntimeError("A guardrail in the pipeline was not created. Check your config and factory registration.")
        result = guardrail.analyze(message)
        if hasattr(result, 'blocked') and result.blocked:
            status = "FAIL"
            reasons.append(result.reason)
        elif hasattr(result, 'warned') and result.warned:
            if status != "FAIL":
                status = "WARN"
            reasons.append(result.reason)
    return {"status": status, "reasons": "; ".join(reasons) if reasons else "-"}

# Call the LLM (mock if openai not available)
def call_llm(prompt):
    api_key = os.environ.get("OPENAI_API_KEY")
    if OpenAIClient and api_key:
        client = OpenAIClient(api_key=api_key)
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=128,
                temperature=0.7,
            )
            content = response.choices[0].message.content
            return content.strip() if content else "[LLM EMPTY RESPONSE]"
        except Exception as e:
            return f"[LLM ERROR: {e}]"
    else:
        # Mock response for demo/testing
        return f"[MOCK LLM RESPONSE to: {prompt[:40]}...]"

# Main demo logic
def main():
    print("\n=== Tech Support Demo: Guardrail Screening ===\n")
    prompts = load_prompts(PROMPTS_FILE)
    config_loader = ConfigLoader()
    config = config_loader.load(str(CONFIG_FILE))
    registry = GuardrailRegistry()
    factory = GuardrailFactory(registry)
    # Register all factories (if needed)
    from stinger.core.guardrail_factory import register_all_factories
    register_all_factories(registry)
    # Build input and output pipelines
    print("Input pipeline configs:", config['pipeline']['input'])
    input_pipeline = []
    for f in config['pipeline']['input']:
        print("Creating input guardrail for config:", f)
        guardrail = factory.create_from_config(f)
        print("Resulting guardrail:", guardrail)
        input_pipeline.append(guardrail)
    print("Output pipeline configs:", config['pipeline']['output'])
    output_pipeline = []
    for f in config['pipeline']['output']:
        print("Creating output guardrail for config:", f)
        guardrail = factory.create_from_config(f)
        print("Resulting guardrail:", guardrail)
        output_pipeline.append(guardrail)

    summary = {"PASS": 0, "FAIL": 0, "WARN": 0}
    for idx, prompt in enumerate(prompts):
        prompt_result = run_guardrails(factory, input_pipeline, prompt)
        if prompt_result["status"] == "FAIL":
            response = "[Prompt blocked by guardrails]"
        else:
            response = call_llm(prompt)
        response_result = run_guardrails(factory, output_pipeline, response)
        print_result_row(idx, prompt, response, prompt_result, response_result)
        # Tally summary
        for status in [prompt_result["status"], response_result["status"]]:
            summary[status] += 1
        time.sleep(0.1)  # For readability

    print("\n=== Summary ===")
    print(f"Total prompts: {len(prompts)}")
    print(f"PASS: {summary['PASS']} | WARN: {summary['WARN']} | FAIL: {summary['FAIL']}")
    print("\nDemo complete.")

if __name__ == "__main__":
    main() 