from app.repositories import ReportsRepository
from app.schemas import EmployeeAnalyticsItem


class GetEmployeeAnalyticsUseCase:
    def __init__(self, reports_repository: ReportsRepository) -> None:
        self.reports_repository = reports_repository

    async def execute(self, limit: int = 20) -> list[EmployeeAnalyticsItem]:
        return await self.reports_repository.get_employee_analytics(limit=limit)
