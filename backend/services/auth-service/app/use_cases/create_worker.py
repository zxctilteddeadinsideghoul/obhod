from app.repositories import TokensRepository
from app.schemas import PrincipalRead, WorkerCreate, WorkerRead


class CreateWorkerUseCase:
    def __init__(self, tokens_repository: TokensRepository) -> None:
        self.tokens_repository = tokens_repository

    async def execute(self, payload: WorkerCreate, principal: PrincipalRead) -> WorkerRead:
        if principal.role != "ADMIN":
            raise PermissionError("Only ADMIN can create workers")
        return await self.tokens_repository.create_worker(payload)
