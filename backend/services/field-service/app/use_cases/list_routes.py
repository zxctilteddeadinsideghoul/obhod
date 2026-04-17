from app.repositories import FieldRepository
from app.schemas import RouteRead


class ListRoutesUseCase:
    def __init__(self, repository: FieldRepository) -> None:
        self.repository = repository

    async def execute(self) -> list[RouteRead]:
        routes = await self.repository.list_routes()
        return [RouteRead.model_validate(route) for route in routes]
