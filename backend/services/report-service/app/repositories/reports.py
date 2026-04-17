from app.core.config import Settings
from app.schemas import CurrentUserRead, HealthRead


class ReportsRepository:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def get_health(self) -> HealthRead:
        return HealthRead(service=self.settings.service_name, status="ok")

    async def get_current_user(
        self,
        user_id: str | None,
        user_role: str | None,
        user_name: str | None,
    ) -> CurrentUserRead:
        return CurrentUserRead(
            service=self.settings.service_name,
            user_id=user_id,
            user_role=user_role,
            user_name=user_name,
        )
