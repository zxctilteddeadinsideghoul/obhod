from app.repositories import RoutesRepository
from app.schemas import RouteRead


class ListRoutesUseCase:
    def __init__(self, repository: RoutesRepository) -> None:
        self.repository = repository

    async def execute(self) -> list[RouteRead]:
        routes = await self.repository.list()
        return [RouteRead.model_validate(route) for route in routes]
