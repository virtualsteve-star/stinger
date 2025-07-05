#!/usr/bin/env python3
"""
Fix remaining pytest import issues in test files.
"""

import re
from pathlib import Path


def fix_pytest_import(file_path: Path) -> bool:
    """Fix pytest import placement in file."""
    try:
        content = file_path.read_text()
        
        # Check if file has import pytest inside docstring
        if '"""\nimport pytest\n' in content:
            # Move import before docstring
            lines = content.split('\n')
            new_lines = []
            in_docstring = False
            found_import = False
            
            for i, line in enumerate(lines):
                if i == 0:  # shebang
                    new_lines.append(line)
                    if lines[i+1].strip() == '"""' and i+2 < len(lines) and lines[i+2].strip() == 'import pytest':
                        new_lines.append('import pytest')
                        new_lines.append('')
                        found_import = True
                elif line.strip() == 'import pytest' and found_import and i == 2:
                    # Skip the import that was inside docstring
                    continue
                else:
                    new_lines.append(line)
            
            if found_import:
                file_path.write_text('\n'.join(new_lines))
                return True
                
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        
    return False


def main():
    """Fix remaining files with pytest import issues."""
    
    files_to_fix = [
        "tests/integration/test_pipeline_integration.py",
        "tests/test_audit_comprehensive.py", 
        "tests/test_performance_validation.py",
        "tests/validation/test_demo_cli_validation.py",
        "tests/behavioral/test_edge_cases_behavior.py",
        "tests/behavioral/test_error_handling_behavior.py",
        "tests/behavioral/test_injection_behavior.py",
        "tests/behavioral/test_performance_behavior.py"
    ]
    
    fixed_count = 0
    
    for file_path in files_to_fix:
        path = Path(file_path)
        if path.exists():
            if fix_pytest_import(path):
                print(f"Fixed: {path}")
                fixed_count += 1
    
    print(f"\nFixed {fixed_count} files")


if __name__ == "__main__":
    main()