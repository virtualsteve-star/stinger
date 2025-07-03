#!/usr/bin/env python3
"""
Behavioral Tests for URL Guardrail

Tests ACTUAL BEHAVIOR: Does it block/allow URLs correctly?
"""

import asyncio

import pytest
from src.stinger.guardrails.url_guardrail import URLGuardrail


class TestURLGuardrailBehavior:
    """Test URL guardrail blocks/allows domains correctly"""
    
    def test_blocked_domains(self):
        """Test that blocked domains are actually blocked"""
        config = {
            "name": "url_blocker",
            "config": {
                "blocked_domains": ["evil.com", "malware.org", "phishing.net"],
                "action": "block"
            }
        }
        guardrail = URLGuardrail(config)
        
        test_cases = [
            # Should block
            ("Visit http://evil.com", True, "Direct blocked domain"),
            ("Go to https://evil.com/path", True, "Blocked domain with path"),
            ("Check out evil.com", True, "Domain without protocol"),
            ("Link: malware.org/download", True, "Another blocked domain"),
            ("subdomain.phishing.net", True, "Subdomain of blocked"),
            
            # Should allow
            ("Visit google.com", False, "Safe domain"),
            ("Go to example.com", False, "Another safe domain"),
            ("The word evil is ok", False, "Just the word, not domain"),
            ("evil.com.example.com", False, "Blocked domain as subdomain of safe"),
        ]
        
        for text, should_block, description in test_cases:
            result = asyncio.run(guardrail.analyze(text))
            assert result.blocked == should_block, f"Failed: {description}. Text: '{text}'"
    
    def test_allowed_domains_only(self):
        """Test allowlist mode - only allowed domains pass"""
        config = {
            "name": "url_allowlist",
            "config": {
                "allowed_domains": ["safe.com", "trusted.org", "mycompany.com"],
                "action": "block"
            }
        }
        guardrail = URLGuardrail(config)
        
        test_cases = [
            # Should allow (in allowlist)
            ("Visit safe.com", False, "Allowed domain"),
            ("Go to https://trusted.org", False, "Allowed with protocol"),
            ("Link to mycompany.com/products", False, "Allowed with path"),
            
            # Should block (not in allowlist)
            ("Visit google.com", True, "Popular but not allowed"),
            ("Go to example.com", True, "Not in allowlist"),
            ("Check evil.com", True, "Definitely not allowed"),
        ]
        
        for text, should_block, description in test_cases:
            result = asyncio.run(guardrail.analyze(text))
            assert result.blocked == should_block, f"Failed: {description}. Text: '{text}'"
    
    def test_both_lists_interaction(self):
        """Test interaction when both blocked and allowed lists are set"""
        config = {
            "name": "url_both",
            "config": {
                "blocked_domains": ["bad.com", "evil.org"],
                "allowed_domains": ["good.com", "safe.org", "bad.com"],  # Conflict!
                "action": "block"
            }
        }
        guardrail = URLGuardrail(config)
        
        # Test conflicting domain (in both lists)
        result = asyncio.run(guardrail.analyze("Visit bad.com"))
        print(f"Domain in both lists - blocked: {result.blocked}")
        
        # Test allowed only
        result = asyncio.run(guardrail.analyze("Visit good.com"))
        print(f"Allowed domain - blocked: {result.blocked}")
        
        # Test blocked only
        result = asyncio.run(guardrail.analyze("Visit evil.org"))
        print(f"Blocked domain - blocked: {result.blocked}")
        
        # Test neither list
        result = asyncio.run(guardrail.analyze("Visit random.com"))
        print(f"Domain in neither list - blocked: {result.blocked}")
    
    def test_subdomain_handling(self):
        """Test how subdomains are handled"""
        config = {
            "name": "url_subdomain",
            "config": {
                "blocked_domains": ["evil.com"],
                "action": "block"
            }
        }
        guardrail = URLGuardrail(config)
        
        subdomain_tests = [
            "sub.evil.com",
            "deep.sub.evil.com", 
            "evil.com.safe.com",  # evil.com is subdomain of safe.com
            "notevil.com",
            "evilcom.org",
        ]
        
        for domain in subdomain_tests:
            result = asyncio.run(guardrail.analyze(f"Visit {domain}"))
            print(f"'{domain}' - blocked: {result.blocked}")
    
    def test_url_detection_patterns(self):
        """Test various URL patterns are detected"""
        config = {
            "name": "url_patterns",
            "config": {
                "blocked_domains": ["blocked.com"],
                "action": "block"
            }
        }
        guardrail = URLGuardrail(config)
        
        url_patterns = [
            # Different protocols
            ("http://blocked.com", True, "HTTP URL"),
            ("https://blocked.com", True, "HTTPS URL"),
            ("ftp://blocked.com", True, "FTP URL"),
            ("blocked.com", True, "No protocol"),
            
            # Different formats
            ("www.blocked.com", True, "With www"),
            ("blocked.com:8080", True, "With port"),
            ("blocked.com/path/to/page", True, "With path"),
            ("blocked.com?param=value", True, "With query"),
            
            # In context
            ("Visit blocked.com today!", True, "In sentence"),
            ("The site (blocked.com) is bad", True, "In parentheses"),
            ("[blocked.com]", True, "In brackets"),
        ]
        
        for text, expected, description in url_patterns:
            result = asyncio.run(guardrail.analyze(text))
            assert result.blocked == expected, f"Failed: {description}"
    
    def test_action_configuration(self):
        """Test different action configurations"""
        # Warn action
        warn_config = {
            "name": "url_warn",
            "config": {
                "blocked_domains": ["suspicious.com"],
                "action": "warn"
            }
        }
        warn_guard = URLGuardrail(warn_config)
        result = asyncio.run(warn_guard.analyze("Visit suspicious.com"))
        print(f"Warn action - blocked: {result.blocked}")
        
        # Allow action
        allow_config = {
            "name": "url_allow",
            "config": {
                "blocked_domains": ["tracked.com"],
                "action": "allow"
            }
        }
        allow_guard = URLGuardrail(allow_config)
        result = asyncio.run(allow_guard.analyze("Visit tracked.com"))
        print(f"Allow action - blocked: {result.blocked}")
    
    def test_empty_configuration(self):
        """Test behavior with empty domain lists"""
        config = {
            "name": "url_empty",
            "config": {
                "blocked_domains": [],
                "allowed_domains": [],
                "action": "block"
            }
        }
        guardrail = URLGuardrail(config)
        
        # With no lists, what happens?
        result = asyncio.run(guardrail.analyze("Visit google.com"))
        print(f"Empty lists - blocked: {result.blocked}")
    
    def test_case_sensitivity(self):
        """Test domain matching case sensitivity"""
        config = {
            "name": "url_case",
            "config": {
                "blocked_domains": ["Evil.COM"],
                "action": "block"
            }
        }
        guardrail = URLGuardrail(config)
        
        case_tests = [
            "evil.com",
            "EVIL.COM",
            "Evil.Com",
            "eViL.cOm",
        ]
        
        for domain in case_tests:
            result = asyncio.run(guardrail.analyze(f"Visit {domain}"))
            print(f"'{domain}' vs 'Evil.COM' - blocked: {result.blocked}")


