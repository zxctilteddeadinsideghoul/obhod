from dataclasses import dataclass

from app.reports.documents import ReportDocument
from app.reports.renderers import CsvReportRenderer, JsonReportRenderer, PdfReportRenderer, ReportRenderer


@dataclass(frozen=True)
class ExportFile:
    content: bytes
    media_type: str
    file_name: str


class ReportExportService:
    def __init__(self, renderers: list[ReportRenderer] | None = None) -> None:
        renderer_list = renderers or [
            CsvReportRenderer(),
            JsonReportRenderer(),
            PdfReportRenderer(),
        ]
        self.renderers = {renderer.format: renderer for renderer in renderer_list}

    def export(self, document: ReportDocument, export_format: str) -> ExportFile:
        renderer = self.renderers.get(export_format)
        if renderer is None:
            raise ValueError("Unsupported export format")

        return ExportFile(
            content=renderer.render(document),
            media_type=renderer.media_type,
            file_name=f"{document.file_prefix}.{renderer.file_extension}",
        )
