export function formatDateTime(value) {
  if (!value) {
    return "—";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  const pad = (part) => String(part).padStart(2, "0");
  const day = pad(date.getDate());
  const month = pad(date.getMonth() + 1);
  const year = date.getFullYear();
  const hours = pad(date.getHours());
  const minutes = pad(date.getMinutes());

  return `${day}.${month}.${year} ${hours}:${minutes}`;
}

export function formatPercent(value) {
  return `${Math.max(0, Math.min(100, Number(value || 0)))}%`;
}

export function equipmentTypeLabel(type) {
  const labels = {
    compressor: "Компрессор",
    pump: "Насос",
    valve: "Арматура",
    heat_exchanger: "Теплообменник",
    fan: "Вентилятор",
  };

  return labels[type] || type || "Не указан";
}

export function planningRuleLabel(rule) {
  const labels = {
    manual: "По запросу",
    every_3_hours: "Каждые 3 часа",
    every_shift: "Каждую смену",
    daily_06_00: "Ежедневно в 06:00",
  };

  return labels[rule] || rule || "Не указано";
}

export function qualificationLabel(value) {
  const labels = {
    "OPERATOR-TU": "Оператор ТУ",
    "OPERATOR-CHEM": "Оператор хим. участка",
  };

  return labels[value] || value || "Не указана";
}

export function confirmMethodLabel(value) {
  const labels = {
    qr: "По QR",
    nfc: "По NFC",
    manual: "Вручную",
  };

  return labels[value] || value || "Не указан";
}

export function answerTypeLabel(value) {
  const labels = {
    bool: "Да/нет",
    number: "Число",
    text: "Текст",
  };

  return labels[value] || value || "Не указан";
}

export function eventTypeLabel(value) {
  const labels = {
    round_started: "Обход начат",
    checkpoint_confirmed: "Точка подтверждена",
    defect_registered: "Замечание зарегистрировано",
    round_completed: "Обход завершен",
    round_created: "Обход создан",
  };

  return labels[value] || value || "Событие";
}

export function resultCodeLabel(value) {
  const labels = {
    ok: "Норма",
    normal: "Норма",
    pass: "Пройдено",
    fail: "Не пройдено",
    yes: "Да",
    no: "Нет",
    true: "Да",
    false: "Нет",
    warning: "Есть отклонение",
    critical: "Критичное отклонение",
    noise: "Посторонний шум",
  };

  return labels[String(value || "").toLowerCase()] || value || "Без оценки";
}

export function displayValue(value) {
  if (value === null || value === undefined || value === "") {
    return "—";
  }

  if (typeof value === "boolean") {
    return value ? "Да" : "Нет";
  }

  if (Array.isArray(value)) {
    return value.length ? value.map(displayValue).join(", ") : "—";
  }

  if (typeof value === "object") {
    const entries = Object.values(value).map(displayValue).filter(Boolean);
    return entries.length ? entries.join(", ") : "—";
  }

  return String(value);
}

export function statusTone(status) {
  const normalized = String(status || "").toLowerCase();

  if (["completed", "done", "signed"].includes(normalized)) {
    return "success";
  }

  if (["warning", "draft", "paused", "sent"].includes(normalized)) {
    return "warning";
  }

  if (["critical", "failed", "cancelled"].includes(normalized)) {
    return "danger";
  }

  return "info";
}

export function sentenceFromStatus(status) {
  const labels = {
    planned: "Запланирован",
    in_progress: "В работе",
    completed: "Завершен",
    done: "Завершен",
    done_with_remarks: "Завершен с замечаниями",
    cancelled: "Отменен",
    draft: "Черновик",
    running: "Выполняется",
    paused: "Приостановлен",
    signed: "Подписан",
  };

  return labels[status] || status || "Не указан";
}

export function equipmentStatusLabel(status) {
  const labels = {
    in_operation: "В работе",
    warning: "Есть замечания",
    critical: "Требует внимания",
    maintenance: "На обслуживании",
    out_of_service: "Выведено из эксплуатации",
  };

  return labels[status] || sentenceFromStatus(status);
}

export function equipmentStatusTone(status) {
  const normalized = String(status || "").toLowerCase();

  if (normalized === "in_operation") {
    return "success";
  }

  if (["warning", "maintenance"].includes(normalized)) {
    return "warning";
  }

  if (["critical", "out_of_service"].includes(normalized)) {
    return "danger";
  }

  return statusTone(status);
}

export function getReadingTone(reading) {
  return reading?.within_limits ? "success" : "danger";
}

export function describeReadingRange(parameter) {
  if (!parameter) {
    return "Норма не задана";
  }

  const min = parameter.min ?? "—";
  const max = parameter.max ?? "—";
  const unit = parameter.unit ? ` ${parameter.unit}` : "";
  return `${min} - ${max}${unit}`;
}

export function getRoundOutcome(detail) {
  const explicitStatus = detail?.report_status || detail?.round?.report_status;
  if (explicitStatus === "success") {
    return { label: "Успешно завершен", tone: "success" };
  }
  if (explicitStatus === "warning") {
    return { label: "Есть замечания", tone: "warning" };
  }
  if (explicitStatus === "danger") {
    return { label: "Требует внимания", tone: "danger" };
  }

  const status = detail?.status || detail?.round?.status;
  const defects = detail?.defects || [];
  const readings = detail?.readings || [];

  if (status === "completed" || status === "done") {
    const hasCriticalDefect = defects.some((item) => ["critical", "danger"].includes(item.severity));
    const hasOutOfRangeReading = readings.some((item) => item.within_limits === false);

    if (hasCriticalDefect || hasOutOfRangeReading) {
      return { label: "Требует внимания", tone: "danger" };
    }

    if (defects.length > 0) {
      return { label: "Есть замечания", tone: "warning" };
    }

    return { label: "Успешно завершен", tone: "success" };
  }

  if (status === "in_progress" || status === "running") {
    return { label: "Выполняется", tone: "info" };
  }

  if (status === "planned" || status === "draft") {
    return { label: "Запланирован", tone: "warning" };
  }

  if (status === "cancelled") {
    return { label: "Отменен", tone: "danger" };
  }

  return { label: sentenceFromStatus(status), tone: statusTone(status) };
}
