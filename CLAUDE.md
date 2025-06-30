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
- All filters must inherit from BaseFilter
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

## Code Review Checklist
Before submitting any changes:
- [ ] Code follows project architecture patterns
- [ ] Tests are meaningful and pass
- [ ] Documentation is updated
- [ ] Error handling is implemented
- [ ] Code is readable and maintainable
- [ ] No unnecessary complexity added

## Remember
**Quality over speed. Architecture over quick fixes. Tests that actually test.**