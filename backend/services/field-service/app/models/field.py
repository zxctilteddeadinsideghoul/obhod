from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class Equipment(Base, TimestampMixin):
    __tablename__ = "field_equipment"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    org_id: Mapped[str] = mapped_column(String(64), index=True)
    code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    name: Mapped[str] = mapped_column(String(255))
    tech_no: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    passport_no: Mapped[str | None] = mapped_column(String(128), nullable=True)
    serial_no: Mapped[str | None] = mapped_column(String(128), nullable=True)
    type_id: Mapped[str] = mapped_column(String(64), index=True)
    location_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    location: Mapped[str | None] = mapped_column(String(512), nullable=True)
    state_id: Mapped[str] = mapped_column(String(64), default="in_operation")
    qr_tag: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    nfc_tag: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    passport_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    snapshot_json: Mapped[dict] = mapped_column(JSONB, default=dict)

    parameters: Mapped[list["EquipmentParameterReading"]] = relationship(back_populates="equipment")
    defects: Mapped[list["Defect"]] = relationship(back_populates="equipment")


class EquipmentParameterDef(Base, TimestampMixin):
    __tablename__ = "field_equipment_parameter_def"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    equipment_type_id: Mapped[str] = mapped_column(String(64), index=True)
    code: Mapped[str] = mapped_column(String(128), index=True)
    name: Mapped[str] = mapped_column(String(255))
    unit: Mapped[str | None] = mapped_column(String(32), nullable=True)
    data_type: Mapped[str] = mapped_column(String(32), default="number")
    min_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    critical_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    critical_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    payload_json: Mapped[dict] = mapped_column(JSONB, default=dict)


class RouteTemplate(Base, TimestampMixin):
    __tablename__ = "field_route_template"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    org_id: Mapped[str] = mapped_column(String(64), index=True)
    department_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    name: Mapped[str] = mapped_column(String(255))
    route_type: Mapped[str] = mapped_column(String(64), default="inspection")
    location: Mapped[str | None] = mapped_column(String(512), nullable=True)
    duration_min: Mapped[int] = mapped_column(Integer)
    planning_rule: Mapped[str] = mapped_column(String(128))
    qualification_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    version: Mapped[str] = mapped_column(String(32), default="1")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    snapshot_json: Mapped[dict] = mapped_column(JSONB, default=dict)

    steps: Mapped[list["RouteStep"]] = relationship(
        back_populates="route_template",
        cascade="all, delete-orphan",
        order_by="RouteStep.seq_no",
    )


class RouteStep(Base, TimestampMixin):
    __tablename__ = "field_route_step"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    route_template_id: Mapped[str] = mapped_column(ForeignKey("field_route_template.id"), index=True)
    seq_no: Mapped[int] = mapped_column(Integer)
    equipment_id: Mapped[str] = mapped_column(ForeignKey("field_equipment.id"), index=True)
    checkpoint_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    mandatory_flag: Mapped[bool] = mapped_column(Boolean, default=True)
    confirm_by: Mapped[str] = mapped_column(String(32), default="manual")
    payload_json: Mapped[dict] = mapped_column(JSONB, default=dict)

    route_template: Mapped[RouteTemplate] = relationship(back_populates="steps")
    equipment: Mapped[Equipment] = relationship()


class Employee(Base, TimestampMixin):
    __tablename__ = "field_employee"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    person_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255))
    qualification_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    department_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    active_flag: Mapped[bool] = mapped_column(Boolean, default=True)


class Shift(Base, TimestampMixin):
    __tablename__ = "field_shift"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    org_id: Mapped[str] = mapped_column(String(64), index=True)
    shift_code: Mapped[str] = mapped_column(String(64))
    start_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    calendar_id: Mapped[str | None] = mapped_column(String(64), nullable=True)


class RoundInstance(Base, TimestampMixin):
    __tablename__ = "field_round_instance"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    org_id: Mapped[str] = mapped_column(String(64), index=True)
    route_template_id: Mapped[str] = mapped_column(ForeignKey("field_route_template.id"), index=True)
    planned_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    planned_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    shift_id: Mapped[str | None] = mapped_column(ForeignKey("field_shift.id"), nullable=True)
    employee_id: Mapped[str] = mapped_column(ForeignKey("field_employee.id"), index=True)
    status: Mapped[str] = mapped_column(String(32), index=True, default="planned")
    source_doc_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    qualification_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    snapshot_json: Mapped[dict] = mapped_column(JSONB, default=dict)

    route_template: Mapped[RouteTemplate] = relationship()
    employee: Mapped[Employee] = relationship()


class ChecklistTemplate(Base, TimestampMixin):
    __tablename__ = "field_checklist_template"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    org_id: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str] = mapped_column(String(255))
    scope: Mapped[str] = mapped_column(String(64), default="round")
    equipment_type_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    version: Mapped[str] = mapped_column(String(32), default="1")
    active_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    active_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    snapshot_json: Mapped[dict] = mapped_column(JSONB, default=dict)

    items: Mapped[list["ChecklistItemTemplate"]] = relationship(
        back_populates="checklist_template",
        cascade="all, delete-orphan",
        order_by="ChecklistItemTemplate.seq_no",
    )


