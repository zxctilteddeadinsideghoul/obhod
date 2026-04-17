import os

from fastapi import FastAPI, Header, Response, status


SERVICE_NAME = os.getenv("SERVICE_NAME", "auth-service")
DEV_AUTH_TOKEN = os.getenv("DEV_AUTH_TOKEN", "dev-token")

app = FastAPI(title=SERVICE_NAME)


@app.get("/api/auth/health")
async def health() -> dict[str, str]:
    return {"service": SERVICE_NAME, "status": "ok"}


@app.get("/api/auth/verify")
async def verify(
    response: Response,
    authorization: str | None = Header(default=None),
    x_forwarded_uri: str | None = Header(default=None),
    x_forwarded_method: str | None = Header(default=None),
) -> dict[str, str]:
    expected = f"Bearer {DEV_AUTH_TOKEN}"
    if authorization != expected:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"detail": "Unauthorized"}

    response.headers["X-User-Id"] = "dev-worker"
    response.headers["X-User-Role"] = "WORKER"
    response.headers["X-User-Name"] = "Development Worker"
    return {
        "status": "allowed",
        "method": x_forwarded_method or "",
        "uri": x_forwarded_uri or "",
    }


@app.get("/api/auth/me")
async def me() -> dict[str, str]:
    return {
        "id": "dev-worker",
        "role": "WORKER",
        "name": "Development Worker",
    }
