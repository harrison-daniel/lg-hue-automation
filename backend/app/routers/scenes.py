"""Scenes API — list and activate scenes."""

from fastapi import APIRouter, HTTPException, Path, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.models.schemas import SceneActivateResponse, ScenesListResponse
from app.services.scene_engine import activate_scene, get_scene_definitions

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/api/scenes", tags=["scenes"])


@router.get("", response_model=ScenesListResponse)
async def list_scenes():
    scenes = get_scene_definitions()
    return ScenesListResponse(scenes=scenes)


@router.post("/{name}/activate", response_model=SceneActivateResponse)
@limiter.limit("10/minute")
async def activate_scene_endpoint(
    request: Request,
    name: str = Path(..., pattern=r"^[a-z0-9\-]+$", max_length=50),
):
    result = await activate_scene(name)

    if not result.success and "not found" in result.message:
        raise HTTPException(status_code=404, detail=result.message)

    return result
