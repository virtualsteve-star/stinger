import yaml
from pathlib import Path
from typing import Dict, Any
from ..utils.exceptions import ConfigurationError

class ConfigLoader:
    def __init__(self):
        self.config = None
    
    def load(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            
            if not self.config:
                raise ConfigurationError("Empty configuration file")
            
            # Basic validation
            if 'version' not in self.config:
                raise ConfigurationError("Missing 'version' field")
            
            if 'pipeline' not in self.config:
                raise ConfigurationError("Missing 'pipeline' field")
            
            return self.config
            
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML: {str(e)}")
        except FileNotFoundError:
            raise ConfigurationError(f"Configuration file not found: {config_path}")
    
    def get_pipeline_config(self, pipeline_type: str = 'input') -> list:
        """Get pipeline configuration for specified type."""
        if not self.config:
            raise ConfigurationError("No configuration loaded")
        
        pipeline = self.config.get('pipeline', {})
        return pipeline.get(pipeline_type, []) 