# Phase 5 Execution Plan – Conversation API & Advanced Features

**Status: ✅ COMPLETED**  
**Start Date**: 2025-06-25  
**Completion Date**: 2025-06-25  

## �� Phase 5 Objective

## Overview
Phase 5 implements content moderation and prompt injection detection using OpenAI APIs. This phase adds two new filters that leverage OpenAI's advanced language models for sophisticated content analysis. The prompt injection detection uses GPT-4.1-nano for fast, cost-effective analysis while maintaining high accuracy.

## Objectives
1. **OpenAI Content Moderation**: Implement content moderation using OpenAI Moderation API
2. **Prompt Injection Detection**: Implement prompt injection detection using OpenAI GPT models
3. **Simple Error Handling**: Handle API failures with basic try/catch and fallback
4. **Graceful Degradation**: System continues operating when OpenAI APIs are down

## Architecture Design

### OpenAI Adapter Interface
```python
class OpenAIAdapter:
    """Adapter for OpenAI API services."""
    
    async def moderate_content(self, content: str) -> ModerationResult:
        """Moderate content using OpenAI Moderation API."""
        pass
    
    async def detect_prompt_injection(self, content: str) -> InjectionResult:
        """Detect prompt injection using OpenAI GPT-4.1-nano model.
        
        Uses a specialized security analyst prompt to classify injection attempts
        and returns structured results with risk assessment.
        """
        pass
    
    async def health_check(self) -> HealthStatus:
        """Check OpenAI API health and availability."""
        pass
```

### Result Structures
```python
@dataclass
class ModerationResult:
    flagged: bool
    categories: Dict[str, bool]  # hate, harassment, self_harm, sexual, violence, etc.
    category_scores: Dict[str, float]
    confidence: float

@dataclass
class InjectionResult:
    detected: bool
    risk_percent: int  # 0-100 (higher = more likely injection)
    level: str  # "low", "medium", "high", "critical"
    indicators: List[str]  # Array of evidence strings
    comment: str  # Summary reasoning
    confidence: float  # Derived from risk_percent
```

### API Key Management Architecture
```python
class APIKeyManager:
    """Centralized API key management with security features."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize with optional config file path."""
        pass
    
    def get_openai_key(self) -> str:
        """Get OpenAI API key securely."""
        pass
    
    def validate_key(self, service: str, key: str) -> bool:
        """Validate API key format and basic connectivity."""
        pass
    
    def rotate_key(self, service: str) -> bool:
        """Rotate API key for specified service."""
        pass
    
    def health_check(self) -> Dict[str, bool]:
        """Check health of all configured API keys."""
        pass
```

### Security Features
- **Environment Variables**: Primary source for API keys (OPENAI_API_KEY)
- **Encrypted Storage**: Optional encrypted local storage for development
- **Key Validation**: Format validation and basic connectivity checks
- **Usage Logging**: Log key usage without exposing actual keys
- **Rotation Support**: Support for key rotation workflows
- **Health Monitoring**: Monitor key validity and service availability

### Pluggable Guardrail Interface
```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class GuardrailInterface(ABC):
    """Universal interface for all guardrails to ensure pluggability."""
    
    @abstractmethod
    async def analyze(self, content: str) -> GuardrailResult:
        """Analyze content and return standardized result."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Return the name/identifier of this guardrail."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this guardrail is available/healthy."""
        pass

@dataclass
class GuardrailResult:
    """Standardized result format for all guardrails."""
    blocked: bool
    confidence: float
    reason: str
    details: Dict[str, Any]
    guardrail_name: str
```

### Example Implementations
```python
# Simple blocklist implementation
class BlocklistGuardrail(GuardrailInterface):
    """Simple blocklist-based guardrail."""
    
    def __init__(self, name: str, blocked_terms: List[str]):
        self.name = name
        self.blocked_terms = blocked_terms
    
    async def analyze(self, content: str) -> GuardrailResult:
        # Simple keyword matching logic
        pass

# OpenAI content moderation
class OpenAIContentModeration(GuardrailInterface):
    """OpenAI API-based content moderation."""
    
    def __init__(self, name: str, api_key: str):
        self.name = name
        self.adapter = OpenAIAdapter(api_key)
    
    async def analyze(self, content: str) -> GuardrailResult:
        # OpenAI API logic
        pass

# Regex prompt injection
class RegexPromptInjection(GuardrailInterface):
    """Regex-based prompt injection detection."""
    
    def __init__(self, name: str, patterns: List[str]):
        self.name = name
        self.patterns = patterns
    
    async def analyze(self, content: str) -> GuardrailResult:
        # Regex pattern matching logic
        pass

# OpenAI prompt injection
class OpenAIPromptInjection(GuardrailInterface):
    """OpenAI API-based prompt injection detection."""
    
    def __init__(self, name: str, api_key: str):
        self.name = name
        self.adapter = OpenAIAdapter(api_key)
    
    async def analyze(self, content: str) -> GuardrailResult:
        # OpenAI API logic
        pass
```

## Implementation Steps

