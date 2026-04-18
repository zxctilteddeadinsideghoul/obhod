from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import DefectsRepository
from app.schemas import DefectRead, DefectStatusUpdate


ALLOWED_DEFECT_STATUSES = {"detected", "in_review", "accepted", "in_work", "resolved", "closed", "rejected"}


class UpdateDefectStatusUseCase:
    def __init__(self, session: AsyncSession, repository: DefectsRepository) -> None:
        self.session = session
        self.repository = repository

    async def execute(
        self,
        defect_id: str,
        payload: DefectStatusUpdate,
        author_id: str,
        user_role: str,
    ) -> DefectRead:
        if user_role != "ADMIN":
            raise PermissionError("Admin role required")
        if payload.status not in ALLOWED_DEFECT_STATUSES:
            raise ValueError(f"Unsupported defect status: {payload.status}")

        defect = await self.repository.get(defect_id)
        defect = await self.repository.update_status(defect, payload.status, payload.comment, author_id)
        await self.session.commit()
        return DefectRead.model_validate(defect)
