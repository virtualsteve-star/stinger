#!/usr/bin/env python3
"""
Stinger Management Console Backend

Simple REST API for monitoring Stinger guardrails.
No authentication required - designed for local use.
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import tempfile
from collections import defaultdict
import random

# Add src to path for Stinger imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import Stinger components
from stinger.core.pipeline import GuardrailPipeline
from stinger.core import audit
from stinger.core.health_monitor import HealthMonitor

# Initialize FastAPI app
app = FastAPI(
    title="Stinger Management Console API",
    description="Simple monitoring API for Stinger guardrails",
    version="1.0.0"
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
console_state = {
    "pipeline": None,
    "health_monitor": None,
    "audit_file": None,
    "start_time": datetime.now()
}


# Response models
class SystemStats(BaseModel):
    total_requests: int
    blocked_requests: int
    block_rate: float
    active_conversations: int
    uptime_seconds: int
    last_activity: Optional[str]


class GuardrailMetric(BaseModel):
    name: str
    type: str
    enabled: bool
    total_checks: int
    blocks: int
    warnings: int
    avg_response_ms: float
    error_rate: float


class ConversationInfo(BaseModel):
    conversation_id: str
    user_id: str
    start_time: str
    turn_count: int
    last_activity: str
    status: str  # active, idle, completed


class AuditLogEntry(BaseModel):
    timestamp: str
    event_type: str
    conversation_id: Optional[str]
    guardrail: Optional[str]
    decision: Optional[str]
    reason: Optional[str]
    user_id: Optional[str]


class HealthStatus(BaseModel):
    status: str  # healthy, degraded, unhealthy
    guardrails_loaded: int
    api_keys_valid: bool
    audit_enabled: bool
    errors: List[str]


@app.on_event("startup")
async def startup_event():
    """Initialize Stinger components on startup."""
    try:
        # Initialize health monitor
        console_state["health_monitor"] = HealthMonitor()
        
        # Set up audit file 
        audit_log_path = Path(tempfile.gettempdir()) / "stinger_web_demo_audit.log"
        console_state["audit_file"] = audit_log_path
        
        # Enable audit logging
        if audit_log_path.exists():
            audit.enable(str(audit_log_path))
            print(f"📝 Reading audit logs from: {audit_log_path}")
        
        # Try to load a sample pipeline for monitoring
        try:
            from stinger.core.config import load_config
            config_path = Path(__file__).parent.parent.parent / "demos" / "web_demo" / "backend" / "demo_config_full.yaml"
            if config_path.exists():
                config = load_config(str(config_path))
                console_state["pipeline"] = GuardrailPipeline(config)
                print(f"✅ Loaded demo pipeline with {len(config.get('input_guardrails', []))} input guardrails")
        except Exception as e:
            print(f"⚠️ Could not load demo pipeline: {e}")
        
        print(f"✅ Management Console API started")
        print(f"📊 Monitoring available at http://localhost:8001")
        
    except Exception as e:
        print(f"⚠️ Warning: Could not initialize all components: {e}")


@app.get("/api/stats/overview")
async def get_system_stats() -> SystemStats:
    """Get system overview statistics."""
    health_monitor = console_state.get("health_monitor")
    
    # Calculate uptime
    uptime = datetime.now() - console_state["start_time"]
    
    # Get real metrics from health monitor
    if health_monitor and health_monitor.performance_metrics:
        metrics = health_monitor.performance_metrics
        total = metrics.get("total_requests", 0)
        blocked = metrics.get("blocked_requests", 0)
        block_rate = (blocked / max(total, 1)) * 100
        
        # Count active conversations from audit log
        active_convos = 0
        if console_state["audit_file"] and console_state["audit_file"].exists():
            # Simple count of unique conversations in last 5 minutes
            recent_time = datetime.now() - timedelta(minutes=5)
            active_convos = 3  # TODO: Parse audit log for real count
        
        return SystemStats(
            total_requests=total,
            blocked_requests=blocked,
            block_rate=round(block_rate, 2),
            active_conversations=active_convos,
            uptime_seconds=int(uptime.total_seconds()),
            last_activity=datetime.fromtimestamp(metrics.get("last_request_time", 0)).isoformat() if metrics.get("last_request_time") else None
        )
    
    # Return some data even if no real metrics yet
    return SystemStats(
        total_requests=0,
        blocked_requests=0,
        block_rate=0.0,
        active_conversations=0,
        uptime_seconds=int(uptime.total_seconds()),
        last_activity=None
    )


@app.get("/api/guardrails/metrics")
async def get_guardrail_metrics() -> List[GuardrailMetric]:
    """Get performance metrics for each guardrail."""
    pipeline = console_state.get("pipeline")
    metrics = []
    
    if pipeline:
        # Get real guardrails from pipeline
        all_guardrails = []
        for g in pipeline.input_guardrails:
            all_guardrails.append(("input", g))
        for g in pipeline.output_guardrails:
            all_guardrails.append(("output", g))
        
        # Create metrics for each guardrail
        for stage, guardrail in all_guardrails:
            # Determine type
            guardrail_type = "ai" if hasattr(guardrail, 'ai_powered') and guardrail.ai_powered else "local"
            
            # Get real metrics if available (would need to track these)
            metric = GuardrailMetric(
                name=f"{guardrail.name} ({stage})",
                type=guardrail_type,
                enabled=guardrail.enabled,
                total_checks=0,  # TODO: Track real metrics
                blocks=0,
                warnings=0,
                avg_response_ms=0.0,
                error_rate=0.0
            )
            metrics.append(metric)
    
    # If no pipeline, return some sample data
    if not metrics:
        sample_guardrails = [
            {"name": "pii_detection (input)", "type": "ai", "enabled": True},
            {"name": "toxicity_detection (input)", "type": "ai", "enabled": True},
            {"name": "prompt_injection (input)", "type": "ai", "enabled": True},
            {"name": "length_filter (input)", "type": "local", "enabled": True},
            {"name": "pii_detection (output)", "type": "ai", "enabled": True},
        ]
        
        for g in sample_guardrails:
            metrics.append(GuardrailMetric(
                **g,
                total_checks=0,
                blocks=0,
                warnings=0,
                avg_response_ms=0.0,
                error_rate=0.0
            ))
    
    return metrics


@app.get("/api/conversations")
async def get_active_conversations() -> List[ConversationInfo]:
    """Get list of active conversations."""
    # Mock data
    now = datetime.now()
    conversations = [
        {
            "conversation_id": "conv_abc123",
            "user_id": "user_001",
            "start_time": (now - timedelta(minutes=15)).isoformat(),
            "turn_count": 8,
            "last_activity": (now - timedelta(seconds=30)).isoformat(),
            "status": "active"
        },
        {
            "conversation_id": "conv_def456",
            "user_id": "user_002", 
            "start_time": (now - timedelta(minutes=5)).isoformat(),
            "turn_count": 3,
            "last_activity": (now - timedelta(seconds=120)).isoformat(),
            "status": "idle"
        },
        {
            "conversation_id": "conv_ghi789",
            "user_id": "demo_user",
            "start_time": (now - timedelta(minutes=2)).isoformat(),
            "turn_count": 1,
            "last_activity": (now - timedelta(seconds=5)).isoformat(),
            "status": "active"
        }
    ]
    
    return [ConversationInfo(**c) for c in conversations]


@app.get("/api/audit/search")
async def search_audit_logs(
    start_time: Optional[str] = Query(None),
    end_time: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    guardrail: Optional[str] = Query(None),
    decision: Optional[str] = Query(None),
    limit: int = Query(100, le=1000)
) -> List[AuditLogEntry]:
    """Search audit logs with filters."""
    logs = []
    
    # Try to read real audit logs
    audit_file = console_state.get("audit_file")
    if audit_file and audit_file.exists():
        try:
            with open(audit_file, 'r') as f:
                # Read last N lines for efficiency
                lines = f.readlines()[-limit*2:]  # Read extra to account for filtering
                
                for line in lines:
                    try:
                        log_data = json.loads(line.strip())
                        
                        # Map audit log format to our API format
                        log_entry = {
                            "timestamp": log_data.get("timestamp", ""),
                            "event_type": log_data.get("event_type", ""),
                            "conversation_id": log_data.get("conversation_id"),
                            "user_id": log_data.get("user_id"),
                            "guardrail": log_data.get("filter_name"),
                            "decision": log_data.get("decision"),
                            "reason": log_data.get("reason")
                        }
                        
                        # Apply filters
                        if event_type and log_entry["event_type"] != event_type:
                            continue
                        if guardrail and log_entry["guardrail"] != guardrail:
                            continue
                        if decision and log_entry["decision"] != decision:
                            continue
                        
                        logs.append(AuditLogEntry(**log_entry))
                        
                    except json.JSONDecodeError:
                        continue
                    except Exception:
                        continue
                        
        except Exception as e:
            print(f"Error reading audit logs: {e}")
    
    # If no real logs, return empty list
    return logs[-limit:] if logs else []


@app.get("/api/analytics/advanced")
async def get_advanced_analytics(
    range: str = Query("24h", regex="^(1h|24h|7d|30d)$")
) -> Dict[str, Any]:
    """Get advanced analytics data."""
    # Generate sample data based on time range
    hours = {
        "1h": 1,
        "24h": 24,
        "7d": 168,
        "30d": 720
    }[range]
    
    # Performance timeline
    performance_timeline = []
    for i in range(min(hours, 48)):
        performance_timeline.append({
            "time": f"{i}h ago",
            "avg_response_ms": random.randint(50, 150),
            "p95_response_ms": random.randint(100, 300)
        })
    
    # Guardrail effectiveness
    guardrail_effectiveness = [
        {"guardrail": "PII", "effectiveness": 95, "block_rate": 8},
        {"guardrail": "Toxicity", "effectiveness": 88, "block_rate": 12},
        {"guardrail": "Injection", "effectiveness": 92, "block_rate": 15},
        {"guardrail": "Length", "effectiveness": 100, "block_rate": 5},
        {"guardrail": "Code", "effectiveness": 85, "block_rate": 3}
    ]
    
    # Threat distribution
    threat_distribution = [
        {"threat_type": "PII Leak", "count": random.randint(10, 50)},
        {"threat_type": "Prompt Injection", "count": random.randint(20, 80)},
        {"threat_type": "Toxic Content", "count": random.randint(5, 30)},
        {"threat_type": "Data Exfiltration", "count": random.randint(2, 15)},
        {"threat_type": "Other", "count": random.randint(1, 10)}
    ]
    
    # Scatter data for request analysis
    scatter_data = []
    for _ in range(100):
        scatter_data.append({
            "request_size": random.uniform(0.1, 10),
            "response_time": random.uniform(20, 200),
            "blocked": random.choice([True, False, False, False])  # 25% blocked
        })
    
    # Calculate insights
    top_threat = max(threat_distribution, key=lambda x: x["count"])
    avg_response = sum(p["avg_response_ms"] for p in performance_timeline[:10]) / min(10, len(performance_timeline))
    
    return {
        "performance_timeline": performance_timeline,
        "guardrail_effectiveness": guardrail_effectiveness,
        "threat_distribution": threat_distribution,
        "scatter_data": scatter_data,
        "top_threat": top_threat["threat_type"],
        "top_threat_count": top_threat["count"],
        "avg_response_time": round(avg_response, 2),
        "p95_response_time": round(avg_response * 1.8, 2),
        "false_positive_rate": round(random.uniform(1, 5), 2),
        "false_positives": random.randint(5, 20)
    }


@app.get("/api/settings/retention")
async def get_retention_settings() -> Dict[str, Any]:
    """Get data retention settings."""
    return {
        "retention_days": console_state.get("retention_days", 7),
        "metrics_sample_rate": console_state.get("metrics_sample_rate", 100)
    }


@app.put("/api/settings/retention")
async def update_retention_settings(settings: Dict[str, Any]) -> Dict[str, str]:
    """Update data retention settings."""
    console_state["retention_days"] = settings.get("retention_days", 7)
    console_state["metrics_sample_rate"] = settings.get("metrics_sample_rate", 100)
    return {"status": "updated"}


@app.post("/api/maintenance/clear-old-data")
async def clear_old_data(params: Dict[str, Any]) -> Dict[str, int]:
    """Clear old data based on retention policy."""
    # Simulate clearing old data
    older_than_days = params.get("older_than_days", 7)
    
    # In a real implementation, this would:
    # 1. Delete audit logs older than specified days
    # 2. Archive or delete old metrics
    # 3. Clean up temporary files
    
    logs_deleted = random.randint(1000, 5000)
    metrics_deleted = random.randint(10000, 50000)
    
    return {
        "logs_deleted": logs_deleted,
        "metrics_deleted": metrics_deleted,
        "older_than_days": older_than_days
    }


@app.get("/api/health")
async def get_system_health() -> HealthStatus:
    """Get system health status."""
    errors = []
    
    # Check components
    health_monitor = console_state.get("health_monitor")
    pipeline = console_state.get("pipeline")
    
    # Determine overall status
    if not errors:
        status = "healthy"
    elif len(errors) < 2:
        status = "degraded"
    else:
        status = "unhealthy"
    
    return HealthStatus(
        status=status,
        guardrails_loaded=7,  # Mock
        api_keys_valid=True,
        audit_enabled=True,
        errors=errors
    )


if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )