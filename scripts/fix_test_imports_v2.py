#!/usr/bin/env python3
"""
Fix pytest import that got placed inside docstrings.
"""

import os
import re
from pathlib import Path


def fix_pytest_in_docstring(file_path: Path) -> bool:
    """Fix pytest import that's inside the module docstring."""
    try:
        content = file_path.read_text()
        
        # Pattern to find import pytest inside docstring
        pattern = re.compile(
            r'(#!/usr/bin/env python3\n""")\n(import pytest\n\n)(.*?""")', 
            re.DOTALL
        )
        
        if pattern.search(content):
            # Move import before docstring
            fixed = pattern.sub(r'\1\n\3"""', content)
            # Add import at the correct location
            lines = fixed.split('\n')
            
            # Find where to insert import (after shebang, before docstring)
            new_lines = []
            inserted = False
            
            for i, line in enumerate(lines):
                new_lines.append(line)
                if i == 0 and line.startswith('#!/usr/bin/env python3'):
                    new_lines.append('import pytest')
                    new_lines.append('')
                    inserted = True
            
            if inserted:
                file_path.write_text('\n'.join(new_lines))
                return True
                
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        
    return False


def main():
    """Fix pytest imports in all test files."""
    test_dir = Path("tests")
    
    if not test_dir.exists():
        print("Error: tests directory not found!")
        return
    
    fixed_count = 0
    
    # List of files we know have this issue
    problem_files = [
        "tests/behavioral/test_action_control_behavior.py",
        "tests/behavioral/test_bypass_attempts.py", 
        "tests/behavioral/test_pii_behavior.py",
        "tests/behavioral/test_simple_guardrails_behavior.py",
        "tests/behavioral/test_toxicity_behavior.py",
        "tests/behavioral/test_edge_cases_behavior.py",
        "tests/behavioral/test_error_handling_behavior.py",
        "tests/behavioral/test_injection_behavior.py",
        "tests/behavioral/test_performance_behavior.py",
        "tests/behavioral/test_url_behavior.py"
    ]
    
    for file_path in problem_files:
        path = Path(file_path)
        if path.exists():
            if fix_pytest_in_docstring(path):
                print(f"Fixed: {path}")
                fixed_count += 1
    
    print(f"\nFixed {fixed_count} files")


if __name__ == "__main__":
    main()