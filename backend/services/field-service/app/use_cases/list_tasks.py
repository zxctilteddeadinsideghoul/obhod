from app.repositories import FieldRepository
from app.schemas import TaskSummaryRead


class ListTasksUseCase:
    def __init__(self, repository: FieldRepository) -> None:
        self.repository = repository

    async def execute(self, user_id: str, user_role: str) -> list[TaskSummaryRead]:
        if user_role == "ADMIN":
            rounds = await self.repository.list_all_rounds()
        else:
            rounds = await self.repository.list_rounds_for_employee(user_id)

        return [
            TaskSummaryRead(
                id=round_item.id,
                status=round_item.status,
                route_id=round_item.route_template_id,
                route_name=round_item.route_template.name,
                planned_start=round_item.planned_start,
                planned_end=round_item.planned_end,
                completion_pct=round_item.snapshot_json.get("completionPct", 0),
            )
            for round_item in rounds
        ]
