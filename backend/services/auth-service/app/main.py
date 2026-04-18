from fastapi import FastAPI

from app.api import api_router
from app.containers import Container
from app.core.config import get_settings


settings = get_settings()
container = Container(settings=settings)

app = FastAPI(title=settings.service_name)
app.container = container  # type: ignore[attr-defined]
app.include_router(api_router)


@app.on_event("startup")
async def startup() -> None:
    await container.tokens_repository().initialize_storage()
