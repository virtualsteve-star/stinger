#!/usr/bin/env python3
"""
Fix pytest import placement in test files.
The import should be at the top, not after the docstring.
"""

import os
import re
from pathlib import Path


def fix_pytest_import(file_path: Path) -> bool:
    """Fix pytest import placement in a single file."""
    try:
        content = file_path.read_text()
        
        # Check if file has the wrong pattern (import after docstring)
        wrong_pattern = re.compile(r'(#!/usr/bin/env python3\n)("""[\s\S]*?"""\n)(import pytest\n)', re.MULTILINE)
        
        if wrong_pattern.search(content):
            # Fix by moving import before docstring
            fixed_content = wrong_pattern.sub(r'\1import pytest\n\n\2', content)
            
            # Remove duplicate import if it exists
            lines = fixed_content.split('\n')
            seen_import = False
            cleaned_lines = []
            
            for line in lines:
                if line.strip() == 'import pytest':
                    if not seen_import:
                        cleaned_lines.append(line)
                        seen_import = True
                else:
                    cleaned_lines.append(line)
            
            fixed_content = '\n'.join(cleaned_lines)
            
            file_path.write_text(fixed_content)
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
    error_count = 0
    
    # Find all Python test files
    for test_file in test_dir.rglob("*.py"):
        if test_file.name.startswith("test_") or test_file.name.endswith("_test.py"):
            if fix_pytest_import(test_file):
                print(f"Fixed: {test_file}")
                fixed_count += 1
    
    print(f"\nFixed {fixed_count} files")
    
    if error_count > 0:
        print(f"Errors: {error_count}")


if __name__ == "__main__":
    main()