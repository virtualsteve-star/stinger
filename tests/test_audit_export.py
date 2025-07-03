"""
Tests for audit trail export functionality.

Tests the CSV and JSON export utilities for compliance reporting.
"""

import csv
import json
import os
import sys
import tempfile

import pytest

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from stinger.core import audit


class TestAuditExport:
    """Test audit trail export functionality."""

    def setup_method(self):
        """Setup for each test."""
        # Disable audit trail before each test
        if audit.is_enabled():
            try:
                audit.disable()
            except RuntimeError:
                # Can't disable in production - reset the global instance
                audit._audit_trail = audit.AuditTrail()

    def test_export_csv_basic(self):
        """Test basic CSV export functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            audit_file = os.path.join(temp_dir, "test_export.log")

            # Enable audit trail and log some events
            audit.enable(audit_file)

            audit.log_prompt("Test prompt 1", user_id="user1", conversation_id="conv1")
            audit.log_guardrail_decision(
                "test_filter", "allow", "Test reason", user_id="user1", conversation_id="conv1"
            )
            audit.log_response("Test response 1", user_id="user1", conversation_id="conv1")

            audit.disable()

            # Export to CSV
            csv_file = os.path.join(temp_dir, "export_test.csv")
            result_file = audit.export_csv(destination=audit_file, output_file=csv_file)

            # Verify export file was created
            assert result_file == csv_file
            assert os.path.exists(csv_file)

            # Read and verify CSV content
            with open(csv_file, "r") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            # Should have 3 events (prompt, decision, response)
            assert len(rows) >= 3

            # Check that all required columns exist
            expected_columns = [
                "timestamp",
                "event_type",
                "user_id",
                "conversation_id",
                "request_id",
                "guardrail_name",
                "decision",
                "reason",
                "confidence",
                "summary",
            ]
            for row in rows:
                for col in expected_columns:
                    assert col in row

            # Check event types are present
            event_types = [row["event_type"] for row in rows]
            assert "user_prompt" in event_types
            assert "guardrail_decision" in event_types
            assert "llm_response" in event_types

    def test_export_json_basic(self):
        """Test basic JSON export functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            audit_file = os.path.join(temp_dir, "test_export.log")

            # Enable audit trail and log some events
            audit.enable(audit_file)

            audit.log_prompt("Test prompt 1", user_id="user1", conversation_id="conv1")
            audit.log_response("Test response 1", user_id="user1", conversation_id="conv1")

            audit.disable()

            # Export to JSON
            json_file = os.path.join(temp_dir, "export_test.json")
            result_file = audit.export_json(destination=audit_file, output_file=json_file)

            # Verify export file was created
            assert result_file == json_file
            assert os.path.exists(json_file)

            # Read and verify JSON content
            with open(json_file, "r") as f:
                export_data = json.load(f)

            # Check export data structure
            assert "export_timestamp" in export_data
            assert "guardrails" in export_data
            assert "total_records" in export_data
            assert "records" in export_data

            # Check filter information
            guardrails = export_data["guardrails"]
            assert guardrails["source_file"] == audit_file

            # Check records
            records = export_data["records"]
            assert len(records) >= 2  # prompt + response
            assert export_data["total_records"] == len(records)

            # Verify event types
            event_types = [r["event_type"] for r in records]
            assert "user_prompt" in event_types
            assert "llm_response" in event_types

    def test_export_csv_with_filters(self):
        """Test CSV export with filtering."""
        with tempfile.TemporaryDirectory() as temp_dir:
            audit_file = os.path.join(temp_dir, "test_filter_export.log")

            # Enable audit trail and log events for different users
            audit.enable(audit_file)

            audit.log_prompt("User1 prompt", user_id="user1", conversation_id="conv1")
            audit.log_prompt("User2 prompt", user_id="user2", conversation_id="conv2")
            audit.log_response("User1 response", user_id="user1", conversation_id="conv1")

            audit.disable()

            # Export only user1 events
            csv_file = os.path.join(temp_dir, "filtered_export.csv")
            result_file = audit.export_csv(
                destination=audit_file, output_file=csv_file, user_id="user1"
            )

            # Read CSV content
            with open(csv_file, "r") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            # Should only have user1 events
            for row in rows:
                if row["user_id"]:  # Skip empty rows
                    assert row["user_id"] == "user1"

            # Should have 2 user1 events (prompt + response)
            user1_events = [row for row in rows if row["user_id"] == "user1"]
            assert len(user1_events) == 2

    def test_export_json_with_filters(self):
        """Test JSON export with filtering."""
        with tempfile.TemporaryDirectory() as temp_dir:
            audit_file = os.path.join(temp_dir, "test_filter_export.log")

            # Enable audit trail and log different event types
            audit.enable(audit_file)

            audit.log_prompt("Test prompt", user_id="user1", conversation_id="conv1")
            audit.log_guardrail_decision(
                "test_filter", "block", "Test block", user_id="user1", conversation_id="conv1"
            )
            audit.log_response("Test response", user_id="user1", conversation_id="conv1")

            audit.disable()

            # Export only guardrail decisions
            json_file = os.path.join(temp_dir, "decisions_export.json")
            result_file = audit.export_json(
                destination=audit_file, output_file=json_file, event_type="guardrail_decision"
            )

            # Read JSON content
            with open(json_file, "r") as f:
                export_data = json.load(f)

            # Check that only guardrail decisions are exported
            records = export_data["records"]
            for record in records:
                assert record["event_type"] == "guardrail_decision"

            # Should have exactly 1 guardrail decision
            assert len(records) == 1
            assert records[0]["guardrail_name"] == "test_filter"
            assert records[0]["decision"] == "block"

    def test_export_auto_filename(self):
        """Test export with auto-generated filenames."""
        with tempfile.TemporaryDirectory() as temp_dir:
            audit_file = os.path.join(temp_dir, "test_auto.log")

            # Enable audit trail and log an event
            audit.enable(audit_file)
            audit.log_prompt("Test prompt", user_id="user1")
            audit.disable()

            # Export without specifying output file
            original_dir = os.getcwd()
            try:
                os.chdir(temp_dir)  # Change to temp dir for auto-generated files

                csv_file = audit.export_csv(destination=audit_file)
                json_file = audit.export_json(destination=audit_file)

                # Files should be created with auto-generated names
                assert csv_file.startswith("audit_export_")
                assert csv_file.endswith(".csv")
                assert os.path.exists(csv_file)

                assert json_file.startswith("audit_export_")
                assert json_file.endswith(".json")
                assert os.path.exists(json_file)

            finally:
                os.chdir(original_dir)

    def test_export_empty_audit_log(self):
        """Test export when audit log is empty."""
        with tempfile.TemporaryDirectory() as temp_dir:
            audit_file = os.path.join(temp_dir, "empty.log")

            # Create empty audit log
            with open(audit_file, "w") as f:
                pass

            # Export should handle empty logs gracefully
            csv_file = os.path.join(temp_dir, "empty_export.csv")
            json_file = os.path.join(temp_dir, "empty_export.json")

            csv_result = audit.export_csv(destination=audit_file, output_file=csv_file)
            json_result = audit.export_json(destination=audit_file, output_file=json_file)

            # Files should be created
            assert csv_result == csv_file
            assert json_result == json_file
            assert os.path.exists(csv_file)
            assert os.path.exists(json_file)

            # CSV should have headers only
            with open(csv_file, "r") as f:
                reader = csv.reader(f)
                rows = list(reader)
            assert len(rows) == 1  # Header row only

            # JSON should have empty records
            with open(json_file, "r") as f:
                export_data = json.load(f)
            assert export_data["total_records"] == 0
            assert len(export_data["records"]) == 0

    def test_export_nonexistent_audit_log(self):
        """Test export when audit log doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nonexistent_file = os.path.join(temp_dir, "doesnt_exist.log")
            csv_file = os.path.join(temp_dir, "export.csv")
            json_file = os.path.join(temp_dir, "export.json")

            # Should handle nonexistent files gracefully
            csv_result = audit.export_csv(destination=nonexistent_file, output_file=csv_file)
            json_result = audit.export_json(destination=nonexistent_file, output_file=json_file)

            # Should return empty results
            assert csv_result == csv_file
            assert json_result == json_file


if __name__ == "__main__":
    pytest.main([__file__])
