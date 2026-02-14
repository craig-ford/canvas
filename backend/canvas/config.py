from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_prefix="CANVAS_", case_sensitive=False)
    
    database_url: str
    cors_origins: list[str]
    log_level: str = "INFO"
    secret_key: str