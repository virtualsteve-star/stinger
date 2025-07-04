# Cleanup Needed

## Outdated Files to Remove

### 1. `stinger_test_runner.py`
- **Status**: Non-functional, outdated
- **Issue**: Looks for `test_runner.py` files in scenario directories that don't exist
- **Action**: DELETE this file

### 2. `docs/TEST_RUNNERS_GUIDE.md` 
- **Status**: Contains incorrect information about two test runners
- **Issue**: Documents stinger_test_runner.py which doesn't work
- **Action**: Either DELETE or UPDATE to only document run_test_suites.py

### 3. Scenario Test Data (Optional Cleanup)
- **Location**: `tests/scenarios/customer_service/` and `tests/scenarios/medical_bot/`
- **Status**: Test data exists but no runners
- **Options**:
  - Option A: Delete these directories if not needed
  - Option B: Implement actual test runners if scenarios are valuable
  - Option C: Leave as-is for future implementation

## Recommended Actions

```bash
# Remove outdated test runner
rm stinger_test_runner.py

# Remove or update the test runners guide
rm docs/TEST_RUNNERS_GUIDE.md  # or update it

# Decision needed on scenario test data
# If removing:
# rm -rf tests/scenarios/customer_service/
# rm -rf tests/scenarios/medical_bot/
```

## What Remains

- `run_test_suites.py` - The working test runner for pytest suites
- All pytest-based tests in organized directories
- Human verification tests in `tests/human/`