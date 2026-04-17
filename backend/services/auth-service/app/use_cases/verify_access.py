from app.repositories import TokensRepository
from app.schemas import AuthVerificationRead


class VerifyAccessUseCase:
    def __init__(self, tokens_repository: TokensRepository) -> None:
        self.tokens_repository = tokens_repository

    async def execute(
        self,
        authorization: str | None,
        forwarded_method: str | None,
        forwarded_uri: str | None,
    ) -> AuthVerificationRead | None:
        principal = await self.tokens_repository.get_principal_by_authorization(authorization)
        if principal is None:
            return None

        return AuthVerificationRead(
            status="allowed",
            method=forwarded_method or "",
            uri=forwarded_uri or "",
            principal=principal,
        )
