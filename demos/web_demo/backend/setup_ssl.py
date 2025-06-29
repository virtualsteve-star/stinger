#!/usr/bin/env python3
"""
SSL Certificate Setup for Stinger Web Demo

This script generates self-signed SSL certificates for local HTTPS development.
The certificates enable secure communication between the React frontend and
FastAPI backend, even in local development.

Usage:
    python setup_ssl.py

This will generate:
    - cert.pem: SSL certificate
    - key.pem: Private key

After running this script, the FastAPI server will start with HTTPS enabled.
"""

import subprocess
import sys
from pathlib import Path


def generate_ssl_certificates():
    """Generate self-signed SSL certificates for local development."""
    
    backend_dir = Path(__file__).parent
    cert_file = backend_dir / "cert.pem"
    key_file = backend_dir / "key.pem"
    
    # Check if certificates already exist
    if cert_file.exists() and key_file.exists():
        print("🔒 SSL certificates already exist!")
        print(f"   Certificate: {cert_file}")
        print(f"   Private key: {key_file}")
        
        overwrite = input("Do you want to regenerate them? (y/N): ").lower().strip()
        if overwrite != 'y':
            print("Keeping existing certificates.")
            return True
    
    print("🔧 Generating self-signed SSL certificates for localhost...")
    
    # OpenSSL command to generate self-signed certificate
    openssl_cmd = [
        "openssl", "req", "-x509", "-newkey", "rsa:4096",
        "-keyout", str(key_file),
        "-out", str(cert_file),
        "-days", "365",
        "-nodes",
        "-subj", "/CN=localhost"
    ]
    
    try:
        # Run OpenSSL command
        result = subprocess.run(
            openssl_cmd,
            cwd=backend_dir,
            capture_output=True,
            text=True,
            check=True
        )
        
        print("✅ SSL certificates generated successfully!")
        print(f"   Certificate: {cert_file}")
        print(f"   Private key: {key_file}")
        print()
        print("🔒 Your FastAPI server will now run with HTTPS enabled.")
        print("📝 When you first access https://localhost:8000 in your browser,")
        print("   you'll need to accept the security warning for the self-signed certificate.")
        print()
        print("🚀 You can now start the backend with: python main.py")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to generate SSL certificates: {e}")
        print(f"   stdout: {e.stdout}")
        print(f"   stderr: {e.stderr}")
        print()
        print("💡 Make sure OpenSSL is installed on your system:")
        print("   - macOS: brew install openssl")
        print("   - Ubuntu/Debian: sudo apt-get install openssl")
        print("   - Windows: Install OpenSSL or use WSL")
        return False
        
    except FileNotFoundError:
        print("❌ OpenSSL not found!")
        print("   Please install OpenSSL to generate SSL certificates:")
        print("   - macOS: brew install openssl")
        print("   - Ubuntu/Debian: sudo apt-get install openssl")
        print("   - Windows: Install OpenSSL or use WSL")
        print()
        print("⚠️ Alternatively, you can run the demo with HTTP (less secure):")
        print("   The FastAPI server will automatically fall back to HTTP if no certificates are found.")
        return False


def verify_certificates():
    """Verify that the generated certificates are valid."""
    backend_dir = Path(__file__).parent
    cert_file = backend_dir / "cert.pem"
    
    if not cert_file.exists():
        return False
    
    try:
        # Verify certificate
        verify_cmd = ["openssl", "x509", "-in", str(cert_file), "-text", "-noout"]
        result = subprocess.run(verify_cmd, capture_output=True, text=True, check=True)
        
        print("🔍 Certificate verification:")
        
        # Extract key information
        lines = result.stdout.split('\n')
        for line in lines:
            if 'Subject:' in line:
                print(f"   Subject: {line.split('Subject:')[1].strip()}")
            elif 'Not Before:' in line:
                print(f"   Valid from: {line.split('Not Before:')[1].strip()}")
            elif 'Not After:' in line:
                print(f"   Valid until: {line.split('Not After:')[1].strip()}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Certificate verification failed: {e}")
        return False


def main():
    """Main function to set up SSL certificates."""
    
    print("🔐 Stinger Web Demo - SSL Certificate Setup")
    print("=" * 50)
    print()
    
    # Generate certificates
    if generate_ssl_certificates():
        print()
        verify_certificates()
        print()
        print("🎉 SSL setup complete!")
        print("   Your Stinger Web Demo is now ready for secure HTTPS communication.")
        print()
        print("Next steps:")
        print("1. Start the backend: python main.py")
        print("2. Build and start the frontend (see frontend/README.md)")
        print("3. Open https://localhost:8000 in your browser")
        print("4. Accept the security warning for the self-signed certificate")
        
    else:
        print()
        print("⚠️ SSL setup failed, but you can still use the demo with HTTP.")
        print("   The FastAPI server will automatically fall back to HTTP mode.")
        print()
        print("Alternative steps:")
        print("1. Start the backend: python main.py (will use HTTP)")
        print("2. Build and start the frontend with HTTP config")
        print("3. Open http://localhost:8000 in your browser")


if __name__ == "__main__":
    main()