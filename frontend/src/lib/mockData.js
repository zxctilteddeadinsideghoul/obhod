const MOCK_DB_STORAGE_KEY = "obhod.mock-db";

const seedData = {
  equipment: [
    {
      id: "EQ-KC0103",
      code: "000000029",
      name: "Поршневая компрессорная установка КС-0103",
      type_id: "compressor",
      location: "АНГКМ / ЦПТГ / УКПГ",
      passport_no: "PS-0103-2018",
      serial_no: "SN-778812",
      tech_no: "KC0103",
      state_id: "in_operation",
      qr_tag: "QR:EQ-KC0103",
      nfc_tag: "NFC:04AABB11CC",
      passport_json: {
        manufacturer: "Арсенал Маш",
        production_date: "2018-05-12",
        service_class: "Критическое оборудование",
        pressure_stage: "II",
      },
      snapshot_json: {
        schema_version: "1.0.0",
        last_inspection_at: "2026-04-17T06:21:00+05:00",
        health_index: 92,
        tags: ["compressor", "gas", "route-critical"],
      },
      parameters: [
        {
          code: "PRESSURE_OUT",
          label: "Давление на выходе",
          unit: "MPa",
          min: 1.4,
          max: 1.6,
          critical_min: 1.3,
          critical_max: 1.7,
        },
      ],
    },
    {
      id: "EQ-PUMP-0201",
      code: "000000041",
      name: "Насос подпитки НП-0201",
      type_id: "pump",
      location: "АНГКМ / ЦПТГ / насосная",
      passport_no: "PS-0201-2019",
      serial_no: "SN-115901",
      tech_no: "NP0201",
      state_id: "warning",
      qr_tag: "QR:EQ-PUMP-0201",
      nfc_tag: "NFC:04CCDDEE01",
      passport_json: {
        manufacturer: "ПромНасос",
        production_date: "2019-02-17",
        power_kw: 45,
        reserve_line: true,
      },
      snapshot_json: {
        schema_version: "1.0.0",
        last_warning_at: "2026-04-16T14:10:00+05:00",
        vibration_alarm_count: 3,
      },
      parameters: [
        {
          code: "VIBRATION",
          label: "Вибрация",
          unit: "mm/s",
          min: 0,
          max: 4.5,
          critical_min: 0,
          critical_max: 6,
        },
      ],
    },
    {
      id: "EQ-VALVE-077",
      code: "000000077",
      name: "Запорная арматура ЗА-077",
      type_id: "valve",
      location: "АНГКМ / узел реагентов",
      passport_no: "PS-077-2017",
      serial_no: "SN-777003",
      tech_no: "ZA077",
      state_id: "in_operation",
      qr_tag: "QR:EQ-VALVE-077",
      nfc_tag: "NFC:04AA11DD77",
      passport_json: {
        manufacturer: "ТехАрм",
        production_date: "2017-11-08",
        diameter: "DN80",
      },
      snapshot_json: {
        schema_version: "1.0.0",
        seal_state: "stable",
      },
      parameters: [],
    },
    {
      id: "EQ-HE-3302",
      code: "000000112",
      name: "Теплообменник Т-3302",
      type_id: "heat_exchanger",
      location: "АНГКМ / блок подготовки газа",
      passport_no: "PS-3302-2020",
      serial_no: "SN-330255",
      tech_no: "T3302",
      state_id: "critical",
      qr_tag: "QR:EQ-HE-3302",
      nfc_tag: "NFC:04FF223302",
      passport_json: {
        manufacturer: "СеверТеплоМаш",
        production_date: "2020-09-21",
        material: "12Х18Н10Т",
      },
      snapshot_json: {
        schema_version: "1.0.0",
        corrosion_risk: "high",
        last_repair_order: "WO-2026-04-03-021",
      },
      parameters: [
        {
          code: "TEMP_OUT",
          label: "Температура на выходе",
          unit: "C",
          min: 72,
          max: 80,
          critical_min: 68,
          critical_max: 85,
        },
      ],
    },
  ],
  routes: [
    {
      id: "ROUTE-KC0103",
      name: "КС0103",
      org_id: "ORG-01",
      department_id: "DEPT-UGP",
      qualification_id: "OPERATOR-TU",
      location: "АНГКМ / ЦПТГ / УКПГ",
      duration_min: 60,
      planning_rule: "every_3_hours",
      version: "3",
      is_active: true,
      steps: [
        {
          id: "STEP-KC0103-1",
          seq_no: 1,
          equipment_id: "EQ-KC0103",
          checkpoint_id: "PI-2",
          mandatory_flag: true,
          confirm_by: "nfc",
        },
        {
          id: "STEP-KC0103-2",
          seq_no: 2,
          equipment_id: "EQ-PUMP-0201",
          checkpoint_id: "VI-1",
          mandatory_flag: true,
          confirm_by: "qr",
        },
      ],
    },
    {
      id: "ROUTE-REAGENT",
      name: "Узел реагентов",
      org_id: "ORG-01",
      department_id: "DEPT-CHEM",
      qualification_id: "OPERATOR-CHEM",
      location: "АНГКМ / узел реагентов",
      duration_min: 35,
      planning_rule: "every_shift",
      version: "2",
      is_active: true,
      steps: [
        {
          id: "STEP-REAGENT-1",
          seq_no: 1,
          equipment_id: "EQ-VALVE-077",
          checkpoint_id: "VA-4",
          mandatory_flag: true,
          confirm_by: "manual",
        },
        {
          id: "STEP-REAGENT-2",
          seq_no: 2,
          equipment_id: "EQ-HE-3302",
          checkpoint_id: "TT-9",
          mandatory_flag: true,
          confirm_by: "qr",
        },
      ],
    },
    {
      id: "ROUTE-PUMP-DAILY",
      name: "Насосная ежедневная",
      org_id: "ORG-01",
      department_id: "DEPT-UGP",
      qualification_id: "OPERATOR-TU",
      location: "АНГКМ / насосная",
      duration_min: 25,
      planning_rule: "daily_06_00",
      version: "1",
      is_active: false,
      steps: [
        {
          id: "STEP-PUMP-1",
          seq_no: 1,
          equipment_id: "EQ-PUMP-0201",
          checkpoint_id: "VI-1",
          mandatory_flag: true,
          confirm_by: "qr",
        },
      ],
    },
  ],
  checklistTemplates: [
    {
      id: "CHK-KC0103",
      name: "Компрессорный обход",
      route_id: "ROUTE-KC0103",
      version: "5",
      items: [
        {
          id: "CHK-KC0103-1",
          seq_no: 1,
          question: "Проверить защитные кожухи и блокировки",
          answer_type: "bool",
          required_flag: true,
        },
        {
          id: "CHK-KC0103-2",
          seq_no: 2,
          question: "Зафиксировать давление на выходе компрессора",
          answer_type: "number",
          required_flag: true,
        },
      ],
    },
    {
      id: "CHK-REAGENT",
      name: "Осмотр узла реагентов",
      route_id: "ROUTE-REAGENT",
      version: "2",
      items: [
        {
          id: "CHK-REAGENT-1",
          seq_no: 1,
          question: "Проверить герметичность арматуры",
          answer_type: "bool",
          required_flag: true,
        },
        {
          id: "CHK-REAGENT-2",
          seq_no: 2,
          question: "Проверить температуру на выходе теплообменника",
          answer_type: "number",
          required_flag: true,
        },
      ],
    },
    {
      id: "CHK-PUMP",
      name: "Насосная проверка",
      route_id: "ROUTE-PUMP-DAILY",
      version: "1",
      items: [
        {
          id: "CHK-PUMP-1",
          seq_no: 1,
          question: "Проверить вибрацию агрегата",
          answer_type: "number",
          required_flag: true,
        },
      ],
    },
  ],
  rounds: [
    {
      id: "ROUND-2026-04-17-000123",
      route_id: "ROUTE-KC0103",
      employee_id: "EMP-145",
      employee_name: "Иван Соколов",
      shift_id: "SHIFT-A-2026-04-17",
      status: "in_progress",
      planned_start: "2026-04-17T06:00:00+05:00",
      planned_end: "2026-04-17T07:00:00+05:00",
      completion_pct: 50,
      checklist_template_id: "CHK-KC0103",
      checklist_instance: {
        id: "CLI-2026-04-17-001",
        status: "running",
        completion_pct: 50,
        started_at: "2026-04-17T06:05:00+05:00",
        finished_at: null,
      },
      readings: [
        {
          equipment_id: "EQ-KC0103",
          checkpoint_id: "PI-2",
          parameter_code: "PRESSURE_OUT",
          value: 1.48,
          unit: "MPa",
          within_limits: true,
          comment: "норма",
        },
      ],
      defects: [],
      journal: [
        {
          id: "JE-0001",
          event_ts: "2026-04-17T06:05:00+05:00",
          event_type: "round_started",
          title: "Обход начат",
        },
        {
          id: "JE-0002",
          event_ts: "2026-04-17T06:14:00+05:00",
          event_type: "checkpoint_confirmed",
          title: "Подтверждена точка PI-2",
        },
      ],
    },
    {
      id: "ROUND-2026-04-17-000124",
      route_id: "ROUTE-REAGENT",
      employee_id: "EMP-233",
      employee_name: "Никита Власов",
      shift_id: "SHIFT-A-2026-04-17",
      status: "completed",
      planned_start: "2026-04-17T08:00:00+05:00",
      planned_end: "2026-04-17T08:40:00+05:00",
      completion_pct: 100,
      checklist_template_id: "CHK-REAGENT",
      checklist_instance: {
        id: "CLI-2026-04-17-002",
        status: "completed",
        completion_pct: 100,
        started_at: "2026-04-17T08:01:00+05:00",
        finished_at: "2026-04-17T08:34:00+05:00",
      },
      readings: [
        {
          equipment_id: "EQ-HE-3302",
          checkpoint_id: "TT-9",
          parameter_code: "TEMP_OUT",
          value: 84,
          unit: "C",
          within_limits: false,
          comment: "выше допуска",
        },
      ],
      defects: [
        {
          id: "DEF-00001353",
          equipment_id: "EQ-HE-3302",
          severity: "critical",
          status: "confirmed",
          comment: "Температура на выходе выше допустимого диапазона",
        },
      ],
      journal: [
        {
          id: "JE-0003",
          event_ts: "2026-04-17T08:01:00+05:00",
          event_type: "round_started",
          title: "Обход начат",
        },
        {
          id: "JE-0004",
          event_ts: "2026-04-17T08:22:00+05:00",
          event_type: "defect_registered",
          title: "Зарегистрировано критическое отклонение",
        },
        {
          id: "JE-0005",
          event_ts: "2026-04-17T08:34:00+05:00",
          event_type: "round_completed",
          title: "Обход завершен",
        },
      ],
    },
    {
      id: "ROUND-2026-04-17-000125",
      route_id: "ROUTE-PUMP-DAILY",
      employee_id: "EMP-145",
      employee_name: "Иван Соколов",
      shift_id: "SHIFT-B-2026-04-17",
      status: "planned",
      planned_start: "2026-04-17T18:00:00+05:00",
      planned_end: "2026-04-17T18:30:00+05:00",
      completion_pct: 0,
      checklist_template_id: "CHK-PUMP",
      checklist_instance: {
        id: "CLI-2026-04-17-003",
        status: "draft",
        completion_pct: 0,
        started_at: null,
        finished_at: null,
      },
      readings: [],
      defects: [],
      journal: [
        {
          id: "JE-0006",
          event_ts: "2026-04-17T16:00:00+05:00",
          event_type: "round_created",
          title: "Обход создан и назначен сотруднику",
        },
      ],
    },
  ],
};

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function readDb() {
  try {
    const raw = localStorage.getItem(MOCK_DB_STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function writeDb(value) {
  localStorage.setItem(MOCK_DB_STORAGE_KEY, JSON.stringify(value));
}

function ensureDb() {
  const existing = readDb();
  if (existing) {
    return existing;
  }

  const next = clone(seedData);
  writeDb(next);
  return next;
}

function getEquipmentIndex(db) {
  return new Map(db.equipment.map((item) => [item.id, item]));
}

function getRouteIndex(db) {
  return new Map(db.routes.map((item) => [item.id, item]));
}

function getChecklistTemplateIndex(db) {
  return new Map(db.checklistTemplates.map((item) => [item.id, item]));
}

function buildTask(round, route) {
  return {
    id: round.id,
    route_name: route?.name || round.route_id,
    status: round.status,
    completion_pct: round.completion_pct || 0,
  };
}

function buildRoundDetail(db, roundId) {
  const equipmentIndex = getEquipmentIndex(db);
  const routeIndex = getRouteIndex(db);
  const checklistIndex = getChecklistTemplateIndex(db);
  const round = db.rounds.find((item) => item.id === roundId);

  if (!round) {
    throw new Error("Обход не найден в mock-хранилище.");
  }

  const route = routeIndex.get(round.route_id);
  const checklistTemplate = checklistIndex.get(round.checklist_template_id) || null;

  return {
    round: {
      id: round.id,
      employee_id: round.employee_id,
      employee_name: round.employee_name,
      route_id: round.route_id,
      shift_id: round.shift_id,
      status: round.status,
      planned_start: round.planned_start,
      planned_end: round.planned_end,
    },
    route: clone(route),
    checklist_template: checklistTemplate ? clone(checklistTemplate) : null,
    checklist_instance: clone(round.checklist_instance),
    equipment: (route?.steps || [])
      .map((step) => equipmentIndex.get(step.equipment_id))
      .filter(Boolean)
      .map((item) => clone(item)),
    readings: clone(round.readings || []),
    defects: clone(round.defects || []),
    journal: clone(round.journal || []),
  };
}

function buildRoundReportListItem(db, round) {
  const route = getRouteIndex(db).get(round.route_id);
  const checklistTemplate = getChecklistTemplateIndex(db).get(round.checklist_template_id);
  const mandatoryStepsTotal = (route?.steps || []).filter((step) => step.mandatory_flag).length;
  const confirmedStepsCount =
    round.status === "completed"
      ? mandatoryStepsTotal
      : round.status === "in_progress"
        ? Math.max(1, Math.round(mandatoryStepsTotal / 2))
        : 0;
  const requiredItemsTotal = (checklistTemplate?.items || []).filter((item) => item.required_flag).length;
  const completedItemsCount = Math.round((requiredItemsTotal * Number(round.completion_pct || 0)) / 100);
  const warningCount = (round.readings || []).filter((reading) => reading.within_limits === false).length;
  const criticalCount = (round.defects || []).filter((defect) => defect.severity === "critical").length;

  return {
    id: round.id,
    status: round.status,
    route_id: round.route_id,
    route_name: route?.name || round.route_id,
    employee_id: round.employee_id,
    employee_name: round.employee_name,
    planned_start: round.planned_start,
    planned_end: round.planned_end || null,
    actual_start: round.checklist_instance?.started_at || null,
    actual_end: round.checklist_instance?.finished_at || null,
    mandatory_steps_total: mandatoryStepsTotal,
    confirmed_steps_count: confirmedStepsCount,
    required_items_total: requiredItemsTotal,
    completed_items_count: completedItemsCount,
    warning_count: warningCount,
    critical_count: criticalCount,
    defects_count: (round.defects || []).length,
    completion_pct: round.completion_pct || 0,
  };
}

function sortByPlannedStartDesc(items) {
  return [...items].sort((left, right) => {
    const leftTime = new Date(left.planned_start || 0).getTime();
    const rightTime = new Date(right.planned_start || 0).getTime();
    return rightTime - leftTime;
  });
}

function delay(value) {
  return new Promise((resolve) => {
    window.setTimeout(() => resolve(clone(value)), 180);
  });
}

export function isMockApiEnabled() {
  const source = String(import.meta.env.VITE_DATA_SOURCE || import.meta.env.VITE_API_MODE || "mock").toLowerCase();
  return source !== "backend";
}

export const mockApi = {
  getCurrentUser() {
    return delay({
      id: "chief-local",
      role: "MANAGER",
      name: "Руководитель смены",
    });
  },

  listTasks() {
    const db = ensureDb();
    const routeIndex = getRouteIndex(db);
    return delay(db.rounds.map((round) => buildTask(round, routeIndex.get(round.route_id))));
  },

  getTaskDetail(_, roundId) {
    return delay(buildRoundDetail(ensureDb(), roundId));
  },

  startRound(_, roundId) {
    const db = ensureDb();
    const round = db.rounds.find((item) => item.id === roundId);

    if (!round) {
      throw new Error("Невозможно стартовать обход: запись не найдена.");
    }

    if (round.status === "completed") {
      throw new Error("Обход уже завершен.");
    }

    round.status = "in_progress";
    round.completion_pct = Math.max(5, round.completion_pct || 0);
    round.checklist_instance.status = "running";
    round.checklist_instance.started_at = round.checklist_instance.started_at || new Date().toISOString();
    round.journal.unshift({
      id: `JE-${Date.now()}`,
      event_ts: new Date().toISOString(),
      event_type: "round_started",
      title: "Обход переведен в работу",
    });

    writeDb(db);
    return delay(buildRoundDetail(db, roundId));
  },

  listEquipment() {
    return delay(ensureDb().equipment);
  },

  getEquipment(_, equipmentId) {
    const equipment = ensureDb().equipment.find((item) => item.id === equipmentId);
    if (!equipment) {
      throw new Error("Оборудование не найдено.");
    }
    return delay(equipment);
  },

  listRoutes() {
    return delay(ensureDb().routes);
  },

  getRoute(_, routeId) {
    const route = ensureDb().routes.find((item) => item.id === routeId);
    if (!route) {
      throw new Error("Маршрут не найден.");
    }
    return delay(route);
  },

  getReportsSummary() {
    const db = ensureDb();
    const rounds = db.rounds.map((round) => buildRoundReportListItem(db, round));

    return delay({
      rounds_total: rounds.length,
      rounds_planned: rounds.filter((round) => round.status === "planned").length,
      rounds_in_progress: rounds.filter((round) => round.status === "in_progress").length,
      rounds_completed: rounds.filter((round) => round.status === "completed").length,
      defects_open: db.rounds.reduce(
        (total, round) => total + (round.defects || []).filter((defect) => defect.status !== "closed").length,
        0,
      ),
      warning_count: rounds.reduce((total, round) => total + round.warning_count, 0),
      critical_count: rounds.reduce((total, round) => total + round.critical_count, 0),
      avg_completion_pct:
        rounds.length > 0 ? rounds.reduce((total, round) => total + round.completion_pct, 0) / rounds.length : 0,
    });
  },

  listRoundReports(_, params = {}) {
    const db = ensureDb();
    const limit = Number(params.limit || 50);
    const offset = Number(params.offset || 0);
    const filtered = sortByPlannedStartDesc(
      db.rounds
        .filter((round) => (params.status ? round.status === params.status : true))
        .filter((round) => (params.employee_id ? round.employee_id === params.employee_id : true))
        .map((round) => buildRoundReportListItem(db, round)),
    );

    return delay(filtered.slice(offset, offset + limit));
  },

  getEquipmentAnalytics(_, params = {}) {
    const db = ensureDb();
    const equipmentIndex = getEquipmentIndex(db);
    const items = Array.from(equipmentIndex.values()).map((equipment) => {
      let defectsCount = 0;
      let warningCount = 0;
      let criticalCount = 0;
      let lastReadingAt = null;

      db.rounds.forEach((round) => {
        (round.defects || [])
          .filter((defect) => defect.equipment_id === equipment.id)
          .forEach((defect) => {
            defectsCount += 1;
            criticalCount += defect.severity === "critical" ? 1 : 0;
          });

        (round.readings || [])
          .filter((reading) => reading.equipment_id === equipment.id)
          .forEach((reading) => {
            warningCount += reading.within_limits === false ? 1 : 0;
            lastReadingAt = round.checklist_instance?.finished_at || round.checklist_instance?.started_at || lastReadingAt;
          });
      });

      return {
        equipment_id: equipment.id,
        equipment_name: equipment.name,
        location: equipment.location,
        defects_count: defectsCount,
        warning_count: warningCount,
        critical_count: criticalCount,
        last_reading_at: lastReadingAt,
      };
    });

    const limit = Number(params.limit || 20);
    const sorted = [...items].sort((left, right) => {
      const leftScore = left.critical_count * 100 + left.defects_count * 10 + left.warning_count;
      const rightScore = right.critical_count * 100 + right.defects_count * 10 + right.warning_count;
      return rightScore - leftScore;
    });

    return delay(sorted.slice(0, limit));
  },

  getEmployeeAnalytics(_, params = {}) {
    const db = ensureDb();
    const items = Array.from(
      db.rounds.reduce((index, round) => {
        const current = index.get(round.employee_id) || {
          employee_id: round.employee_id,
          employee_name: round.employee_name,
          rounds_total: 0,
          rounds_completed: 0,
          confirmed_steps_count: 0,
          durationSamples: [],
          warning_count: 0,
          critical_count: 0,
        };

        const reportItem = buildRoundReportListItem(db, round);
        current.rounds_total += 1;
        current.rounds_completed += round.status === "completed" ? 1 : 0;
        current.confirmed_steps_count += reportItem.confirmed_steps_count;
        current.warning_count += reportItem.warning_count;
        current.critical_count += reportItem.critical_count;

        if (reportItem.actual_start && reportItem.actual_end) {
          const durationMs = new Date(reportItem.actual_end).getTime() - new Date(reportItem.actual_start).getTime();
          if (durationMs > 0) {
            current.durationSamples.push(durationMs / 60000);
          }
        }

        index.set(round.employee_id, current);
        return index;
      }, new Map()).values(),
    ).map((employee) => ({
      employee_id: employee.employee_id,
      employee_name: employee.employee_name,
      rounds_total: employee.rounds_total,
      rounds_completed: employee.rounds_completed,
      confirmed_steps_count: employee.confirmed_steps_count,
      avg_duration_min:
        employee.durationSamples.length > 0
          ? employee.durationSamples.reduce((total, value) => total + value, 0) / employee.durationSamples.length
          : null,
      warning_count: employee.warning_count,
      critical_count: employee.critical_count,
    }));

    const limit = Number(params.limit || 20);
    const sorted = [...items].sort((left, right) => right.rounds_completed - left.rounds_completed);
    return delay(sorted.slice(0, limit));
  },

  reset() {
    localStorage.removeItem(MOCK_DB_STORAGE_KEY);
    return delay(ensureDb());
  },
};
