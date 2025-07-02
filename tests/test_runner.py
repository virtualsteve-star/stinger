import json
import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.stinger.core.config import ConfigLoader
from src.stinger.core.pipeline import GuardrailPipeline
from src.stinger.guardrails.pass_through import PassThroughGuardrail
from src.stinger.guardrails.keyword_block import KeywordBlockGuardrail
from src.stinger.guardrails.regex_guardrail import RegexGuardrail
from src.stinger.guardrails.length_guardrail import LengthGuardrail
from src.stinger.guardrails.url_guardrail import URLGuardrail


def load_jsonl(path):
    with open(path, "r") as f:
        return [json.loads(line) for line in f if line.strip()]


GUARDRAIL_REGISTRY = {
    "pass_through": PassThroughGuardrail,
    "keyword_block": KeywordBlockGuardrail,
    "regex_filter": RegexGuardrail,
    "length_filter": LengthGuardrail,
    "url_filter": URLGuardrail,
}


async def run_smoke_test():
    """Run smoke test with pass-through filter."""
    print("🚀 Starting smoke test...")

    # Create pipeline from config
    pipeline = GuardrailPipeline("tests/configs/minimal.yaml")
    print("✅ Pipeline created")

    # Load test cases from JSONL
    test_cases = load_jsonl("tests/test_corpus/smoke_test.jsonl")

    passed = 0
    total = len(test_cases)

    for i, case in enumerate(test_cases, 1):
        test_input = case.get("input")
        expected = case.get("expected")
        try:
            result = await pipeline.check_input_async(test_input)
            # Convert PipelineResult to action string
            if result["blocked"]:
                action = "block"
            elif result["warnings"]:
                action = "warn"
            else:
                action = "allow"

            if action == expected:
                print(
                    f"✅ Test {i}: PASS - '{str(test_input)[:20]}...' ({case.get('description')})"
                )
                passed += 1
            else:
                print(
                    f"❌ Test {i}: FAIL - '{str(test_input)[:20]}...' -> {action} (expected {expected})"
                )
        except Exception as e:
            print(f"❌ Test {i}: ERROR - '{str(test_input)[:20]}...' -> {str(e)}")

    print(f"\n📊 Results: {passed}/{total} tests passed")
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_smoke_test())
    if success:
        print("🎉 All smoke tests passed!")
        sys.exit(0)
    else:
        print("💥 Some tests failed!")
        sys.exit(1)
