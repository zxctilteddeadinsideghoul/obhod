from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import AuditLog, ChecklistInstance, ChecklistItemResult, ChecklistItemTemplate, ChecklistTemplate, JournalEntry
from app.schemas import ChecklistItemResultCreate


class ChecklistsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_templates(self) -> list[ChecklistTemplate]:
        result = await self.session.execute(
            select(ChecklistTemplate)
            .options(selectinload(ChecklistTemplate.items))
            .order_by(ChecklistTemplate.name)
        )
        return list(result.scalars().unique().all())

    async def get_template(self, template_id: str) -> ChecklistTemplate:
        result = await self.session.execute(
            select(ChecklistTemplate)
            .where(ChecklistTemplate.id == template_id)
            .options(selectinload(ChecklistTemplate.items))
        )
        template = result.scalars().unique().one_or_none()
        if template is None:
            raise KeyError(f"Checklist template {template_id} not found")
        return template

    async def get_instance_for_round(self, round_id: str) -> ChecklistInstance:
        result = await self.session.execute(
            select(ChecklistInstance)
            .where(ChecklistInstance.round_instance_id == round_id)
            .options(
                selectinload(ChecklistInstance.round_instance),
                selectinload(ChecklistInstance.checklist_template).selectinload(ChecklistTemplate.items),
                selectinload(ChecklistInstance.results),
            )
            .order_by(ChecklistInstance.created_at)
        )
        checklist_instance = result.scalars().unique().first()
        if checklist_instance is None:
            raise KeyError(f"Checklist for round {round_id} not found")
        return checklist_instance

    async def get_instance(self, checklist_instance_id: str) -> ChecklistInstance:
        result = await self.session.execute(
            select(ChecklistInstance)
            .where(ChecklistInstance.id == checklist_instance_id)
            .options(
                selectinload(ChecklistInstance.round_instance),
                selectinload(ChecklistInstance.checklist_template).selectinload(ChecklistTemplate.items),
                selectinload(ChecklistInstance.results),
            )
        )
        checklist_instance = result.scalars().unique().one_or_none()
        if checklist_instance is None:
            raise KeyError(f"Checklist instance {checklist_instance_id} not found")
        return checklist_instance

    async def mark_started(self, checklist_instance: ChecklistInstance, author_id: str) -> ChecklistInstance:
        now = datetime.now(timezone.utc)
        before = {
            "status": checklist_instance.status,
            "started_at": checklist_instance.started_at.isoformat() if checklist_instance.started_at else None,
        }

        checklist_instance.status = "in_progress"
        if checklist_instance.started_at is None:
            checklist_instance.started_at = now

        self.session.add(
            JournalEntry(
                id=str(uuid4()),
                event_ts=now,
                event_type="checklist.started",
                entity_type="checklist_instance",
                entity_id=checklist_instance.id,
                org_id=checklist_instance.round_instance.org_id,
                employee_id=checklist_instance.round_instance.employee_id,
                shift_id=checklist_instance.round_instance.shift_id,
                payload_json={"authorId": author_id, "roundId": checklist_instance.round_instance_id},
            )
        )
        self.session.add(
            AuditLog(
                id=str(uuid4()),
                entity_type="checklist_instance",
                entity_id=checklist_instance.id,
                op="start",
                author_id=author_id,
                before_json=before,
                after_json={"status": checklist_instance.status, "started_at": checklist_instance.started_at.isoformat()},
            )
        )
        await self.session.flush()
        return checklist_instance

    async def submit_item_result(
        self,
        checklist_instance: ChecklistInstance,
        item_template_id: str,
        payload: ChecklistItemResultCreate,
        author_id: str,
    ) -> tuple[ChecklistItemResult, ChecklistInstance]:
        item_template = self._find_item_template(checklist_instance, item_template_id)
        result_status = self._infer_result_status(item_template, payload)

        existing_result = await self._get_existing_result(checklist_instance.id, item_template_id)
        before = self._result_snapshot(existing_result) if existing_result is not None else None
        if existing_result is None:
            existing_result = ChecklistItemResult(
                id=str(uuid4()),
                checklist_instance_id=checklist_instance.id,
                item_template_id=item_template_id,
            )
            self.session.add(existing_result)

        existing_result.equipment_id = payload.equipment_id
        existing_result.result_code = payload.result_code
        existing_result.result_value = payload.result_value
        existing_result.comment = payload.comment
        existing_result.due_date = payload.due_date
        existing_result.status = result_status
        checklist_instance.status = "in_progress"
        if checklist_instance.started_at is None:
            checklist_instance.started_at = datetime.now(timezone.utc)

        await self.session.flush()
        checklist_instance.completion_pct = await self._calculate_completion_pct(checklist_instance)

        now = datetime.now(timezone.utc)
        self.session.add(
            JournalEntry(
                id=str(uuid4()),
                event_ts=now,
                event_type="checklist.item_submitted",
                entity_type="checklist_item_result",
                entity_id=existing_result.id,
                org_id=checklist_instance.round_instance.org_id,
                equipment_id=existing_result.equipment_id,
                employee_id=checklist_instance.round_instance.employee_id,
                shift_id=checklist_instance.round_instance.shift_id,
                payload_json={
                    "authorId": author_id,
                    "checklistInstanceId": checklist_instance.id,
                    "itemTemplateId": item_template_id,
                    "status": result_status,
                },
            )
        )
        self.session.add(
            AuditLog(
                id=str(uuid4()),
                entity_type="checklist_item_result",
                entity_id=existing_result.id,
                op="submit",
                author_id=author_id,
                before_json=before,
                after_json=self._result_snapshot(existing_result),
            )
        )
        await self.session.flush()
        return existing_result, checklist_instance

    async def mark_finished(self, checklist_instance: ChecklistInstance, author_id: str) -> ChecklistInstance:
        checklist_instance.completion_pct = await self._calculate_completion_pct(checklist_instance)
        missing_items = await self.list_missing_required_items(checklist_instance)
        if missing_items:
            raise ValueError(f"Required checklist items are not completed: {', '.join(missing_items)}")

        now = datetime.now(timezone.utc)
        before = {
            "status": checklist_instance.status,
            "finished_at": checklist_instance.finished_at.isoformat() if checklist_instance.finished_at else None,
            "completion_pct": checklist_instance.completion_pct,
        }
        checklist_instance.status = "completed"
        checklist_instance.finished_at = now
        checklist_instance.completion_pct = 100

        self.session.add(
            JournalEntry(
                id=str(uuid4()),
                event_ts=now,
                event_type="checklist.completed",
                entity_type="checklist_instance",
                entity_id=checklist_instance.id,
                org_id=checklist_instance.round_instance.org_id,
                employee_id=checklist_instance.round_instance.employee_id,
                shift_id=checklist_instance.round_instance.shift_id,
                payload_json={"authorId": author_id, "roundId": checklist_instance.round_instance_id},
            )
        )
        self.session.add(
            AuditLog(
                id=str(uuid4()),
                entity_type="checklist_instance",
                entity_id=checklist_instance.id,
                op="finish",
                author_id=author_id,
                before_json=before,
                after_json={
                    "status": checklist_instance.status,
                    "finished_at": checklist_instance.finished_at.isoformat(),
                    "completion_pct": checklist_instance.completion_pct,
                },
            )
        )
        await self.session.flush()
        return checklist_instance

    async def list_missing_required_items(self, checklist_instance: ChecklistInstance) -> list[str]:
        required_items = [item for item in checklist_instance.checklist_template.items if item.required_flag]
        if not required_items:
            return []

        result = await self.session.execute(
            select(ChecklistItemResult.item_template_id).where(
                ChecklistItemResult.checklist_instance_id == checklist_instance.id,
                ChecklistItemResult.item_template_id.in_([item.id for item in required_items]),
            )
        )
        completed_item_ids = set(result.scalars().all())
        return [item.id for item in required_items if item.id not in completed_item_ids]

    async def _get_existing_result(
        self,
        checklist_instance_id: str,
        item_template_id: str,
    ) -> ChecklistItemResult | None:
        result = await self.session.execute(
            select(ChecklistItemResult).where(
                ChecklistItemResult.checklist_instance_id == checklist_instance_id,
                ChecklistItemResult.item_template_id == item_template_id,
            )
        )
        return result.scalars().one_or_none()

    async def _calculate_completion_pct(self, checklist_instance: ChecklistInstance) -> int:
        required_items = [item for item in checklist_instance.checklist_template.items if item.required_flag]
        if not required_items:
            return 100

        result = await self.session.execute(
            select(ChecklistItemResult.item_template_id).where(
                ChecklistItemResult.checklist_instance_id == checklist_instance.id,
                ChecklistItemResult.item_template_id.in_([item.id for item in required_items]),
            )
        )
        completed_count = len(set(result.scalars().all()))
        return int(completed_count / len(required_items) * 100)

    def _find_item_template(
        self,
        checklist_instance: ChecklistInstance,
        item_template_id: str,
    ) -> ChecklistItemTemplate:
        for item in checklist_instance.checklist_template.items:
            if item.id == item_template_id:
                return item
        raise KeyError(f"Checklist item template {item_template_id} not found")

    def _infer_result_status(
        self,
        item_template: ChecklistItemTemplate,
        payload: ChecklistItemResultCreate,
    ) -> str:
        if payload.result_code in {"critical", "fail_critical"}:
            return "critical"
        if payload.result_code in {"warning", "fail", "abnormal"}:
            return "warning"
        if item_template.answer_type == "bool" and payload.result_value.get("value") is False:
            return "warning"
        return "normal"

    def _result_snapshot(self, result: ChecklistItemResult | None) -> dict | None:
        if result is None:
            return None
        return {
            "id": result.id,
            "checklist_instance_id": result.checklist_instance_id,
            "item_template_id": result.item_template_id,
            "equipment_id": result.equipment_id,
            "result_code": result.result_code,
            "result_value": result.result_value,
            "comment": result.comment,
            "due_date": result.due_date.isoformat() if result.due_date else None,
            "status": result.status,
        }
