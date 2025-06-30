#!/usr/bin/env python3
"""
Debug script for QA team to troubleshoot web demo startup issues.
Run this script to diagnose and fix common startup problems.
"""

import subprocess
import sys
import os
import time
import requests
from pathlib import Path

def run_command(cmd, description):
    """Run a command and report results."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"   ✅ Success")
            if result.stdout.strip():
                print(f"   📝 Output: {result.stdout.strip()}")
        else:
            print(f"   ❌ Failed (exit code: {result.returncode})")
            if result.stderr.strip():
                print(f"   🚨 Error: {result.stderr.strip()}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"   ⏰ Timeout after 10 seconds")
        return False
    except Exception as e:
        print(f"   💥 Exception: {e}")
        return False

def check_port(port):
    """Check if a port is in use."""
    print(f"🔍 Checking port {port}...")
    result = subprocess.run(f"lsof -ti:{port}", shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        pids = result.stdout.strip().split('\n')
        print(f"   ⚠️  Port {port} is in use by PIDs: {', '.join(pids)}")
        return False
    else:
        print(f"   ✅ Port {port} is free")
        return True

def kill_port_processes(port):
    """Kill processes using a specific port."""
    print(f"🔪 Killing processes on port {port}...")
    result = subprocess.run(f"lsof -ti:{port}", shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        pids = result.stdout.strip().split('\n')
        for pid in pids:
            subprocess.run(f"kill -9 {pid}", shell=True, capture_output=True)
            print(f"   💀 Killed PID {pid}")
        time.sleep(2)
        return True
    else:
        print(f"   ℹ️  No processes found on port {port}")
        return True

def test_backend_startup():
    """Test if backend can start successfully."""
    print(f"🧪 Testing backend startup...")
    
    backend_dir = Path(__file__).parent / "backend"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).parent.parent.parent / "src")
    
    try:
        # Start backend in background
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env
        )
        
        # Wait up to 15 seconds for startup
        for i in range(15):
            try:
                response = requests.get("http://127.0.0.1:8000/api/health", timeout=2)
                if response.status_code == 200:
                    print(f"   ✅ Backend started successfully (took {i+1}s)")
                    print(f"   📊 Health response: {response.json()}")
                    process.terminate()
                    process.wait(timeout=5)
                    return True
            except:
                pass
            time.sleep(1)
        
        print(f"   ❌ Backend failed to respond within 15 seconds")
        
        # Get process output
        try:
            stdout, stderr = process.communicate(timeout=2)
            if stdout:
                print(f"   📝 Stdout: {stdout.decode()}")
            if stderr:
                print(f"   🚨 Stderr: {stderr.decode()}")
        except:
            pass
            
        process.terminate()
        process.wait(timeout=5)
        return False
        
    except Exception as e:
        print(f"   💥 Exception during startup test: {e}")
        return False

def main():
    """Main troubleshooting routine."""
    print("🔧 STINGER WEB DEMO TROUBLESHOOTING")
    print("=" * 50)
    
    # Step 1: Check Python environment
    print("\n📋 STEP 1: Python Environment")
    run_command("python3 --version", "Checking Python version")
    run_command("which python3", "Finding Python executable")
    
    # Step 2: Check Stinger installation
    print("\n📋 STEP 2: Stinger Installation")
    src_path = Path(__file__).parent.parent.parent / "src"
    print(f"🔍 Checking Stinger source at: {src_path}")
    if src_path.exists():
        print("   ✅ Stinger source directory found")
        stinger_init = src_path / "stinger" / "__init__.py"
        if stinger_init.exists():
            print("   ✅ Stinger package structure looks good")
        else:
            print("   ❌ Stinger package structure missing")
    else:
        print("   ❌ Stinger source directory not found")
    
    # Step 3: Check dependencies
    print("\n📋 STEP 3: Dependencies")
    dependencies = ["fastapi", "uvicorn", "requests", "yaml", "openai"]
    for dep in dependencies:
        cmd = f"python3 -c \"import {dep}; print('{dep} version:', getattr({dep}, '__version__', 'unknown'))\""
        run_command(cmd, f"Checking {dep}")
    
    # Step 4: Check API key
    print("\n📋 STEP 4: API Key Configuration")
    if os.getenv('OPENAI_API_KEY'):
        key_preview = os.getenv('OPENAI_API_KEY')[:10] + "..." if len(os.getenv('OPENAI_API_KEY')) > 10 else os.getenv('OPENAI_API_KEY')
        print(f"   ✅ OPENAI_API_KEY found: {key_preview}")
    else:
        print("   ⚠️  OPENAI_API_KEY not set (demo will use mock responses)")
    
    # Step 5: Check and clean ports
    print("\n📋 STEP 5: Port Management")
    ports_free = True
    for port in [8000, 3000]:
        if not check_port(port):
            ports_free = False
    
    if not ports_free:
        print("\n🔧 Cleaning up port conflicts...")
        for port in [8000, 3000]:
            kill_port_processes(port)
        
        # Verify cleanup
        print("\n🔍 Verifying port cleanup...")
        for port in [8000, 3000]:
            check_port(port)
    
    # Step 6: Test backend startup
    print("\n📋 STEP 6: Backend Startup Test")
    backend_works = test_backend_startup()
    
    # Final summary
    print("\n🎯 TROUBLESHOOTING SUMMARY")
    print("=" * 30)
    if backend_works:
        print("✅ Backend can start successfully!")
        print("💡 Try running: python3 start_demo.py")
    else:
        print("❌ Backend startup failed")
        print("💡 Check the error messages above")
        print("💡 Try running the individual commands manually")
    
    print("\n📚 Additional Resources:")
    print("   - Demo README: demos/web_demo/README.md")
    print("   - Quick start: demos/web_demo/QUICK_START.md")
    print("   - Setup guide: demos/web_demo/SETUP.md")

if __name__ == "__main__":
    main()