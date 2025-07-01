import json
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.stinger.core.config import ConfigLoader
from src.stinger.core.pipeline import GuardrailPipeline
from src.stinger.guardrails.pass_through import PassThroughGuardrail
from src.stinger.guardrails.keyword_block import KeywordBlockGuardrail
from src.stinger.guardrails.regex_guardrail import RegexGuardrail
from src.stinger.guardrails.length_guardrail import LengthGuardrail
from src.stinger.guardrails.url_guardrail import URLGuardrail

def load_jsonl(path):
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

async def run_test_suite(config_path: str, test_corpus_path: str, suite_name: str):
    """Run a specific test suite with given configuration and corpus."""
    print(f"\n🧪 Running {suite_name} test suite...")
    
    # Load configuration
    config_loader = ConfigLoader()
    config = config_loader.load(config_path)
    print(f"✅ Configuration loaded: {config_path}")
    
    # Create filters from config
    filter_configs = config_loader.get_pipeline_config('input')
    guardrails = []
    for fc in filter_configs:
        guardrail_type = fc.get('type')
        filter_cls = GUARDRAIL_REGISTRY.get(guardrail_type)
        if filter_cls:
            try:
                filters.append(filter_cls(fc))
                print(f"✅ Created filter: {fc.get('name')} ({guardrail_type})")
            except Exception as e:
                print(f"❌ Failed to create filter {fc.get('name')}: {str(e)}")
        else:
            print(f"⚠️ Unknown filter type: {guardrail_type}, skipping.")
    
    if not guardrails:
        print("❌ No valid filters created!")
        return False
    
    # Create pipeline
    pipeline = GuardrailPipeline(filters)
    print(f"✅ Pipeline created with {len(filters)} filters")
    
    # Load test cases
    test_cases = load_jsonl(test_corpus_path)
    if not test_cases:
        print("❌ No test cases found!")
        return False
    
    # Run tests
    passed = 0
    total = len(test_cases)
    
    for i, case in enumerate(test_cases, 1):
        test_input = case.get('input')
        expected = case.get('expected')
        description = case.get('description', 'No description')
        
        try:
            result = await pipeline.process(test_input)
            if result.blocked == expected:
                print(f"✅ Test {i:2d}: PASS - {description}")
                passed += 1
            else:
                print(f"❌ Test {i:2d}: FAIL - {description}")
                print(f"   Expected: {expected}, Got: {result.blocked}")
                print(f"   Reason: {result.reason}")
        except Exception as e:
            print(f"💥 Test {i:2d}: ERROR - {description}")
            print(f"   Error: {str(e)}")
    
    print(f"\n📊 {suite_name} Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    return passed == total

async def main():
    """Run all Classic Filter Pipeline test suites."""
    print("🚀 Starting Classic Filter Pipeline Test Suite")
    print("=" * 50)
    
    # Test suites to run
    test_suites = [
        {
            'name': 'Smoke Test (Original)',
            'config': 'tests/configs/minimal.yaml',
            'corpus': 'tests/test_corpus/smoke_test.jsonl'
        },
        {
            'name': 'Regex Filter Test',
            'config': 'tests/configs/comprehensive.yaml',
            'corpus': 'tests/test_corpus/regex_test.jsonl'
        },
        {
            'name': 'URL Filter Test',
            'config': 'tests/configs/comprehensive.yaml',
            'corpus': 'tests/test_corpus/url_test.jsonl'
        }
    ]
    
    all_passed = True
    total_tests = 0
    total_passed = 0
    
    for suite in test_suites:
        success = await run_test_suite(
            suite['config'],
            suite['corpus'],
            suite['name']
        )
        if not success:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All Classic Filter Pipeline test suites passed!")
        sys.exit(0)
    else:
        print("💥 Some test suites failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 