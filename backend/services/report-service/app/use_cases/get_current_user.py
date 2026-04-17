from app.repositories import ReportsRepository
from app.schemas import CurrentUserRead


class GetCurrentUserUseCase:
    def __init__(self, reports_repository: ReportsRepository) -> None:
        self.reports_repository = reports_repository

    async def execute(
        self,
        user_id: str | None,
        user_role: str | None,
        user_name: str | None,
    ) -> CurrentUserRead:
        return await self.reports_repository.get_current_user(user_id, user_role, user_name)
