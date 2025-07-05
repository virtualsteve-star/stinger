#!/usr/bin/env python3
"""
Categorize tests into appropriate tiers based on their characteristics.

This script analyzes test files and suggests which tier they belong to:
- CI: Fast tests without AI calls
- Efficacy: Tests that validate AI behavior
- Performance: Load and scalability tests
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Set


def uses_ai_calls(file_path: Path) -> bool:
    """Check if a test file uses AI guardrails."""
    try:
        content = file_path.read_text()
        
        # Check for AI guardrail imports
        ai_indicators = [
            'AIBasedPIIDetectionGuardrail',
            'AIBasedToxicityGuardrail', 
            'PromptInjectionGuardrail',
            'ContentModerationGuardrail',
            'ai_based_pii',
            'ai_based_toxicity',
            'prompt_injection',
            'content_moderation',
            'OpenAI',
            'openai'
        ]
        
        for indicator in ai_indicators:
            if indicator in content:
                return True
                
        return False
    except Exception:
        return False


def is_performance_test(file_path: Path) -> bool:
    """Check if a test is focused on performance."""
    name = file_path.name.lower()
    content = file_path.read_text().lower()
    
    performance_indicators = [
        'performance',
        'benchmark',
        'load',
        'stress',
        'scalability',
        'concurrent',
        'throughput',
        'latency'
    ]
    
    return any(ind in name or ind in content for ind in performance_indicators)


def is_slow_test(file_path: Path) -> bool:
    """Check if test is marked as slow or has slow test names."""
    content = file_path.read_text()
    
    slow_indicators = [
        '@pytest.mark.slow',
        'test_encoding_based_bypasses',
        'test_injection_evasion_techniques',
        'test_sophisticated_injections',
        'test_ai_guardrail_performance_benchmarks',
        'test_bypass_techniques',
        'test_prompt_injection_accuracy'
    ]
    
    return any(ind in content for ind in slow_indicators)


def categorize_test_file(file_path: Path) -> str:
    """Categorize a single test file."""
    # Performance tests
    if is_performance_test(file_path):
        return 'performance'
    
    # AI-based tests go to efficacy
    if uses_ai_calls(file_path):
        return 'efficacy'
    
    # Slow tests without AI also go to efficacy
    if is_slow_test(file_path):
        return 'efficacy'
    
    # Everything else is CI
    return 'ci'


def analyze_all_tests() -> Dict[str, List[Path]]:
    """Analyze all test files and categorize them."""
    test_dir = Path('tests')
    categories = {
        'ci': [],
        'efficacy': [],
        'performance': []
    }
    
    # Find all test files
    test_files = list(test_dir.rglob('test_*.py'))
    
    for test_file in test_files:
        # Skip files already in tier directories
        if any(part in ['ci', 'efficacy', 'performance'] for part in test_file.parts):
            continue
            
        category = categorize_test_file(test_file)
        categories[category].append(test_file)
    
    return categories


def print_categorization_report(categories: Dict[str, List[Path]]) -> None:
    """Print a report of test categorization."""
    print("=== Test Categorization Report ===\n")
    
    total_tests = sum(len(files) for files in categories.values())
    print(f"Total test files to categorize: {total_tests}\n")
    
    for tier, files in categories.items():
        print(f"{tier.upper()} Tier ({len(files)} files):")
        print("-" * 40)
        
        # Group by directory
        by_dir: Dict[str, List[Path]] = {}
        for f in sorted(files):
            dir_name = str(f.parent.relative_to('tests'))
            if dir_name not in by_dir:
                by_dir[dir_name] = []
            by_dir[dir_name].append(f)
        
        for dir_name, dir_files in sorted(by_dir.items()):
            print(f"\n  {dir_name}/")
            for f in sorted(dir_files)[:5]:
                print(f"    - {f.name}")
            if len(dir_files) > 5:
                print(f"    ... and {len(dir_files) - 5} more")
        
        print()


def generate_migration_script(categories: Dict[str, List[Path]]) -> None:
    """Generate a script to migrate tests to appropriate tiers."""
    print("\n=== Migration Commands ===\n")
    print("# Run these commands to reorganize tests:\n")
    
    for tier, files in categories.items():
        if not files:
            continue
            
        print(f"# {tier.upper()} tier migrations:")
        for f in sorted(files):
            # Determine if we need to add markers or move files
            relative_path = f.relative_to('tests')
            
            # For now, just add markers - don't move files
            print(f"# Add @pytest.mark.{tier} to {relative_path}")
        
        print()


def main():
    """Main entry point."""
    print("Analyzing test files...\n")
    
    categories = analyze_all_tests()
    print_categorization_report(categories)
    generate_migration_script(categories)
    
    # Print summary
    print("\n=== Summary ===")
    print(f"CI tests (fast, no AI): {len(categories['ci'])}")
    print(f"Efficacy tests (AI behavior): {len(categories['efficacy'])}")
    print(f"Performance tests (load/scale): {len(categories['performance'])}")
    
    print("\nNext steps:")
    print("1. Review the categorization above")
    print("2. Add appropriate pytest markers to each test file")
    print("3. Move tests to tier directories if desired")
    print("4. Update CI/CD pipelines to run appropriate tiers")


if __name__ == "__main__":
    main()