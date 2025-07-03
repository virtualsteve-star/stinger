#!/usr/bin/env python3
"""Fix simple guardrail constructor calls"""

import re

# Fix test_simple_guardrails_behavior.py
with open('tests/behavioral/test_simple_guardrails_behavior.py', 'r') as f:
    content = f.read()

# Replace guardrail constructors that take (name, config) with just (config)
guardrails = ['LengthGuardrail', 'RegexGuardrail', 'KeywordBlockGuardrail']

for guardrail in guardrails:
    # Pattern to match Guardrail("name", config)
    pattern = rf'{guardrail}\(["\'][^"\']+["\']\s*,\s*'
    replacement = f'{guardrail}('
    content = re.sub(pattern, replacement, content)

with open('tests/behavioral/test_simple_guardrails_behavior.py', 'w') as f:
    f.write(content)

print("Fixed simple guardrail constructor calls")