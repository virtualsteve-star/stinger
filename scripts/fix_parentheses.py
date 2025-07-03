#!/usr/bin/env python3
"""Fix missing closing parentheses in test files"""

import re
import os

def fix_parentheses(file_path):
    """Fix missing closing parentheses"""
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    fixed = False
    for i, line in enumerate(lines):
        # Check for lines ending with asyncio.run(...analyze(...) without closing )
        if 'asyncio.run(' in line and '.analyze(' in line and not line.rstrip().endswith('))'):
            # Count parentheses
            open_count = line.count('(')
            close_count = line.count(')')
            
            if open_count > close_count:
                # Add missing parentheses
                missing = open_count - close_count
                lines[i] = line.rstrip() + ')' * missing + '\n'
                fixed = True
                print(f"Fixed line {i+1} in {file_path}")
    
    if fixed:
        with open(file_path, 'w') as f:
            f.writelines(lines)
        print(f"Fixed {file_path}")

# Fix all behavioral test files
test_dir = 'tests/behavioral'
for filename in os.listdir(test_dir):
    if filename.endswith('.py'):
        file_path = os.path.join(test_dir, filename)
        fix_parentheses(file_path)