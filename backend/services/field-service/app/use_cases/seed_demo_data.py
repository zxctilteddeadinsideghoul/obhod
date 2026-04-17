from app.repositories import DemoDataRepository


class SeedDemoDataUseCase:
    def __init__(self, repository: DemoDataRepository) -> None:
        self.repository = repository

    async def execute(self) -> dict[str, str]:
        await self.repository.seed()
        return {"status": "ok"}
