from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import AuditLog, Equipment, JournalEntry, RouteStep, RouteStepVisit, RoundInstance
from app.schemas import RouteStepConfirmCreate


class RouteStepVisitsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_route_step_for_round(self, round_instance: RoundInstance, route_step_id: str) -> RouteStep:
        result = await self.session.execute(
            select(RouteStep)
            .where(
                RouteStep.id == route_step_id,
                RouteStep.route_template_id == round_instance.route_template_id,
            )
            .options(selectinload(RouteStep.equipment))
        )
        route_step = result.scalars().one_or_none()
        if route_step is None:
            raise KeyError(f"Route step {route_step_id} not found in round route")
        return route_step

    async def confirm(
        self,
        round_instance: RoundInstance,
        route_step: RouteStep,
        payload: RouteStepConfirmCreate,
        author_id: str,
    ) -> RouteStepVisit:
        expected_value = self._expected_marker(route_step.equipment, payload.confirm_by)
        if expected_value is None:
            raise ValueError(f"Equipment has no {payload.confirm_by} marker")
        if payload.scanned_value != expected_value:
            raise ValueError("Scanned marker does not match route step equipment")

        now = datetime.now(timezone.utc)
        existing_visit = await self._get_existing_visit(round_instance.id, route_step.id)
        if existing_visit is not None:
            existing_visit.confirmed_by = payload.confirm_by
            existing_visit.scanned_value = payload.scanned_value
            existing_visit.confirmed_at = now
            existing_visit.status = "confirmed"
            existing_visit.payload_json = payload.payload_json
            visit = existing_visit
        else:
            visit = RouteStepVisit(
                id=str(uuid4()),
                round_instance_id=round_instance.id,
                route_step_id=route_step.id,
                equipment_id=route_step.equipment_id,
                employee_id=round_instance.employee_id,
                confirmed_by=payload.confirm_by,
                scanned_value=payload.scanned_value,
                confirmed_at=now,
                status="confirmed",
                payload_json=payload.payload_json,
            )
            self.session.add(visit)

        self.session.add(
            JournalEntry(
                id=str(uuid4()),
                event_ts=now,
                event_type="route_step.confirmed",
                entity_type="route_step_visit",
                entity_id=visit.id,
                org_id=round_instance.org_id,
                equipment_id=route_step.equipment_id,
                employee_id=round_instance.employee_id,
                shift_id=round_instance.shift_id,
                payload_json={
                    "authorId": author_id,
                    "roundId": round_instance.id,
                    "routeStepId": route_step.id,
                    "confirmedBy": payload.confirm_by,
                },
            )
        )
        self.session.add(
            AuditLog(
                id=str(uuid4()),
                entity_type="route_step_visit",
                entity_id=visit.id,
                op="confirm",
                author_id=author_id,
                before_json=None,
                after_json={
                    "round_instance_id": round_instance.id,
                    "route_step_id": route_step.id,
                    "equipment_id": route_step.equipment_id,
                    "confirmed_by": payload.confirm_by,
                    "confirmed_at": now.isoformat(),
                    "status": visit.status,
                },
            )
        )
        await self.session.flush()
        return visit

    async def _get_existing_visit(
        self,
        round_instance_id: str,
        route_step_id: str,
    ) -> RouteStepVisit | None:
        result = await self.session.execute(
            select(RouteStepVisit).where(
                RouteStepVisit.round_instance_id == round_instance_id,
                RouteStepVisit.route_step_id == route_step_id,
            )
        )
        return result.scalars().one_or_none()

    def _expected_marker(self, equipment: Equipment, confirm_by: str) -> str | None:
        if confirm_by == "qr":
            return equipment.qr_tag
        if confirm_by == "nfc":
            return equipment.nfc_tag
        raise ValueError("Unsupported confirmation method")
