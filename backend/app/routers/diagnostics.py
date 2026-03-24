"""Router for server diagnostics — CPU temp, disk, memory, uptime."""

from fastapi import APIRouter

from app.models.schemas import DiagnosticsResponse
from app.services.diagnostics import get_diagnostics

router = APIRouter(prefix="/api/diagnostics", tags=["diagnostics"])


@router.get("", response_model=DiagnosticsResponse)
async def server_diagnostics():
    """Return current server health metrics."""
    return get_diagnostics()
