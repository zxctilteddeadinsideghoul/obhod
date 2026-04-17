from app.repositories import ChecklistsRepository
from app.schemas import ChecklistTemplateRead


class GetChecklistTemplateUseCase:
    def __init__(self, repository: ChecklistsRepository) -> None:
        self.repository = repository

    async def execute(self, template_id: str) -> ChecklistTemplateRead:
        template = await self.repository.get_template(template_id)
        return ChecklistTemplateRead.model_validate(template)
