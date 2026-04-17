from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import RouteTemplate
from app.models.field import RouteStep


class RoutesRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(self) -> list[RouteTemplate]:
        result = await self.session.execute(
            select(RouteTemplate)
            .options(selectinload(RouteTemplate.steps).selectinload(RouteStep.equipment))
            .order_by(RouteTemplate.name)
        )
        return list(result.scalars().unique().all())

    async def get(self, route_id: str) -> RouteTemplate:
        result = await self.session.execute(
            select(RouteTemplate)
            .where(RouteTemplate.id == route_id)
            .options(selectinload(RouteTemplate.steps).selectinload(RouteStep.equipment))
        )
        route = result.scalars().unique().one_or_none()
        if route is None:
            raise KeyError(f"Route {route_id} not found")
        return route
