from app.repositories import ReportsRepository
from app.schemas import ReportsSummary


class GetReportsSummaryUseCase:
    def __init__(self, reports_repository: ReportsRepository) -> None:
        self.reports_repository = reports_repository

    async def execute(self) -> ReportsSummary:
        return await self.reports_repository.get_summary()
