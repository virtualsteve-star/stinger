# Phase 5a Execution Plan – OpenAI Integration & Content Moderation

**Status: ✅ COMPLETED**  
**Start Date**: 2025-06-25  
**Completion Date**: 2025-06-28  

## 🎯 Phase 5a Objective

## Overview
Phase 5a implements three additional classifier filter categories, each with both simple (regex/blocklist) and AI-based implementations: PII detection, toxicity detection, and code generation detection. This dual approach provides flexibility for different use cases - simple filters for speed and cost-effectiveness, AI-based filters for higher accuracy and context understanding.

## Objectives
1. **PII Detection Filters**: Implement both regex-based and AI-based detection of sensitive personal information
2. **Toxicity Detection Filters**: Implement both regex-based and AI-based detection of toxic content
3. **Code Generation Filters**: Implement both regex-based and AI-based detection of code injection attempts
4. **Enhanced Pattern Libraries**: Create comprehensive regex pattern libraries for simple implementations
5. **AI-Powered Detection**: Leverage OpenAI for higher accuracy detection
6. **Comprehensive Test Corpora**: Develop validation data for both filter types

## Architecture Design

### Centralized Model Configuration System

Before implementing the individual filters, we'll create a centralized model configuration system that provides a unified abstraction for AI models across all filters.

#### Model Configuration
```python
# configs/models.yaml
models:
  default: "gpt-4.1-nano"  # Always use gpt-4.1-nano, NOT gpt-4o-mini
  
  filters:
    content_moderation: "gpt-4.1-nano"
    prompt_injection: "gpt-4.1-nano"
    pii_detection: "gpt-4.1-nano"
    toxicity_detection: "gpt-4.1-nano"
    code_generation: "gpt-4.1-nano"
  
  settings:
    temperature: 0.1
    max_tokens: 500
    timeout: 30
```

