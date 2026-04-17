from app.repositories import FieldRepository
from app.schemas import EquipmentRead


class ListEquipmentUseCase:
    def __init__(self, repository: FieldRepository) -> None:
        self.repository = repository

    async def execute(self) -> list[EquipmentRead]:
        equipment = await self.repository.list_equipment()
        return [EquipmentRead.model_validate(item) for item in equipment]
