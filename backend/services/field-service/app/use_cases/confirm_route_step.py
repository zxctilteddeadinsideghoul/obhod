from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import ChecklistsRepository, RouteStepVisitsRepository, RoundsRepository
from app.schemas import (
    ChecklistInstanceRead,
    ChecklistTemplateRead,
    EquipmentRead,
    RouteStepConfirmCreate,
    RouteStepConfirmRead,
    RouteStepVisitRead,
)


class ConfirmRouteStepUseCase:
    def __init__(
        self,
        session: AsyncSession,
        rounds_repository: RoundsRepository,
        route_step_visits_repository: RouteStepVisitsRepository,
        checklists_repository: ChecklistsRepository,
    ) -> None:
        self.session = session
        self.rounds_repository = rounds_repository
        self.route_step_visits_repository = route_step_visits_repository
        self.checklists_repository = checklists_repository

    async def execute(
        self,
        round_id: str,
        route_step_id: str,
        payload: RouteStepConfirmCreate,
        user_id: str,
        user_role: str,
    ) -> RouteStepConfirmRead:
        round_instance = await self.rounds_repository.get(round_id)
        if user_role != "ADMIN" and round_instance.employee_id != user_id:
            raise PermissionError("Task is not assigned to current worker")
        if round_instance.status == "completed":
            raise ValueError("Completed round cannot be changed")

        route_step = await self.route_step_visits_repository.get_route_step_for_round(round_instance, route_step_id)
        visit = await self.route_step_visits_repository.confirm(round_instance, route_step, payload, user_id)
        checklist_instance = await self.checklists_repository.get_instance_for_round(round_id)
        await self.session.commit()

        return RouteStepConfirmRead(
            status=visit.status,
            visit=RouteStepVisitRead.model_validate(visit),
            equipment=EquipmentRead.model_validate(route_step.equipment),
            checklist_instance=ChecklistInstanceRead.model_validate(checklist_instance),
            checklist_template=ChecklistTemplateRead.model_validate(checklist_instance.checklist_template),
        )
