from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.containers import Container
from app.db import get_session
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


def get_container(request: Request) -> Container:
    return request.app.container  # type: ignore[attr-defined]


def get_health_use_case(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> GetHealthUseCase:
    return get_container(request).get_health_use_case(session)


def get_current_user_use_case(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> GetCurrentUserUseCase:
    return get_container(request).get_current_user_use_case(session)


def list_round_reports_use_case(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> ListRoundReportsUseCase:
    return get_container(request).list_round_reports_use_case(session)


def get_round_report_use_case(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> GetRoundReportUseCase:
    return get_container(request).get_round_report_use_case(session)


def get_reports_summary_use_case(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> GetReportsSummaryUseCase:
    return get_container(request).get_reports_summary_use_case(session)


def get_equipment_analytics_use_case(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> GetEquipmentAnalyticsUseCase:
    return get_container(request).get_equipment_analytics_use_case(session)


def get_employee_analytics_use_case(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> GetEmployeeAnalyticsUseCase:
    return get_container(request).get_employee_analytics_use_case(session)


def export_round_report_use_case(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> ExportRoundReportUseCase:
    return get_container(request).export_round_report_use_case(session)


def export_reports_analytics_use_case(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> ExportReportsAnalyticsUseCase:
    return get_container(request).export_reports_analytics_use_case(session)