class ChecklistItemTemplate(Base, TimestampMixin):
    __tablename__ = "field_checklist_item_template"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    checklist_template_id: Mapped[str] = mapped_column(ForeignKey("field_checklist_template.id"), index=True)
    seq_no: Mapped[int] = mapped_column(Integer)
    question: Mapped[str] = mapped_column(Text)
    answer_type: Mapped[str] = mapped_column(String(32))
    required_flag: Mapped[bool] = mapped_column(Boolean, default=True)
    norm_ref: Mapped[str | None] = mapped_column(String(128), nullable=True)
    payload_json: Mapped[dict] = mapped_column(JSONB, default=dict)

    checklist_template: Mapped[ChecklistTemplate] = relationship(back_populates="items")


class ChecklistInstance(Base, TimestampMixin):
    __tablename__ = "field_checklist_instance"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    round_instance_id: Mapped[str] = mapped_column(ForeignKey("field_round_instance.id"), index=True)
    checklist_template_id: Mapped[str] = mapped_column(ForeignKey("field_checklist_template.id"), index=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), index=True, default="draft")
    completion_pct: Mapped[int] = mapped_column(Integer, default=0)
    snapshot_json: Mapped[dict] = mapped_column(JSONB, default=dict)

    round_instance: Mapped[RoundInstance] = relationship()
    checklist_template: Mapped[ChecklistTemplate] = relationship()
    results: Mapped[list["ChecklistItemResult"]] = relationship(
        back_populates="checklist_instance",
        cascade="all, delete-orphan",
    )


class ChecklistItemResult(Base, TimestampMixin):
    __tablename__ = "field_checklist_item_result"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    checklist_instance_id: Mapped[str] = mapped_column(ForeignKey("field_checklist_instance.id"), index=True)
    item_template_id: Mapped[str] = mapped_column(ForeignKey("field_checklist_item_template.id"), index=True)
    equipment_id: Mapped[str | None] = mapped_column(ForeignKey("field_equipment.id"), nullable=True)
    result_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    result_value: Mapped[dict] = mapped_column(JSONB, default=dict)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="normal")

    checklist_instance: Mapped[ChecklistInstance] = relationship(back_populates="results")
    item_template: Mapped[ChecklistItemTemplate] = relationship()


class EquipmentParameterReading(Base, TimestampMixin):
    __tablename__ = "field_equipment_parameter_reading"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    equipment_id: Mapped[str] = mapped_column(ForeignKey("field_equipment.id"), index=True)
    parameter_def_id: Mapped[str] = mapped_column(ForeignKey("field_equipment_parameter_def.id"), index=True)
    reading_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    value_num: Mapped[float | None] = mapped_column(Float, nullable=True)
    value_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(64), default="mobile")
    route_step_id: Mapped[str | None] = mapped_column(ForeignKey("field_route_step.id"), nullable=True)
    checklist_item_result_id: Mapped[str | None] = mapped_column(
        ForeignKey("field_checklist_item_result.id"),
        nullable=True,
    )
    within_limits: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    payload_json: Mapped[dict] = mapped_column(JSONB, default=dict)

    equipment: Mapped[Equipment] = relationship(back_populates="parameters")
    parameter_def: Mapped[EquipmentParameterDef] = relationship()


class Defect(Base, TimestampMixin):
    __tablename__ = "field_defect"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    org_id: Mapped[str] = mapped_column(String(64), index=True)
    equipment_id: Mapped[str] = mapped_column(ForeignKey("field_equipment.id"), index=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    source_checklist_id: Mapped[str | None] = mapped_column(ForeignKey("field_checklist_instance.id"), nullable=True)
    checkpoint_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(String(32), default="medium")
    attention_marker: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(32), index=True, default="detected")
    payload_json: Mapped[dict] = mapped_column(JSONB, default=dict)

    equipment: Mapped[Equipment] = relationship(back_populates="defects")


class JournalEntry(Base, TimestampMixin):
    __tablename__ = "field_journal_entry"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    event_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    event_type: Mapped[str] = mapped_column(String(128), index=True)
    entity_type: Mapped[str] = mapped_column(String(64), index=True)
    entity_id: Mapped[str] = mapped_column(String(64), index=True)
    org_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    equipment_id: Mapped[str | None] = mapped_column(ForeignKey("field_equipment.id"), nullable=True)
    employee_id: Mapped[str | None] = mapped_column(ForeignKey("field_employee.id"), nullable=True)
    shift_id: Mapped[str | None] = mapped_column(ForeignKey("field_shift.id"), nullable=True)
    payload_json: Mapped[dict] = mapped_column(JSONB, default=dict)


class Attachment(Base, TimestampMixin):
    __tablename__ = "field_attachment"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(64), index=True)
    entity_id: Mapped[str] = mapped_column(String(64), index=True)
    file_name: Mapped[str] = mapped_column(String(255))
    mime_type: Mapped[str] = mapped_column(String(128))
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    checksum: Mapped[str | None] = mapped_column(String(255), nullable=True)
    storage_uri: Mapped[str] = mapped_column(String(1024))
    payload_json: Mapped[dict] = mapped_column(JSONB, default=dict)


class AuditLog(Base):
    __tablename__ = "field_audit_log"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(64), index=True)
    entity_id: Mapped[str] = mapped_column(String(64), index=True)
    op: Mapped[str] = mapped_column(String(64))
    author_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    op_ts_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    before_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    after_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    source_device_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
