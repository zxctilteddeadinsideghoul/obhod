from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.api.dependencies import (
    get_get_checklist_template_use_case,
    get_get_equipment_use_case,
    get_get_route_use_case,
    get_get_task_detail_use_case,
    get_finish_round_use_case,
    get_list_checklist_templates_use_case,
    get_list_equipment_use_case,
    get_list_my_rounds_use_case,
    get_list_routes_use_case,
    get_list_tasks_use_case,
    get_seed_demo_data_use_case,
    get_start_round_use_case,
    get_submit_checklist_item_result_use_case,
    get_submit_equipment_reading_use_case,
)
from app.schemas import (
    ChecklistItemResultCreate,
    ChecklistItemResultSubmitRead,
    ChecklistTemplateRead,
    EquipmentParameterReadingCreate,
    EquipmentParameterReadingSubmitRead,
    EquipmentRead,
    RouteRead,
    RoundRead,
    TaskDetailRead,
    TaskSummaryRead,
)
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


router = APIRouter(prefix="/api/field", tags=["field"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"service": "field-service", "status": "ok"}


@router.get("/whoami")
async def whoami(
    x_user_id: str | None = Header(default=None),
    x_user_role: str | None = Header(default=None),
    x_user_name: str | None = Header(default=None),
) -> dict[str, str | None]:
    return {
        "service": "field-service",
        "user_id": x_user_id,
        "user_role": x_user_role,
        "user_name": x_user_name,
    }


@router.post("/admin/seed-demo")
async def seed_demo(
    x_user_role: str | None = Header(default=None),
    use_case: SeedDemoDataUseCase = Depends(get_seed_demo_data_use_case),
) -> dict[str, str]:
    if x_user_role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return await use_case.execute()


@router.get("/equipment", response_model=list[EquipmentRead])
async def list_equipment(
    use_case: ListEquipmentUseCase = Depends(get_list_equipment_use_case),
) -> list[EquipmentRead]:
    return await use_case.execute()


@router.get("/equipment/{equipment_id}", response_model=EquipmentRead)
async def get_equipment(
    equipment_id: str,
    use_case: GetEquipmentUseCase = Depends(get_get_equipment_use_case),
) -> EquipmentRead:
    try:
        return await use_case.execute(equipment_id)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipment not found")


@router.post("/equipment/{equipment_id}/readings", response_model=EquipmentParameterReadingSubmitRead)
async def submit_equipment_reading(
    equipment_id: str,
    payload: EquipmentParameterReadingCreate,
    x_user_id: str = Header(),
    use_case: SubmitEquipmentReadingUseCase = Depends(get_submit_equipment_reading_use_case),
) -> EquipmentParameterReadingSubmitRead:
    try:
        return await use_case.execute(equipment_id, payload, x_user_id)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipment or parameter definition not found")


@router.get("/routes", response_model=list[RouteRead])
async def list_routes(
    use_case: ListRoutesUseCase = Depends(get_list_routes_use_case),
) -> list[RouteRead]:
    return await use_case.execute()


@router.get("/routes/{route_id}", response_model=RouteRead)
async def get_route(
    route_id: str,
    use_case: GetRouteUseCase = Depends(get_get_route_use_case),
) -> RouteRead:
    try:
        return await use_case.execute(route_id)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")


@router.get("/rounds/my", response_model=list[RoundRead])
async def list_my_rounds(
    x_user_id: str = Header(),
    use_case: ListMyRoundsUseCase = Depends(get_list_my_rounds_use_case),
) -> list[RoundRead]:
    return await use_case.execute(x_user_id)


@router.get("/tasks/my", response_model=list[TaskSummaryRead])
async def list_my_tasks(
    x_user_id: str = Header(),
    x_user_role: str = Header(),
    use_case: ListTasksUseCase = Depends(get_list_tasks_use_case),
) -> list[TaskSummaryRead]:
    return await use_case.execute(x_user_id, x_user_role)


@router.get("/tasks/{round_id}", response_model=TaskDetailRead)
async def get_task(
    round_id: str,
    x_user_id: str = Header(),
    x_user_role: str = Header(),
    use_case: GetTaskDetailUseCase = Depends(get_get_task_detail_use_case),
) -> TaskDetailRead:
    try:
        return await use_case.execute(round_id, x_user_id, x_user_role)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Task is not assigned to current worker")


@router.post("/tasks/{round_id}/start", response_model=RoundRead)
async def start_round(
    round_id: str,
    x_user_id: str = Header(),
    x_user_role: str = Header(),
    use_case: StartRoundUseCase = Depends(get_start_round_use_case),
) -> RoundRead:
    try:
        return await use_case.execute(round_id, x_user_id, x_user_role)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Task is not assigned to current worker")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post("/tasks/{round_id}/finish", response_model=RoundRead)
async def finish_round(
    round_id: str,
    x_user_id: str = Header(),
    x_user_role: str = Header(),
    use_case: FinishRoundUseCase = Depends(get_finish_round_use_case),
) -> RoundRead:
    try:
        return await use_case.execute(round_id, x_user_id, x_user_role)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Task is not assigned to current worker")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get("/checklists/templates", response_model=list[ChecklistTemplateRead])
async def list_checklist_templates(
    use_case: ListChecklistTemplatesUseCase = Depends(get_list_checklist_templates_use_case),
) -> list[ChecklistTemplateRead]:
    return await use_case.execute()


@router.get("/checklists/templates/{template_id}", response_model=ChecklistTemplateRead)
async def get_checklist_template(
    template_id: str,
    use_case: GetChecklistTemplateUseCase = Depends(get_get_checklist_template_use_case),
) -> ChecklistTemplateRead:
    try:
        return await use_case.execute(template_id)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checklist template not found")


@router.post(
    "/checklists/{checklist_instance_id}/items/{item_template_id}/result",
    response_model=ChecklistItemResultSubmitRead,
)
async def submit_checklist_item_result(
    checklist_instance_id: str,
    item_template_id: str,
    payload: ChecklistItemResultCreate,
    x_user_id: str = Header(),
    x_user_role: str = Header(),
    use_case: SubmitChecklistItemResultUseCase = Depends(get_submit_checklist_item_result_use_case),
) -> ChecklistItemResultSubmitRead:
    try:
        return await use_case.execute(checklist_instance_id, item_template_id, payload, x_user_id, x_user_role)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checklist item not found")
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Checklist is not assigned to current worker")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
