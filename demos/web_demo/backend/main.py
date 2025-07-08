#!/usr/bin/env python3
"""
FastAPI backend for Stinger Web Demo

This backend provides REST endpoints for the React frontend to interact with
Stinger guardrails, handle chat conversations, and demonstrate real-time
security audit trail capabilities.

Features:
- Real OpenAI LLM integration with Stinger guardrails
- Conversation API for multi-turn context management
- Dynamic guardrail configuration
- Real-time audit log viewer
- HTTPS with self-signed certificates for security
"""

import sys
import os
import logging
import tempfile
import json
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor
import traceback

# Add src to path for Stinger imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from contextlib import asynccontextmanager
from pydantic import BaseModel

import stinger
from stinger.core.pipeline import GuardrailPipeline
from stinger.core.conversation import Conversation
from stinger.core import audit
from stinger.core.api_key_manager import get_openai_key
from stinger.adapters.openai_adapter import OpenAIAdapter
from stinger.core.health_monitor import HealthMonitor

# Pydantic models for request/response
class ChatMessage(BaseModel):
    content: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    content: str
    blocked: bool
    warnings: List[str]
    reasons: List[str]
    conversation_id: str
    processing_details: Dict[str, Any]


class GuardrailConfig(BaseModel):
    name: str
    enabled: bool


class GuardrailSettings(BaseModel):
    input_guardrails: List[GuardrailConfig]
    output_guardrails: List[GuardrailConfig]
    preset: str
    use_conversation_aware_prompt_injection: bool = False


class SystemStatus(BaseModel):
    status: str
    pipeline_loaded: bool
    conversation_active: bool
    audit_enabled: bool
    total_guardrails: int
    enabled_guardrails: int

# Shared resources (app.state)
executor = ThreadPoolExecutor(max_workers=4)

# Direct async guardrail operations - no longer need thread pool wrappers
async def check_input_async(pipeline, content, conversation):
    """Run input guardrails using native async methods."""
    return await pipeline.check_input_async(content, conversation)

async def check_output_async(pipeline, content, conversation):
    """Run output guardrails using native async methods."""
    return await pipeline.check_output_async(content, conversation)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)  # Use stdout instead of stderr
    ]
)
logger = logging.getLogger(__name__)


# Dependency injection functions
def get_pipeline(request: Request) -> GuardrailPipeline:
    """Get the current pipeline from app state."""
    pipeline = getattr(request.app.state, 'current_pipeline', None)
    if not pipeline:
        raise HTTPException(status_code=500, detail="Pipeline not initialized")
    return pipeline

def get_openai_adapter(request: Request) -> Optional[OpenAIAdapter]:
    """Get the OpenAI adapter from app state."""
    return getattr(request.app.state, 'openai_adapter', None)

def get_conversation(request: Request) -> Optional[Conversation]:
    """Get the current conversation from app state."""
    return getattr(request.app.state, 'current_conversation', None)

def get_current_guardrail_settings(request: Request) -> Optional[GuardrailSettings]:
    """Get the current guardrail settings from app state."""
    return getattr(request.app.state, 'current_guardrail_settings', None)

def get_health_monitor(request: Request) -> Optional[HealthMonitor]:
    """Get the health monitor from app state."""
    return getattr(request.app.state, 'health_monitor', None)


