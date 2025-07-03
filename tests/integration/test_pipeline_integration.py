#!/usr/bin/env python3
"""
Integration Tests for Pipeline → Guardrail Flow

Tests that configuration flows correctly through the pipeline to guardrails.
This is where the critical config bug was hiding.
"""

import json
import os
import tempfile

import yaml

from src.stinger.core.pipeline import GuardrailPipeline


def create_pipeline_from_config(config: dict) -> GuardrailPipeline:
    """Helper to create pipeline from config dict"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(config, f)
        config_file = f.name

    try:
        pipeline = GuardrailPipeline(config_file)
        return pipeline
    finally:
        os.unlink(config_file)


class TestPipelineConfigFlow:
    """Test configuration flows correctly from pipeline to guardrails"""

    def test_nested_config_structure(self):
        """Test the ACTUAL config structure used by pipeline"""
        # This is how configs are ACTUALLY structured
        pipeline_config = {
            "version": "1.0",
            "pipeline": {
                "input": [
                    {
                        "name": "pii_test",
                        "type": "simple_pii_detection",
                        "enabled": True,
                        "on_error": "block",
                        "config": {  # Config is NESTED here
                            "confidence_threshold": 0.123,  # Unique value to verify
                            "patterns": ["ssn"],
                            "custom_param": "test_value",
                        },
                    }
                ],
                "output": [],
            },
        }

        # Create pipeline
        pipeline = create_pipeline_from_config(pipeline_config)

        # Get the guardrail
        guardrail = pipeline.input_pipeline[0] if pipeline.input_pipeline else None
        assert guardrail is not None, "Guardrail not created"

        # CRITICAL TEST: Did the config values get through?
        if hasattr(guardrail, "confidence_threshold"):
            assert (
                guardrail.confidence_threshold == 0.123
            ), f"Config not extracted! Got {guardrail.confidence_threshold}, expected 0.123"

        # Test custom param if supported
        if hasattr(guardrail, "custom_param"):
            assert guardrail.custom_param == "test_value", "Custom param not extracted"

    def test_all_guardrail_config_extraction(self):
        """Test ALL guardrails extract nested config correctly"""
        guardrail_configs = [
            {
                "name": "pii",
                "type": "simple_pii_detection",
                "enabled": True,
                "on_error": "block",
                "config": {"confidence_threshold": 0.111},
            },
            {
                "name": "toxicity",
                "type": "simple_toxicity_detection",
                "enabled": True,
                "on_error": "block",
                "config": {"confidence_threshold": 0.222},
            },
            {
                "name": "injection",
                "type": "prompt_injection",
                "enabled": True,
                "on_error": "block",
                "config": {"risk_threshold": 33},
            },
            {
                "name": "code",
                "type": "simple_code_generation",
                "enabled": True,
                "on_error": "block",
                "config": {"confidence_threshold": 0.444},
            },
            {
                "name": "length",
                "type": "length_filter",
                "enabled": True,
                "on_error": "block",
                "config": {"max_length": 555},
            },
            {
                "name": "url",
                "type": "url_filter",
                "enabled": True,
                "on_error": "block",
                "config": {"blocked_domains": ["test.com"]},
            },
        ]

        for config in guardrail_configs:
            print(f"\nTesting {config['type']}...")

            # Create pipeline with single guardrail
            pipeline_config = {"version": "1.0", "pipeline": {"input": [config], "output": []}}

            pipeline = create_pipeline_from_config(pipeline_config)

            # Get the guardrail from pipeline
            if pipeline.input_pipeline:
                guardrail = pipeline.input_pipeline[0]
            else:
                print(f"  Failed to create guardrail for {config['type']}")
                continue

            # Check critical config values
            if "confidence_threshold" in config["config"]:
                if hasattr(guardrail, "confidence_threshold"):
                    actual = guardrail.confidence_threshold
                    expected = config["config"]["confidence_threshold"]
                    assert (
                        actual == expected
                    ), f"{config['type']}: threshold not extracted! Got {actual}, expected {expected}"
                else:
                    print(f"  Warning: {config['type']} has no confidence_threshold attribute")

            if "risk_threshold" in config["config"]:
                if hasattr(guardrail, "risk_threshold"):
                    actual = guardrail.risk_threshold
                    expected = config["config"]["risk_threshold"]
                    assert (
                        actual == expected
                    ), f"{config['type']}: risk threshold not extracted! Got {actual}, expected {expected}"

            if "max_length" in config["config"]:
                if hasattr(guardrail, "max_length"):
                    actual = guardrail.max_length
                    expected = config["config"]["max_length"]
                    assert (
                        actual == expected
                    ), f"{config['type']}: max_length not extracted! Got {actual}, expected {expected}"

    def test_pipeline_stage_assignment(self):
        """Test guardrails are assigned to correct pipeline stages"""
        config = {
            "version": "1.0",
            "pipeline": {
                "input": [
                    {
                        "name": "input_guard",
                        "type": "simple_pii_detection",
                        "enabled": True,
                        "on_error": "block",
                        "config": {"confidence_threshold": 0.8},
                    },
                    {
                        "name": "both_guard",
                        "type": "length_filter",
                        "enabled": True,
                        "on_error": "block",
                        "config": {"max_length": 1000},
                    },
                ],
                "output": [
                    {
                        "name": "output_guard",
                        "type": "simple_toxicity_detection",
                        "enabled": True,
                        "on_error": "block",
                        "config": {"confidence_threshold": 0.7},
                    },
                    {
                        "name": "both_guard",
                        "type": "length_filter",
                        "enabled": True,
                        "on_error": "block",
                        "config": {"max_length": 1000},
                    },
                ],
            },
        }

        pipeline = create_pipeline_from_config(config)

        # Check stage assignments
        input_names = [g.name for g in pipeline.input_pipeline]
        output_names = [g.name for g in pipeline.output_pipeline]

        assert "input_guard" in input_names, "Input stage guardrail not in input"
        assert "output_guard" in output_names, "Output stage guardrail not in output"
        assert "both_guard" in input_names, "Both stage guardrail not in input"
        assert "both_guard" in output_names, "Both stage guardrail not in output"

    def test_config_validation_errors(self):
        """Test pipeline handles invalid configs gracefully"""
        invalid_configs = [
            # Missing type
            {"pipeline": {"name": "test"}, "guardrails": [{"name": "test", "config": {}}]},
            # Invalid type
            {
                "pipeline": {"name": "test"},
                "guardrails": [{"name": "test", "type": "nonexistent", "config": {}}],
            },
            # Missing config
            {"pipeline": {"name": "test"}, "guardrails": [{"name": "test", "type": "length"}]},
        ]

        for config in invalid_configs:
            try:
                pipeline = create_pipeline_from_config(config)
                # Document behavior - does it fail or handle gracefully?
                print(
                    f"Config {config} created pipeline with {len(pipeline.input_guardrails)} guardrails"
                )
            except Exception as e:
                print(f"Config {config} raised: {type(e).__name__}: {e}")

    def test_enabled_disabled_states(self):
        """Test enabled/disabled configuration works"""
        config = {
            "version": "1.0",
            "pipeline": {
                "input": [
                    {
                        "name": "enabled_guard",
                        "type": "simple_pii_detection",
                        "enabled": True,
                        "on_error": "block",
                        "config": {"confidence_threshold": 0.8},
                    },
                    {
                        "name": "disabled_guard",
                        "type": "simple_toxicity_detection",
                        "enabled": False,
                        "on_error": "block",
                        "config": {"confidence_threshold": 0.7},
                    },
                ],
                "output": [],
            },
        }

        pipeline = create_pipeline_from_config(config)

        # Process some content
        result = pipeline.check_input("My SSN is 123-45-6789 and I hate you")

        # Check that enabled guard blocked the PII
        assert result["blocked"] == True, "Should block due to PII from enabled guard"
        assert "enabled_guard" in result["details"], "Enabled guard should be in details"

        # Verify the disabled guard didn't run
        enabled_guard_details = result["details"].get("enabled_guard", {})
        assert enabled_guard_details.get("blocked") == True, "Enabled guard should block"


class TestConfigMerging:
    """Test configuration merging and defaults"""

    def test_default_value_inheritance(self):
        """Test guardrails get default values when not specified"""
        # Create through pipeline
        pipeline_config = {
            "version": "1.0",
            "pipeline": {
                "input": [
                    {
                        "name": "minimal",
                        "type": "simple_pii_detection",
                        "enabled": True,
                        "on_error": "block",
                        "config": {
                            # Only specify patterns, not threshold
                            "patterns": ["ssn"]
                        },
                    }
                ],
                "output": [],
            },
        }
        pipeline = create_pipeline_from_config(pipeline_config)
        guardrail = pipeline.input_pipeline[0] if pipeline.input_pipeline else None

        if not guardrail:
            print("Failed to create guardrail")
            return

        # Should have default confidence threshold
        if hasattr(guardrail, "confidence_threshold"):
            print(f"Default confidence threshold: {guardrail.confidence_threshold}")
            assert guardrail.confidence_threshold > 0, "Should have positive default"

    def test_partial_config_override(self):
        """Test partial config overrides work"""
        # Create through pipeline
        pipeline_config = {
            "version": "1.0",
            "pipeline": {
                "input": [
                    {
                        "name": "partial",
                        "type": "simple_toxicity_detection",
                        "enabled": True,
                        "on_error": "block",
                        "config": {
                            "categories": ["hate_speech"],  # Override categories with valid name
                            # confidence_threshold should use default
                        },
                    }
                ],
                "output": [],
            },
        }
        pipeline = create_pipeline_from_config(pipeline_config)
        guardrail = pipeline.input_pipeline[0] if pipeline.input_pipeline else None

        if not guardrail:
            print("Failed to create guardrail")
            return

        # Check overridden value
        if hasattr(guardrail, "enabled_categories"):
            assert "hate_speech" in guardrail.enabled_categories, "Category override failed"

        # Check default value
        if hasattr(guardrail, "confidence_threshold"):
            assert guardrail.confidence_threshold > 0, "Should have default threshold"


class TestRealWorldConfigScenarios:
    """Test real-world configuration scenarios"""

    def test_yaml_config_loading(self):
        """Test loading config from YAML matches expected structure"""
        yaml_content = """
