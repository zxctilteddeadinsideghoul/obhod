from app.repositories import FieldRepository
from app.schemas import ChecklistTemplateRead


class ListChecklistTemplatesUseCase:
    def __init__(self, repository: FieldRepository) -> None:
        self.repository = repository

    async def execute(self) -> list[ChecklistTemplateRead]:
        templates = await self.repository.list_checklist_templates()
        return [ChecklistTemplateRead.model_validate(template) for template in templates]
