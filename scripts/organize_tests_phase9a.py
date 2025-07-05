#!/usr/bin/env python3
"""
Phase 9A: Test Organization Script
Reorganizes test files into proper subdirectories based on their pytest markers.
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

# Define the test categorization rules
MARKER_TO_DIR = {
    'efficacy': 'efficacy',
    'performance': 'performance',
    'ci': 'ci',
    'integration': 'integration',
    'behavioral': 'behavioral',
}

# Files that should remain in root (unit tests)
UNIT_TEST_PATTERNS = [
    r'^test_simple_.*_guardrail\.py$',  # Simple guardrail unit tests
    r'^test_.*_guardrail\.py$',  # Other guardrail unit tests
    r'^test_guardrail_factory_and_api_filters\.py$',  # Core factory test
]

# Files to move based on content/name patterns (override markers if needed)
CONTENT_BASED_MOVES = {
    'validation': [
        'test_input_validation.py',
        'test_schema_validation.py',
        'test_error_handling.py',
        'test_utilities.py',
        'test_regex_security.py',
    ],
    'integration': [
        'test_integration_guardrails.py',
        'test_conversation_integration.py',
        'test_audit_trail_integration.py',
        'test_conversation_aware_prompt_injection.py',
    ],
    'efficacy': [
        'test_ai_guardrails_integration.py',
        'test_openai_content_moderation.py',
        'test_openai_prompt_injection.py',
    ],
    'performance': [
        'test_performance_validation.py',
    ],
}

# Audit-related tests should go to integration
AUDIT_TESTS = [
    'test_audit_async_buffering.py',
    'test_audit_comprehensive.py',
    'test_audit_export.py',
    'test_audit_query_tools.py',
    'test_audit_trail_basic.py',
    'test_audit_trail_integration.py',
]


def find_markers(file_path: Path) -> List[str]:
    """Extract pytest markers from a test file."""
    markers = []
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Find all pytest markers
        marker_pattern = r'@pytest\.mark\.(\w+)'
        found_markers = re.findall(marker_pattern, content)
        
        # Count occurrences
        marker_counts = {}
        for marker in found_markers:
            marker_counts[marker] = marker_counts.get(marker, 0) + 1
            
        # Return unique markers sorted by frequency
        markers = sorted(marker_counts.keys(), key=lambda x: marker_counts[x], reverse=True)
        
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        
    return markers


def should_remain_unit_test(filename: str) -> bool:
    """Check if a test file should remain in the root as a unit test."""
    for pattern in UNIT_TEST_PATTERNS:
        if re.match(pattern, filename):
            return True
    return False


def categorize_test_file(file_path: Path) -> str:
    """Determine which directory a test file should be in."""
    filename = file_path.name
    
    # Check if it's a unit test that should stay in root
    if should_remain_unit_test(filename):
        return 'root'
    
    # Check content-based moves first (these override markers)
    for target_dir, files in CONTENT_BASED_MOVES.items():
        if filename in files:
            return target_dir
            
    # Check if it's an audit test
    if filename in AUDIT_TESTS:
        return 'integration'
    
    # Check markers
    markers = find_markers(file_path)
    
    # Prioritize markers
    for marker in markers:
        if marker in MARKER_TO_DIR:
            return MARKER_TO_DIR[marker]
    
    # Default rules based on filename patterns
    if 'integration' in filename:
        return 'integration'
    elif 'validation' in filename or 'error' in filename:
        return 'validation'
    elif 'performance' in filename:
        return 'performance'
    elif 'ai_' in filename or 'openai' in filename:
        return 'efficacy'
    elif 'conversation' in filename or 'audit' in filename:
        return 'integration'
    
    # Default to root (unit test)
    return 'root'


def organize_tests(dry_run: bool = True):
    """Organize test files into proper subdirectories."""
    tests_dir = Path(__file__).parent.parent / 'tests'
    
    # Create subdirectories if they don't exist
    subdirs = ['efficacy', 'performance', 'integration', 'validation', 'ci', 'behavioral', 'human']
    for subdir in subdirs:
        subdir_path = tests_dir / subdir
        if not subdir_path.exists():
            if not dry_run:
                subdir_path.mkdir(exist_ok=True)
                # Create __init__.py if it doesn't exist
                init_file = subdir_path / '__init__.py'
                if not init_file.exists():
                    init_file.write_text("")
            print(f"{'Would create' if dry_run else 'Created'} directory: {subdir_path}")
    
    # Find all test files in root
    test_files = list(tests_dir.glob('test_*.py'))
    
    # Categorize and move files
    moves = []
    for test_file in test_files:
        if test_file.is_file():
            category = categorize_test_file(test_file)
            
            if category != 'root':
                target_dir = tests_dir / category
                target_path = target_dir / test_file.name
                
                # Check if file already exists in target
                if target_path.exists():
                    print(f"⚠️  {test_file.name} already exists in {category}/, skipping")
                else:
                    moves.append((test_file, target_path, category))
    
    # Display planned moves
    if moves:
        print(f"\n{'Planned' if dry_run else 'Executing'} file moves:")
        print("-" * 60)
        
        # Group by category
        moves_by_category = {}
        for src, dst, cat in moves:
            if cat not in moves_by_category:
                moves_by_category[cat] = []
            moves_by_category[cat].append(src.name)
        
        for category, files in sorted(moves_by_category.items()):
            print(f"\n→ {category}/")
            for filename in sorted(files):
                print(f"  - {filename}")
        
        print(f"\nTotal files to move: {len(moves)}")
        
        if not dry_run:
            # Execute moves
            for src, dst, cat in moves:
                shutil.move(str(src), str(dst))
                print(f"✓ Moved {src.name} to {cat}/")
    else:
        print("\nNo files need to be moved.")
    
    # Report on files remaining in root
    remaining = []
    for test_file in tests_dir.glob('test_*.py'):
        if test_file.is_file():
            remaining.append(test_file.name)
    
    if remaining:
        print(f"\nFiles remaining in root (unit tests):")
        for filename in sorted(remaining):
            print(f"  - {filename}")
    
    return len(moves)


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Organize test files based on pytest markers")
    parser.add_argument('--execute', action='store_true', 
                       help='Actually move files (default is dry run)')
    
    args = parser.parse_args()
    
    print("Phase 9A: Test Organization Script")
    print("=" * 60)
    
    if args.execute:
        print("🚀 EXECUTING file moves...\n")
        organize_tests(dry_run=False)
        print("\n✅ Test reorganization complete!")
    else:
        print("🔍 DRY RUN mode (use --execute to actually move files)\n")
        organize_tests(dry_run=True)
        print("\n💡 Run with --execute to perform these moves")


if __name__ == "__main__":
    main()