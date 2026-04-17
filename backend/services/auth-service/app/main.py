import os

from fastapi import FastAPI, Header, Response, status


SERVICE_NAME = os.getenv("SERVICE_NAME", "auth-service")
DEV_AUTH_TOKEN = os.getenv("DEV_AUTH_TOKEN", "dev-token")
DEV_ADMIN_TOKEN = os.getenv("DEV_ADMIN_TOKEN", "dev-admin-token")

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
    worker_token = f"Bearer {DEV_AUTH_TOKEN}"
    admin_token = f"Bearer {DEV_ADMIN_TOKEN}"
    if authorization not in {worker_token, admin_token}:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"detail": "Unauthorized"}

    is_admin = authorization == admin_token
    response.headers["X-User-Id"] = "dev-admin" if is_admin else "dev-worker"
    response.headers["X-User-Role"] = "ADMIN" if is_admin else "WORKER"
    response.headers["X-User-Name"] = "Development Admin" if is_admin else "Development Worker"
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
