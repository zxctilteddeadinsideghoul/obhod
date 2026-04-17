from datetime import datetime

from pydantic import BaseModel


class HealthRead(BaseModel):
    service: str
    status: str


class CurrentUserRead(BaseModel):
    service: str
    user_id: str | None = None
    user_role: str | None = None
    user_name: str | None = None


class RoundReportListItem(BaseModel):
    id: str
    status: str
    route_id: str
    route_name: str
    employee_id: str
    employee_name: str
    planned_start: datetime
    planned_end: datetime | None = None
    actual_start: datetime | None = None
    actual_end: datetime | None = None
    mandatory_steps_total: int
    confirmed_steps_count: int
    required_items_total: int
    completed_items_count: int
    warning_count: int
    critical_count: int
    defects_count: int
    completion_pct: int


class ChecklistResultRead(BaseModel):
    item_template_id: str
    question: str
    equipment_id: str | None = None
    equipment_name: str | None = None
    route_step_id: str | None = None
    result_code: str | None = None
    result_value: dict
    comment: str | None = None
    status: str


class EquipmentReadingRead(BaseModel):
    id: str
    equipment_id: str
    equipment_name: str
    parameter_name: str
    unit: str | None = None
    reading_ts: datetime
    value_num: float | None = None
    value_text: str | None = None
    source: str
    within_limits: bool | None = None


class DefectRead(BaseModel):
    id: str
    equipment_id: str
    equipment_name: str
    detected_at: datetime
    title: str
    description: str | None = None
    severity: str
    status: str


class RoundReportDetail(BaseModel):
    round: RoundReportListItem
    checklist_results: list[ChecklistResultRead]
    readings: list[EquipmentReadingRead]
    defects: list[DefectRead]


class ReportsSummary(BaseModel):
    rounds_total: int
    rounds_planned: int
    rounds_in_progress: int
    rounds_completed: int
    defects_open: int
    warning_count: int
    critical_count: int
    avg_completion_pct: float


class EquipmentAnalyticsItem(BaseModel):
    equipment_id: str
    equipment_name: str
    location: str | None = None
    defects_count: int
    warning_count: int
    critical_count: int
    last_reading_at: datetime | None = None


class EmployeeAnalyticsItem(BaseModel):
    employee_id: str
    employee_name: str
    rounds_total: int
    rounds_completed: int
    confirmed_steps_count: int
    avg_duration_min: float | None = None
    warning_count: int
    critical_count: int
