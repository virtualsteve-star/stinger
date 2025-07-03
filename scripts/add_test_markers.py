#!/usr/bin/env python3
"""
Add pytest markers to test files based on their characteristics.

This script helps migrate existing tests to the three-tier system.
"""

import re
from pathlib import Path
from typing import List, Tuple


def uses_ai_imports(content: str) -> bool:
    """Check if test imports AI-related guardrails."""
    ai_patterns = [
        r'ContentModerationGuardrail',
        r'PromptInjectionGuardrail',
        r'from.*openai',
        r'import.*openai',
        r'AIBased.*Guardrail',
        r'ai_based.*guardrail'
    ]
    
    for pattern in ai_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return True
    return False


def is_performance_focused(content: str) -> bool:
    """Check if test is focused on performance testing."""
    perf_patterns = [
        r'performance',
        r'benchmark',
        r'load.*test',
        r'stress.*test',
        r'concurrent',
        r'throughput',
        r'latency',
        r'time\.time\(\)',
        r'elapsed.*time',
        r'measure.*time'
    ]
    
    for pattern in perf_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return True
    return False


def has_markers(content: str) -> List[str]:
    """Extract existing markers from test file."""
    markers = []
    marker_pattern = r'@pytest\.mark\.(\w+)'
    matches = re.findall(marker_pattern, content)
    return list(set(matches))


def add_marker_to_file(file_path: Path, marker: str) -> bool:
    """Add a pytest marker to a test file."""
    content = file_path.read_text()
    
    # Check if already has the marker
    existing_markers = has_markers(content)
    if marker in existing_markers:
        return False
    
    # Find the right place to add the marker
    lines = content.split('\n')
    
    # Look for existing class or function definitions
    import_section_end = 0
    for i, line in enumerate(lines):
        if line.strip() and not line.startswith('import') and not line.startswith('from'):
            if not line.startswith('#') and not line.startswith('"""'):
                import_section_end = i
                break
    
    # Add marker import if needed
    if '@pytest.mark' not in content:
        # Find where to add pytest import
        pytest_imported = False
        for i, line in enumerate(lines):
            if 'import pytest' in line:
                pytest_imported = True
                break
        
        if not pytest_imported:
            lines.insert(import_section_end, 'import pytest\n')
            import_section_end += 1
    
    # Add marker to classes
    modified = False
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('class Test'):
            # Add marker before class
            indent = len(line) - len(line.lstrip())
            marker_line = ' ' * indent + f'@pytest.mark.{marker}'
            
            # Check if previous line is already a marker
            if i > 0 and '@pytest.mark' in lines[i-1]:
                # Add after existing markers
                lines.insert(i, marker_line)
                i += 1
            else:
                lines.insert(i, marker_line)
                i += 1
            modified = True
        i += 1
    
    if modified:
        file_path.write_text('\n'.join(lines))
    
    return modified


def categorize_and_mark_tests():
    """Categorize all tests and add appropriate markers."""
    test_dir = Path('tests')
    
    # Files to process
    test_files = list(test_dir.rglob('test_*.py'))
    
    # Skip already marked files
    files_to_mark = []
    for test_file in test_files:
        # Skip files in tier directories
        if any(part in ['ci', 'efficacy', 'performance'] for part in test_file.parts):
            continue
            
        content = test_file.read_text()
        markers = has_markers(content)
        
        # Skip if already has tier markers
        if any(m in ['ci', 'efficacy', 'performance'] for m in markers):
            continue
            
        files_to_mark.append(test_file)
    
    print(f"Found {len(files_to_mark)} test files without tier markers\n")
    
    # Categorize and mark each file
    marked_files = {'ci': [], 'efficacy': [], 'performance': []}
    
    for test_file in files_to_mark:
        content = test_file.read_text()
        
        # Determine category
        if uses_ai_imports(content):
            category = 'efficacy'
        elif is_performance_focused(content):
            category = 'performance'
        else:
            category = 'ci'
        
        # Add marker
        if add_marker_to_file(test_file, category):
            marked_files[category].append(test_file)
            print(f"Added @pytest.mark.{category} to {test_file}")
    
    # Summary
    print("\n=== Summary ===")
    for category, files in marked_files.items():
        print(f"{category}: {len(files)} files marked")


def main():
    """Main entry point."""
    print("Adding pytest markers to test files...")
    print("This will help organize tests into the three-tier system\n")
    
    categorize_and_mark_tests()
    
    print("\nNext steps:")
    print("1. Review the markers added to ensure they're correct")
    print("2. Run tests by tier: pytest -m ci")
    print("3. Consider moving tests to tier directories if desired")


if __name__ == "__main__":
    main()