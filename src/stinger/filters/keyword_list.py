import os
from pathlib import Path
from typing import List, Optional
from ..core.base_filter import BaseFilter, FilterResult
from ..utils.exceptions import FilterError

class KeywordListFilter(BaseFilter):
    """
    Filter that blocks content containing any of a list of keywords.
    Supports both inline keywords and loading from external files.
    """
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.keywords = []
        self.case_sensitive = config.get('case_sensitive', False)
        self._load_keywords()
    
    def _load_keywords(self):
        """Load keywords from config or file."""
        # Get inline keywords
        inline_keywords = self.config.get('keywords', [])
        if isinstance(inline_keywords, str):
            inline_keywords = [inline_keywords]
        
        # Get file path for keywords
        keywords_file = self.config.get('keywords_file')
        
        if keywords_file:
            try:
                file_keywords = self._load_keywords_from_file(keywords_file)
                # Combine file keywords with inline keywords (file takes precedence)
                self.keywords = file_keywords + [kw for kw in inline_keywords if kw not in file_keywords]
            except Exception as e:
                # If file loading fails, use only inline keywords
                from ..core.error_handling import safe_error_message, sanitize_path
                safe_path = sanitize_path(keywords_file)
                safe_msg = safe_error_message(e, f"loading keywords from file {safe_path}")
                self.keywords = inline_keywords
                print(f"⚠️ Warning: {safe_msg}")
                print(f"   Using fallback keywords: {inline_keywords}")
        else:
            self.keywords = inline_keywords
        
        # Validate keywords
        if not self.keywords:
            raise FilterError("No keywords provided for KeywordListFilter")
        
        # Convert to lowercase for case-insensitive matching
        if not self.case_sensitive:
            self.keywords = [kw.lower() for kw in self.keywords]
    
    def _load_keywords_from_file(self, file_path: str) -> List[str]:
        """Load keywords from a text file."""
        # Resolve relative path from config file location
        config_dir = self.config.get('_config_dir', '.')
        resolved_path = Path(config_dir) / file_path
        
        if not resolved_path.exists():
            raise FileNotFoundError(f"Keywords file not found: {resolved_path}")
        
        keywords = []
        try:
            with open(resolved_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith('#'):
                        keywords.append(line)
        except Exception as e:
            from ..core.error_handling import safe_error_message, sanitize_path
            safe_path = sanitize_path(str(resolved_path))
            # Check if this is a file access error (before any lines processed)
            if 'line_num' not in locals():
                safe_msg = safe_error_message(e, f"opening keywords file {safe_path}")
            else:
                safe_msg = safe_error_message(e, f"reading keywords file {safe_path} at line {line_num}")
            raise FilterError(f"Failed to read keywords file: {safe_msg}")
        
        return keywords
    
    async def run(self, content: str) -> FilterResult:
        """Run the keyword list filter on the given content."""
        if not content:
            return FilterResult(action='allow', reason='no content to check')
        
        if not self.keywords:
            return FilterResult(action='allow', reason='no keywords configured')
        
        # Prepare content for matching
        content_to_check = content if self.case_sensitive else content.lower()
        
        # Check for matches
        matched_keywords = []
        for keyword in self.keywords:
            if keyword in content_to_check:
                matched_keywords.append(keyword)
        
        if matched_keywords:
            # Return the first matched keyword for the reason
            matched_keyword = matched_keywords[0]
            return FilterResult(
                action='block',
                reason=f'blocked keywords: {", ".join(matched_keywords)}',
                confidence=1.0
            )
        
        return FilterResult(action='allow', reason='no keyword matches')
    
    def validate_config(self) -> bool:
        """Validate filter configuration."""
        # Check that we have either keywords or keywords_file
        has_inline = bool(self.config.get('keywords'))
        has_file = bool(self.config.get('keywords_file'))
        
        if not has_inline and not has_file:
            raise FilterError("KeywordListFilter requires either 'keywords' or 'keywords_file' configuration")
        
        return True 