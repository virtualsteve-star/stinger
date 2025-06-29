# Phase 5c Execution Plan – Prompt Injection Detection

**Status: ✅ COMPLETED**  
**Start Date**: 2025-06-25  
**Completion Date**: 2025-06-25  

## 🎯 Phase 5c Objective

## Overview
This phase delivers a complete, developer-focused Tech Support Demo application that showcases how to use the Stinger guardrail system to screen prompts and responses with a real LLM (e.g., GPT-4.1-nano). The demo is designed to highlight ease of integration, clear results, and best practices for new users. It will also serve as a primary tool for evaluating the overall design and developer experience of the Stinger system.

## Scenario: Technical Support Agent Bot
The demo will simulate a technical support agent bot. Prompts will represent user queries to tech support (some benign, some problematic), and the bot's responses will be generated and screened. This scenario is realistic, relatable, and demonstrates the value of guardrails in a support context.

## Goals
- Provide a clear, end-to-end example for developers
- Demonstrate screening of both prompts and responses
- Use a realistic scenario and appropriate guardrails
- Make all steps, files, and requirements visible in a dedicated demo folder
- Log and pretty-print all results for maximum clarity
- Serve as a system evaluation and developer experience showcase

## Requirements
- **Demo Folder:** All code, configs, and data for the demo must be in `demos/tech_support/`
- **Prompt File:** Demo loads prompts from a file (e.g., `prompts.txt` or `prompts.jsonl`)
- **Guardrails/Scenario:**
  - Scenario: Technical Support Agent Bot
  - Guardrails: Toxicity detection, PII detection, code generation detection (to block sharing of sensitive info, abusive language, or code snippets)
- **Screening:**
  - Each prompt is screened by the guardrails before being sent to the model
  - Each model response is also screened by the guardrails
- **LLM Integration:** Use the centralized model configuration (GPT-4.1-nano)
- **Logging:**
  - For each prompt/response, log:
    - Prompt text
    - Model response
    - Guardrail results (pass/fail/warn, with reasons) for both prompt and response
    - Flags for any triggers
  - Pretty-print results to the console (table or formatted output)
  - Print a summary at the end (counts of pass/fail/warn)
- **Documentation:**
  - README in the demo folder with setup and usage instructions
  - Comments in code to guide developers

## Proposed Folder Structure
```
demos/
└── tech_support/
    ├── demo.py         # Main demo script
    ├── prompts.txt     # List of prompts (good and bad)
    ├── config.yaml     # Guardrail scenario config (for tech support)
    └── README.md       # Demo instructions
```

## Implementation Steps
1. **Create `demos/tech_support/` directory**
2. **Write `prompts.txt`** with a mix of good and bad tech support prompts
3. **Select scenario and guardrails** (Technical Support Agent Bot with toxicity, PII, and code generation filters)
4. **Write `config.yaml`** for the chosen scenario/guardrails
5. **Implement `demo.py`:**
    - Load prompts from file
    - For each prompt:
        - Screen with guardrails (log results)
        - If passed, send to LLM (GPT-4.1-nano)
        - Screen response with guardrails (log results)
        - Pretty-print/log all results
    - Print summary at end
6. **Write `README.md`** with clear setup and usage instructions
7. **Test the demo end-to-end**
8. **Iterate for clarity and developer experience**

## Success Criteria
- ✅ Demo runs with a single command
- ✅ All results are clearly logged and flagged
- ✅ Prompts and responses are both screened
- ✅ README and code are clear for new developers
- ✅ Demo folder is self-contained and easy to copy/adapt
- ✅ Demo is suitable for system evaluation and developer onboarding

## Timeline
- **Estimated Duration:** 1-2 days
- **Priority:** High (developer onboarding and experience)

## Notes
- Use only open-source or non-sensitive prompts for the demo
- If LLM API keys are required, document setup in README
- Focus on clarity, reproducibility, and best practices 

## Major Deliverables

1. **Refactor Stinger as a Reusable Python Package**
   - Move all core framework code into a top-level `stinger/` package directory.
   - Ensure all modules use absolute imports and proper `__init__.py` files.
   - Add a `pyproject.toml` (or `setup.py`) to make Stinger installable via `pip`.
   - Remove all sys.path hacks and relative import issues.
   - Update documentation to reflect the new structure and installation instructions.
   - **Rationale:** This is essential for Stinger to be adopted as a reusable, extensible framework for safeguarding LLM applications. It aligns with Python best practices and enables easy integration into any project.

2. **Tech Support Demo as System Test & Developer Experience Validation**
   - The demo app will be updated to import Stinger as an installed package, not via sys.path or direct source imports.
   - The demo will serve as a real-world example and a system test to ensure the packaging and API are developer-friendly and robust.
   - Success criteria: The demo runs cleanly after a `pip install .` from the project root, and all guardrails function as expected.

3. **(Other deliverables as previously listed...)**

---

*This packaging milestone is a critical step for Stinger's maturity and adoption as a framework. The Tech Support Demo will be the primary tool for validating this deliverable.* 