from app.repositories import FieldRepository
from app.schemas import ChecklistTemplateRead


class GetChecklistTemplateUseCase:
    def __init__(self, repository: FieldRepository) -> None:
        self.repository = repository

    async def execute(self, template_id: str) -> ChecklistTemplateRead:
        template = await self.repository.get_checklist_template(template_id)
        return ChecklistTemplateRead.model_validate(template)
