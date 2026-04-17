from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import AdminRepository
from app.schemas import RouteCreate, RouteRead


class CreateRouteUseCase:
    def __init__(self, session: AsyncSession, repository: AdminRepository) -> None:
        self.session = session
        self.repository = repository

    async def execute(self, payload: RouteCreate, author_id: str, user_role: str) -> RouteRead:
        if user_role != "ADMIN":
            raise PermissionError("Admin role required")

        route = await self.repository.create_route(payload, author_id)
        await self.session.commit()
        return RouteRead.model_validate(route)
