from functools import lru_cache
from pydantic import BaseModel
import os


class Settings(BaseModel):
    service_name: str = "auth-service"
    database_url: str = "postgresql://obhod:obhod@postgres:5432/obhod"
    dev_auth_token: str = "dev-token"
    dev_admin_token: str = "dev-admin-token"
    auth_secret: str = "change-me-in-production"
    access_token_ttl_sec: int = 60 * 60 * 12
    worker_login: str = "worker"
    worker_password: str = "worker123"
    admin_login: str = "admin"
    admin_password: str = "admin123"


@lru_cache
def get_settings() -> Settings:
    return Settings(
        service_name=os.getenv("SERVICE_NAME", "auth-service"),
        database_url=os.getenv("DATABASE_URL", "postgresql://obhod:obhod@postgres:5432/obhod"),
        dev_auth_token=os.getenv("DEV_AUTH_TOKEN", "dev-token"),
        dev_admin_token=os.getenv("DEV_ADMIN_TOKEN", "dev-admin-token"),
        auth_secret=os.getenv("AUTH_SECRET", "change-me-in-production"),
        access_token_ttl_sec=int(os.getenv("ACCESS_TOKEN_TTL_SEC", str(60 * 60 * 12))),
        worker_login=os.getenv("WORKER_LOGIN", "worker"),
        worker_password=os.getenv("WORKER_PASSWORD", "worker123"),
        admin_login=os.getenv("ADMIN_LOGIN", "admin"),
        admin_password=os.getenv("ADMIN_PASSWORD", "admin123"),
    )
