from app.repositories import ReportsRepository
from app.reports import RoundReportDocument
from app.services.report_export import ExportFile, ReportExportService


class ExportRoundReportUseCase:
    def __init__(
        self,
        reports_repository: ReportsRepository,
        export_service: ReportExportService,
    ) -> None:
        self.reports_repository = reports_repository
        self.export_service = export_service

    async def execute(self, round_id: str, export_format: str) -> ExportFile | None:
        report = await self.reports_repository.get_round_report(round_id)
        if report is None:
            return None
        return self.export_service.export(RoundReportDocument(report), export_format)
