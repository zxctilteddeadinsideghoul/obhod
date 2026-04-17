from app.core.config import Settings
from app.schemas import PrincipalRead


class TokensRepository:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def get_principal_by_authorization(self, authorization: str | None) -> PrincipalRead | None:
        if authorization == f"Bearer {self.settings.dev_admin_token}":
            return PrincipalRead(id="dev-admin", role="ADMIN", name="Development Admin")

        if authorization == f"Bearer {self.settings.dev_auth_token}":
            return PrincipalRead(id="dev-worker", role="WORKER", name="Development Worker")

        return None
