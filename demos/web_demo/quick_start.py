#!/usr/bin/env python3
"""
Quick Demo Starter - Simple version that starts and exits

Usage:
    python3 quick_start.py                # Start both services
    python3 quick_start.py --backend-only # Backend only
    python3 quick_start.py --test         # Quick test and exit
"""

import subprocess
import sys
import os
import time
import argparse
import requests
from pathlib import Path
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def log(message, level="INFO"):
    """Simple logging with timestamp."""
    timestamp = time.strftime("%H:%M:%S")
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
    icon = icons.get(level, "ℹ️")
    print(f"[{timestamp}] {icon} {message}")

def cleanup_ports():
    """Kill processes on demo ports."""
    log("Cleaning up ports...")
    for port in [3000, 8000]:
        try:
            result = subprocess.run(f"lsof -ti:{port}", shell=True, capture_output=True, text=True)
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    subprocess.run(f"kill -9 {pid}", shell=True, capture_output=True)
                    log(f"Killed process {pid} on port {port}")
        except:
            pass
    time.sleep(1)

def start_backend():
    """Start backend and verify it's working."""
    log("Starting backend...")
    
    demo_dir = Path(__file__).parent
    backend_dir = demo_dir / "backend"
    
    # Set up environment
    env = os.environ.copy()
    env["PYTHONPATH"] = str(demo_dir.parent.parent / "src")
    
    # Start backend process
    process = subprocess.Popen(
        [sys.executable, "main.py"],
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )
    
    log(f"Backend process started (PID: {process.pid})")
    
    # Wait for it to be ready
    for attempt in range(30):
        try:
            response = requests.get("https://localhost:8000/api/health", verify=False, timeout=2)
            if response.status_code == 200:
                data = response.json()
                enabled = data.get('enabled_guardrails', 0)
                total = data.get('total_guardrails', 0)
                log(f"Backend ready - {enabled}/{total} guardrails", "SUCCESS")
                
                # Quick test
                test_response = requests.post("https://localhost:8000/api/chat",
                                            json={"content": "Hello test"},
                                            verify=False, timeout=5)
                if test_response.status_code == 200:
                    log("✓ Chat API working", "SUCCESS")
                    return process
                else:
                    log("✗ Chat API test failed", "ERROR")
                    return None
        except:
            if attempt % 5 == 0 and attempt > 0:
                log(f"Waiting for backend... ({attempt}s)")
            time.sleep(1)
    
    log("Backend failed to start", "ERROR")
    return None

def start_frontend():
    """Start frontend."""
    log("Starting frontend...")
    log("⏱️ This will take 60-90 seconds for initial build...")
    
    demo_dir = Path(__file__).parent
    frontend_dir = demo_dir / "frontend"
    
    # Create build optimizations
    env_file = frontend_dir / ".env.local"
    if not env_file.exists():
        optimizations = [
            "FAST_REFRESH=true",
            "CHOKIDAR_USEPOLLING=false",
            "GENERATE_SOURCEMAP=false",
            "ESLINT_NO_DEV_ERRORS=true"
        ]
        with open(env_file, 'w') as f:
            f.write('\n'.join(optimizations) + '\n')
        log("✓ Build optimizations configured")
    
    # Check dependencies
    if not (frontend_dir / "node_modules").exists():
        log("Installing frontend dependencies...")
        result = subprocess.run(["npm", "install"], cwd=frontend_dir, capture_output=True)
        if result.returncode != 0:
            log("npm install failed", "ERROR")
            return None
    
    # Start frontend
    env = os.environ.copy()
    env.update({
        "HTTPS": "true",
        "SSL_CRT_FILE": "../backend/cert.pem",
        "SSL_KEY_FILE": "../backend/key.pem",
        "BROWSER": "none"
    })
    
    process = subprocess.Popen(
        ["npm", "start"],
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )
    
    log(f"Frontend process started (PID: {process.pid})")
    
    # Wait for frontend
    for attempt in range(120):
        try:
            if attempt % 15 == 0 and attempt > 0:
                log(f"Frontend still building... ({attempt}s)")
            
            response = requests.get("https://localhost:3000", verify=False, timeout=2)
            if response.status_code == 200:
                log("Frontend ready", "SUCCESS")
                return process
        except:
            time.sleep(1)
    
    log("Frontend failed to start", "ERROR")
    return None

def main():
    parser = argparse.ArgumentParser(description="Quick Demo Starter")
    parser.add_argument("--backend-only", action="store_true", help="Backend only")
    parser.add_argument("--test", action="store_true", help="Quick test and exit")
    
    args = parser.parse_args()
    
    log("🚀 Quick Demo Starter")
    log("=" * 50)
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        log(f"✓ OpenAI API key: {api_key[:8]}...{api_key[-4:]}", "SUCCESS")
    else:
        log("⚠️ No API key - running in mock mode", "WARNING")
    
    # Cleanup
    cleanup_ports()
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        log("Failed to start backend", "ERROR")
        return 1
    
    # Start frontend unless backend-only
    frontend_process = None
    if not args.backend_only:
        frontend_process = start_frontend()
        if not frontend_process:
            log("Failed to start frontend", "ERROR")
            backend_process.terminate()
            return 1
    
    # Show URLs
    log("=" * 50)
    log("🎉 Demo started successfully!", "SUCCESS")
    log("Backend: https://localhost:8000/api/docs")
    if not args.backend_only:
        log("Frontend: https://localhost:3000")
    
    if args.test:
        log("Test mode - stopping services...")
        if frontend_process:
            frontend_process.terminate()
        backend_process.terminate()
        log("Services stopped", "SUCCESS")
        return 0
    
    log("Services are running. Use Ctrl+C to stop or check PIDs above.")
    log("For build performance: subsequent starts will be much faster!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())