#!/usr/bin/env python3
"""Test startup and immediate shutdown"""

import subprocess
import sys
import time

print("🧪 Testing startup script...")

# Start the startup script
proc = subprocess.Popen([sys.executable, "start_demo.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

# Let it run for 8 seconds
time.sleep(8)

# Kill it
proc.terminate()
stdout, _ = proc.communicate(timeout=5)

print("📋 Output:")
print(stdout.decode())

print(f"🎯 Return code: {proc.returncode}")