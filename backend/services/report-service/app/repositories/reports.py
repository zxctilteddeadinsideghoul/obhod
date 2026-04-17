from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.schemas import (
    ChecklistResultRead,
    CurrentUserRead,
    DefectRead,
    EmployeeAnalyticsItem,
    EquipmentAnalyticsItem,
    EquipmentReadingRead,
    HealthRead,
    ReportsSummary,
    RoundReportDetail,
    RoundReportListItem,
)


ROUND_REPORT_SELECT = """
with mandatory_steps as (
    select route_template_id, count(*)::int as mandatory_steps_total
    from field_route_step
    where mandatory_flag = true
    group by route_template_id
),
confirmed_steps as (
    select round_instance_id, count(distinct route_step_id)::int as confirmed_steps_count
    from field_route_step_visit
    where status = 'confirmed'
    group by round_instance_id
),
required_items as (
    select ci.round_instance_id, count(cit.id)::int as required_items_total
    from field_checklist_instance ci
    join field_checklist_item_template cit on cit.checklist_template_id = ci.checklist_template_id
    where cit.required_flag = true
    group by ci.round_instance_id
),
completed_items as (
    select ci.round_instance_id, count(distinct cir.item_template_id)::int as completed_items_count
    from field_checklist_item_result cir
    join field_checklist_instance ci on ci.id = cir.checklist_instance_id
    group by ci.round_instance_id
),
result_statuses as (
    select
        ci.round_instance_id,
        count(*) filter (where cir.status = 'warning')::int as warning_count,
        count(*) filter (where cir.status = 'critical')::int as critical_count
    from field_checklist_item_result cir
    join field_checklist_instance ci on ci.id = cir.checklist_instance_id
    group by ci.round_instance_id
),
defects as (
    select source_checklist_id, count(*)::int as defects_count
    from field_defect
    group by source_checklist_id
)
select
    ri.id,
    ri.status,
    rt.id as route_id,
    rt.name as route_name,
    e.id as employee_id,
    e.full_name as employee_name,
    ri.planned_start,
    ri.planned_end,
    ri.actual_start,
    ri.actual_end,
    coalesce(ms.mandatory_steps_total, 0) as mandatory_steps_total,
    coalesce(cs.confirmed_steps_count, 0) as confirmed_steps_count,
    coalesce(req.required_items_total, 0) as required_items_total,
    coalesce(done.completed_items_count, 0) as completed_items_count,
    coalesce(rs.warning_count, 0) as warning_count,
    coalesce(rs.critical_count, 0) as critical_count,
    coalesce(sum(coalesce(d.defects_count, 0)), 0)::int as defects_count,
    case
        when coalesce(ms.mandatory_steps_total, 0) = 0 then 0
        else least(100, round(coalesce(cs.confirmed_steps_count, 0)::numeric * 100 / ms.mandatory_steps_total)::int)
    end as completion_pct
from field_round_instance ri
join field_route_template rt on rt.id = ri.route_template_id
join field_employee e on e.id = ri.employee_id
left join mandatory_steps ms on ms.route_template_id = ri.route_template_id
left join confirmed_steps cs on cs.round_instance_id = ri.id
left join required_items req on req.round_instance_id = ri.id
left join completed_items done on done.round_instance_id = ri.id
left join result_statuses rs on rs.round_instance_id = ri.id
left join field_checklist_instance ci on ci.round_instance_id = ri.id
left join defects d on d.source_checklist_id = ci.id
"""

ROUND_REPORT_GROUP_BY = """
group by
    ri.id,
    rt.id,
    rt.name,
    e.id,
    e.full_name,
    ms.mandatory_steps_total,
    cs.confirmed_steps_count,
    req.required_items_total,
    done.completed_items_count,
    rs.warning_count,
    rs.critical_count
"""


