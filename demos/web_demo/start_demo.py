#!/usr/bin/env python3
"""Start the Stinger Web Demo"""

import os
import sys

def main():
    # Check for CI mode
    ci_mode = "--ci" in sys.argv
    
    # Kill any existing backend
    os.system("lsof -ti:8000 | xargs kill -9 2>/dev/null || true")
    
    print("🚀 Starting Stinger Web Demo")
    if not ci_mode:
        print("💡 Press Ctrl+C to stop")
    
    # Just run the backend directly
    os.chdir("backend")
    
    if ci_mode:
        # In CI mode, exit on error
        exit_code = os.system("python3 main.py")
        sys.exit(exit_code >> 8)  # Convert to proper exit code
    else:
        # Interactive mode
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