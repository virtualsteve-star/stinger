# Extensibility Guide

**How to Create Custom Filters and Guardrails for Stinger**

This guide will teach you how to extend Stinger with your own custom filters, guardrails, and monitoring capabilities.

## 🏗️ Architecture Overview

Stinger is built around a modular architecture with these key components:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Conversation  │    │   Guardrail     │    │   Health        │
│   Management    │    │   Pipeline      │    │   Monitoring    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Filter        │
                    │   Interface     │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PII Filter    │    │  Toxicity       │    │  Custom Filter  │
│                 │    │  Filter         │    │  (Your Code)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 Creating Your First Custom Filter

### Step 1: Understand the Interface

All filters must implement the `GuardrailInterface`:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class GuardrailResult:
    blocked: bool
    confidence: float
    reason: str
    details: Dict[str, Any]

class GuardrailInterface(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the guardrail."""
        pass
    
    @property
    @abstractmethod
    def guardrail_type(self) -> GuardrailType:
        """Type of guardrail."""
        pass
    
    @abstractmethod
    async def analyze(self, content: str) -> GuardrailResult:
        """Analyze content and return result."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if guardrail is available."""
        pass
    
    @abstractmethod
    def get_config(self) -> Dict[str, Any]:
        """Get guardrail configuration."""
        pass
```

### Step 2: Create Your Filter

Here's a simple example - a profanity filter:

```python
# src/stinger/filters/custom_profanity_filter.py

import re
from typing import Dict, Any, List
from .base_filter import BaseFilter
from ..core.guardrail_interface import GuardrailInterface, GuardrailResult, GuardrailType

class CustomProfanityFilter(BaseFilter, GuardrailInterface):
    """
    Custom profanity filter that blocks content containing profane words.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Load profanity list from config
        self.profanity_words = config.get('profanity_words', [])
        self.case_sensitive = config.get('case_sensitive', False)
        self.block_threshold = config.get('block_threshold', 1)
        
        # Compile regex patterns for efficiency
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for profanity detection."""
        if self.case_sensitive:
            patterns = [re.escape(word) for word in self.profanity_words]
        else:
            patterns = [re.escape(word) for word in self.profanity_words]
        
        self.profanity_pattern = re.compile('|'.join(patterns), 
                                          flags=0 if self.case_sensitive else re.IGNORECASE)
    
    async def analyze(self, content: str) -> GuardrailResult:
        """
        Analyze content for profanity.
        
        Args:
            content: Content to analyze
            
        Returns:
            GuardrailResult with analysis
        """
        if not content or not self.enabled:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="Filter disabled or empty content",
                details={'profanity_count': 0}
            )
        
        # Find profanity matches
        matches = self.profanity_pattern.findall(content)
        profanity_count = len(matches)
        
        # Determine if content should be blocked
        blocked = profanity_count >= self.block_threshold
        confidence = min(1.0, profanity_count / max(self.block_threshold, 1))
        
        # Create reason message
        if blocked:
            reason = f"Content contains {profanity_count} profane words (threshold: {self.block_threshold})"
        else:
            reason = f"Content contains {profanity_count} profane words (below threshold)"
        
        return GuardrailResult(
            blocked=blocked,
            confidence=confidence,
            reason=reason,
            details={
                'profanity_count': profanity_count,
                'profanity_words': list(set(matches)),
                'threshold': self.block_threshold
            }
        )
    
    def is_available(self) -> bool:
        """Check if filter is available."""
        return len(self.profanity_words) > 0
    
    def get_config(self) -> Dict[str, Any]:
        """Get filter configuration."""
        return {
            'name': self.name,
            'type': 'custom_profanity_filter',
            'enabled': self.enabled,
            'profanity_words_count': len(self.profanity_words),
            'case_sensitive': self.case_sensitive,
            'block_threshold': self.block_threshold
        }
    
    def update_config(self, config: Dict[str, Any]) -> bool:
        """Update filter configuration."""
        try:
            if 'profanity_words' in config:
                self.profanity_words = config['profanity_words']
                self._compile_patterns()
            
            if 'case_sensitive' in config:
                self.case_sensitive = config['case_sensitive']
                self._compile_patterns()
            
            if 'block_threshold' in config:
                self.block_threshold = config['block_threshold']
            
            return True
        except Exception as e:
            logger.error(f"Failed to update profanity filter config: {e}")
            return False
