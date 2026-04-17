from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import ChecklistTemplate


class ChecklistsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_templates(self) -> list[ChecklistTemplate]:
        result = await self.session.execute(
            select(ChecklistTemplate)
            .options(selectinload(ChecklistTemplate.items))
            .order_by(ChecklistTemplate.name)
        )
        return list(result.scalars().unique().all())

    async def get_template(self, template_id: str) -> ChecklistTemplate:
        result = await self.session.execute(
            select(ChecklistTemplate)
            .where(ChecklistTemplate.id == template_id)
            .options(selectinload(ChecklistTemplate.items))
        )
        template = result.scalars().unique().one_or_none()
        if template is None:
            raise KeyError(f"Checklist template {template_id} not found")
        return template
