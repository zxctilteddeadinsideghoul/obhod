from dependency_injector import providers
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.containers import Container
from app.db import get_db_session
from app.use_cases import (
    FinishRoundUseCase,
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
    StartRoundUseCase,
    SubmitChecklistItemResultUseCase,
    SubmitEquipmentReadingUseCase,
)


def get_container(request: Request) -> Container:
    return request.app.container  # type: ignore[attr-defined]


def _build_with_session(container: Container, provider, session: AsyncSession):
    with container.db_session.override(providers.Object(session)):
        return provider()


def get_seed_demo_data_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
) -> SeedDemoDataUseCase:
    return _build_with_session(container, container.seed_demo_data_use_case, session)


def get_list_equipment_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
) -> ListEquipmentUseCase:
    return _build_with_session(container, container.list_equipment_use_case, session)


def get_get_equipment_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
) -> GetEquipmentUseCase:
    return _build_with_session(container, container.get_equipment_use_case, session)


def get_submit_equipment_reading_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
) -> SubmitEquipmentReadingUseCase:
    return _build_with_session(container, container.submit_equipment_reading_use_case, session)


def get_list_routes_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
) -> ListRoutesUseCase:
    return _build_with_session(container, container.list_routes_use_case, session)


def get_get_route_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
) -> GetRouteUseCase:
    return _build_with_session(container, container.get_route_use_case, session)


def get_list_my_rounds_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
) -> ListMyRoundsUseCase:
    return _build_with_session(container, container.list_my_rounds_use_case, session)


def get_list_tasks_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
) -> ListTasksUseCase:
    return _build_with_session(container, container.list_tasks_use_case, session)


def get_get_task_detail_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
) -> GetTaskDetailUseCase:
    return _build_with_session(container, container.get_task_detail_use_case, session)


def get_start_round_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
) -> StartRoundUseCase:
    return _build_with_session(container, container.start_round_use_case, session)


def get_submit_checklist_item_result_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
) -> SubmitChecklistItemResultUseCase:
    return _build_with_session(container, container.submit_checklist_item_result_use_case, session)


def get_finish_round_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
) -> FinishRoundUseCase:
    return _build_with_session(container, container.finish_round_use_case, session)


def get_list_checklist_templates_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
) -> ListChecklistTemplatesUseCase:
    return _build_with_session(container, container.list_checklist_templates_use_case, session)


def get_get_checklist_template_use_case(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
) -> GetChecklistTemplateUseCase:
    return _build_with_session(container, container.get_checklist_template_use_case, session)
