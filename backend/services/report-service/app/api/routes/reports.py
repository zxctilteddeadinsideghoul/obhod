from typing import Literal

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response, status

from app.api.dependencies import (
    export_reports_analytics_use_case,
    export_round_report_use_case,
    get_current_user_use_case,
    get_employee_analytics_use_case,
    get_equipment_analytics_use_case,
    get_health_use_case,
    get_reports_summary_use_case,
    get_round_report_use_case,
    list_round_reports_use_case,
)
from app.schemas import (
    CurrentUserRead,
    EmployeeAnalyticsItem,
    EquipmentAnalyticsItem,
    HealthRead,
    ReportsSummary,
    RoundReportDetail,
    RoundReportListItem,
)
from app.use_cases import (
    ExportReportsAnalyticsUseCase,
    ExportRoundReportUseCase,
    GetCurrentUserUseCase,
    GetEmployeeAnalyticsUseCase,
    GetEquipmentAnalyticsUseCase,
    GetHealthUseCase,
    GetReportsSummaryUseCase,
    GetRoundReportUseCase,
    ListRoundReportsUseCase,
)


router = APIRouter(prefix="/api/reports", tags=["reports"])


def require_admin(x_user_role: str | None) -> None:
    if x_user_role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can access reports",
        )


def export_response(content: bytes, media_type: str, file_name: str) -> Response:
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
    )


@router.get("/health", response_model=HealthRead)
async def health(
    use_case: GetHealthUseCase = Depends(get_health_use_case),
) -> HealthRead:
    return await use_case.execute()


@router.get("/whoami", response_model=CurrentUserRead)
async def whoami(
    x_user_id: str | None = Header(default=None),
    x_user_role: str | None = Header(default=None),
    x_user_name: str | None = Header(default=None),
    use_case: GetCurrentUserUseCase = Depends(get_current_user_use_case),
) -> CurrentUserRead:
    return await use_case.execute(x_user_id, x_user_role, x_user_name)


@router.get("/rounds", response_model=list[RoundReportListItem])
async def list_round_reports(
    x_user_role: str | None = Header(default=None),
    report_status: str | None = Query(default=None, alias="status"),
    employee_id: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    use_case: ListRoundReportsUseCase = Depends(list_round_reports_use_case),
) -> list[RoundReportListItem]:
    require_admin(x_user_role)
    return await use_case.execute(
        status=report_status,
        employee_id=employee_id,
        limit=limit,
        offset=offset,
    )


@router.get("/rounds/{round_id}", response_model=RoundReportDetail)
async def get_round_report(
    round_id: str,
    x_user_role: str | None = Header(default=None),
    use_case: GetRoundReportUseCase = Depends(get_round_report_use_case),
) -> RoundReportDetail:
    require_admin(x_user_role)
    report = await use_case.execute(round_id)
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Round report not found")
    return report


@router.get("/rounds/{round_id}/export")
async def export_round_report(
    round_id: str,
    x_user_role: str | None = Header(default=None),
    export_format: Literal["csv", "json"] = Query(default="csv", alias="format"),
    use_case: ExportRoundReportUseCase = Depends(export_round_report_use_case),
) -> Response:
    require_admin(x_user_role)
    export_file = await use_case.execute(round_id=round_id, export_format=export_format)
    if export_file is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Round report not found")
    return export_response(
        content=export_file.content,
        media_type=export_file.media_type,
        file_name=export_file.file_name,
    )


@router.get("/analytics/summary", response_model=ReportsSummary)
async def get_reports_summary(
    x_user_role: str | None = Header(default=None),
    use_case: GetReportsSummaryUseCase = Depends(get_reports_summary_use_case),
) -> ReportsSummary:
    require_admin(x_user_role)
    return await use_case.execute()


@router.get("/analytics/equipment", response_model=list[EquipmentAnalyticsItem])
async def get_equipment_analytics(
    x_user_role: str | None = Header(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    use_case: GetEquipmentAnalyticsUseCase = Depends(get_equipment_analytics_use_case),
) -> list[EquipmentAnalyticsItem]:
    require_admin(x_user_role)
    return await use_case.execute(limit=limit)


@router.get("/analytics/employees", response_model=list[EmployeeAnalyticsItem])
async def get_employee_analytics(
    x_user_role: str | None = Header(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    use_case: GetEmployeeAnalyticsUseCase = Depends(get_employee_analytics_use_case),
) -> list[EmployeeAnalyticsItem]:
    require_admin(x_user_role)
    return await use_case.execute(limit=limit)


@router.get("/analytics/export")
async def export_reports_analytics(
    x_user_role: str | None = Header(default=None),
    export_format: Literal["csv", "json"] = Query(default="csv", alias="format"),
    limit: int = Query(default=20, ge=1, le=100),
    use_case: ExportReportsAnalyticsUseCase = Depends(export_reports_analytics_use_case),
) -> Response:
    require_admin(x_user_role)
    export_file = await use_case.execute(export_format=export_format, limit=limit)
    return export_response(
        content=export_file.content,
        media_type=export_file.media_type,
        file_name=export_file.file_name,
    )
