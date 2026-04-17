"""initial field schema

Revision ID: 20260417_0001
Revises:
Create Date: 2026-04-17
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260417_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "field_equipment",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("org_id", sa.String(length=64), nullable=False),
        sa.Column("code", sa.String(length=64)),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("tech_no", sa.String(length=128)),
        sa.Column("passport_no", sa.String(length=128)),
        sa.Column("serial_no", sa.String(length=128)),
        sa.Column("type_id", sa.String(length=64), nullable=False),
        sa.Column("location_id", sa.String(length=128)),
        sa.Column("location", sa.String(length=512)),
        sa.Column("state_id", sa.String(length=64), nullable=False),
        sa.Column("qr_tag", sa.String(length=255)),
        sa.Column("nfc_tag", sa.String(length=255)),
        sa.Column("passport_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("snapshot_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_field_equipment_org_id", "field_equipment", ["org_id"])
    op.create_index("ix_field_equipment_qr_tag", "field_equipment", ["qr_tag"])
    op.create_index("ix_field_equipment_nfc_tag", "field_equipment", ["nfc_tag"])
    op.create_index("ix_field_equipment_tech_no", "field_equipment", ["tech_no"])
    op.create_index("ix_field_equipment_type_id", "field_equipment", ["type_id"])

    op.create_table(
        "field_equipment_parameter_def",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("equipment_type_id", sa.String(length=64), nullable=False),
        sa.Column("code", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("unit", sa.String(length=32)),
        sa.Column("data_type", sa.String(length=32), nullable=False),
        sa.Column("min_value", sa.Float()),
        sa.Column("max_value", sa.Float()),
        sa.Column("critical_min", sa.Float()),
        sa.Column("critical_max", sa.Float()),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_field_equipment_parameter_def_equipment_type_id", "field_equipment_parameter_def", ["equipment_type_id"])
    op.create_index("ix_field_equipment_parameter_def_code", "field_equipment_parameter_def", ["code"])

    op.create_table(
        "field_route_template",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("org_id", sa.String(length=64), nullable=False),
        sa.Column("department_id", sa.String(length=64)),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("route_type", sa.String(length=64), nullable=False),
        sa.Column("location", sa.String(length=512)),
        sa.Column("duration_min", sa.Integer(), nullable=False),
        sa.Column("planning_rule", sa.String(length=128), nullable=False),
        sa.Column("qualification_id", sa.String(length=64)),
        sa.Column("version", sa.String(length=32), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("snapshot_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_field_route_template_org_id", "field_route_template", ["org_id"])

    op.create_table(
        "field_employee",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("person_id", sa.String(length=64)),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("qualification_id", sa.String(length=64)),
        sa.Column("department_id", sa.String(length=64)),
        sa.Column("active_flag", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "field_shift",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("org_id", sa.String(length=64), nullable=False),
        sa.Column("shift_code", sa.String(length=64), nullable=False),
        sa.Column("start_ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("calendar_id", sa.String(length=64)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_field_shift_org_id", "field_shift", ["org_id"])

    op.create_table(
        "field_checklist_template",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("org_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("scope", sa.String(length=64), nullable=False),
        sa.Column("equipment_type_id", sa.String(length=64)),
        sa.Column("version", sa.String(length=32), nullable=False),
        sa.Column("active_from", sa.Date()),
        sa.Column("active_to", sa.Date()),
        sa.Column("snapshot_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_field_checklist_template_org_id", "field_checklist_template", ["org_id"])

    op.create_table(
        "field_route_step",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("route_template_id", sa.String(length=64), sa.ForeignKey("field_route_template.id"), nullable=False),
        sa.Column("seq_no", sa.Integer(), nullable=False),
        sa.Column("equipment_id", sa.String(length=64), sa.ForeignKey("field_equipment.id"), nullable=False),
        sa.Column("checkpoint_id", sa.String(length=64)),
        sa.Column("mandatory_flag", sa.Boolean(), nullable=False),
        sa.Column("confirm_by", sa.String(length=32), nullable=False),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_field_route_step_route_template_id", "field_route_step", ["route_template_id"])
    op.create_index("ix_field_route_step_equipment_id", "field_route_step", ["equipment_id"])

    op.create_table(
        "field_round_instance",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("org_id", sa.String(length=64), nullable=False),
        sa.Column("route_template_id", sa.String(length=64), sa.ForeignKey("field_route_template.id"), nullable=False),
        sa.Column("planned_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("planned_end", sa.DateTime(timezone=True)),
        sa.Column("actual_start", sa.DateTime(timezone=True)),
        sa.Column("actual_end", sa.DateTime(timezone=True)),
        sa.Column("shift_id", sa.String(length=64), sa.ForeignKey("field_shift.id")),
        sa.Column("employee_id", sa.String(length=64), sa.ForeignKey("field_employee.id"), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("source_doc_id", sa.String(length=128)),
        sa.Column("qualification_id", sa.String(length=64)),
        sa.Column("snapshot_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_field_round_instance_org_id", "field_round_instance", ["org_id"])
    op.create_index("ix_field_round_instance_route_template_id", "field_round_instance", ["route_template_id"])
    op.create_index("ix_field_round_instance_planned_start", "field_round_instance", ["planned_start"])
    op.create_index("ix_field_round_instance_employee_id", "field_round_instance", ["employee_id"])
    op.create_index("ix_field_round_instance_status", "field_round_instance", ["status"])

    op.create_table(
        "field_checklist_item_template",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("checklist_template_id", sa.String(length=64), sa.ForeignKey("field_checklist_template.id"), nullable=False),
        sa.Column("seq_no", sa.Integer(), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer_type", sa.String(length=32), nullable=False),
        sa.Column("required_flag", sa.Boolean(), nullable=False),
        sa.Column("norm_ref", sa.String(length=128)),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_field_checklist_item_template_checklist_template_id", "field_checklist_item_template", ["checklist_template_id"])

    op.create_table(
        "field_checklist_instance",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("round_instance_id", sa.String(length=64), sa.ForeignKey("field_round_instance.id"), nullable=False),
        sa.Column("checklist_template_id", sa.String(length=64), sa.ForeignKey("field_checklist_template.id"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("completion_pct", sa.Integer(), nullable=False),
        sa.Column("snapshot_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_field_checklist_instance_round_instance_id", "field_checklist_instance", ["round_instance_id"])
    op.create_index("ix_field_checklist_instance_checklist_template_id", "field_checklist_instance", ["checklist_template_id"])
    op.create_index("ix_field_checklist_instance_status", "field_checklist_instance", ["status"])

    op.create_table(
        "field_route_step_visit",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("round_instance_id", sa.String(length=64), sa.ForeignKey("field_round_instance.id"), nullable=False),
        sa.Column("route_step_id", sa.String(length=64), sa.ForeignKey("field_route_step.id"), nullable=False),
        sa.Column("equipment_id", sa.String(length=64), sa.ForeignKey("field_equipment.id"), nullable=False),
        sa.Column("employee_id", sa.String(length=64), sa.ForeignKey("field_employee.id"), nullable=False),
        sa.Column("confirmed_by", sa.String(length=32), nullable=False),
        sa.Column("scanned_value", sa.String(length=255), nullable=False),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_field_route_step_visit_round_instance_id", "field_route_step_visit", ["round_instance_id"])
    op.create_index("ix_field_route_step_visit_route_step_id", "field_route_step_visit", ["route_step_id"])
    op.create_index("ix_field_route_step_visit_equipment_id", "field_route_step_visit", ["equipment_id"])
    op.create_index("ix_field_route_step_visit_employee_id", "field_route_step_visit", ["employee_id"])
    op.create_index("ix_field_route_step_visit_confirmed_at", "field_route_step_visit", ["confirmed_at"])
    op.create_index("ix_field_route_step_visit_status", "field_route_step_visit", ["status"])

    op.create_table(
        "field_checklist_item_result",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("checklist_instance_id", sa.String(length=64), sa.ForeignKey("field_checklist_instance.id"), nullable=False),
        sa.Column("item_template_id", sa.String(length=64), sa.ForeignKey("field_checklist_item_template.id"), nullable=False),
        sa.Column("equipment_id", sa.String(length=64), sa.ForeignKey("field_equipment.id")),
        sa.Column("route_step_id", sa.String(length=64), sa.ForeignKey("field_route_step.id")),
        sa.Column("result_code", sa.String(length=64)),
        sa.Column("result_value", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("comment", sa.Text()),
        sa.Column("due_date", sa.Date()),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_field_checklist_item_result_checklist_instance_id", "field_checklist_item_result", ["checklist_instance_id"])
    op.create_index("ix_field_checklist_item_result_item_template_id", "field_checklist_item_result", ["item_template_id"])

    op.create_table(
        "field_equipment_parameter_reading",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("equipment_id", sa.String(length=64), sa.ForeignKey("field_equipment.id"), nullable=False),
        sa.Column("parameter_def_id", sa.String(length=64), sa.ForeignKey("field_equipment_parameter_def.id"), nullable=False),
        sa.Column("reading_ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("value_num", sa.Float()),
        sa.Column("value_text", sa.Text()),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("route_step_id", sa.String(length=64), sa.ForeignKey("field_route_step.id")),
        sa.Column("checklist_item_result_id", sa.String(length=64), sa.ForeignKey("field_checklist_item_result.id")),
        sa.Column("within_limits", sa.Boolean()),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_field_equipment_parameter_reading_equipment_id", "field_equipment_parameter_reading", ["equipment_id"])
    op.create_index("ix_field_equipment_parameter_reading_parameter_def_id", "field_equipment_parameter_reading", ["parameter_def_id"])
    op.create_index("ix_field_equipment_parameter_reading_reading_ts", "field_equipment_parameter_reading", ["reading_ts"])

    op.create_table(
        "field_defect",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("org_id", sa.String(length=64), nullable=False),
        sa.Column("equipment_id", sa.String(length=64), sa.ForeignKey("field_equipment.id"), nullable=False),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source_checklist_id", sa.String(length=64), sa.ForeignKey("field_checklist_instance.id")),
        sa.Column("checkpoint_id", sa.String(length=64)),
        sa.Column("created_by", sa.String(length=64)),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("severity", sa.String(length=32), nullable=False),
        sa.Column("attention_marker", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_field_defect_org_id", "field_defect", ["org_id"])
    op.create_index("ix_field_defect_equipment_id", "field_defect", ["equipment_id"])
    op.create_index("ix_field_defect_detected_at", "field_defect", ["detected_at"])
    op.create_index("ix_field_defect_status", "field_defect", ["status"])

    op.create_table(
        "field_journal_entry",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("event_ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("event_type", sa.String(length=128), nullable=False),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("entity_id", sa.String(length=64), nullable=False),
        sa.Column("org_id", sa.String(length=64)),
        sa.Column("equipment_id", sa.String(length=64), sa.ForeignKey("field_equipment.id")),
        sa.Column("employee_id", sa.String(length=64), sa.ForeignKey("field_employee.id")),
        sa.Column("shift_id", sa.String(length=64), sa.ForeignKey("field_shift.id")),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_field_journal_entry_event_ts", "field_journal_entry", ["event_ts"])
    op.create_index("ix_field_journal_entry_event_type", "field_journal_entry", ["event_type"])
    op.create_index("ix_field_journal_entry_entity_type", "field_journal_entry", ["entity_type"])
    op.create_index("ix_field_journal_entry_entity_id", "field_journal_entry", ["entity_id"])
    op.create_index("ix_field_journal_entry_org_id", "field_journal_entry", ["org_id"])

    op.create_table(
        "field_attachment",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("entity_id", sa.String(length=64), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=128), nullable=False),
        sa.Column("size_bytes", sa.Integer()),
        sa.Column("checksum", sa.String(length=255)),
        sa.Column("storage_uri", sa.String(length=1024), nullable=False),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_field_attachment_entity_type", "field_attachment", ["entity_type"])
    op.create_index("ix_field_attachment_entity_id", "field_attachment", ["entity_id"])

    op.create_table(
        "field_audit_log",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("entity_id", sa.String(length=64), nullable=False),
        sa.Column("op", sa.String(length=64), nullable=False),
        sa.Column("author_id", sa.String(length=64)),
        sa.Column("op_ts_utc", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("before_json", postgresql.JSONB(astext_type=sa.Text())),
        sa.Column("after_json", postgresql.JSONB(astext_type=sa.Text())),
        sa.Column("source_device_id", sa.String(length=128)),
    )
    op.create_index("ix_field_audit_log_entity_type", "field_audit_log", ["entity_type"])
    op.create_index("ix_field_audit_log_entity_id", "field_audit_log", ["entity_id"])
    op.create_index("ix_field_audit_log_op_ts_utc", "field_audit_log", ["op_ts_utc"])


def downgrade() -> None:
    for table_name in (
        "field_audit_log",
        "field_attachment",
        "field_journal_entry",
        "field_defect",
        "field_equipment_parameter_reading",
        "field_checklist_item_result",
        "field_route_step_visit",
        "field_checklist_instance",
        "field_checklist_item_template",
        "field_round_instance",
        "field_route_step",
        "field_checklist_template",
        "field_shift",
        "field_employee",
        "field_route_template",
        "field_equipment_parameter_def",
        "field_equipment",
    ):
        op.drop_table(table_name)
