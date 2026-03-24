"""Scene engine — orchestrates concurrent TV + light changes for each scene."""

import logging
from asyncio import gather
from pathlib import Path

import yaml

from app.models.schemas import SceneAction, SceneActivateResponse, SceneDefinition
from app.services.ha_client import ha_client

logger = logging.getLogger(__name__)

SCENES_FILE = Path(__file__).parent.parent.parent / "scenes" / "scenes.yaml"


def load_scenes() -> list[dict]:
    with open(SCENES_FILE) as f:
        data = yaml.safe_load(f)
    return data.get("scenes", [])


def get_scene_definitions() -> list[SceneDefinition]:
    raw_scenes = load_scenes()
    definitions = []
    for scene in raw_scenes:
        actions = [
            SceneAction(
                type=action["type"],
                target=action["target"],
                description=action.get("description", ""),
            )
            for action in scene.get("actions", [])
        ]
        definitions.append(
            SceneDefinition(
                name=scene["name"],
                display_name=scene["display_name"],
                description=scene["description"],
                icon=scene.get("icon", ""),
                time_of_day=scene.get("time_of_day", "any"),
                actions=actions,
            )
        )
    return definitions


def get_scene_by_name(name: str) -> dict | None:
    for scene in load_scenes():
        if scene["name"] == name:
            return scene
    return None


async def _execute_action(action: dict) -> str | None:
    """Execute a single scene action. Returns error string on failure."""
    action_type = action["type"]
    target = action["target"]
    description = action.get("description", target)

    try:
        if action_type == "tv_mode":
            # Direct Luna API call — instant picture mode change (~200ms)
            success = await ha_client.set_picture_mode(target)
            if not success:
                return f"Failed to set picture mode: {description}"

        elif action_type == "script":
            success = await ha_client.run_script(target)
            if not success:
                return f"Failed to run script: {description}"

        elif action_type == "light":
            brightness = action.get("brightness_pct")
            color_temp = action.get("color_temp_kelvin")
            turn_on = brightness is None or brightness > 0

            success = await ha_client.set_light(
                entity_id=target,
                brightness_pct=brightness,
                color_temp_kelvin=color_temp,
                turn_on=turn_on,
            )
            if not success:
                return f"Failed to set light: {description}"

        else:
            return f"Unknown action type: {action_type}"

    except Exception as e:
        logger.exception(f"Error executing action: {description}")
        return f"Error: {description} — {e}"

    return None


async def activate_scene(name: str) -> SceneActivateResponse:
    scene = get_scene_by_name(name)
    if scene is None:
        return SceneActivateResponse(
            scene=name,
            success=False,
            message=f"Scene '{name}' not found",
            errors=[f"No scene defined with name '{name}'"],
        )

    actions = scene.get("actions", [])
    if not actions:
        return SceneActivateResponse(
            scene=name,
            success=True,
            message="Scene has no actions",
            errors=[],
        )

    # Run all actions concurrently — lights change instantly while TV navigates menus
    results = await gather(*[_execute_action(action) for action in actions])
    errors = [r for r in results if r is not None]

    return SceneActivateResponse(
        scene=name,
        success=len(errors) == 0,
        message=(
            f"Scene '{scene['display_name']}' activated successfully"
            if not errors
            else f"Scene '{scene['display_name']}' had {len(errors)} error(s)"
        ),
        errors=errors,
    )
