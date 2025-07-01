# Phase 7D.2: Web Demo Stability Fix Plan

## Problem Analysis

### Current Issues:
1. **Frontend Memory Crashes**: React dev server runs out of memory
2. **Large Monolithic Component**: App.tsx is 451 lines (too large)
3. **React 19.1.0**: Using latest React which may have compatibility issues
4. **Development Server**: react-scripts dev server is memory intensive

### Root Causes:
1. **Monolithic App.tsx**: All logic in one component causes excessive re-renders
2. **Memory Leaks**: Possible unmanaged state or effect hooks
3. **Build Tool Issues**: react-scripts known for memory problems with large apps

## Solution Strategy

### Option 1: Quick Fix (Recommended for Phase 7D.2)
Focus on making the demo stable enough for testing without major refactoring.

1. **Downgrade Dependencies**:
   - React 19.1.0 → 18.2.0 (stable LTS)
   - react-scripts 5.0.1 (keep, but optimize)

2. **Add Memory Optimization**:
   - Create `.env` file with build optimizations
   - Add memory limits to package.json scripts
   - Disable source maps in development

3. **Simple Component Split**:
   - Extract ChatMessage component
   - Extract GuardrailSettings component
   - Keep main logic in App.tsx for now

4. **Production Build Focus**:
   - Ensure production build works reliably
   - Create simple static server for production build
   - Document this as primary demo method

### Option 2: Full Refactor (Future Enhancement)
Complete architectural overhaul - save for post-Phase 7.

1. **Modern Build Tool**: Migrate from react-scripts to Vite
2. **Component Architecture**: Full component separation
3. **State Management**: Add proper state management
4. **TypeScript Optimization**: Improve type definitions

## Implementation Plan for Quick Fix

### Step 1: Create Build Optimizations
```bash
# Create .env file
GENERATE_SOURCEMAP=false
FAST_REFRESH=false
NODE_OPTIONS=--max-old-space-size=4096
```

### Step 2: Update package.json Scripts
```json
"scripts": {
  "start": "GENERATE_SOURCEMAP=false react-scripts start",
  "build": "GENERATE_SOURCEMAP=false react-scripts build",
  "start:prod": "npm run build && node serve-prod.js"
}
```

### Step 3: Extract Components
1. ChatMessage.tsx - Display individual messages
2. GuardrailSettings.tsx - Settings panel
3. AuditLog.tsx - Audit log display

### Step 4: Create Production Server
Simple Express server to serve the production build with HTTPS.

### Step 5: Update Documentation
- Primary method: Use production build
- Secondary method: Development server (with caveats)

## Success Criteria

1. **Production Build**: Works 100% of the time
2. **Static Serving**: Reliable HTTPS serving of production build
3. **Demo Usability**: Users can test all features
4. **Documentation**: Clear instructions for both methods

## Timeline

- 2 hours: Implement quick fixes
- 1 hour: Test thoroughly
- 30 minutes: Update documentation

## Decision

Recommend **Option 1: Quick Fix** for Phase 7D.2. This provides:
- Immediate stability improvements
- Minimal code changes
- Focus on working demo for release
- Future refactoring possible post-release

The goal is a stable, working demo for Phase 7 completion, not architectural perfection.