from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class EquipmentRead(BaseModel):
    id: str
    org_id: str
    code: str | None = None
    name: str
    tech_no: str | None = None
    passport_no: str | None = None
    serial_no: str | None = None
    type_id: str
    location: str | None = None
    state_id: str
    qr_tag: str | None = None
    nfc_tag: str | None = None
    passport_json: dict = Field(default_factory=dict)
    snapshot_json: dict = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class RouteStepRead(BaseModel):
    id: str
    seq_no: int
    equipment_id: str
    checkpoint_id: str | None = None
    mandatory_flag: bool
    confirm_by: str

    model_config = ConfigDict(from_attributes=True)


class RouteRead(BaseModel):
    id: str
    org_id: str
    department_id: str | None = None
    name: str
    route_type: str
    location: str | None = None
    duration_min: int
    planning_rule: str
    qualification_id: str | None = None
    version: str
    is_active: bool
    steps: list[RouteStepRead] = Field(default_factory=list)
    snapshot_json: dict = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class RoundRead(BaseModel):
    id: str
    org_id: str
    route_template_id: str
    planned_start: datetime
    planned_end: datetime | None = None
    actual_start: datetime | None = None
    actual_end: datetime | None = None
    shift_id: str | None = None
    employee_id: str
    status: str
    qualification_id: str | None = None
    snapshot_json: dict = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class ChecklistItemTemplateRead(BaseModel):
    id: str
    seq_no: int
    question: str
    answer_type: str
    required_flag: bool
    norm_ref: str | None = None
    payload_json: dict = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class ChecklistTemplateRead(BaseModel):
    id: str
    org_id: str
    name: str
    scope: str
    equipment_type_id: str | None = None
    version: str
    items: list[ChecklistItemTemplateRead] = Field(default_factory=list)
    snapshot_json: dict = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class ChecklistInstanceRead(BaseModel):
    id: str
    round_instance_id: str
    checklist_template_id: str
    started_at: datetime | None = None
    finished_at: datetime | None = None
    status: str
    completion_pct: int
    snapshot_json: dict = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class ChecklistItemResultRead(BaseModel):
    id: str
    checklist_instance_id: str
    item_template_id: str
    equipment_id: str | None = None
    result_code: str | None = None
    result_value: dict = Field(default_factory=dict)
    comment: str | None = None
    due_date: date | None = None
    status: str

    model_config = ConfigDict(from_attributes=True)


class ChecklistItemResultCreate(BaseModel):
    equipment_id: str | None = None
    result_code: str | None = None
    result_value: dict = Field(default_factory=dict)
    comment: str | None = None
    due_date: date | None = None


class ChecklistItemResultSubmitRead(BaseModel):
    result: ChecklistItemResultRead
    checklist_instance: ChecklistInstanceRead


class TaskSummaryRead(BaseModel):
    id: str
    status: str
    route_id: str
    route_name: str
    planned_start: datetime
    planned_end: datetime | None = None
    completion_pct: int = 0


class TaskDetailRead(BaseModel):
    round: RoundRead
    route: RouteRead
    equipment: list[EquipmentRead]
    checklist_instance: ChecklistInstanceRead | None = None
    checklist_template: ChecklistTemplateRead | None = None
