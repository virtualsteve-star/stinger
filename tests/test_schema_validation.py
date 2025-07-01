import pytest
import tempfile
import os
from src.stinger.core.config import ConfigLoader
from src.stinger.utils.exceptions import ConfigurationError


class TestSchemaValidation:
    """Test YAML schema validation functionality."""
    
    def test_valid_config_passes_validation(self):
        """Test that a valid configuration passes schema validation."""
        valid_config = """
        version: "1.0"
        pipeline:
          input:
            - type: keyword_list
              name: toxic_language
              enabled: true
              on_error: block
              case_sensitive: false
              keywords:
                - hate
                - violence
                - abuse
            - type: length_filter
              name: max_length
              enabled: true
              on_error: block
              max_length: 1000
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(valid_config)
            config_path = f.name
        
        try:
            config_loader = ConfigLoader()
            config = config_loader.load(config_path)
            
            # Should not raise any exceptions
            assert config is not None
            assert 'pipeline' in config
            assert 'input' in config['pipeline']
            assert len(config['pipeline']['input']) == 2
            
        finally:
            os.unlink(config_path)
    
    def test_invalid_config_missing_type_fails_validation(self):
        """Test that a configuration missing required 'type' field fails validation."""
        invalid_config = """
        version: "1.0"
        pipeline:
          input:
            - name: toxic_language
              enabled: true
              on_error: block
              keywords:
                - hate
                - violence
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(invalid_config)
            config_path = f.name
        
        try:
            config_loader = ConfigLoader()
            
            with pytest.raises(ConfigurationError) as exc_info:
                config_loader.load(config_path)
            
            # Check that the error message mentions the missing field
            error_msg = str(exc_info.value)
            assert "type" in error_msg.lower()
            
        finally:
            os.unlink(config_path)
    
    def test_invalid_config_wrong_type_fails_validation(self):
        """Test that a configuration with invalid filter type fails validation."""
        invalid_config = """
        version: "1.0"
        pipeline:
          input:
            - type: invalid_filter_type
              name: test_filter
              enabled: true
              on_error: block
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(invalid_config)
            config_path = f.name
        
        try:
            config_loader = ConfigLoader()
            
            with pytest.raises(ConfigurationError) as exc_info:
                config_loader.load(config_path)
            
            # Check that the error message mentions the invalid type
            error_msg = str(exc_info.value)
            assert "invalid_filter_type" in error_msg or "type" in error_msg.lower()
            
        finally:
            os.unlink(config_path)
    
    def test_invalid_config_missing_required_fields_fails_validation(self):
        """Test that a configuration missing required fields fails validation."""
        invalid_config = """
        version: "1.0"
        pipeline:
          input:
            - type: keyword_list
              enabled: true
              on_error: block
              # Missing 'name' field
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(invalid_config)
            config_path = f.name
        
        try:
            config_loader = ConfigLoader()
            
            with pytest.raises(ConfigurationError) as exc_info:
                config_loader.load(config_path)
            
            # Check that the error message mentions the missing field
            error_msg = str(exc_info.value)
            assert "name" in error_msg.lower()
            
        finally:
            os.unlink(config_path)
    
    def test_invalid_config_wrong_data_types_fails_validation(self):
        """Test that a configuration with wrong data types fails validation."""
        invalid_config = """
        version: "1.0"
        pipeline:
          input:
            - type: length_filter
              name: max_length
              enabled: "not_a_boolean"  # Should be boolean
              on_error: block
              max_length: "not_a_number"  # Should be number
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(invalid_config)
            config_path = f.name
        
        try:
            config_loader = ConfigLoader()
            
            with pytest.raises(ConfigurationError) as exc_info:
                config_loader.load(config_path)
            
            # Should fail validation due to wrong data types
            error_msg = str(exc_info.value)
            assert "boolean" in error_msg.lower() or "number" in error_msg.lower()
            
        finally:
            os.unlink(config_path)
    
    def test_empty_filters_list_passes_validation(self):
        """Test that an empty filters list is valid."""
        valid_config = """
        version: "1.0"
        pipeline:
          input: []
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(valid_config)
            config_path = f.name
        
        try:
            config_loader = ConfigLoader()
            config = config_loader.load(config_path)
            
            # Should not raise any exceptions
            assert config is not None
            assert 'pipeline' in config
            assert 'input' in config['pipeline']
            assert len(config['pipeline']['input']) == 0
            
        finally:
            os.unlink(config_path)
    
    def test_complex_valid_config_passes_validation(self):
        """Test that a complex but valid configuration passes validation."""
        valid_config = """
        version: "1.0"
        pipeline:
          input:
            - type: keyword_list
              name: toxic_language
              enabled: true
              on_error: block
              case_sensitive: false
              keywords:
                - hate
                - violence
                - abuse
            - type: length_filter
              name: max_length
              enabled: true
              on_error: block
              max_length: 1000
            - type: regex_filter
              name: url_blocker
              enabled: true
              on_error: block
              patterns:
                - "https?://.*"
            - type: pass_through
              name: always_pass
              enabled: true
              on_error: block
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(valid_config)
            config_path = f.name
        
        try:
            config_loader = ConfigLoader()
            config = config_loader.load(config_path)
            
            # Should not raise any exceptions
            assert config is not None
            assert 'pipeline' in config
            assert 'input' in config['pipeline']
            assert len(config['pipeline']['input']) == 4
            
            # Check that all filters have required fields
            for guardrail_config in config['pipeline']['input']:
                assert 'type' in guardrail_config
                assert 'name' in guardrail_config
                assert 'enabled' in guardrail_config
                assert 'on_error' in guardrail_config
            
        finally:
            os.unlink(config_path) 