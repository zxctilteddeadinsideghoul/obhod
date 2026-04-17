from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.reports.utils import to_plain
from app.schemas import (
    EmployeeAnalyticsItem,
    EquipmentAnalyticsItem,
    ReportsSummary,
    RoundReportDetail,
)


@dataclass(frozen=True)
class ReportSection:
    title: str
    rows: list[dict[str, Any]]


class ReportDocument(ABC):
    @property
    @abstractmethod
    def report_id(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def title(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def file_prefix(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def to_sections(self) -> list[ReportSection]:
        raise NotImplementedError


class RoundReportDocument(ReportDocument):
    def __init__(self, report: RoundReportDetail) -> None:
        self.report = report

    @property
    def report_id(self) -> str:
        return self.report.round.id

    @property
    def title(self) -> str:
        return "Obhod round report"

    @property
    def file_prefix(self) -> str:
        return f"round-report-{self.report_id}"

    def to_dict(self) -> dict[str, Any]:
        return to_plain(self.report)

    def to_sections(self) -> list[ReportSection]:
        return [
            ReportSection("Round", [to_plain(self.report.round)]),
            ReportSection("Checklist results", to_plain(self.report.checklist_results)),
            ReportSection("Equipment readings", to_plain(self.report.readings)),
            ReportSection("Defects", to_plain(self.report.defects)),
            ReportSection("Attachments", to_plain(self.report.attachments)),
        ]


class AnalyticsReportDocument(ReportDocument):
    def __init__(
        self,
        summary: ReportsSummary,
        equipment: list[EquipmentAnalyticsItem],
        employees: list[EmployeeAnalyticsItem],
        generated_at: datetime,
    ) -> None:
        self.summary = summary
        self.equipment = equipment
        self.employees = employees
        self.generated_at = generated_at

    @property
    def report_id(self) -> str:
        return "analytics"

    @property
    def title(self) -> str:
        return "Obhod analytics report"

    @property
    def file_prefix(self) -> str:
        return "reports-analytics"

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "summary": self.summary,
            "equipment": self.equipment,
            "employees": self.employees,
        }

    def to_sections(self) -> list[ReportSection]:
        return [
            ReportSection("Generated at", [{"generated_at": self.generated_at}]),
            ReportSection("Summary", [to_plain(self.summary)]),
            ReportSection("Equipment analytics", to_plain(self.equipment)),
            ReportSection("Employee analytics", to_plain(self.employees)),
        ]
