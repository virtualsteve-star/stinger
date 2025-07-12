"""
Test metrics collection and endpoint.
"""

import json

import pytest

try:
    from fastapi.testclient import TestClient

    from stinger.api import metrics
    from stinger.api.app import app
except ImportError:
    pytest.skip("FastAPI not installed, skipping API tests", allow_module_level=True)


@pytest.fixture
def client():
    # Reset metrics for each test
    metrics._metrics = metrics.MetricsCollector()
    return TestClient(app)


@pytest.mark.ci
def test_metrics_endpoint_json(client):
    """Test metrics endpoint returns JSON format."""
    response = client.get("/metrics?format=json")
    assert response.status_code == 200

    data = response.json()
    assert "uptime_seconds" in data
    assert "counters" in data
    assert "gauges" in data
    assert "histograms" in data
    assert "rates" in data


@pytest.mark.ci
def test_metrics_endpoint_prometheus(client):
    """Test metrics endpoint returns Prometheus format."""
    response = client.get("/metrics?format=prometheus")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; version=0.0.4; charset=utf-8"

    content = response.text
    assert "# TYPE" in content


@pytest.mark.ci
def test_request_metrics_recorded(client):
    """Test that API requests are recorded in metrics."""
    # Make some API calls
    client.get("/health")
    client.post("/v1/check", json={"text": "test", "kind": "prompt"})

    # Check metrics
    response = client.get("/metrics")
    data = response.json()

    # Should have request counters
    assert any("api_requests_total" in key for key in data["counters"])

    # Should have request duration histograms
    assert any("api_request_duration_ms" in key for key in data["histograms"])


@pytest.mark.ci
def test_guardrail_metrics_recorded(client):
    """Test that guardrail checks are recorded in metrics."""
    # Make a check that triggers guardrails
    client.post("/v1/check", json={"text": "This is a test message", "kind": "prompt"})

    # Check metrics
    response = client.get("/metrics")
    data = response.json()

    # Should have guardrail counters
    assert any("guardrail_checks_total" in key for key in data["counters"])


@pytest.mark.ci
def test_error_metrics_recorded(client):
    """Test that errors are recorded in metrics."""
    # Trigger an error
    client.post(
        "/v1/check", json={"text": "", "kind": "prompt"}  # Empty text should fail validation
    )

    # Check metrics
    response = client.get("/metrics")
    data = response.json()

    # Should have error counters
    assert any("api_errors_total" in key for key in data["counters"])


@pytest.mark.ci
def test_response_time_header(client):
    """Test that response time is added to headers."""
    response = client.get("/health")
    assert "X-Response-Time" in response.headers
    assert response.headers["X-Response-Time"].endswith("ms")


@pytest.mark.ci
def test_metrics_collector_unit():
    """Test MetricsCollector functionality directly."""
    collector = metrics.MetricsCollector()

    # Test counter
    collector.increment("test_counter", 5)
    collector.increment("test_counter", 3)
    summary = collector.get_metrics_summary()
    assert summary["counters"]["test_counter"] == 8

    # Test gauge
    collector.set_gauge("test_gauge", 42.5)
    summary = collector.get_metrics_summary()
    assert summary["gauges"]["test_gauge"] == 42.5

    # Test histogram
    collector.record_value("test_histogram", 10)
    collector.record_value("test_histogram", 20)
    collector.record_value("test_histogram", 30)
    summary = collector.get_metrics_summary()

    hist_stats = summary["histograms"]["test_histogram"]
    assert hist_stats["count"] == 3
    assert hist_stats["min"] == 10
    assert hist_stats["max"] == 30
    assert hist_stats["avg"] == 20

    # Test labels
    collector.increment("labeled_metric", 1, {"env": "test", "version": "1.0"})
    summary = collector.get_metrics_summary()
    assert "labeled_metric{env=test,version=1.0}" in summary["counters"]
