"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ha_url: str = "http://localhost:8123"
    ha_token: str

    ha_tv_entity: str = "media_player.lg_webos_smart_tv"
    ha_light_entities: str = "light.living_room,light.bedroom"

    allowed_origins: str = ""

    @property
    def light_entity_list(self) -> list[str]:
        return [e.strip() for e in self.ha_light_entities.split(",") if e.strip()]

    @property
    def allowed_origins_list(self) -> list[str]:
        if not self.allowed_origins:
            return []
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
    }


settings = Settings()
