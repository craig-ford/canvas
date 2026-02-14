from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_prefix="CANVAS_", case_sensitive=False)
    
    database_url: str
    cors_origins: list[str]
    log_level: str = "INFO"
    secret_key: str
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    upload_dir: str = "/uploads"
    max_upload_size_mb: int = 10