from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import api_router
from app.containers import Container
from app.core.config import get_settings
from app.db import engine


settings = get_settings()
container = Container(settings=settings)


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        yield
    finally:
        await engine.dispose()


app = FastAPI(title=settings.service_name, lifespan=lifespan)
app.container = container  # type: ignore[attr-defined]
app.include_router(api_router)
