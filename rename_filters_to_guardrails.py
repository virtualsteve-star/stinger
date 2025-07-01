#!/usr/bin/env python3
"""
Phase 7B.3 Part 1: Comprehensive Filter → Guardrail Renaming Script

This script systematically renames all occurrences of "filter" to "guardrail"
throughout the Stinger codebase for consistency.
"""

import os
import re
import shutil
from pathlib import Path
from typing import List, Tuple, Dict

# Define the renaming patterns
FILE_RENAMES = {
    # Implementation files
    'ai_code_generation_filter.py': 'ai_code_generation_guardrail.py',
    'ai_pii_detection_filter.py': 'ai_pii_detection_guardrail.py',
    'ai_toxicity_detection_filter.py': 'ai_toxicity_detection_guardrail.py',
    'base_ai_filter.py': 'base_ai_guardrail.py',
    'content_moderation_filter.py': 'content_moderation_guardrail.py',
    'keyword_block_filter.py': 'keyword_block_guardrail.py',
    'keyword_list_filter.py': 'keyword_list_guardrail.py',
    'length_filter.py': 'length_guardrail.py',
    'pass_through_filter.py': 'pass_through_guardrail.py',
    'prompt_injection_filter.py': 'prompt_injection_guardrail.py',
    'regex_filter.py': 'regex_guardrail.py',
    'simple_code_generation_filter.py': 'simple_code_generation_guardrail.py',
    'simple_pii_detection_filter.py': 'simple_pii_detection_guardrail.py',
    'simple_toxicity_detection_filter.py': 'simple_toxicity_detection_guardrail.py',
    'topic_filter.py': 'topic_guardrail.py',
    'url_filter.py': 'url_guardrail.py',
}

# Class name mappings
CLASS_RENAMES = {
    'AICodeGenerationGuardrail': 'AICodeGenerationGuardrail',
    'AIPIIDetectionGuardrail': 'AIPIIDetectionGuardrail',
    'AIToxicityDetectionGuardrail': 'AIToxicityDetectionGuardrail',
    'BaseAIGuardrail': 'BaseAIGuardrail',
    'ContentModerationGuardrail': 'ContentModerationGuardrail',
    'KeywordBlockGuardrail': 'KeywordBlockGuardrail',
    'KeywordListGuardrail': 'KeywordListGuardrail',
    'LengthGuardrail': 'LengthGuardrail',
    'PassThroughGuardrail': 'PassThroughGuardrail',
    'PromptInjectionGuardrail': 'PromptInjectionGuardrail',
    'RegexGuardrail': 'RegexGuardrail',
    'SimpleCodeGenerationGuardrail': 'SimpleCodeGenerationGuardrail',
    'SimplePIIDetectionGuardrail': 'SimplePIIDetectionGuardrail',
    'SimpleToxicityDetectionGuardrail': 'SimpleToxicityDetectionGuardrail',
    'TopicGuardrail': 'TopicGuardrail',
    'URLGuardrail': 'URLGuardrail',
    # Base classes
    'BaseGuardrail': 'BaseGuardrail',
    'ValidatedGuardrail': 'ValidatedGuardrail',
}

# Import statement patterns
IMPORT_PATTERNS = [
    (r'from \.filters import', 'from .guardrails import'),
    (r'from src\.stinger\.filters', 'from src.stinger.guardrails'),
    (r'from stinger\.filters', 'from stinger.guardrails'),
    (r'from \.\.filters', 'from ..guardrails'),
    (r'src/stinger/guardrails/', 'src/stinger/guardrails/'),
]

# Variable and config key patterns
VARIABLE_PATTERNS = [
    (r'\bfilter_obj\b', 'guardrail_obj'),
    (r'\bfilter_instance\b', 'guardrail_instance'),
    (r'\bfilter_config\b', 'guardrail_config'),
    (r'\bfilter_type\b', 'guardrail_type'),
    (r'\bfilter_name\b', 'guardrail_name'),
    (r'\bfilters\b(?=\s*=|\s*:)', 'guardrails'),  # guardrails = or guardrails:
    (r'["\']filters["\'](?=\s*:)', '"guardrails"'),  # "guardrails":
    (r'GUARDRAIL_REGISTRY', 'GUARDRAIL_REGISTRY'),
    (r'guardrail_registry', 'guardrail_registry'),
]

