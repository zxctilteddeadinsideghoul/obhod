from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import ChecklistsRepository, DefectsRepository, RouteStepVisitsRepository
from app.schemas import ChecklistInstanceRead, ChecklistItemResultCreate, ChecklistItemResultRead, ChecklistItemResultSubmitRead


class SubmitChecklistItemResultUseCase:
    def __init__(
        self,
        session: AsyncSession,
        checklists_repository: ChecklistsRepository,
        route_step_visits_repository: RouteStepVisitsRepository,
        defects_repository: DefectsRepository,
    ) -> None:
        self.session = session
        self.checklists_repository = checklists_repository
        self.route_step_visits_repository = route_step_visits_repository
        self.defects_repository = defects_repository

    async def execute(
        self,
        checklist_instance_id: str,
        item_template_id: str,
        payload: ChecklistItemResultCreate,
        user_id: str,
        user_role: str,
    ) -> ChecklistItemResultSubmitRead:
        checklist_instance = await self.checklists_repository.get_instance(checklist_instance_id)
        if user_role != "ADMIN" and checklist_instance.round_instance.employee_id != user_id:
            raise PermissionError("Checklist is not assigned to current worker")
        if checklist_instance.status == "completed":
            raise ValueError("Completed checklist cannot be changed")
        if payload.route_step_id is None:
            raise ValueError("route_step_id is required")

        await self.route_step_visits_repository.ensure_confirmed(
            checklist_instance.round_instance,
            payload.route_step_id,
            payload.equipment_id,
        )

        result, checklist_instance = await self.checklists_repository.submit_item_result(
            checklist_instance,
            item_template_id,
            payload,
            user_id,
        )
        item_template = self.checklists_repository.find_item_template(checklist_instance, item_template_id)
        await self.defects_repository.create_from_checklist_result(
            checklist_instance,
            result,
            item_template,
            user_id,
        )
        await self.session.commit()
        return ChecklistItemResultSubmitRead(
            result=ChecklistItemResultRead.model_validate(result),
            checklist_instance=ChecklistInstanceRead.model_validate(checklist_instance),
        )
