from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import FieldRepository
from app.use_cases import (
    GetChecklistTemplateUseCase,
    GetEquipmentUseCase,
    GetRouteUseCase,
    GetTaskDetailUseCase,
    ListChecklistTemplatesUseCase,
    ListEquipmentUseCase,
    ListMyRoundsUseCase,
    ListRoutesUseCase,
    ListTasksUseCase,
    SeedDemoDataUseCase,
)


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["app.api.dependencies"])

    db_session = providers.Dependency(instance_of=AsyncSession)

    field_repository = providers.Factory(FieldRepository, session=db_session)

    seed_demo_data_use_case = providers.Factory(SeedDemoDataUseCase, repository=field_repository)
    list_equipment_use_case = providers.Factory(ListEquipmentUseCase, repository=field_repository)
    get_equipment_use_case = providers.Factory(GetEquipmentUseCase, repository=field_repository)
    list_routes_use_case = providers.Factory(ListRoutesUseCase, repository=field_repository)
    get_route_use_case = providers.Factory(GetRouteUseCase, repository=field_repository)
    list_my_rounds_use_case = providers.Factory(ListMyRoundsUseCase, repository=field_repository)
    list_tasks_use_case = providers.Factory(ListTasksUseCase, repository=field_repository)
    get_task_detail_use_case = providers.Factory(GetTaskDetailUseCase, repository=field_repository)
    list_checklist_templates_use_case = providers.Factory(ListChecklistTemplatesUseCase, repository=field_repository)
    get_checklist_template_use_case = providers.Factory(GetChecklistTemplateUseCase, repository=field_repository)