def test_financial_url_scenario():
    """Test URL filtering in financial context"""
    config = {
        "name": "financial_urls",
        "config": {
            "allowed_domains": [
                "mybank.com",
                "securepayment.com",
                "officialbank.org"
            ],
            "blocked_domains": [
                "phishing-bank.com",
                "fake-payment.org",
                "scam.com"
            ],
            "action": "block"
        }
    }
    guardrail = URLGuardrail(config)
    
    scenarios = [
        # Should allow
        ("Login at mybank.com", False, "Official bank"),
        ("Pay via securepayment.com", False, "Approved payment"),
        
        # Should block  
        ("Login at phishing-bank.com", True, "Phishing site"),
        ("Transfer via totallynotascam.com", True, "Not in allowlist"),
        ("Click scam.com/free-money", True, "Known scam"),
    ]
    
    for text, expected, description in scenarios:
        result = asyncio.run(guardrail.analyze(text))
        assert result.blocked == expected, f"Financial URL: {description}"


if __name__ == "__main__":
    test = TestURLGuardrailBehavior()
    
    print("=== URL Guardrail Behavioral Test Results ===")
    print("\n1. Testing blocked domains...")
    try:
        test.test_blocked_domains()
        print("✓ Blocked domains test passed")
    except AssertionError as e:
        print(f"✗ Blocked domains test failed: {e}")
    
    print("\n2. Testing allowed domains...")
    try:
        test.test_allowed_domains_only()
        print("✓ Allowed domains test passed")
    except AssertionError as e:
        print(f"✗ Allowed domains test failed: {e}")
    
    print("\n3. Testing subdomain handling...")
    test.test_subdomain_handling()
    
    print("\n4. Testing case sensitivity...")
    test.test_case_sensitivity()