#### Model Abstraction Factory
```python
class ModelProvider:
    """Abstract interface for model providers."""
    
    @abstractmethod
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate a response from the model."""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get the name of the model being used."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the model is available."""
        pass

class OpenAIModelProvider(ModelProvider):
    """OpenAI model provider implementation."""
    
    def __init__(self, model_name: str, api_key: str, **kwargs):
        self.model_name = model_name
        self.client = AsyncOpenAI(api_key=api_key)
        self.temperature = kwargs.get('temperature', 0.1)
        self.max_tokens = kwargs.get('max_tokens', 500)
        self.timeout = kwargs.get('timeout', 30)
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate a response using OpenAI API."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=kwargs.get('temperature', self.temperature),
                max_tokens=kwargs.get('max_tokens', self.max_tokens)
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            raise ModelError(f"OpenAI API error: {e}")
    
    def get_model_name(self) -> str:
        return self.model_name
    
    def is_available(self) -> bool:
        return self.client is not None

class ModelFactory:
    """Factory for creating model providers."""
    
    def __init__(self, config_path: str = "configs/models.yaml"):
        self.config = self._load_config(config_path)
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load model configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            # Fallback to default configuration
            return {
                'default': 'gpt-4.1-nano',
                'filters': {
                    'content_moderation': 'gpt-4.1-nano',
                    'prompt_injection': 'gpt-4.1-nano',
                    'pii_detection': 'gpt-4.1-nano',
                    'toxicity_detection': 'gpt-4.1-nano',
                    'code_generation': 'gpt-4.1-nano'
                },
                'settings': {
                    'temperature': 0.1,
                    'max_tokens': 500,
                    'timeout': 30
                }
            }
    
    def create_model_provider(self, filter_type: str, api_key: str) -> ModelProvider:
        """Create a model provider for a specific filter type."""
        model_name = self.config['filters'].get(filter_type, self.config['default'])
        settings = self.config['settings']
        
        return OpenAIModelProvider(
            model_name=model_name,
            api_key=api_key,
            **settings
        )
    
    def get_model_name(self, filter_type: str) -> str:
        """Get the model name for a specific filter type."""
        return self.config['filters'].get(filter_type, self.config['default'])

### Filter Implementation Strategy

Each filter category will have two implementations:

1. **Simple Implementation** (Regex/Blocklist):
   - Fast execution (< 10ms per message)
   - No external API dependencies
   - Lower accuracy but high reliability
   - Cost-effective for high-volume processing

2. **AI Implementation** (OpenAI-based):
   - Higher accuracy and context understanding
   - Slower execution (200-500ms per message)
   - Requires OpenAI API access
   - Better handling of edge cases and context

### PII Detection Filters

#### Simple PII Detection Filter
```python
class SimplePIIDetectionFilter(GuardrailInterface):
    """Regex-based PII detection filter."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.pii_patterns = {
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b',
            'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
        }
        self.enabled_patterns = config.get('patterns', list(self.pii_patterns.keys()))
        self.confidence_threshold = config.get('confidence_threshold', 0.8)
    
    async def analyze(self, content: str) -> GuardrailResult:
        """Analyze content for PII patterns using regex."""
        detected_pii = []
        confidence_scores = {}
        
        for pii_type, pattern in self.pii_patterns.items():
            if pii_type in self.enabled_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    detected_pii.append(pii_type)
                    confidence_scores[pii_type] = min(0.9, 0.5 + len(matches) * 0.1)
        
        if detected_pii:
            max_confidence = max(confidence_scores.values())
            blocked = max_confidence >= self.confidence_threshold
            
            return GuardrailResult(
                blocked=blocked,
                confidence=max_confidence,
                reason=f"PII detected (regex): {', '.join(detected_pii)}",
                details={
                    'detected_pii': detected_pii,
                    'confidence_scores': confidence_scores,
                    'method': 'regex'
                },
                guardrail_name=self.name,
                guardrail_type=GuardrailType.PII_DETECTION
            )
        else:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="No PII detected (regex)",
                details={'detected_pii': [], 'confidence_scores': {}, 'method': 'regex'},
                guardrail_name=self.name,
                guardrail_type=GuardrailType.PII_DETECTION
            )
```

#### AI-Based PII Detection Filter
```python
class AIPIIDetectionFilter(GuardrailInterface):
    """AI-based PII detection filter using centralized model configuration."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.api_key = config.get('api_key')
        self.confidence_threshold = config.get('confidence_threshold', 0.8)
        
        # Use centralized model factory
        self.model_factory = ModelFactory()
        self.model_provider = self.model_factory.create_model_provider('pii_detection', self.api_key) if self.api_key else None
        
        self.pii_prompt = """
You are a data privacy specialist. Analyze the following text and identify any Personally Identifiable Information (PII).

PII includes:
- Social Security Numbers (SSN)
- Credit card numbers
- Email addresses
- Phone numbers
- IP addresses
- Driver's license numbers
- Passport numbers
- Bank account numbers

Respond with a JSON object containing:
- "detected": boolean (true if PII detected)
- "pii_types": array of strings (types of PII found)
- "confidence": float (0.0 to 1.0)
- "details": string (brief explanation)

Text to analyze: {content}
"""
    
    async def analyze(self, content: str) -> GuardrailResult:
        """Analyze content for PII using AI with centralized model configuration."""
        if not self.model_provider:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="AI PII detection unavailable - no API key",
                details={'error': 'no_api_key', 'method': 'ai', 'model': 'none'},
                guardrail_name=self.name,
                guardrail_type=GuardrailType.PII_DETECTION
            )
        
        try:
            # Use centralized model provider
            response_content = await self.model_provider.generate_response(
                self.pii_prompt.format(content=content)
            )
            
            if response_content:
                import json
                try:
                    data = json.loads(response_content.strip())
                    
                    detected = data.get("detected", False)
                    pii_types = data.get("pii_types", [])
                    confidence = data.get("confidence", 0.0)
                    
                    blocked = detected and confidence >= self.confidence_threshold
                    
                    return GuardrailResult(
                        blocked=blocked,
                        confidence=confidence,
                        reason=f"PII detected (AI): {', '.join(pii_types)}" if detected else "No PII detected (AI)",
                        details={
                            'detected_pii': pii_types,
                            'confidence': confidence,
                            'method': 'ai',
                            'model': self.model_provider.get_model_name()
                        },
                        guardrail_name=self.name,
                        guardrail_type=GuardrailType.PII_DETECTION
                    )
                except json.JSONDecodeError:
                    return self._fallback_result(content)
            
        except Exception as e:
            return self._fallback_result(content, str(e))
    
    def _fallback_result(self, content: str, error: str = "AI analysis failed") -> GuardrailResult:
        """Fallback to simple regex detection when AI fails."""
        simple_filter = SimplePIIDetectionFilter(self.name, {'confidence_threshold': self.confidence_threshold})
        return await simple_filter.analyze(content)
