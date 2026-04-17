from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Equipment


class EquipmentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(self) -> list[Equipment]:
        result = await self.session.execute(select(Equipment).order_by(Equipment.name))
        return list(result.scalars().all())

    async def get(self, equipment_id: str) -> Equipment:
        equipment = await self.session.get(Equipment, equipment_id)
        if equipment is None:
            raise KeyError(f"Equipment {equipment_id} not found")
        return equipment
