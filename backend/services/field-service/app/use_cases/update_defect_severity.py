from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import DefectsRepository
from app.schemas import DefectRead, DefectSeverityUpdate


ALLOWED_DEFECT_SEVERITIES = {"info", "low", "medium", "high", "critical"}


class UpdateDefectSeverityUseCase:
    def __init__(self, session: AsyncSession, repository: DefectsRepository) -> None:
        self.session = session
        self.repository = repository

    async def execute(
        self,
        defect_id: str,
        payload: DefectSeverityUpdate,
        author_id: str,
        user_role: str,
    ) -> DefectRead:
        if user_role != "ADMIN":
            raise PermissionError("Admin role required")
        if payload.severity not in ALLOWED_DEFECT_SEVERITIES:
            raise ValueError(f"Unsupported defect severity: {payload.severity}")

        defect = await self.repository.get(defect_id)
        defect = await self.repository.update_severity(defect, payload.severity, payload.comment, author_id)
        await self.session.commit()
        return DefectRead.model_validate(defect)
