#!/usr/bin/env python3
"""
Script to fix import paths in test files after 7B.1 duplicate source tree elimination.
"""

import os
import re
import glob

def fix_imports_in_file(filepath):
    """Fix import paths in a single file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Track if we made changes
    original_content = content
    
    # Fix import patterns
    replacements = [
        # Core imports
        (r'from src\.core\.', 'from src.stinger.core.'),
        (r'import src\.core\.', 'import src.stinger.core.'),
        
        # Filter imports
        (r'from src\.filters\.', 'from src.stinger.guardrails.'),
        (r'import src\.filters\.', 'import src.stinger.filters.'),
        
        # Adapter imports
        (r'from src\.adapters\.', 'from src.stinger.adapters.'),
        (r'import src\.adapters\.', 'import src.stinger.adapters.'),
        
        # Utils imports
        (r'from src\.utils\.', 'from src.stinger.utils.'),
        (r'import src\.utils\.', 'import src.stinger.utils.'),
        
        # Data imports
        (r'from src\.data\.', 'from src.stinger.data.'),
        (r'import src\.data\.', 'import src.stinger.data.'),
        
        # Scenarios imports
        (r'from src\.scenarios\.', 'from src.stinger.scenarios.'),
        (r'import src\.scenarios\.', 'import src.stinger.scenarios.'),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # Only write if changes were made
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    
    return False

def main():
    """Fix imports in all test files."""
    test_files = glob.glob('tests/*.py')
    
    fixed_count = 0
    for test_file in test_files:
        if fix_imports_in_file(test_file):
            print(f"Fixed imports in: {test_file}")
            fixed_count += 1
    
    print(f"\nFixed imports in {fixed_count} test files.")

if __name__ == '__main__':
    main() 