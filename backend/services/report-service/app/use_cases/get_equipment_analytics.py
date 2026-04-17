from app.repositories import ReportsRepository
from app.schemas import EquipmentAnalyticsItem


class GetEquipmentAnalyticsUseCase:
    def __init__(self, reports_repository: ReportsRepository) -> None:
        self.reports_repository = reports_repository

    async def execute(self, limit: int = 20) -> list[EquipmentAnalyticsItem]:
        return await self.reports_repository.get_equipment_analytics(limit=limit)
