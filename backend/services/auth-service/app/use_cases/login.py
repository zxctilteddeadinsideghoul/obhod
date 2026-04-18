from app.core.config import Settings
from app.repositories import TokensRepository
from app.schemas import LoginResponse


class LoginUseCase:
    def __init__(self, settings: Settings, tokens_repository: TokensRepository) -> None:
        self.settings = settings
        self.tokens_repository = tokens_repository

    async def execute(self, username: str, password: str) -> LoginResponse | None:
        principal = await self.tokens_repository.get_principal_by_credentials(username, password)
        if principal is None:
            return None

        return LoginResponse(
            access_token=self.tokens_repository.issue_access_token(principal),
            expires_in=self.settings.access_token_ttl_sec,
            user=principal,
        )
