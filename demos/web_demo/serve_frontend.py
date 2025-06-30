#!/usr/bin/env python3
"""
Simple HTTP server for React app with proper SPA routing
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

class SPAHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Handler that serves index.html for all routes (SPA behavior)"""
    
    def end_headers(self):
        # Add CORS headers to allow API calls
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_GET(self):
        # If it's an API call, this won't be hit due to proxy config
        # But we can add some debug info
        if self.path.startswith('/api/'):
            self.send_error(404, f"API call {self.path} should be proxied to backend")
            return
            
        # For all other routes, try to serve the file, or fall back to index.html
        requested_path = self.path.split('?')[0]  # Remove query params
        
        # If it's a file request with extension, serve it directly
        if '.' in requested_path.split('/')[-1]:
            super().do_GET()
            return
            
        # For routes like /, /test, etc., serve index.html
        if requested_path == '/' or not requested_path.startswith('/static/'):
            self.path = '/index.html'
            
        super().do_GET()

def main():
    PORT = 3000
    
    # Change to the build directory
    build_dir = Path(__file__).parent / "frontend" / "build"
    if not build_dir.exists():
        print(f"❌ Build directory not found: {build_dir}")
        print("Run 'npm run build' in the frontend directory first")
        return 1
        
    os.chdir(build_dir)
    
    try:
        with socketserver.TCPServer(("", PORT), SPAHTTPRequestHandler) as httpd:
            print(f"🚀 Serving React app at http://localhost:{PORT}")
            print(f"📁 Serving from: {build_dir}")
            print(f"🧪 Test mode: http://localhost:{PORT}/?test=true")
            print("Press Ctrl+C to stop")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        return 0
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Port {PORT} is already in use")
            print("Stop the existing server or use a different port")
            return 1
        else:
            print(f"❌ Server error: {e}")
            return 1

if __name__ == "__main__":
    sys.exit(main())