```

### Toxicity Detection Filters

#### Simple Toxicity Detection Filter
```python
class SimpleToxicityDetectionFilter(GuardrailInterface):
    """Regex-based toxicity detection filter."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.toxicity_patterns = {
            'hate_speech': [
                r'\b(nazi|fascist|racist|bigot|homophobe)\b',
                r'\b(kill\s+all|exterminate|genocide)\b'
            ],
            'harassment': [
                r'\b(stalk|harass|bully|intimidate)\b',
                r'\b(you\s+suck|you\re\s+stupid|you\re\s+worthless)\b'
            ],
            'threats': [
                r'\b(i\s+will\s+kill|i\s+will\s+hurt|i\s+will\s+destroy)\b',
                r'\b(you\s+will\s+die|you\s+will\s+pay)\b'
            ],
            'sexual_harassment': [
                r'\b(sexual|nude|porn|explicit)\b.*\b(harass|assault|abuse)\b'
            ]
        }
        self.enabled_categories = config.get('categories', list(self.toxicity_patterns.keys()))
        self.confidence_threshold = config.get('confidence_threshold', 0.7)
    
    async def analyze(self, content: str) -> GuardrailResult:
        """Analyze content for toxicity patterns using regex."""
        detected_toxicity = []
        confidence_scores = {}
        
        for category, patterns in self.toxicity_patterns.items():
            if category in self.enabled_categories:
                category_matches = 0
                for pattern in patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    category_matches += len(matches)
                
                if category_matches > 0:
                    detected_toxicity.append(category)
                    confidence_scores[category] = min(0.95, 0.3 + category_matches * 0.2)
        
        if detected_toxicity:
            max_confidence = max(confidence_scores.values())
            blocked = max_confidence >= self.confidence_threshold
            
            return GuardrailResult(
                blocked=blocked,
                confidence=max_confidence,
                reason=f"Toxic content detected (regex): {', '.join(detected_toxicity)}",
                details={
                    'detected_toxicity': detected_toxicity,
                    'confidence_scores': confidence_scores,
                    'method': 'regex'
                },
                guardrail_name=self.name,
                guardrail_type=GuardrailType.TOXICITY_DETECTION
            )
        else:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="No toxic content detected (regex)",
                details={'detected_toxicity': [], 'confidence_scores': {}, 'method': 'regex'},
                guardrail_name=self.name,
                guardrail_type=GuardrailType.TOXICITY_DETECTION
            )
```

#### AI-Based Toxicity Detection Filter
```python
class AIToxicityDetectionFilter(GuardrailInterface):
    """AI-based toxicity detection filter using centralized model configuration."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.api_key = config.get('api_key')
        self.confidence_threshold = config.get('confidence_threshold', 0.7)
        
        # Use centralized model factory
        self.model_factory = ModelFactory()
        self.model_provider = self.model_factory.create_model_provider('toxicity_detection', self.api_key) if self.api_key else None
        
        self.toxicity_prompt = """
You are a content moderation specialist. Analyze the following text for toxic content.

Toxic content includes:
- Hate speech and discrimination
- Harassment and bullying
- Threats and violence
- Sexual harassment
- Explicit or inappropriate content

Respond with a JSON object containing:
- "detected": boolean (true if toxic content detected)
- "toxicity_types": array of strings (types of toxicity found)
- "confidence": float (0.0 to 1.0)
- "details": string (brief explanation)

Text to analyze: {content}
"""
    
    async def analyze(self, content: str) -> GuardrailResult:
        """Analyze content for toxicity using AI with centralized model configuration."""
        if not self.model_provider:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="AI toxicity detection unavailable - no API key",
                details={'error': 'no_api_key', 'method': 'ai', 'model': 'none'},
                guardrail_name=self.name,
                guardrail_type=GuardrailType.TOXICITY_DETECTION
            )
        
        try:
            # Use centralized model provider
            response_content = await self.model_provider.generate_response(
                self.toxicity_prompt.format(content=content)
            )
            
            if response_content:
                import json
                try:
                    data = json.loads(response_content.strip())
                    
                    detected = data.get("detected", False)
                    toxicity_types = data.get("toxicity_types", [])
                    confidence = data.get("confidence", 0.0)
                    
                    blocked = detected and confidence >= self.confidence_threshold
                    
                    return GuardrailResult(
                        blocked=blocked,
                        confidence=confidence,
                        reason=f"Toxic content detected (AI): {', '.join(toxicity_types)}" if detected else "No toxic content detected (AI)",
                        details={
                            'detected_toxicity': toxicity_types,
                            'confidence': confidence,
                            'method': 'ai',
                            'model': self.model_provider.get_model_name()
                        },
                        guardrail_name=self.name,
                        guardrail_type=GuardrailType.TOXICITY_DETECTION
                    )
                except json.JSONDecodeError:
                    return self._fallback_result(content)
            
        except Exception as e:
            return self._fallback_result(content, str(e))
    
    def _fallback_result(self, content: str, error: str = "AI analysis failed") -> GuardrailResult:
        """Fallback to simple regex detection when AI fails."""
        simple_filter = SimpleToxicityDetectionFilter(self.name, {'confidence_threshold': self.confidence_threshold})
        return await simple_filter.analyze(content)
