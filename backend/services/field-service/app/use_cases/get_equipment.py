from app.repositories import FieldRepository
from app.schemas import EquipmentRead


class GetEquipmentUseCase:
    def __init__(self, repository: FieldRepository) -> None:
        self.repository = repository

    async def execute(self, equipment_id: str) -> EquipmentRead:
        equipment = await self.repository.get_equipment(equipment_id)
        return EquipmentRead.model_validate(equipment)
