from app.repositories import DefectsRepository
from app.schemas import DefectRead


class ListDefectsUseCase:
    def __init__(self, repository: DefectsRepository) -> None:
        self.repository = repository

    async def execute(
        self,
        user_role: str,
        status: str | None = None,
        severity: str | None = None,
        equipment_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[DefectRead]:
        if user_role != "ADMIN":
            raise PermissionError("Admin role required")

        defects = await self.repository.list(
            status=status,
            severity=severity,
            equipment_id=equipment_id,
            limit=limit,
            offset=offset,
        )
        return [DefectRead.model_validate(defect) for defect in defects]