```

### Code Generation Filters

#### Simple Code Generation Filter
```python
class SimpleCodeGenerationFilter(GuardrailInterface):
    """Regex-based code generation detection filter."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.code_patterns = {
            'code_blocks': [
                r'```[\w]*\n.*?\n```',  # Markdown code blocks
                r'`.*?`',  # Inline code
                r'<code>.*?</code>',  # HTML code tags
                r'<pre>.*?</pre>'  # HTML pre tags
            ],
            'programming_keywords': [
                r'\b(function|def|class|import|export|require|var|let|const)\b',
                r'\b(if|else|for|while|switch|case|break|continue|return)\b',
                r'\b(public|private|protected|static|final|abstract|interface)\b'
            ],
            'code_injection': [
                r'\b(eval|exec|system|shell|bash|python|javascript|php)\b',
                r'\b(script|alert|console\.log|document\.write)\b',
                r'\b(sql|query|database|table|select|insert|update|delete)\b'
            ],
            'file_operations': [
                r'\b(file|read|write|open|close|delete|remove|create)\b',
                r'\b(path|directory|folder|mkdir|rmdir|chmod|chown)\b'
            ]
        }
        self.enabled_categories = config.get('categories', list(self.code_patterns.keys()))
        self.confidence_threshold = config.get('confidence_threshold', 0.6)
        self.min_keywords = config.get('min_keywords', 3)
    
    async def analyze(self, content: str) -> GuardrailResult:
        """Analyze content for code generation patterns using regex."""
        detected_code = []
        confidence_scores = {}
        total_keywords = 0
        
        for category, patterns in self.code_patterns.items():
            if category in self.enabled_categories:
                category_matches = 0
                for pattern in patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    category_matches += len(matches)
                
                if category_matches > 0:
                    detected_code.append(category)
                    total_keywords += category_matches
                    base_confidence = 0.4 if category == 'code_blocks' else 0.2
                    confidence_scores[category] = min(0.9, base_confidence + category_matches * 0.15)
        
        if detected_code and total_keywords >= self.min_keywords:
            max_confidence = max(confidence_scores.values())
            blocked = max_confidence >= self.confidence_threshold
            
            return GuardrailResult(
                blocked=blocked,
                confidence=max_confidence,
                reason=f"Code generation detected (regex): {', '.join(detected_code)}",
                details={
                    'detected_code': detected_code,
                    'confidence_scores': confidence_scores,
                    'total_keywords': total_keywords,
                    'method': 'regex'
                },
                guardrail_name=self.name,
                guardrail_type=GuardrailType.CODE_GENERATION
            )
        else:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="No code generation detected (regex)",
                details={'detected_code': [], 'confidence_scores': {}, 'total_keywords': 0, 'method': 'regex'},
                guardrail_name=self.name,
                guardrail_type=GuardrailType.CODE_GENERATION
            )
```

#### AI-Based Code Generation Filter
```python
class AICodeGenerationFilter(GuardrailInterface):
    """AI-based code generation detection filter using centralized model configuration."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.api_key = config.get('api_key')
        self.confidence_threshold = config.get('confidence_threshold', 0.6)
        
        # Use centralized model factory
        self.model_factory = ModelFactory()
        self.model_provider = self.model_factory.create_model_provider('code_generation', self.api_key) if self.api_key else None
        
        self.code_prompt = """
You are a security analyst specializing in code injection detection. Analyze the following text and determine if it contains code generation or injection attempts.

Code generation/injection includes:
- Programming code blocks
- Code snippets and functions
- System commands and scripts
- Database queries
- File operations
- Code execution attempts

Respond with a JSON object containing:
- "detected": boolean (true if code generation detected)
- "code_types": array of strings (types of code found)
- "confidence": float (0.0 to 1.0)
- "details": string (brief explanation)

Text to analyze: {content}
"""
    
    async def analyze(self, content: str) -> GuardrailResult:
        """Analyze content for code generation using AI with centralized model configuration."""
        if not self.model_provider:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="AI code generation detection unavailable - no API key",
                details={'error': 'no_api_key', 'method': 'ai', 'model': 'none'},
                guardrail_name=self.name,
                guardrail_type=GuardrailType.CODE_GENERATION
            )
        
        try:
            # Use centralized model provider
            response_content = await self.model_provider.generate_response(
                self.code_prompt.format(content=content)
            )
            
            if response_content:
                import json
                try:
                    data = json.loads(response_content.strip())
                    
                    detected = data.get("detected", False)
                    code_types = data.get("code_types", [])
                    confidence = data.get("confidence", 0.0)
                    
                    blocked = detected and confidence >= self.confidence_threshold
                    
                    return GuardrailResult(
                        blocked=blocked,
                        confidence=confidence,
                        reason=f"Code generation detected (AI): {', '.join(code_types)}" if detected else "No code generation detected (AI)",
                        details={
                            'detected_code': code_types,
                            'confidence': confidence,
                            'method': 'ai',
                            'model': self.model_provider.get_model_name()
                        },
                        guardrail_name=self.name,
                        guardrail_type=GuardrailType.CODE_GENERATION
                    )
                except json.JSONDecodeError:
                    return self._fallback_result(content)
            
        except Exception as e:
            return self._fallback_result(content, str(e))
    
    def _fallback_result(self, content: str, error: str = "AI analysis failed") -> GuardrailResult:
        """Fallback to simple regex detection when AI fails."""
        simple_filter = SimpleCodeGenerationFilter(self.name, {'confidence_threshold': self.confidence_threshold})
        return await simple_filter.analyze(content)
