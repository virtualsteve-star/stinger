#!/usr/bin/env python3
"""
Smoke Tests for CI Pipeline

Ultra-fast tests that verify basic functionality without AI calls.
These tests should complete in <5 seconds total.
"""

import pytest
import asyncio
from pathlib import Path


@pytest.mark.ci
class TestSmoke:
    """Ultra-fast smoke tests for CI - <5s total"""
    
    def test_imports(self):
        """Verify all modules import successfully"""
        import stinger
        from stinger.core.pipeline import GuardrailPipeline
        from stinger.core.guardrail_interface import GuardrailRegistry
        from stinger.guardrails.simple_pii_detection_guardrail import SimplePIIDetectionGuardrail
        from stinger.guardrails.simple_toxicity_detection_guardrail import SimpleToxicityDetectionGuardrail
        from stinger.guardrails.length_guardrail import LengthGuardrail
        
    def test_basic_pipeline_creation(self):
        """Pipeline can be created with minimal config"""
        from stinger.core.pipeline import GuardrailPipeline
        import tempfile
        import yaml
        
        config = {
            "version": "1.0", 
            "pipeline": {
                "input": [],
                "output": []
            }
        }
        
        # Create temp config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            config_path = f.name
        
        try:
            # Empty pipeline doesn't need AI
            pipeline = GuardrailPipeline(config_path)
            assert pipeline is not None
            assert len(pipeline.input_pipeline) == 0
            assert len(pipeline.output_pipeline) == 0
        finally:
            Path(config_path).unlink()
        
    def test_guardrail_registry(self):
        """All guardrails are registered"""
        from stinger.core.guardrail_interface import GuardrailRegistry, GuardrailType
        from stinger.core.guardrail_factory import register_all_factories
        
        registry = GuardrailRegistry()
        register_all_factories(registry)
        
        # Check that factories are registered
        # We can't easily list all types, but we can check specific ones exist
        test_types = [
            GuardrailType.SIMPLE_PII_DETECTION,
            GuardrailType.SIMPLE_TOXICITY_DETECTION,
            GuardrailType.LENGTH_FILTER
        ]
        
        for guard_type in test_types:
            # Try to create a test guardrail
            config = {"name": "test", "config": {}}
            guardrail = registry.create_guardrail(guard_type, "test", config)
            # Some might fail due to missing config, but factory should exist
            assert guard_type in registry._factories


@pytest.mark.ci
class TestConfigValidation:
    """Fast config validation tests"""
    
    def test_config_structure_validation(self):
        """Config structure is validated"""
        from stinger.core.config import ConfigLoader
        import tempfile
        import yaml
        
        # Valid config should pass
        valid_config = {
            "version": "1.0",
            "pipeline": {
                "input": [
                    {
                        "name": "pii",
                        "type": "simple_pii_detection", 
                        "enabled": True,
                        "on_error": "block",
                        "config": {"confidence_threshold": 0.7}
                    }
                ],
                "output": []
            }
        }
        
        # ConfigLoader validates by loading
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_config, f)
            config_path = f.name
        
        try:
            loader = ConfigLoader()
            config = loader.load(config_path)
            assert config is not None
            assert 'pipeline' in config
        finally:
            Path(config_path).unlink()
        
    def test_preset_configs_exist(self):
        """All preset configs are available"""
        from stinger.core.preset_configs import PresetConfigs
        
        presets = ["customer_service", "medical", "educational"]
        for preset in presets:
            # Just check config exists and has right structure
            config = PresetConfigs.get_preset(preset)
            assert config is not None
            assert 'pipeline' in config
            assert 'input' in config['pipeline']
            assert 'output' in config['pipeline']


@pytest.mark.ci 
class TestSimpleGuardrails:
    """Fast tests for non-AI guardrails"""
    
    def test_simple_pii_detection(self):
        """Simple regex-based PII detection (NOT AI)"""
        from stinger.guardrails.simple_pii_detection_guardrail import SimplePIIDetectionGuardrail
        
        config = {"name": "pii", "config": {"confidence_threshold": 0.7}}
        guardrail = SimplePIIDetectionGuardrail("test", config)
        
        # This uses regex patterns, not AI
        result = asyncio.run(guardrail.analyze("SSN: 123-45-6789"))
        assert result.blocked is True
        assert result.confidence > 0.7
        
        result = asyncio.run(guardrail.analyze("Hello world"))
        assert result.blocked is False
        
    def test_simple_toxicity(self):
        """Simple pattern-based toxicity (NOT AI)"""
        from stinger.guardrails.simple_toxicity_detection_guardrail import SimpleToxicityDetectionGuardrail
        
        config = {"name": "toxicity", "config": {"confidence_threshold": 0.7}}
        guardrail = SimpleToxicityDetectionGuardrail("test", config)
        
        # Uses keyword patterns, not AI
        result = asyncio.run(guardrail.analyze("I hate you"))
        assert result.blocked is True
        
        result = asyncio.run(guardrail.analyze("Have a nice day"))
        assert result.blocked is False
        
    def test_length_guardrail(self):
        """Length guardrail blocks correctly"""
        from stinger.guardrails.length_guardrail import LengthGuardrail
        
        config = {"name": "length", "config": {"max_length": 10}}
        guardrail = LengthGuardrail(config)
        
        result = asyncio.run(guardrail.analyze("short"))
        assert result.blocked is False
        
        result = asyncio.run(guardrail.analyze("this is too long for the limit"))
        assert result.blocked is True


@pytest.mark.ci
class TestPipelineBasics:
    """Test basic pipeline functionality without AI"""
    
    def test_empty_pipeline_execution(self):
        """Empty pipeline executes without errors"""
        from stinger.core.pipeline import GuardrailPipeline
        import tempfile
        import yaml
        
        config = {
            "version": "1.0",
            "pipeline": {"input": [], "output": []}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            config_path = f.name
        
        try:
            pipeline = GuardrailPipeline(config_path)
            result = pipeline.check_input("test message")
            
            assert result is not None
            assert result['blocked'] is False
            assert 'warnings' in result
            assert 'reasons' in result
        finally:
            Path(config_path).unlink()
        
    def test_simple_guardrail_pipeline(self):
        """Pipeline with simple guardrails works"""
        from stinger.core.pipeline import GuardrailPipeline
        import tempfile
        import yaml
        
        config = {
            "version": "1.0",
            "pipeline": {
                "input": [
                    {
                        "name": "length_check",
                        "type": "length_filter",
                        "enabled": True,
                        "on_error": "block",
                        "config": {"max_length": 50}
                    }
                ],
                "output": []
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            config_path = f.name
        
        try:
            pipeline = GuardrailPipeline(config_path)
            
            # Short message passes
            result = pipeline.check_input("Hello")
            assert result['blocked'] is False
            
            # Long message blocked
            result = pipeline.check_input("x" * 100)
            assert result['blocked'] is True
        finally:
            Path(config_path).unlink()