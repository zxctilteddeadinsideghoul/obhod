from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import AdminRepository
from app.schemas import RoundCreate, RoundRead


class CreateRoundUseCase:
    def __init__(self, session: AsyncSession, repository: AdminRepository) -> None:
        self.session = session
        self.repository = repository

    async def execute(self, payload: RoundCreate, author_id: str, user_role: str) -> RoundRead:
        if user_role != "ADMIN":
            raise PermissionError("Admin role required")

        round_instance = await self.repository.create_round(payload, author_id)
        await self.session.commit()
        return RoundRead.model_validate(round_instance)
