import csv
import io
import json
import textwrap
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel

from app.schemas import (
    EmployeeAnalyticsItem,
    EquipmentAnalyticsItem,
    ReportsSummary,
    RoundReportDetail,
)


@dataclass(frozen=True)
class ExportFile:
    content: bytes
    media_type: str
    file_name: str


class ReportExportService:
    def export_round_report(self, report: RoundReportDetail, export_format: str) -> ExportFile:
        if export_format == "json":
            return ExportFile(
                content=self._json_bytes(report),
                media_type="application/json",
                file_name=f"round-report-{report.round.id}.json",
            )
        if export_format == "csv":
            return ExportFile(
                content=self._round_report_csv(report),
                media_type="text/csv; charset=utf-8",
                file_name=f"round-report-{report.round.id}.csv",
            )
        if export_format == "pdf":
            return ExportFile(
                content=self._round_report_pdf(report),
                media_type="application/pdf",
                file_name=f"round-report-{report.round.id}.pdf",
            )
        raise ValueError("Unsupported export format")

    def export_analytics(
        self,
        summary: ReportsSummary,
        equipment: list[EquipmentAnalyticsItem],
        employees: list[EmployeeAnalyticsItem],
        export_format: str,
    ) -> ExportFile:
        generated_at = datetime.utcnow().replace(microsecond=0)
        if export_format == "json":
            return ExportFile(
                content=self._json_bytes(
                    {
                        "generated_at": generated_at,
                        "summary": summary,
                        "equipment": equipment,
                        "employees": employees,
                    }
                ),
                media_type="application/json",
                file_name="reports-analytics.json",
            )
        if export_format == "csv":
            return ExportFile(
                content=self._analytics_csv(summary, equipment, employees, generated_at),
                media_type="text/csv; charset=utf-8",
                file_name="reports-analytics.csv",
            )
        if export_format == "pdf":
            return ExportFile(
                content=self._analytics_pdf(summary, equipment, employees, generated_at),
                media_type="application/pdf",
                file_name="reports-analytics.pdf",
            )
        raise ValueError("Unsupported export format")

    def _round_report_csv(self, report: RoundReportDetail) -> bytes:
        buffer = io.StringIO()
        writer = csv.writer(buffer)

        writer.writerow(["Round"])
        round_data = self._to_plain_dict(report.round)
        for key, value in round_data.items():
            writer.writerow([key, self._format_value(value)])

        writer.writerow([])
        writer.writerow(["Checklist results"])
        writer.writerow(
            [
                "item_template_id",
                "question",
                "equipment_id",
                "equipment_name",
                "route_step_id",
                "result_code",
                "result_value",
                "comment",
                "status",
            ]
        )
        for item in report.checklist_results:
            row = self._to_plain_dict(item)
            writer.writerow(
                [
                    row["item_template_id"],
                    row["question"],
                    row["equipment_id"],
                    row["equipment_name"],
                    row["route_step_id"],
                    row["result_code"],
                    self._format_value(row["result_value"]),
                    row["comment"],
                    row["status"],
                ]
            )

        writer.writerow([])
        writer.writerow(["Equipment readings"])
        writer.writerow(
            [
                "id",
                "equipment_id",
                "equipment_name",
                "parameter_name",
                "unit",
                "reading_ts",
                "value_num",
                "value_text",
                "source",
                "within_limits",
            ]
        )
        for reading in report.readings:
            row = self._to_plain_dict(reading)
            writer.writerow(
                [
                    row["id"],
                    row["equipment_id"],
                    row["equipment_name"],
                    row["parameter_name"],
                    row["unit"],
                    self._format_value(row["reading_ts"]),
                    row["value_num"],
                    row["value_text"],
                    row["source"],
                    row["within_limits"],
                ]
            )

        writer.writerow([])
        writer.writerow(["Defects"])
        writer.writerow(
            [
                "id",
                "equipment_id",
                "equipment_name",
                "detected_at",
                "title",
                "description",
                "severity",
                "status",
            ]
        )
        for defect in report.defects:
            row = self._to_plain_dict(defect)
            writer.writerow(
                [
                    row["id"],
                    row["equipment_id"],
                    row["equipment_name"],
                    self._format_value(row["detected_at"]),
                    row["title"],
                    row["description"],
                    row["severity"],
                    row["status"],
                ]
            )

        writer.writerow([])
        writer.writerow(["Attachments"])
        writer.writerow(
            [
                "id",
                "entity_type",
                "entity_id",
                "file_name",
                "mime_type",
                "size_bytes",
                "checksum",
                "download_url",
            ]
        )
        for attachment in report.attachments:
            row = self._to_plain_dict(attachment)
            writer.writerow(
                [
                    row["id"],
                    row["entity_type"],
                    row["entity_id"],
                    row["file_name"],
                    row["mime_type"],
                    row["size_bytes"],
                    row["checksum"],
                    row["download_url"],
                ]
            )

        return self._csv_bytes(buffer)

    def _analytics_csv(
        self,
        summary: ReportsSummary,
        equipment: list[EquipmentAnalyticsItem],
        employees: list[EmployeeAnalyticsItem],
        generated_at: datetime,
    ) -> bytes:
        buffer = io.StringIO()
        writer = csv.writer(buffer)

        writer.writerow(["Generated at", self._format_value(generated_at)])
        writer.writerow([])

        writer.writerow(["Summary"])
        for key, value in self._to_plain_dict(summary).items():
            writer.writerow([key, self._format_value(value)])

        writer.writerow([])
        writer.writerow(["Equipment analytics"])
        writer.writerow(
            [
                "equipment_id",
                "equipment_name",
                "location",
                "defects_count",
                "warning_count",
                "critical_count",
                "last_reading_at",
            ]
        )
        for item in equipment:
            row = self._to_plain_dict(item)
            writer.writerow(
                [
                    row["equipment_id"],
                    row["equipment_name"],
                    row["location"],
                    row["defects_count"],
                    row["warning_count"],
                    row["critical_count"],
                    self._format_value(row["last_reading_at"]),
                ]
            )

        writer.writerow([])
        writer.writerow(["Employee analytics"])
        writer.writerow(
            [
                "employee_id",
                "employee_name",
                "rounds_total",
                "rounds_completed",
                "confirmed_steps_count",
                "avg_duration_min",
                "warning_count",
                "critical_count",
            ]
        )
        for item in employees:
            row = self._to_plain_dict(item)
            writer.writerow(
                [
                    row["employee_id"],
                    row["employee_name"],
                    row["rounds_total"],
                    row["rounds_completed"],
                    row["confirmed_steps_count"],
                    row["avg_duration_min"],
                    row["warning_count"],
                    row["critical_count"],
                ]
            )

        return self._csv_bytes(buffer)

    def _json_bytes(self, value: Any) -> bytes:
        plain_value = self._to_plain_dict(value)
        return json.dumps(plain_value, ensure_ascii=False, default=self._format_value, indent=2).encode("utf-8")

    def _round_report_pdf(self, report: RoundReportDetail) -> bytes:
        lines: list[str] = [
            "Obhod round report",
            f"Round ID: {report.round.id}",
            f"Route: {report.round.route_name}",
            f"Employee: {report.round.employee_name}",
            f"Status: {report.round.status}",
            f"Planned start: {self._format_value(report.round.planned_start)}",
            f"Actual start: {self._format_value(report.round.actual_start)}",
            f"Actual end: {self._format_value(report.round.actual_end)}",
            f"Completion: {report.round.completion_pct}%",
            f"Warnings: {report.round.warning_count}",
            f"Critical deviations: {report.round.critical_count}",
            f"Defects: {report.round.defects_count}",
            "",
            "Checklist results",
        ]
        for item in report.checklist_results:
            lines.extend(
                [
                    f"- {item.question}",
                    f"  Equipment: {item.equipment_name or item.equipment_id or ''}",
                    f"  Status: {item.status}; code: {item.result_code or ''}",
                    f"  Value: {self._format_value(item.result_value)}",
                    f"  Comment: {item.comment or ''}",
                ]
            )

        lines.extend(["", "Equipment readings"])
        for reading in report.readings:
            value = reading.value_text if reading.value_text is not None else reading.value_num
            lines.append(
                f"- {reading.equipment_name}: {reading.parameter_name} = "
                f"{self._format_value(value)} {reading.unit or ''}; source={reading.source}"
            )

        lines.extend(["", "Defects"])
        for defect in report.defects:
            lines.extend(
                [
                    f"- {defect.title}",
                    f"  Equipment: {defect.equipment_name}",
                    f"  Severity: {defect.severity}; status: {defect.status}",
                    f"  Detected at: {self._format_value(defect.detected_at)}",
                    f"  Description: {defect.description or ''}",
                ]
            )

        lines.extend(["", "Attachments"])
        for attachment in report.attachments:
            lines.append(f"- {attachment.file_name}: {attachment.download_url}")

        return self._simple_pdf(lines)

    def _analytics_pdf(
        self,
        summary: ReportsSummary,
        equipment: list[EquipmentAnalyticsItem],
        employees: list[EmployeeAnalyticsItem],
        generated_at: datetime,
    ) -> bytes:
        lines: list[str] = [
            "Obhod analytics report",
            f"Generated at: {self._format_value(generated_at)}",
            "",
            "Summary",
        ]
        for key, value in self._to_plain_dict(summary).items():
            lines.append(f"- {key}: {self._format_value(value)}")

        lines.extend(["", "Equipment analytics"])
        for item in equipment:
            lines.append(
                f"- {item.equipment_name}: defects={item.defects_count}, "
                f"warnings={item.warning_count}, critical={item.critical_count}, "
                f"last_reading={self._format_value(item.last_reading_at)}"
            )

        lines.extend(["", "Employee analytics"])
        for item in employees:
            lines.append(
                f"- {item.employee_name}: rounds={item.rounds_completed}/{item.rounds_total}, "
                f"steps={item.confirmed_steps_count}, warnings={item.warning_count}, "
                f"critical={item.critical_count}"
            )

        return self._simple_pdf(lines)

    def _simple_pdf(self, lines: list[str]) -> bytes:
        page_width = 595
        page_height = 842
        left = 42
        top = 800
        font_size = 10
        line_height = 14
        max_chars = 92
        max_lines_per_page = 52

        wrapped_lines: list[str] = []
        for line in lines:
            ascii_line = self._to_pdf_text(line)
            if not ascii_line:
                wrapped_lines.append("")
                continue
            wrapped_lines.extend(textwrap.wrap(ascii_line, width=max_chars) or [""])

        pages = [
            wrapped_lines[index : index + max_lines_per_page]
            for index in range(0, len(wrapped_lines), max_lines_per_page)
        ] or [[]]

        objects: list[bytes] = []

        def add_object(payload: bytes) -> int:
            objects.append(payload)
            return len(objects)

        catalog_id = add_object(b"<< /Type /Catalog /Pages 2 0 R >>")
        pages_id = add_object(b"")
        font_id = add_object(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
        page_ids: list[int] = []

        for page_lines in pages:
            commands = ["BT", f"/F1 {font_size} Tf", f"{left} {top} Td"]
            first_line = True
            for line in page_lines:
                if first_line:
                    first_line = False
                else:
                    commands.append(f"0 -{line_height} Td")
                commands.append(f"({self._escape_pdf_text(line)}) Tj")
            commands.append("ET")
            content = "\n".join(commands).encode("ascii")
            content_id = add_object(
                b"<< /Length " + str(len(content)).encode("ascii") + b" >>\nstream\n" + content + b"\nendstream"
            )
            page_id = add_object(
                (
                    f"<< /Type /Page /Parent {pages_id} 0 R "
                    f"/MediaBox [0 0 {page_width} {page_height}] "
                    f"/Resources << /Font << /F1 {font_id} 0 R >> >> "
                    f"/Contents {content_id} 0 R >>"
                ).encode("ascii")
            )
            page_ids.append(page_id)

        kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
        objects[pages_id - 1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode("ascii")
        objects[catalog_id - 1] = b"<< /Type /Catalog /Pages 2 0 R >>"

        buffer = io.BytesIO()
        buffer.write(b"%PDF-1.4\n")
        offsets = [0]
        for object_id, payload in enumerate(objects, start=1):
            offsets.append(buffer.tell())
            buffer.write(f"{object_id} 0 obj\n".encode("ascii"))
            buffer.write(payload)
            buffer.write(b"\nendobj\n")

        xref_offset = buffer.tell()
        buffer.write(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
        buffer.write(b"0000000000 65535 f \n")
        for offset in offsets[1:]:
            buffer.write(f"{offset:010d} 00000 n \n".encode("ascii"))
        buffer.write(
            (
                "trailer\n"
                f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
                "startxref\n"
                f"{xref_offset}\n"
                "%%EOF\n"
            ).encode("ascii")
        )
        return buffer.getvalue()

    def _csv_bytes(self, buffer: io.StringIO) -> bytes:
        return ("\ufeff" + buffer.getvalue()).encode("utf-8")

    def _to_plain_dict(self, value: Any) -> Any:
        if isinstance(value, BaseModel):
            if hasattr(value, "model_dump"):
                return value.model_dump(mode="json")
            return value.dict()
        if isinstance(value, list):
            return [self._to_plain_dict(item) for item in value]
        if isinstance(value, dict):
            return {key: self._to_plain_dict(item) for key, item in value.items()}
        return value

    def _format_value(self, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, datetime | date):
            return value.isoformat()
        if isinstance(value, dict | list):
            return json.dumps(value, ensure_ascii=False, default=self._format_value)
        return str(value)

    def _to_pdf_text(self, value: str) -> str:
        translit = {
            "А": "A",
            "Б": "B",
            "В": "V",
            "Г": "G",
            "Д": "D",
            "Е": "E",
            "Ё": "E",
            "Ж": "Zh",
            "З": "Z",
            "И": "I",
            "Й": "Y",
            "К": "K",
            "Л": "L",
            "М": "M",
            "Н": "N",
            "О": "O",
            "П": "P",
            "Р": "R",
            "С": "S",
            "Т": "T",
            "У": "U",
            "Ф": "F",
            "Х": "Kh",
            "Ц": "Ts",
            "Ч": "Ch",
            "Ш": "Sh",
            "Щ": "Sch",
            "Ъ": "",
            "Ы": "Y",
            "Ь": "",
            "Э": "E",
            "Ю": "Yu",
            "Я": "Ya",
            "а": "a",
            "б": "b",
            "в": "v",
            "г": "g",
            "д": "d",
            "е": "e",
            "ё": "e",
            "ж": "zh",
            "з": "z",
            "и": "i",
            "й": "y",
            "к": "k",
            "л": "l",
            "м": "m",
            "н": "n",
            "о": "o",
            "п": "p",
            "р": "r",
            "с": "s",
            "т": "t",
            "у": "u",
            "ф": "f",
            "х": "kh",
            "ц": "ts",
            "ч": "ch",
            "ш": "sh",
            "щ": "sch",
            "ъ": "",
            "ы": "y",
            "ь": "",
            "э": "e",
            "ю": "yu",
            "я": "ya",
            "№": "No",
            "—": "-",
            "–": "-",
            "«": '"',
            "»": '"',
        }
        text = "".join(translit.get(char, char) for char in value)
        return text.encode("latin-1", errors="replace").decode("latin-1")

    def _escape_pdf_text(self, value: str) -> str:
        return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
