import json
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.config import ConfigLoader
from src.core.pipeline import FilterPipeline
from src.filters.pass_through import PassThroughFilter
from src.filters.keyword_block import KeywordBlockFilter

def load_jsonl(path):
    with open(path, 'r') as f:
        return [json.loads(line) for line in f if line.strip()]

FILTER_REGISTRY = {
    'pass_through': PassThroughFilter,
    'keyword_block': KeywordBlockFilter,
}

async def run_smoke_test():
    """Run smoke test with pass-through filter."""
    print("🚀 Starting smoke test...")
    
    # Load configuration
    config_loader = ConfigLoader()
    config = config_loader.load('configs/minimal.yaml')
    print("✅ Configuration loaded")
    
    # Create filters from config
    filter_configs = config_loader.get_pipeline_config('input')
    filters = []
    for fc in filter_configs:
        filter_type = fc.get('type')
        filter_cls = FILTER_REGISTRY.get(filter_type)
        if filter_cls:
            filters.append(filter_cls(fc))
        else:
            print(f"⚠️ Unknown filter type: {filter_type}, skipping.")
    print(f"✅ {len(filters)} filters created")
    
    # Create pipeline
    pipeline = FilterPipeline(filters)
    print("✅ Pipeline created")
    
    # Load test cases from JSONL
    test_cases = load_jsonl('tests/test_corpus/smoke_test.jsonl')
    
    passed = 0
    total = len(test_cases)
    
    for i, case in enumerate(test_cases, 1):
        test_input = case.get('input')
        expected = case.get('expected')
        try:
            result = await pipeline.process(test_input)
            if result.action == expected:
                print(f"✅ Test {i}: PASS - '{str(test_input)[:20]}...' ({case.get('description')})")
                passed += 1
            else:
                print(f"❌ Test {i}: FAIL - '{str(test_input)[:20]}...' -> {result.action} (expected {expected})")
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