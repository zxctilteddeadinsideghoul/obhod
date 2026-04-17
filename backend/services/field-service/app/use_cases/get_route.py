from app.repositories import FieldRepository
from app.schemas import RouteRead


class GetRouteUseCase:
    def __init__(self, repository: FieldRepository) -> None:
        self.repository = repository

    async def execute(self, route_id: str) -> RouteRead:
        route = await self.repository.get_route(route_id)
        return RouteRead.model_validate(route)