### Step 1: Universal Guardrail Interface System
**Duration**: 2-3 days
**Deliverables**:
- `src/core/guardrail_interface.py` - Universal interface for all guardrails
- `src/core/guardrail_result.py` - Standardized result structures
- `src/core/guardrail_registry.py` - Registry for managing guardrail implementations
- `src/core/guardrail_factory.py` - Factory for creating guardrail instances

**Tasks**:
- [ ] Define universal GuardrailInterface with standardized methods
- [ ] Create GuardrailResult data structure for consistent results
- [ ] Implement guardrail registry for dynamic loading
- [ ] Create factory pattern for guardrail instantiation
- [ ] Write comprehensive unit tests for interface contracts
- [ ] Create example implementations (blocklist, regex, OpenAI)

### Step 2: API Key Management System
**Duration**: 1-2 days
**Deliverables**:
- `src/core/api_key_manager.py` - Centralized API key management
- `src/core/security.py` - Security utilities for key handling
- `configs/api_keys_template.yaml` - Template for API key configuration
- Environment variable integration

**Tasks**:
- [ ] Create centralized API key manager with encryption
- [ ] Implement secure key loading from environment variables
- [ ] Add key rotation and validation capabilities
- [ ] Create key health checking and monitoring
- [ ] Add logging for key usage (without exposing keys)
- [ ] Write unit tests for key management security
- [ ] Create configuration templates for different environments

### Step 3: OpenAI Adapter Implementation
**Duration**: 2-3 days
**Deliverables**:
- `src/adapters/openai_adapter.py` - OpenAI API adapter
- `src/adapters/result_structures.py` - Result data structures
- `src/adapters/error_handler.py` - Simple error handling utilities

**Tasks**:
- [ ] Implement OpenAI Moderation API client
- [ ] Implement OpenAI GPT-4.1-nano API client for prompt injection detection
- [ ] Create result data structures for moderation and injection detection
- [ ] Add simple error handling with try/catch patterns
- [ ] Integrate with API key manager for secure key access
- [ ] Add key validation and health checking
- [ ] Write unit tests for adapter interface

### Step 4: Guardrail Implementations
**Duration**: 3-4 days
**Deliverables**:
- `src/guardrails/blocklist_guardrail.py` - Simple blocklist implementation
- `src/guardrails/regex_guardrail.py` - Regex pattern matching implementation
- `src/guardrails/openai_content_moderation.py` - OpenAI content moderation
- `src/guardrails/openai_prompt_injection.py` - OpenAI prompt injection detection
- `configs/guardrails_phase5.yaml` - Guardrail configuration

**Tasks**:
- [ ] Create blocklist-based guardrail (universal interface)
- [ ] Create regex-based guardrail (universal interface)
- [ ] Create OpenAI content moderation guardrail (universal interface)
- [ ] Create OpenAI prompt injection guardrail (universal interface)
- [ ] Add configuration for switching between any implementations
- [ ] Create comprehensive test scenarios for all implementations
- [ ] Add performance benchmarks for all implementations
- [ ] Write integration tests with real examples
- [ ] Implement fallback logic when APIs are unavailable

### Step 5: Integration & Testing
**Duration**: 2-3 days
**Deliverables**:
- Enhanced pipeline with new filters
- Comprehensive test suite
- Updated documentation

**Tasks**:
- [ ] Integrate new filters into the pipeline
- [ ] Add graceful degradation when OpenAI APIs are down
- [ ] Create comprehensive test scenarios
- [ ] Update documentation with new filter usage
- [ ] Add configuration examples for both filters

## Success Criteria
- [ ] API key management system implemented and tested
- [ ] Secure key handling with environment variable support
- [ ] OpenAI content moderation filter implemented and tested
- [ ] OpenAI prompt injection detection filter implemented and tested
- [ ] Simple error handling working for API failures
- [ ] Graceful degradation when OpenAI services are unavailable
- [ ] Content moderation meets accuracy targets (95%+ precision, 90%+ recall)
- [ ] Prompt injection detection meets accuracy targets (90%+ precision, 85%+ recall)
- [ ] Comprehensive test coverage (>90% for new code)
- [ ] Documentation updated with OpenAI integration and key management
- [ ] Configuration examples provided for both filters and key management

## Risk Mitigation
- **API Rate Limits**: Implement rate limiting and retry logic
- **API Costs**: Monitor usage and implement cost controls (GPT-4.1-nano is cost-effective)
- **API Availability**: Implement fallback mechanisms
- **Model Changes**: Use stable API endpoints and versioning
- **Key Security**: Secure API key management with environment variables
- **Key Rotation**: Support for key rotation and validation

## Dependencies

### External Services
- OpenAI Moderation API
- Azure Content Safety API
- Redis (optional, for caching)

### Internal Dependencies
- Phase 4c completion (simplified architecture)
- Async/await support in Python
- Configuration management system
- Test framework

## Timeline
- **Total Duration**: 20-25 days
- **Parallel Work**: Steps 2-6 can be worked on in parallel
- **Critical Path**: Adapter interface → OpenAI adapter → Integration testing
- **Milestones**: 
  - Week 1: Adapter interface and OpenAI integration
  - Week 2: Azure integration and PII/Toxicity filters
  - Week 3: Jailbreak/Prompt injection and performance optimization
  - Week 4: Integration testing and documentation

