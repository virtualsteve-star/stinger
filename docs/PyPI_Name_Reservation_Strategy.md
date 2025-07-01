# PyPI Name Reservation Strategy

## Overview

To protect the Stinger project's namespace on PyPI, we're reserving three related package names:

1. **`stinger`** - Short, memorable name (placeholder)
2. **`stinger-guardrails`** - Main package name (placeholder for now)
3. **`stinger-guardrails-alpha`** - Current alpha release

## Current Plan

### Phase 1: Reserve Names (Immediate)
- Upload placeholder packages for `stinger` and `stinger-guardrails`
- These redirect users to the appropriate package
- Prevents name squatting

### Phase 2: Alpha Release (Current)
- Publish actual framework as `stinger-guardrails-alpha`
- This is the working package users can install and test

### Phase 3: Production Release (Future)
- Transition from `stinger-guardrails-alpha` to `stinger-guardrails`
- Consider if `stinger` should remain a redirect or become the primary name

## Placeholder Package Details

### `stinger` (0.0.1)
- Status: Placeholder only
- Description: Redirects to stinger-guardrails
- Purpose: Reserve short name for potential future use

### `stinger-guardrails` (0.0.1)
- Status: Placeholder (will become main package)
- Description: Points to alpha version for now
- Purpose: Reserve primary package name

### `stinger-guardrails-alpha` (0.1.0a1)
- Status: Active development package
- Description: Full framework implementation
- Purpose: Current distribution for testing

## How to Reserve the Names

1. Build the placeholder packages:
   ```bash
   cd placeholders
   ./build_placeholders.sh
   ```

2. Upload to PyPI (requires credentials):
   ```bash
   # Upload stinger placeholder
   cd stinger
   python3 -m twine upload dist/*
   
   # Upload stinger-guardrails placeholder
   cd ../stinger-guardrails
   python3 -m twine upload dist/*
   ```

3. Then upload the actual alpha package:
   ```bash
   cd ../..
   python3 -m twine upload dist/stinger_guardrails_alpha-*
   ```

## Benefits

1. **Brand Protection**: Prevents others from taking these names
2. **Flexibility**: Can decide later which name to use as primary
3. **User Guidance**: Placeholders guide users to the right package
4. **Professional**: Shows project maturity and planning

## Future Decisions

When ready for production release, decide:
- Should `stinger-guardrails` be the primary name? (Recommended)
- Should `stinger` redirect forever or become primary?
- How to handle the transition from alpha to production?

## Important Notes

- Once a name is taken on PyPI, it cannot be transferred (only deleted with admin help)
- Placeholder packages should have clear documentation pointing to the real package
- Version 0.0.1 is standard for placeholders
- All three packages should have consistent maintainer information

---

Created: 2025-07-01