from app.repositories import TokensRepository
from app.schemas import PrincipalRead


class GetCurrentUserUseCase:
    def __init__(self, tokens_repository: TokensRepository) -> None:
        self.tokens_repository = tokens_repository

    async def execute(self, authorization: str | None) -> PrincipalRead | None:
        return await self.tokens_repository.get_principal_by_authorization(authorization)
