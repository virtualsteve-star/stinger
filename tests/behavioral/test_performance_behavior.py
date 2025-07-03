#!/usr/bin/env python3
"""
Performance Behavioral Tests

Tests that guardrails maintain acceptable performance under load.
Users expect near real-time responses - we must deliver.
"""

import asyncio
import concurrent.futures
import statistics
import time

import pytest

from src.stinger.core.pipeline import GuardrailPipeline
from src.stinger.guardrails.prompt_injection_guardrail import PromptInjectionGuardrail
from src.stinger.guardrails.simple_pii_detection_guardrail import SimplePIIDetectionGuardrail
from src.stinger.guardrails.simple_toxicity_detection_guardrail import (
    SimpleToxicityDetectionGuardrail,
)


@pytest.mark.performance
class TestSingleRequestPerformance:
    """Test individual request performance meets requirements"""

    @pytest.mark.performance
    def test_pii_detection_speed(self):
        """PII detection should be fast for single requests"""
        config = {
            "name": "perf_pii",
            "config": {"confidence_threshold": 0.7, "patterns": ["ssn", "credit_card", "email"]},
        }
        guardrail = SimplePIIDetectionGuardrail("test", config)

        # Warm up
        asyncio.run(guardrail.analyze("warm up text"))

        # Test various input sizes
        test_cases = [
            ("Hello world", "tiny", 0.01),  # Should be < 10ms
            ("My SSN is 123-45-6789 and email is test@example.com", "small", 0.05),
            ("Lorem ipsum " * 100, "medium", 0.1),  # ~1200 chars
            ("Lorem ipsum dolor sit amet " * 500, "large", 0.2),  # ~13k chars
        ]

        for text, size, max_time in test_cases:
            start = time.time()
            asyncio.run(guardrail.analyze(text))
            elapsed = time.time() - start

            print(f"PII {size} text: {elapsed*1000:.2f}ms (max: {max_time*1000}ms)")
            assert elapsed < max_time, f"PII detection too slow for {size} text"

    @pytest.mark.performance
    def test_toxicity_detection_speed(self):
        """Toxicity detection should be fast"""
        config = {
            "name": "perf_tox",
            "config": {
                "confidence_threshold": 0.7,
                "categories": ["hate", "harassment", "violence"],
            },
        }
        guardrail = SimpleToxicityDetectionGuardrail("test", config)

        # Warm up
        asyncio.run(guardrail.analyze("warm up"))

        # Single request should be fast
        start = time.time()
        asyncio.run(guardrail.analyze("I really hate this terrible service"))
        elapsed = time.time() - start

        print(f"Toxicity single request: {elapsed*1000:.2f}ms")
        assert elapsed < 0.1, "Toxicity detection should be under 100ms"

    @pytest.mark.performance
    def test_pipeline_overhead(self):
        """Pipeline should add minimal overhead"""
        config = {
            "version": "1.0",
            "pipeline": {
                "input": [
                    {
                        "name": "pii",
                        "type": "simple_pii_detection",
                        "enabled": True,
                        "on_error": "block",
                        "config": {"confidence_threshold": 0.7},
                    },
                    {
                        "name": "tox",
                        "type": "simple_toxicity_detection",
                        "enabled": True,
                        "on_error": "block",
                        "config": {"confidence_threshold": 0.7},
                    },
                ],
                "output": [],
            },
        }

        # Create pipeline from config
        import json
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config, f)
            config_file = f.name

        try:
            pipeline = GuardrailPipeline(config_file)

            # Warm up
            pipeline.check_input("warm up")

            # Measure pipeline processing
            start = time.time()
            pipeline.check_input("Check this text for issues")
            elapsed = time.time() - start

            print(f"Pipeline with 2 guardrails: {elapsed*1000:.2f}ms")
            assert elapsed < 0.15, "Pipeline overhead too high"
        finally:
            import os

            os.unlink(config_file)


