import os

from fastapi import FastAPI, Header


SERVICE_NAME = os.getenv("SERVICE_NAME", "report-service")

app = FastAPI(title=SERVICE_NAME)


@app.get("/api/reports/health")
async def health() -> dict[str, str]:
    return {"service": SERVICE_NAME, "status": "ok"}


@app.get("/api/reports/whoami")
async def whoami(
    x_user_id: str | None = Header(default=None),
    x_user_role: str | None = Header(default=None),
    x_user_name: str | None = Header(default=None),
) -> dict[str, str | None]:
    return {
        "service": SERVICE_NAME,
        "user_id": x_user_id,
        "user_role": x_user_role,
        "user_name": x_user_name,
    }
