#!/usr/bin/env python3
"""
Stinger Web Demo Startup Script

This script helps you get the Stinger Web Demo running quickly by:
1. Checking all dependencies
2. Setting up SSL certificates
3. Starting the backend server
4. Providing instructions for the frontend

Usage:
    python start_demo.py
"""

import subprocess
import sys
import os
import time
from pathlib import Path


def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)


def print_status(message, status="info"):
    """Print a status message with icon."""
    icons = {
        "success": "✅",
        "error": "❌", 
        "warning": "⚠️",
        "info": "ℹ️"
    }
    print(f"{icons.get(status, 'ℹ️')} {message}")


def check_dependencies():
    """Check if all required dependencies are available."""
    print_header("CHECKING DEPENDENCIES")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print_status("Python 3.8+ required", "error")
        return False
    print_status(f"Python {sys.version.split()[0]} ✓", "success")
    
    # Check Stinger installation
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
        import stinger
        print_status("Stinger installed ✓", "success")
    except ImportError:
        print_status("Stinger not found - please install from project root", "error")
        return False
    
    # Check FastAPI
    try:
        import fastapi
        print_status("FastAPI available ✓", "success")
    except ImportError:
        print_status("FastAPI not installed - run: pip install fastapi uvicorn", "error")
        return False
    
    # Check Node.js (optional)
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print_status(f"Node.js {result.stdout.strip()} ✓", "success")
        else:
            print_status("Node.js not found (required for frontend)", "warning")
    except FileNotFoundError:
        print_status("Node.js not found (required for frontend)", "warning")
    
    return True


def setup_ssl():
    """Set up SSL certificates if needed."""
    print_header("SSL CERTIFICATE SETUP")
    
    backend_dir = Path(__file__).parent / "backend"
    cert_file = backend_dir / "cert.pem"
    key_file = backend_dir / "key.pem"
    
    if cert_file.exists() and key_file.exists():
        print_status("SSL certificates already exist ✓", "success")
        return True
    
    print_status("Generating SSL certificates...", "info")
    
    try:
        setup_script = backend_dir / "setup_ssl.py"
        result = subprocess.run([sys.executable, str(setup_script)], 
                              cwd=backend_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            print_status("SSL certificates generated ✓", "success")
            return True
        else:
            print_status(f"SSL setup failed: {result.stderr}", "error")
            print_status("Will run with HTTP instead", "warning")
            return False
    except Exception as e:
        print_status(f"SSL setup error: {e}", "error")
        print_status("Will run with HTTP instead", "warning")
        return False


def start_backend():
    """Start the FastAPI backend server."""
    print_header("STARTING BACKEND SERVER")
    
    backend_dir = Path(__file__).parent / "backend"
    main_script = backend_dir / "main.py"
    
    if not main_script.exists():
        print_status("Backend main.py not found", "error")
        return False
    
    print_status("Starting FastAPI backend...", "info")
    print_status("Backend will be available at: https://localhost:8000", "info")
    print_status("API documentation: https://localhost:8000/api/docs", "info")
    print("")
    print_status("Press Ctrl+C to stop the server", "warning")
    print("")
    
    try:
        # Start the backend server
        subprocess.run([sys.executable, str(main_script)], cwd=backend_dir)
    except KeyboardInterrupt:
        print_status("\nBackend server stopped", "info")
    except Exception as e:
        print_status(f"Backend failed to start: {e}", "error")
        return False
    
    return True


def show_frontend_instructions():
    """Show instructions for starting the frontend."""
    print_header("FRONTEND SETUP INSTRUCTIONS")
    
    frontend_dir = Path(__file__).parent / "frontend"
    
    print("To complete the demo setup, open a new terminal and run:")
    print("")
    print(f"  cd {frontend_dir}")
    print("  npm install")
    print("  npm start")
    print("")
    print("The frontend will be available at: https://localhost:3000")
    print("")
    print_status("Frontend setup is optional - the backend API works standalone", "info")


def main():
    """Main startup routine."""
    print_header("STINGER WEB DEMO STARTUP")
    print("🚀 Welcome to the Stinger Guardrails Web Demo!")
    print("")
    print("This script will help you get the demo running quickly.")
    
    # Check dependencies
    if not check_dependencies():
        print_status("Dependency check failed - please resolve issues above", "error")
        return 1
    
    # Setup SSL
    ssl_success = setup_ssl()
    
    # Show frontend instructions
    show_frontend_instructions()
    
    # Ask user if they want to start backend
    print_header("STARTING DEMO")
    response = input("Start the backend server now? (y/N): ").lower().strip()
    
    if response in ['y', 'yes']:
        # Start backend
        if not start_backend():
            return 1
    else:
        print_status("To start manually, run:", "info")
        print(f"  cd {Path(__file__).parent / 'backend'}")
        print("  python main.py")
    
    print_header("DEMO READY")
    print("🎉 Stinger Web Demo is ready!")
    print("")
    print("Quick test commands:")
    print("  curl https://localhost:8000/api/health")
    print("  curl https://localhost:8000/api/guardrails")
    print("")
    print("Enjoy exploring Stinger's guardrail capabilities!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())