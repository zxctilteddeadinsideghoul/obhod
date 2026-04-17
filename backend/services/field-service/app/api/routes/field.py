from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.containers import Container
from app.schemas import ChecklistTemplateRead, EquipmentRead, RouteRead, RoundRead
from app.services import FieldService


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
@inject
async def seed_demo(
    x_user_role: str | None = Header(default=None),
    service: FieldService = Depends(Provide[Container.field_service]),
) -> dict[str, str]:
    if x_user_role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return await service.seed_demo_data()


@router.get("/equipment", response_model=list[EquipmentRead])
@inject
async def list_equipment(
    service: FieldService = Depends(Provide[Container.field_service]),
) -> list[EquipmentRead]:
    return await service.list_equipment()


@router.get("/equipment/{equipment_id}", response_model=EquipmentRead)
@inject
async def get_equipment(
    equipment_id: str,
    service: FieldService = Depends(Provide[Container.field_service]),
) -> EquipmentRead:
    try:
        return await service.get_equipment(equipment_id)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipment not found")


@router.get("/routes", response_model=list[RouteRead])
@inject
async def list_routes(
    service: FieldService = Depends(Provide[Container.field_service]),
) -> list[RouteRead]:
    return await service.list_routes()


@router.get("/routes/{route_id}", response_model=RouteRead)
@inject
async def get_route(
    route_id: str,
    service: FieldService = Depends(Provide[Container.field_service]),
) -> RouteRead:
    try:
        return await service.get_route(route_id)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")


@router.get("/rounds/my", response_model=list[RoundRead])
@inject
async def list_my_rounds(
    x_user_id: str = Header(),
    service: FieldService = Depends(Provide[Container.field_service]),
) -> list[RoundRead]:
    return await service.list_my_rounds(x_user_id)


@router.get("/checklists/templates", response_model=list[ChecklistTemplateRead])
@inject
async def list_checklist_templates(
    service: FieldService = Depends(Provide[Container.field_service]),
) -> list[ChecklistTemplateRead]:
    return await service.list_checklist_templates()


@router.get("/checklists/templates/{template_id}", response_model=ChecklistTemplateRead)
@inject
async def get_checklist_template(
    template_id: str,
    service: FieldService = Depends(Provide[Container.field_service]),
) -> ChecklistTemplateRead:
    try:
        return await service.get_checklist_template(template_id)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checklist template not found")
