# Super Demo Test Plan

## Overview
This test plan describes how to validate the Super Demo end-to-end, with a focus on minimizing manual browser debugging and copy-paste. The plan covers both backend and frontend, guardrail enforcement, and user experience.

---

## Security

- **Test HTTPS Communication:**
  - Verify the backend (FastAPI) serves over HTTPS using the self-signed certificate.
  - Verify the frontend (React) connects to the backend via `https://localhost:PORT`.
  - Confirm that all API requests and responses are encrypted (inspect browser network tab for HTTPS).
- **Test Self-Signed Certificate Setup:**
  - Follow the setup instructions from the implementation plan to generate and use a self-signed certificate.
  - Confirm the browser prompts to accept the self-signed certificate and that, once accepted, the app works as expected.
- **Test CORS Restrictions:**
  - Verify that CORS headers only allow requests from the local frontend origin.
  - Attempt to connect from a non-allowed origin and confirm the request is blocked (receives CORS error).

---

## 1. Test Strategy

### 1.1 Automated Testing
- **Backend:**
  - Use pytest to test all FastAPI endpoints (`/chat`, `/settings`, `/guardrails`)
  - Mock OpenAI API for deterministic results
  - Unit and integration tests for Stinger guardrail logic
- **Frontend:**
  - Use **Playwright** (recommended) for browser automation
  - Simulate user interactions: send messages, toggle guardrails, select bots
  - Validate UI for blocked messages and reason display
  - Test settings pane and guardrail toggling

### 1.2 Manual Testing
- Minimal manual browser debugging required
- Manual exploratory testing for UI/UX polish and edge cases

---

## 2. Guardrails to Test

### Input Filters
- Input Length (local)
- Rate Limit (local)
- PII (local)
- Profanity (local)
- Prompt Injection (local)
- Prompt Injection (conversation-aware, multi-turn)
- Toxicity (AI)
- Prompt Injection (AI)

### Output Filters
- PII (local)
- Profanity (local)
- Code Generation (local)
- Toxicity (AI)
- Prompt Injection (AI)

---

## 3. UI/UX Validation
- **Reference screenshot for layout and style**
- Test chat area, settings pane, bot selector, and message bubbles
- Ensure blocked messages show reason clearly
- Responsive design: test on desktop and mobile

---

## 4. Out of Scope
- Dockerization
- Paid web testing tools
- Multi-user testing

---

## 5. Test Cases

### 5.1 Backend
- [ ] **Input Guardrail Block:**
  - Send message with PII, toxicity, prompt injection, code, etc.
  - Verify backend blocks and returns correct reason
- [ ] **Output Guardrail Block:**
  - LLM returns blocked content, verify output guardrail blocks and returns reason
- [ ] **Allow Case:**
  - Normal message passes through all guardrails
- [ ] **Settings Endpoint:**
  - Toggle guardrails, verify backend respects changes
- [ ] **Guardrail Enable/Disable Testing:**
  - **Individual Toggle Testing:**
    - Test enabling/disabling each guardrail individually via API
    - Verify `enable_guardrail()` and `disable_guardrail()` methods work correctly
    - Confirm guardrail state persists across API calls
  - **Combination Testing:**
    - Test enabling/disabling multiple guardrails simultaneously
    - Verify all guardrails work independently without interference
    - Test edge case: enable all, then disable all, then enable some
  - **Input/Output Duplicate Testing:**
    - Test guardrails that appear in both input and output (e.g., "pii_check")
    - Verify disabling input "pii_check" doesn't affect output "pii_check"
    - Verify enabling output "pii_check" doesn't affect input "pii_check"
    - Confirm `get_guardrail_status()` correctly reports separate states
  - **Count Accuracy Testing:**
    - Verify `/api/health` returns "0/4" when all guardrails are disabled
    - Verify `/api/health` returns "4/4" when all guardrails are enabled
    - Test partial states and verify count matches actual enabled state
    - Verify count updates immediately after each API call
  - **State Persistence Testing:**
    - Test guardrail settings persist after backend restart
    - Verify saved settings are applied on startup from saved file
    - Test switching between presets and verify guardrail states are correctly applied
  - **API Endpoint Testing:**
    - Test `/api/guardrails` POST with various combinations
    - Verify `/api/guardrails` GET returns correct current state
    - Test error handling for invalid guardrail names
- [ ] **Error Handling:**
  - Simulate OpenAI/network errors, verify user-friendly error returned

### 5.2 Frontend
- [ ] **Chat Flow:**
  - User sends/receives messages, UI updates correctly
- [ ] **Settings Pane:**
  - User toggles guardrails, UI updates, backend reflects changes
- [ ] **Guardrail Enable/Disable Testing:**
  - **Individual Toggle Testing:**
    - Toggle each guardrail individually on/off
    - Verify the toggle state persists after page refresh
    - Confirm the enabled count updates correctly (e.g., "3/5 active")
  - **Combination Testing:**
    - Test enabling/disabling multiple guardrails simultaneously
    - Verify all toggles work independently without interference
    - Test edge case: enable all, then disable all, then enable some
  - **Input/Output Duplicate Testing:**
    - Test guardrails that appear in both input and output (e.g., "pii_check")
    - Verify disabling input "pii_check" doesn't affect output "pii_check"
    - Verify enabling output "pii_check" doesn't affect input "pii_check"
    - Confirm count accuracy when same guardrail type is in both pipelines
  - **Count Accuracy Testing:**
    - Verify "0/4 active" when all guardrails are disabled
    - Verify "4/4 active" when all guardrails are enabled
    - Test partial states (e.g., "2/4 active") and verify count matches actual enabled state
    - Verify count updates immediately after each toggle action
  - **State Persistence Testing:**
    - Toggle guardrails, refresh page, verify settings are restored
    - Restart backend, verify saved settings are applied on startup
    - Test switching between presets and verify guardrail states are correctly applied
- [ ] **Blocked Message UI:**
  - Blocked messages show reason, visually distinct
- [ ] **Responsive Design:**
  - Test on desktop and mobile
- [ ] **Error Handling:**
  - Network/API errors show clear, actionable messages

### 5.3 End-to-End
- [ ] **Scenario Tests:**
  - Run canned conversations that trigger each guardrail
  - Verify correct block/allow behavior and UI feedback

---

## 6. Test Data
- Provide a set of test messages for each guardrail (PII, toxicity, code, etc.)
- Include both block and allow cases

---

## 7. Pain Minimization
- All block reasons and errors are shown in the UI (no browser console needed)
- Automated browser tests for all major flows

---

## 8. Manual Test Script (if needed)
1. Start backend and frontend locally
2. Open browser, load chat UI
3. Send test messages, toggle guardrails, verify UI/UX
4. Check backend logs for errors

---

## 9. Stretch Goals
- Full Playwright/Selenium test suite for CI
- Automated accessibility and mobile/responsive checks 