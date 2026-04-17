from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    ChecklistInstance,
    ChecklistItemTemplate,
    ChecklistTemplate,
    Employee,
    Equipment,
    EquipmentParameterDef,
    RouteTemplate,
    RoundInstance,
    Shift,
)
from app.models.field import RouteStep


class DemoDataRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def seed(self) -> None:
        existing = await self.session.get(Equipment, "EQ-KC0103")
        if existing is not None:
            return

        now = datetime.now(timezone.utc)
        equipment = Equipment(
            id="EQ-KC0103",
            org_id="ORG-01",
            code="000000029",
            name="Поршневая компрессорная установка КС-0103",
            tech_no="KC0103",
            passport_no="PS-0103-2018",
            serial_no="SN-778812",
            type_id="compressor",
            location_id="LOC-UKPG",
            location="АНГКМ / ЦПТГ / УКПГ",
            state_id="in_operation",
            qr_tag="QR:EQ-KC0103",
            nfc_tag="NFC:04AABB11CC",
            passport_json={
                "manufacturer": "не указано",
                "productionDate": "2018-05-12",
                "passportNo": "PS-0103-2018",
                "serialNo": "SN-778812",
                "techNo": "KC0103",
            },
            snapshot_json={
                "serviceNorms": [{"kind": "inspection", "periodicity": "3h"}],
                "tags": {"qr": "QR:EQ-KC0103", "nfc": "NFC:04AABB11CC"},
            },
        )
        parameter = EquipmentParameterDef(
            id="PARAM-COMPRESSOR-PRESSURE-OUT",
            equipment_type_id="compressor",
            code="PRESSURE_OUT",
            name="Давление на выходе компрессора",
            unit="MPa",
            data_type="number",
            min_value=1.4,
            max_value=1.6,
            critical_min=1.3,
            critical_max=1.7,
        )
        employee = Employee(
            id="dev-worker",
            person_id="EMP-145",
            full_name="Development Worker",
            qualification_id="OPERATOR-TU",
            department_id="DEPT-UGP",
        )
        shift = Shift(
            id="SHIFT-A-2026-04-17",
            org_id="ORG-01",
            shift_code="A",
            start_ts=now,
            end_ts=now,
            calendar_id="CAL-UGP",
        )
        route = RouteTemplate(
            id="ROUTE-KC0103",
            org_id="ORG-01",
            department_id="DEPT-UGP",
            name="КС0103",
            route_type="inspection",
            location="АНГКМ / ЦПТГ / УКПГ",
            duration_min=60,
            planning_rule="every_3_hours",
            qualification_id="OPERATOR-TU",
            version="3",
            snapshot_json={
                "id": "ROUTE-KC0103",
                "name": "КС0103",
                "orgId": "ORG-01",
                "durationMin": 60,
                "planningRule": "every_3_hours",
                "version": "3",
            },
        )
        route_step = RouteStep(
            id="ROUTE-KC0103-STEP-1",
            route_template_id="ROUTE-KC0103",
            seq_no=1,
            equipment_id="EQ-KC0103",
            checkpoint_id="PI-2",
            mandatory_flag=True,
            confirm_by="nfc",
        )
        checklist_template = ChecklistTemplate(
            id="TPL-EVERYDAY-SAFETY-02",
            org_id="ORG-01",
            name="Ежесменный осмотр компрессорной установки",
            scope="round",
            equipment_type_id="compressor",
            version="1",
            snapshot_json={
                "schemaVersion": "1.0.0",
                "answerTypes": ["bool", "enum", "number", "text", "photo"],
            },
        )
        checklist_items = [
            ChecklistItemTemplate(
                id="TPL-EVERYDAY-SAFETY-02-ITEM-1",
                checklist_template_id="TPL-EVERYDAY-SAFETY-02",
                seq_no=1,
                question="На оборудовании установлены защитные кожухи и блокировки",
                answer_type="bool",
                required_flag=True,
            ),
            ChecklistItemTemplate(
                id="TPL-EVERYDAY-SAFETY-02-ITEM-2",
                checklist_template_id="TPL-EVERYDAY-SAFETY-02",
                seq_no=2,
                question="Давление на выходе компрессора",
                answer_type="number",
                required_flag=True,
                norm_ref="PRESSURE_OUT",
            ),
        ]
        round_instance = RoundInstance(
            id="ROUND-2026-04-17-000123",
            org_id="ORG-01",
            route_template_id="ROUTE-KC0103",
            planned_start=now,
            planned_end=now,
            shift_id="SHIFT-A-2026-04-17",
            employee_id="dev-worker",
            status="planned",
            qualification_id="OPERATOR-TU",
            snapshot_json={"schemaVersion": "1.0.0"},
        )
        checklist_instance = ChecklistInstance(
            id="CL-2026-04-17-555",
            round_instance_id="ROUND-2026-04-17-000123",
            checklist_template_id="TPL-EVERYDAY-SAFETY-02",
            status="draft",
            completion_pct=0,
            snapshot_json={"entityRef": {"entityType": "round", "entityId": "ROUND-2026-04-17-000123"}},
        )

        self.session.add_all(
            [
                equipment,
                parameter,
                employee,
                shift,
                route,
                route_step,
                checklist_template,
                *checklist_items,
                round_instance,
                checklist_instance,
            ]
        )
        await self.session.commit()
