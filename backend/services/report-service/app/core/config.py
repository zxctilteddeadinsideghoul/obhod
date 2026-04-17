from functools import lru_cache
import os

from pydantic import BaseModel


class Settings(BaseModel):
    service_name: str = "report-service"
    database_url: str = "postgresql://obhod:obhod@postgres:5432/obhod"

    @property
    def sqlalchemy_database_url(self) -> str:
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings(
        service_name=os.getenv("SERVICE_NAME", "report-service"),
        database_url=os.getenv("DATABASE_URL", "postgresql://obhod:obhod@postgres:5432/obhod"),
    )
