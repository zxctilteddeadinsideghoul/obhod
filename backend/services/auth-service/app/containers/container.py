from app.core.config import Settings
from app.repositories import TokensRepository
from app.use_cases import CreateWorkerUseCase, GetCurrentUserUseCase, LoginUseCase, VerifyAccessUseCase


class Container:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def tokens_repository(self) -> TokensRepository:
        return TokensRepository(settings=self.settings)

    def verify_access_use_case(self) -> VerifyAccessUseCase:
        return VerifyAccessUseCase(tokens_repository=self.tokens_repository())

    def get_current_user_use_case(self) -> GetCurrentUserUseCase:
        return GetCurrentUserUseCase(tokens_repository=self.tokens_repository())

    def login_use_case(self) -> LoginUseCase:
        return LoginUseCase(settings=self.settings, tokens_repository=self.tokens_repository())

    def create_worker_use_case(self) -> CreateWorkerUseCase:
        return CreateWorkerUseCase(tokens_repository=self.tokens_repository())
