from datetime import datetime

from app.repositories import ReportsRepository
from app.reports import AnalyticsReportDocument
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
        document = AnalyticsReportDocument(
            summary=summary,
            equipment=equipment,
            employees=employees,
            generated_at=datetime.utcnow().replace(microsecond=0),
        )
        return self.export_service.export(document, export_format)
