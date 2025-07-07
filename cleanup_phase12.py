#!/usr/bin/env python3
"""Clean up repository and commit Phase 12 changes."""
import subprocess
import os
import sys

def run_git_command(cmd, description):
    """Run a git command and report results."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Success: {description}")
            if result.stdout:
                print(f"   {result.stdout.strip()}")
            return True
        else:
            print(f"⚠️  Warning: {description}")
            if result.stderr:
                print(f"   {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Execute cleanup and commit process."""
    print("🧹 Cleaning up repository and committing Phase 12")
    print("=" * 50)
    
    # Change to repository root
    os.chdir('/Users/steve/Documents/GitHub/Stinger')
    
    # Step 1: Stage documentation moves
    print("\n📁 Step 1: Staging documentation reorganization")
    run_git_command("git add docs/plans/", "Add new documentation location")
    
    # Remove old documentation files
    old_docs = [
        "docs/DOCUMENTATION_UPDATE_SUMMARY.md",
        "docs/Phase7D1_Completion_Summary.md",
        "docs/Phase7D2_Completion_Summary.md",
        "docs/Phase7D2_WebDemo_Fix_Plan.md",
        "docs/Phase7D3_Completion_Summary.md",
        "docs/Phase7D4_Completion_Summary.md",
        "docs/Phase7E_Test_Consolidation_Summary.md",
        "docs/Phase7_Pre_Close_Deep_Review.md",
        "docs/Phase7_Progress_Update.md",
        "docs/QA_FIXES_SUMMARY.md",
        "docs/Security_Fixes_Summary.md",
        "docs/Test_Cleanup_Plan.md",
        "docs/Test_Cleanup_Summary.md"
    ]
    
    for doc in old_docs:
        run_git_command(f"git rm {doc} 2>/dev/null", f"Remove {os.path.basename(doc)}")
    
    # Step 2: Remove obsolete test files
    print("\n🧪 Step 2: Removing obsolete test files")
    old_tests = [
        "tests/scenarios/customer_service/customer_service_test_runner.py",
        "tests/scenarios/medical_bot/medical_bot_test_runner.py",
        "tests/scenarios/run_all_tests.py",
        "tests/test_classic_guardrail_pipeline.py",
        "tests/test_integration.py",
        "tests/test_runner.py"
    ]
    
    for test in old_tests:
        run_git_command(f"git rm {test} 2>/dev/null", f"Remove {os.path.basename(test)}")
    
    # Step 3: Commit reorganization
    print("\n💾 Step 3: Committing reorganization")
    commit_msg = """Reorganize documentation into plans directory and remove obsolete test files

- Move all phase documentation to docs/plans/ for better organization
- Remove obsolete test runners (replaced by new test organization)
- Clean up repository structure"""
    
    run_git_command(f'git commit -m "{commit_msg}"', "Commit reorganization")
    
    # Step 4: Stage Phase 12 changes
    print("\n📦 Step 4: Staging Phase 12 changes")
    phase12_files = [
        ".github/workflows/publish.yml",
        "RELEASING.md",
        "scripts/build_package.sh",
        "scripts/upload_to_pypi.sh",
        "scripts/test_pypi_package.sh",
        "scripts/pre_publish_check.sh",
        "scripts/verify_pypi_release.py",
        "scripts/run_phase12_tests.sh",
        "pyproject.toml",
        "src/stinger/__init__.py",
        ".bumpversion.cfg",
        "CHANGELOG.md",
        "docs/GETTING_STARTED.md",
        "docs/plans/Phase12*.md",
        "run_phase12_tests.py",
        "check_ci_readiness.py",
        "cleanup_and_commit.sh",
        "cleanup_phase12.py"
    ]
    
    for file in phase12_files:
        if '*' in file:
            run_git_command(f"git add {file}", f"Add {file}")
        else:
            if os.path.exists(file):
                run_git_command(f"git add {file}", f"Add {os.path.basename(file)}")
    
    # Step 5: Commit Phase 12
    print("\n💾 Step 5: Committing Phase 12")
    commit_msg = """Phase 12 Complete: PyPI Publishing Infrastructure for v0.1.0a3

- Add GitHub Actions workflow for automated publishing
- Create comprehensive test suite for package verification  
- Add build and upload helper scripts
- Update version to 0.1.0a3
- Add RELEASING.md documentation
- Fix documentation issues found during review
- Enhanced tests to verify positive/negative cases for input/output guardrails"""
    
    run_git_command(f'git commit -m "{commit_msg}"', "Commit Phase 12")
    
    # Step 6: Show status
    print("\n📊 Step 6: Current status")
    run_git_command("git status --short", "Git status")
    
    # Show recent commits
    print("\n📝 Recent commits:")
    run_git_command("git log --oneline -5", "Recent commits")
    
    print("\n✅ Cleanup and commits complete!")
    print("\nNext steps:")
    print("1. Run: ./scripts/local-ci-check.sh")
    print("2. Push to dev: git push origin dev")
    print("3. Check CI: gh run list --branch dev")
    print("4. Create PR: gh pr create --base main --head dev")

if __name__ == "__main__":
    main()