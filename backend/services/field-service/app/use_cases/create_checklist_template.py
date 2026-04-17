from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import AdminRepository
from app.schemas import ChecklistTemplateCreate, ChecklistTemplateRead


class CreateChecklistTemplateUseCase:
    def __init__(self, session: AsyncSession, repository: AdminRepository) -> None:
        self.session = session
        self.repository = repository

    async def execute(
        self,
        payload: ChecklistTemplateCreate,
        author_id: str,
        user_role: str,
    ) -> ChecklistTemplateRead:
        if user_role != "ADMIN":
            raise PermissionError("Admin role required")

        template = await self.repository.create_checklist_template(payload, author_id)
        await self.session.commit()
        return ChecklistTemplateRead.model_validate(template)
