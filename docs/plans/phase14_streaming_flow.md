# Phase 14 Streaming Flow Diagrams

## Overall Streaming Architecture

```mermaid
graph TB
    subgraph "Client (Browser Extension)"
        CE[Content Entry]
        CS[Client Rules]
        SS[Stream Sender]
    end
    
    subgraph "Stinger API"
        SE[Stream Endpoint]
        SM[Session Manager]
        PC[Performance Classifier]
        
        subgraph "Execution Modes"
            BG[Blocking Guards<br/>INSTANT/FAST]
            MG[Monitor Guards<br/>SLOW/VERY_SLOW]
        end
        
        AT[Audit Trail]
    end
    
    subgraph "Analytics"
        SIEM[SIEM System]
        RD[Risk Dashboard]
    end
    
    CE -->|Stream chunks| SS
    CS -->|Quick checks| CE
    SS -->|SSE| SE
    SE --> SM
    SM --> PC
    PC -->|Route by speed| BG
    PC -->|Async tasks| MG
    BG -->|Immediate| SE
    MG -->|Background| AT
    AT --> SIEM
    AT --> RD
```

## Guardrail Execution Flow by Performance Class

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Instant
    participant Fast  
    participant Slow
    participant Monitor
    participant Audit
    
    User->>API: Stream chunk "Hello, my SSN is..."
    
    Note over API: Performance Classification
    
    par Blocking Execution
        API->>Instant: Regex PII (2ms)
        Instant-->>API: BLOCKED - SSN detected
    and Fast Checks
        API->>Fast: Keyword check (50ms)
        Fast-->>API: OK
    end
    
    API-->>User: Block response
    
    Note over API: Schedule async
    
    API->>Monitor: AI sentiment (2000ms)
    API->>Monitor: Context analysis (3000ms)
    
    Note over Monitor: Running in background
    
    Monitor-->>Audit: Risk score: 0.85
    Monitor-->>Audit: Would have blocked: No
    
    Audit-->>SIEM: Security event logged
```

## Streaming Session Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Initialized: POST /stream/start
    
    Initialized --> Active: First update
    Active --> Active: POST /stream/update
    Active --> Checking: Checkpoint reached
    
    Checking --> Blocked: Guardrail triggered
    Checking --> Active: All passed
    
    Active --> Finalizing: POST /stream/finish
    Blocked --> Finalizing: User ends
    
    Finalizing --> Audited: Create log entry
    Audited --> [*]
    
    Active --> Timeout: No activity 5min
    Timeout --> [*]
```

## Performance-Based Checkpoint Strategy

```
Content Stream: "Write a Python function to analyze customer data and..."

INSTANT (<10ms):   |W|r|i|t|e| |a| |P|y|t|h|o|n|...
                    ✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓

FAST (10-100ms):    |Write| |a| |Python| |function|...
                     ✓      ✓   ✓        ✓

MODERATE (100-1000ms): |Write a Python function|...
                        ✓

SLOW (1-5s):        |Write a Python function to analyze customer data|.
                     ✓ (or async)

VERY_SLOW (>5s):    [Entire message - async only]
                     ➜ Monitor mode
```

## Monitor Mode Decision Flow

```mermaid
graph TD
    G[Guardrail] --> P{Performance<br/>Class?}
    
    P -->|INSTANT<br/><10ms| B1[Always BLOCK]
    P -->|FAST<br/>10-100ms| C1{Config?}
    P -->|MODERATE<br/>100-1000ms| C2{Config?}
    P -->|SLOW<br/>1-5s| C3{Config?}
    P -->|VERY_SLOW<br/>>5s| M1[Always MONITOR]
    
    C1 -->|Default| B2[BLOCK]
    C1 -->|Override| M2[MONITOR]
    
    C2 -->|Default| B3[BLOCK]
    C2 -->|Override| M3[MONITOR]
    
    C3 -->|Default| M4[MONITOR]
    C3 -->|Override| B4[BLOCK<br/>Warning: Slow!]
    
    B1 --> SYNC[Sync Execution]
    B2 --> SYNC
    B3 --> SYNC
    B4 --> SYNC
    
    M1 --> ASYNC[Async Queue]
    M2 --> ASYNC
    M3 --> ASYNC
    M4 --> ASYNC
    
    SYNC --> R[Return Result]
    ASYNC --> A[Audit Later]
```

## Implementation Priority Matrix

```
High Impact / Low Effort:
┌─────────────────────────────┐
│ • Client-side regex rules   │
│ • Performance metadata      │
│ • Basic monitor mode        │
└─────────────────────────────┘
            ↓
High Impact / High Effort:
┌─────────────────────────────┐
│ • Streaming API endpoints   │
│ • Session management        │
│ • Web demo streaming        │
└─────────────────────────────┘
            ↓
Low Impact / Low Effort:
┌─────────────────────────────┐
│ • Status indicators         │
│ • Metrics enhancement       │
│ • Documentation             │
└─────────────────────────────┘
```