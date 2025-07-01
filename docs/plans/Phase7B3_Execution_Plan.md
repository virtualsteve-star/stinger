# Phase 7B.3: Consolidate AI Guardrail Implementations & Clean Architecture

## Execution Plan

This phase has three major parts that must be executed in order:

### Part 1: Language Consistency - Filter → Guardrail
**Goal**: Eliminate confusion by using "guardrail" consistently throughout the codebase.

**Execution Order**:
1. Rename directory: `src/stinger/guardrails/` → `src/stinger/guardrails/`
2. Rename all filter files: `*_filter.py` → `*_guardrail.py`
3. Update all class names: `*Filter` → `*Guardrail`
4. Update all imports across the codebase
5. Update test files and their imports
6. Update configuration keys and factory patterns
7. Run tests to ensure nothing broke

**Complexity**: High - touches nearly every file in the codebase

### Part 2: Clean Model Provider Architecture
**Goal**: Simplify the OpenAI adapter to be just a thin model communication layer.

**Execution Order**:
1. Extract prompt injection logic from OpenAI adapter
2. Extract content moderation logic from OpenAI adapter
3. Create new `PromptInjectionGuardrail` with extracted logic
4. Create new `ContentModerationGuardrail` with extracted logic
5. Simplify OpenAI adapter to just model calls
6. Consolidate ModelProvider and OpenAIAdapter into single clean interface
7. Update all references to use new architecture

**Complexity**: Medium - focused refactoring of adapter layer

### Part 3: Create BaseAIGuardrail
**Goal**: Eliminate ~400 lines of duplicate code across AI guardrails.

**Execution Order**:
1. Create `BaseAIGuardrail` class (building on the BaseAIGuardrail we started)
2. Migrate `AIPIIDetectionGuardrail` to use base class
3. Migrate `AIToxicityDetectionGuardrail` to use base class
4. Migrate `AICodeGenerationGuardrail` to use base class
5. Implement new `PromptInjectionGuardrail` using base class
6. Implement new `ContentModerationGuardrail` using base class
7. Test all AI guardrails

**Complexity**: Medium - consolidation pattern is clear

## Risk Mitigation

1. **Create backup before starting**: `git stash` or new branch
2. **Run tests after each major step** to catch breaks early
3. **Use automated scripts** for mass renaming to avoid human error
4. **Update imports systematically** using grep/sed patterns

## Current Status

- Directory rename: COMPLETED ✓
- Next step: Create comprehensive renaming script

## Files Affected (Estimate)

- ~20 guardrail implementation files
- ~30 test files
- ~10 configuration files
- ~50 import statements across codebase
- All documentation mentioning "filter"

## Success Metrics

1. Zero occurrences of "filter" in guardrail context
2. All 441 tests passing
3. ~400 lines of code removed from AI guardrails
4. OpenAI adapter < 100 lines
5. Clean separation of concerns