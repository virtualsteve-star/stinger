import yaml
from pathlib import Path
from typing import Dict, Any
from ..utils.exceptions import ConfigurationError
import jsonschema

CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "version": {"type": "string"},
        "pipeline": {
            "type": "object",
            "properties": {
                "input": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"type": "string", "enum": [
                                "keyword_block", "keyword_list", "regex_filter", "length_filter", "url_filter", "pass_through"
                            ]},
                            "enabled": {"type": "boolean"},
                            "on_error": {"type": "string", "enum": ["block", "allow", "skip"]},
                            "min_length": {"type": "integer"},
                            "max_length": {"type": "integer"},
                            "keyword": {"type": "string"},
                            "keywords": {
                                "oneOf": [
                                    {"type": "array", "items": {"type": "string"}},
                                    {"type": "string"}
                                ]
                            },
                            "keywords_file": {"type": "string"},
                            "keyword_files": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "case_sensitive": {"type": "boolean"},
                            "patterns": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "action": {"type": "string"},
                            "thresholds": {
                                "type": "object",
                                "properties": {
                                    "allow": {
                                        "type": "array",
                                        "items": {"type": "integer"},
                                        "minItems": 2,
                                        "maxItems": 2
                                    },
                                    "warn": {
                                        "type": "array",
                                        "items": {"type": "integer"},
                                        "minItems": 2,
                                        "maxItems": 2
                                    },
                                    "block": {
                                        "type": "array",
                                        "items": {"type": "integer"},
                                        "minItems": 2,
                                        "maxItems": 2
                                    }
                                }
                            },
                            "rules": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "type": {"type": "string", "enum": ["regex", "keyword", "combination", "ai_scorer"]},
                                        "certainty": {"type": "integer", "minimum": 1, "maximum": 100},
                                        "description": {"type": "string"},
                                        "pattern": {"type": "string"},
                                        "keywords": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        },
                                        "logic": {"type": "string"},
                                        "case_sensitive": {"type": "boolean"}
                                    },
                                    "required": ["name", "type", "certainty", "description"]
                                }
                            }
                        },
                        "required": ["name", "type", "enabled", "on_error"]
                    }
                }
            },
            "required": ["input"]
        }
    },
    "required": ["version", "pipeline"]
}

class ConfigLoader:
    def __init__(self):
        self.config = None
    
    def load(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file and validate against schema."""
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            
            if not self.config:
                raise ConfigurationError("Empty configuration file")
            
            # Schema validation
            try:
                jsonschema.validate(instance=self.config, schema=CONFIG_SCHEMA)
            except jsonschema.ValidationError as e:
                # Try to provide line number if possible
                msg = f"Config schema validation error: {e.message}"
                if e.path:
                    msg += f" at {list(e.path)}"
                raise ConfigurationError(msg)
            
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
    
    def build_filters(self, config: Dict[str, Any] = None) -> list:
        """Build filter instances from configuration."""
        if config is None:
            config = self.config
        else:
            self.config = config  # Ensure get_pipeline_config works
        
        if not config:
            raise ConfigurationError("No configuration provided")
        
        from ..filters import FILTER_REGISTRY
        
        filters = []
        pipeline_config = self.get_pipeline_config('input')
        
        for filter_config in pipeline_config:
            filter_type = filter_config.get('type')
            if filter_type not in FILTER_REGISTRY:
                raise ConfigurationError(f"Unknown filter type: {filter_type}")
            
            filter_class = FILTER_REGISTRY[filter_type]
            filter_instance = filter_class(config=filter_config)
            filters.append(filter_instance)
        
        return filters 