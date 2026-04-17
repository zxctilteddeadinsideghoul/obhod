from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import ChecklistsRepository
from app.schemas import ChecklistInstanceRead, ChecklistItemResultCreate, ChecklistItemResultRead, ChecklistItemResultSubmitRead


class SubmitChecklistItemResultUseCase:
    def __init__(
        self,
        session: AsyncSession,
        checklists_repository: ChecklistsRepository,
    ) -> None:
        self.session = session
        self.checklists_repository = checklists_repository

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

        result, checklist_instance = await self.checklists_repository.submit_item_result(
            checklist_instance,
            item_template_id,
            payload,
            user_id,
        )
        await self.session.commit()
        return ChecklistItemResultSubmitRead(
            result=ChecklistItemResultRead.model_validate(result),
            checklist_instance=ChecklistInstanceRead.model_validate(checklist_instance),
        )
