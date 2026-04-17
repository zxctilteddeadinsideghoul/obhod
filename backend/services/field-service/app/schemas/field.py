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


class EquipmentCreate(BaseModel):
    id: str
    org_id: str = "ORG-01"
    code: str | None = None
    name: str
    tech_no: str | None = None
    passport_no: str | None = None
    serial_no: str | None = None
    type_id: str
    location_id: str | None = None
    location: str | None = None
    state_id: str = "in_operation"
    qr_tag: str | None = None
    nfc_tag: str | None = None
    passport_json: dict = Field(default_factory=dict)
    snapshot_json: dict = Field(default_factory=dict)


class EquipmentParameterReadingCreate(BaseModel):
    parameter_def_id: str
    reading_ts: datetime | None = None
    value_num: float | None = None
    value_text: str | None = None
    source: str = "mobile"
    route_step_id: str | None = None
    checklist_item_result_id: str | None = None
    payload_json: dict = Field(default_factory=dict)


class EquipmentParameterReadingRead(BaseModel):
    id: str
    equipment_id: str
    parameter_def_id: str
    reading_ts: datetime
    value_num: float | None = None
    value_text: str | None = None
    source: str
    route_step_id: str | None = None
    checklist_item_result_id: str | None = None
    within_limits: bool | None = None
    payload_json: dict = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class EquipmentParameterReadingSubmitRead(BaseModel):
    reading: EquipmentParameterReadingRead
    status: str
    message: str


class EquipmentParameterDefRead(BaseModel):
    id: str
    equipment_type_id: str
    code: str
    name: str
    unit: str | None = None
    data_type: str
    min_value: float | None = None
    max_value: float | None = None
    critical_min: float | None = None
    critical_max: float | None = None
    payload_json: dict = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class TaskEquipmentParameterRead(BaseModel):
    equipment_id: str
    parameter_def: EquipmentParameterDefRead


class RouteStepRead(BaseModel):
    id: str
    seq_no: int
    equipment_id: str
    checkpoint_id: str | None = None
    mandatory_flag: bool
    confirm_by: str

    model_config = ConfigDict(from_attributes=True)


class RouteStepConfirmCreate(BaseModel):
    confirm_by: str = "qr"
    scanned_value: str
    payload_json: dict = Field(default_factory=dict)


class RouteStepVisitRead(BaseModel):
    id: str
    round_instance_id: str
    route_step_id: str
    equipment_id: str
    employee_id: str
    confirmed_by: str
    scanned_value: str
    confirmed_at: datetime
    status: str
    payload_json: dict = Field(default_factory=dict)

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


class RouteStepCreate(BaseModel):
    id: str | None = None
    seq_no: int
    equipment_id: str
    checkpoint_id: str | None = None
    mandatory_flag: bool = True
    confirm_by: str = "qr"
    payload_json: dict = Field(default_factory=dict)


class RouteCreate(BaseModel):
    id: str
    org_id: str = "ORG-01"
    department_id: str | None = None
    name: str
    route_type: str = "inspection"
    location: str | None = None
    duration_min: int = 60
    planning_rule: str = "manual"
    qualification_id: str | None = None
    version: str = "1"
    is_active: bool = True
    steps: list[RouteStepCreate] = Field(default_factory=list)
    snapshot_json: dict = Field(default_factory=dict)


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


class RoundCreate(BaseModel):
    id: str | None = None
    org_id: str = "ORG-01"
    route_template_id: str
    checklist_template_id: str
    employee_id: str
    planned_start: datetime
    planned_end: datetime | None = None
    shift_id: str | None = None
    source_doc_id: str | None = None
    qualification_id: str | None = None
    snapshot_json: dict = Field(default_factory=dict)


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


class ChecklistItemTemplateCreate(BaseModel):
    id: str | None = None
    seq_no: int
    question: str
    answer_type: str
    required_flag: bool = True
    norm_ref: str | None = None
    payload_json: dict = Field(default_factory=dict)


class ChecklistTemplateCreate(BaseModel):
    id: str
    org_id: str = "ORG-01"
    name: str
    scope: str = "round"
    equipment_type_id: str | None = None
    version: str = "1"
    active_from: date | None = None
    active_to: date | None = None
    items: list[ChecklistItemTemplateCreate] = Field(default_factory=list)
    snapshot_json: dict = Field(default_factory=dict)


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
    route_step_id: str | None = None
    result_code: str | None = None
    result_value: dict = Field(default_factory=dict)
    comment: str | None = None
    due_date: date | None = None
    status: str

    model_config = ConfigDict(from_attributes=True)


class ChecklistItemResultCreate(BaseModel):
    equipment_id: str | None = None
    route_step_id: str | None = None
    result_code: str | None = None
    result_value: dict = Field(default_factory=dict)
    comment: str | None = None
    due_date: date | None = None


class ChecklistItemResultSubmitRead(BaseModel):
    result: ChecklistItemResultRead
    checklist_instance: ChecklistInstanceRead


class AttachmentRead(BaseModel):
    id: str
    entity_type: str
    entity_id: str
    file_name: str
    mime_type: str
    size_bytes: int | None = None
    checksum: str | None = None
    storage_uri: str
    download_url: str
    payload_json: dict = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class DefectRead(BaseModel):
    id: str
    org_id: str
    equipment_id: str
    detected_at: datetime
    source_checklist_id: str | None = None
    checkpoint_id: str | None = None
    created_by: str | None = None
    title: str
    description: str | None = None
    severity: str
    attention_marker: bool
    status: str
    payload_json: dict = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class DefectStatusUpdate(BaseModel):
    status: str
    comment: str | None = None


class DefectSeverityUpdate(BaseModel):
    severity: str
    comment: str | None = None


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
    checklist_results: list[ChecklistItemResultRead] = Field(default_factory=list)
    equipment_parameters: list[TaskEquipmentParameterRead] = Field(default_factory=list)


class RouteStepConfirmRead(BaseModel):
    status: str
    visit: RouteStepVisitRead
    equipment: EquipmentRead
    checklist_instance: ChecklistInstanceRead | None = None
    checklist_template: ChecklistTemplateRead | None = None
