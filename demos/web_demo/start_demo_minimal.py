#!/usr/bin/env python3
"""Minimal Stinger Web Demo Startup"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("🚀 Starting Stinger Web Demo...")
    
    # Kill existing
    os.system("lsof -ti:8000 | xargs kill -9 2>/dev/null || true")
    
    # Set environment
    backend_dir = Path(__file__).parent / "backend"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).parent.parent.parent / "src")
    
    # Check API key
    if os.getenv('OPENAI_API_KEY'):
        print("✅ OpenAI API key found")
    else:
        print("⚠️  No OPENAI_API_KEY - will use mock responses")
    
    # Start backend
    print("🔄 Starting backend on http://127.0.0.1:8000")
    print("💡 Press Ctrl+C to stop")
    
    # Use os.system for simplicity - blocks until Ctrl+C
    try:
        os.chdir(backend_dir)
        os.environ.update(env)
        os.system("python3 main.py")
    except KeyboardInterrupt:
        print("\n🛑 Stopped")

if __name__ == "__main__":
    main()