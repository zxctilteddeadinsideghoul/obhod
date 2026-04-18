from app.repositories import DemoDataRepository


class SeedDemoDataUseCase:
    def __init__(self, repository: DemoDataRepository) -> None:
        self.repository = repository

    async def execute(self, include_rounds: bool = True) -> dict[str, str | bool]:
        await self.repository.seed(include_rounds=include_rounds)
        return {"status": "ok", "include_rounds": include_rounds}
