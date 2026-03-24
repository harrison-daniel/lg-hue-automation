"""Pydantic models for API request/response validation."""

from enum import Enum

from pydantic import BaseModel


class DeviceType(str, Enum):
    TV = "tv"
    HUE = "hue"


class DeviceStatus(BaseModel):
    name: str
    type: DeviceType
    online: bool
    state: str
    entity_id: str


class DevicesResponse(BaseModel):
    devices: list[DeviceStatus]


class SceneAction(BaseModel):
    type: str
    target: str
    description: str


class SceneDefinition(BaseModel):
    name: str
    display_name: str
    description: str
    icon: str
    time_of_day: str = "any"
    actions: list[SceneAction]


class ScenesListResponse(BaseModel):
    scenes: list[SceneDefinition]


class SceneActivateResponse(BaseModel):
    scene: str
    success: bool
    message: str
    errors: list[str]


class HealthResponse(BaseModel):
    status: str
    version: str
    ha_connected: bool


# --- Diagnostics models ---


class CpuTemperature(BaseModel):
    label: str
    current: float
    high: float | None = None
    critical: float | None = None


class DiskUsage(BaseModel):
    total_gb: float
    used_gb: float
    free_gb: float
    percent: float


class MemoryUsage(BaseModel):
    total_gb: float
    used_gb: float
    available_gb: float
    percent: float


class DiagnosticsResponse(BaseModel):
    cpu_temps: list[CpuTemperature]
    disk: DiskUsage
    memory: MemoryUsage
    cpu_percent: float
    uptime_seconds: float
    uptime_human: str
