from app.repositories import ChecklistsRepository
from app.schemas import ChecklistTemplateRead


class ListChecklistTemplatesUseCase:
    def __init__(self, repository: ChecklistsRepository) -> None:
        self.repository = repository

    async def execute(self) -> list[ChecklistTemplateRead]:
        templates = await self.repository.list_templates()
        return [ChecklistTemplateRead.model_validate(template) for template in templates]