```

### Step 3: Create Configuration

Create a YAML configuration file:

```yaml
# src/stinger/filters/configs/custom_profanity.yaml
name: "custom_profanity_filter"
enabled: true
profanity_words:
  - "bad_word_1"
  - "bad_word_2"
  - "bad_word_3"
case_sensitive: false
block_threshold: 1
```

### Step 4: Register Your Filter

Add your filter to the factory:

```python
# src/stinger/core/guardrail_factory.py

# Add this to the _create_filter method
elif filter_type == "custom_profanity":
    from ..filters.custom_profanity_filter import CustomProfanityFilter
    return CustomProfanityFilter(config)
```

### Step 5: Use Your Filter

```python
# Use in a pipeline
from stinger import GuardrailPipeline

# Create pipeline with your custom filter
pipeline = GuardrailPipeline("path/to/config.yaml")

# Test your filter
result = await pipeline.check_input("This contains bad_word_1")
print(f"Blocked: {result['blocked']}")
```

## 🧪 Testing Your Custom Filter

### Unit Tests

```python
# tests/test_custom_profanity_filter.py

import pytest
from src.stinger.filters.custom_profanity_filter import CustomProfanityFilter

class TestCustomProfanityFilter:
    
    def test_profanity_detection(self):
        """Test basic profanity detection."""
        config = {
            'name': 'test_profanity',
            'profanity_words': ['bad', 'evil'],
            'block_threshold': 1
        }
        
        filter_instance = CustomProfanityFilter(config)
        
        # Test with profanity
        result = await filter_instance.analyze("This is bad content")
        assert result.blocked == True
        assert result.confidence > 0.5
        
        # Test without profanity
        result = await filter_instance.analyze("This is good content")
        assert result.blocked == False
        assert result.confidence == 0.0
    
    def test_threshold_behavior(self):
        """Test block threshold behavior."""
        config = {
            'name': 'test_profanity',
            'profanity_words': ['bad'],
            'block_threshold': 2
        }
        
        filter_instance = CustomProfanityFilter(config)
        
        # One profanity word (below threshold)
        result = await filter_instance.analyze("This is bad")
        assert result.blocked == False
        
        # Two profanity words (at threshold)
        result = await filter_instance.analyze("This is bad and bad")
        assert result.blocked == True
```

### Integration Tests

```python
# tests/test_integration_filters.py

def test_custom_profanity_in_pipeline():
    """Test custom profanity filter in pipeline."""
    config = {
        'input_guardrails': [
            {
                'type': 'custom_profanity',
                'name': 'test_profanity',
                'enabled': True,
                'profanity_words': ['bad'],
                'block_threshold': 1
            }
        ]
    }
    
    pipeline = GuardrailPipeline(config)
    result = pipeline.check_input("This is bad content")
    
    assert result['blocked'] == True
    assert 'test_profanity' in result['reasons'][0]
