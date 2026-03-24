"""Devices API — online/offline status for TV and Hue lights."""

from fastapi import APIRouter

from app.config import settings
from app.models.schemas import DeviceStatus, DeviceType, DevicesResponse
from app.services.ha_client import ha_client

router = APIRouter(prefix="/api/devices", tags=["devices"])


@router.get("/status", response_model=DevicesResponse)
async def get_device_status():
    devices: list[DeviceStatus] = []

    tv_status = await ha_client.get_device_status(settings.ha_tv_entity)
    tv_name = tv_status.get("attributes", {}).get("friendly_name", "LG TV")
    devices.append(
        DeviceStatus(
            name=tv_name,
            type=DeviceType.TV,
            online=tv_status["online"],
            state=tv_status["state"],
            entity_id=settings.ha_tv_entity,
        )
    )

    for entity_id in settings.light_entity_list:
        light_status = await ha_client.get_device_status(entity_id)
        light_name = light_status.get("attributes", {}).get("friendly_name", entity_id)
        devices.append(
            DeviceStatus(
                name=light_name,
                type=DeviceType.HUE,
                online=light_status["online"],
                state=light_status["state"],
                entity_id=entity_id,
            )
        )

    return DevicesResponse(devices=devices)
