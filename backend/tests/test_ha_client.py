"""Tests for the Home Assistant API client."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.ha_client import HAClient


@pytest.fixture
def ha():
    with patch("app.services.ha_client.settings") as mock_settings:
        mock_settings.ha_url = "http://localhost:8123"
        mock_settings.ha_token = "test-token-123"
        client = HAClient()
        yield client


class TestHAClient:
    @pytest.mark.asyncio
    async def test_call_service_constructs_correct_request(self, ha):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.is_closed = False
        ha._client = mock_client

        result = await ha.call_service(
            domain="light",
            service="turn_on",
            entity_id="light.living_room",
            data={"brightness_pct": 50},
        )

        assert result is True
        mock_client.post.assert_called_once_with(
            "/api/services/light/turn_on",
            json={
                "entity_id": "light.living_room",
                "brightness_pct": 50,
            },
        )

    @pytest.mark.asyncio
    async def test_run_script_calls_correct_service(self, ha):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.is_closed = False
        ha._client = mock_client

        await ha.run_script("tv_picture_cinema")

        mock_client.post.assert_called_once_with(
            "/api/services/script/turn_on",
            json={"entity_id": "script.tv_picture_cinema"},
        )

    @pytest.mark.asyncio
    async def test_set_light_turn_off(self, ha):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.is_closed = False
        ha._client = mock_client

        await ha.set_light("light.bedroom", turn_on=False)

        mock_client.post.assert_called_once_with(
            "/api/services/light/turn_off",
            json={"entity_id": "light.bedroom"},
        )

    @pytest.mark.asyncio
    async def test_is_connected_returns_false_on_error(self, ha):
        import httpx

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.ConnectError("refused"))
        mock_client.is_closed = False
        ha._client = mock_client

        result = await ha.is_connected()
        assert result is False
