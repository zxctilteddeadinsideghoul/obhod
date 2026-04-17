from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import AdminRepository
from app.schemas import EquipmentCreate, EquipmentRead


class CreateEquipmentUseCase:
    def __init__(self, session: AsyncSession, repository: AdminRepository) -> None:
        self.session = session
        self.repository = repository

    async def execute(self, payload: EquipmentCreate, author_id: str, user_role: str) -> EquipmentRead:
        if user_role != "ADMIN":
            raise PermissionError("Admin role required")

        equipment = await self.repository.create_equipment(payload, author_id)
        await self.session.commit()
        return EquipmentRead.model_validate(equipment)