```

## 🔄 Advanced Filter Patterns

### 1. AI-Powered Filters

```python
class AIContentFilter(BaseFilter, GuardrailInterface):
    """Filter using AI to analyze content."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key')
        self.model = config.get('model', 'gpt-4o-mini')
        self.threshold = config.get('threshold', 0.7)
        
        # Initialize AI client
        self.client = OpenAIAdapter(self.api_key)
    
    async def analyze(self, content: str) -> GuardrailResult:
        """Use AI to analyze content."""
        try:
            # Create analysis prompt
            prompt = f"""
            Analyze this content for inappropriate material:
            "{content}"
            
            Return a JSON response with:
            - blocked: boolean
            - confidence: float (0-1)
            - reason: string
            """
            
            # Call AI
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200
            )
            
            # Parse response
            result_data = json.loads(response.choices[0].message.content)
            
            return GuardrailResult(
                blocked=result_data['blocked'],
                confidence=result_data['confidence'],
                reason=result_data['reason'],
                details={'ai_model': self.model}
            )
            
        except Exception as e:
            logger.error(f"AI filter error: {e}")
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason=f"AI filter error: {e}",
                details={'error': str(e)}
            )
```

### 2. Regex-Based Filters

```python
class RegexFilter(BaseFilter, GuardrailInterface):
    """Filter using regex patterns."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.patterns = config.get('patterns', [])
        self.case_sensitive = config.get('case_sensitive', False)
        
        # Compile patterns
        flags = 0 if self.case_sensitive else re.IGNORECASE
        self.compiled_patterns = [re.compile(pattern, flags) for pattern in self.patterns]
    
    async def analyze(self, content: str) -> GuardrailResult:
        """Check content against regex patterns."""
        matches = []
        
        for pattern in self.compiled_patterns:
            pattern_matches = pattern.findall(content)
            if pattern_matches:
                matches.extend(pattern_matches)
        
        blocked = len(matches) > 0
        confidence = min(1.0, len(matches) / 10.0)  # Normalize to 0-1
        
        return GuardrailResult(
            blocked=blocked,
            confidence=confidence,
            reason=f"Found {len(matches)} regex matches" if blocked else "No regex matches",
            details={'matches': matches, 'patterns_checked': len(self.patterns)}
        )
```

### 3. Rate-Limited Filters

```python
class RateLimitedFilter(BaseFilter, GuardrailInterface):
    """Filter with built-in rate limiting."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.rate_limiter = get_global_rate_limiter()
        self.rate_limit_key = config.get('rate_limit_key', 'default')
        self.max_requests_per_minute = config.get('max_requests_per_minute', 60)
    
    async def analyze(self, content: str) -> GuardrailResult:
        """Analyze with rate limiting."""
        # Check rate limit
        rate_result = self.rate_limiter.check_rate_limit(
            self.rate_limit_key,
            {'requests_per_minute': self.max_requests_per_minute}
        )
        
        if rate_result['exceeded']:
            return GuardrailResult(
                blocked=True,
                confidence=1.0,
                reason=f"Rate limit exceeded: {rate_result['reason']}",
                details={'rate_limit': rate_result}
            )
        
        # Record request
        self.rate_limiter.record_request(self.rate_limit_key)
        
        # Perform actual analysis
        # ... your filter logic here ...
        
        return GuardrailResult(
            blocked=False,
            confidence=0.5,
            reason="Content analyzed successfully",
            details={'rate_limit_remaining': rate_result['remaining']}
        )
```

## 📊 Health Monitoring for Custom Filters

### Adding Health Status

```python
class CustomFilter(BaseFilter, GuardrailInterface):
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get filter health status."""
        return {
            'name': self.name,
            'type': 'custom_filter',
            'enabled': self.enabled,
            'available': self.is_available(),
            'last_check': time.time(),
            'custom_metrics': {
                'total_checks': self.total_checks,
                'blocked_count': self.blocked_count,
                'avg_response_time_ms': self.avg_response_time
            }
        }
    
    def record_metrics(self, response_time_ms: float, blocked: bool):
        """Record performance metrics."""
        self.total_checks += 1
        if blocked:
            self.blocked_count += 1
        
        # Update average response time
        self.avg_response_time = (
            (self.avg_response_time * (self.total_checks - 1) + response_time_ms) 
            / self.total_checks
        )
```

### Health Check Integration

```python
# In your filter's analyze method
async def analyze(self, content: str) -> GuardrailResult:
    start_time = time.time()
    
    try:
        # Your filter logic here
        result = await self._perform_analysis(content)
        
        # Record metrics
        response_time = (time.time() - start_time) * 1000
        self.record_metrics(response_time, result.blocked)
        
        return result
        
    except Exception as e:
        # Record error
        self.record_metrics((time.time() - start_time) * 1000, False)
        raise
