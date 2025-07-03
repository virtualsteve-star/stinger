#!/usr/bin/env python3
"""
Fix missing asyncio.run() calls in behavioral tests
"""

import re
import os

def fix_async_calls(file_path):
    """Fix missing asyncio.run() calls"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if asyncio is imported
    if 'import asyncio' not in content:
        # Add asyncio import after other imports
        import_section = []
        other_lines = []
        in_imports = True
        
        for line in content.split('\n'):
            if in_imports:
                if line.startswith('import ') or line.startswith('from '):
                    import_section.append(line)
                elif line.strip() == '' and import_section:
                    # Still in import section
                    import_section.append(line)
                else:
                    # End of imports
                    in_imports = False
                    import_section.append('import asyncio')
                    import_section.append('')
                    other_lines.append(line)
            else:
                other_lines.append(line)
        
        if in_imports:
            # File is all imports
            import_section.append('import asyncio')
        
        content = '\n'.join(import_section + other_lines)
    
    # Fix analyze calls without asyncio.run
    # Match patterns like: result = guardrail.analyze(...)
    # But not: result = asyncio.run(guardrail.analyze(...))
    pattern = r'(\s*)([\w_]+)\s*=\s*([\w_\.]+)\.analyze\('
    
    def replace_analyze(match):
        indent = match.group(1)
        var_name = match.group(2)
        obj_name = match.group(3)
        return f"{indent}{var_name} = asyncio.run({obj_name}.analyze("
    
    # Find all matches and check they're not already wrapped
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if '.analyze(' in line and 'asyncio.run' not in line and '=' in line:
            lines[i] = re.sub(pattern, replace_analyze, line)
        elif '.analyze(' in line and 'asyncio.run' not in line and '=' not in line:
            # Handle cases like: strict.analyze(text)
            pattern2 = r'(\s*)([\w_\.]+)\.analyze\('
            def replace_analyze2(match):
                indent = match.group(1)
                obj_name = match.group(2)
                return f"{indent}asyncio.run({obj_name}.analyze("
            lines[i] = re.sub(pattern2, replace_analyze2, line)
    
    content = '\n'.join(lines)
    
    # Fix list comprehensions
    # [guardrail.analyze(text) for text in test_texts]
    content = re.sub(
        r'\[([\w_\.]+)\.analyze\(([^)]+)\)\s+for',
        r'[asyncio.run(\1.analyze(\2)) for',
        content
    )
    
    # Write back
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed {file_path}")

# Fix all behavioral test files
test_dir = 'tests/behavioral'
for filename in os.listdir(test_dir):
    if filename.endswith('.py') and filename != 'test_pii_behavior.py':  # Skip already fixed file
        file_path = os.path.join(test_dir, filename)
        fix_async_calls(file_path)