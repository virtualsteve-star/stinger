# Phase 11: Stinger Management Panel

## Overview

Create a simple, lightweight management console for monitoring Stinger guardrails. This will provide operators with real-time insights into system health, performance, and security events without unnecessary complexity.

## Objectives

1. **Simple Monitoring**: Clear view of system health and active conversations
2. **Performance Analytics**: Guardrail performance metrics and trends
3. **Log Analysis**: Search and filter audit logs
4. **Minimal Dependencies**: Fast build/run with minimal bloat
5. **Easy to Use**: No authentication, just run and monitor

## Architecture

### Backend (FastAPI)
- Simple REST API endpoints
- Polling-based updates (no WebSockets)
- Direct integration with existing Stinger components
- No additional database required (uses existing audit logs)
- No authentication or access control

### Frontend (React + Minimal Dependencies)
- Reuse components from Phase 10 web demo
- Recharts for data visualization (lightweight, no D3 dependency)
- React Query for efficient data fetching with smart polling
- Tailwind CSS for styling (utility-first, small bundle)
- No heavy UI frameworks (no Material-UI, Ant Design, etc.)

## Core Features

### 1. Dashboard Overview
```
┌─────────────────────────────────────────────────────────────┐
│ 🛡️ Stinger Management Panel                    [Live] 🟢    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Total Reqs  │  │ Blocked     │  │ Active      │        │
│  │   12,456    │  │   234 (2%)  │  │   3 convos  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                             │
│  ┌─────────────────────────────────────────────────┐       │
│  │ Request Volume (Last Hour)          [Chart]     │       │
│  └─────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### 2. Guardrail Performance View
- Real-time metrics per guardrail:
  - Average response time
  - Block/warn/allow rates
  - Error rates
  - P95/P99 latencies
- Sortable table with sparkline trends
- Click for detailed guardrail analytics

### 3. Active Conversations Monitor
- Live view of ongoing conversations
- Conversation metadata (ID, user, start time)
- Real-time guardrail decisions
- Ability to flag/review conversations
- Export conversation history

### 4. Audit Log Explorer
**Smart Filtering:**
- Time range selector
- Guardrail type filter
- Decision filter (blocked/warned/allowed)
- Severity filter
- Full-text search

**Insights Features:**
- Top blocked patterns
- Anomaly detection (spike in blocks)
- User behavior patterns
- Most triggered guardrails

### 5. System Health Monitor
- Guardrail health status (up/down/degraded)
- API key status (valid/expiring/invalid)
- Response time trends
- Error rate monitoring
- Resource usage (if available)

## Technical Implementation

### Backend Endpoints
```python
# FastAPI routes - Simple REST, no auth required
GET  /api/stats/overview      # Dashboard stats
GET  /api/guardrails/metrics  # Guardrail performance  
GET  /api/conversations       # Active conversations
GET  /api/audit/search        # Log search with filters
GET  /api/health             # System health status
# No WebSockets - just polling
```

### Frontend Components
```
src/
├── components/
│   ├── Dashboard/
│   │   ├── StatsCards.jsx
│   │   ├── VolumeChart.jsx
│   │   └── QuickInsights.jsx
│   ├── Guardrails/
│   │   ├── PerformanceTable.jsx
│   │   ├── GuardrailDetail.jsx
│   │   └── MetricSparkline.jsx
│   ├── Conversations/
│   │   ├── ActiveList.jsx
│   │   ├── ConversationDetail.jsx
│   │   └── DecisionFeed.jsx
│   ├── Logs/
│   │   ├── LogExplorer.jsx
│   │   ├── FilterPanel.jsx
│   │   └── InsightCards.jsx
│   └── Health/
│       ├── SystemStatus.jsx
│       └── HealthIndicators.jsx
├── hooks/
│   ├── useMetrics.js      # Polling with React Query
│   ├── useAuditLogs.js    # Log fetching and filtering
│   └── usePolling.js      # Smart polling intervals
└── utils/
    ├── api.js
    ├── formatters.js
    └── constants.js
