from functools import lru_cache
import os

from pydantic import BaseModel


class Settings(BaseModel):
    service_name: str = "report-service"


@lru_cache
def get_settings() -> Settings:
    return Settings(service_name=os.getenv("SERVICE_NAME", "report-service"))
