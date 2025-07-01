#!/usr/bin/env python3
"""
Update all examples to follow the standardized pattern.
This script adds prerequisite checking and error handling to all examples.
"""

import os
import sys
from pathlib import Path
import re


# Standard prerequisite check to add to examples
PREREQUISITE_CHECK = '''def check_prerequisites() -> bool:
    """Check if all prerequisites are met."""
    print("🔍 Checking prerequisites...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    
    # Check if Stinger is installed
    try:
        import stinger
        print("✅ Stinger is installed")
    except ImportError:
        print("❌ Stinger is not installed")
        print("   Install with: pip install stinger-guardrails-alpha")
        return False
    
    return True
'''

# Standard main wrapper
MAIN_WRAPPER = '''def main():
    """Main entry point with proper error handling."""
    # Check prerequisites
    if not check_prerequisites():
        print("\\n⚠️  Prerequisites not met. Please fix the issues above.")
        return 1
    
    # Run the example
    try:
        run_example()
        print("\\n✅ Example completed successfully!")
        return 0
    except Exception as e:
        print(f"\\n❌ Example failed: {e}")
        print("\\n💡 Troubleshooting:")
        print("   1. Check error message above")
        print("   2. Ensure environment is configured")
        print("   3. Run: stinger setup")
        return 1


if __name__ == "__main__":
    sys.exit(main())
'''


def needs_update(content: str) -> bool:
    """Check if file needs updating."""
    # Skip if already has prerequisite check
    if "check_prerequisites" in content:
        return False
    
    # Skip if it's a utility file
    if "if __name__" not in content:
        return False
        
    return True


def update_example(file_path: Path) -> bool:
    """Update a single example file."""
    print(f"Checking {file_path.name}...")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    if not needs_update(content):
        print(f"  ✓ Already updated or doesn't need update")
        return False
    
    # Extract the main logic
    # Look for the main() function
    main_match = re.search(r'def main\(\):(.*?)(?=\nif __name__|$)', content, re.DOTALL)
    if not main_match:
        print(f"  ⚠️  No main() function found, skipping")
        return False
    
    main_body = main_match.group(1)
    
    # Create updated content
    imports = "import sys\nimport os\n"
    
    # Extract existing imports
    import_section = re.findall(r'^(import .*|from .* import .*)$', content, re.MULTILINE)
    if import_section:
        # Add sys and os if not already there
        has_sys = any('import sys' in imp for imp in import_section)
        has_os = any('import os' in imp for imp in import_section)
        
        if not has_sys:
            import_section.insert(0, 'import sys')
        if not has_os:
            import_section.insert(1, 'import os')
        
        imports = '\n'.join(import_section)
    
    # Extract docstring
    docstring_match = re.match(r'^(#!/usr/bin/env python3\n)?(""".*?""")', content, re.DOTALL)
    docstring = docstring_match.group(0) if docstring_match else '"""Example"""'
    
    # Build new content
    new_content = f'''#!/usr/bin/env python3
{docstring}

{imports}


{PREREQUISITE_CHECK}


def run_example():
    """Run the main example code."""
{main_body}


{MAIN_WRAPPER}'''
    
    # Write backup
    backup_path = file_path.with_suffix('.py.bak')
    with open(backup_path, 'w') as f:
        f.write(content)
    
    # Write updated file
    with open(file_path, 'w') as f:
        f.write(new_content)
    
    print(f"  ✅ Updated {file_path.name}")
    return True


def main():
    """Update all examples."""
    print("🔄 Updating Stinger Examples")
    print("=" * 40)
    
    examples_dir = Path(__file__).parent
    getting_started_dir = examples_dir / "getting_started"
    
    if not getting_started_dir.exists():
        print("❌ getting_started directory not found")
        return 1
    
    # Process all Python files
    updated = 0
    for py_file in getting_started_dir.glob("*.py"):
        if py_file.name.endswith('_enhanced.py'):
            continue  # Skip already enhanced files
            
        if update_example(py_file):
            updated += 1
    
    print(f"\n✅ Updated {updated} example files")
    print("   Backup files created with .bak extension")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())