class ReportsRepository:
    def __init__(self, settings: Settings, session: AsyncSession) -> None:
        self.settings = settings
        self.session = session

    async def get_health(self) -> HealthRead:
        return HealthRead(service=self.settings.service_name, status="ok")

    async def get_current_user(
        self,
        user_id: str | None,
        user_role: str | None,
        user_name: str | None,
    ) -> CurrentUserRead:
        return CurrentUserRead(
            service=self.settings.service_name,
            user_id=user_id,
            user_role=user_role,
            user_name=user_name,
        )

    async def list_round_reports(
        self,
        status: str | None = None,
        employee_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[RoundReportListItem]:
        filters = []
        params: dict[str, object] = {"limit": limit, "offset": offset}
        if status is not None:
            filters.append("ri.status = :status")
            params["status"] = status
        if employee_id is not None:
            filters.append("ri.employee_id = :employee_id")
            params["employee_id"] = employee_id

        where_clause = f"where {' and '.join(filters)}" if filters else ""
        query = text(
            f"""
            {ROUND_REPORT_SELECT}
            {where_clause}
            {ROUND_REPORT_GROUP_BY}
            order by ri.planned_start desc
            limit :limit offset :offset
            """
        )
        result = await self.session.execute(query, params)
        return [RoundReportListItem(**dict(row)) for row in result.mappings().all()]

    async def get_round_report(self, round_id: str) -> RoundReportDetail | None:
        round_query = text(
            f"""
            {ROUND_REPORT_SELECT}
            where ri.id = :round_id
            {ROUND_REPORT_GROUP_BY}
            """
        )
        round_result = await self.session.execute(round_query, {"round_id": round_id})
        round_row = round_result.mappings().one_or_none()
        if round_row is None:
            return None

        results = await self.session.execute(
            text(
                """
                select
                    cir.item_template_id,
                    cit.question,
                    cir.equipment_id,
                    eq.name as equipment_name,
                    cir.route_step_id,
                    cir.result_code,
                    cir.result_value,
                    cir.comment,
                    cir.status
                from field_checklist_item_result cir
                join field_checklist_instance ci on ci.id = cir.checklist_instance_id
                join field_checklist_item_template cit on cit.id = cir.item_template_id
                left join field_equipment eq on eq.id = cir.equipment_id
                where ci.round_instance_id = :round_id
                order by cit.seq_no
                """
            ),
            {"round_id": round_id},
        )
        readings = await self.session.execute(
            text(
                """
                select
                    r.id,
                    r.equipment_id,
                    eq.name as equipment_name,
                    pd.name as parameter_name,
                    pd.unit,
                    r.reading_ts,
                    r.value_num,
                    r.value_text,
                    r.source,
                    r.within_limits
                from field_equipment_parameter_reading r
                join field_equipment eq on eq.id = r.equipment_id
                join field_equipment_parameter_def pd on pd.id = r.parameter_def_id
                join field_route_step rs on rs.id = r.route_step_id
                join field_round_instance ri on ri.route_template_id = rs.route_template_id
                where ri.id = :round_id
                order by r.reading_ts, eq.name, pd.name
                """
            ),
            {"round_id": round_id},
        )
        defects = await self.session.execute(
            text(
                """
                select
                    d.id,
                    d.equipment_id,
                    eq.name as equipment_name,
                    d.detected_at,
                    d.title,
                    d.description,
                    d.severity,
                    d.status
                from field_defect d
                join field_equipment eq on eq.id = d.equipment_id
                left join field_checklist_instance ci on ci.id = d.source_checklist_id
                where ci.round_instance_id = :round_id
                order by d.detected_at desc
                """
            ),
            {"round_id": round_id},
        )

        return RoundReportDetail(
            round=RoundReportListItem(**dict(round_row)),
            checklist_results=[ChecklistResultRead(**dict(row)) for row in results.mappings().all()],
            readings=[EquipmentReadingRead(**dict(row)) for row in readings.mappings().all()],
            defects=[DefectRead(**dict(row)) for row in defects.mappings().all()],
        )

    async def get_summary(self) -> ReportsSummary:
        result = await self.session.execute(
            text(
                """
                with round_stats as (
                    select
                        count(*)::int as rounds_total,
                        count(*) filter (where status = 'planned')::int as rounds_planned,
                        count(*) filter (where status = 'in_progress')::int as rounds_in_progress,
                        count(*) filter (where status = 'completed')::int as rounds_completed
                    from field_round_instance
                ),
                issue_stats as (
                    select
                        count(*) filter (where status = 'warning')::int as warning_count,
                        count(*) filter (where status = 'critical')::int as critical_count
                    from field_checklist_item_result
                ),
                defect_stats as (
                    select count(*) filter (where status not in ('closed', 'resolved'))::int as defects_open
                    from field_defect
                ),
                completion_stats as (
                    select coalesce(avg(ci.completion_pct), 0)::float as avg_completion_pct
                    from field_checklist_instance ci
                )
                select *
                from round_stats, issue_stats, defect_stats, completion_stats
                """
            )
        )
        return ReportsSummary(**dict(result.mappings().one()))

    async def get_equipment_analytics(self, limit: int = 20) -> list[EquipmentAnalyticsItem]:
        result = await self.session.execute(
            text(
                """
                select
                    eq.id as equipment_id,
                    eq.name as equipment_name,
                    eq.location,
                    count(distinct d.id)::int as defects_count,
                    count(distinct cir.id) filter (where cir.status = 'warning')::int as warning_count,
                    count(distinct cir.id) filter (where cir.status = 'critical')::int as critical_count,
                    max(r.reading_ts) as last_reading_at
                from field_equipment eq
                left join field_defect d on d.equipment_id = eq.id
                left join field_checklist_item_result cir on cir.equipment_id = eq.id
                left join field_equipment_parameter_reading r on r.equipment_id = eq.id
                group by eq.id, eq.name, eq.location
                order by critical_count desc, defects_count desc, warning_count desc, eq.name
                limit :limit
                """
            ),
            {"limit": limit},
        )
        return [EquipmentAnalyticsItem(**dict(row)) for row in result.mappings().all()]

    async def get_employee_analytics(self, limit: int = 20) -> list[EmployeeAnalyticsItem]:
        result = await self.session.execute(
            text(
                """
                select
                    e.id as employee_id,
                    e.full_name as employee_name,
                    count(distinct ri.id)::int as rounds_total,
                    count(distinct ri.id) filter (where ri.status = 'completed')::int as rounds_completed,
                    count(distinct rsv.route_step_id)::int as confirmed_steps_count,
                    avg(extract(epoch from (ri.actual_end - ri.actual_start)) / 60)
                        filter (where ri.actual_start is not null and ri.actual_end is not null)::float as avg_duration_min,
                    count(distinct cir.id) filter (where cir.status = 'warning')::int as warning_count,
                    count(distinct cir.id) filter (where cir.status = 'critical')::int as critical_count
                from field_employee e
                left join field_round_instance ri on ri.employee_id = e.id
                left join field_route_step_visit rsv on rsv.round_instance_id = ri.id
                left join field_checklist_instance ci on ci.round_instance_id = ri.id
                left join field_checklist_item_result cir on cir.checklist_instance_id = ci.id
                group by e.id, e.full_name
                order by rounds_completed desc, confirmed_steps_count desc, e.full_name
                limit :limit
                """
            ),
            {"limit": limit},
        )
        return [EmployeeAnalyticsItem(**dict(row)) for row in result.mappings().all()]
