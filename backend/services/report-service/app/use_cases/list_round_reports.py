from app.repositories import ReportsRepository
from app.schemas import RoundReportListItem


class ListRoundReportsUseCase:
    def __init__(self, reports_repository: ReportsRepository) -> None:
        self.reports_repository = reports_repository

    async def execute(
        self,
        status: str | None = None,
        employee_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[RoundReportListItem]:
        return await self.reports_repository.list_round_reports(
            status=status,
            employee_id=employee_id,
            limit=limit,
            offset=offset,
        )
