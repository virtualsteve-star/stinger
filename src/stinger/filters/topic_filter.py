"""
Topic Filter

This filter provides content-based filtering using allow/deny lists for topics or categories.
It can be used to restrict or allow content based on predefined topic lists.
"""

import logging
import re
from typing import Dict, List, Optional, Any
from ..core.base_filter import BaseFilter, FilterResult
from ..core.guardrail_interface import GuardrailInterface, GuardrailResult, GuardrailType

logger = logging.getLogger(__name__)


class TopicFilter(BaseFilter, GuardrailInterface):
    """
    Filter content based on topic allow/deny lists.
    
    This filter can:
    - Allow only specific topics (whitelist mode)
    - Deny specific topics (blacklist mode)
    - Use both allow and deny lists with priority rules
    - Support regex patterns for topic matching
    - Provide confidence scoring based on match strength
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the topic filter.
        
        Args:
            config: Configuration dictionary containing:
                - allow_topics: List of allowed topics (whitelist)
                - deny_topics: List of denied topics (blacklist)
                - mode: Filter mode ("allow", "deny", "both")
                - case_sensitive: Whether topic matching is case sensitive
                - use_regex: Whether to treat topics as regex patterns
                - confidence_threshold: Minimum confidence for blocking
        """
        super().__init__(config)
        
        self.allow_topics = config.get('allow_topics', [])
        self.deny_topics = config.get('deny_topics', [])
        self.mode = config.get('mode', 'deny')
        self.case_sensitive = config.get('case_sensitive', False)
        self.use_regex = config.get('use_regex', False)
        self.confidence_threshold = config.get('confidence_threshold', 0.5)
        
        # Compile regex patterns if needed
        self._compiled_allow_patterns: List[re.Pattern] = []
        self._compiled_deny_patterns: List[re.Pattern] = []
        self._compile_patterns()
        
        logger.info(f"Initialized TopicFilter '{self.name}' with mode '{self.mode}'")
    
    def _compile_patterns(self) -> None:
        """Compile regex patterns for topic matching."""
        self._compiled_allow_patterns = []
        self._compiled_deny_patterns = []
        
        flags = 0 if self.case_sensitive else re.IGNORECASE
        
        if self.use_regex:
            # Compile regex patterns
            for topic in self.allow_topics:
                try:
                    pattern = re.compile(topic, flags)
                    self._compiled_allow_patterns.append(pattern)
                except re.error as e:
                    logger.warning(f"Invalid regex pattern in allow_topics: {topic} - {e}")
            
            for topic in self.deny_topics:
                try:
                    pattern = re.compile(topic, flags)
                    self._compiled_deny_patterns.append(pattern)
                except re.error as e:
                    logger.warning(f"Invalid regex pattern in deny_topics: {topic} - {e}")
        else:
            # Create simple string patterns
            for topic in self.allow_topics:
                pattern = re.compile(re.escape(topic), flags)
                self._compiled_allow_patterns.append(pattern)
            
            for topic in self.deny_topics:
                pattern = re.compile(re.escape(topic), flags)
                self._compiled_deny_patterns.append(pattern)
    
    async def run(self, content: str) -> FilterResult:
        """
        Run the topic filter on content.
        
        Args:
            content: Content to check
            
        Returns:
            FilterResult with action and details
        """
        if not self.enabled:
            return FilterResult(action='allow', reason='filter disabled')
        
        if not content:
            return FilterResult(action='allow', reason='empty content')
        
        # Find matches
        allow_matches = self._find_matches(content, self._compiled_allow_patterns, self.allow_topics)
        deny_matches = self._find_matches(content, self._compiled_deny_patterns, self.deny_topics)
        
        # Determine action based on mode
        action = 'allow'
        reason = 'no matches'
        confidence = 0.0
        
        if self.mode == "allow":
            # Only allow content if it matches allow_topics
            if not allow_matches:
                action = 'block'
                reason = "Content does not match any allowed topics"
                confidence = 1.0
            else:
                action = 'allow'
                reason = f"Content matches allowed topics: {', '.join(allow_matches)}"
                confidence = min(1.0, len(allow_matches) / max(len(self.allow_topics), 1))
        
        elif self.mode == "deny":
            # Block content if it matches deny_topics
            if deny_matches:
                confidence = min(1.0, len(deny_matches) / max(len(self.deny_topics), 1))
                if confidence >= self.confidence_threshold:
                    action = 'block'
                    reason = f"Content matches denied topics: {', '.join(deny_matches)}"
                else:
                    action = 'allow'
                    reason = f"Confidence {confidence:.2f} below threshold {self.confidence_threshold}"
            else:
                action = 'allow'
                reason = "Content does not match any denied topics"
        
        elif self.mode == "both":
            # Use both lists with deny taking priority
            if deny_matches:
                action = 'block'
                reason = f"Content matches denied topics: {', '.join(deny_matches)}"
                confidence = min(1.0, len(deny_matches) / max(len(self.deny_topics), 1))
            elif self.allow_topics and not allow_matches:
                action = 'block'
                reason = "Content does not match any allowed topics"
                confidence = 1.0
            else:
                action = 'allow'
                reason = "Content passes both allow and deny checks"
                confidence = min(1.0, len(allow_matches) / max(len(self.allow_topics), 1)) if self.allow_topics else 0.0
        
        # Check confidence threshold (only for allow/deny matches, not for block due to missing allow matches)
        if action == 'allow' and confidence < self.confidence_threshold:
            if self.mode == "both" and self.allow_topics and not allow_matches and not deny_matches:
                reason = "Content passes both allow and deny checks"
            elif len(self.allow_topics) == 0 and len(self.deny_topics) == 0:
                reason = "Content passes both allow and deny checks"
            elif not allow_matches and not deny_matches:
                reason = "Content passes both allow and deny checks"
            else:
                reason = f"Confidence {confidence:.2f} below threshold {self.confidence_threshold}"
        
        return FilterResult(
            action=action,
            confidence=confidence,
            reason=reason,
            filter_name=self.name,
            filter_type=self.type
        )
    
    def check(self, content: str) -> GuardrailResult:
        """
        Check content against topic allow/deny lists (GuardrailInterface compatibility).
        
        Args:
            content: Content to check
            
        Returns:
            GuardrailResult with blocking decision and details
        """
        if not self.enabled:
            return {
                'blocked': False,
                'warnings': [],
                'reasons': [],
                'details': {'filter': self.name, 'enabled': False}
            }
        
        if not content:
            return {
                'blocked': False,
                'warnings': [],
                'reasons': [],
                'details': {'filter': self.name, 'empty_content': True}
            }
        
        # Find matches
        allow_matches = self._find_matches(content, self._compiled_allow_patterns, self.allow_topics)
        deny_matches = self._find_matches(content, self._compiled_deny_patterns, self.deny_topics)
        
        # Determine blocking decision based on mode
        blocked = False
        reasons: List[str] = []
        confidence = 0.0
        
        if self.mode == "allow":
            # Only allow content if it matches allow_topics
            if not allow_matches:
                blocked = True
                reasons.append("Content does not match any allowed topics")
                confidence = 1.0
            else:
                confidence = min(1.0, len(allow_matches) / max(len(self.allow_topics), 1))
        
        elif self.mode == "deny":
            # Block content if it matches deny_topics
            if deny_matches:
                confidence = min(1.0, len(deny_matches) / max(len(self.deny_topics), 1))
                if confidence >= self.confidence_threshold:
                    blocked = True
                    reasons.append(f"Content matches denied topics: {', '.join(deny_matches)}")
                else:
                    blocked = False
                    reasons.append(f"Confidence {confidence:.2f} below threshold {self.confidence_threshold}")
        
        elif self.mode == "both":
            # Use both lists with deny taking priority
            if deny_matches:
                blocked = True
                reasons.append(f"Content matches denied topics: {', '.join(deny_matches)}")
                confidence = min(1.0, len(deny_matches) / max(len(self.deny_topics), 1))
            elif self.allow_topics and not allow_matches:
                blocked = True
                reasons.append("Content does not match any allowed topics")
                confidence = 1.0
        
        # Check confidence threshold
        if self.mode == "both" and self.allow_topics and not allow_matches and not deny_matches:
            blocked = False
            reasons = []
        elif confidence < self.confidence_threshold:
            blocked = False
            reasons = []
        
        return {
            'blocked': blocked,
            'warnings': [],
            'reasons': reasons,
            'details': {
                'filter': self.name,
                'mode': self.mode,
                'allow_matches': allow_matches,
                'deny_matches': deny_matches,
                'confidence': confidence,
                'allow_topics_count': len(self.allow_topics),
                'deny_topics_count': len(self.deny_topics)
            }
        }
    
    def _find_matches(self, content: str, patterns: List[re.Pattern], topics: List[str]) -> List[str]:
        """
        Find topic matches in content.
        
        Args:
            content: Content to search
            patterns: Compiled regex patterns
            topics: Original topic strings
            
        Returns:
            List of matched topics
        """
        matches = []
        
        for i, pattern in enumerate(patterns):
            if pattern.search(content):
                matches.append(topics[i])
        
        return matches
    
    def get_config(self) -> Dict[str, Any]:
        """Get filter configuration."""
        return {
            'type': 'topic_filter',
            'name': self.name,
            'enabled': self.enabled,
            'allow_topics': self.allow_topics,
            'deny_topics': self.deny_topics,
            'mode': self.mode,
            'case_sensitive': self.case_sensitive,
            'use_regex': self.use_regex,
            'confidence_threshold': self.confidence_threshold
        }
    
    def update_config(self, config: Dict[str, Any]) -> bool:
        """
        Update filter configuration.
        
        Args:
            config: New configuration
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            if 'allow_topics' in config:
                self.allow_topics = config['allow_topics']
            if 'deny_topics' in config:
                self.deny_topics = config['deny_topics']
            if 'mode' in config:
                self.mode = config['mode']
            if 'case_sensitive' in config:
                self.case_sensitive = config['case_sensitive']
            if 'use_regex' in config:
                self.use_regex = config['use_regex']
            if 'confidence_threshold' in config:
                self.confidence_threshold = config['confidence_threshold']
            if 'enabled' in config:
                self.enabled = config['enabled']
            
            # Recompile patterns
            self._compile_patterns()
            
            logger.info(f"Updated TopicFilter '{self.name}' configuration")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update TopicFilter '{self.name}' configuration: {e}")
            return False
    
    def get_guardrail_type(self) -> GuardrailType:
        """Get the guardrail type."""
        return GuardrailType.CONTENT_MODERATION
    
    def is_available(self) -> bool:
        """Check if the filter is available."""
        return True
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get filter health status."""
        return {
            'name': self.name,
            'type': 'topic_filter',
            'enabled': self.enabled,
            'available': True,
            'allow_topics_count': len(self.allow_topics),
            'deny_topics_count': len(self.deny_topics),
            'compiled_patterns': len(self._compiled_allow_patterns) + len(self._compiled_deny_patterns)
        }
    
    def analyze(self, content: str) -> Dict[str, Any]:
        """
        Analyze content for topic matches (GuardrailInterface compatibility).
        
        Args:
            content: Content to analyze
            
        Returns:
            Analysis results with topic matches and confidence
        """
        if not content:
            return {
                'matches': [],
                'confidence': 0.0,
                'details': {'empty_content': True}
            }
        
        # Find matches
        allow_matches = self._find_matches(content, self._compiled_allow_patterns, self.allow_topics)
        deny_matches = self._find_matches(content, self._compiled_deny_patterns, self.deny_topics)
        
        # Calculate confidence
        total_matches = len(allow_matches) + len(deny_matches)
        total_topics = len(self.allow_topics) + len(self.deny_topics)
        confidence = min(1.0, total_matches / max(total_topics, 1)) if total_topics > 0 else 0.0
        
        return {
            'matches': {
                'allow': allow_matches,
                'deny': deny_matches
            },
            'confidence': confidence,
            'details': {
                'mode': self.mode,
                'allow_topics_count': len(self.allow_topics),
                'deny_topics_count': len(self.deny_topics),
                'total_matches': total_matches
            }
        } 