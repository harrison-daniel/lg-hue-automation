"""Tests for the scenes API and scene engine."""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.main import app

app.state.limiter = Limiter(key_func=get_remote_address)

client = TestClient(app)


class TestScenesEndpoints:
    def test_list_scenes(self):
        response = client.get("/api/scenes")

        assert response.status_code == 200
        data = response.json()
        assert "scenes" in data
        assert len(data["scenes"]) > 0

        scene = data["scenes"][0]
        assert "name" in scene
        assert "display_name" in scene
        assert "description" in scene
        assert "actions" in scene

    def test_list_scenes_contains_expected_scenes(self):
        response = client.get("/api/scenes")
        data = response.json()

        scene_names = [s["name"] for s in data["scenes"]]
        assert "night-tv" in scene_names
        assert "night-gaming" in scene_names
        assert "night-movie" in scene_names
        assert "day-tv" in scene_names
        assert "day-gaming" in scene_names
        assert "day-movie" in scene_names
        assert "all-off" in scene_names

    def test_scenes_have_time_of_day(self):
        response = client.get("/api/scenes")
        data = response.json()

        for scene in data["scenes"]:
            assert "time_of_day" in scene
            assert scene["time_of_day"] in ("day", "night", "any")

    @patch("app.services.scene_engine.ha_client")
    def test_activate_scene_success(self, mock_ha):
        mock_ha.set_picture_mode = AsyncMock(return_value=True)
        mock_ha.run_script = AsyncMock(return_value=True)
        mock_ha.set_light = AsyncMock(return_value=True)

        response = client.post("/api/scenes/night-tv/activate")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["scene"] == "night-tv"
        assert len(data["errors"]) == 0

    @patch("app.services.scene_engine.ha_client")
    def test_activate_scene_partial_failure(self, mock_ha):
        mock_ha.set_picture_mode = AsyncMock(return_value=True)
        mock_ha.run_script = AsyncMock(return_value=True)
        mock_ha.set_light = AsyncMock(side_effect=[False, True])

        response = client.post("/api/scenes/night-tv/activate")

        data = response.json()
        assert data["success"] is False
        assert len(data["errors"]) > 0

    def test_activate_nonexistent_scene(self):
        response = client.post("/api/scenes/nonexistent/activate")
        assert response.status_code == 404


class TestHealthEndpoint:
    @patch("app.main.ha_client")
    def test_health_check_connected(self, mock_ha):
        mock_ha.is_connected = AsyncMock(return_value=True)

        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["ha_connected"] is True

    @patch("app.main.ha_client")
    def test_health_check_disconnected(self, mock_ha):
        mock_ha.is_connected = AsyncMock(return_value=False)

        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["ha_connected"] is False
