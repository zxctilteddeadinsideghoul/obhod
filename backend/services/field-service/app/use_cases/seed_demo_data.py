from app.repositories import FieldRepository


class SeedDemoDataUseCase:
    def __init__(self, repository: FieldRepository) -> None:
        self.repository = repository

    async def execute(self) -> dict[str, str]:
        await self.repository.seed_demo_data()
        return {"status": "ok"}
