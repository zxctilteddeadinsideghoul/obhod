from app.repositories import EquipmentRepository
from app.schemas import EquipmentRead


class ListEquipmentUseCase:
    def __init__(self, repository: EquipmentRepository) -> None:
        self.repository = repository

    async def execute(self) -> list[EquipmentRead]:
        equipment = await self.repository.list()
        return [EquipmentRead.model_validate(item) for item in equipment]
