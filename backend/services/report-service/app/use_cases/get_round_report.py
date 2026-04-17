from app.repositories import ReportsRepository
from app.schemas import RoundReportDetail


class GetRoundReportUseCase:
    def __init__(self, reports_repository: ReportsRepository) -> None:
        self.reports_repository = reports_repository

    async def execute(self, round_id: str) -> RoundReportDetail | None:
        return await self.reports_repository.get_round_report(round_id)
