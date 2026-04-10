from fastapi.templating import Jinja2Templates
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    secret_key: str
    cookie_secure: bool = True

    redis_url: str = "redis://localhost:6379/0"

    r2_endpoint: str = ""
    r2_access_key: str = ""
    r2_secret_key: str = ""
    r2_bucket_name: str = ""
    r2_public_url: str = ""


settings = Settings()
templates = Jinja2Templates(directory="src/templates")
