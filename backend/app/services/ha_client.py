"""Home Assistant REST API client — bridge between our backend and HA."""

import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class HAClient:
    def __init__(self) -> None:
        self._base_url = settings.ha_url.rstrip("/")
        self._headers = {
            "Authorization": f"Bearer {settings.ha_token}",
            "Content-Type": "application/json",
        }
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                headers=self._headers,
                timeout=30.0,
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def get_state(self, entity_id: str) -> dict:
        client = await self._get_client()
        response = await client.get(f"/api/states/{entity_id}")
        response.raise_for_status()
        return response.json()

    async def is_connected(self) -> bool:
        try:
            client = await self._get_client()
            response = await client.get("/api/")
            return response.status_code == 200
        except httpx.HTTPError:
            return False

    async def get_device_status(self, entity_id: str) -> dict:
        try:
            state_data = await self.get_state(entity_id)
            state = state_data.get("state", "unavailable")
            return {
                "online": state != "unavailable",
                "state": state,
                "attributes": state_data.get("attributes", {}),
            }
        except httpx.HTTPError as e:
            logger.error(f"Failed to get state for {entity_id}: {e}")
            return {"online": False, "state": "unavailable", "attributes": {}}

    async def call_service(
        self,
        domain: str,
        service: str,
        entity_id: str | None = None,
        data: dict | None = None,
    ) -> bool:
        payload: dict = {}
        if entity_id:
            payload["entity_id"] = entity_id
        if data:
            payload.update(data)

        try:
            client = await self._get_client()
            response = await client.post(
                f"/api/services/{domain}/{service}",
                json=payload,
            )
            response.raise_for_status()
            logger.info(f"Service call: {domain}.{service} → {entity_id}")
            return True
        except httpx.HTTPError as e:
            logger.error(f"Service call failed: {domain}.{service} → {e}")
            return False

    async def run_script(self, script_name: str) -> bool:
        return await self.call_service("script", "turn_on", f"script.{script_name}")

    async def activate_scene(self, scene_entity_id: str) -> bool:
        return await self.call_service("scene", "turn_on", scene_entity_id)

    async def send_button(self, button: str, entity_id: str | None = None) -> bool:
        target = entity_id or settings.ha_tv_entity
        return await self.call_service(
            domain="webostv",
            service="button",
            entity_id=target,
            data={"button": button},
        )

    async def set_picture_mode(self, mode: str, entity_id: str | None = None) -> bool:
        """Set TV picture mode via button navigation."""
        import asyncio

        target = entity_id or settings.ha_tv_entity

        # LG C1 picture mode menu positions from top:
        # Vivid(0), Standard(1), Eco(2), Cinema(3),
        # Sports(4), Game(5), Filmmaker(6)
        mode_positions = {
            "vivid": 0,
            "standard": 1,
            "eco": 2,
            "cinema": 3,
            "sports": 4,
            "game": 5,
            "filmmaker": 6,
        }

        position = mode_positions.get(mode)
        if position is None:
            logger.error(f"Unknown picture mode: {mode}")
            return False

        steps = [
            ("MENU", 1.5),
            ("DOWN", 0.4),
            ("ENTER", 0.8),
            ("ENTER", 0.8),
        ]

        # Navigate to the correct mode position
        for _ in range(position):
            steps.append(("DOWN", 0.3))

        steps.append(("ENTER", 0.5))
        steps.append(("EXIT", 0))

        for button, delay in steps:
            success = await self.send_button(button, target)
            if not success:
                logger.error(f"Button press failed: {button}")
                return False
            if delay > 0:
                await asyncio.sleep(delay)

        return True

    async def set_light(
        self,
        entity_id: str,
        brightness_pct: int | None = None,
        color_temp_kelvin: int | None = None,
        turn_on: bool = True,
    ) -> bool:
        if not turn_on:
            return await self.call_service("light", "turn_off", entity_id)

        data: dict = {}
        if brightness_pct is not None:
            data["brightness_pct"] = max(0, min(100, brightness_pct))
        if color_temp_kelvin is not None:
            data["kelvin"] = color_temp_kelvin

        return await self.call_service("light", "turn_on", entity_id, data)


ha_client = HAClient()
