"""
API Key Management System

This module provides centralized API key management with security features
for handling external API keys like OpenAI.
"""

import os
import re
import logging
from typing import Dict, Optional, Any, Union, TYPE_CHECKING
from pathlib import Path
import yaml
import json

# Optional encryption - will be added when cryptography is available
try:
    from cryptography.fernet import Fernet
    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False
    Fernet = None

if TYPE_CHECKING:
    from cryptography.fernet import Fernet as FernetType
else:
    FernetType = Any


logger = logging.getLogger(__name__)


class APIKeyManager:
    """Centralized API key management with security features."""
    
    def __init__(self, config_path: Optional[str] = None, encryption_key: Optional[str] = None):
        """Initialize with optional config file path and encryption key."""
        self.config_path = config_path
        self.encryption_key = encryption_key or self._generate_encryption_key()
        self._fernet: Optional[FernetType] = None
        if ENCRYPTION_AVAILABLE and self.encryption_key and Fernet is not None:
            try:
                self._fernet = Fernet(self.encryption_key.encode())
            except Exception as e:
                logger.warning(f"Failed to initialize encryption: {e}")
        self._keys: Dict[str, str] = {}
        self._load_keys()
    
    def _generate_encryption_key(self) -> str:
        """Generate a new encryption key."""
        if ENCRYPTION_AVAILABLE and Fernet is not None:
            return Fernet.generate_key().decode()
        return "no-encryption-available"
    
    def _load_keys(self) -> None:
        """Load API keys from environment variables and config file."""
        # Load from environment variables first (highest priority)
        self._load_from_environment()
        
        # Load from config file if specified
        if self.config_path and Path(self.config_path).exists():
            self._load_from_config_file()
        
        # Load from secure local storage
        self._load_from_secure_storage()
    
    def _load_from_environment(self) -> None:
        """Load API keys from environment variables."""
        env_keys = {
            'openai': 'OPENAI_API_KEY',
            'azure_openai': 'AZURE_OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
        }
        
        for service, env_var in env_keys.items():
            key = os.getenv(env_var)
            if key:
                self._keys[service] = key
                logger.info(f"Loaded {service} API key from environment variable")
    
    def _load_from_config_file(self) -> None:
        """Load API keys from config file."""
        if not self.config_path:
            return
            
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            if config and 'api_keys' in config:
                for service, key_data in config['api_keys'].items():
                    if isinstance(key_data, dict) and 'encrypted_key' in key_data:
                        # Decrypt the key
                        if self._fernet is not None:
                            encrypted_key = key_data['encrypted_key'].encode()
                            try:
                                decrypted_key = self._fernet.decrypt(encrypted_key).decode()
                                self._keys[service] = decrypted_key
                                logger.info(f"Loaded encrypted {service} API key from config file")
                            except Exception as e:
                                logger.warning(f"Failed to decrypt {service} API key: {e}")
                        else:
                            logger.warning(f"Encryption not available, skipping encrypted {service} API key")
                    elif isinstance(key_data, str):
                        # Plain text key (not recommended for production)
                        self._keys[service] = key_data
                        logger.warning(f"Loaded plain text {service} API key from config file")
        except Exception as e:
            logger.error(f"Failed to load API keys from config file: {e}")
    
    def _load_from_secure_storage(self) -> None:
        """Load API keys from secure local storage."""
        secure_path = Path.home() / '.stinger' / 'api_keys.enc'
        
        if secure_path.exists():
            try:
                with open(secure_path, 'r') as f:
                    encrypted_data = f.read().strip()
                
                if self._fernet is not None:
                    decrypted_data = self._fernet.decrypt(encrypted_data.encode()).decode()
                    keys_data = json.loads(decrypted_data)
                    
                    for service, key in keys_data.items():
                        if service not in self._keys:  # Don't override env vars
                            self._keys[service] = key
                            logger.info(f"Loaded {service} API key from secure storage")
                else:
                    logger.warning("Encryption not available, skipping secure storage")
                    
            except Exception as e:
                logger.error(f"Failed to load from secure storage: {e}")
    
    def get_openai_key(self) -> Optional[str]:
        """Get OpenAI API key securely."""
        return self._keys.get('openai')
    
    def get_azure_openai_key(self) -> Optional[str]:
        """Get Azure OpenAI API key securely."""
        return self._keys.get('azure_openai')
    
    def get_anthropic_key(self) -> Optional[str]:
        """Get Anthropic API key securely."""
        return self._keys.get('anthropic')
    
    def get_key(self, service: str) -> Optional[str]:
        """Get API key for specified service."""
        return self._keys.get(service)
    
    def set_key(self, service: str, key: str, encrypt: bool = True) -> bool:
        """Set API key for specified service."""
        try:
            if encrypt and self._fernet is not None:
                # Store encrypted key
                encrypted_key = self._fernet.encrypt(key.encode()).decode()
                self._keys[service] = key  # Store decrypted key in memory
                
                # Save to config file if available
                if self.config_path:
                    self._save_to_config_file(service, encrypted_key)
            else:
                self._keys[service] = key
            
            logger.info(f"Set {service} API key")
            return True
        except Exception as e:
            logger.error(f"Failed to set {service} API key: {e}")
            return False
    
    def _save_to_config_file(self, service: str, encrypted_key: str) -> None:
        """Save encrypted key to config file."""
        if not self.config_path:
            return
            
        try:
            config = {}
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    config = yaml.safe_load(f) or {}
            
            if 'api_keys' not in config:
                config['api_keys'] = {}
            
            config['api_keys'][service] = {
                'encrypted_key': encrypted_key,
                'encrypted': True
            }
            
            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            logger.info(f"Saved encrypted {service} API key to config file")
        except Exception as e:
            logger.error(f"Failed to save {service} API key to config file: {e}")
    
    def validate_key(self, service: str, key: Optional[str] = None) -> bool:
        """Validate API key format and basic connectivity."""
        if key is None:
            key = self.get_key(service)
        
        if not key:
            return False
        
        # Basic format validation
        if service == 'openai':
            return self._validate_openai_key(key)
        elif service == 'azure_openai':
            return self._validate_azure_openai_key(key)
        elif service == 'anthropic':
            return self._validate_anthropic_key(key)
        
        return True  # Unknown service, assume valid
    
    def _validate_openai_key(self, key: str) -> bool:
        """Validate OpenAI API key format."""
        # OpenAI keys can be different formats:
        # - sk-... (standard keys, typically 51 chars)
        # - sk-svcacct-... (service account keys, longer)
        # - sk-proj-... (project keys)
        return bool(re.match(r'^sk-[A-Za-z0-9_-]{20,}$', key))
    
    def _validate_azure_openai_key(self, key: str) -> bool:
        """Validate Azure OpenAI API key format."""
        # Azure OpenAI keys are typically 32 characters long
        return bool(re.match(r'^[A-Za-z0-9]{32}$', key))
    
    def _validate_anthropic_key(self, key: str) -> bool:
        """Validate Anthropic API key format."""
        # Anthropic keys start with 'sk-ant-' and are typically 48 characters long
        return bool(re.match(r'^sk-ant-[A-Za-z0-9]{43}$', key))
    
    def rotate_key(self, service: str) -> bool:
        """Rotate API key for specified service (placeholder for future implementation)."""
        logger.info(f"Key rotation requested for {service} (not implemented)")
        return False
    
    def health_check(self) -> Dict[str, bool]:
        """Check health of all configured API keys."""
        health_status = {}
        
        for service in self._keys.keys():
            health_status[service] = self.validate_key(service)
        
        return health_status
    
    def list_services(self) -> list:
        """List all configured services."""
        return list(self._keys.keys())
    
    def clear_keys(self) -> None:
        """Clear all stored API keys."""
        self._keys.clear()
        logger.info("Cleared all API keys")
    
    def export_encryption_key(self) -> str:
        """Export the encryption key for backup purposes."""
        return self.encryption_key
    
    def import_encryption_key(self, key: str) -> bool:
        """Import an encryption key."""
        try:
            self.encryption_key = key
            if ENCRYPTION_AVAILABLE and Fernet is not None:
                self._fernet = Fernet(key.encode())
            return True
        except Exception as e:
            logger.error(f"Failed to import encryption key: {e}")
            return False
    
    def save_to_secure_storage(self, service: str, key: str) -> bool:
        """Save API key to secure local storage."""
        if not ENCRYPTION_AVAILABLE or self._fernet is None:
            logger.error("Encryption not available for secure storage")
            return False
        
        try:
            # Create .stinger directory if it doesn't exist
            secure_dir = Path.home() / '.stinger'
            secure_dir.mkdir(mode=0o700, exist_ok=True)
            
            secure_path = secure_dir / 'api_keys.enc'
            
            # Load existing keys or create new dict
            existing_keys = {}
            if secure_path.exists():
                try:
                    with open(secure_path, 'r') as f:
                        encrypted_data = f.read().strip()
                    decrypted_data = self._fernet.decrypt(encrypted_data.encode()).decode()
                    existing_keys = json.loads(decrypted_data)
                except Exception:
                    existing_keys = {}
            
            # Add/update the key
            existing_keys[service] = key
            
            # Encrypt and save
            json_data = json.dumps(existing_keys)
            encrypted_data = self._fernet.encrypt(json_data.encode()).decode()
            
            with open(secure_path, 'w') as f:
                f.write(encrypted_data)
            
            # Set secure permissions
            secure_path.chmod(0o600)
            
            logger.info(f"Saved {service} API key to secure storage")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save to secure storage: {e}")
            return False
    
    def get_secure_storage_path(self) -> str:
        """Get the path to secure storage."""
        return str(Path.home() / '.stinger' / 'api_keys.enc') 