```

## 🔧 Configuration Management

### Dynamic Configuration

```python
class ConfigurableFilter(BaseFilter, GuardrailInterface):
    
    def update_config(self, config: Dict[str, Any]) -> bool:
        """Update filter configuration dynamically."""
        try:
            # Validate new config
            if not self._validate_config(config):
                return False
            
            # Update configuration
            self._apply_config(config)
            
            # Log the change
            logger.info(f"Updated config for filter {self.name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update config for {self.name}: {e}")
            return False
    
    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate configuration before applying."""
        required_fields = ['enabled', 'threshold']
        return all(field in config for field in required_fields)
    
    def _apply_config(self, config: Dict[str, Any]):
        """Apply new configuration."""
        self.enabled = config.get('enabled', self.enabled)
        self.threshold = config.get('threshold', self.threshold)
        # ... other config updates
```

### Configuration Validation

```python
import yaml
from typing import Dict, Any

def validate_filter_config(config_path: str) -> bool:
    """Validate filter configuration file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Check required fields
        required_fields = ['name', 'type', 'enabled']
        for field in required_fields:
            if field not in config:
                print(f"❌ Missing required field: {field}")
                return False
        
        # Check filter type
        valid_types = ['custom_profanity', 'regex', 'ai_content']
        if config['type'] not in valid_types:
            print(f"❌ Invalid filter type: {config['type']}")
            return False
        
        print("✅ Configuration is valid")
        return True
        
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False
```

## 🚀 Best Practices

### 1. Performance Optimization

```python
class OptimizedFilter(BaseFilter, GuardrailInterface):
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Pre-compile patterns for efficiency
        self._compile_patterns()
        
        # Use caching for expensive operations
        self._cache = {}
        self._cache_size = config.get('cache_size', 1000)
    
    def _compile_patterns(self):
        """Pre-compile regex patterns."""
        patterns = self.config.get('patterns', [])
        self.compiled_patterns = [re.compile(p) for p in patterns]
    
    async def analyze(self, content: str) -> GuardrailResult:
        """Analyze with caching and optimization."""
        # Check cache first
        cache_key = hash(content)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Perform analysis
        result = await self._perform_analysis(content)
        
        # Cache result
        if len(self._cache) < self._cache_size:
            self._cache[cache_key] = result
        
        return result
```

### 2. Error Handling

```python
class RobustFilter(BaseFilter, GuardrailInterface):
    
    async def analyze(self, content: str) -> GuardrailResult:
        """Robust analysis with error handling."""
        try:
            # Validate input
            if not content or not isinstance(content, str):
                return GuardrailResult(
                    blocked=False,
                    confidence=0.0,
                    reason="Invalid input content",
                    details={'error': 'Invalid input type'}
                )
            
            # Perform analysis
            result = await self._perform_analysis(content)
            
            # Validate result
            if not isinstance(result, GuardrailResult):
                raise ValueError("Analysis must return GuardrailResult")
            
            return result
            
        except Exception as e:
            logger.error(f"Filter {self.name} error: {e}")
            
            # Return safe default
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason=f"Filter error: {str(e)}",
                details={'error': str(e), 'filter_name': self.name}
            )
```

### 3. Logging and Monitoring

```python
import logging
from datetime import datetime

class MonitoredFilter(BaseFilter, GuardrailInterface):
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = logging.getLogger(f"filter.{self.name}")
        self.metrics = {
            'total_requests': 0,
            'blocked_requests': 0,
            'errors': 0,
            'avg_response_time': 0.0
        }
    
    async def analyze(self, content: str) -> GuardrailResult:
        start_time = datetime.now()
        
        try:
            self.metrics['total_requests'] += 1
            
            result = await self._perform_analysis(content)
            
            if result.blocked:
                self.metrics['blocked_requests'] += 1
                self.logger.info(f"Blocked content: {result.reason}")
            
            # Update metrics
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self._update_response_time(response_time)
            
            return result
            
        except Exception as e:
            self.metrics['errors'] += 1
            self.logger.error(f"Analysis error: {e}")
            raise
    
    def _update_response_time(self, response_time_ms: float):
        """Update average response time."""
        total = self.metrics['total_requests']
        current_avg = self.metrics['avg_response_time']
        self.metrics['avg_response_time'] = (
            (current_avg * (total - 1) + response_time_ms) / total
        )