# Test file patterns
TEST_FILE_RENAMES = {
    'test_keyword_block_filter.py': 'test_keyword_block_guardrail.py',
    'test_keyword_list_filter.py': 'test_keyword_list_guardrail.py',
    'test_length_filter.py': 'test_length_guardrail.py',
    'test_regex_filter.py': 'test_regex_guardrail.py',
    'test_topic_filter.py': 'test_topic_guardrail.py',
    'test_url_filter.py': 'test_url_guardrail.py',
    'test_simple_code_generation_filter.py': 'test_simple_code_generation_guardrail.py',
    'test_simple_pii_detection_filter.py': 'test_simple_pii_detection_guardrail.py',
    'test_simple_toxicity_detection_filter.py': 'test_simple_toxicity_detection_guardrail.py',
    'test_ai_filters_integration.py': 'test_ai_guardrails_integration.py',
    'test_classic_filter_pipeline.py': 'test_classic_guardrail_pipeline.py',
    'test_integration_filters.py': 'test_integration_guardrails.py',
}


def rename_files(directory: Path, renames: Dict[str, str]) -> List[Tuple[Path, Path]]:
    """Rename files according to the mapping."""
    renamed = []
    
    for old_name, new_name in renames.items():
        old_path = directory / old_name
        if old_path.exists():
            new_path = directory / new_name
            old_path.rename(new_path)
            renamed.append((old_path, new_path))
            print(f"✓ Renamed: {old_name} → {new_name}")
        else:
            # Try to find it with glob
            matches = list(directory.glob(f"**/{old_name}"))
            for old_path in matches:
                new_path = old_path.parent / new_name
                old_path.rename(new_path)
                renamed.append((old_path, new_path))
                print(f"✓ Renamed: {old_path.relative_to(directory)} → {new_path.relative_to(directory)}")
    
    return renamed


def update_file_contents(file_path: Path, patterns: List[Tuple[str, str]]) -> bool:
    """Update file contents with regex patterns."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Apply all patterns
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        # Apply class renames
        for old_class, new_class in CLASS_RENAMES.items():
            content = re.sub(rf'\b{old_class}\b', new_class, content)
        
        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    except Exception as e:
        print(f"✗ Error updating {file_path}: {e}")
        return False


def update_all_files(root_dir: Path) -> int:
    """Update all Python files in the directory."""
    updated = 0
    patterns = IMPORT_PATTERNS + VARIABLE_PATTERNS
    
    # Find all Python files
    for py_file in root_dir.rglob("*.py"):
        # Skip virtual environments and build directories
        if any(part in py_file.parts for part in ['.venv', 'venv', 'build', 'dist', '__pycache__', '.git']):
            continue
        
        if update_file_contents(py_file, patterns):
            updated += 1
            print(f"✓ Updated: {py_file.relative_to(root_dir)}")
    
    # Also update YAML files
    for yaml_file in root_dir.rglob("*.yaml"):
        if any(part in yaml_file.parts for part in ['.venv', 'venv', 'build', 'dist', '.git']):
            continue
        
        if update_file_contents(yaml_file, VARIABLE_PATTERNS):
            updated += 1
            print(f"✓ Updated: {yaml_file.relative_to(root_dir)}")
    
    # Update Markdown files
    for md_file in root_dir.rglob("*.md"):
        if any(part in md_file.parts for part in ['.venv', 'venv', 'build', 'dist', '.git']):
            continue
        
        if update_file_contents(md_file, patterns):
            updated += 1
            print(f"✓ Updated: {md_file.relative_to(root_dir)}")
    
    return updated


def main():
    """Main execution function."""
    print("=" * 60)
    print("Phase 7B.3 Part 1: Filter → Guardrail Renaming")
    print("=" * 60)
    
    # Get project root
    project_root = Path(__file__).parent
    guardrails_dir = project_root / "src" / "stinger" / "guardrails"
    tests_dir = project_root / "tests"
    
    if not guardrails_dir.exists():
        print("✗ Guardrails directory not found. Did the rename happen?")
        return
    
    # Step 1: Rename implementation files
    print("\n1. Renaming implementation files...")
    impl_renamed = rename_files(guardrails_dir, FILE_RENAMES)
    print(f"   Renamed {len(impl_renamed)} implementation files")
    
    # Step 2: Rename test files
    print("\n2. Renaming test files...")
    test_renamed = rename_files(tests_dir, TEST_FILE_RENAMES)
    print(f"   Renamed {len(test_renamed)} test files")
    
    # Step 3: Update all file contents
    print("\n3. Updating file contents...")
    updated = update_all_files(project_root)
    print(f"   Updated {updated} files")
    
    # Step 4: Summary
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"✓ Renamed {len(impl_renamed)} implementation files")
    print(f"✓ Renamed {len(test_renamed)} test files")
    print(f"✓ Updated {updated} files with new references")
    print("\nNext steps:")
    print("1. Run tests to ensure nothing broke")
    print("2. Review changes with git diff")
    print("3. Proceed to Part 2 of Phase 7B.3")
    

if __name__ == "__main__":
    main()