```

## Implementation Steps

### Step 1: Centralized Model Configuration System
**Duration**: 1 day
**Deliverables**:
- `src/core/model_config.py` - Centralized model configuration system
- `configs/models.yaml` - Model configuration file
- Model abstraction factory and provider classes

**Tasks**:
- [ ] Create `ModelProvider` abstract interface
- [ ] Implement `OpenAIModelProvider` class
- [ ] Create `ModelFactory` for centralized model creation
- [ ] Create `configs/models.yaml` configuration file
- [ ] Add model configuration loading and validation
- [ ] Write unit tests for model configuration system
- [ ] Ensure all models default to "gpt-4.1-nano" (NOT gpt-4o-mini)

### Step 2: Update Guardrail Interface
**Duration**: 1 day
**Deliverables**:
- Update `GuardrailType` enum to include new filter types
- Add new filter types to the universal interface

**Tasks**:
- [ ] Add `PII_DETECTION`, `TOXICITY_DETECTION`, `CODE_GENERATION` to `GuardrailType`
- [ ] Update factory registration for new filter types
- [ ] Add new filter types to test suite

### Step 3: Simple Filter Implementations
**Duration**: 3 days
**Deliverables**:
- `src/filters/simple_pii_detection_filter.py`
- `src/filters/simple_toxicity_detection_filter.py`
- `src/filters/simple_code_generation_filter.py`
- Comprehensive regex pattern libraries

**Tasks**:
- [ ] Implement simple PII detection filter with regex patterns
- [ ] Implement simple toxicity detection filter with regex patterns
- [ ] Implement simple code generation filter with regex patterns
- [ ] Create comprehensive pattern libraries
- [ ] Write unit tests for simple filter implementations

### Step 4: AI-Based Filter Implementations
**Duration**: 3 days
**Deliverables**:
- `src/filters/ai_pii_detection_filter.py`
- `src/filters/ai_toxicity_detection_filter.py`
- `src/filters/ai_code_generation_filter.py`
- OpenAI integration for all filter types

**Tasks**:
- [ ] Implement AI-based PII detection filter using OpenAI
- [ ] Implement AI-based toxicity detection filter using OpenAI
- [ ] Implement AI-based code generation filter using OpenAI
- [ ] Add fallback mechanisms to simple filters
- [ ] Write unit tests for AI-based filter implementations

### Step 5: Integration & Testing
**Duration**: 2 days
**Deliverables**:
- Updated pipeline with all new filters
- Comprehensive test suite for both simple and AI implementations
- Configuration examples for all filter types

**Tasks**:
- [ ] Integrate all new filters into the pipeline
- [ ] Create comprehensive test scenarios for both implementations
- [ ] Update documentation with new filter usage
- [ ] Add configuration examples for all filters
- [ ] Create demo scripts for new filters

## Success Criteria
- [ ] Centralized model configuration system implemented and tested
- [ ] All AI filters use "gpt-4.1-nano" model (NOT gpt-4o-mini)
- [ ] Model abstraction factory provides unified interface for all AI filters
- [ ] Simple PII detection filter implemented and tested (accuracy ≥ 95%)
- [ ] AI-based PII detection filter implemented and tested (accuracy ≥ 98%)
- [ ] Simple toxicity detection filter implemented and tested (accuracy ≥ 90%)
- [ ] AI-based toxicity detection filter implemented and tested (accuracy ≥ 95%)
- [ ] Simple code generation filter implemented and tested (accuracy ≥ 85%)
- [ ] AI-based code generation filter implemented and tested (accuracy ≥ 90%)
- [ ] All filters integrate with universal guardrail interface
- [ ] Fallback mechanisms work correctly when AI is unavailable
- [ ] Comprehensive test coverage (>90% for new code)
- [ ] Configuration examples provided for all filter types

## Configuration Examples

### Model Configuration
```yaml
# configs/models.yaml
models:
  default: "gpt-4.1-nano"  # Always use gpt-4.1-nano, NOT gpt-4o-mini
  
  filters:
    content_moderation: "gpt-4.1-nano"
    prompt_injection: "gpt-4.1-nano"
    pii_detection: "gpt-4.1-nano"
    toxicity_detection: "gpt-4.1-nano"
    code_generation: "gpt-4.1-nano"
  
  settings:
    temperature: 0.1
    max_tokens: 500
    timeout: 30
