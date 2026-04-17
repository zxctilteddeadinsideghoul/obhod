from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import RuleBasedDefectSeverityCalculator, RuleBasedEquipmentStabilityCalculator
from app.repositories import (
    AdminRepository,
    AttachmentsRepository,
    ChecklistsRepository,
    DemoDataRepository,
    DefectsRepository,
    EquipmentRepository,
    RoundsRepository,
    RouteStepVisitsRepository,
    RoutesRepository,
    TasksRepository,
)
from app.use_cases import (
    ConfirmRouteStepUseCase,
    CreateChecklistTemplateUseCase,
    CreateEquipmentUseCase,
    CreateRoundUseCase,
    CreateRouteUseCase,
    DownloadAttachmentUseCase,
    FinishRoundUseCase,
    GetDefectUseCase,
    GetChecklistTemplateUseCase,
    GetEquipmentUseCase,
    GetRouteUseCase,
    GetTaskDetailUseCase,
    ListChecklistTemplatesUseCase,
    ListAttachmentsUseCase,
    ListEquipmentUseCase,
    ListDefectsUseCase,
    ListMyRoundsUseCase,
    ListRoutesUseCase,
    ListTasksUseCase,
    SeedDemoDataUseCase,
    StartRoundUseCase,
    SubmitChecklistItemResultUseCase,
    SubmitEquipmentReadingUseCase,
    UploadAttachmentUseCase,
    UpdateDefectSeverityUseCase,
    UpdateDefectStatusUseCase,
)
from app.core.config import get_settings
from app.services import ObjectStorage


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["app.api.dependencies"])

    db_session = providers.Dependency(instance_of=AsyncSession)

    object_storage = providers.Singleton(ObjectStorage, settings=providers.Callable(get_settings))
    equipment_stability_calculator = providers.Factory(RuleBasedEquipmentStabilityCalculator)
    defect_severity_calculator = providers.Factory(RuleBasedDefectSeverityCalculator)

    admin_repository = providers.Factory(AdminRepository, session=db_session)
    attachments_repository = providers.Factory(AttachmentsRepository, session=db_session)
    checklists_repository = providers.Factory(ChecklistsRepository, session=db_session)
    defects_repository = providers.Factory(
        DefectsRepository,
        session=db_session,
        stability_calculator=equipment_stability_calculator,
        severity_calculator=defect_severity_calculator,
    )
    demo_data_repository = providers.Factory(DemoDataRepository, session=db_session)
    equipment_repository = providers.Factory(EquipmentRepository, session=db_session)
    route_step_visits_repository = providers.Factory(RouteStepVisitsRepository, session=db_session)
    rounds_repository = providers.Factory(RoundsRepository, session=db_session)
    routes_repository = providers.Factory(RoutesRepository, session=db_session)
    tasks_repository = providers.Factory(TasksRepository, session=db_session)

    create_equipment_use_case = providers.Factory(
        CreateEquipmentUseCase,
        session=db_session,
        repository=admin_repository,
    )
    create_checklist_template_use_case = providers.Factory(
        CreateChecklistTemplateUseCase,
        session=db_session,
        repository=admin_repository,
    )
    create_route_use_case = providers.Factory(
        CreateRouteUseCase,
        session=db_session,
        repository=admin_repository,
    )
    create_round_use_case = providers.Factory(
        CreateRoundUseCase,
        session=db_session,
        repository=admin_repository,
    )
    upload_attachment_use_case = providers.Factory(
        UploadAttachmentUseCase,
        session=db_session,
        attachments_repository=attachments_repository,
        object_storage=object_storage,
    )
    list_attachments_use_case = providers.Factory(
        ListAttachmentsUseCase,
        attachments_repository=attachments_repository,
    )
    download_attachment_use_case = providers.Factory(
        DownloadAttachmentUseCase,
        attachments_repository=attachments_repository,
        object_storage=object_storage,
    )
    list_defects_use_case = providers.Factory(
        ListDefectsUseCase,
        repository=defects_repository,
    )
    get_defect_use_case = providers.Factory(
        GetDefectUseCase,
        repository=defects_repository,
    )
    update_defect_status_use_case = providers.Factory(
        UpdateDefectStatusUseCase,
        session=db_session,
        repository=defects_repository,
    )
    update_defect_severity_use_case = providers.Factory(
        UpdateDefectSeverityUseCase,
        session=db_session,
        repository=defects_repository,
    )
    seed_demo_data_use_case = providers.Factory(SeedDemoDataUseCase, repository=demo_data_repository)
    list_equipment_use_case = providers.Factory(ListEquipmentUseCase, repository=equipment_repository)
    get_equipment_use_case = providers.Factory(GetEquipmentUseCase, repository=equipment_repository)
    submit_equipment_reading_use_case = providers.Factory(
        SubmitEquipmentReadingUseCase,
        session=db_session,
        equipment_repository=equipment_repository,
        rounds_repository=rounds_repository,
        route_step_visits_repository=route_step_visits_repository,
        defects_repository=defects_repository,
    )
    confirm_route_step_use_case = providers.Factory(
        ConfirmRouteStepUseCase,
        session=db_session,
        rounds_repository=rounds_repository,
        route_step_visits_repository=route_step_visits_repository,
        checklists_repository=checklists_repository,
    )
    list_routes_use_case = providers.Factory(ListRoutesUseCase, repository=routes_repository)
    get_route_use_case = providers.Factory(GetRouteUseCase, repository=routes_repository)
    list_my_rounds_use_case = providers.Factory(ListMyRoundsUseCase, repository=rounds_repository)
    list_tasks_use_case = providers.Factory(ListTasksUseCase, rounds_repository=rounds_repository)
    get_task_detail_use_case = providers.Factory(
        GetTaskDetailUseCase,
        rounds_repository=rounds_repository,
        tasks_repository=tasks_repository,
    )
    start_round_use_case = providers.Factory(
        StartRoundUseCase,
        session=db_session,
        rounds_repository=rounds_repository,
        checklists_repository=checklists_repository,
    )
    submit_checklist_item_result_use_case = providers.Factory(
        SubmitChecklistItemResultUseCase,
        session=db_session,
        checklists_repository=checklists_repository,
        route_step_visits_repository=route_step_visits_repository,
        defects_repository=defects_repository,
    )
    finish_round_use_case = providers.Factory(
        FinishRoundUseCase,
        session=db_session,
        rounds_repository=rounds_repository,
        checklists_repository=checklists_repository,
        route_step_visits_repository=route_step_visits_repository,
    )
    list_checklist_templates_use_case = providers.Factory(
        ListChecklistTemplatesUseCase,
        repository=checklists_repository,
    )
    get_checklist_template_use_case = providers.Factory(
        GetChecklistTemplateUseCase,
        repository=checklists_repository,
    )