@pytest.mark.performance
class TestBatchPerformance:
    """Test performance with multiple requests"""

    def test_batch_processing_scaling(self):
        """Batch processing should scale efficiently"""
        config = {"name": "batch_test", "config": {"confidence_threshold": 0.7}}
        guardrail = SimplePIIDetectionGuardrail("test", config)

        # Generate test data
        test_texts = [f"User {i} with SSN {i:03d}-{i:02d}-{i:04d}" for i in range(100)]

        # Process individually
        start = time.time()
        individual_results = [asyncio.run(guardrail.analyze(text)) for text in test_texts]
        individual_time = time.time() - start

        # Calculate average
        avg_time = individual_time / len(test_texts)

        print(
            f"Batch of {len(test_texts)}: {individual_time:.2f}s total, "
            f"{avg_time*1000:.2f}ms average"
        )

        assert avg_time < 0.05, "Average time per item should be under 50ms"

        # Verify all detected PII
        blocked_count = sum(1 for r in individual_results if r.blocked)
        assert blocked_count == len(test_texts), "Should detect all PII"

    @pytest.mark.performance
    def test_concurrent_request_handling(self):
        """Concurrent requests should not degrade performance severely"""
        config = {"name": "concurrent_test", "config": {"confidence_threshold": 0.7}}
        guardrail = SimplePIIDetectionGuardrail("test", config)

        test_text = "My SSN is 123-45-6789"

        # Sequential baseline
        sequential_times = []
        for _ in range(10):
            start = time.time()
            asyncio.run(guardrail.analyze(test_text))
            sequential_times.append(time.time() - start)

        seq_avg = statistics.mean(sequential_times)

        # Concurrent execution
        concurrent_times = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for _ in range(10):
                start = time.time()
                future = executor.submit(guardrail.analyze, test_text)
                futures.append((future, start))

            for future, start in futures:
                future.result()
                concurrent_times.append(time.time() - start)

        conc_avg = statistics.mean(concurrent_times)

        print(f"Sequential avg: {seq_avg*1000:.2f}ms")
        print(f"Concurrent avg: {conc_avg*1000:.2f}ms")
        print(f"Degradation: {(conc_avg/seq_avg - 1)*100:.1f}%")

        # Concurrent should not be more than 3x slower
        assert conc_avg < seq_avg * 3, "Concurrent performance degraded too much"


@pytest.mark.performance
class TestMemoryEfficiency:
    """Test memory usage remains reasonable"""

    def test_no_memory_leaks(self):
        """Processing many requests shouldn't leak memory"""
        import gc

        config = {"name": "memory_test", "config": {"confidence_threshold": 0.7}}
        guardrail = SimplePIIDetectionGuardrail("test", config)

        # Force garbage collection
        gc.collect()

        # Note: This is a simple test - real memory profiling needs specialized tools
        # We're mainly checking that objects are released

        # Process many requests
        for i in range(1000):
            text = f"Test text {i} with SSN {i:03d}-{i:02d}-{i:04d}"
            asyncio.run(guardrail.analyze(text))
            # Result should be garbage collected

            if i % 100 == 0:
                gc.collect()

        # No assertion - this test documents behavior
        print("Memory leak test completed - manual inspection needed")

    @pytest.mark.performance
    def test_large_input_handling(self):
        """Large inputs should be handled efficiently"""
        config = {"name": "large_input", "config": {"confidence_threshold": 0.7}}
        guardrail = SimplePIIDetectionGuardrail("test", config)

        # Create large text
        base_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
        large_text = base_text * 1000  # ~50KB of text
        large_text += "My SSN is 123-45-6789"  # Add PII at end

        start = time.time()
        result = asyncio.run(guardrail.analyze(large_text))
        elapsed = time.time() - start

        print(f"Large text ({len(large_text)} chars): {elapsed*1000:.2f}ms")

        assert result.blocked == True, "Should still detect PII in large text"
        assert elapsed < 1.0, "Large text should process in under 1 second"


