"""Server diagnostics — reads CPU temp, disk, memory, and uptime via psutil."""

import logging
import time
from pathlib import Path

import psutil

logger = logging.getLogger(__name__)

# When running inside Docker with /sys mounted to /host/sys
HOST_SYS_THERMAL = Path("/host/sys/class/thermal")
CONTAINER_SYS_THERMAL = Path("/sys/class/thermal")


def _read_thermal_zones() -> list[dict]:
    """Read CPU temps directly from sysfs (fallback for Docker)."""
    thermal_base = (
        HOST_SYS_THERMAL if HOST_SYS_THERMAL.exists() else CONTAINER_SYS_THERMAL
    )
    temps = []

    if not thermal_base.exists():
        return temps

    for zone in sorted(thermal_base.glob("thermal_zone*")):
        temp_file = zone / "temp"
        type_file = zone / "type"
        if not temp_file.exists():
            continue
        try:
            millidegrees = int(temp_file.read_text().strip())
            label = type_file.read_text().strip() if type_file.exists() else zone.name
            temps.append({
                "label": label,
                "current": millidegrees / 1000.0,
                "high": None,
                "critical": None,
            })
        except (ValueError, OSError):
            continue

    return temps


def get_cpu_temperatures() -> list[dict]:
    """Get CPU temperatures. Tries psutil first, falls back to sysfs."""
    try:
        sensor_data = psutil.sensors_temperatures()
        if sensor_data:
            temps = []
            for _chip, entries in sensor_data.items():
                for entry in entries:
                    temps.append({
                        "label": entry.label or "CPU",
                        "current": entry.current,
                        "high": entry.high,
                        "critical": entry.critical,
                    })
            return temps
    except (AttributeError, OSError):
        # psutil.sensors_temperatures() not available on this platform
        pass

    return _read_thermal_zones()


def get_disk_usage() -> dict:
    total, used, free, percent = psutil.disk_usage("/")
    return {
        "total_gb": round(total / (1024**3), 1),
        "used_gb": round(used / (1024**3), 1),
        "free_gb": round(free / (1024**3), 1),
        "percent": percent,
    }


def get_memory_usage() -> dict:
    mem = psutil.virtual_memory()
    return {
        "total_gb": round(mem.total / (1024**3), 1),
        "used_gb": round(mem.used / (1024**3), 1),
        "available_gb": round(mem.available / (1024**3), 1),
        "percent": mem.percent,
    }


def get_cpu_percent() -> float:
    return psutil.cpu_percent(interval=0.1)


def _format_uptime(seconds: float) -> str:
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    parts.append(f"{minutes}m")
    return " ".join(parts)


def get_uptime() -> tuple[float, str]:
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    return uptime_seconds, _format_uptime(uptime_seconds)


def get_diagnostics() -> dict:
    """Aggregate all system diagnostics into a single response."""
    uptime_seconds, uptime_human = get_uptime()
    return {
        "cpu_temps": get_cpu_temperatures(),
        "disk": get_disk_usage(),
        "memory": get_memory_usage(),
        "cpu_percent": get_cpu_percent(),
        "uptime_seconds": uptime_seconds,
        "uptime_human": uptime_human,
    }
