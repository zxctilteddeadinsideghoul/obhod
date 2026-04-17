from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import api_router
from app.containers import Container
from app.db import Base, engine


container = Container()
container.wire(packages=["app.api.routes"])


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    try:
        yield
    finally:
        await engine.dispose()


app = FastAPI(title="Obhod Field Service", lifespan=lifespan)
app.container = container  # type: ignore[attr-defined]
app.include_router(api_router)