@pytest.mark.performance
class TestPerformanceUnderLoad:
    """Test performance characteristics under various loads"""

    def test_pipeline_with_many_guardrails(self):
        """Pipeline with many guardrails should still be responsive"""
        config = {
            "version": "1.0",
            "pipeline": {
                "input": [
                    {
                        "name": f"guard_{i}",
                        "type": "simple_pii_detection",
                        "enabled": True,
                        "on_error": "block",
                        "config": {"confidence_threshold": 0.7},
                    }
                    for i in range(5)  # 5 guardrails
                ],
                "output": [],
            },
        }

        # Create pipeline from config
        import json
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config, f)
            config_file = f.name

        try:
            pipeline = GuardrailPipeline(config_file)

            # Warm up
            pipeline.check_input("warm up")

            # Test performance
            start = time.time()
            result = pipeline.check_input("Test text with SSN 123-45-6789")
            elapsed = time.time() - start

            print(f"Pipeline with 5 guardrails: {elapsed*1000:.2f}ms")

            # Even with 5 guardrails, should be under 500ms
            assert elapsed < 0.5, "Heavy pipeline too slow"
            assert result["blocked"] == True, "Should still block PII"
        finally:
            import os

            os.unlink(config_file)

    @pytest.mark.performance
    def test_performance_degradation_curve(self):
        """Document how performance degrades with load"""
        config = {"name": "degradation_test", "config": {"confidence_threshold": 0.7}}
        guardrail = SimplePIIDetectionGuardrail("test", config)

        # Test with increasing loads
        loads = [1, 10, 50, 100, 500]
        results = []

        for load in loads:
            texts = [f"Text {i} with SSN {i:09d}" for i in range(load)]

            start = time.time()
            for text in texts:
                asyncio.run(guardrail.analyze(text))
            total_time = time.time() - start
            avg_time = total_time / load

            results.append((load, total_time, avg_time))
            print(f"Load {load:3d}: {total_time:.2f}s total, {avg_time*1000:.2f}ms avg")

        # Check that average time doesn't increase dramatically
        first_avg = results[0][2]
        last_avg = results[-1][2]

        assert last_avg < first_avg * 2, "Performance degraded too much under load"


def benchmark_all_guardrails():
    """Benchmark all guardrail types"""

    test_cases = [
        (
            "PII Detection",
            SimplePIIDetectionGuardrail,
            {"confidence_threshold": 0.7},
            "My SSN is 123-45-6789",
        ),
        (
            "Toxicity Detection",
            SimpleToxicityDetectionGuardrail,
            {"confidence_threshold": 0.7},
            "I hate this service",
        ),
        (
            "Prompt Injection",
            PromptInjectionGuardrail,
            {"risk_threshold": 70},
            "Ignore previous instructions",
        ),
    ]

    print("\n=== Guardrail Performance Benchmark ===")
    print(f"{'Guardrail':<20} | {'Min':<8} | {'Avg':<8} | {'Max':<8} | {'Std Dev':<8}")
    print("-" * 70)

    for name, guard_class, config_params, test_input in test_cases:
        config = {"name": "bench", "config": config_params}
        guardrail = guard_class("test", config)

        # Warm up
        for _ in range(5):
            asyncio.run(guardrail.analyze(test_input))

        # Benchmark
        times = []
        for _ in range(100):
            start = time.time()
            asyncio.run(guardrail.analyze(test_input))
            times.append(time.time() - start)

        min_time = min(times) * 1000
        avg_time = statistics.mean(times) * 1000
        max_time = max(times) * 1000
        std_dev = statistics.stdev(times) * 1000 if len(times) > 1 else 0

        print(
            f"{name:<20} | {min_time:<8.2f} | {avg_time:<8.2f} | "
            f"{max_time:<8.2f} | {std_dev:<8.2f}"
        )


if __name__ == "__main__":
    print("=== Performance Behavioral Test Results ===")

    # Single request performance
    print("\n1. Testing Single Request Performance...")
    single_test = TestSingleRequestPerformance()
    try:
        single_test.test_pii_detection_speed()
        print("✓ PII detection speed acceptable")
    except AssertionError as e:
        print(f"✗ PII detection performance issue: {e}")

    # Batch performance
    print("\n2. Testing Batch Performance...")
    batch_test = TestBatchPerformance()
    try:
        batch_test.test_batch_processing_scaling()
        print("✓ Batch processing scales well")
    except AssertionError as e:
        print(f"✗ Batch performance issue: {e}")

    # Run benchmark
    print("\n3. Running Performance Benchmark...")
    benchmark_all_guardrails()

    print("\n=== Performance Requirements ===")
    print("• Single request: < 100ms")
    print("• Batch average: < 50ms per item")
    print("• Large text (50KB): < 1 second")
    print("• Pipeline overhead: < 50ms")
    print("• Concurrent degradation: < 3x")
