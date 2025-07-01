# API Key Security Fix Plan

**Date:** June 28, 2025  
**Status:** In Progress  
**Priority:** Critical Security Fix  
**Estimated Duration:** 3-5 days  

## 🚨 **CRITICAL ISSUES TO FIX**

Based on the security audit, the following critical issues must be addressed immediately:

1. **Environment variable substitution not implemented** - `${OPENAI_API_KEY}` literals in config files
2. **Inconsistent API key management** - Multiple approaches across codebase
3. **Test file security** - `test_api_keys.yaml` not properly gitignored
4. **Missing configuration validation** - No validation of API key configuration

## 📋 **FIX PLAN**

### **Phase 1: Critical Infrastructure Fixes (Day 1)**

#### 1.1 Implement Environment Variable Substitution
**File:** `src/stinger/core/config.py`  
**Priority:** CRITICAL

**Action:**
- Add environment variable substitution to `ConfigLoader.load()` method
- Support `${VAR}` syntax in all configuration values
- Add recursive substitution for nested dictionaries and lists
- Add validation to ensure required environment variables are set

**Implementation:**
```python
def _substitute_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively substitute environment variables in config."""
    if isinstance(config, dict):
        return {k: self._substitute_env_vars(v) for k, v in config.items()}
    elif isinstance(config, list):
        return [self._substitute_env_vars(item) for item in config]
    elif isinstance(config, str):
        # Replace ${VAR} with environment variable values
        return re.sub(r'\$\{([^}]+)\}', lambda m: os.getenv(m.group(1), ''), config)
    return config
```

**Testing:**
- Test with valid environment variables
- Test with missing environment variables (should fail gracefully)
- Test with nested configurations
- Test with array configurations

#### 1.2 Fix .gitignore Security Issue
**File:** `.gitignore`  
**Priority:** CRITICAL

**Action:**
- Add proper patterns for API key files
- Ensure `test_api_keys.yaml` is excluded
- Add patterns for other sensitive files

**Changes:**
```gitignore
# API Keys and Secrets
test_api_keys.yaml
*.key
*.pem
*.env
secrets/
api_keys/
```

#### 1.3 Create Unified API Key Access Pattern
**File:** `src/stinger/core/api_key_manager.py`  
**Priority:** HIGH

**Action:**
- Create global API key manager instance
- Add convenience functions for common operations
- Ensure consistent access patterns across codebase

**Implementation:**
```python
# Global instance
_api_key_manager = APIKeyManager()

def get_api_key(service: str = 'openai') -> Optional[str]:
    """Unified API key access."""
    return _api_key_manager.get_key(service)

def validate_api_key_config() -> Dict[str, bool]:
    """Validate all API key configurations."""
    return _api_key_manager.health_check()
```

### **Phase 2: Standardize API Key Usage (Day 2)**

#### 2.1 Update AI Filters to Use Centralized Manager
**Files to Update:**
- `src/stinger/guardrails/ai_code_generation_filter.py`
- `src/stinger/guardrails/ai_pii_detection_filter.py`
- `src/stinger/guardrails/ai_toxicity_detection_filter.py`
- `src/stinger/guardrails/content_moderation_filter.py`

**Action:**
- Replace direct `config.get('api_key')` access with centralized manager
- Remove hardcoded API key references
- Add proper error handling for missing keys

**Before:**
```python
self.api_key = config.get('api_key')
```

**After:**
```python
from ..core.api_key_manager import get_api_key
self.api_key = get_api_key('openai')
```

#### 2.2 Update Demo and Example Files
**Files to Update:**
- `demos/tech_support/demo_utils.py`
- `examples/getting_started/*.py`
- Any other files using direct environment variable access

**Action:**
- Replace `os.environ.get("OPENAI_API_KEY")` with centralized access
- Add proper error handling and user guidance
- Update documentation references

#### 2.3 Add Configuration Validation
**File:** `src/stinger/core/config.py`  
**Priority:** HIGH

**Action:**
- Add API key configuration validation to `ConfigLoader`
- Validate that required API keys are available
- Provide clear error messages for missing configuration

