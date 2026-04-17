from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import api_router
from app.containers import Container
from app.db import engine
from app.migrations import run_migrations


container = Container()
container.wire(modules=["app.api.dependencies"])


@asynccontextmanager
async def lifespan(_: FastAPI):
    await run_migrations()

    try:
        yield
    finally:
        await engine.dispose()


app = FastAPI(title="Obhod Field Service", lifespan=lifespan)
app.container = container  # type: ignore[attr-defined]
app.include_router(api_router)
