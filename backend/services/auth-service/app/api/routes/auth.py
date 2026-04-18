from fastapi import APIRouter, Depends, Header, HTTPException, Response, status

from app.api.dependencies import (
    get_create_worker_use_case,
    get_current_user_use_case,
    get_login_use_case,
    get_verify_access_use_case,
)
from app.core.config import get_settings
from app.schemas import LoginRequest, LoginResponse, PrincipalRead, WorkerCreate, WorkerRead
from app.use_cases import CreateWorkerUseCase, GetCurrentUserUseCase, LoginUseCase, VerifyAccessUseCase


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"service": get_settings().service_name, "status": "ok"}


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    use_case: LoginUseCase = Depends(get_login_use_case),
) -> LoginResponse:
    result = await use_case.execute(payload.username, payload.password)
    if result is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    return result


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
    if principal is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return principal


@router.post("/admin/workers", response_model=WorkerRead, status_code=status.HTTP_201_CREATED)
async def create_worker(
    payload: WorkerCreate,
    authorization: str | None = Header(default=None),
    current_user_use_case: GetCurrentUserUseCase = Depends(get_current_user_use_case),
    create_worker_use_case: CreateWorkerUseCase = Depends(get_create_worker_use_case),
) -> WorkerRead:
    principal = await current_user_use_case.execute(authorization)
    if principal is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    try:
        return await create_worker_use_case.execute(payload, principal)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except FileExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
