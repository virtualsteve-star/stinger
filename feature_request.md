## Feature Request: Guardrail for Image Content Security in LLM Output

**Summary:**
Add a guardrail that scans LLM output for markdown or HTML image tags and blocks, warns, or sanitizes any that are not from a configurable list of trusted domains. This helps prevent data exfiltration via image links when rendering LLM output as markdown.

**Acceptance Criteria:**
- Detects markdown (![]()) and HTML (<img>) image tags in LLM output.
- Blocks, warns, or sanitizes output if untrusted/external image sources are detected.
- Trusted domains are configurable.
- Optionally, provides a summary or log of blocked/sanitized content.

// Add comments for more detail or specific use cases as needed. 