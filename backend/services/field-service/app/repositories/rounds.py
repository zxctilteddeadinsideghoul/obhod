from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import RoundInstance


class RoundsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_for_employee(self, employee_id: str) -> list[RoundInstance]:
        result = await self.session.execute(
            select(RoundInstance)
            .where(RoundInstance.employee_id == employee_id)
            .options(selectinload(RoundInstance.route_template))
            .order_by(RoundInstance.planned_start)
        )
        return list(result.scalars().all())

    async def list_all(self) -> list[RoundInstance]:
        result = await self.session.execute(
            select(RoundInstance)
            .options(selectinload(RoundInstance.route_template))
            .order_by(RoundInstance.planned_start)
        )
        return list(result.scalars().all())

    async def get(self, round_id: str) -> RoundInstance:
        result = await self.session.execute(
            select(RoundInstance)
            .where(RoundInstance.id == round_id)
            .options(selectinload(RoundInstance.route_template))
        )
        round_instance = result.scalars().one_or_none()
        if round_instance is None:
            raise KeyError(f"Round {round_id} not found")
        return round_instance
