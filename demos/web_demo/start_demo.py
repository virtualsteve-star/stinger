#!/usr/bin/env python3
"""
Stinger Web Demo Startup Script

This script provides comprehensive demo startup with clear status reporting
and addresses frontend build performance issues.

Usage:
    python start_demo.py                  # Start both services with status updates
    python start_demo.py --backend-only   # Start only backend for API testing
    python start_demo.py --fresh-build    # Force clean frontend build
    python start_demo.py --no-wait        # Don't wait for user input

Features:
- Clear status reporting with timestamps
- Frontend build optimization 
- Process management and cleanup
- Comprehensive health checking
- API key status validation
"""

import subprocess
import sys
import os
import time
import argparse
import signal
import requests
from pathlib import Path
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings for self-signed certificates
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class DemoStarter:
    def __init__(self, args):
        self.demo_dir = Path(__file__).parent
        self.backend_dir = self.demo_dir / "backend"
        self.frontend_dir = self.demo_dir / "frontend"
        self.backend_process = None
        self.frontend_process = None
        self.args = args
        self.api_key_available = bool(os.getenv('OPENAI_API_KEY'))
        
    def log(self, message, level="INFO"):
        """Log a message with timestamp and clear status."""
        timestamp = time.strftime("%H:%M:%S")
        icons = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "ERROR": "❌", 
            "WARNING": "⚠️",
            "WORKING": "🔄",
            "ROCKET": "🚀"
        }
        icon = icons.get(level, "ℹ️")
        print(f"[{timestamp}] {icon} {message}")
        
    def print_header(self, title):
        """Print a formatted section header."""
        print("\n" + "="*70)
        print(f" {title}")
        print("="*70)
        
    def cleanup_existing_processes(self):
        """Kill any existing processes on demo ports."""
        self.log("Cleaning up existing processes...", "WORKING")
        
        for port in [3000, 8000]:
            try:
                result = subprocess.run(f"lsof -ti:{port}", 
                                      shell=True, capture_output=True, text=True)
                if result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        subprocess.run(f"kill -9 {pid}", shell=True, capture_output=True)
                        self.log(f"Killed existing process {pid} on port {port}")
            except:
                pass
        time.sleep(2)
        
    def check_system_requirements(self):
        """Check all system requirements."""
        self.log("Checking system requirements...", "WORKING")
        
        # Python version
        if sys.version_info < (3, 8):
            self.log("Python 3.8+ required", "ERROR")
            return False
        self.log(f"✓ Python {sys.version.split()[0]}")
        
        # Stinger installation
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
            from stinger.core.api_key_manager import get_openai_key
            self.log("✓ Stinger library available")
        except ImportError as e:
            self.log(f"✗ Stinger not found: {e}", "ERROR")
            return False
            
        # FastAPI
        try:
            import fastapi
            import uvicorn
            self.log("✓ FastAPI and Uvicorn available")
        except ImportError:
            self.log("✗ FastAPI/Uvicorn missing - run: pip install fastapi uvicorn", "ERROR")
            return False
            
        # Node.js (for frontend)
        if not self.args.backend_only:
            try:
                result = subprocess.run(["node", "--version"], capture_output=True, text=True)
                if result.returncode == 0:
                    node_version = result.stdout.strip()
                    self.log(f"✓ Node.js {node_version}")
                else:
                    self.log("✗ Node.js not found", "ERROR")
                    return False
            except FileNotFoundError:
                self.log("✗ Node.js not installed", "ERROR")
                return False
                
            # npm
            try:
                result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
                if result.returncode == 0:
                    npm_version = result.stdout.strip()
                    self.log(f"✓ npm {npm_version}")
                else:
                    self.log("✗ npm not found", "ERROR")
                    return False
            except FileNotFoundError:
                self.log("✗ npm not installed", "ERROR")
                return False
        
        return True
        
    def setup_ssl_certificates(self):
        """Ensure SSL certificates exist."""
        cert_file = self.backend_dir / "cert.pem"
        key_file = self.backend_dir / "key.pem"
        
        if cert_file.exists() and key_file.exists():
            self.log("✓ SSL certificates found")
            return True
            
        self.log("Generating SSL certificates...", "WORKING")
        try:
            setup_script = self.backend_dir / "setup_ssl.py"
            result = subprocess.run([sys.executable, str(setup_script)], 
                                  cwd=self.backend_dir, capture_output=True, text=True)
            if result.returncode == 0:
                self.log("✓ SSL certificates generated", "SUCCESS")
                return True
            else:
                self.log(f"✗ Certificate generation failed: {result.stderr}", "ERROR")
                return False
        except Exception as e:
            self.log(f"✗ Certificate setup error: {e}", "ERROR")
            return False
            
    def check_api_key_status(self):
        """Check and report API key configuration."""
        self.log("Checking API key configuration...", "WORKING")
        
        if self.api_key_available:
            key = os.getenv('OPENAI_API_KEY')
            masked_key = f"{key[:8]}...{key[-4:]}" if key else "unknown"
            self.log(f"✓ OpenAI API key configured: {masked_key}", "SUCCESS")
            return True
        else:
            self.log("⚠️ No OpenAI API key found - demo will run in mock mode", "WARNING")
            self.log("💡 Set OPENAI_API_KEY environment variable for real LLM responses")
            return False
            
    def optimize_frontend_build(self):
        """Address frontend build performance issues."""
        if self.args.backend_only:
            return True
            
        self.log("Optimizing frontend build configuration...", "WORKING")
        
        # Create .env.local with build optimizations
        env_file = self.frontend_dir / ".env.local"
        optimizations = [
            "# Build performance optimizations",
            "FAST_REFRESH=true",
            "CHOKIDAR_USEPOLLING=false", 
            "TSC_COMPILE_ON_ERROR=true",
            "ESLINT_NO_DEV_ERRORS=true",
            "GENERATE_SOURCEMAP=false"
        ]
        
        if self.args.fresh_build or not env_file.exists():
            with open(env_file, 'w') as f:
                f.write('\n'.join(optimizations) + '\n')
            self.log("✓ Frontend build optimizations configured")
            
        # Check if fresh build needed
        if self.args.fresh_build:
            build_dir = self.frontend_dir / "build"
            if build_dir.exists():
                import shutil
                shutil.rmtree(build_dir)
                self.log("✓ Cleared build cache for fresh build")
                
        # Check frontend dependencies
        node_modules = self.frontend_dir / "node_modules"
        package_lock = self.frontend_dir / "package-lock.json"
        package_json = self.frontend_dir / "package.json"
        
        deps_need_install = False
        if not node_modules.exists() or not package_lock.exists():
            deps_need_install = True
        else:
            try:
                lock_time = package_lock.stat().st_mtime
                json_time = package_json.stat().st_mtime
                if json_time > lock_time:
                    deps_need_install = True
            except:
                deps_need_install = True
                
        if deps_need_install:
            self.log("Installing/updating frontend dependencies...", "WORKING")
            result = subprocess.run(["npm", "install"], 
                                  cwd=self.frontend_dir, 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.log("✓ Frontend dependencies installed")
            else:
                self.log(f"✗ npm install failed: {result.stderr}", "ERROR")
                return False
        else:
            self.log("✓ Frontend dependencies up to date")
            
        return True
        
    def start_backend(self):
        """Start the backend server with proper monitoring."""
        self.log("Starting backend server...", "WORKING")
        
        # Set up environment
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).parent.parent.parent / "src")
        
        try:
            self.backend_process = subprocess.Popen(
                [sys.executable, "main.py"],
                cwd=self.backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
            
            self.log(f"Backend process started (PID: {self.backend_process.pid})")
            
            # Wait for backend to be ready with status updates
            self.log("Waiting for backend to initialize...", "WORKING")
            for attempt in range(30):
                try:
                    response = requests.get("https://localhost:8000/api/health", 
                                          verify=False, timeout=2)
                    if response.status_code == 200:
                        data = response.json()
                        enabled = data.get('enabled_guardrails', 0)
                        total = data.get('total_guardrails', 0)
                        self.log(f"Backend ready - {enabled}/{total} guardrails active", "SUCCESS")
                        
                        # Test API key integration
                        if self.api_key_available:
                            self.log("✓ Real LLM responses available", "SUCCESS")
                        else:
                            self.log("⚠️ Running in mock mode", "WARNING")
                            
                        return True
                except:
                    if attempt % 5 == 0 and attempt > 0:
                        self.log(f"Still waiting for backend... ({attempt}s)")
                    time.sleep(1)
                    
            self.log("Backend failed to start within 30 seconds", "ERROR")
            self.show_backend_logs()
            return False
            
        except Exception as e:
            self.log(f"Failed to start backend: {e}", "ERROR")
            return False
            
    def start_frontend(self):
        """Start the frontend server with build progress monitoring."""
        if self.args.backend_only:
            return True
            
        self.log("Starting frontend server...", "WORKING")
        self.log("⏱️ Initial build may take 60-90 seconds...")
        
        # Set up environment with optimizations
        env = os.environ.copy()
        env.update({
            "HTTPS": "true",
            "SSL_CRT_FILE": "../backend/cert.pem", 
            "SSL_KEY_FILE": "../backend/key.pem",
            "BROWSER": "none"  # Don't auto-open browser
        })
        
        try:
            self.frontend_process = subprocess.Popen(
                ["npm", "start"],
                cwd=self.frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, 
                text=True,
                env=env
            )
            
            self.log(f"Frontend process started (PID: {self.frontend_process.pid})")
            
            # Wait for frontend with progress updates
            for attempt in range(120):  # 2 minutes max
                try:
                    if attempt % 15 == 0 and attempt > 0:
                        self.log(f"Frontend still building... ({attempt}s)")
                        
                    response = requests.get("https://localhost:3000", 
                                          verify=False, timeout=2)
                    if response.status_code == 200:
                        self.log("Frontend ready", "SUCCESS")
                        return True
                except:
                    time.sleep(1)
                    
            self.log("Frontend failed to start within 2 minutes", "ERROR")
            return False
            
        except Exception as e:
            self.log(f"Failed to start frontend: {e}", "ERROR")
            return False
            
    def test_demo_functionality(self):
        """Run a quick functionality test."""
        self.log("Testing demo functionality...", "WORKING")
        
        try:
            # Test health endpoint
            response = requests.get("https://localhost:8000/api/health", verify=False, timeout=5)
            if response.status_code != 200:
                self.log("✗ Health check failed", "ERROR")
                return False
                
            # Test chat endpoint
            response = requests.post("https://localhost:8000/api/chat",
                                   json={"content": "Hello test"},
                                   verify=False, timeout=10)
            if response.status_code != 200:
                self.log("✗ Chat API test failed", "ERROR")
                return False
                
            data = response.json()
            required_fields = ["content", "blocked", "warnings", "conversation_id"]
            for field in required_fields:
                if field not in data:
                    self.log(f"✗ Missing response field: {field}", "ERROR")
                    return False
                    
            self.log("✓ Core functionality verified", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"✗ Functionality test failed: {e}", "ERROR")
            return False
            
    def show_backend_logs(self):
        """Show recent backend logs for debugging."""
        if self.backend_process:
            try:
                stdout, stderr = self.backend_process.communicate(timeout=1)
                if stderr:
                    self.log("Recent backend errors:", "ERROR")
                    print(stderr[-1000:])  # Last 1000 chars
            except:
                pass
                
    def show_demo_urls(self):
        """Display demo access information."""
        self.print_header("🎮 DEMO ACCESS INFORMATION")
        
        self.log("Backend API:", "SUCCESS")
        self.log("   https://localhost:8000/api/docs  (Interactive API docs)")
        self.log("   https://localhost:8000/api/health (Health check)")
        
        if not self.args.backend_only:
            self.log("Frontend Web Interface:", "SUCCESS") 
            self.log("   https://localhost:3000  (Main demo interface)")
            
        if self.api_key_available:
            self.log("✅ Real LLM responses enabled", "SUCCESS")
        else:
            self.log("💡 To enable real LLM responses:", "INFO")
            self.log("   export OPENAI_API_KEY='your-key-here'")
            self.log("   Then restart the backend")
            
    def show_build_performance_info(self):
        """Show build performance tips."""
        if not self.args.backend_only:
            self.print_header("⚡ BUILD PERFORMANCE NOTES")
            self.log("Why the initial build takes time:", "INFO")
            self.log("   - React compiles and optimizes all components")
            self.log("   - TypeScript checking and bundling")
            self.log("   - CSS processing and optimization")
            self.log("")
            self.log("Performance improvements implemented:", "SUCCESS")
            self.log("   ✓ Fast refresh enabled for quick hot reloads")
            self.log("   ✓ File polling disabled (uses native file watching)")
            self.log("   ✓ Source maps disabled for faster builds")
            self.log("   ✓ ESLint warnings don't block compilation")
            self.log("")
            self.log("Subsequent changes should be much faster!", "SUCCESS")
            
    def cleanup(self):
        """Clean up all processes."""
        self.log("Shutting down demo services...", "WORKING")
        
        processes = [
            ("Frontend", self.frontend_process),
            ("Backend", self.backend_process)
        ]
        
        for name, process in processes:
            if process:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                    self.log(f"✓ {name} stopped")
                except subprocess.TimeoutExpired:
                    process.kill()
                    self.log(f"✓ {name} force stopped")
                except:
                    pass
                    
        # Final port cleanup
        self.cleanup_existing_processes()
        
    def run_demo(self):
        """Main demo startup routine."""
        self.print_header("🚀 STINGER WEB DEMO STARTUP")
        
        try:
            # System checks
            if not self.check_system_requirements():
                return False
                
            # Clean existing processes
            self.cleanup_existing_processes()
            
            # SSL setup
            if not self.setup_ssl_certificates():
                return False
                
            # API key status
            self.check_api_key_status()
            
            # Frontend optimization
            if not self.optimize_frontend_build():
                return False
                
            # Start services
            self.print_header("🔧 STARTING SERVICES")
            
            if not self.start_backend():
                return False
                
            if not self.start_frontend():
                return False
                
            # Test functionality
            if not self.test_demo_functionality():
                self.log("⚠️ Some functionality tests failed", "WARNING")
                
            # Success!
            self.print_header("🎉 DEMO STARTED SUCCESSFULLY")
            self.show_demo_urls()
            self.show_build_performance_info()
            
            self.log("Press Ctrl+C to stop all services", "INFO")
            
            # Keep running or exit in test mode
            if self.args.test:
                self.log("Test mode - stopping services and exiting...", "INFO")
                return True
            else:
                self.log("Services are now running. Use Ctrl+C to stop.", "INFO")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    self.log("Demo stopped by user", "INFO")
                
            return True
            
        except Exception as e:
            self.log(f"Demo startup error: {e}", "ERROR")
            return False
        finally:
            self.cleanup()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Start Stinger Web Demo with comprehensive status reporting")
    parser.add_argument("--backend-only", action="store_true", 
                       help="Start only the backend API server")
    parser.add_argument("--fresh-build", action="store_true",
                       help="Force a clean frontend build")
    parser.add_argument("--no-wait", action="store_true",
                       help="Don't wait for user confirmation")
    parser.add_argument("--test", action="store_true",
                       help="Test startup and exit (don't keep running)")
    
    args = parser.parse_args()
    
    starter = DemoStarter(args)
    
    # Handle cleanup on exit
    def signal_handler(sig, frame):
        starter.cleanup()
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # User confirmation unless --no-wait
    if not args.no_wait:
        print("🚀 Stinger Web Demo Startup Script")
        print("=" * 50)
        print("This will start the demo with comprehensive status reporting.")
        print("")
        if args.backend_only:
            print("Mode: Backend API only")
        else:
            print("Mode: Full demo (backend + frontend)")
            print("Note: Initial frontend build may take 60-90 seconds")
        print("")
        
        response = input("Continue? (Y/n): ").strip().lower()
        if response and response not in ['y', 'yes']:
            print("Cancelled.")
            return 0
    
    success = starter.run_demo()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())