from app.repositories import RoundsRepository
from app.schemas import RoundRead


class ListMyRoundsUseCase:
    def __init__(self, repository: RoundsRepository) -> None:
        self.repository = repository

    async def execute(self, employee_id: str) -> list[RoundRead]:
        rounds = await self.repository.list_for_employee(employee_id)
        return [RoundRead.model_validate(round_item) for round_item in rounds]
