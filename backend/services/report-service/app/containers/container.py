from app.core.config import Settings
from app.repositories import ReportsRepository
from app.use_cases import GetCurrentUserUseCase, GetHealthUseCase


class Container:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def reports_repository(self) -> ReportsRepository:
        return ReportsRepository(settings=self.settings)

    def get_health_use_case(self) -> GetHealthUseCase:
        return GetHealthUseCase(reports_repository=self.reports_repository())

    def get_current_user_use_case(self) -> GetCurrentUserUseCase:
        return GetCurrentUserUseCase(reports_repository=self.reports_repository())
