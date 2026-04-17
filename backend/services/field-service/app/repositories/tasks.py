from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import (
    ChecklistInstance,
    ChecklistItemResult,
    ChecklistTemplate,
    Equipment,
    EquipmentParameterDef,
    RouteTemplate,
    RoundInstance,
)
from app.models.field import RouteStep


class TasksRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_detail(
        self,
        round_id: str,
    ) -> tuple[
        RoundInstance,
        RouteTemplate,
        list[Equipment],
        ChecklistInstance | None,
        ChecklistTemplate | None,
        list[ChecklistItemResult],
        list[tuple[str, EquipmentParameterDef]],
    ]:
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

        checklist_results = await self._list_checklist_results(checklist_instance)
        equipment_parameters = await self._list_equipment_parameters(equipment)

        return (
            round_instance,
            route,
            equipment,
            checklist_instance,
            checklist_template,
            checklist_results,
            equipment_parameters,
        )

    async def _list_checklist_results(
        self,
        checklist_instance: ChecklistInstance | None,
    ) -> list[ChecklistItemResult]:
        if checklist_instance is None:
            return []

        result = await self.session.execute(
            select(ChecklistItemResult)
            .where(ChecklistItemResult.checklist_instance_id == checklist_instance.id)
            .order_by(ChecklistItemResult.created_at)
        )
        return list(result.scalars().all())

    async def _list_equipment_parameters(
        self,
        equipment: list[Equipment],
    ) -> list[tuple[str, EquipmentParameterDef]]:
        if not equipment:
            return []

        type_ids = sorted({item.type_id for item in equipment})
        result = await self.session.execute(
            select(EquipmentParameterDef)
            .where(EquipmentParameterDef.equipment_type_id.in_(type_ids))
            .order_by(EquipmentParameterDef.equipment_type_id, EquipmentParameterDef.name)
        )
        parameter_defs = list(result.scalars().all())

        equipment_by_type: dict[str, list[Equipment]] = {}
        for item in equipment:
            equipment_by_type.setdefault(item.type_id, []).append(item)

        return [
            (equipment_item.id, parameter_def)
            for parameter_def in parameter_defs
            for equipment_item in equipment_by_type.get(parameter_def.equipment_type_id, [])
        ]
