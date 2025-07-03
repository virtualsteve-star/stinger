#!/usr/bin/env python3
"""Fix URLGuardrail constructor calls"""

import re

# Fix test_url_behavior.py
with open('tests/behavioral/test_url_behavior.py', 'r') as f:
    content = f.read()

# Replace URLGuardrail("name", config) with URLGuardrail(config)
content = re.sub(r'URLGuardrail\("[^"]+",\s*', 'URLGuardrail(', content)

with open('tests/behavioral/test_url_behavior.py', 'w') as f:
    f.write(content)

print("Fixed URLGuardrail constructor calls in test_url_behavior.py")