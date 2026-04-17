from app.repositories import RoundsRepository, TasksRepository
from app.schemas import ChecklistInstanceRead, ChecklistTemplateRead, EquipmentRead, RouteRead, RoundRead, TaskDetailRead


class GetTaskDetailUseCase:
    def __init__(self, rounds_repository: RoundsRepository, tasks_repository: TasksRepository) -> None:
        self.rounds_repository = rounds_repository
        self.tasks_repository = tasks_repository

    async def execute(self, round_id: str, user_id: str, user_role: str) -> TaskDetailRead:
        round_item = await self.rounds_repository.get(round_id)
        if user_role != "ADMIN" and round_item.employee_id != user_id:
            raise PermissionError("Round is not assigned to current worker")

        round_instance, route, equipment, checklist_instance, checklist_template = await self.tasks_repository.get_detail(round_id)
        return TaskDetailRead(
            round=RoundRead.model_validate(round_instance),
            route=RouteRead.model_validate(route),
            equipment=[EquipmentRead.model_validate(item) for item in equipment],
            checklist_instance=(
                ChecklistInstanceRead.model_validate(checklist_instance)
                if checklist_instance is not None
                else None
            ),
            checklist_template=(
                ChecklistTemplateRead.model_validate(checklist_template)
                if checklist_template is not None
                else None
            ),
        )
