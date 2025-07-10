#!/usr/bin/env python3
"""Start the Stinger Web Demo"""

import os
import sys

def main():
    # Check for CI mode
    ci_mode = "--ci" in sys.argv
    detached_mode = "--detached" in sys.argv or "--background" in sys.argv
    
    # Kill any existing backend
    os.system("lsof -ti:8000 | xargs kill -9 2>/dev/null || true")
    
    print("🚀 Starting Stinger Web Demo")
    
    # Change to backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), "backend")
    os.chdir(backend_dir)
    
    if detached_mode:
        # Run in background/detached mode
        import subprocess
        log_file = "/tmp/stinger_web_demo.log"
        pid_file = "/tmp/stinger_web_demo.pid"
        
        # Start the process in background
        with open(log_file, 'w') as log:
            process = subprocess.Popen(
                [sys.executable, "main.py"],
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=True
            )
        
        # Save PID
        with open(pid_file, 'w') as f:
            f.write(str(process.pid))
        
        print(f"✅ Server started in background (PID: {process.pid})")
        print(f"📋 Logs: {log_file}")
        print(f"🔑 PID file: {pid_file}")
        print("\n🔗 Quick Access URLs:")
        print("   Demo:   http://127.0.0.1:8000")
        print("   Health: http://127.0.0.1:8000/api/health")
        print("   API:    http://127.0.0.1:8000/api/docs")
        print("\n💡 To stop: kill $(cat /tmp/stinger_web_demo.pid)")
        
    elif ci_mode:
        # In CI mode, exit on error
        exit_code = os.system("python3 main.py")
        sys.exit(exit_code >> 8)  # Convert to proper exit code
    else:
        # Interactive mode
        print("💡 Press Ctrl+C to stop")
        try:
            os.system("python3 main.py")
        except KeyboardInterrupt:
            print("\n🛑 Stopped")
            
        print("\n🔗 Quick Access URLs:")
        print("   Demo:   http://127.0.0.1:8000")
        print("   Health: http://127.0.0.1:8000/api/health")
        print("   API:    http://127.0.0.1:8000/api/docs")

if __name__ == "__main__":
    main()