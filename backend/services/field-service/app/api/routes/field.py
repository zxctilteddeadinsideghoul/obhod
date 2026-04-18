import json

from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, Query, UploadFile, status
from fastapi.responses import Response

from app.api.dependencies import (
    get_confirm_route_step_use_case,
    get_create_checklist_template_use_case,
    get_create_equipment_use_case,
    get_create_round_use_case,
    get_create_route_use_case,
    get_download_attachment_use_case,
    get_get_checklist_template_use_case,
    get_get_equipment_use_case,
    get_get_route_use_case,
    get_get_task_detail_use_case,
    get_finish_round_use_case,
    get_get_defect_use_case,
    get_list_attachments_use_case,
    get_list_checklist_templates_use_case,
    get_list_defects_use_case,
    get_list_equipment_use_case,
    get_list_my_rounds_use_case,
    get_list_routes_use_case,
    get_list_tasks_use_case,
    get_seed_demo_data_use_case,
    get_start_round_use_case,
    get_submit_checklist_item_result_use_case,
    get_submit_equipment_reading_use_case,
    get_upload_attachment_use_case,
    get_update_defect_severity_use_case,
    get_update_defect_status_use_case,
)
from app.schemas import (
    AttachmentRead,
    ChecklistTemplateCreate,
    ChecklistItemResultCreate,
    ChecklistItemResultSubmitRead,
    ChecklistTemplateRead,
    DefectRead,
    DefectSeverityUpdate,
    DefectStatusUpdate,
    EquipmentCreate,
    EquipmentParameterReadingCreate,
    EquipmentParameterReadingSubmitRead,
    EquipmentRead,
    RoundCreate,
    RouteCreate,
    RouteRead,
    RouteStepConfirmCreate,
    RouteStepConfirmRead,
    RoundRead,
    TaskDetailRead,
    TaskSummaryRead,
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
    ListDefectsUseCase,
    ListEquipmentUseCase,
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
    include_rounds: bool = Query(default=True),
    x_user_role: str | None = Header(default=None),
    use_case: SeedDemoDataUseCase = Depends(get_seed_demo_data_use_case),
) -> dict[str, str | bool]:
    if x_user_role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return await use_case.execute(include_rounds=include_rounds)


@router.post("/admin/equipment", response_model=EquipmentRead, status_code=status.HTTP_201_CREATED)
async def create_equipment(
    payload: EquipmentCreate,
    x_user_id: str = Header(),
    x_user_role: str = Header(),
    use_case: CreateEquipmentUseCase = Depends(get_create_equipment_use_case),
) -> EquipmentRead:
    try:
        return await use_case.execute(payload, x_user_id, x_user_role)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post("/admin/checklists/templates", response_model=ChecklistTemplateRead, status_code=status.HTTP_201_CREATED)
async def create_checklist_template(
    payload: ChecklistTemplateCreate,
    x_user_id: str = Header(),
    x_user_role: str = Header(),
    use_case: CreateChecklistTemplateUseCase = Depends(get_create_checklist_template_use_case),
) -> ChecklistTemplateRead:
    try:
        return await use_case.execute(payload, x_user_id, x_user_role)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post("/admin/routes", response_model=RouteRead, status_code=status.HTTP_201_CREATED)
async def create_route(
    payload: RouteCreate,
    x_user_id: str = Header(),
    x_user_role: str = Header(),
    use_case: CreateRouteUseCase = Depends(get_create_route_use_case),
) -> RouteRead:
    try:
        return await use_case.execute(payload, x_user_id, x_user_role)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipment not found")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post("/admin/rounds", response_model=RoundRead, status_code=status.HTTP_201_CREATED)
