from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    ChecklistInstance,
    ChecklistItemTemplate,
    ChecklistTemplate,
    Employee,
    Equipment,
    EquipmentParameterDef,
    RouteStep,
    RouteTemplate,
    RoundInstance,
    Shift,
)


class DemoDataRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def seed(self) -> None:
        now = datetime.now(timezone.utc)
        await self._merge_all(
            [
                *self._equipment(),
                *self._parameter_defs(),
                *self._employees(),
                self._shift(now),
                *self._routes(),
                *self._route_steps(),
                *self._checklist_templates(),
                *self._checklist_items(),
                *self._rounds(now),
                *self._checklist_instances(),
            ]
        )
        await self.session.commit()

    async def _merge_all(self, objects: list[object]) -> None:
        for item in objects:
            await self.session.merge(item)

    def _equipment(self) -> list[Equipment]:
        return [
            Equipment(
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
            ),
            Equipment(
                id="EQ-PUMP-0201",
                org_id="ORG-01",
                code="000000113",
                name="Насос циркуляционный НЦ-0201",
                tech_no="NC0201",
                passport_no="PS-0201-2020",
                serial_no="SN-554201",
                type_id="pump",
                location_id="LOC-UKPG",
                location="АНГКМ / ЦПТГ / Насосная",
                state_id="in_operation",
                qr_tag="QR:EQ-PUMP-0201",
                nfc_tag="NFC:04AABB22DD",
                passport_json={
                    "productionDate": "2020-03-18",
                    "passportNo": "PS-0201-2020",
                    "serialNo": "SN-554201",
                    "techNo": "NC0201",
                },
                snapshot_json={
                    "serviceNorms": [{"kind": "inspection", "periodicity": "shift"}],
                    "tags": {"qr": "QR:EQ-PUMP-0201", "nfc": "NFC:04AABB22DD"},
                },
            ),
            Equipment(
                id="EQ-TRANS-1001",
                org_id="ORG-01",
                code="000000207",
                name="Трансформатор силовой ТМ-1001",
                tech_no="TM1001",
                passport_no="PS-1001-2019",
                serial_no="SN-991001",
                type_id="transformer",
                location_id="LOC-SUBSTATION",
                location="АНГКМ / Подстанция 6 кВ",
                state_id="in_operation",
                qr_tag="QR:EQ-TRANS-1001",
                nfc_tag="NFC:04AABB33EE",
                passport_json={
                    "productionDate": "2019-10-04",
                    "passportNo": "PS-1001-2019",
                    "serialNo": "SN-991001",
                    "techNo": "TM1001",
                },
                snapshot_json={
                    "serviceNorms": [{"kind": "inspection", "periodicity": "day"}],
                    "tags": {"qr": "QR:EQ-TRANS-1001", "nfc": "NFC:04AABB33EE"},
                },
            ),
        ]

    def _parameter_defs(self) -> list[EquipmentParameterDef]:
        return [
            EquipmentParameterDef(
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
            ),
            EquipmentParameterDef(
                id="PARAM-COMPRESSOR-TEMP-BEARING",
                equipment_type_id="compressor",
                code="TEMP_BEARING",
                name="Температура подшипника компрессора",
                unit="C",
                data_type="number",
                min_value=35,
                max_value=75,
                critical_min=25,
                critical_max=90,
            ),
            EquipmentParameterDef(
                id="PARAM-PUMP-VIBRATION",
                equipment_type_id="pump",
                code="VIBRATION",
                name="Вибрация насоса",
                unit="mm/s",
                data_type="number",
                min_value=0,
                max_value=4.5,
                critical_min=None,
                critical_max=7.1,
            ),
            EquipmentParameterDef(
                id="PARAM-TRANS-OIL-TEMP",
                equipment_type_id="transformer",
                code="OIL_TEMP",
                name="Температура масла трансформатора",
                unit="C",
                data_type="number",
                min_value=-20,
                max_value=80,
                critical_min=-35,
                critical_max=95,
            ),
        ]

    def _employees(self) -> list[Employee]:
        return [
            Employee(
                id="dev-worker",
                person_id="EMP-145",
                full_name="Development Worker",
                qualification_id="OPERATOR-TU",
                department_id="DEPT-UGP",
            ),
            Employee(
                id="dev-worker-2",
                person_id="EMP-146",
                full_name="Second Test Worker",
                qualification_id="OPERATOR-TU",
                department_id="DEPT-UGP",
            ),
            Employee(
                id="dev-admin",
                person_id="EMP-001",
                full_name="Development Admin",
                qualification_id="MASTER",
                department_id="DEPT-UGP",
            ),
        ]

    def _shift(self, now: datetime) -> Shift:
        return Shift(
            id="SHIFT-A-2026-04-17",
            org_id="ORG-01",
            shift_code="A",
            start_ts=now.replace(hour=8, minute=0, second=0, microsecond=0),
            end_ts=now.replace(hour=20, minute=0, second=0, microsecond=0),
            calendar_id="CAL-UGP",
        )

    def _routes(self) -> list[RouteTemplate]:
        return [
            RouteTemplate(
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
            ),
            RouteTemplate(
                id="ROUTE-ENERGY-SHIFT",
                org_id="ORG-01",
                department_id="DEPT-UGP",
                name="Сменный обход энергоцеха",
                route_type="inspection",
                location="АНГКМ / Энергоцех",
                duration_min=90,
                planning_rule="each_shift",
                qualification_id="OPERATOR-TU",
                version="1",
                snapshot_json={
                    "id": "ROUTE-ENERGY-SHIFT",
                    "name": "Сменный обход энергоцеха",
                    "orgId": "ORG-01",
                    "durationMin": 90,
                    "planningRule": "each_shift",
                    "version": "1",
                },
            ),
        ]

    def _route_steps(self) -> list[RouteStep]:
        return [
            RouteStep(
                id="ROUTE-KC0103-STEP-1",
                route_template_id="ROUTE-KC0103",
                seq_no=1,
                equipment_id="EQ-KC0103",
                checkpoint_id="PI-2",
                mandatory_flag=True,
                confirm_by="nfc",
            ),
            RouteStep(
                id="ROUTE-ENERGY-SHIFT-STEP-1",
                route_template_id="ROUTE-ENERGY-SHIFT",
                seq_no=1,
                equipment_id="EQ-KC0103",
                checkpoint_id="CP-COMPRESSOR",
                mandatory_flag=True,
                confirm_by="qr",
            ),
            RouteStep(
                id="ROUTE-ENERGY-SHIFT-STEP-2",
                route_template_id="ROUTE-ENERGY-SHIFT",
                seq_no=2,
                equipment_id="EQ-PUMP-0201",
                checkpoint_id="CP-PUMP",
                mandatory_flag=True,
                confirm_by="qr",
            ),
            RouteStep(
                id="ROUTE-ENERGY-SHIFT-STEP-3",
                route_template_id="ROUTE-ENERGY-SHIFT",
                seq_no=3,
                equipment_id="EQ-TRANS-1001",
                checkpoint_id="CP-TRANSFORMER",
                mandatory_flag=True,
                confirm_by="qr",
            ),
        ]

    def _checklist_templates(self) -> list[ChecklistTemplate]:
        return [
            ChecklistTemplate(
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
            ),
            ChecklistTemplate(
                id="TPL-ENERGY-SHIFT-01",
                org_id="ORG-01",
                name="Сменная форма осмотра оборудования энергоцеха",
                scope="round",
                equipment_type_id=None,
                version="1",
                snapshot_json={
                    "schemaVersion": "1.0.0",
                    "answerTypes": ["bool", "number", "text", "photo"],
                },
            ),
        ]

    def _checklist_items(self) -> list[ChecklistItemTemplate]:
        return [
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
            ChecklistItemTemplate(
                id="TPL-ENERGY-SHIFT-01-ITEM-1",
                checklist_template_id="TPL-ENERGY-SHIFT-01",
                seq_no=1,
                question="Визуальное состояние оборудования без замечаний",
                answer_type="bool",
                required_flag=True,
            ),
            ChecklistItemTemplate(
                id="TPL-ENERGY-SHIFT-01-ITEM-2",
                checklist_template_id="TPL-ENERGY-SHIFT-01",
                seq_no=2,
                question="Отсутствуют посторонние шумы, запахи, течи",
                answer_type="bool",
                required_flag=True,
            ),
            ChecklistItemTemplate(
                id="TPL-ENERGY-SHIFT-01-ITEM-3",
                checklist_template_id="TPL-ENERGY-SHIFT-01",
                seq_no=3,
                question="Контрольное показание параметра оборудования",
                answer_type="number",
                required_flag=True,
            ),
            ChecklistItemTemplate(
                id="TPL-ENERGY-SHIFT-01-ITEM-4",
                checklist_template_id="TPL-ENERGY-SHIFT-01",
                seq_no=4,
                question="Комментарий обходчика",
                answer_type="text",
                required_flag=False,
            ),
        ]

    def _rounds(self, now: datetime) -> list[RoundInstance]:
        return [
            RoundInstance(
                id="ROUND-2026-04-17-000123",
                org_id="ORG-01",
                route_template_id="ROUTE-KC0103",
                planned_start=now,
                planned_end=now + timedelta(hours=1),
                shift_id="SHIFT-A-2026-04-17",
                employee_id="dev-worker",
                status="planned",
                qualification_id="OPERATOR-TU",
                snapshot_json={"schemaVersion": "1.0.0"},
            ),
            RoundInstance(
                id="ROUND-2026-04-17-000200",
                org_id="ORG-01",
                route_template_id="ROUTE-ENERGY-SHIFT",
                planned_start=now + timedelta(minutes=15),
                planned_end=now + timedelta(hours=2),
                shift_id="SHIFT-A-2026-04-17",
                employee_id="dev-worker",
                status="planned",
                qualification_id="OPERATOR-TU",
                snapshot_json={"schemaVersion": "1.0.0", "priority": "normal"},
            ),
            RoundInstance(
                id="ROUND-2026-04-17-000201",
                org_id="ORG-01",
                route_template_id="ROUTE-ENERGY-SHIFT",
                planned_start=now + timedelta(hours=3),
                planned_end=now + timedelta(hours=4, minutes=30),
                shift_id="SHIFT-A-2026-04-17",
                employee_id="dev-worker-2",
                status="planned",
                qualification_id="OPERATOR-TU",
                snapshot_json={"schemaVersion": "1.0.0", "priority": "low"},
            ),
        ]

    def _checklist_instances(self) -> list[ChecklistInstance]:
        return [
            ChecklistInstance(
                id="CL-2026-04-17-555",
                round_instance_id="ROUND-2026-04-17-000123",
                checklist_template_id="TPL-EVERYDAY-SAFETY-02",
                status="draft",
                completion_pct=0,
                snapshot_json={"entityRef": {"entityType": "round", "entityId": "ROUND-2026-04-17-000123"}},
            ),
            ChecklistInstance(
                id="CL-2026-04-17-700",
                round_instance_id="ROUND-2026-04-17-000200",
                checklist_template_id="TPL-ENERGY-SHIFT-01",
                status="draft",
                completion_pct=0,
                snapshot_json={"entityRef": {"entityType": "round", "entityId": "ROUND-2026-04-17-000200"}},
            ),
            ChecklistInstance(
                id="CL-2026-04-17-701",
                round_instance_id="ROUND-2026-04-17-000201",
                checklist_template_id="TPL-ENERGY-SHIFT-01",
                status="draft",
                completion_pct=0,
                snapshot_json={"entityRef": {"entityType": "round", "entityId": "ROUND-2026-04-17-000201"}},
            ),
        ]
