# Tech Support Demo

This demo showcases the developer experience and effectiveness of Stinger's guardrail system for a Tech Support LLM agent.

## Purpose
- **Evaluate developer experience**: Demonstrates how easy it is to integrate and configure guardrails for a real-world use case.
- **Showcase guardrail effectiveness**: Screens both prompts and LLM responses for toxicity, PII, and code generation risks.
- **System evaluation**: Provides pretty-printed results and a summary for rapid assessment.

## How It Works
- Loads a set of tech support prompts (good and bad) from `prompts.txt`.
- Screens each prompt using the configured guardrails (toxicity, PII, code generation).
- If a prompt passes, it is sent to the LLM (OpenAI, or a mock if no API key is set).
- The LLM response is also screened by the same guardrails.
- Results are printed in a readable format, with a summary at the end.

## Setup
1. **Install dependencies** (from the project root):
   ```bash
   pip install -r requirements.txt
   ```
2. **Set your OpenAI API key** (optional, for real LLM responses):
   ```bash
   export OPENAI_API_KEY=sk-...
   ```
   If not set, the demo will use mock LLM responses.

## Running the Demo
From the project root:
```bash
python demos/tech_support/demo.py
```

## Files
- `demo.py` — Main demo script
- `prompts.txt` — Example tech support prompts (good and bad)
- `config.yaml` — Guardrail scenario configuration

## Interpreting Results
- Each prompt and response is shown with its guardrail status:
  - `PASS`: No issues detected
  - `FAIL`: Blocked by guardrails (with reasons)
  - `WARN`: Warning (not blocking, but flagged)
- The summary shows the total number of passes, warnings, and failures.

## Customization
- Add or modify prompts in `prompts.txt`.
- Adjust guardrail configuration in `config.yaml` to test different scenarios.

---
This demo is part of Stinger Phase 5c and is intended for system evaluation and developer experience review. 