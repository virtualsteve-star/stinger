# Phase 5c Configuration Reorganization Plan

**Status: ✅ COMPLETED**  
**Start Date**: 2025-06-25  
**Completion Date**: 2025-06-25  

## Overview
Reorganize configuration files to follow Python best practices by co-locating configs with their related source code, improving maintainability and discoverability.

## Problem Statement
Current `/configs` directory mixes production settings, test configurations, example templates, and use case configs, making it difficult to:
- Map source files to their configurations
- Understand which configs are for what purpose
- Maintain and refactor configurations
- Avoid using test configs in production

## Goals
1. **Improve Discoverability**: Make it easy to find which config goes with which code
2. **Separate Concerns**: Clearly distinguish production, test, and example configs
3. **Follow Python Best Practices**: Co-locate configs with related source code
4. **Preserve Functionality**: Ensure all tests pass after reorganization
5. **Maintain Backward Compatibility**: Update all references to config files

## Proposed Structure

### Before (Current)
```
configs/
├── models.yaml                    # Production model settings
├── ai_code_generation.yaml        # Example config
├── simple_code_generation.yaml    # Example config
├── ai_toxicity_detection.yaml     # Example config
├── simple_toxicity_detection.yaml # Example config
├── ai_pii_detection.yaml          # Example config
├── simple_pii_detection.yaml      # Example config
├── openai_comprehensive.yaml      # Use case config
├── medical_bot.yaml               # Use case config
├── medical_bot_simple.yaml        # Use case config
├── customer_service.yaml          # Use case config
├── customer_service_simple.yaml   # Use case config
├── comprehensive_filters.yaml     # Example config
├── comprehensive.yaml             # Test config
├── minimal.yaml                   # Test config
├── customer_service_invalid.yaml  # Test config
└── keyword_lists/                 # Production data
    ├── pii.txt
    ├── medical_terms.txt
    ├── spam_indicators.txt
    ├── harassment.txt
    ├── profanity.txt
    └── toxic_language.txt
```

### After (Proposed)
```
src/
├── core/
│   ├── model_config.py
│   └── configs/
│       └── models.yaml            # Production model settings
├── filters/
│   ├── ai_pii_detection_filter.py
│   ├── ai_toxicity_detection_filter.py
│   ├── ai_code_generation_filter.py
│   ├── simple_pii_detection_filter.py
│   ├── simple_toxicity_detection_filter.py
│   ├── simple_code_generation_filter.py
│   └── configs/                   # Filter example configs
│       ├── ai_pii_detection.yaml
│       ├── ai_toxicity_detection.yaml
│       ├── ai_code_generation.yaml
│       ├── simple_pii_detection.yaml
│       ├── simple_toxicity_detection.yaml
│       └── simple_code_generation.yaml
├── scenarios/
│   ├── customer_service/
│   │   ├── customer_service.py
│   │   └── config.yaml            # Use case config
│   └── medical_bot/
│       ├── medical_bot.py
│       └── config.yaml            # Use case config
└── data/                          # Production data
    └── keyword_lists/
        ├── pii.txt
        ├── medical_terms.txt
        ├── spam_indicators.txt
        ├── harassment.txt
        ├── profanity.txt
        └── toxic_language.txt

tests/
└── configs/                       # Test-specific configs
    ├── minimal.yaml
    ├── comprehensive.yaml
    ├── customer_service_invalid.yaml
    └── comprehensive_filters.yaml

examples/                          # Example configurations
├── openai_comprehensive.yaml
├── medical_bot_simple.yaml
├── customer_service_simple.yaml
└── pii_detection.yaml

configs/                           # Legacy - will be removed after migration
└── (empty or removed)
```

## Implementation Steps

### Step 1: Create New Directory Structure
- [ ] Create `src/core/configs/` directory
- [ ] Create `src/filters/configs/` directory
- [ ] Create `src/scenarios/customer_service/` directory
- [ ] Create `src/scenarios/medical_bot/` directory
- [ ] Create `src/data/keyword_lists/` directory
- [ ] Create `tests/configs/` directory
- [ ] Create `examples/` directory

### Step 2: Move Production Configs
- [ ] Move `configs/models.yaml` → `src/core/configs/models.yaml`
- [ ] Move `configs/keyword_lists/` → `src/data/keyword_lists/`

### Step 3: Move Filter Example Configs
- [ ] Move `configs/ai_pii_detection.yaml` → `src/filters/configs/ai_pii_detection.yaml`
- [ ] Move `configs/ai_toxicity_detection.yaml` → `src/filters/configs/ai_toxicity_detection.yaml`
- [ ] Move `configs/ai_code_generation.yaml` → `src/filters/configs/ai_code_generation.yaml`
- [ ] Move `configs/simple_pii_detection.yaml` → `src/filters/configs/simple_pii_detection.yaml`
- [ ] Move `configs/simple_toxicity_detection.yaml` → `src/filters/configs/simple_toxicity_detection.yaml`
- [ ] Move `configs/simple_code_generation.yaml` → `src/filters/configs/simple_code_generation.yaml`

### Step 4: Move Use Case Configs
- [ ] Move `configs/customer_service.yaml` → `src/scenarios/customer_service/config.yaml`
- [ ] Move `configs/medical_bot.yaml` → `src/scenarios/medical_bot/config.yaml`

### Step 5: Move Test Configs
- [ ] Move `configs/minimal.yaml` → `tests/configs/minimal.yaml`
- [ ] Move `configs/comprehensive.yaml` → `tests/configs/comprehensive.yaml`
- [ ] Move `configs/customer_service_invalid.yaml` → `tests/configs/customer_service_invalid.yaml`
- [ ] Move `configs/comprehensive_filters.yaml` → `tests/configs/comprehensive_filters.yaml`

### Step 6: Move Example Configs
- [ ] Move `configs/openai_comprehensive.yaml` → `examples/openai_comprehensive.yaml`
- [ ] Move `configs/medical_bot_simple.yaml` → `examples/medical_bot_simple.yaml`
- [ ] Move `configs/customer_service_simple.yaml` → `examples/customer_service_simple.yaml`
- [ ] Move `configs/pii_detection.yaml` → `examples/pii_detection.yaml`

### Step 7: Update Source Code References
- [ ] Update `src/core/model_config.py` to use new path
- [ ] Update all test files to use new config paths
- [ ] Update documentation references
- [ ] Update any hardcoded config paths in source code

### Step 8: Update Documentation
- [ ] Update README.md with new config structure
- [ ] Update test documentation
- [ ] Update any other documentation files

### Step 9: Validation
- [ ] Run all tests to ensure functionality is preserved
- [ ] Verify all configs are properly loaded
- [ ] Check that no hardcoded paths remain

### Step 10: Cleanup
- [ ] Remove old `configs/` directory
- [ ] Update .gitignore if needed
- [ ] Remove any references to old paths

## Success Criteria
1. ✅ All tests pass after reorganization
2. ✅ Configs are co-located with related source code
3. ✅ Clear separation between production, test, and example configs
4. ✅ No hardcoded paths to old config locations
5. ✅ Documentation is updated and accurate
6. ✅ Backward compatibility is maintained

## Risk Mitigation
- **Risk**: Tests fail after moving configs
  - **Mitigation**: Update all references before removing old configs
- **Risk**: Hardcoded paths break functionality
  - **Mitigation**: Search and replace all config references systematically
- **Risk**: Documentation becomes outdated
  - **Mitigation**: Update documentation as part of the reorganization

## Timeline
- **Estimated Duration**: 2-3 hours
- **Dependencies**: None (can be done independently)
- **Priority**: Medium (improves maintainability but not critical functionality) 