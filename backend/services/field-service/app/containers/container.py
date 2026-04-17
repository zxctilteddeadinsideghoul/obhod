from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import (
    ChecklistsRepository,
    DemoDataRepository,
    EquipmentRepository,
    RoundsRepository,
    RoutesRepository,
    TasksRepository,
)
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

    checklists_repository = providers.Factory(ChecklistsRepository, session=db_session)
    demo_data_repository = providers.Factory(DemoDataRepository, session=db_session)
    equipment_repository = providers.Factory(EquipmentRepository, session=db_session)
    rounds_repository = providers.Factory(RoundsRepository, session=db_session)
    routes_repository = providers.Factory(RoutesRepository, session=db_session)
    tasks_repository = providers.Factory(TasksRepository, session=db_session)

    seed_demo_data_use_case = providers.Factory(SeedDemoDataUseCase, repository=demo_data_repository)
    list_equipment_use_case = providers.Factory(ListEquipmentUseCase, repository=equipment_repository)
    get_equipment_use_case = providers.Factory(GetEquipmentUseCase, repository=equipment_repository)
    list_routes_use_case = providers.Factory(ListRoutesUseCase, repository=routes_repository)
    get_route_use_case = providers.Factory(GetRouteUseCase, repository=routes_repository)
    list_my_rounds_use_case = providers.Factory(ListMyRoundsUseCase, repository=rounds_repository)
    list_tasks_use_case = providers.Factory(ListTasksUseCase, rounds_repository=rounds_repository)
    get_task_detail_use_case = providers.Factory(
        GetTaskDetailUseCase,
        rounds_repository=rounds_repository,
        tasks_repository=tasks_repository,
    )
    list_checklist_templates_use_case = providers.Factory(
        ListChecklistTemplatesUseCase,
        repository=checklists_repository,
    )
    get_checklist_template_use_case = providers.Factory(
        GetChecklistTemplateUseCase,
        repository=checklists_repository,
    )
