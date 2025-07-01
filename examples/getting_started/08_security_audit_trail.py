#!/usr/bin/env python3
"""
Security Audit Trail Getting Started Example

This example shows how to enable the security audit trail system in Stinger
for tracking all security-related behavior for forensic analysis and compliance.

This is NOT developer debug logging - this tracks security decisions for audit purposes.
"""

import os
import json
import tempfile

import stinger


def main():
    print("=== Stinger Security Audit Trail Example ===\n")
    
    # 1. Zero-config enable - Just enable it!
    print("1. Zero-config enable:")
    print("   stinger.audit.enable()  # Just works!")
    
    stinger.audit.enable()
    print(f"   ✓ Audit trail enabled: {stinger.audit.is_enabled()}")
    stinger.audit.disable()  # Disable for next example
    
    # 2. Easy destination configuration
    print("\n2. Easy destination configuration:")
    
    # Console logging (great for development)
    print("   stinger.audit.enable('stdout')  # Console logging")
    stinger.audit.enable("stdout")
    
    # Log some example security events
    stinger.audit.log_prompt(
        prompt="What is the weather today?",
        user_id="user_123",
        conversation_id="conv_456"
    )
    
    stinger.audit.log_guardrail_decision(
        guardrail_name="content_moderation",
        decision="allow",
        reason="Content is safe",
        user_id="user_123",
        conversation_id="conv_456"
    )
    
    stinger.audit.log_response(
        response="It's sunny and 75°F today!",
        user_id="user_123", 
        conversation_id="conv_456",
        model_used="gpt-4.1-nano"
    )
    
    print("   ✓ Security events logged to console above")
    stinger.audit.disable()
    
    # 3. File logging with PII redaction
    print("\n3. File logging with PII redaction:")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        audit_file = f.name
    
    print(f"   stinger.audit.enable('{audit_file}', redact_pii=True)")
    stinger.audit.enable(audit_file, redact_pii=True)
    
    # Log a prompt with PII
    stinger.audit.log_prompt(
        prompt="My email is john@example.com and I need help",
        user_id="user_123"
    )
    
    stinger.audit.disable()
    
    # Show the redacted content
    with open(audit_file, 'r') as f:
        lines = f.readlines()
        
    print("   ✓ Audit log created with PII redaction:")
    for line in lines:
        record = json.loads(line)
        if record.get("event_type") == "user_prompt":
            print(f"     Original: 'My email is john@example.com and I need help'")
            print(f"     Redacted: '{record['prompt']}'")
            break
    
    # Clean up
    os.unlink(audit_file)
    
    # 4. Smart environment detection
    print("\n4. Smart environment detection:")
    print("   - Development: stdout, no PII redaction")
    print("   - Production: ./audit.log, PII redaction enabled")
    print("   - Docker: stdout, PII redaction enabled")
    print("   ✓ Just call audit.enable() and it chooses smart defaults!")
    
    # 5. Integration with guardrails
    print("\n5. Pipeline integration:")
    print("   Creating pipeline and enabling audit trail...")
    
    # Enable audit to stdout for demo
    stinger.audit.enable("stdout")
    
    # Create a guardrail pipeline
    pipeline = stinger.create_pipeline()
    
    # Create a conversation for context
    from stinger.core.conversation import Conversation
    conversation = Conversation("demo_user", "assistant", conversation_id="demo_conv")
    
    print("   Processing input through guardrails with audit trail:")
    input_result = pipeline.check_input("Hello, can you help me?", conversation=conversation)
    
    print("   Processing output through guardrails with audit trail:")
    output_result = pipeline.check_output("Of course! I'm here to help.", conversation=conversation)
    
    print("   ✓ Complete conversation flow logged with all security decisions!")
    
    stinger.audit.disable()
    
    # 6. Compliance reporting with export utilities
    print("\n6. Compliance reporting:")
    print("   Creating sample audit data for export...")
    
    # Create a temporary audit file with sample data
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        export_audit_file = f.name
    
    stinger.audit.enable(export_audit_file)
    
    # Generate sample compliance data
    stinger.audit.log_prompt("What are the security policies?", user_id="compliance_user", conversation_id="audit_conv")
    stinger.audit.log_guardrail_decision("policy_check", "allow", "Approved security query", 
                                        user_id="compliance_user", conversation_id="audit_conv")
    stinger.audit.log_response("Here are our security policies...", user_id="compliance_user", conversation_id="audit_conv")
    
    stinger.audit.disable()
    
    # Export to CSV for compliance reporting
    csv_file = stinger.audit.export_csv(destination=export_audit_file)
    print(f"   ✓ CSV export created: {csv_file}")
    
    # Export to JSON for analysis
    json_file = stinger.audit.export_json(destination=export_audit_file)
    print(f"   ✓ JSON export created: {json_file}")
    
    # Show sample of CSV content
    import csv
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"   📊 CSV contains {len(rows)} audit records")
    print(f"   📋 Available for compliance teams and auditors")
    
    # Clean up export files
    os.unlink(export_audit_file)
    os.unlink(csv_file)
    os.unlink(json_file)
    
    print("\n=== Complete Security Audit Trail ===")
    print("✓ Zero-config enable: audit.enable()")
    print("✓ Easy destinations: file or stdout")
    print("✓ Smart environment detection")
    print("✓ PII redaction when needed")
    print("✓ JSON format for easy analysis")
    print("✓ Compliance export utilities (CSV/JSON)")
    print("✓ Designed for forensic analysis and compliance")


if __name__ == "__main__":
    main()