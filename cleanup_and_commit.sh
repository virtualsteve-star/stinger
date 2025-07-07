#!/bin/bash
# Script to clean up repository and commit Phase 12

echo "🧹 Cleaning up repository and committing Phase 12..."
echo "=================================================="

# Step 1: Handle documentation reorganization
echo -e "\n📁 Step 1: Staging documentation reorganization..."
git add docs/plans/
git rm docs/DOCUMENTATION_UPDATE_SUMMARY.md 2>/dev/null || true
git rm docs/Phase7D1_Completion_Summary.md 2>/dev/null || true
git rm docs/Phase7D2_Completion_Summary.md 2>/dev/null || true
git rm docs/Phase7D2_WebDemo_Fix_Plan.md 2>/dev/null || true
git rm docs/Phase7D3_Completion_Summary.md 2>/dev/null || true
git rm docs/Phase7D4_Completion_Summary.md 2>/dev/null || true
git rm docs/Phase7E_Test_Consolidation_Summary.md 2>/dev/null || true
git rm docs/Phase7_Pre_Close_Deep_Review.md 2>/dev/null || true
git rm docs/Phase7_Progress_Update.md 2>/dev/null || true
git rm docs/QA_FIXES_SUMMARY.md 2>/dev/null || true
git rm docs/Security_Fixes_Summary.md 2>/dev/null || true
git rm docs/Test_Cleanup_Plan.md 2>/dev/null || true
git rm docs/Test_Cleanup_Summary.md 2>/dev/null || true

# Step 2: Handle test file deletions
echo -e "\n🧪 Step 2: Removing obsolete test files..."
git rm tests/scenarios/customer_service/customer_service_test_runner.py 2>/dev/null || true
git rm tests/scenarios/medical_bot/medical_bot_test_runner.py 2>/dev/null || true
git rm tests/scenarios/run_all_tests.py 2>/dev/null || true
git rm tests/test_classic_guardrail_pipeline.py 2>/dev/null || true
git rm tests/test_integration.py 2>/dev/null || true
git rm tests/test_runner.py 2>/dev/null || true

# Step 3: Commit the reorganization
echo -e "\n💾 Step 3: Committing reorganization..."
git commit -m "Reorganize documentation into plans directory and remove obsolete test files

- Move all phase documentation to docs/plans/ for better organization
- Remove obsolete test runners (replaced by new test organization)
- Clean up repository structure" || echo "No reorganization changes to commit"

# Step 4: Stage Phase 12 changes
echo -e "\n📦 Step 4: Staging Phase 12 changes..."
git add .github/workflows/publish.yml
git add RELEASING.md
git add scripts/build_package.sh
git add scripts/upload_to_pypi.sh
git add scripts/test_pypi_package.sh
git add scripts/pre_publish_check.sh
git add scripts/verify_pypi_release.py
git add scripts/run_phase12_tests.sh
git add pyproject.toml
git add src/stinger/__init__.py
git add .bumpversion.cfg
git add CHANGELOG.md
git add docs/GETTING_STARTED.md
git add docs/plans/Phase12*.md
git add run_phase12_tests.py
git add check_ci_readiness.py

# Step 5: Commit Phase 12
echo -e "\n💾 Step 5: Committing Phase 12..."
git commit -m "Phase 12 Complete: PyPI Publishing Infrastructure for v0.1.0a3

- Add GitHub Actions workflow for automated publishing
- Create comprehensive test suite for package verification
- Add build and upload helper scripts
- Update version to 0.1.0a3
- Add RELEASING.md documentation
- Fix documentation issues found during review
- Enhanced tests to verify positive/negative cases for input/output guardrails" || echo "No Phase 12 changes to commit"

# Step 6: Show current status
echo -e "\n📊 Step 6: Current git status..."
git status

echo -e "\n✅ Cleanup and commits complete!"
echo "Next steps:"
echo "1. Run: ./scripts/local-ci-check.sh"
echo "2. Push to dev: git push origin dev"
echo "3. Check CI status: gh run list --branch dev"