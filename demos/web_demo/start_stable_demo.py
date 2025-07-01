#!/usr/bin/env python3
"""
Start the Stinger Web Demo in stable production mode.
This version builds and serves the frontend as static files to avoid memory issues.
"""

import os
import sys
import time
import subprocess
import signal
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class StableDemoRunner:
    def __init__(self):
        self.demo_dir = Path(__file__).parent
        self.frontend_dir = self.demo_dir / "frontend"
        self.backend_dir = self.demo_dir / "backend"
        self.processes = []
        
    def check_prerequisites(self):
        """Check if all prerequisites are met."""
        print("🔍 Checking prerequisites...")
        
        # Check Node.js
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            print(f"✅ Node.js: {result.stdout.strip()}")
        except FileNotFoundError:
            print("❌ Node.js not found. Please install Node.js 14+ first.")
            return False
            
        # Check npm
        try:
            result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
            print(f"✅ npm: {result.stdout.strip()}")
        except FileNotFoundError:
            print("❌ npm not found. Please install npm.")
            return False
            
        # Check Python
        print(f"✅ Python: {sys.version.split()[0]}")
        
        return True
        
    def install_dependencies(self):
        """Install all required dependencies."""
        print("\n📦 Installing dependencies...")
        
        # Install web demo server dependencies
        if not (self.demo_dir / "node_modules").exists():
            print("Installing production server dependencies...")
            subprocess.run(["npm", "install"], cwd=self.demo_dir, check=True)
            
        # Install frontend dependencies
        if not (self.frontend_dir / "node_modules").exists():
            print("Installing frontend dependencies...")
            subprocess.run(["npm", "install"], cwd=self.frontend_dir, check=True)
            
        # Install backend dependencies
        print("Checking backend dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      cwd=self.backend_dir, check=True)
        
    def build_frontend(self):
        """Build the frontend for production."""
        print("\n🔨 Building frontend (this may take a minute)...")
        
        build_path = self.frontend_dir / "build"
        if build_path.exists() and build_path.is_dir():
            # Check if build is recent (less than 1 hour old)
            index_file = build_path / "index.html"
            if index_file.exists():
                age = time.time() - index_file.stat().st_mtime
                if age < 3600:  # 1 hour
                    print("✅ Using existing build (less than 1 hour old)")
                    return True
                    
        # Build frontend
        env = os.environ.copy()
        env["GENERATE_SOURCEMAP"] = "false"
        
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd=self.frontend_dir,
            env=env,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("❌ Frontend build failed!")
            print(result.stderr)
            return False
            
        print("✅ Frontend built successfully")
        return True
        
    def start_backend(self):
        """Start the backend service."""
        print("\n🚀 Starting backend service...")
        
        # Set environment for backend
        env = os.environ.copy()
        env["DEMO_MODE"] = "true"
        
        # Start backend process
        backend_process = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=self.backend_dir,
            env=env
        )
        self.processes.append(backend_process)
        
        # Wait for backend to be ready
        print("⏳ Waiting for backend to start...")
        time.sleep(3)
        
        # Check if backend is running
        try:
            import requests
            response = requests.get("https://localhost:8000/api/health", verify=False)
            if response.status_code == 200:
                print("✅ Backend is running at https://localhost:8000")
                return True
        except:
            pass
            
        print("⚠️  Backend may not be fully ready yet, continuing...")
        return True
        
    def start_frontend_server(self):
        """Start the production frontend server."""
        print("\n🌐 Starting frontend server...")
        
        # Start production server
        frontend_process = subprocess.Popen(
            ["node", "serve-production.js"],
            cwd=self.demo_dir
        )
        self.processes.append(frontend_process)
        
        print("✅ Frontend server starting at https://localhost:3000")
        return True
        
    def run(self):
        """Run the complete demo setup."""
        print("🛡️  Stinger Web Demo - Stable Production Mode")
        print("=" * 50)
        
        if not self.check_prerequisites():
            return
            
        try:
            self.install_dependencies()
            
            if not self.build_frontend():
                print("\n❌ Failed to build frontend")
                return
                
            if not self.start_backend():
                print("\n❌ Failed to start backend")
                return
                
            if not self.start_frontend_server():
                print("\n❌ Failed to start frontend server")
                return
                
            print("\n" + "=" * 50)
            print("✅ Demo is running!")
            print("\n📋 Access the demo at: https://localhost:3000")
            print("📚 API documentation at: https://localhost:8000/api/docs")
            print("\n⚠️  Note: Accept the self-signed certificate warning in your browser")
            print("\nPress Ctrl+C to stop the demo")
            print("=" * 50)
            
            # Wait for interrupt
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down demo...")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            self.cleanup()
            
    def cleanup(self):
        """Clean up all processes."""
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                try:
                    process.kill()
                except:
                    pass
        print("✅ Demo stopped")

if __name__ == "__main__":
    runner = StableDemoRunner()
    runner.run()