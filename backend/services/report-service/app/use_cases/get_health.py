from app.repositories import ReportsRepository
from app.schemas import HealthRead


class GetHealthUseCase:
    def __init__(self, reports_repository: ReportsRepository) -> None:
        self.reports_repository = reports_repository

    async def execute(self) -> HealthRead:
        return await self.reports_repository.get_health()
