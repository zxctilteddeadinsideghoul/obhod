from app.repositories import EquipmentRepository
from app.schemas import EquipmentRead


class GetEquipmentUseCase:
    def __init__(self, repository: EquipmentRepository) -> None:
        self.repository = repository

    async def execute(self, equipment_id: str) -> EquipmentRead:
        equipment = await self.repository.get(equipment_id)
        return EquipmentRead.model_validate(equipment)