# Define lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    logger.info("Starting Stinger Web Demo backend...")
    
    # Initialize OpenAI adapter using centralized API key manager
    try:
        api_key = get_openai_key()
        if api_key:
            openai_adapter = OpenAIAdapter(api_key=api_key)
            app.state.openai_adapter = openai_adapter
            logger.info("✅ OpenAI adapter initialized with API key from centralized manager")
        else:
            logger.warning("⚠️ No OpenAI API key found in centralized key manager")
            logger.info("💡 To configure API key: Set OPENAI_API_KEY environment variable or use Stinger's key manager")
            app.state.openai_adapter = None
    except Exception as e:
        logger.warning(f"⚠️ OpenAI adapter initialization failed: {e}")
        app.state.openai_adapter = None
    
    # Initialize audit logging with proper error handling
    try:
        audit_log_file = str(Path(tempfile.gettempdir()) / "stinger_web_demo_audit.log")
        audit.enable(audit_log_file, redact_pii=True)
        app.state.audit_log_file = audit_log_file
        logger.info(f"✅ Audit logging enabled: {audit_log_file}")
    except Exception as e:
        logger.warning(f"⚠️ Audit logging initialization failed: {e}")
        app.state.audit_log_file = None
    
    # Initialize default pipeline with custom configuration including prompt injection
    try:
        # Create a custom pipeline configuration with prompt injection
        import yaml
        from stinger.core.pipeline import GuardrailPipeline
        
        # Load comprehensive demo configuration
        config_file_path = Path(__file__).parent / "demo_config_full.yaml"
        
        # If the full config doesn't exist, create it
        if not config_file_path.exists():
            # Fallback to inline config
            demo_config_yaml = """
version: "1.0"
pipeline:
  input:
    - name: pii_check
      type: ai_pii_detection
      enabled: true
      risk_threshold: 70
      block_levels: ["high", "critical"]
      warn_levels: ["medium"]
      on_error: "allow"
    - name: toxicity_check
      type: simple_toxicity_detection
      enabled: true
      risk_threshold: 70
      block_levels: ["high", "critical"]
      warn_levels: ["medium"]
      on_error: "allow"
    - name: length_check
      type: length_guardrail
      enabled: true
      max_length: 1000
      on_error: "allow"
    - name: prompt_injection_check
      type: prompt_injection
      enabled: true
      risk_threshold: 70
      block_levels: ["high", "critical"]
      warn_levels: ["medium"]
      on_error: "allow"
  output:
    - name: pii_check
      type: ai_pii_detection
      enabled: true
      risk_threshold: 70
      block_levels: ["high", "critical"]
      warn_levels: ["medium"]
      on_error: "allow"
    - name: code_generation_check
      type: ai_code_generation
      enabled: true
      risk_threshold: 70
      block_levels: ["high", "critical"]
      warn_levels: ["medium"]
      on_error: "allow"
"""
        
        try:
            # Try to load the comprehensive config file first
            if config_file_path.exists():
                current_pipeline = GuardrailPipeline(str(config_file_path))
                logger.info("✅ Comprehensive demo pipeline loaded with all 14+ guardrails")
            else:
                # Write fallback config to temporary file
                config_file = Path(tempfile.gettempdir()) / "demo_pipeline.yaml"
                with open(config_file, 'w') as f:
                    f.write(demo_config_yaml)
                
                current_pipeline = GuardrailPipeline(str(config_file))
                logger.info("✅ Basic demo pipeline loaded")
        except Exception as e:
            logger.warning(f"⚠️ Custom pipeline failed, falling back to preset: {e}")
            current_pipeline = GuardrailPipeline.from_preset("customer_service")
            logger.info("✅ Fallback customer service pipeline loaded")
        
        app.state.current_pipeline = current_pipeline
        
        # Initialize guardrail settings from current pipeline status
        status = current_pipeline.get_guardrail_status()
        app.state.current_guardrail_settings = GuardrailSettings(
            input_guardrails=[
                GuardrailConfig(name=info["name"], enabled=info["enabled"])
                for info in status.get("input_guardrails", [])
            ],
            output_guardrails=[
                GuardrailConfig(name=info["name"], enabled=info["enabled"])
                for info in status.get("output_guardrails", [])
            ],
            preset="demo",
            use_conversation_aware_prompt_injection=False
        )
        logger.info("✅ Guardrail settings initialized from pipeline")
            
    except Exception as e:
        logger.error(f"❌ Failed to load default pipeline: {e}")
        # Create a basic pipeline as fallback
        try:
            current_pipeline = GuardrailPipeline()  # Use default config
            app.state.current_pipeline = current_pipeline
            logger.info("✅ Fallback basic pipeline loaded")
        except Exception as fallback_error:
            logger.error(f"❌ Failed to create fallback pipeline: {fallback_error}")
            app.state.current_pipeline = None
    
    # Initialize conversation
    app.state.current_conversation = None
    
    # Initialize HealthMonitor
    app.state.health_monitor = HealthMonitor()
    logger.info("✅ HealthMonitor initialized for performance tracking")
    
    logger.info("🚀 Stinger Web Demo backend ready!")
    
    yield
    
    # Shutdown - clean up resources
    logger.info("Shutting down Stinger Web Demo backend...")
    
    # Clean up audit logging
    try:
        if audit.is_enabled():
            audit.disable()
            logger.info("✅ Audit logging disabled")
    except Exception as e:
        logger.warning(f"⚠️ Error disabling audit logging: {e}")
    
    # Clean up executor
    try:
        executor.shutdown(wait=False)
        logger.info("✅ Thread executor shutdown")
    except Exception as e:
        logger.warning(f"⚠️ Error shutting down executor: {e}")


