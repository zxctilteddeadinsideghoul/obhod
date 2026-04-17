from app.repositories import ReportsRepository
from app.services.report_export import ExportFile, ReportExportService


class ExportReportsAnalyticsUseCase:
    def __init__(
        self,
        reports_repository: ReportsRepository,
        export_service: ReportExportService,
    ) -> None:
        self.reports_repository = reports_repository
        self.export_service = export_service

    async def execute(self, export_format: str, limit: int = 20) -> ExportFile:
        summary = await self.reports_repository.get_summary()
        equipment = await self.reports_repository.get_equipment_analytics(limit=limit)
        employees = await self.reports_repository.get_employee_analytics(limit=limit)
        return self.export_service.export_analytics(summary, equipment, employees, export_format)