## Next Steps
1. Review and approve this execution plan
2. Set up development environment with API access
3. Begin implementation with adapter interface
4. Create test corpora for validation
5. Establish monitoring and metrics collection

## Configuration Examples

### OpenAI Content Moderation Configuration
```yaml
filters:
  - name: "openai_content_moderation"
    type: "openai_content_moderation"
    enabled: true
    api_key: "${OPENAI_API_KEY}"
    categories: ["hate", "harassment", "violence", "sexual", "self_harm"]
    confidence_threshold: 0.7
    on_error: "allow"
```

### OpenAI Prompt Injection Detection Configuration
```yaml
filters:
  - name: "openai_prompt_injection"
    type: "openai_prompt_injection"
    enabled: true
    api_key: "${OPENAI_API_KEY}"
    model: "gpt-4.1-nano"  # Fast and cost-effective model
    risk_thresholds:
      low: 25
      medium: 50
      high: 75
      critical: 90
    block_levels: ["high", "critical"]  # Block high and critical risk levels
    on_error: "warn"
```

### API Key Configuration Template
```yaml
# configs/api_keys_template.yaml
# Copy this to api_keys.yaml and fill in your actual keys
# NEVER commit api_keys.yaml to version control

api_keys:
  openai:
    api_key: "${OPENAI_API_KEY}"  # Set via environment variable
    organization: "${OPENAI_ORG_ID}"  # Optional
    model: "gpt-4.1-nano"
  
  # Future services can be added here
  # azure:
  #   endpoint: "${AZURE_ENDPOINT}"
  #   api_key: "${AZURE_API_KEY}"

security:
  # Enable encrypted local storage (development only)
  encrypted_storage: false
  encryption_key: "${ENCRYPTION_KEY}"  # For local encrypted storage
  
  # Key validation settings
  validate_on_startup: true
  health_check_interval: 300  # seconds
  
  # Logging settings
  log_usage: true
  log_errors: true
  mask_keys_in_logs: true
```

### Environment Variables Setup
```bash
# Required environment variables
export OPENAI_API_KEY="sk-..."
export OPENAI_ORG_ID="org-..."  # Optional

# Optional for encrypted local storage
export ENCRYPTION_KEY="your-encryption-key"
```

### Content Moderation Configuration (Swappable)
```yaml
filters:
  - name: "content_moderation"
    type: "content_moderation"
    enabled: true
    implementation: "openai"  # or "blocklist"
    
    # OpenAI implementation config
    openai:
      api_key: "${OPENAI_API_KEY}"
      categories: ["hate", "harassment", "violence", "sexual", "self_harm"]
      confidence_threshold: 0.7
      on_error: "allow"
    
    # Blocklist implementation config
    blocklist:
      blocked_terms: ["term1", "term2", "term3"]
      case_sensitive: false
      on_error: "block"
```

### Prompt Injection Configuration (Swappable)
```yaml
filters:
  - name: "prompt_injection"
    type: "prompt_injection"
    enabled: true
    implementation: "openai"  # or "regex"
    
    # OpenAI implementation config
    openai:
      api_key: "${OPENAI_API_KEY}"
      model: "gpt-4.1-nano"
      risk_thresholds:
        low: 25
        medium: 50
        high: 75
        critical: 90
      block_levels: ["high", "critical"]
      on_error: "warn"
    
    # Regex implementation config
    regex:
      patterns:
        - "ignore previous instructions"
        - "you are now"
        - "system prompt"
        - "role play"
      case_sensitive: false
      on_error: "block"
```

### Universal Guardrail Configuration
```yaml
# configs/guardrails_phase5.yaml
# Mix and match any guardrails - they all use the same interface

guardrails:
  # Content moderation - choose one or combine multiple
  - name: "content_moderation_blocklist"
    type: "blocklist"
    enabled: true
    blocked_terms: ["term1", "term2", "term3"]
    case_sensitive: false
    on_error: "block"
  
  - name: "content_moderation_openai"
    type: "openai_content_moderation"
    enabled: true
    api_key: "${OPENAI_API_KEY}"
    categories: ["hate", "harassment", "violence", "sexual", "self_harm"]
    confidence_threshold: 0.7
    on_error: "allow"
  
  # Prompt injection - choose one or combine multiple
  - name: "prompt_injection_regex"
    type: "regex"
    enabled: true
    patterns:
      - "ignore previous instructions"
      - "you are now"
      - "system prompt"
      - "role play"
    case_sensitive: false
    on_error: "block"
  
  - name: "prompt_injection_openai"
    type: "openai_prompt_injection"
    enabled: true
    api_key: "${OPENAI_API_KEY}"
    model: "gpt-4.1-nano"
    risk_thresholds:
      low: 25
      medium: 50
      high: 75
      critical: 90
    block_levels: ["high", "critical"]
    on_error: "warn"
  
  # Future guardrails can be added here with the same interface
  # - name: "pii_detection"
  #   type: "regex_pii"
  #   enabled: true
  #   patterns: ["ssn", "credit_card", "email"]
  #   on_error: "block"
``` 