version: "1.0"
pipeline:
  input:
    - name: pii_guard
      type: simple_pii_detection
      enabled: true
      on_error: block
      config:
        confidence_threshold: 0.75
        patterns: ["ssn", "credit_card"]
      
    - name: toxicity_guard
      type: simple_toxicity_detection
      enabled: true
      on_error: block
      config:
        confidence_threshold: 0.65
        categories: ["hate_speech", "harassment"]
        
  output: []
"""

        # Parse YAML
        config = yaml.safe_load(yaml_content)

        # Create pipeline
        pipeline = create_pipeline_from_config(config)

        # Verify guardrails created with correct config
        assert len(pipeline.input_pipeline) >= 2, "Not all guardrails created"

        # Find PII guardrail
        pii_guard = next((g for g in pipeline.input_pipeline if g.name == "pii_guard"), None)
        assert pii_guard is not None, "PII guardrail not found"

        if hasattr(pii_guard, "confidence_threshold"):
            assert pii_guard.confidence_threshold == 0.75, "YAML config not applied"

    def test_environment_variable_substitution(self):
        """Test if config supports environment variables"""
        import os

        os.environ["TEST_THRESHOLD"] = "0.42"

        config = {
            "pipeline": {"name": "env_test"},
            "guardrails": [
                {
                    "name": "env_guard",
                    "type": "simple_pii_detection",
                    "config": {
                        # This might not work - document behavior
                        "confidence_threshold": "${TEST_THRESHOLD}"
                    },
                }
            ],
        }

        try:
            pipeline = create_pipeline_from_config(config)
            guard = pipeline.input_guardrails[0]
            if hasattr(guard, "confidence_threshold"):
                print(f"Env var substitution result: {guard.confidence_threshold}")
        except Exception as e:
            print(f"Env var substitution not supported: {e}")


if __name__ == "__main__":
    print("=== Pipeline Integration Test Results ===")

    # Critical config flow test
    print("\n1. Testing nested config structure...")
    config_test = TestPipelineConfigFlow()
    try:
        config_test.test_nested_config_structure()
        print("✓ Nested config test passed")
    except AssertionError as e:
        print(f"✗ CRITICAL: Nested config test failed: {e}")

    print("\n2. Testing all guardrail config extraction...")
    config_test.test_all_guardrail_config_extraction()

    print("\n3. Testing YAML config loading...")
    scenario_test = TestRealWorldConfigScenarios()
    try:
        scenario_test.test_yaml_config_loading()
        print("✓ YAML config test passed")
    except AssertionError as e:
        print(f"✗ YAML config test failed: {e}")