**Implementation:**
```python
def validate_api_keys(self, config: Dict[str, Any]) -> None:
    """Validate API key configuration."""
    from .api_key_manager import validate_api_key_config
    
    # Check for unresolved environment variables
    unresolved_vars = self._find_unresolved_env_vars(config)
    if unresolved_vars:
        raise ConfigurationError(f"Unresolved environment variables: {unresolved_vars}")
    
    # Validate API key availability
    key_status = validate_api_key_config()
    missing_keys = [service for service, available in key_status.items() if not available]
    if missing_keys:
        raise ConfigurationError(f"Missing API keys for services: {missing_keys}")
```

### **Phase 3: Security Hardening (Day 3)**

#### 3.1 Improve Encryption Key Management
**File:** `src/stinger/core/api_key_manager.py`  
**Priority:** MEDIUM

**Action:**
- Implement persistent encryption key storage
- Add secure key generation and rotation
- Improve encryption key backup and recovery

**Implementation:**
```python
def _get_encryption_key_path(self) -> Path:
    """Get path to stored encryption key."""
    return Path.home() / '.stinger' / '.encryption_key'

def _load_or_generate_encryption_key(self) -> str:
    """Load existing encryption key or generate new one."""
    key_path = self._get_encryption_key_path()
    
    if key_path.exists():
        with open(key_path, 'r') as f:
            return f.read().strip()
    else:
        # Generate new key
        key = self._generate_encryption_key()
        key_path.parent.mkdir(mode=0o700, exist_ok=True)
        with open(key_path, 'w') as f:
            f.write(key)
        key_path.chmod(0o600)
        return key
```

#### 3.2 Add API Key Usage Monitoring
**File:** `src/stinger/core/api_key_manager.py`  
**Priority:** MEDIUM

**Action:**
- Add usage tracking for API keys
- Monitor for unusual usage patterns
- Add rate limiting per API key

**Implementation:**
```python
def track_api_key_usage(self, service: str, operation: str) -> None:
    """Track API key usage for monitoring."""
    # Implementation for usage tracking
    pass

def get_usage_stats(self, service: str) -> Dict[str, Any]:
    """Get usage statistics for API key."""
    # Implementation for usage statistics
    pass
```

#### 3.3 Improve Error Handling and Logging
**Priority:** MEDIUM

**Action:**
- Add structured logging for API key operations
- Improve error messages for missing/invalid keys
- Add audit trail for API key access

### **Phase 4: Documentation and Testing (Day 4-5)**

#### 4.1 Create Comprehensive API Key Documentation
**File:** `docs/API_KEY_MANAGEMENT.md`  
**Priority:** HIGH

**Content:**
- Overview of API key management architecture
- Environment variable setup guide
- Configuration file examples
- Security best practices
- Troubleshooting guide
- Migration guide from old patterns

**Structure:**
```markdown
# API Key Management Guide

## Overview
- Centralized API key management system
- Environment variable support
- Encrypted storage options
- Security features

## Setup
- Environment variables
- Configuration files
- Secure storage

## Best Practices
- Never commit API keys to version control
- Use environment variables in production
- Enable encryption for sensitive deployments
- Regular key rotation

## Troubleshooting
- Common issues and solutions
- Debugging missing keys
- Error message explanations
```

#### 4.2 Update Existing Documentation
**Files to Update:**
- `docs/GETTING_STARTED.md`
- `docs/API_REFERENCE.md`
- `docs/EXTENSIBILITY_GUIDE.md`
- `README.md`

**Action:**
- Update all API key references to use new patterns
- Add security warnings and best practices
- Update examples to use centralized manager
- Add migration notes for existing users

#### 4.3 Comprehensive Testing
**Priority:** HIGH

**Action:**
- Create test suite for environment variable substitution
- Test API key validation and error handling
- Test encryption/decryption functionality
- Test configuration loading with various scenarios
- Integration tests for all filter types

**Test Files to Create:**
- `tests/test_api_key_security.py`
- `tests/test_config_loader_env_substitution.py`
- `tests/test_api_key_manager_integration.py`

### **Phase 5: Cleanup and Validation (Day 5)**

#### 5.1 Remove Insecure Files
**Action:**
- Delete `test_api_keys.yaml` after confirming it's in .gitignore
- Remove any other test files with API key placeholders
- Clean up any temporary files

#### 5.2 Security Review
**Action:**
- Run security audit tools
- Review all API key access patterns
- Verify no hardcoded keys remain
- Check for any remaining security issues

#### 5.3 Final Validation
**Action:**
- Test all filters with new API key management
- Verify environment variable substitution works
- Test encryption functionality
- Validate documentation is complete and accurate

