from fastapi import APIRouter, Depends, Header

from app.api.dependencies import get_current_user_use_case, get_health_use_case
from app.schemas import CurrentUserRead, HealthRead
from app.use_cases import GetCurrentUserUseCase, GetHealthUseCase


router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/health", response_model=HealthRead)
async def health(
    use_case: GetHealthUseCase = Depends(get_health_use_case),
) -> HealthRead:
    return await use_case.execute()


@router.get("/whoami", response_model=CurrentUserRead)
async def whoami(
    x_user_id: str | None = Header(default=None),
    x_user_role: str | None = Header(default=None),
    x_user_name: str | None = Header(default=None),
    use_case: GetCurrentUserUseCase = Depends(get_current_user_use_case),
) -> CurrentUserRead:
    return await use_case.execute(x_user_id, x_user_role, x_user_name)
