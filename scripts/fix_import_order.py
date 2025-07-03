#!/usr/bin/env python3
"""Fix import order - move imports after shebang and docstring"""

import os

def fix_import_order(file_path):
    """Fix import placement"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if asyncio import is before shebang
    if content.startswith('import asyncio\n\n#!/usr/bin/env python3'):
        # Fix it by moving import after docstring
        lines = content.split('\n')
        
        # Find where docstring ends
        in_docstring = False
        docstring_end = 0
        for i, line in enumerate(lines):
            if line.strip() == '"""' and i > 0:
                if in_docstring:
                    docstring_end = i + 1
                    break
                else:
                    in_docstring = True
        
        # Reconstruct with correct order
        new_lines = []
        # Skip the first import asyncio line
        i = 0
        if lines[0] == 'import asyncio':
            i = 2  # Skip import and empty line
        
        # Add lines up to docstring end
        while i < docstring_end:
            new_lines.append(lines[i])
            i += 1
        
        # Add empty line and import
        new_lines.append('')
        new_lines.append('import asyncio')
        
        # Add rest of file
        for j in range(i, len(lines)):
            new_lines.append(lines[j])
        
        with open(file_path, 'w') as f:
            f.write('\n'.join(new_lines))
        print(f"Fixed import order in {file_path}")

# Fix all behavioral test files
test_dir = 'tests/behavioral'
for filename in os.listdir(test_dir):
    if filename.endswith('.py'):
        file_path = os.path.join(test_dir, filename)
        fix_import_order(file_path)