#!/usr/bin/env python3
"""
Add pytest markers to test files based on their characteristics.
Version 2: Handles both classes and individual test functions.
"""

import re
from pathlib import Path
from typing import List, Set, Tuple


def uses_ai_imports(content: str) -> bool:
    """Check if test imports AI-related guardrails."""
    ai_patterns = [
        r'ContentModerationGuardrail',
        r'PromptInjectionGuardrail',
        r'from.*openai',
        r'import.*openai',
        r'AIBased.*Guardrail',
        r'ai_based.*guardrail',
        r'test_ai_',
        r'test_.*_ai_',
        r'openai_',
        r'gpt-'
    ]
    
    for pattern in ai_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return True
    return False


def is_performance_focused(content: str, filename: str) -> bool:
    """Check if test is focused on performance testing."""
    # Check filename
    if any(x in filename.lower() for x in ['performance', 'benchmark', 'load', 'stress']):
        return True
        
    perf_patterns = [
        r'test_.*performance',
        r'test_.*benchmark',
        r'test_.*load',
        r'test_.*stress',
        r'test_.*concurrent',
        r'test_.*throughput',
        r'test_.*latency',
        r'test_.*scaling',
        r'test_.*memory',
        r'measure.*time',
        r'elapsed.*>.*\d+',  # Tests checking elapsed time
        r'assert.*time.*<'   # Performance assertions
    ]
    
    for pattern in perf_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return True
    return False


def is_slow_test(content: str) -> bool:
    """Check if test is likely to be slow based on patterns."""
    slow_patterns = [
        r'test_encoding_based_bypasses',
        r'test_injection_evasion',
        r'test_sophisticated_injections',
        r'test_ai_.*accuracy',
        r'test_prompt_injection_accuracy',
        r'test_bypass_techniques',
        r'test_.*comprehensive',
        r'for.*in range\(\d{3,}',  # Large loops
        r'asyncio\.sleep\([^0)]',  # Sleep > 0
        r'time\.sleep\([^0)]'      # Sleep > 0
    ]
    
    for pattern in slow_patterns:
        if re.search(pattern, content):
            return True
    return False


def categorize_test(content: str, filename: str) -> str:
    """Categorize a test based on its content and filename."""
    # Priority order: performance > efficacy > ci
    
    # Performance tests
    if is_performance_focused(content, filename):
        return 'performance'
    
    # AI/Efficacy tests
    if uses_ai_imports(content) or is_slow_test(content):
        return 'efficacy'
    
    # Default to CI for fast, non-AI tests
    return 'ci'


def add_markers_to_content(content: str, filename: str) -> Tuple[str, List[str]]:
    """Add markers to test classes and functions in content."""
    lines = content.split('\n')
    modified_lines = []
    changes = []
    
    # Check if pytest is imported
    has_pytest_import = any('import pytest' in line for line in lines)
    if not has_pytest_import:
        # Add pytest import after other imports
        import_added = False
        for i, line in enumerate(lines):
            modified_lines.append(line)
            if not import_added and line.strip() and not line.startswith(('import', 'from', '#', '"""')):
                if i > 0:  # Add before this line
                    modified_lines.insert(-1, 'import pytest')
                    modified_lines.insert(-1, '')
                    import_added = True
        if not import_added:
            lines.insert(0, 'import pytest\n')
    else:
        modified_lines = lines.copy()
    
    # Process the content
    i = 0
    while i < len(modified_lines):
        line = modified_lines[i]
        stripped = line.strip()
        
        # Check for test class or function
        is_test_class = stripped.startswith('class Test')
        is_test_func = (stripped.startswith('def test_') or 
                       stripped.startswith('async def test_'))
        
        if is_test_class or is_test_func:
            # Extract just this test's content for categorization
            test_content = []
            indent_level = len(line) - len(line.lstrip())
            j = i
            while j < len(modified_lines):
                test_line = modified_lines[j]
                if j > i and test_line.strip() and len(test_line) - len(test_line.lstrip()) <= indent_level:
                    # Found next class/function at same or lower indent
                    break
                test_content.append(test_line)
                j += 1
            
            test_text = '\n'.join(test_content)
            category = categorize_test(test_text, filename)
            
            # Check if already has this marker
            has_marker = False
            if i > 0:
                prev_lines = modified_lines[max(0, i-5):i]
                for prev_line in prev_lines:
                    if f'@pytest.mark.{category}' in prev_line:
                        has_marker = True
                        break
            
            if not has_marker:
                # Add the marker
                indent = ' ' * indent_level
                marker_line = f'{indent}@pytest.mark.{category}'
                
                # Find where to insert (after any existing decorators)
                insert_pos = i
                while insert_pos > 0 and modified_lines[insert_pos - 1].strip().startswith('@'):
                    insert_pos -= 1
                
                modified_lines.insert(insert_pos, marker_line)
                i += 1  # Adjust index since we inserted a line
                
                if is_test_class:
                    changes.append(f"Added @pytest.mark.{category} to class {stripped.split()[1].rstrip(':')}")
                else:
                    func_name = re.search(r'def\s+(\w+)', stripped)
                    if func_name:
                        changes.append(f"Added @pytest.mark.{category} to function {func_name.group(1)}")
        
        i += 1
    
    return '\n'.join(modified_lines), changes


def process_test_file(file_path: Path) -> List[str]:
    """Process a single test file and add markers."""
    content = file_path.read_text()
    
    # Skip if already in a tier directory
    if any(part in ['ci', 'efficacy', 'performance'] for part in file_path.parts):
        return []
    
    # Skip if it's not a test file
    if not file_path.name.startswith('test_'):
        return []
    
    # Process the file
    new_content, changes = add_markers_to_content(content, file_path.name)
    
    if changes:
        file_path.write_text(new_content)
        
    return changes


def main():
    """Main entry point."""
    print("=== Test Marker Addition Script v2 ===")
    print("Adding pytest markers to ALL test functions and classes...\n")
    
    test_dir = Path('tests')
    test_files = list(test_dir.rglob('test_*.py'))
    
    total_changes = 0
    file_changes = {}
    
    for test_file in sorted(test_files):
        changes = process_test_file(test_file)
        if changes:
            file_changes[test_file] = changes
            total_changes += len(changes)
    
    # Print summary
    print(f"\n=== Summary ===")
    print(f"Processed {len(test_files)} test files")
    print(f"Modified {len(file_changes)} files")
    print(f"Added {total_changes} markers total\n")
    
    # Print details
    if file_changes:
        print("=== Changes by File ===")
        for file_path, changes in file_changes.items():
            print(f"\n{file_path}:")
            for change in changes:
                print(f"  - {change}")
    
    # Category summary
    category_counts = {'ci': 0, 'efficacy': 0, 'performance': 0}
    for changes in file_changes.values():
        for change in changes:
            for cat in category_counts:
                if f'@pytest.mark.{cat}' in change:
                    category_counts[cat] += 1
    
    print(f"\n=== Markers Added by Category ===")
    for cat, count in category_counts.items():
        print(f"{cat}: {count} markers")
    
    print("\n✅ Complete! Run 'pytest -m <tier>' to test each tier.")


if __name__ == "__main__":
    main()