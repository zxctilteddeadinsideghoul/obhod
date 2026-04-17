from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import ChecklistInstance, ChecklistTemplate, Equipment, RouteTemplate, RoundInstance
from app.models.field import RouteStep


class TasksRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_detail(
        self,
        round_id: str,
    ) -> tuple[RoundInstance, RouteTemplate, list[Equipment], ChecklistInstance | None, ChecklistTemplate | None]:
        round_result = await self.session.execute(
            select(RoundInstance)
            .where(RoundInstance.id == round_id)
            .options(selectinload(RoundInstance.route_template))
        )
        round_instance = round_result.scalars().one_or_none()
        if round_instance is None:
            raise KeyError(f"Round {round_id} not found")

        route_result = await self.session.execute(
            select(RouteTemplate)
            .where(RouteTemplate.id == round_instance.route_template_id)
            .options(selectinload(RouteTemplate.steps).selectinload(RouteStep.equipment))
        )
        route = route_result.scalars().unique().one()
        equipment = [step.equipment for step in route.steps]

        checklist_result = await self.session.execute(
            select(ChecklistInstance)
            .where(ChecklistInstance.round_instance_id == round_id)
            .options(
                selectinload(ChecklistInstance.checklist_template).selectinload(ChecklistTemplate.items),
            )
            .order_by(ChecklistInstance.created_at)
        )
        checklist_instance = checklist_result.scalars().unique().first()
        checklist_template = checklist_instance.checklist_template if checklist_instance else None

        return round_instance, route, equipment, checklist_instance, checklist_template
