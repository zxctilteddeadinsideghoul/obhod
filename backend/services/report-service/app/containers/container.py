from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.repositories import ReportsRepository
from app.use_cases import (
    GetCurrentUserUseCase,
    GetEmployeeAnalyticsUseCase,
    GetEquipmentAnalyticsUseCase,
    GetHealthUseCase,
    GetReportsSummaryUseCase,
    GetRoundReportUseCase,
    ListRoundReportsUseCase,
)


class Container:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def reports_repository(self, session: AsyncSession) -> ReportsRepository:
        return ReportsRepository(settings=self.settings, session=session)

    def get_health_use_case(self, session: AsyncSession) -> GetHealthUseCase:
        return GetHealthUseCase(reports_repository=self.reports_repository(session))

    def get_current_user_use_case(self, session: AsyncSession) -> GetCurrentUserUseCase:
        return GetCurrentUserUseCase(reports_repository=self.reports_repository(session))

    def list_round_reports_use_case(self, session: AsyncSession) -> ListRoundReportsUseCase:
        return ListRoundReportsUseCase(reports_repository=self.reports_repository(session))

    def get_round_report_use_case(self, session: AsyncSession) -> GetRoundReportUseCase:
        return GetRoundReportUseCase(reports_repository=self.reports_repository(session))

    def get_reports_summary_use_case(self, session: AsyncSession) -> GetReportsSummaryUseCase:
        return GetReportsSummaryUseCase(reports_repository=self.reports_repository(session))

    def get_equipment_analytics_use_case(self, session: AsyncSession) -> GetEquipmentAnalyticsUseCase:
        return GetEquipmentAnalyticsUseCase(reports_repository=self.reports_repository(session))

    def get_employee_analytics_use_case(self, session: AsyncSession) -> GetEmployeeAnalyticsUseCase:
        return GetEmployeeAnalyticsUseCase(reports_repository=self.reports_repository(session))
