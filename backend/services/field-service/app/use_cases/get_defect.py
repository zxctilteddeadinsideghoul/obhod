from app.repositories import DefectsRepository
from app.schemas import DefectRead


class GetDefectUseCase:
    def __init__(self, repository: DefectsRepository) -> None:
        self.repository = repository

    async def execute(self, defect_id: str, user_role: str) -> DefectRead:
        if user_role != "ADMIN":
            raise PermissionError("Admin role required")

        defect = await self.repository.get(defect_id)
        return DefectRead.model_validate(defect)