```

## 📚 Example Implementations

### Complete Example: Sentiment Filter

```python
# src/stinger/filters/sentiment_filter.py

import re
from typing import Dict, Any, List
from .base_filter import BaseFilter
from ..core.guardrail_interface import GuardrailInterface, GuardrailResult, GuardrailType

class SentimentFilter(BaseFilter, GuardrailInterface):
    """
    Filter content based on sentiment analysis.
    Blocks overly negative or hostile content.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Sentiment thresholds
        self.negative_threshold = config.get('negative_threshold', -0.5)
        self.hostile_threshold = config.get('hostile_threshold', -0.8)
        
        # Negative word patterns
        self.negative_words = config.get('negative_words', [])
        self.hostile_words = config.get('hostile_words', [])
        
        # Compile patterns
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for sentiment detection."""
        self.negative_pattern = re.compile(
            '|'.join(re.escape(word) for word in self.negative_words),
            re.IGNORECASE
        )
        self.hostile_pattern = re.compile(
            '|'.join(re.escape(word) for word in self.hostile_words),
            re.IGNORECASE
        )
    
    async def analyze(self, content: str) -> GuardrailResult:
        """Analyze content sentiment."""
        if not content or not self.enabled:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="Filter disabled or empty content",
                details={'sentiment_score': 0.0}
            )
        
        # Calculate sentiment score
        sentiment_score = self._calculate_sentiment(content)
        
        # Determine if content should be blocked
        blocked = sentiment_score <= self.hostile_threshold
        confidence = abs(sentiment_score)
        
        # Create reason
        if sentiment_score <= self.hostile_threshold:
            reason = f"Hostile content detected (score: {sentiment_score:.2f})"
        elif sentiment_score <= self.negative_threshold:
            reason = f"Negative content detected (score: {sentiment_score:.2f})"
        else:
            reason = f"Content sentiment acceptable (score: {sentiment_score:.2f})"
        
        return GuardrailResult(
            blocked=blocked,
            confidence=confidence,
            reason=reason,
            details={
                'sentiment_score': sentiment_score,
                'negative_threshold': self.negative_threshold,
                'hostile_threshold': self.hostile_threshold
            }
        )
    
    def _calculate_sentiment(self, content: str) -> float:
        """Calculate sentiment score (-1 to 1)."""
        # Count negative and hostile words
        negative_count = len(self.negative_pattern.findall(content))
        hostile_count = len(self.hostile_pattern.findall(content))
        
        # Calculate score (negative = negative sentiment)
        total_words = len(content.split())
        if total_words == 0:
            return 0.0
        
        # Weight hostile words more heavily
        sentiment_score = -(negative_count + 2 * hostile_count) / total_words
        
        # Clamp to -1 to 1
        return max(-1.0, min(1.0, sentiment_score))
    
    def is_available(self) -> bool:
        """Check if filter is available."""
        return len(self.negative_words) > 0 or len(self.hostile_words) > 0
    
    def get_config(self) -> Dict[str, Any]:
        """Get filter configuration."""
        return {
            'name': self.name,
            'type': 'sentiment_filter',
            'enabled': self.enabled,
            'negative_threshold': self.negative_threshold,
            'hostile_threshold': self.hostile_threshold,
            'negative_words_count': len(self.negative_words),
            'hostile_words_count': len(self.hostile_words)
        }
```

## 🎯 Next Steps

Now that you understand how to create custom filters:

1. **Start Simple**: Begin with basic regex or keyword filters
2. **Add Testing**: Write comprehensive tests for your filters
3. **Optimize**: Add caching and performance improvements
4. **Monitor**: Integrate with health monitoring
5. **Share**: Contribute your filters to the community

## 📖 Additional Resources

- **Base Filter Class**: `src/stinger/filters/base_filter.py`
- **Guardrail Interface**: `src/stinger/core/guardrail_interface.py`
- **Existing Filters**: `src/stinger/filters/` directory
- **Test Examples**: `tests/` directory
- **Configuration Examples**: `src/stinger/filters/configs/`

---

**🚀 Happy coding! Your custom filters will help make LLM applications safer and more reliable.** 