## 🔧 **IMPLEMENTATION DETAILS**

### **Environment Variable Substitution Implementation**

```python
import os
import re
from typing import Dict, Any

class ConfigLoader:
    def _substitute_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively substitute environment variables in config."""
        if isinstance(config, dict):
            return {k: self._substitute_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._substitute_env_vars(item) for item in config]
        elif isinstance(config, str):
            # Replace ${VAR} with environment variable values
            def replace_var(match):
                var_name = match.group(1)
                value = os.getenv(var_name)
                if value is None:
                    raise ConfigurationError(f"Environment variable {var_name} not set")
                return value
            return re.sub(r'\$\{([^}]+)\}', replace_var, config)
        return config
    
    def load(self, config_path: str) -> Dict[str, Any]:
        """Load and process configuration file."""
        # Load YAML
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Substitute environment variables
        config = self._substitute_env_vars(config)
        
        # Validate configuration
        self._validate_config(config)
        
        return config
```

### **Unified API Key Access Pattern**

```python
# src/stinger/core/api_key_manager.py

# Global instance
_api_key_manager = None

def _get_api_key_manager() -> APIKeyManager:
    """Get or create global API key manager instance."""
    global _api_key_manager
    if _api_key_manager is None:
        _api_key_manager = APIKeyManager()
    return _api_key_manager

def get_api_key(service: str = 'openai') -> Optional[str]:
    """Get API key for specified service."""
    return _get_api_key_manager().get_key(service)

def validate_api_key_config() -> Dict[str, bool]:
    """Validate all API key configurations."""
    return _get_api_key_manager().health_check()

def set_api_key(service: str, key: str, encrypt: bool = True) -> bool:
    """Set API key for specified service."""
    return _get_api_key_manager().set_key(service, key, encrypt)
```

## 📊 **SUCCESS CRITERIA**

### **Must Have (Critical)**
- [ ] Environment variable substitution works in all config files
- [ ] All filters use centralized API key manager
- [ ] No hardcoded API keys in codebase
- [ ] `test_api_keys.yaml` properly excluded from version control
- [ ] Configuration validation catches missing API keys
- [ ] Clear error messages for missing/invalid keys

### **Should Have (Important)**
- [ ] Comprehensive documentation created
- [ ] All examples updated to use new patterns
- [ ] Encryption key management improved
- [ ] Usage monitoring implemented
- [ ] Security audit passes

### **Nice to Have (Optional)**
- [ ] API key rotation functionality
- [ ] Integration with external secret managers
- [ ] Advanced usage analytics
- [ ] Automated security scanning

## 🚀 **ROLLOUT PLAN**

### **Pre-Rollout**
1. Create backup of current configuration
2. Document current API key setup for each environment
3. Prepare rollback plan

### **Rollout Steps**
1. Deploy environment variable substitution
2. Update configuration files
3. Test in development environment
4. Update documentation
5. Deploy to staging
6. Final testing
7. Deploy to production

### **Post-Rollout**
1. Monitor for any issues
2. Collect feedback from users
3. Update documentation based on feedback
4. Schedule follow-up security review

## 📝 **DOCUMENTATION DELIVERABLES**

1. **API Key Management Guide** (`docs/API_KEY_MANAGEMENT.md`)
2. **Updated Getting Started Guide** (`docs/GETTING_STARTED.md`)
3. **Security Best Practices** (`docs/SECURITY.md`)
4. **Migration Guide** (`docs/MIGRATION.md`)
5. **Troubleshooting Guide** (`docs/TROUBLESHOOTING.md`)

## 🔍 **VALIDATION CHECKLIST**

### **Before Deployment**
- [ ] All tests pass
- [ ] Security audit completed
- [ ] Documentation reviewed
- [ ] Configuration files updated
- [ ] Environment variables documented

### **After Deployment**
- [ ] All filters working correctly
- [ ] API keys loading properly
- [ ] Error handling working
- [ ] Documentation accessible
- [ ] No security issues found

## 🗑️ **CLEANUP**

Once this plan is completed and validated:
1. Delete this plan file
2. Update project status
3. Archive any temporary files
4. Update version history
5. Schedule regular security reviews

---

**Note:** This plan addresses critical security issues and should be completed as soon as possible. The centralized API key management system is well-designed but not being utilized properly due to missing infrastructure components. 