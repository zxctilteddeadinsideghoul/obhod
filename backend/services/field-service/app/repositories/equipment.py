from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditLog, Equipment, EquipmentParameterDef, EquipmentParameterReading, JournalEntry
from app.schemas import EquipmentParameterReadingCreate


class EquipmentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(self) -> list[Equipment]:
        result = await self.session.execute(select(Equipment).order_by(Equipment.name))
        return list(result.scalars().all())

    async def get(self, equipment_id: str) -> Equipment:
        equipment = await self.session.get(Equipment, equipment_id)
        if equipment is None:
            raise KeyError(f"Equipment {equipment_id} not found")
        return equipment

    async def get_parameter_def(self, parameter_def_id: str) -> EquipmentParameterDef:
        parameter_def = await self.session.get(EquipmentParameterDef, parameter_def_id)
        if parameter_def is None:
            raise KeyError(f"Parameter definition {parameter_def_id} not found")
        return parameter_def

    async def create_reading(
        self,
        equipment: Equipment,
        parameter_def: EquipmentParameterDef,
        payload: EquipmentParameterReadingCreate,
        author_id: str,
    ) -> tuple[EquipmentParameterReading, str, str]:
        reading_ts = payload.reading_ts or datetime.now(timezone.utc)
        within_limits, status, message = self._evaluate_limits(parameter_def, payload.value_num)
        reading_payload = {
            **payload.payload_json,
            "status": status,
            "message": message,
            "limits": {
                "min": parameter_def.min_value,
                "max": parameter_def.max_value,
                "criticalMin": parameter_def.critical_min,
                "criticalMax": parameter_def.critical_max,
            },
        }

        reading = EquipmentParameterReading(
            id=str(uuid4()),
            equipment_id=equipment.id,
            parameter_def_id=parameter_def.id,
            reading_ts=reading_ts,
            value_num=payload.value_num,
            value_text=payload.value_text,
            source=payload.source,
            route_step_id=payload.route_step_id,
            checklist_item_result_id=payload.checklist_item_result_id,
            within_limits=within_limits,
            payload_json=reading_payload,
        )
        self.session.add(reading)

        now = datetime.now(timezone.utc)
        self.session.add(
            JournalEntry(
                id=str(uuid4()),
                event_ts=now,
                event_type="equipment.reading_submitted",
                entity_type="equipment_parameter_reading",
                entity_id=reading.id,
                org_id=equipment.org_id,
                equipment_id=equipment.id,
                employee_id=author_id,
                payload_json={
                    "authorId": author_id,
                    "parameterDefId": parameter_def.id,
                    "parameterCode": parameter_def.code,
                    "status": status,
                    "withinLimits": within_limits,
                },
            )
        )
        self.session.add(
            AuditLog(
                id=str(uuid4()),
                entity_type="equipment_parameter_reading",
                entity_id=reading.id,
                op="create",
                author_id=author_id,
                before_json=None,
                after_json={
                    "equipment_id": reading.equipment_id,
                    "parameter_def_id": reading.parameter_def_id,
                    "reading_ts": reading.reading_ts.isoformat(),
                    "value_num": reading.value_num,
                    "value_text": reading.value_text,
                    "within_limits": reading.within_limits,
                    "status": status,
                },
            )
        )
        await self.session.flush()
        return reading, status, message

    def _evaluate_limits(
        self,
        parameter_def: EquipmentParameterDef,
        value_num: float | None,
    ) -> tuple[bool | None, str, str]:
        if value_num is None:
            return None, "not_evaluated", "Numeric value is not provided"

        if parameter_def.critical_min is not None and value_num < parameter_def.critical_min:
            return False, "critical", "Value is below critical minimum"
        if parameter_def.critical_max is not None and value_num > parameter_def.critical_max:
            return False, "critical", "Value is above critical maximum"
        if parameter_def.min_value is not None and value_num < parameter_def.min_value:
            return False, "warning", "Value is below recommended minimum"
        if parameter_def.max_value is not None and value_num > parameter_def.max_value:
            return False, "warning", "Value is above recommended maximum"

        has_limits = any(
            limit is not None
            for limit in (
                parameter_def.min_value,
                parameter_def.max_value,
                parameter_def.critical_min,
                parameter_def.critical_max,
            )
        )
        if not has_limits:
            return None, "not_evaluated", "Parameter has no configured limits"

        return True, "normal", "Value is within configured limits"