# Initialize FastAPI app
app = FastAPI(
    title="Stinger Web Demo API",
    description="Backend API for Stinger Guardrails Web Demo",
    lifespan=lifespan,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost:3000", "http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check(
    pipeline: GuardrailPipeline = Depends(get_pipeline)
) -> SystemStatus:
    """Health check endpoint."""
    guardrail_status = pipeline.get_guardrail_status()
    input_guardrails = guardrail_status.get("input_guardrails", [])
    output_guardrails = guardrail_status.get("output_guardrails", [])
    # Count input and output guardrails separately (they can have the same name)
    total_guardrails = len(input_guardrails) + len(output_guardrails)
    enabled_guardrails = sum(1 for g in input_guardrails if g["enabled"]) + sum(1 for g in output_guardrails if g["enabled"])
    
    return SystemStatus(
        status="healthy",
        pipeline_loaded=True,
        conversation_active=getattr(app.state, 'current_conversation', None) is not None,
        audit_enabled=audit.is_enabled(),
        total_guardrails=total_guardrails,
        enabled_guardrails=enabled_guardrails
    )


@app.post("/api/chat")
async def chat_endpoint(
    message: ChatMessage,
    pipeline: GuardrailPipeline = Depends(get_pipeline),
    openai_adapter: Optional[OpenAIAdapter] = Depends(get_openai_adapter),
    health_monitor: Optional[HealthMonitor] = Depends(get_health_monitor)
) -> ChatResponse:
    """Main chat endpoint that processes user input through guardrails and LLM."""
    import time
    start_time = time.time()
    
    # Get or create conversation
    conversation = getattr(app.state, 'current_conversation', None)
    if not conversation:
        conversation = Conversation.human_ai("web_demo_user", "gpt-4o-mini")
        app.state.current_conversation = conversation
    
    # Add user message to conversation
    conversation.add_prompt(message.content)
    
    # Check input through guardrails
    input_result = await check_input_async(pipeline, message.content, conversation)
    
    if input_result['blocked']:
        # Input was blocked by guardrails
        
        # Update performance metrics
        if health_monitor:
            response_time_ms = (time.time() - start_time) * 1000
            health_monitor.update_performance_metrics(response_time_ms, blocked=True)
        
        return ChatResponse(
            content="",
            blocked=True,
            warnings=input_result['warnings'],
            reasons=input_result['reasons'],
            conversation_id=conversation.conversation_id,
            processing_details=input_result['details']
        )
    
    # Generate response using OpenAI (if available)
    if openai_adapter:
        try:
            # Get conversation history for context
            history = conversation.get_history()
            
            # Generate response using OpenAI
            response = await openai_adapter.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": message.content}
                ],
                max_tokens=150,
                temperature=0.7
            )
            response_content = response.choices[0].message.content or "I apologize, but I couldn't generate a response."
            logger.info(f"OpenAI response content: {response_content[:100]}...")  # Debug log
            
            # Check output through guardrails (this automatically adds response to conversation)
            output_result = await check_output_async(pipeline, response_content, conversation)
            
            if output_result['blocked']:
                # Output was blocked by guardrails
                return ChatResponse(
                    content="",
                    blocked=True,
                    warnings=output_result['warnings'],
                    reasons=output_result['reasons'],
                    conversation_id=conversation.conversation_id,
                    processing_details=output_result['details']
                )
            
            # Update performance metrics
            if health_monitor:
                response_time_ms = (time.time() - start_time) * 1000
                health_monitor.update_performance_metrics(response_time_ms, blocked=False)
            
            # Return successful response
            chat_response = ChatResponse(
                content=response_content,
                blocked=False,
                warnings=input_result['warnings'] + output_result['warnings'],
                reasons=[],
                conversation_id=conversation.conversation_id,
                processing_details={
                    'input': input_result['details'],
                    'output': output_result['details']
                }
            )
            logger.info(f"Returning chat response with content: {chat_response.content[:100]}...")  # Debug log
            logger.info(f"Full response object: {chat_response.dict()}")  # More detailed debug
            return chat_response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return ChatResponse(
                content="I apologize, but I'm having trouble generating a response right now.",
                blocked=False,
                warnings=input_result['warnings'] + [f"LLM Error: {str(e)}"],
                reasons=[],
                conversation_id=conversation.conversation_id,
                processing_details={
                    'input': input_result['details'],
                    'llm_error': str(e)
                }
            )
    else:
        # No OpenAI adapter available - return mock response with setup instructions
        mock_response = """⚠️ OpenAI API not configured. To enable LLM responses:

1. Get an API key from https://platform.openai.com/account/api-keys
2. Set the environment variable: export OPENAI_API_KEY="your-key-here"
3. Restart the backend server

For now, this is a mock response demonstrating that guardrails are working correctly."""
        
        # Check output through guardrails (this automatically adds response to conversation)
        output_result = await check_output_async(pipeline, mock_response, conversation)
        
        # Update performance metrics
        if health_monitor:
            response_time_ms = (time.time() - start_time) * 1000
            health_monitor.update_performance_metrics(response_time_ms, blocked=False)
        
        return ChatResponse(
            content=mock_response,
            blocked=False,
            warnings=input_result['warnings'] + output_result['warnings'] + ["OpenAI API key not configured"],
            reasons=[],
            conversation_id=conversation.conversation_id,
            processing_details={
                'input': input_result['details'],
                'output': output_result['details'],
                'mock_response': True,
                'setup_required': 'OPENAI_API_KEY environment variable'
            }
        )


