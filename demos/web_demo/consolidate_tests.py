#!/usr/bin/env python3
"""
Consolidate web demo test files.
This script backs up and removes redundant test files after consolidation.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime


def main():
    """Consolidate test files."""
    print("🧹 Consolidating Web Demo Test Files")
    print("=" * 40)
    
    # Files to keep (new consolidated tests)
    keep_files = [
        "test_core_functionality.py",
        "test_integration_complete.py",
        "test_browser_e2e.py",
    ]
    
    # Files to remove (redundant tests)
    remove_files = [
        "test_actual_e2e.py",
        "test_basic_functionality.py",
        "test_demo_e2e.py",
        "test_demo_integration.py",
        "test_e2e_comprehensive.py",
        "test_integration_e2e.py",
        "test_quick_e2e.py",
        "test_real_e2e.py",
        "test_real_frontend_backend.py",
        "test_simple_e2e.py",
        "test_startup_detection.py",
        "test_startup.py",
        "test_true_e2e.py",
        "test_working_e2e.py",
    ]
    
    web_demo_dir = Path(__file__).parent
    
    # Create backup directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = web_demo_dir / f"test_backup_{timestamp}"
    backup_dir.mkdir(exist_ok=True)
    
    print(f"\n📁 Creating backup in: {backup_dir}")
    
    # Back up files to remove
    backed_up = 0
    for filename in remove_files:
        file_path = web_demo_dir / filename
        if file_path.exists():
            backup_path = backup_dir / filename
            shutil.copy2(file_path, backup_path)
            backed_up += 1
            print(f"  ✓ Backed up {filename}")
            
    print(f"\n✅ Backed up {backed_up} files")
    
    # Remove redundant files
    removed = 0
    print("\n🗑️  Removing redundant test files...")
    for filename in remove_files:
        file_path = web_demo_dir / filename
        if file_path.exists():
            file_path.unlink()
            removed += 1
            print(f"  ✓ Removed {filename}")
            
    print(f"\n✅ Removed {removed} redundant files")
    
    # Verify consolidated files exist
    print("\n📋 Verifying consolidated test files...")
    for filename in keep_files:
        file_path = web_demo_dir / filename
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  ✓ {filename} ({size:,} bytes)")
        else:
            print(f"  ❌ {filename} NOT FOUND")
            
    # Summary
    print("\n" + "=" * 40)
    print("📊 Consolidation Summary:")
    print(f"  - Original test files: 14")
    print(f"  - Consolidated to: 3")
    print(f"  - Reduction: 78.6%")
    print(f"  - Backup location: {backup_dir}")
    
    print("\n✅ Test consolidation complete!")
    print("\nTo restore original files if needed:")
    print(f"  cp {backup_dir}/*.py .")


if __name__ == "__main__":
    main()