```

### Simple PII Detection Configuration
```yaml
filters:
  - name: "simple_pii_detection"
    type: "simple_pii_detection"
    enabled: true
    patterns: ["ssn", "credit_card", "email", "phone", "ip_address"]
    confidence_threshold: 0.8
    on_error: "block"
```

### AI-Based PII Detection Configuration
```yaml
filters:
  - name: "ai_pii_detection"
    type: "ai_pii_detection"
    enabled: true
    api_key: "${OPENAI_API_KEY}"
    confidence_threshold: 0.8
    on_error: "allow"
    # Model is automatically configured from configs/models.yaml
```

### Simple Toxicity Detection Configuration
```yaml
filters:
  - name: "simple_toxicity_detection"
    type: "simple_toxicity_detection"
    enabled: true
    categories: ["hate_speech", "harassment", "threats", "sexual_harassment"]
    confidence_threshold: 0.7
    on_error: "block"
```

### AI-Based Toxicity Detection Configuration
```yaml
filters:
  - name: "ai_toxicity_detection"
    type: "ai_toxicity_detection"
    enabled: true
    api_key: "${OPENAI_API_KEY}"
    confidence_threshold: 0.7
    on_error: "allow"
    # Model is automatically configured from configs/models.yaml
```

### Simple Code Generation Configuration
```yaml
filters:
  - name: "simple_code_generation"
    type: "simple_code_generation"
    enabled: true
    categories: ["code_blocks", "programming_keywords", "code_injection", "file_operations"]
    confidence_threshold: 0.6
    min_keywords: 3
    on_error: "warn"
```

### AI-Based Code Generation Configuration
```yaml
filters:
  - name: "ai_code_generation"
    type: "ai_code_generation"
    enabled: true
    api_key: "${OPENAI_API_KEY}"
    confidence_threshold: 0.6
    on_error: "warn"
    # Model is automatically configured from configs/models.yaml
```

### Comprehensive Configuration (Both Simple and AI)
```yaml
filters:
  # Simple filters for speed and reliability
  - name: "simple_pii_detection"
    type: "simple_pii_detection"
    enabled: true
    patterns: ["ssn", "credit_card", "email", "phone"]
    confidence_threshold: 0.8
    on_error: "block"
  
  - name: "simple_toxicity_detection"
    type: "simple_toxicity_detection"
    enabled: true
    categories: ["hate_speech", "harassment", "threats"]
    confidence_threshold: 0.7
    on_error: "block"
  
  - name: "simple_code_generation"
    type: "simple_code_generation"
    enabled: true
    categories: ["code_blocks", "code_injection"]
    confidence_threshold: 0.6
    on_error: "warn"
  
  # AI-based filters for higher accuracy (using centralized model config)
  - name: "ai_pii_detection"
    type: "ai_pii_detection"
    enabled: true
    api_key: "${OPENAI_API_KEY}"
    confidence_threshold: 0.8
    on_error: "allow"
  
  - name: "ai_toxicity_detection"
    type: "ai_toxicity_detection"
    enabled: true
    api_key: "${OPENAI_API_KEY}"
    confidence_threshold: 0.7
    on_error: "allow"
  
  - name: "ai_code_generation"
    type: "ai_code_generation"
    enabled: true
    api_key: "${OPENAI_API_KEY}"
    confidence_threshold: 0.6
    on_error: "warn"
```

## Timeline
- **Total Duration**: 10 days
- **Critical Path**: Model config → Interface updates → Simple filters → AI filters → Integration
- **Milestones**: 
  - Week 1: Model configuration system and interface updates
  - Week 1: Simple filter implementations
  - Week 2: AI-based filter implementations and integration testing

## Next Steps
1. Review and approve this execution plan
2. Create GitHub issues for each filter implementation
3. Begin implementation with interface updates
4. Create test corpora for validation
5. Implement simple filters first, then AI-based filters 