@app.get("/api/guardrails")
async def get_guardrail_settings(
    settings: Optional[GuardrailSettings] = Depends(get_current_guardrail_settings)
) -> GuardrailSettings:
    """Get current guardrail configuration."""
    if not settings:
        raise HTTPException(status_code=500, detail="Guardrail settings not initialized")
    return settings


@app.post("/api/guardrails")
async def update_guardrail_settings(
    settings: GuardrailSettings,
    pipeline: GuardrailPipeline = Depends(get_pipeline)
) -> dict:
    """Update guardrail configuration."""
    
    try:
        logger.info(f"Received guardrail settings update: {settings}")
        
        # Get current pipeline status to understand the structure
        current_status = pipeline.get_guardrail_status()
        input_guardrails = {g["name"]: g for g in current_status.get("input_guardrails", [])}
        output_guardrails = {g["name"]: g for g in current_status.get("output_guardrails", [])}
        
        # Track processed guardrails to avoid duplicates
        processed_guardrails = set()
        
        # Update input guardrails
        logger.info(f"Processing {len(settings.input_guardrails)} input guardrails:")
        for guardrail in settings.input_guardrails:
            if guardrail.name in input_guardrails:
                logger.info(f"  Input guardrail '{guardrail.name}': {'enabling' if guardrail.enabled else 'disabling'}")
                if guardrail.enabled:
                    pipeline.enable_guardrail(guardrail.name, pipeline_type='input')
                else:
                    pipeline.disable_guardrail(guardrail.name, pipeline_type='input')
            else:
                logger.warning(f"  Input guardrail not found: {guardrail.name}")
        
        # Update output guardrails
        logger.info(f"Processing {len(settings.output_guardrails)} output guardrails:")
        for guardrail in settings.output_guardrails:
            if guardrail.name in output_guardrails:
                logger.info(f"  Output guardrail '{guardrail.name}': {'enabling' if guardrail.enabled else 'disabling'}")
                if guardrail.enabled:
                    pipeline.enable_guardrail(guardrail.name, pipeline_type='output')
                else:
                    pipeline.disable_guardrail(guardrail.name, pipeline_type='output')
            else:
                logger.warning(f"  Output guardrail not found: {guardrail.name}")
        
        # Update app state
        app.state.current_guardrail_settings = settings
        
        logger.info("✅ Guardrail settings updated successfully")
        return {"status": "success", "message": "Guardrail settings updated"}
        
    except Exception as e:
        logger.error(f"❌ Error updating guardrail settings: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to update guardrail settings: {str(e)}")


