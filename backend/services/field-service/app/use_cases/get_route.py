from app.repositories import RoutesRepository
from app.schemas import RouteRead


class GetRouteUseCase:
    def __init__(self, repository: RoutesRepository) -> None:
        self.repository = repository

    async def execute(self, route_id: str) -> RouteRead:
        route = await self.repository.get(route_id)
        return RouteRead.model_validate(route)
