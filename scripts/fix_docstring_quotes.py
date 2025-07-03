#!/usr/bin/env python3
"""
Fix double closing quotes in docstrings.
"""

import os
from pathlib import Path


def fix_docstring_quotes(file_path: Path) -> bool:
    """Fix files that have extra quotes at end of docstring."""
    try:
        content = file_path.read_text()
        
        # Replace """" with """
        if '""""""' in content:
            fixed_content = content.replace('""""""', '"""')
            file_path.write_text(fixed_content)
            return True
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        
    return False


def main():
    """Fix docstring quotes in behavioral test files."""
    
    # Files that need fixing
    files_to_fix = [
        "tests/behavioral/test_action_control_behavior.py",
        "tests/behavioral/test_bypass_attempts.py",
        "tests/behavioral/test_pii_behavior.py",
        "tests/behavioral/test_simple_guardrails_behavior.py",
        "tests/behavioral/test_toxicity_behavior.py",
        "tests/behavioral/test_url_behavior.py",
        "tests/behavioral/test_edge_cases_behavior.py",
        "tests/behavioral/test_error_handling_behavior.py",
        "tests/behavioral/test_injection_behavior.py",
        "tests/behavioral/test_performance_behavior.py"
    ]
    
    fixed_count = 0
    
    for file_path in files_to_fix:
        path = Path(file_path)
        if path.exists():
            if fix_docstring_quotes(path):
                print(f"Fixed: {path}")
                fixed_count += 1
    
    print(f"\nFixed {fixed_count} files")


if __name__ == "__main__":
    main()