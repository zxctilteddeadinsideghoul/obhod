from functools import lru_cache
from pydantic import BaseModel
import os


class Settings(BaseModel):
    service_name: str = "auth-service"
    dev_auth_token: str = "dev-token"
    dev_admin_token: str = "dev-admin-token"


@lru_cache
def get_settings() -> Settings:
    return Settings(
        service_name=os.getenv("SERVICE_NAME", "auth-service"),
        dev_auth_token=os.getenv("DEV_AUTH_TOKEN", "dev-token"),
        dev_admin_token=os.getenv("DEV_ADMIN_TOKEN", "dev-admin-token"),
    )