async def create_round(
    payload: RoundCreate,
    x_user_id: str = Header(),
    x_user_role: str = Header(),
    use_case: CreateRoundUseCase = Depends(get_create_round_use_case),
) -> RoundRead:
    try:
        return await use_case.execute(payload, x_user_id, x_user_role)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route, checklist template or employee not found")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post("/attachments", response_model=AttachmentRead, status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    entity_type: str = Form(),
    entity_id: str = Form(),
    file: UploadFile = File(),
    payload_json: str = Form(default="{}"),
    x_user_id: str = Header(),
    x_user_role: str = Header(),
    use_case: UploadAttachmentUseCase = Depends(get_upload_attachment_use_case),
) -> AttachmentRead:
    try:
        payload = json.loads(payload_json)
        if not isinstance(payload, dict):
            raise ValueError("payload_json must be an object")
        return await use_case.execute(entity_type, entity_id, file, payload, x_user_id, x_user_role)
    except json.JSONDecodeError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid payload_json")
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment target not found")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get("/attachments", response_model=list[AttachmentRead])
async def list_attachments(
    entity_type: str,
    entity_id: str,
    x_user_id: str = Header(),
    x_user_role: str = Header(),
    use_case: ListAttachmentsUseCase = Depends(get_list_attachments_use_case),
) -> list[AttachmentRead]:
    try:
        return await use_case.execute(entity_type, entity_id, x_user_id, x_user_role)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment target not found")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get("/attachments/{attachment_id}/download")
async def download_attachment(
    attachment_id: str,
    x_user_id: str = Header(),
    x_user_role: str = Header(),
    use_case: DownloadAttachmentUseCase = Depends(get_download_attachment_use_case),
) -> Response:
    try:
        content, file_name, mime_type = await use_case.execute(attachment_id, x_user_id, x_user_role)
        return Response(
            content=content,
            media_type=mime_type,
            headers={"Content-Disposition": f'inline; filename="{file_name}"'},
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")


@router.get("/defects", response_model=list[DefectRead])
async def list_defects(
    x_user_role: str = Header(),
    defect_status: str | None = Query(default=None, alias="status"),
    severity: str | None = None,
    equipment_id: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    use_case: ListDefectsUseCase = Depends(get_list_defects_use_case),
) -> list[DefectRead]:
    try:
        return await use_case.execute(
            user_role=x_user_role,
            status=defect_status,
            severity=severity,
            equipment_id=equipment_id,
            limit=limit,
            offset=offset,
        )
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")


@router.get("/defects/{defect_id}", response_model=DefectRead)
async def get_defect(
    defect_id: str,
    x_user_role: str = Header(),
    use_case: GetDefectUseCase = Depends(get_get_defect_use_case),
) -> DefectRead:
    try:
        return await use_case.execute(defect_id, x_user_role)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Defect not found")


@router.patch("/defects/{defect_id}/status", response_model=DefectRead)
async def update_defect_status(
    defect_id: str,
    payload: DefectStatusUpdate,
    x_user_id: str = Header(),
    x_user_role: str = Header(),
    use_case: UpdateDefectStatusUseCase = Depends(get_update_defect_status_use_case),
) -> DefectRead:
    try:
        return await use_case.execute(defect_id, payload, x_user_id, x_user_role)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Defect not found")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.patch("/defects/{defect_id}/severity", response_model=DefectRead)
async def update_defect_severity(
    defect_id: str,
    payload: DefectSeverityUpdate,
    x_user_id: str = Header(),
    x_user_role: str = Header(),
    use_case: UpdateDefectSeverityUseCase = Depends(get_update_defect_severity_use_case),
) -> DefectRead:
    try:
        return await use_case.execute(defect_id, payload, x_user_id, x_user_role)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Defect not found")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


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
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


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


@router.post("/tasks/{round_id}/steps/{route_step_id}/confirm", response_model=RouteStepConfirmRead)
async def confirm_route_step(
    round_id: str,
    route_step_id: str,
    payload: RouteStepConfirmCreate,
    x_user_id: str = Header(),
    x_user_role: str = Header(),
    use_case: ConfirmRouteStepUseCase = Depends(get_confirm_route_step_use_case),
) -> RouteStepConfirmRead:
    try:
        return await use_case.execute(round_id, route_step_id, payload, x_user_id, x_user_role)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task or route step not found")
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