@app.get("/api/debug/test")
async def debug_test():
    """Debug endpoint to test basic functionality."""
    # Test ChatResponse serialization
    test_response = ChatResponse(
        content="This is a test message from the debug endpoint",
        blocked=False,
        warnings=["Test warning"],
        reasons=[],
        conversation_id="test-conversation-123",
        processing_details={"test": "details"}
    )
    return test_response


@app.post("/api/debug/chat")
async def debug_chat(
    message: ChatMessage,
    openai_adapter: Optional[OpenAIAdapter] = Depends(get_openai_adapter)
) -> dict:
    """Debug endpoint to test OpenAI integration without guardrails."""
    if not openai_adapter:
        return {
            "error": "OpenAI not configured",
            "content": "OpenAI adapter not available"
        }
    
    try:
        # Direct OpenAI call
        response = await openai_adapter.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message.content}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        raw_content = response.choices[0].message.content
        
        return {
            "raw_content": raw_content,
            "content_type": str(type(raw_content)),
            "content_length": len(raw_content) if raw_content else 0,
            "is_none": raw_content is None,
            "is_empty": raw_content == "",
            "response_object": str(response.choices[0].message)
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "type": str(type(e))
        }


@app.post("/api/preset")
async def load_preset(
    preset_data: dict,
    pipeline: GuardrailPipeline = Depends(get_pipeline)
) -> dict:
    """Load a preset configuration."""
    try:
        preset_name = preset_data.get("preset")
        if not preset_name:
            raise HTTPException(status_code=400, detail="Preset name is required")
        
        # Create new pipeline from preset
        new_pipeline = GuardrailPipeline.from_preset(preset_name)
        app.state.current_pipeline = new_pipeline
        
        # Update guardrail settings
        status = new_pipeline.get_guardrail_status()
        app.state.current_guardrail_settings = GuardrailSettings(
            input_guardrails=[
                GuardrailConfig(name=info["name"], enabled=info["enabled"])
                for info in status.get("input_guardrails", [])
            ],
            output_guardrails=[
                GuardrailConfig(name=info["name"], enabled=info["enabled"])
                for info in status.get("output_guardrails", [])
            ],
            preset=preset_name,
            use_conversation_aware_prompt_injection=False
        )
        
        logger.info(f"✅ Loaded preset: {preset_name}")
        return {"status": "success", "message": f"Preset '{preset_name}' loaded"}
        
    except Exception as e:
        logger.error(f"❌ Error loading preset: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load preset: {str(e)}")


@app.get("/api/presets")
async def get_available_presets() -> dict:
    """Get available preset configurations."""
    presets = GuardrailPipeline.get_available_presets()
    return {"presets": presets}


@app.get("/api/audit_log")
async def get_audit_log() -> dict:
    """Get recent audit log entries."""
    try:
        if not audit.is_enabled():
            return {
                "status": "disabled",
                "recent_records": [],
                "message": "Audit logging is not enabled"
            }
        
        # Get recent records using the query function
        audit_file = getattr(app.state, 'audit_log_file', None)
        if audit_file:
            recent_records = audit.query(last_hour=True, destination=audit_file)
        else:
            recent_records = []
        
        return {
            "status": "enabled",
            "recent_records": recent_records,
            "total_records": len(recent_records)
        }
        
    except Exception as e:
        logger.error(f"Error getting audit log: {e}")
        return {
            "status": "error",
            "recent_records": [],
            "error": str(e)
        }


