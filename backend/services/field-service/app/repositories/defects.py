from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import (
    DefectSeverityCalculator,
    DefectSeverityInput,
    EquipmentStabilityCalculator,
    EquipmentStabilityInput,
)
from app.models import (
    AuditLog,
    ChecklistInstance,
    ChecklistItemResult,
    ChecklistItemTemplate,
    Defect,
    Equipment,
    EquipmentParameterDef,
    EquipmentParameterReading,
    JournalEntry,
)


class DefectsRepository:
    def __init__(
        self,
        session: AsyncSession,
        stability_calculator: EquipmentStabilityCalculator,
        severity_calculator: DefectSeverityCalculator,
    ) -> None:
        self.session = session
        self.stability_calculator = stability_calculator
        self.severity_calculator = severity_calculator

    async def list(
        self,
        status: str | None = None,
        severity: str | None = None,
        equipment_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Defect]:
        query = select(Defect)
        if status is not None:
            query = query.where(Defect.status == status)
        if severity is not None:
            query = query.where(Defect.severity == severity)
        if equipment_id is not None:
            query = query.where(Defect.equipment_id == equipment_id)

        result = await self.session.execute(
            query.order_by(Defect.detected_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def get(self, defect_id: str) -> Defect:
        defect = await self.session.get(Defect, defect_id)
        if defect is None:
            raise KeyError(f"Defect {defect_id} not found")
        return defect

    async def update_status(self, defect: Defect, new_status: str, comment: str | None, author_id: str) -> Defect:
        before = self._defect_snapshot(defect)
        defect.status = new_status
        history = list(defect.payload_json.get("statusHistory", []))
        history.append(
            {
                "status": new_status,
                "comment": comment,
                "authorId": author_id,
                "changedAt": datetime.now(timezone.utc).isoformat(),
            }
        )
        defect.payload_json = {**defect.payload_json, "statusHistory": history}
        await self._write_update_audit(defect, "status_update", author_id, before)
        return defect

    async def update_severity(self, defect: Defect, new_severity: str, comment: str | None, author_id: str) -> Defect:
        before = self._defect_snapshot(defect)
        defect.severity = new_severity
        defect.attention_marker = new_severity in {"high", "critical"}
        overrides = list(defect.payload_json.get("severityOverrides", []))
        overrides.append(
            {
                "severity": new_severity,
                "comment": comment,
                "authorId": author_id,
                "changedAt": datetime.now(timezone.utc).isoformat(),
            }
        )
        defect.payload_json = {**defect.payload_json, "severityOverrides": overrides}
        await self._write_update_audit(defect, "severity_update", author_id, before)
        return defect

    async def create_from_checklist_result(
        self,
        checklist_instance: ChecklistInstance,
        checklist_result: ChecklistItemResult,
        item_template: ChecklistItemTemplate,
        author_id: str,
    ) -> Defect | None:
        if checklist_result.status not in {"warning", "critical"}:
            return None
        if checklist_result.equipment_id is None:
            return None

        equipment = await self.session.get(Equipment, checklist_result.equipment_id)
        if equipment is None:
            raise KeyError(f"Equipment {checklist_result.equipment_id} not found")

        stability_input = await self.get_stability_input(equipment.id)
        stability = self.stability_calculator.calculate(stability_input)
        severity_input = self._severity_input_from_checklist_result(
            checklist_result,
            item_template,
            stability.risk_factor,
        )
        severity = self.severity_calculator.calculate(severity_input)

        title = f"Отклонение по чек-листу: {item_template.question[:160]}"
        description = checklist_result.comment or f"Результат пункта чек-листа: {checklist_result.result_code}"
        return await self._create_defect(
            org_id=checklist_instance.round_instance.org_id,
            equipment_id=equipment.id,
            source_checklist_id=checklist_instance.id,
            checkpoint_id=checklist_result.route_step_id,
            created_by=author_id,
            title=title,
            description=description,
            severity=severity.severity,
            attention_marker=severity.severity in {"high", "critical"},
            payload_json={
                "source": "checklist_item_result",
                "checklistItemResultId": checklist_result.id,
                "itemTemplateId": item_template.id,
                "resultCode": checklist_result.result_code,
                "resultStatus": checklist_result.status,
                "severity": self._severity_payload(severity),
                "stability": self._stability_payload(stability),
            },
        )

    async def create_from_equipment_reading(
        self,
        equipment: Equipment,
        parameter_def: EquipmentParameterDef,
        reading: EquipmentParameterReading,
        status: str,
        message: str,
        author_id: str,
    ) -> Defect | None:
        if status not in {"warning", "critical"}:
            return None

        stability_input = await self.get_stability_input(equipment.id)
        stability = self.stability_calculator.calculate(stability_input)
        severity_input = self._severity_input_from_reading(status, stability.risk_factor)
        severity = self.severity_calculator.calculate(severity_input)

        return await self._create_defect(
            org_id=equipment.org_id,
            equipment_id=equipment.id,
            source_checklist_id=None,
            checkpoint_id=reading.route_step_id,
            created_by=author_id,
            title=f"Отклонение параметра: {parameter_def.name}",
            description=message,
            severity=severity.severity,
            attention_marker=severity.severity in {"high", "critical"},
            payload_json={
                "source": "equipment_parameter_reading",
                "readingId": reading.id,
                "parameterDefId": parameter_def.id,
                "parameterCode": parameter_def.code,
                "valueNum": reading.value_num,
                "valueText": reading.value_text,
                "readingStatus": status,
                "limits": reading.payload_json.get("limits", {}),
                "severity": self._severity_payload(severity),
                "stability": self._stability_payload(stability),
            },
        )

    async def get_stability_input(self, equipment_id: str) -> EquipmentStabilityInput:
        now = datetime.now(timezone.utc)
        first_reading_result = await self.session.execute(
            select(func.min(EquipmentParameterReading.reading_ts)).where(
                EquipmentParameterReading.equipment_id == equipment_id,
            )
        )
        first_reading_at = first_reading_result.scalar_one_or_none()
        if first_reading_at is None:
            history_depth_days = 0
        else:
            history_depth_days = max(0, (now - first_reading_at).days)

        warnings_last_30_days = await self._count_readings_by_status(equipment_id, "warning", now - timedelta(days=30))
        critical_last_30_days = await self._count_readings_by_status(equipment_id, "critical", now - timedelta(days=30))
        defects_last_90_days = await self._count_defects(equipment_id, now - timedelta(days=90))

        return EquipmentStabilityInput(
            history_depth_days=history_depth_days,
            warnings_last_30_days=warnings_last_30_days,
            critical_last_30_days=critical_last_30_days,
            defects_last_90_days=defects_last_90_days,
        )

    async def _count_readings_by_status(self, equipment_id: str, status: str, since: datetime) -> int:
        result = await self.session.execute(
            select(func.count(EquipmentParameterReading.id)).where(
                EquipmentParameterReading.equipment_id == equipment_id,
                EquipmentParameterReading.reading_ts >= since,
                EquipmentParameterReading.payload_json["status"].astext == status,
            )
        )
        return int(result.scalar_one())

    async def _count_defects(self, equipment_id: str, since: datetime) -> int:
        result = await self.session.execute(
            select(func.count(Defect.id)).where(
                Defect.equipment_id == equipment_id,
                Defect.detected_at >= since,
            )
        )
        return int(result.scalar_one())

    async def _create_defect(
        self,
        org_id: str,
        equipment_id: str,
        source_checklist_id: str | None,
        checkpoint_id: str | None,
        created_by: str,
        title: str,
        description: str | None,
        severity: str,
        attention_marker: bool,
        payload_json: dict,
    ) -> Defect:
        now = datetime.now(timezone.utc)
        defect = Defect(
            id=str(uuid4()),
            org_id=org_id,
            equipment_id=equipment_id,
            detected_at=now,
            source_checklist_id=source_checklist_id,
            checkpoint_id=checkpoint_id,
            created_by=created_by,
            title=title,
            description=description,
            severity=severity,
            attention_marker=attention_marker,
            status="detected",
            payload_json=payload_json,
        )
        self.session.add(defect)
        self.session.add(
            JournalEntry(
                id=str(uuid4()),
                event_ts=now,
                event_type="defect.detected",
                entity_type="defect",
                entity_id=defect.id,
                org_id=org_id,
                equipment_id=equipment_id,
                employee_id=created_by,
                payload_json={
                    "authorId": created_by,
                    "severity": severity,
                    "attentionMarker": attention_marker,
                    "source": payload_json.get("source"),
                },
            )
        )
        self.session.add(
            AuditLog(
                id=str(uuid4()),
                entity_type="defect",
                entity_id=defect.id,
                op="create",
                author_id=created_by,
                before_json=None,
                after_json={
                    "equipment_id": defect.equipment_id,
                    "severity": defect.severity,
                    "status": defect.status,
                    "title": defect.title,
                    "payload_json": defect.payload_json,
                },
            )
        )
        await self.session.flush()
        return defect

    async def _write_update_audit(self, defect: Defect, op: str, author_id: str, before: dict) -> None:
        now = datetime.now(timezone.utc)
        self.session.add(
            JournalEntry(
                id=str(uuid4()),
                event_ts=now,
                event_type=f"defect.{op}",
                entity_type="defect",
                entity_id=defect.id,
                org_id=defect.org_id,
                equipment_id=defect.equipment_id,
                employee_id=author_id,
                payload_json={
                    "authorId": author_id,
                    "status": defect.status,
                    "severity": defect.severity,
                },
            )
        )
        self.session.add(
            AuditLog(
                id=str(uuid4()),
                entity_type="defect",
                entity_id=defect.id,
                op=op,
                author_id=author_id,
                before_json=before,
                after_json=self._defect_snapshot(defect),
            )
        )
        await self.session.flush()

    def _severity_input_from_checklist_result(
        self,
        checklist_result: ChecklistItemResult,
        item_template: ChecklistItemTemplate,
        equipment_risk_factor: float,
    ) -> DefectSeverityInput:
        severity_config = item_template.payload_json.get("severity", {})
        answer_config = item_template.payload_json.get("answers", {}).get(checklist_result.result_code or "", {})
        deviation_score = answer_config.get("score")
        if deviation_score is None:
            deviation_score = 2 if checklist_result.status == "critical" else 1

        return DefectSeverityInput(
            impact_score=int(severity_config.get("impactScore", 1)),
            safety_score=int(severity_config.get("safetyScore", 0)),
            deviation_score=int(deviation_score),
            repeat_score=1 if checklist_result.status == "critical" else 0,
            downtime_score=int(severity_config.get("downtimeScore", 1 if checklist_result.status == "critical" else 0)),
            equipment_risk_factor=equipment_risk_factor,
        )

    def _severity_input_from_reading(self, status: str, equipment_risk_factor: float) -> DefectSeverityInput:
        return DefectSeverityInput(
            impact_score=1 if status == "warning" else 2,
            safety_score=0,
            deviation_score=1 if status == "warning" else 2,
            repeat_score=0,
            downtime_score=1 if status == "critical" else 0,
            equipment_risk_factor=equipment_risk_factor,
        )

    def _severity_payload(self, severity) -> dict:
        return {
            "baseScore": severity.base_score,
            "finalScore": severity.final_score,
            "level": severity.severity_level,
            "severity": severity.severity,
            "factors": severity.factors,
            "rulesApplied": severity.rules_applied,
        }

    def _stability_payload(self, stability) -> dict:
        return {
            "score": stability.stability_score,
            "riskFactor": stability.risk_factor,
            "basis": stability.basis,
        }

    def _defect_snapshot(self, defect: Defect) -> dict:
        return {
            "id": defect.id,
            "equipment_id": defect.equipment_id,
            "severity": defect.severity,
            "attention_marker": defect.attention_marker,
            "status": defect.status,
            "payload_json": defect.payload_json,
        }
