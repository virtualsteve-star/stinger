#!/usr/bin/env python3
"""
Human Verification Test Script
Phase 9: Human-in-the-Loop Testing

This script runs all guardrails with predefined positive and negative test cases
and generates a comprehensive, human-readable report for manual verification.
"""

import argparse
import asyncio
import json

# Add src to path for imports
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from stinger.core.guardrail_interface import GuardrailInterface
from stinger.guardrails.ai_code_generation_guardrail import AICodeGenerationGuardrail
from stinger.guardrails.ai_pii_detection_guardrail import AIPIIDetectionGuardrail
from stinger.guardrails.ai_toxicity_detection_guardrail import AIToxicityDetectionGuardrail
from stinger.guardrails.keyword_block import KeywordBlockGuardrail
from stinger.guardrails.length_guardrail import LengthGuardrail
from stinger.guardrails.prompt_injection_guardrail import PromptInjectionGuardrail
from stinger.guardrails.regex_guardrail import RegexGuardrail
from stinger.guardrails.simple_code_generation_guardrail import SimpleCodeGenerationGuardrail
from stinger.guardrails.simple_pii_detection_guardrail import SimplePIIDetectionGuardrail
from stinger.guardrails.simple_toxicity_detection_guardrail import SimpleToxicityDetectionGuardrail
from stinger.guardrails.topic_guardrail import TopicGuardrail
from stinger.guardrails.url_guardrail import URLGuardrail


@dataclass
class TestResult:
    """Represents the result of a single test case."""

    guardrail_name: str
    guardrail_type: str  # "local" or "ai"
    test_type: str  # "positive" or "negative"
    input_text: str
    expected_result: str
    actual_result: str
    confidence: float
    response_time: float
    matched_expectation: bool
    details: Dict[str, Any]
    config_details: str = ""


