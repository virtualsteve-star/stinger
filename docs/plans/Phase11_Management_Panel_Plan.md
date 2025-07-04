# Phase 11: Stinger Management Panel

## Overview

Create a lightweight, attractive HTML management panel for monitoring and analyzing Stinger guardrails in real-time. This will provide operators with insights into system health, performance, and security events.

## Objectives

1. **Real-time Monitoring**: Live view of system health and active conversations
2. **Performance Analytics**: Guardrail performance metrics and trends
3. **Log Analysis**: Smart search and filtering of audit logs
4. **Minimal Dependencies**: Fast build/run with minimal bloat
5. **Production Ready**: Secure, performant, and useful for operators

## Architecture

### Backend (FastAPI)
- Lightweight REST API endpoints
- WebSocket for real-time updates
- Direct integration with existing Stinger components
- No additional database required (uses existing audit logs)

### Frontend (React + Minimal Dependencies)
- Create React App (minimal template)
- Recharts for data visualization (lightweight, no D3 dependency)
- React Query for efficient data fetching
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
# FastAPI routes
GET  /api/stats/overview      # Dashboard stats
GET  /api/guardrails/metrics  # Guardrail performance
GET  /api/conversations       # Active conversations
GET  /api/audit/search        # Log search with filters
GET  /api/health             # System health status
WS   /ws/live                # WebSocket for real-time updates
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
│   ├── useWebSocket.js
│   ├── useMetrics.js
│   └── useAuditLogs.js
└── utils/
    ├── api.js
    ├── formatters.js
    └── constants.js
```

### Data Flow
1. **Real-time Updates**: WebSocket pushes live metrics
2. **Polling**: Background refresh every 30s for non-critical data
3. **Caching**: React Query caches responses for efficiency
4. **Pagination**: Server-side pagination for log explorer

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

### Phase 11A: Core Infrastructure (2 days)
- Set up FastAPI endpoints
- Create React app structure
- Implement WebSocket connection
- Basic authentication/security

### Phase 11B: Dashboard & Metrics (2 days)
- Dashboard overview components
- Guardrail performance table
- Real-time metric updates
- Basic charts with Recharts

### Phase 11C: Conversation & Logs (2 days)
- Active conversation monitor
- Audit log explorer with filters
- Search functionality
- Export capabilities

### Phase 11D: Polish & Deploy (1 day)
- System health monitoring
- Error handling
- Performance optimization
- Deployment configuration

## Performance Targets

- **Initial Load**: < 2 seconds
- **Bundle Size**: < 200KB gzipped
- **API Response**: < 100ms for most endpoints
- **WebSocket Latency**: < 50ms
- **Memory Usage**: < 50MB client-side

## Security Considerations

1. **Authentication**: API key or session-based
2. **Read-only**: No modification capabilities
3. **Rate Limiting**: Prevent abuse
4. **CORS**: Properly configured
5. **Data Sanitization**: Prevent XSS

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
│ 🛡️ Stinger Management                          admin │ ⚙️ │ 🔔 │
├───────┬─────────────────────────────────────────────────────────┤
│       │                                                         │
│   📊  │  System Overview                              Live 🟢  │
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

1. **Review & Approve**: Get feedback on the plan
2. **Prototype**: Build minimal version for validation
3. **Iterate**: Refine based on user feedback
4. **Deploy**: Production-ready release

This management panel will provide operators with a powerful yet lightweight tool for monitoring and analyzing their Stinger deployment without adding significant complexity or dependencies.