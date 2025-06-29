# Stinger Core API Critical Fix Implementation Plan

**Date:** June 29, 2025  
**Author:** AI Assistant  
**Scope:** Addressing critical reliability and developer experience issues in the Stinger core API, as identified in the code review.

---

## Table of Contents
1. [Overview](#overview)
2. [Critical Items & Rationale](#critical-items--rationale)
3. [Implementation Steps](#implementation-steps)
    - [1. Eliminate Global State](#1-eliminate-global-state)
    - [2. Thread-Safe Conversation State](#2-thread-safe-conversation-state)
    - [3. Guardrail Enable/Disable Logic](#3-guardrail-enabledisable-logic)
    - [4. Async/Sync Boundary Fixes](#4-asyncsync-boundary-fixes)
    - [5. Error Handling Standardization](#5-error-handling-standardization)
4. [Testing Plan](#testing-plan)
5. [Completion Criteria](#completion-criteria)

---

## Overview

This plan addresses the most urgent reliability and developer experience issues in the Stinger core API. The goal is to:
- Eliminate global state and race conditions
- Make conversation and pipeline state thread-safe
- Fix guardrail enable/disable logic for input/output separation
- Correct async/sync code boundaries
- Standardize error handling

---

## Critical Items & Rationale

### 1. Eliminate Global State
- **Rationale:** Global variables (`current_pipeline`, etc.) cause race conditions, unpredictable state, and break multi-user support.
- **Goal:** All shared state must be managed via dependency injection or `app.state` only, with clear ownership.

### 2. Thread-Safe Conversation State
- **Rationale:** Conversation state is mutated without locking, leading to race conditions and backend crashes.
- **Goal:** All conversation state changes must be atomic and thread-safe.

### 3. Guardrail Enable/Disable Logic
- **Rationale:** Guardrails with the same name in input/output pipelines are not distinguished, causing toggling bugs and UI confusion.
- **Goal:** Enable/disable operations must be scoped to input/output and unique per instance.

### 4. Async/Sync Boundary Fixes
- **Rationale:** Use of `asyncio.run()` inside async code is an anti-pattern and can break the event loop.
- **Goal:** All async code must use `await` and never block the event loop.

### 5. Error Handling Standardization
- **Rationale:** Inconsistent error handling (exceptions vs. None returns) makes debugging and recovery difficult.
- **Goal:** All errors must be handled in a standardized, predictable way.

---

## Implementation Steps

### 1. Eliminate Global State
**a. Remove all global variables for pipeline, conversation, etc.**
- Refactor backend (e.g., `main.py`) to use only `app.state` for shared objects.
- Ensure all state is initialized in FastAPI lifespan events or dependency-injected.
- Remove any fallback or legacy global state access.

**b. Refactor all accessors to use dependency injection or `app.state`.**
- Update all endpoints and helper functions to use `Depends(get_pipeline)` or similar.
- Add clear documentation for state ownership.

**c. Add locking for shared state if needed.**
- Use `threading.Lock` or `asyncio.Lock` for any mutable shared state.

---

### 2. Thread-Safe Conversation State
**a. Add a lock to the Conversation class.**
- Add a `self._lock = threading.Lock()` (or `asyncio.Lock` if async context) to the Conversation class.

**b. Wrap all state-mutating methods with the lock.**
- Methods: `add_prompt`, `add_response`, `add_turn`, `add_exchange`, etc.
- Use `with self._lock:` or `async with self._lock:` as appropriate.

**c. Audit all direct attribute mutations and refactor to use safe methods.**
- Ensure no code mutates `self.turns` or other state directly outside of locked methods.

---

### 3. Guardrail Enable/Disable Logic
**a. Refactor pipeline to distinguish input/output guardrails.**
- Change `enable_guardrail` and `disable_guardrail` to accept both `name` and `pipeline_type` (`input` or `output`).
- Update all callers to specify which pipeline to operate on.

**b. Enforce unique names within each pipeline.**
- Add validation to config loading to ensure no duplicate names within input or output.

**c. Update status and UI logic to reflect input/output separation.**
- Update `/api/health` and related endpoints to report counts per pipeline and overall.

---

### 4. Async/Sync Boundary Fixes
**a. Refactor `_run_pipeline` to be async.**
- Change `_run_pipeline` to `async def` and use `await guardrail.analyze(content)`.
- Update all callers to use `await`.

**b. Remove all uses of `asyncio.run()` in async code.**
- Replace with `await` or refactor to sync context if needed.

**c. Audit all filter and guardrail code for async/sync mismatches.**
- Ensure all async methods are awaited.

---

### 5. Error Handling Standardization
**a. Define a standard error handling policy.**
- All errors should raise a custom exception or return a standardized error object.
- No silent failures (e.g., returning `None` on error).

**b. Refactor all factory and pipeline methods to follow the policy.**
- Update factories to raise or return error objects, not `None`.
- Update pipeline to catch and log errors, then propagate in a standard way.

**c. Add error logging and audit trail for all critical failures.**
- Ensure all errors are logged with context.

---

## Testing Plan

1. **Unit Tests**
    - Add/expand tests for all state management, guardrail toggling, and async code.
    - Test thread safety by simulating concurrent requests.
    - Test error handling by injecting failures and verifying responses.

2. **Integration Tests**
    - Test full chat flow with multiple users and rapid toggling of guardrails.
    - Test UI/health endpoint for correct counts and state after toggling.
    - Test for race conditions by running parallel requests.

3. **Regression Tests**
    - Ensure all previous tests pass.
    - Add tests for previously reported bugs (e.g., "1/4" enabled bug, conversation crashes).

4. **Manual QA**
    - Use the Super Demo UI to toggle guardrails, send/receive messages, and verify correct state and counts.
    - Check logs for errors, race conditions, and audit trail completeness.

---

## Completion Criteria
- No global state remains; all shared state is managed via dependency injection or `app.state`.
- Conversation state is thread-safe and race-condition free.
- Guardrail enable/disable logic is correct for input/output and UI always matches backend.
- No use of `asyncio.run()` in async code; all async code is properly awaited.
- All errors are handled in a standardized, logged, and auditable way.
- All tests (unit, integration, regression) pass.
- Manual QA confirms stability and correct behavior in the Super Demo.

---

**End of Plan** 