```

### Data Flow
1. **Smart Polling**: 5s for metrics, 10s for conversations
2. **Tab-aware**: Reduce polling when tab is hidden
3. **Caching**: React Query caches responses for efficiency
4. **Pagination**: Server-side pagination for log explorer
5. **Manual Refresh**: Refresh buttons for immediate updates

## Open Source Components

### Required (Minimal Set)
1. **React** (v18) - UI framework
2. **Recharts** - Lightweight charting (63KB gzipped)
3. **React Query** - Data fetching/caching (13KB gzipped)
4. **Tailwind CSS** - Utility CSS framework
5. **FastAPI** - Backend API (already in use)
6. **date-fns** - Date utilities (lightweight)

### Optional Enhancements
1. **Fuse.js** - Fuzzy search for logs (client-side)
2. **React Table** - Advanced table features (if needed)
3. **Framer Motion** - Smooth animations (if desired)

## Development Plan

### Phase 11A: Core Infrastructure (1 day)
- Set up simple FastAPI endpoints (no auth)
- Adapt Phase 10 React components
- Implement smart polling with React Query
- Basic project structure

### Phase 11B: Dashboard & Metrics (1.5 days)
- Dashboard overview (reuse Phase 10 patterns)
- Guardrail performance table
- Polling-based metric updates
- Simple charts with Recharts

### Phase 11C: Conversation & Logs (1.5 days)
- Active conversation monitor
- Audit log explorer (adapt LogPanel from Phase 10)
- Search functionality
- CSV export for logs

### Phase 11D: Polish & Deploy (1 day)
- System health monitoring
- Error handling
- Performance optimization
- Simple deployment (just run it!)

## Performance Targets

- **Initial Load**: < 2 seconds
- **Bundle Size**: < 200KB gzipped
- **API Response**: < 100ms for most endpoints
- **Polling Efficiency**: Smart intervals based on tab visibility
- **Memory Usage**: < 50MB client-side

## Security Considerations

1. **No Authentication**: Simple console, run locally
2. **Read-only**: No modification capabilities  
3. **CORS**: Configured for local development
4. **Data Sanitization**: Prevent XSS
5. **Local Use**: Designed for operators with system access

## Deployment Options

1. **Standalone**: Separate service on different port
2. **Integrated**: Part of main Stinger API
3. **Static Hosting**: Frontend on CDN, API separate

## Success Criteria

1. **Useful**: Provides actionable insights
2. **Fast**: Loads and updates quickly
3. **Attractive**: Clean, modern UI
4. **Reliable**: Handles errors gracefully
5. **Lightweight**: Minimal dependencies

## Example UI Mockup

```
┌─────────────────────────────────────────────────────────────────┐
│ 🛡️ Stinger Management Console                    [↻ Refresh]  │
├───────┬─────────────────────────────────────────────────────────┤
│       │                                                         │
│   📊  │  System Overview                    Updated: 2s ago  │
│   🎯  │  ┌─────────────┬─────────────┬─────────────┐         │
│   💬  │  │ Total       │ Blocked     │ Active      │         │
│   📝  │  │ 12,456      │ 234 (1.9%)  │ 3 convos    │         │
│   ❤️  │  └─────────────┴─────────────┴─────────────┘         │
│       │                                                         │
│       │  Request Volume (60 min)                               │
│       │  ┌─────────────────────────────────────────┐         │
│       │  │     ╱╲    ╱╲                             │         │
│       │  │   ╱╱  ╲  ╱  ╲  ╱╲                       │         │
│       │  │ ╱╱     ╲╱    ╲╱  ╲───                   │         │
│       │  └─────────────────────────────────────────┘         │
│       │                                                         │
│       │  Top Guardrails (by blocks)                           │
│       │  ┌─────────────────────────────────────────┐         │
│       │  │ 🚫 Toxicity Detection    ████████ 45%   │         │
│       │  │ 🔒 PII Detection         ████ 23%       │         │
│       │  │ 💉 Prompt Injection      ███ 18%        │         │
│       │  │ 🌐 URL Filter            ██ 14%         │         │
│       │  └─────────────────────────────────────────┘         │
└───────┴─────────────────────────────────────────────────────────┘
```

## Next Steps

1. **Start Simple**: Build core monitoring features first
2. **Reuse Phase 10**: Leverage existing components
3. **Test Locally**: Ensure it works out of the box
4. **Document**: Simple README for operators

## Quick Start (Future)
```bash
# Start Stinger with management console
cd management-console
npm install
npm start
# Open http://localhost:3001
```

This management console will provide operators with a simple, no-auth monitoring tool that just works. Perfect for development and small deployments where simplicity matters more than enterprise features.