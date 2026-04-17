export function formatDateTime(value) {
  if (!value) {
    return "—";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("ru-RU", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

export function formatPercent(value) {
  return `${Math.max(0, Math.min(100, Number(value || 0)))}%`;
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
