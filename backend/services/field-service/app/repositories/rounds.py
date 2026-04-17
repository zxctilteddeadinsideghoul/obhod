from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import AuditLog, JournalEntry, RoundInstance
from app.models.field import RouteStep


class RoundsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_for_employee(self, employee_id: str) -> list[RoundInstance]:
        result = await self.session.execute(
            select(RoundInstance)
            .where(RoundInstance.employee_id == employee_id)
            .options(selectinload(RoundInstance.route_template))
            .order_by(RoundInstance.planned_start)
        )
        return list(result.scalars().all())

    async def list_all(self) -> list[RoundInstance]:
        result = await self.session.execute(
            select(RoundInstance)
            .options(selectinload(RoundInstance.route_template))
            .order_by(RoundInstance.planned_start)
        )
        return list(result.scalars().all())

    async def get(self, round_id: str) -> RoundInstance:
        result = await self.session.execute(
            select(RoundInstance)
            .where(RoundInstance.id == round_id)
            .options(selectinload(RoundInstance.route_template))
        )
        round_instance = result.scalars().one_or_none()
        if round_instance is None:
            raise KeyError(f"Round {round_id} not found")
        return round_instance

    async def get_by_route_step_and_employee(self, route_step_id: str, employee_id: str) -> RoundInstance:
        result = await self.session.execute(
            select(RoundInstance)
            .join(RouteStep, RouteStep.route_template_id == RoundInstance.route_template_id)
            .where(
                RouteStep.id == route_step_id,
                RoundInstance.employee_id == employee_id,
                RoundInstance.status != "completed",
            )
            .options(selectinload(RoundInstance.route_template))
            .order_by(RoundInstance.planned_start)
        )
        round_instance = result.scalars().first()
        if round_instance is None:
            raise KeyError(f"Active round for route step {route_step_id} not found")
        return round_instance

    async def mark_started(self, round_instance: RoundInstance, author_id: str) -> RoundInstance:
        now = datetime.now(timezone.utc)
        before = {
            "status": round_instance.status,
            "actual_start": round_instance.actual_start.isoformat() if round_instance.actual_start else None,
        }

        round_instance.status = "in_progress"
        if round_instance.actual_start is None:
            round_instance.actual_start = now

        self.session.add(
            JournalEntry(
                id=str(uuid4()),
                event_ts=now,
                event_type="round.started",
                entity_type="round",
                entity_id=round_instance.id,
                org_id=round_instance.org_id,
                employee_id=round_instance.employee_id,
                shift_id=round_instance.shift_id,
                payload_json={"authorId": author_id},
            )
        )
        self.session.add(
            AuditLog(
                id=str(uuid4()),
                entity_type="round",
                entity_id=round_instance.id,
                op="start",
                author_id=author_id,
                before_json=before,
                after_json={"status": round_instance.status, "actual_start": round_instance.actual_start.isoformat()},
            )
        )
        await self.session.flush()
        return round_instance

    async def mark_finished(self, round_instance: RoundInstance, author_id: str) -> RoundInstance:
        now = datetime.now(timezone.utc)
        before = {
            "status": round_instance.status,
            "actual_end": round_instance.actual_end.isoformat() if round_instance.actual_end else None,
        }

        round_instance.status = "completed"
        round_instance.actual_end = now

        self.session.add(
            JournalEntry(
                id=str(uuid4()),
                event_ts=now,
                event_type="round.completed",
                entity_type="round",
                entity_id=round_instance.id,
                org_id=round_instance.org_id,
                employee_id=round_instance.employee_id,
                shift_id=round_instance.shift_id,
                payload_json={"authorId": author_id},
            )
        )
        self.session.add(
            AuditLog(
                id=str(uuid4()),
                entity_type="round",
                entity_id=round_instance.id,
                op="finish",
                author_id=author_id,
                before_json=before,
                after_json={"status": round_instance.status, "actual_end": round_instance.actual_end.isoformat()},
            )
        )
        await self.session.flush()
        return round_instance
