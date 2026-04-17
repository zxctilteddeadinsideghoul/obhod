from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import ChecklistsRepository, RoundsRepository
from app.schemas import RoundRead


class StartRoundUseCase:
    def __init__(
        self,
        session: AsyncSession,
        rounds_repository: RoundsRepository,
        checklists_repository: ChecklistsRepository,
    ) -> None:
        self.session = session
        self.rounds_repository = rounds_repository
        self.checklists_repository = checklists_repository

    async def execute(self, round_id: str, user_id: str, user_role: str) -> RoundRead:
        round_instance = await self.rounds_repository.get(round_id)
        if user_role != "ADMIN" and round_instance.employee_id != user_id:
            raise PermissionError("Round is not assigned to current worker")
        if round_instance.status == "completed":
            raise ValueError("Completed round cannot be started")

        checklist_instance = await self.checklists_repository.get_instance_for_round(round_id)
        await self.rounds_repository.mark_started(round_instance, user_id)
        await self.checklists_repository.mark_started(checklist_instance, user_id)
        await self.session.commit()
        return RoundRead.model_validate(round_instance)