class HumanVerificationTester:
    """Main class for running human verification tests."""

    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.guardrails = {}
        self.results = []

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        with open(self.config_path, "r") as f:
            return yaml.safe_load(f)

    def _create_guardrail(
        self, name: str, guardrail_type: str, config: Dict[str, Any], is_ai: bool = False
    ) -> GuardrailInterface:
        """Create a guardrail instance based on type."""
        guardrail_classes = {
            # Local versions
            "simple_pii_detection": SimplePIIDetectionGuardrail,
            "simple_toxicity_detection": SimpleToxicityDetectionGuardrail,
            "simple_code_generation": SimpleCodeGenerationGuardrail,
            # AI versions
            "ai_pii_detection": AIPIIDetectionGuardrail,
            "ai_toxicity_detection": AIToxicityDetectionGuardrail,
            "ai_code_generation": AICodeGenerationGuardrail,
            # Other guardrails (local only)
            "url_filter": URLGuardrail,
            "length_guardrail": LengthGuardrail,
            "regex_guardrail": RegexGuardrail,
            "keyword_block": KeywordBlockGuardrail,
            "topic_filter": TopicGuardrail,
            "prompt_injection": PromptInjectionGuardrail,
        }

        if guardrail_type not in guardrail_classes:
            raise ValueError(f"Unknown guardrail type: {guardrail_type}")

        # Different guardrails have different constructor signatures
        if guardrail_type in ["url_filter", "length_guardrail", "regex_guardrail", "topic_filter"]:
            # These guardrails take config dict directly with patterns at top level
            full_config = {"name": name, **config}
            return guardrail_classes[guardrail_type](full_config)
        elif guardrail_type == "keyword_block":
            # KeywordBlockGuardrail takes config with keywords at top level
            full_config = {"name": name, **config}
            return guardrail_classes[guardrail_type](full_config)
        else:
            # SimplePIIDetection, SimpleToxicity, SimpleCodeGen, PromptInjection take (name, config)
            return guardrail_classes[guardrail_type](name, {"name": name, "config": config})

    def _get_config_details(self, guardrail_name: str) -> str:
        """Get configuration details for a guardrail."""
        base_name = guardrail_name.replace("_local", "").replace("_ai", "")
        if base_name in self.config["guardrail_configs"]:
            config = self.config["guardrail_configs"][base_name]["config"]
            details = []

            if "max_length" in config:
                details.append(f"Max Length: {config['max_length']}")
            if "min_length" in config:
                details.append(f"Min Length: {config['min_length']}")
            if "blocked_domains" in config:
                details.append(f"Blocked Domains: {', '.join(config['blocked_domains'])}")
            if "deny_topics" in config:
                details.append(f"Denied Topics: {', '.join(config['deny_topics'])}")
            if "allow_topics" in config:
                details.append(f"Allowed Topics: {', '.join(config['allow_topics'])}")
            if "confidence_threshold" in config:
                details.append(f"Confidence Threshold: {config['confidence_threshold']}")
            if "keyword" in config:
                details.append(f"Blocked Keyword: '{config['keyword']}'")
            if "patterns" in config:
                details.append(f"Patterns: {', '.join(config['patterns'])}")

            return "; ".join(details) if details else "Default configuration"
        return "Configuration not found"

    def _setup_guardrails(self):
        """Set up all guardrails for testing."""
        for name, config in self.config["guardrail_configs"].items():
            guardrail_type = config["type"]
            guardrail_config = config["config"]

            # Create local version
            local_name = f"{name}_local"
            self.guardrails[local_name] = self._create_guardrail(
                local_name, guardrail_type, guardrail_config, is_ai=False
            )

            # Create AI version if available
            if guardrail_type in [
                "simple_pii_detection",
                "simple_toxicity_detection",
                "simple_code_generation",
            ]:
                ai_type = guardrail_type.replace("simple_", "ai_")
                ai_name = f"{name}_ai"
                self.guardrails[ai_name] = self._create_guardrail(
                    ai_name, ai_type, guardrail_config, is_ai=True
                )

    async def _run_single_test(
        self, guardrail_name: str, test_type: str, test_case: Dict[str, Any]
    ) -> TestResult:
        """Run a single test case."""
        guardrail = self.guardrails[guardrail_name]
        input_text = test_case["text"]
        expected_result = test_case["expected"]

        # Run the test
        start_time = time.time()
        try:
            result = await guardrail.analyze(input_text)
            response_time = time.time() - start_time

            actual_result = "blocked" if result.blocked else "allowed"
            matched_expectation = actual_result == expected_result

            return TestResult(
                guardrail_name=guardrail_name,
                guardrail_type="ai" if "ai" in guardrail_name else "local",
                test_type=test_type,
                input_text=input_text,
                expected_result=expected_result,
                actual_result=actual_result,
                confidence=result.confidence,
                response_time=response_time,
                matched_expectation=matched_expectation,
                details=result.details,
                config_details=self._get_config_details(guardrail_name),
            )
        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                guardrail_name=guardrail_name,
                guardrail_type="ai" if "ai" in guardrail_name else "local",
                test_type=test_type,
                input_text=input_text,
                expected_result=expected_result,
                actual_result="error",
                confidence=0.0,
                response_time=response_time,
                matched_expectation=False,
                details={"error": str(e)},
                config_details=self._get_config_details(guardrail_name),
            )

    async def run_all_tests(self):
        """Run all test cases."""
        self._setup_guardrails()

        for guardrail_name, test_cases in self.config["test_cases"].items():
            for test_type in ["positive", "negative"]:
                if test_type in test_cases:
                    test_case = test_cases[test_type]

                    # Test local version
                    local_guardrail_name = f"{guardrail_name}_local"
                    if local_guardrail_name in self.guardrails:
                        result = await self._run_single_test(
                            local_guardrail_name, test_type, test_case
                        )
                        self.results.append(result)

                    # Test AI version if available
                    ai_guardrail_name = f"{guardrail_name}_ai"
                    if ai_guardrail_name in self.guardrails:
                        result = await self._run_single_test(
                            ai_guardrail_name, test_type, test_case
                        )
                        self.results.append(result)

    def _format_text(self, text: str, max_length: int = 60) -> str:
        """Format text for display, truncating if too long."""
        if len(text) <= max_length:
            return text
        return text[: max_length - 3] + "..."

    def _format_full_text(self, text: str) -> str:
        """Format full text with proper indentation for display."""
        # Split into lines if text is very long
        if len(text) > 80:
            lines = []
            current_line = ""
            words = text.split()

            for word in words:
                if len(current_line + " " + word) <= 75:  # Leave room for indentation
                    current_line += (" " + word) if current_line else word
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word

            if current_line:
                lines.append(current_line)

            return "\n".join(f"   {line}" for line in lines)
        else:
            return f"   {text}"

    def _get_status_symbol(self, matched: bool) -> str:
        """Get status symbol for test result."""
        return "✅" if matched else "❌"

    def _get_status_text(self, matched: bool) -> str:
        """Get status text for test result."""
        return "MATCH" if matched else "MISMATCH"

    def generate_report(self) -> str:
        """Generate a pretty-printed report."""
        if not self.results:
            return "No test results available."

        # Calculate statistics
        total_tests = len(self.results)
        matched_tests = sum(1 for r in self.results if r.matched_expectation)
        failed_tests = total_tests - matched_tests
        success_rate = (matched_tests / total_tests) * 100

        # Group results by guardrail (base name)
        guardrail_results = {}
        for result in self.results:
            base_name = result.guardrail_name.replace("_local", "").replace("_ai", "")
            if base_name not in guardrail_results:
                guardrail_results[base_name] = []
            guardrail_results[base_name].append(result)

        # Generate report
        report_lines = []

        # Header
        report_lines.extend(
            [
                "╔══════════════════════════════════════════════════════════════════════════════╗",
                "║                           HUMAN VERIFICATION REPORT                          ║",
                "║                              Phase 9 Testing                                 ║",
                f"║                              {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                              ║",
                "╚══════════════════════════════════════════════════════════════════════════════╝",
                "",
                "📊 SUMMARY",
                "═══════════════════════════════════════════════════════════════════════════════════",
                f"Total Tests: {total_tests} ({len(guardrail_results)} guardrails × 2 tests each)",
                f"✅ Matched Expectations: {matched_tests}",
                f"❌ Failed Expectations: {failed_tests}",
                f"Success Rate: {success_rate:.1f}%",
                "",
                "🔍 DETAILED RESULTS",
                "═══════════════════════════════════════════════════════════════════════════════════",
                "",
            ]
        )

        # Detailed results for each guardrail
        for i, (guardrail_name, results) in enumerate(guardrail_results.items(), 1):
            guardrail_name_clean = guardrail_name.replace("_", " ").title()
            report_lines.extend([f"{i}. {guardrail_name_clean.upper()}", "─" * 80, ""])

            # Group by test type (positive/negative) and show local vs AI
            test_types = {}
            for result in results:
                if result.test_type not in test_types:
                    test_types[result.test_type] = []
                test_types[result.test_type].append(result)

            for test_type in ["positive", "negative"]:
                if test_type in test_types:
                    type_results = test_types[test_type]
                    test_type_upper = test_type.upper()

                    report_lines.extend([f"   {test_type_upper} TEST CASES:", ""])

                    for result in type_results:
                        status_symbol = self._get_status_symbol(result.matched_expectation)
                        status_text = self._get_status_text(result.matched_expectation)
                        formatted_text = self._format_text(result.input_text)
                        full_text = self._format_full_text(result.input_text)
                        guardrail_type_display = f"[{result.guardrail_type.upper()}]"

                        report_lines.extend(
                            [
                                f"   {status_symbol} {guardrail_type_display} {test_type_upper} TEST:",
                                f'      Truncated: "{formatted_text}"',
                                f"      Full Text:",
                                full_text,
                                f"      Configuration: {result.config_details}",
                                f"      Expected: {result.expected_result.upper()}",
                                f"      Actual:   {result.actual_result.upper()} (confidence: {result.confidence:.2f})",
                                f"      Response Time: {result.response_time:.3f}s",
                                f"      Status:   {status_symbol} {status_text}",
                                "",
                            ]
                        )

        # Failed tests summary
        failed_results = [r for r in self.results if not r.matched_expectation]
        if failed_results:
            report_lines.extend(
                [
                    "📋 FAILED TESTS SUMMARY",
                    "═══════════════════════════════════════════════════════════════════════════════════",
                ]
            )

            for i, result in enumerate(failed_results, 1):
                guardrail_name_clean = result.guardrail_name.replace("_", " ").title()
                test_type = result.test_type.title()
                formatted_text = self._format_text(result.input_text, 40)

                report_lines.extend(
                    [
                        f"{i}. {guardrail_name_clean} - {test_type} Test",
                        f'   Issue: {result.actual_result} result for "{formatted_text}"',
                        f"   Expected: {result.expected_result}, Got: {result.actual_result}",
                        "",
                    ]
                )

        # Recommendations
        report_lines.extend(
            [
                "🎯 RECOMMENDATIONS",
                "═══════════════════════════════════════════════════════════════════════════════════",
            ]
        )

        if failed_tests == 0:
            report_lines.append("• All tests passed! System is working as expected.")
        else:
            report_lines.extend(
                [
                    f"• {failed_tests} tests need human review and potential guardrail tuning",
                    f"• Overall system is working well ({success_rate:.1f}% success rate)",
                ]
            )

            # Specific recommendations based on failures
            for result in failed_results:
                if result.guardrail_name == "toxicity_detection":
                    report_lines.append("• Consider adjusting toxicity detection sensitivity")
                elif result.guardrail_name == "url_filter":
                    report_lines.append("• Review URL subdomain handling logic")
                else:
                    report_lines.append(f"• Review {result.guardrail_name} configuration")

        return "\n".join(report_lines)

    def save_report(self, output_path: str):
        """Save report to file."""
        report = self.generate_report()
        with open(output_path, "w") as f:
            f.write(report)
        print(f"Report saved to: {output_path}")

    def save_json_report(self, output_path: str):
        """Save detailed results as JSON."""
        json_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": len(self.results),
                "matched_tests": sum(1 for r in self.results if r.matched_expectation),
                "failed_tests": sum(1 for r in self.results if not r.matched_expectation),
                "success_rate": (
                    sum(1 for r in self.results if r.matched_expectation) / len(self.results)
                )
                * 100,
            },
            "results": [
                {
                    "guardrail_name": r.guardrail_name,
                    "test_type": r.test_type,
                    "input_text": r.input_text,
                    "expected_result": r.expected_result,
                    "actual_result": r.actual_result,
                    "confidence": r.confidence,
                    "response_time": r.response_time,
                    "matched_expectation": r.matched_expectation,
                    "details": r.details,
                }
                for r in self.results
            ],
        }

        with open(output_path, "w") as f:
            json.dump(json_data, f, indent=2)
        print(f"JSON report saved to: {output_path}")


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Human Verification Test Script")
    parser.add_argument("--config", default="config.yaml", help="Path to configuration file")
    parser.add_argument("--output", help="Output file for report")
    parser.add_argument("--json", help="Output file for JSON report")

    args = parser.parse_args()

    # Create tester and run tests
    tester = HumanVerificationTester(args.config)
    print("🚀 Running Human Verification Tests...")
    print("=" * 60)

    await tester.run_all_tests()

    # Generate and display report
    report = tester.generate_report()
    print(report)

    # Save reports if requested
    if args.output:
        tester.save_report(args.output)
    else:
        # Default output to results directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_output = f"results/human_verification_report_{timestamp}.txt"
        tester.save_report(default_output)

    if args.json:
        tester.save_json_report(args.json)
    else:
        # Default JSON output to results directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_json = f"results/human_verification_report_{timestamp}.json"
        tester.save_json_report(default_json)

    # Exit with appropriate code
    failed_tests = sum(1 for r in tester.results if not r.matched_expectation)
    if failed_tests > 0:
        print(f"\n⚠️  {failed_tests} tests failed. Please review the results above.")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
