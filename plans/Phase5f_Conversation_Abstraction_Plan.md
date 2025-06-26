# Phase 5f Execution and Test Plan – Conversation Abstraction

## Objective
Add an **optional Conversation abstraction** to Stinger, enabling multi-turn context, improved logging, and future multi-turn guardrails—without complicating simple demos or requiring conversation for filtering.

## Key Deliverables
- `Conversation` class: Holds unique ID, ordered turns (prompts/responses), metadata.
- **Support for per-conversation rate limiting:** Ability to set a rate limit on a conversation; conversation can block or warn when the limit is exceeded.
- Optional integration with `GuardrailPipeline` and guardrails (accept `conversation` parameter).
- Updated logging to include conversation ID when available.
- **Conversation is a central, useful construct for logging and traceability, supporting ultimate logging goals.**
- Documentation and usage examples.
- Comprehensive unit and integration tests.
- **A demo script showcasing the conversation construct, including multi-turn, rate limiting, and logging.**

## Implementation Steps

1. **Design Conversation Class**
   - Pythonic dataclass or class with:
     - Unique conversation ID (UUID or user-supplied)
     - Ordered list of turns (prompt/response pairs, with timestamps/metadata)
     - Methods to add/retrieve turns, get history, etc.
     - Optional metadata (user, session, etc.)
     - **Support for per-conversation rate limiting:**
       - Configurable rate limit (e.g., max turns per minute/hour)
       - Methods to check and enforce rate limits (block or warn when exceeded)

2. **Integrate with GuardrailPipeline (Optionally)**
   - Update `check_input` and `check_output` to accept an optional `conversation: Conversation = None` parameter.
   - Pass conversation to guardrails if provided.
   - Ensure all guardrails can ignore or use conversation as needed.
   - **Do not require conversation for filtering**—all existing single-turn code and demos must work unchanged.

3. **Update Logging/Tracing**
   - Include conversation ID in logs/events if available.
   - **Ensure the conversation abstraction is a central, useful construct for logging and traceability.**
   - All logs/events related to prompts, responses, and guardrail checks should reference the conversation when present.
   - Enable easy reconstruction of conversation flows from logs for auditing, debugging, and analytics.

4. **Documentation**
   - Add docstrings and usage examples for Conversation.
   - Update API docs to show optional conversation parameter.
   - Add a short example of multi-turn usage (in docs, not in simple demos).
   - Document per-conversation rate limiting and logging features.

5. **Backward Compatibility**
   - Ensure all existing demos, tests, and single-turn usage work without modification.
   - Conversation support is 100% optional and pythonic (default is None).

6. **Demo Script**
   - Create a new demo (e.g., `demos/conversation_demo.py`) that:
     - Demonstrates creating a conversation, adding multiple turns, and associating prompts/responses.
     - Shows rate limiting in action (block/warn when exceeded).
     - Prints/logs conversation ID and history.
     - Optionally, demonstrates multi-turn guardrail logic (if implemented).
   - Ensure the demo is clear, well-documented, and easy to run.

## Test Plan

- **Unit Tests**
  - Conversation class: creation, adding turns, retrieving history, metadata.
  - Edge cases: empty conversation, duplicate IDs, metadata handling.
  - **Per-conversation rate limiting:**
    - Set rate limit, add turns, verify block/warn when exceeded.
    - Reset/adjust rate limit and verify behavior.

- **Integration Tests**
  - GuardrailPipeline: filtering with and without conversation.
  - Multi-turn: add several turns, ensure order/history is correct.
  - Guardrails: verify they can access conversation if provided, ignore if not.
  - **Rate limiting in pipeline:**
    - Pass conversation with rate limit, verify pipeline respects block/warn when limit exceeded.

- **Regression Tests**
  - All existing single-turn tests and demos must pass unchanged.

- **Logging Tests**
  - Logs include conversation ID when provided.
  - **Logs and events can be grouped and reconstructed by conversation.**
  - No errors if conversation is None.

- **Documentation Tests**
  - Example code for both single-turn and conversation-aware usage.
  - Example for per-conversation rate limiting and logging.

- **Demo Scenario**
  - Run the conversation demo script:
    - Verify multi-turn flow, rate limiting, and logging.
    - Confirm output is clear and conversation features are demonstrated.
    - Ensure demo is easy to run and understand for new users.

## Exit Criteria
- All tests (unit, integration, regression) pass.
- Simple demos and single-turn usage are unchanged.
- Conversation support is optional, pythonic, and well-documented.
- **Per-conversation rate limiting is implemented and tested.**
- **Conversation is a central, useful construct for logging and traceability.**
- **Demo script clearly demonstrates conversation features.**
- Logging and traceability improved.
- Docs/examples updated.

## Risks & Mitigations
- **Backward compatibility:** Strictly optional parameter, default None.
- **API clarity:** Use type hints, docstrings, and clear docs.
- **Performance:** Minimal impact if conversation is not used.

## Timeline
1. Design Conversation class and API (1 day)
2. Implement and integrate with pipeline/guardrails (1–2 days)
3. Update logging and docs (1 day)
4. Write and run tests (1 day)
5. Create and validate demo script (0.5 day)
6. Review and finalize (0.5 day)

---

This plan ensures Stinger gains powerful, optional conversation support for multi-turn context, per-conversation rate limiting, robust logging/traceability, and a clear demo—without complicating simple use cases or breaking backward compatibility. 