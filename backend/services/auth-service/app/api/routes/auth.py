from fastapi import APIRouter, Depends, Header, Response, status

from app.api.dependencies import get_current_user_use_case, get_verify_access_use_case
from app.core.config import get_settings
from app.schemas import PrincipalRead
from app.use_cases import GetCurrentUserUseCase, VerifyAccessUseCase


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"service": get_settings().service_name, "status": "ok"}


@router.get("/verify")
async def verify(
    response: Response,
    authorization: str | None = Header(default=None),
    x_forwarded_uri: str | None = Header(default=None),
    x_forwarded_method: str | None = Header(default=None),
    use_case: VerifyAccessUseCase = Depends(get_verify_access_use_case),
) -> dict[str, str]:
    verification = await use_case.execute(authorization, x_forwarded_method, x_forwarded_uri)
    if verification is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"detail": "Unauthorized"}

    response.headers["X-User-Id"] = verification.principal.id
    response.headers["X-User-Role"] = verification.principal.role
    response.headers["X-User-Name"] = verification.principal.name
    return {
        "status": verification.status,
        "method": verification.method,
        "uri": verification.uri,
    }


@router.get("/me", response_model=PrincipalRead)
async def me(
    authorization: str | None = Header(default=None),
    use_case: GetCurrentUserUseCase = Depends(get_current_user_use_case),
) -> PrincipalRead:
    principal = await use_case.execute(authorization)
    return principal or PrincipalRead(id="dev-worker", role="WORKER", name="Development Worker")
