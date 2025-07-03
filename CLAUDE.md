# CLAUDE.md - AI Assistant Guidelines for Stinger Project

## BRANCH POLICY REMINDER
Always work against the 'dev' branch for all development, except when explicitly instructed to use 'main'.
This ensures safe, reviewable PRs and keeps main stable.

## CRITICAL BRANCH WORKFLOW RULE
NEVER push directly to main branch. ALWAYS:
1. Work on dev branch
2. Make changes and commit to dev
3. Push to origin/dev
4. Create PR from dev to main
5. Merge via PR, never direct push to main
This rule is non-negotiable for code safety and review process.

## Code Quality & Architecture

### 1. Permission & Communication
- **NEVER** make changes to the repository without explicit instruction or asking first
- Always explain what you're planning to do before making changes
- If unsure about an approach, ask for clarification

### 2. Maintainable Code Principles
- Focus on **architecture re-use** - design components to be extensible
- Write code that's easy to understand, modify, and extend
- Prefer composition over inheritance where appropriate
- Keep functions and classes focused on single responsibilities

### 3. Code Organization
- If files exceed 200-300 lines, refactor into smaller, focused modules
- Break large classes into smaller, cohesive components
- Extract common patterns into reusable utilities
- Maintain clear separation of concerns

### 4. Code Quality Standards
- Write code that **people will actually read and understand**
- Use descriptive variable and function names
- Add meaningful comments for complex logic
- Follow Python best practices and PEP 8 style guidelines
- The codebase should be a pleasure to work with

### 4.1. Pragmatic Linting Strategy
- **Focus on real issues, not style preferences**
- Use `.flake8` config to ignore style-only issues:
  - E203, W503: Black compatibility
  - E712: True/False comparisons (style preference)
  - F541: f-strings without placeholders (minor)
  - E402: Import order in tests (needed for sys.path)
  - W293: Whitespace on blank lines (trivial)
  - E501: Long lines (many valid reasons)
- **Must fix actual bugs and code smells:**
  - F401: Unused imports in src/ (real code smell)
  - F841: Unused variables in src/ (real code smell)
  - E722: Bare except (security risk)
  - F811: Redefinitions (actual bugs)
- **Per-file ignores:**
  - Tests can have unused variables (F841)
  - Complex functions marked as legitimately complex (C901)
- **Benefits:** CI focuses on real issues, developers aren't blocked by pedantic style checks
- **Philosophy:** Pragmatic quality over perfect style

## Testing Philosophy

### 5. Test Quality Over Quantity
- **Tests must actually TEST functionality** - no useless unit tests
- **NEVER fudge test results** to meet deadlines or make anyone happy
- If tests are failing, fix the code, not the tests
- Write tests that catch real bugs and prevent regressions
- Focus on integration tests that verify the system works end-to-end
- Test edge cases and error conditions

### 6. Test-Driven Development
- Write tests first when adding new features
- Ensure tests fail before implementing the feature
- Make the code pass the hard tests, not the easy ones
- Maintain high test coverage for critical paths

## Development Workflow

### 7. Incremental Development
- Build features incrementally with working code at each step
- Commit frequently with meaningful commit messages
- Test thoroughly before pushing changes
- Keep the main branch stable and working

### 8. Documentation
- Keep README and documentation up to date
- Document complex algorithms and design decisions
- Include examples and usage patterns
- Make the project accessible to new contributors

## Project-Specific Guidelines

### 9. Filter Development
- All filters must inherit from BaseGuardrail
- Implement proper error handling and graceful degradation
- Add comprehensive test cases for each filter
- Document filter configuration options

### 10. Configuration Management
- Validate configuration files thoroughly
- Provide clear error messages for invalid configs
- Support backward compatibility when possible
- Document all configuration options

### 11. Issue Management
- Use GitHub CLI (`gh issue create`, `gh issue list`, etc.) to manage issues directly from terminal
- Avoid copy/paste by using `--body-file` flag for issue content
- Example: `gh issue create --title "Title" --body-file issue.md`

## AI Model Configuration
**IMPORTANT**: Always use "gpt-4.1-nano" as the base model for AI filters, NOT "gpt-4o-mini"
This has been discussed and agreed upon - gpt-4.1-nano is the correct model name
Use this consistently across all AI-based filters and adapters

## GitHub Repository
Always use 'virtualsteve-star/stinger' as the GitHub repo for CLI and issue-related actions

## Date Handling
ALWAYS use the real current date when documenting completion dates, timestamps, or any time-related information
Run 'date' command to get the current date/time before writing dates in documentation
Never assume or guess dates - always verify with the system date

## Process Testing Rules
- **NEVER use `command &` with Bash tool** - causes hanging when trying to capture output
- **For long-running services:** test endpoints directly, don't background processes
- **If testing startup:** use wrapper scripts that exit quickly or test specific functionality
- **Examples:**
  - ❌ `python3 server.py &` (will hang)
  - ✅ `curl http://localhost:8000/health` (test endpoint)
  - ✅ Start process, let user interrupt, then verify it worked

