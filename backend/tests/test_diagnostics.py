"""Tests for the server diagnostics endpoint."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestDiagnosticsEndpoint:
    @patch("app.routers.diagnostics.get_diagnostics")
    def test_diagnostics_returns_200(self, mock_diag):
        mock_diag.return_value = {
            "cpu_temps": [{"label": "CPU", "current": 55.0, "high": 80.0, "critical": 100.0}],
            "disk": {"total_gb": 113.0, "used_gb": 22.0, "free_gb": 91.0, "percent": 19.5},
            "memory": {"total_gb": 3.7, "used_gb": 1.2, "available_gb": 2.5, "percent": 32.4},
            "cpu_percent": 12.3,
            "uptime_seconds": 86400.0,
            "uptime_human": "1d 0h 0m",
        }

        response = client.get("/api/diagnostics")

        assert response.status_code == 200
        data = response.json()
        assert "cpu_temps" in data
        assert "disk" in data
        assert "memory" in data
        assert "uptime_human" in data
        assert data["cpu_temps"][0]["current"] == 55.0
        assert data["disk"]["percent"] == 19.5

    @patch("app.routers.diagnostics.get_diagnostics")
    def test_diagnostics_empty_temps(self, mock_diag):
        """Graceful response when temperature sensors are unavailable."""
        mock_diag.return_value = {
            "cpu_temps": [],
            "disk": {"total_gb": 113.0, "used_gb": 22.0, "free_gb": 91.0, "percent": 19.5},
            "memory": {"total_gb": 3.7, "used_gb": 1.2, "available_gb": 2.5, "percent": 32.4},
            "cpu_percent": 5.0,
            "uptime_seconds": 3600.0,
            "uptime_human": "1h 0m",
        }

        response = client.get("/api/diagnostics")
        assert response.status_code == 200
        assert response.json()["cpu_temps"] == []


class TestDiagnosticsService:
    def test_format_uptime(self):
        from app.services.diagnostics import _format_uptime

        assert _format_uptime(90061) == "1d 1h 1m"
        assert _format_uptime(3661) == "1h 1m"
        assert _format_uptime(300) == "5m"
        assert _format_uptime(0) == "0m"
