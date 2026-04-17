import csv
import io
import json
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
