from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "model"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    app_name: str = "Ovarian Cancer AI"
    app_env: str = "development"
    secret_key: str = "dev-secret-change-me"
    iot_device_token: str = "dev-device-token"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    database_url: str = f"sqlite:///{(BASE_DIR / 'ovarian_ai.db').as_posix()}"
    risk_low_threshold: float = 0.30
    risk_high_threshold: float = 0.70
    host: str = "0.0.0.0"
    port: int = 5000

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
