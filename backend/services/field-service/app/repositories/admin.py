from datetime import timedelta
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    AuditLog,
    ChecklistInstance,
    ChecklistItemTemplate,
    ChecklistTemplate,
    Employee,
    Equipment,
    JournalEntry,
    RouteStep,
    RouteTemplate,
    RoundInstance,
)
from app.schemas import ChecklistTemplateCreate, EquipmentCreate, RoundCreate, RouteCreate


class AdminRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_equipment(self, payload: EquipmentCreate, author_id: str) -> Equipment:
        await self._ensure_absent(Equipment, payload.id, "Equipment")

        qr_tag = payload.qr_tag or f"QR:{payload.id}"
        equipment = Equipment(
            id=payload.id,
            org_id=payload.org_id,
            code=payload.code,
            name=payload.name,
            tech_no=payload.tech_no,
            passport_no=payload.passport_no,
            serial_no=payload.serial_no,
            type_id=payload.type_id,
            location_id=payload.location_id,
            location=payload.location,
            state_id=payload.state_id,
            qr_tag=qr_tag,
            nfc_tag=payload.nfc_tag,
            passport_json=payload.passport_json,
            snapshot_json={
                **payload.snapshot_json,
                "tags": {
                    **payload.snapshot_json.get("tags", {}),
                    "qr": qr_tag,
                    "nfc": payload.nfc_tag,
                },
            },
        )
        self.session.add(equipment)
        self._add_journal(
            event_type="equipment.created",
            entity_type="equipment",
            entity_id=equipment.id,
            org_id=equipment.org_id,
            equipment_id=equipment.id,
            employee_id=author_id,
            payload_json={"authorId": author_id, "qrTag": equipment.qr_tag, "nfcTag": equipment.nfc_tag},
        )
        self._add_audit("equipment", equipment.id, "create", author_id, None, self._equipment_snapshot(equipment))
        await self.session.flush()
        return equipment

    async def create_checklist_template(
        self,
        payload: ChecklistTemplateCreate,
        author_id: str,
    ) -> ChecklistTemplate:
        await self._ensure_absent(ChecklistTemplate, payload.id, "Checklist template")

        template = ChecklistTemplate(
            id=payload.id,
            org_id=payload.org_id,
            name=payload.name,
            scope=payload.scope,
            equipment_type_id=payload.equipment_type_id,
            version=payload.version,
            active_from=payload.active_from,
            active_to=payload.active_to,
            snapshot_json=payload.snapshot_json,
        )
        template.items = [
            ChecklistItemTemplate(
                id=item.id or f"{payload.id}-ITEM-{item.seq_no}",
                checklist_template_id=payload.id,
                seq_no=item.seq_no,
                question=item.question,
                answer_type=item.answer_type,
                required_flag=item.required_flag,
                norm_ref=item.norm_ref,
                payload_json=item.payload_json,
            )
            for item in payload.items
        ]
        self.session.add(template)
        self._add_journal(
            event_type="checklist_template.created",
            entity_type="checklist_template",
            entity_id=template.id,
            org_id=template.org_id,
            employee_id=author_id,
            payload_json={"authorId": author_id, "itemsCount": len(template.items)},
        )
        self._add_audit(
            "checklist_template",
            template.id,
            "create",
            author_id,
            None,
            {"id": template.id, "name": template.name, "items_count": len(template.items)},
        )
        await self.session.flush()
        return template

    async def create_route(self, payload: RouteCreate, author_id: str) -> RouteTemplate:
        await self._ensure_absent(RouteTemplate, payload.id, "Route")
        for step in payload.steps:
            await self._ensure_exists(Equipment, step.equipment_id, "Equipment")

        route = RouteTemplate(
            id=payload.id,
            org_id=payload.org_id,
            department_id=payload.department_id,
            name=payload.name,
            route_type=payload.route_type,
            location=payload.location,
            duration_min=payload.duration_min,
            planning_rule=payload.planning_rule,
            qualification_id=payload.qualification_id,
            version=payload.version,
            is_active=payload.is_active,
            snapshot_json=payload.snapshot_json,
        )
        route.steps = [
            RouteStep(
                id=step.id or f"{payload.id}-STEP-{step.seq_no}",
                route_template_id=payload.id,
                seq_no=step.seq_no,
                equipment_id=step.equipment_id,
                checkpoint_id=step.checkpoint_id,
                mandatory_flag=step.mandatory_flag,
                confirm_by=step.confirm_by,
                payload_json=step.payload_json,
            )
            for step in sorted(payload.steps, key=lambda item: item.seq_no)
        ]
        self.session.add(route)
        self._add_journal(
            event_type="route.created",
            entity_type="route_template",
            entity_id=route.id,
            org_id=route.org_id,
            employee_id=author_id,
            payload_json={"authorId": author_id, "stepsCount": len(route.steps)},
        )
        self._add_audit(
            "route_template",
            route.id,
            "create",
            author_id,
            None,
            {"id": route.id, "name": route.name, "steps_count": len(route.steps)},
        )
        await self.session.flush()
        return route

    async def create_round(self, payload: RoundCreate, author_id: str) -> RoundInstance:
        route = await self._ensure_exists(RouteTemplate, payload.route_template_id, "Route")
        await self._ensure_exists(ChecklistTemplate, payload.checklist_template_id, "Checklist template")
        await self._ensure_exists(Employee, payload.employee_id, "Employee")

        round_id = payload.id or f"ROUND-{uuid4()}"
        await self._ensure_absent(RoundInstance, round_id, "Round")

        planned_end = payload.planned_end or payload.planned_start + timedelta(minutes=route.duration_min)
        round_instance = RoundInstance(
            id=round_id,
            org_id=payload.org_id,
            route_template_id=payload.route_template_id,
            planned_start=payload.planned_start,
            planned_end=planned_end,
            shift_id=payload.shift_id,
            employee_id=payload.employee_id,
            status="planned",
            source_doc_id=payload.source_doc_id,
            qualification_id=payload.qualification_id or route.qualification_id,
            snapshot_json=payload.snapshot_json,
        )
        checklist_instance = ChecklistInstance(
            id=f"CL-{uuid4()}",
            round_instance_id=round_id,
            checklist_template_id=payload.checklist_template_id,
            status="draft",
            completion_pct=0,
            snapshot_json={"entityRef": {"entityType": "round", "entityId": round_id}},
        )
        self.session.add(round_instance)
        self.session.add(checklist_instance)
        self._add_journal(
            event_type="round.created",
            entity_type="round",
            entity_id=round_instance.id,
            org_id=round_instance.org_id,
            employee_id=round_instance.employee_id,
            shift_id=round_instance.shift_id,
            payload_json={
                "authorId": author_id,
                "routeTemplateId": round_instance.route_template_id,
                "checklistTemplateId": checklist_instance.checklist_template_id,
            },
        )
        self._add_audit(
            "round",
            round_instance.id,
            "create",
            author_id,
            None,
            {
                "id": round_instance.id,
                "route_template_id": round_instance.route_template_id,
                "employee_id": round_instance.employee_id,
                "planned_start": round_instance.planned_start.isoformat(),
                "planned_end": round_instance.planned_end.isoformat() if round_instance.planned_end else None,
            },
        )
        await self.session.flush()
        return round_instance

    async def _ensure_absent(self, model, entity_id: str, entity_name: str) -> None:
        if await self.session.get(model, entity_id) is not None:
            raise ValueError(f"{entity_name} {entity_id} already exists")

    async def _ensure_exists(self, model, entity_id: str, entity_name: str):
        entity = await self.session.get(model, entity_id)
        if entity is None:
            raise KeyError(f"{entity_name} {entity_id} not found")
        return entity

    def _add_journal(
        self,
        event_type: str,
        entity_type: str,
        entity_id: str,
        org_id: str | None,
        employee_id: str | None,
        payload_json: dict,
        equipment_id: str | None = None,
        shift_id: str | None = None,
    ) -> None:
        from datetime import datetime, timezone

        self.session.add(
            JournalEntry(
                id=str(uuid4()),
                event_ts=datetime.now(timezone.utc),
                event_type=event_type,
                entity_type=entity_type,
                entity_id=entity_id,
                org_id=org_id,
                equipment_id=equipment_id,
                employee_id=employee_id,
                shift_id=shift_id,
                payload_json=payload_json,
            )
        )

    def _add_audit(
        self,
        entity_type: str,
        entity_id: str,
        op: str,
        author_id: str,
        before_json: dict | None,
        after_json: dict | None,
    ) -> None:
        self.session.add(
            AuditLog(
                id=str(uuid4()),
                entity_type=entity_type,
                entity_id=entity_id,
                op=op,
                author_id=author_id,
                before_json=before_json,
                after_json=after_json,
            )
        )

    def _equipment_snapshot(self, equipment: Equipment) -> dict:
        return {
            "id": equipment.id,
            "name": equipment.name,
            "type_id": equipment.type_id,
            "location": equipment.location,
            "qr_tag": equipment.qr_tag,
            "nfc_tag": equipment.nfc_tag,
        }
