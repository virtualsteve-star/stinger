"""
High-Level Guardrail Pipeline API

This module provides a simple, developer-friendly API for using guardrails
without dealing with async complexity or low-level configuration.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union, TypedDict
from pathlib import Path

from .guardrail_interface import GuardrailInterface, GuardrailResult, GuardrailRegistry, GuardrailFactory
from .config import ConfigLoader
from .guardrail_interface import GuardrailRegistry, GuardrailFactory, GuardrailInterface
from .preset_configs import PresetConfigs
from ..utils.exceptions import PipelineError, ConfigurationError

logger = logging.getLogger(__name__)


class PipelineResult(TypedDict):
    """Type definition for guardrail check results."""
    blocked: bool
    warnings: List[str]
    reasons: List[str]
    details: Dict[str, Any]
    pipeline_type: str


class PipelineStatus(TypedDict):
    """Type definition for pipeline status information."""
    input_guardrails: List[Dict[str, Any]]
    output_guardrails: List[Dict[str, Any]]
    total_enabled: int
    total_disabled: int


class GuardrailPipeline:
    """
    High-level API for using guardrails with a simple, synchronous interface.
    
    This class provides a developer-friendly way to:
    - Load configurations from YAML files or use preset configurations
    - Run content through input and output guardrails
    - Get clear, actionable results
    - Handle errors gracefully
    
    Example:
        ```python
        from stinger import GuardrailPipeline
        
        # Create pipeline from preset
        pipeline = GuardrailPipeline.from_preset("customer_service")
        
        # Or create from config file
        pipeline = GuardrailPipeline("config.yaml")
        
        # Check input content
        result = pipeline.check_input("Hello, world!")
        if result['blocked']:
            print(f"Input blocked: {result['reasons']}")
        
        # Check output content
        result = pipeline.check_output("Here's your response...")
        if result['blocked']:
            print(f"Output blocked: {result['reasons']}")
        ```
    """
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None) -> None:
        """
        Initialize the guardrail pipeline.
        
        Args:
            config_path: Path to YAML configuration file. If None, uses default config.
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file is invalid
            RuntimeError: If pipeline initialization fails
        """
        try:
            self.config_loader = ConfigLoader()
            self.registry = GuardrailRegistry()
            self.factory = GuardrailFactory(self.registry)
            
            # Register all available guardrail factories
            from .guardrail_factory import register_all_factories
            register_all_factories(self.registry)
            
            # Load configuration
            if config_path:
                config_path = Path(config_path)
                if not config_path.exists():
                    raise FileNotFoundError(f"Configuration file not found: {config_path}")
                self.config = self.config_loader.load(str(config_path))
            else:
                # Use default config
                default_config_path = Path(__file__).parent / "configs" / "models.yaml"
                if not default_config_path.exists():
                    raise FileNotFoundError(f"Default configuration file not found: {default_config_path}")
                self.config = self.config_loader.load(str(default_config_path))
            
            # Build pipelines
            self.input_pipeline = self._build_pipeline('input')
            self.output_pipeline = self._build_pipeline('output')
            
            logger.info(f"GuardrailPipeline initialized with {len(self.input_pipeline)} input and {len(self.output_pipeline)} output guardrails")
            
        except Exception as e:
            logger.error(f"Failed to initialize GuardrailPipeline: {e}")
            raise RuntimeError(f"Pipeline initialization failed: {e}") from e
    
    @classmethod
    def from_preset(cls, preset_name: str) -> 'GuardrailPipeline':
        """
        Create a pipeline from a preset configuration.
        
        Args:
            preset_name: Name of the preset configuration
            
        Returns:
            Configured GuardrailPipeline instance
            
        Raises:
            ValueError: If preset name is invalid
            RuntimeError: If pipeline initialization fails
        """
        try:
            # Get preset configuration
            preset_config = PresetConfigs.get_preset(preset_name)
            
            # Create temporary config file
            import tempfile
            import yaml
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(preset_config, f)
                temp_config_path = f.name
            
            # Create pipeline from temp config
            pipeline = cls(temp_config_path)
            
            # Clean up temp file
            Path(temp_config_path).unlink()
            
            logger.info(f"Created pipeline from preset: {preset_name}")
            return pipeline
            
        except Exception as e:
            logger.error(f"Failed to create pipeline from preset '{preset_name}': {e}")
            raise RuntimeError(f"Preset pipeline creation failed: {e}") from e
    
    @classmethod
    def get_available_presets(cls) -> Dict[str, str]:
        """
        Get available preset configurations.
        
        Returns:
            Dictionary mapping preset names to descriptions
        """
        return PresetConfigs.get_available_presets()
    
    @classmethod
    def save_preset_config(cls, preset_name: str, filename: str) -> None:
        """
        Save a preset configuration to a file.
        
        Args:
            preset_name: Name of the preset to save
            filename: Output filename
            
        Raises:
            ValueError: If preset name is invalid
        """
        try:
            preset_config = PresetConfigs.get_preset(preset_name)
            PresetConfigs.save_preset(preset_config, filename)
            logger.info(f"Saved preset '{preset_name}' to {filename}")
        except Exception as e:
            logger.error(f"Failed to save preset '{preset_name}': {e}")
            raise
    
    def _build_pipeline(self, pipeline_type: str) -> List[GuardrailInterface]:
        """
        Build a pipeline from configuration.
        
        Args:
            pipeline_type: Type of pipeline ('input' or 'output')
            
        Returns:
            List of configured guardrail instances
            
        Raises:
            ValueError: If pipeline_type is invalid
        """
        if pipeline_type not in ['input', 'output']:
            raise ValueError(f"Invalid pipeline type: {pipeline_type}. Must be 'input' or 'output'")
        
        pipeline_configs = self.config.get('pipeline', {}).get(pipeline_type, [])
        pipeline = []
        
        for config in pipeline_configs:
            try:
                guardrail = self.factory.create_from_config(config)
                if guardrail:
                    pipeline.append(guardrail)
                    logger.debug(f"Added {pipeline_type} guardrail: {guardrail.name}")
                else:
                    logger.warning(f"Failed to create {pipeline_type} guardrail from config: {config}")
            except Exception as e:
                logger.error(f"Error creating {pipeline_type} guardrail: {e}")
        
        return pipeline
    
    def check_input(self, content: str) -> PipelineResult:
        """
        Check input content through all input guardrails.
        
        Args:
            content: The input content to check
            
        Returns:
            Dict with 'blocked', 'warnings', 'reasons', and 'details' keys
            
        Raises:
            ValueError: If content is None or empty
            RuntimeError: If pipeline execution fails
        """
        if content is None:
            raise ValueError("Content cannot be None")
        
        return self._run_pipeline(self.input_pipeline, content, "input")
    
    def check_output(self, content: str) -> PipelineResult:
        """
        Check output content through all output guardrails.
        
        Args:
            content: The output content to check
            
        Returns:
            Dict with 'blocked', 'warnings', 'reasons', and 'details' keys
            
        Raises:
            ValueError: If content is None or empty
            RuntimeError: If pipeline execution fails
        """
        if content is None:
            raise ValueError("Content cannot be None")
        
        return self._run_pipeline(self.output_pipeline, content, "output")
    
    def _run_pipeline(self, pipeline: List[GuardrailInterface], content: str, pipeline_type: str) -> PipelineResult:
        """
        Run content through a pipeline of guardrails.
        
        Args:
            pipeline: List of guardrail instances
            content: Content to check
            pipeline_type: Type of pipeline for logging
            
        Returns:
            Standardized result dictionary
            
        Raises:
            RuntimeError: If pipeline execution fails catastrophically
        """
        blocked = False
        warnings: List[str] = []
        reasons: List[str] = []
        details: Dict[str, Any] = {}
        
        for guardrail in pipeline:
            try:
                # Run the async analyze method in a sync context
                result = asyncio.run(guardrail.analyze(content))
                
                if result.blocked:
                    blocked = True
                    reasons.append(f"{guardrail.name}: {result.reason}")
                
                if result.confidence > 0.5 and not result.blocked:
                    warnings.append(f"{guardrail.name}: {result.reason}")
                
                # Store detailed results
                details[guardrail.name] = {
                    'blocked': result.blocked,
                    'confidence': result.confidence,
                    'reason': result.reason,
                    'details': result.details
                }
                
            except Exception as e:
                logger.error(f"Error running {guardrail.name} guardrail: {e}")
                reasons.append(f"{guardrail.name}: Error - {str(e)}")
                details[guardrail.name] = {
                    'error': str(e),
                    'blocked': False,
                    'confidence': 0.0
                }
        
        return {
            'blocked': blocked,
            'warnings': warnings,
            'reasons': reasons,
            'details': details,
            'pipeline_type': pipeline_type
        }
    
    def get_guardrail_status(self) -> PipelineStatus:
        """
        Get status of all guardrails in the pipeline.
        
        Returns:
            Dictionary with guardrail status information
        """
        status: PipelineStatus = {
            'input_guardrails': [],
            'output_guardrails': [],
            'total_enabled': 0,
            'total_disabled': 0
        }
        
        for guardrail in self.input_pipeline:
            status['input_guardrails'].append({
                'name': guardrail.name,
                'type': guardrail.guardrail_type.value,
                'enabled': guardrail.enabled,
                'available': guardrail.is_available()
            })
            if guardrail.enabled:
                status['total_enabled'] += 1
            else:
                status['total_disabled'] += 1
        
        for guardrail in self.output_pipeline:
            status['output_guardrails'].append({
                'name': guardrail.name,
                'type': guardrail.guardrail_type.value,
                'enabled': guardrail.enabled,
                'available': guardrail.is_available()
            })
            if guardrail.enabled:
                status['total_enabled'] += 1
            else:
                status['total_disabled'] += 1
        
        return status
    
    def enable_guardrail(self, name: str) -> bool:
        """
        Enable a specific guardrail by name.
        
        Args:
            name: Name of the guardrail to enable
            
        Returns:
            True if guardrail was found and enabled, False otherwise
        """
        for guardrail in self.input_pipeline + self.output_pipeline:
            if guardrail.name == name:
                guardrail.enable()
                logger.info(f"Enabled guardrail: {name}")
                return True
        logger.warning(f"Guardrail not found: {name}")
        return False
    
    def disable_guardrail(self, name: str) -> bool:
        """
        Disable a specific guardrail by name.
        
        Args:
            name: Name of the guardrail to disable
            
        Returns:
            True if guardrail was found and disabled, False otherwise
        """
        for guardrail in self.input_pipeline + self.output_pipeline:
            if guardrail.name == name:
                guardrail.disable()
                logger.info(f"Disabled guardrail: {name}")
                return True
        logger.warning(f"Guardrail not found: {name}")
        return False
    
    def get_guardrail_config(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration of a specific guardrail.
        
        Args:
            name: Name of the guardrail
            
        Returns:
            Guardrail configuration or None if not found
        """
        for guardrail in self.input_pipeline + self.output_pipeline:
            if guardrail.name == name:
                return guardrail.get_config()
        return None
    
    def update_guardrail_config(self, name: str, config: Dict[str, Any]) -> bool:
        """
        Update configuration of a specific guardrail.
        
        Args:
            name: Name of the guardrail
            config: New configuration dictionary
            
        Returns:
            True if guardrail was found and updated, False otherwise
        """
        for guardrail in self.input_pipeline + self.output_pipeline:
            if guardrail.name == name:
                success = guardrail.update_config(config)
                if success:
                    logger.info(f"Updated guardrail config: {name}")
                else:
                    logger.error(f"Failed to update guardrail config: {name}")
                return success
        logger.warning(f"Guardrail not found: {name}")
        return False


# Convenience function for quick usage
def create_pipeline(config_path: Optional[Union[str, Path]] = None) -> GuardrailPipeline:
    """
    Create a guardrail pipeline with the given configuration.
    
    This is a convenience function for quick pipeline creation.
    
    Args:
        config_path: Path to YAML configuration file
        
    Returns:
        Configured GuardrailPipeline instance
        
    Example:
        ```python
        from stinger import create_pipeline
        
        pipeline = create_pipeline("my_config.yaml")
        result = pipeline.check_input("Hello, world!")
        ```
    """
    return GuardrailPipeline(config_path) 