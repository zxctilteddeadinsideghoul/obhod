from app.repositories import FieldRepository
from app.schemas import ChecklistTemplateRead, EquipmentRead, RouteRead, RoundRead


class FieldService:
    def __init__(self, repository: FieldRepository) -> None:
        self.repository = repository

    async def seed_demo_data(self) -> dict[str, str]:
        await self.repository.seed_demo_data()
        return {"status": "ok"}

    async def list_equipment(self) -> list[EquipmentRead]:
        equipment = await self.repository.list_equipment()
        return [EquipmentRead.model_validate(item) for item in equipment]

    async def get_equipment(self, equipment_id: str) -> EquipmentRead:
        return EquipmentRead.model_validate(await self.repository.get_equipment(equipment_id))

    async def list_routes(self) -> list[RouteRead]:
        routes = await self.repository.list_routes()
        return [RouteRead.model_validate(route) for route in routes]

    async def get_route(self, route_id: str) -> RouteRead:
        return RouteRead.model_validate(await self.repository.get_route(route_id))

    async def list_my_rounds(self, employee_id: str) -> list[RoundRead]:
        rounds = await self.repository.list_rounds_for_employee(employee_id)
        return [RoundRead.model_validate(round_item) for round_item in rounds]

    async def list_checklist_templates(self) -> list[ChecklistTemplateRead]:
        templates = await self.repository.list_checklist_templates()
        return [ChecklistTemplateRead.model_validate(template) for template in templates]

    async def get_checklist_template(self, template_id: str) -> ChecklistTemplateRead:
        return ChecklistTemplateRead.model_validate(await self.repository.get_checklist_template(template_id))
