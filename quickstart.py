#!/usr/bin/env python3
"""
Quick start script for Stinger Guardrails.
Run this after installation to set up your environment.
"""

import subprocess
import sys

def main():
    print("🛡️  Stinger Guardrails Quick Start")
    print("=" * 40)
    print("\nThis script will help you set up Stinger.")
    print("Running setup wizard...\n")
    
    # Run the setup wizard
    try:
        result = subprocess.run([sys.executable, "-m", "stinger", "setup"], check=False)
        return result.returncode
    except Exception as e:
        print(f"Error running setup: {e}")
        print("\nPlease ensure Stinger is installed:")
        print("  pip install stinger-guardrails-alpha")
        return 1

if __name__ == "__main__":
    sys.exit(main())