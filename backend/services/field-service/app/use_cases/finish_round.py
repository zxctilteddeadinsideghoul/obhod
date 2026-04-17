from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import ChecklistsRepository, RoundsRepository, RouteStepVisitsRepository
from app.schemas import RoundRead


class FinishRoundUseCase:
    def __init__(
        self,
        session: AsyncSession,
        rounds_repository: RoundsRepository,
        checklists_repository: ChecklistsRepository,
        route_step_visits_repository: RouteStepVisitsRepository,
    ) -> None:
        self.session = session
        self.rounds_repository = rounds_repository
        self.checklists_repository = checklists_repository
        self.route_step_visits_repository = route_step_visits_repository

    async def execute(self, round_id: str, user_id: str, user_role: str) -> RoundRead:
        round_instance = await self.rounds_repository.get(round_id)
        if user_role != "ADMIN" and round_instance.employee_id != user_id:
            raise PermissionError("Round is not assigned to current worker")
        if round_instance.status == "completed":
            return RoundRead.model_validate(round_instance)

        checklist_instance = await self.checklists_repository.get_instance_for_round(round_id)
        missing_step_ids = await self.route_step_visits_repository.list_missing_mandatory_step_ids(round_instance)
        if missing_step_ids:
            raise ValueError(f"Required route steps are not confirmed: {', '.join(missing_step_ids)}")

        await self.checklists_repository.mark_finished(checklist_instance, user_id)
        await self.rounds_repository.mark_finished(round_instance, user_id)
        await self.session.commit()
        return RoundRead.model_validate(round_instance)