@app.post("/api/conversation/reset")
async def reset_conversation() -> dict:
    """Reset the current conversation."""
    app.state.current_conversation = None
    logger.info("✅ Conversation reset")
    return {"status": "success", "message": "Conversation reset"}


@app.get("/api/conversation")
async def get_conversation_info() -> dict:
    """Get information about the current conversation."""
    conversation = getattr(app.state, 'current_conversation', None)
    
    if not conversation:
        return {
            "active": False,
            "conversation_id": None,
            "turn_count": 0
        }
    
    return {
        "active": True,
        "conversation_id": conversation.conversation_id,
        "turn_count": len(conversation.turns),
        "last_activity": conversation.last_activity.isoformat() if conversation.last_activity else None
    }


@app.get("/api/test")
async def test_endpoint() -> dict:
    """Simple test endpoint to verify API is working."""
    return {
        "status": "ok",
        "message": "API is working correctly",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/debug/chat")
async def debug_chat_endpoint(message: ChatMessage) -> dict:
    """Debug endpoint to test chat response format."""
    return {
        "content": f"Debug response: You said '{message.content}'",
        "blocked": False,
        "warnings": ["This is a debug endpoint"],
        "reasons": [],
        "conversation_id": "debug-conversation",
        "processing_details": {"debug": True}
    }


@app.get("/api/performance")
async def get_performance_metrics(
    health_monitor: Optional[HealthMonitor] = Depends(get_health_monitor)
) -> dict:
    """Get performance metrics from health monitor."""
    if not health_monitor:
        return {
            "status": "unavailable",
            "message": "Health monitor not initialized"
        }
    
    # Get performance metrics from health monitor
    metrics = health_monitor.performance_metrics
    
    return {
        "status": "ok",
        "metrics": {
            "total_requests": metrics.get("total_requests", 0),
            "blocked_requests": metrics.get("blocked_requests", 0),
            "avg_response_time_ms": round(metrics.get("avg_response_time_ms", 0), 2),
            "peak_response_time_ms": round(metrics.get("peak_response_time_ms", 0), 2),
            "last_request_time": metrics.get("last_request_time"),
            "block_rate": round(metrics.get("blocked_requests", 0) / max(metrics.get("total_requests", 1), 1) * 100, 2)
        }
    }


@app.get("/api/guardrails/details")
async def get_guardrail_details(
    pipeline: GuardrailPipeline = Depends(get_pipeline)
) -> dict:
    """Get detailed information about all available guardrails."""
    
    # Define guardrail descriptions for better UI
    guardrail_descriptions = {
        # AI-powered guardrails
        "ai_pii_detection": {
            "display_name": "AI PII Detection",
            "description": "Uses AI to detect personally identifiable information like SSNs, credit cards, emails",
            "category": "ai",
            "type": "privacy"
        },
        "ai_toxicity_detection": {
            "display_name": "AI Toxicity Detection", 
            "description": "AI-powered detection of hate speech, threats, and toxic content",
            "category": "ai",
            "type": "safety"
        },
        "ai_code_generation": {
            "display_name": "AI Code Generation Detection",
            "description": "Detects attempts to generate potentially malicious code",
            "category": "ai",
            "type": "security"
        },
        "prompt_injection": {
            "display_name": "Prompt Injection Detection",
            "description": "Detects attempts to manipulate AI behavior through prompt injection",
            "category": "ai",
            "type": "security"
        },
        
        # Simple/local guardrails
        "simple_pii_detection": {
            "display_name": "Regex PII Detection",
            "description": "Fast regex-based detection of common PII patterns",
            "category": "local",
            "type": "privacy"
        },
        "simple_toxicity_detection": {
            "display_name": "Keyword Toxicity Detection",
            "description": "Fast keyword-based detection of inappropriate content",
            "category": "local",
            "type": "safety"
        },
        "simple_code_generation": {
            "display_name": "Pattern Code Detection",
            "description": "Pattern-based detection of code generation attempts",
            "category": "local",
            "type": "security"
        },
        
        # Pattern-based guardrails
        "keyword_block": {
            "display_name": "Keyword Blocker",
            "description": "Blocks specific keywords or phrases",
            "category": "local",
            "type": "guardrail"
        },
        "regex_guardrail": {
            "display_name": "Regex Guardrail",
            "description": "Guards against content matching regex patterns",
            "category": "local",
            "type": "guardrail"
        },
        "url_guardrail": {
            "display_name": "URL Guardrail",
            "description": "Blocks or allows specific domains and URLs",
            "category": "local",
            "type": "guardrail"
        },
        "length_guardrail": {
            "display_name": "Length Limiter",
            "description": "Enforces minimum and maximum message lengths",
            "category": "local",
            "type": "guardrail"
        },
        "topic_guardrail": {
            "display_name": "Topic Guardrail",
            "description": "AI-based guarding against specific topics or themes",
            "category": "ai",
            "type": "guardrail"
        }
    }
    
    # Get current pipeline status
    status = pipeline.get_guardrail_status()
    
    # Enhance guardrail info with descriptions
    enhanced_info = {
        "input_guardrails": [],
        "output_guardrails": []
    }
    
    for guardrail in status.get("input_guardrails", []):
        name = guardrail["name"]
        # Remove suffixes like _output, _input for matching
        base_name = name.replace("_output", "").replace("_input", "")
        
        # Try to find description by type first, then by name
        guardrail_type = guardrail.get("type", "")
        description_info = guardrail_descriptions.get(guardrail_type) or guardrail_descriptions.get(base_name, {})
        
        enhanced_guardrail = {
            **guardrail,
            "display_name": description_info.get("display_name", name.replace("_", " ").title()),
            "description": description_info.get("description", "Custom guardrail"),
            "category": description_info.get("category", "custom"),
            "guardrail_type": description_info.get("type", "guardrail")
        }
        enhanced_info["input_guardrails"].append(enhanced_guardrail)
    
    for guardrail in status.get("output_guardrails", []):
        name = guardrail["name"]
        # Remove suffixes like _output, _input for matching
        base_name = name.replace("_output", "").replace("_input", "")
        
        # Try to find description by type first, then by name
        guardrail_type = guardrail.get("type", "")
        description_info = guardrail_descriptions.get(guardrail_type) or guardrail_descriptions.get(base_name, {})
        
        enhanced_guardrail = {
            **guardrail,
            "display_name": description_info.get("display_name", name.replace("_", " ").title()),
            "description": description_info.get("description", "Custom guardrail"),
            "category": description_info.get("category", "custom"),
            "guardrail_type": description_info.get("type", "guardrail")
        }
        enhanced_info["output_guardrails"].append(enhanced_guardrail)
    
    return enhanced_info


# Serve frontend files
try:
    frontend_path = Path(__file__).parent.parent / "frontend" / "build"
    if frontend_path.exists():
        app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
        
        @app.get("/{full_path:path}")
        async def serve_frontend(full_path: str):
            """Serve frontend files."""
            file_path = frontend_path / full_path
            if file_path.exists() and file_path.is_file():
                return FileResponse(str(file_path))
            return FileResponse(str(frontend_path / "index.html"))
        
        @app.get("/")
        async def root():
            """Serve the main page."""
            return FileResponse(str(frontend_path / "index.html"))
            
    else:
        logger.warning("Frontend build directory not found. API-only mode.")
        
except Exception as e:
    logger.warning(f"Could not mount frontend: {e}")




@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for better error reporting."""
    logger.error(f"Unhandled exception: {exc}")
    logger.error(f"Full traceback: {traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting backend on HTTP...")
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[str(Path(__file__).parent)]
    )