## API Key Environment Variable Handling (Stinger)
- API keys (e.g., OPENAI_API_KEY) should be set as environment variables, preferably using macOS Keychain for devs using Cursor or similar tools.
- The recommended workflow is:
    1. Store the key in Keychain: security add-generic-password -a "$USER" -s openai-api-key -w 'sk-...'
    2. Expose it as an environment variable: launchctl setenv OPENAI_API_KEY $(security find-generic-password -w -s openai-api-key)
- The Stinger centralized API key manager will automatically pick up the key from the environment.
- All filters and services must use the centralized manager for key access (never read keys directly from config or os.environ).
- See docs/API_KEY_HANDLING.md for full details.

## Pre-PR Checklist
**IMPORTANT**: Before creating any PR, you MUST run local CI checks to avoid CI failures.

### Quick Check (Required)
```bash
# Run this single command before every PR:
./scripts/local-ci-check.sh
```

### Manual Steps (if script unavailable)
1. **Format code**: `black src/ tests/`
2. **Fix imports**: `isort src/ tests/`
3. **Check style**: `flake8 src/ tests/`
4. **Run tests**: `pytest`
5. **Check Python 3.8**: `python3.8 -m py_compile src/stinger/core/*.py`

### Pre-commit Hooks (Recommended)
```bash
# One-time setup
pip install pre-commit
pre-commit install

# Now hooks run automatically on git commit
```

## Code Review Checklist
Before submitting any changes:
- [ ] Ran `./scripts/local-ci-check.sh` - ALL CHECKS PASSED
- [ ] Code follows project architecture patterns
- [ ] Tests are meaningful and pass
- [ ] Documentation is updated
- [ ] Error handling is implemented
- [ ] Code is readable and maintainable
- [ ] No unnecessary complexity added

## Remember
**Quality over speed. Architecture over quick fixes. Tests that actually test.**
**No CI surprises - check locally first!**

## Common Development Commands

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_simple_pii_detection_guardrail.py -v

# Run specific test
pytest tests/test_integration.py::test_pipeline_with_all_guardrails -v

# Run with coverage
pytest tests/ -v --cov=src/stinger --cov-report=html

# Run only fast tests (skip slow/integration tests)
pytest tests/ -v -m "not slow"
```

### Building and Publishing
```bash
# Build distribution packages
python3 -m build

# Check package quality
python3 -m twine check dist/*

# Install in development mode
pip install -e .

# Install with all dependencies
pip install -e ".[all]"
```

### Code Quality
```bash
# Format code
black src/ tests/ --line-length=100

# Sort imports
isort src/ tests/

# Type checking
mypy src/stinger --ignore-missing-imports

# Lint
flake8 src/ tests/ --max-line-length=100 --extend-ignore=E203,W503
```

### Running Demos
```bash
# CLI demo
stinger demo

# Web demo
cd demos/web_demo && python3 start_demo.py

# Conversation demo
python3 demos/conversation_demo.py
```

## High-Level Architecture

### Core Pipeline Architecture
The framework centers around the `GuardrailPipeline` which orchestrates guardrails:

```
User Input → Input Pipeline → LLM → Output Pipeline → Response
                ↓                         ↓
            Audit Trail              Audit Trail
```

### Key Components

1. **GuardrailInterface** (`src/stinger/core/guardrail_interface.py`)
   - Base interface all guardrails implement
   - Defines `analyze()` method returning `GuardrailResult`
   - Supports both sync and async operations

2. **GuardrailPipeline** (`src/stinger/core/pipeline.py`)
   - Orchestrates multiple guardrails in sequence
   - Separate input and output pipelines
   - Handles configuration loading and guardrail initialization
   - Integrates with conversation tracking and audit logging

3. **Configuration System**
   - YAML-based configuration with schema validation
   - Preset system for common use cases (customer_service, medical, etc.)
   - Runtime configuration updates supported
   - Located in `src/stinger/core/config.py` and `preset_configs.py`

4. **Guardrail Types**
   - **Simple/Regex-based**: PII detection, toxicity, code generation
   - **AI-powered**: Uses OpenAI for advanced detection
   - **Stateful**: Conversation-aware prompt injection
   - All located in `src/stinger/guardrails/`

5. **Conversation Management** (`src/stinger/core/conversation.py`)
   - Tracks multi-turn conversations
   - Provides context to guardrails
   - Integrates with rate limiting

6. **Audit System** (`src/stinger/core/audit.py`)
   - Zero-config audit trail
   - Logs all security decisions
   - PII redaction capabilities
   - Async buffering for performance

### Web Demo Architecture
The web demo (`demos/web_demo/`) showcases the framework:
- **Backend**: FastAPI server integrating GuardrailPipeline
- **Frontend**: React app demonstrating real-time guardrail feedback
- **Serves as**: Integration example and testing ground

### Extension Points
1. Create new guardrails by implementing `GuardrailInterface`
2. Add guardrail types in `GuardrailType` enum
3. Register factory functions in `guardrail_factory.py`
4. Create presets in `preset_configs.py`