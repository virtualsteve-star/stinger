# CI/CD Tips from Stinger Core Team

Congratulations on setting up your CI/CD pipeline! Here are some tips from our experience to help maintain consistency and avoid common pitfalls.

## 1. Linting and Formatting Synchronization

**Our Pain Point**: We frequently had CI failures due to formatting inconsistencies between local development and CI.

**Recommendations**:
- **Pin your tool versions**: In your `package.json`, pin exact versions of ESLint, Prettier, etc.
  ```json
  "devDependencies": {
    "eslint": "8.45.0",  // Not ^8.45.0
    "prettier": "3.0.0"   // Not ~3.0.0
  }
  ```
- **Pre-commit hooks**: Consider adding Husky to run formatters before commits
- **Local CI script**: Add a script that runs all CI checks locally:
  ```json
  "scripts": {
    "ci:local": "npm run type-check && npm run lint && npm run test"
  }
  ```

## 2. Cross-Platform Consistency

**Our Experience**: Windows CI often fails differently than macOS/Linux.

**Your Setup Looks Good**: Testing on multiple Node versions is smart. Consider:
- Add Windows to your test matrix if you haven't already
- Be careful with path separators in tests
- Mock file system operations that might behave differently

## 3. Artifact and Release Management

**What We Do**:
- Every CI run produces artifacts (even non-releases)
- We use semantic commit messages for automatic versioning
- Our release process is fully automated from tags

**Suggestions for Your Workflow**:
- Consider using `semantic-release` for automated versioning
- Add commit message validation (conventional commits)
- Store test results as artifacts for debugging failed CI runs

## 4. Security Scanning Integration

**Great Choice on CodeQL!** Additional recommendations:
- Add `npm audit` to your CI pipeline
- Consider Snyk for dependency vulnerability scanning (free for open source)
- Run security scans on PR branches, not just main

## 5. Managing Secrets and API Keys

**Critical for Browser Extensions**:
```yaml
# In your CI, validate secrets exist before using them
- name: Validate Chrome Store Secrets
  run: |
    if [[ -z "${{ secrets.CHROME_APP_ID }}" ]]; then
      echo "::warning::Chrome Store secrets not configured"
    fi
```

## 6. Performance and Time Management

**Our Metrics**:
- Keep CI under 5 minutes for developer happiness
- Parallelize where possible
- Cache dependencies aggressively

**For Your Pipeline**:
```yaml
- uses: actions/cache@v3
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
```

## 7. Coordinating with Stinger API

Since you're integrating with our API:
- **Version Compatibility**: Add a CI check that validates your extension against our API
- **Mock vs Real**: Use mocked Stinger responses for unit tests, real API for E2E
- **Breaking Changes**: Subscribe to our releases to catch API changes early

## 8. PR Workflow Recommendations

**What Works for Us**:
- Require CI passing before merge
- Auto-update branches with base branch changes
- Use merge queues for busy periods

**For Your PR Template**, consider adding:
- [ ] Tested against Stinger API v1
- [ ] Updated TypeScript types if API interaction changed
- [ ] Verified in Chrome, Firefox, Edge

## 9. Debugging CI Failures

**Time Savers**:
1. **SSH into runners**: GitHub supports debugging via SSH
2. **Verbose logging**: Add debug flags in CI but not local
3. **Fail fast**: Order your CI jobs by likelihood of failure

## 10. Metrics and Monitoring

**Track These**:
- CI success rate (aim for >95%)
- Average CI duration
- Flaky test frequency
- Time from PR to merge

## Quick Wins You Can Add Now

1. **Badge for Stinger compatibility**:
   ```markdown
   ![Stinger Compatible](https://img.shields.io/badge/Stinger-v0.1.0a3-brightgreen)
   ```

2. **API compatibility check**:
   ```yaml
   - name: Check Stinger API compatibility
     run: |
       curl -f https://api.stinger.dev/health || exit 1
   ```

3. **Automated dependency updates** (you have Dependabot ✅)
   - Consider grouping updates to reduce PR noise

## Coordination Points

Let's align on:
1. **Release cycles**: We typically release on Tuesdays
2. **API deprecation**: We'll give 30 days notice
3. **Security issues**: Direct channel for critical issues

Great work on the comprehensive setup! The E2E tests with Playwright are particularly valuable for browser extensions. Let us know if you need any Stinger-specific CI integration support.

---
*From the Stinger Core Team*  
*Feel free to reach out in #plugin-dev channel*