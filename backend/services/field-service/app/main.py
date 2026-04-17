from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import api_router
from app.containers import Container
from app.db import engine


container = Container()
container.wire(modules=["app.api.dependencies"])


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        yield
    finally:
        await engine.dispose()


app = FastAPI(title="Obhod Field Service", lifespan=lifespan)
app.container = container  # type: ignore[attr-defined]
app.include_router(api_router)
