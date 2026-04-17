import { useMemo, useState } from "react";
import { useAuth } from "../auth/AuthContext";
import { Card, EmptyState, ErrorState, LoadingState, MetricCard, PageHeader, StatusBadge } from "../components/Ui";
import { useAsyncResource } from "../lib/hooks";
import { api } from "../lib/api";
import {
  answerTypeLabel,
  confirmMethodLabel,
  displayValue,
  eventTypeLabel,
  formatDateTime,
  formatPercent,
  getRoundOutcome,
  planningRuleLabel,
  qualificationLabel,
  resultCodeLabel,
  sentenceFromStatus,
  statusTone,
} from "../lib/format";

function toDateTimeLocalValue(date = new Date()) {
  const pad = (part) => String(part).padStart(2, "0");
  const local = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
  return `${local.getFullYear()}-${pad(local.getMonth() + 1)}-${pad(local.getDate())}T${pad(local.getHours())}:${pad(local.getMinutes())}`;
}

function describeParameterRange(parameterDef) {
  const min = parameterDef?.min_value ?? "—";
  const max = parameterDef?.max_value ?? "—";
  const unit = parameterDef?.unit ? ` ${parameterDef.unit}` : "";
  return `${min}-${max}${unit}`;
}

function describeCriticalRange(parameterDef) {
  const min = parameterDef?.critical_min ?? "—";
  const max = parameterDef?.critical_max ?? "—";
  const unit = parameterDef?.unit ? ` ${parameterDef.unit}` : "";
  return `${min}-${max}${unit}`;
}

function getTaskProgress(task) {
  const raw = Number(task?.completion_pct || 0);
  if (raw > 0) {
    return formatPercent(raw);
  }

  if (task?.status === "completed") {
    return "100%";
  }

  if (task?.status === "planned") {
    return "Ожидает старта";
  }

  if (task?.status === "in_progress") {
    return "Выполняется";
  }

  return "—";
}

async function loadEmployeeOptions(token) {
  const employees = await api.getEmployeeAnalytics(token, { limit: 100 });
  return employees
    .map((employee) => ({
      value: employee.employee_id,
      label: `${employee.employee_name} (${employee.employee_id})`,
    }))
    .sort((left, right) => left.label.localeCompare(right.label, "ru"));
}

async function loadShiftOptions(token) {
  const tasks = await api.listTasks(token);
  if (!tasks.length) {
    return [];
  }

  const details = await Promise.all(tasks.map((task) => api.getTaskDetail(token, task.id).catch(() => null)));
  const shifts = new Set(details.map((detail) => detail?.round?.shift_id).filter(Boolean));

  return Array.from(shifts)
    .sort((left, right) => left.localeCompare(right, "ru"))
    .map((shiftId) => ({
      value: shiftId,
      label: shiftId,
    }));
}

export function RoundsPage() {
  const { session } = useAuth();
  const [selectedRoundId, setSelectedRoundId] = useState(null);
  const [actionError, setActionError] = useState("");
  const [createError, setCreateError] = useState("");
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({
    id: "",
    route_template_id: "",
    checklist_template_id: "",
    employee_id: "",
    planned_start: toDateTimeLocalValue(),
    shift_id: "",
  });
  const tasksState = useAsyncResource(() => api.listTasks(session.token), [session.token]);
  const routesState = useAsyncResource(() => api.listRoutes(session.token), [session.token]);
  const checklistTemplatesState = useAsyncResource(() => api.listChecklistTemplates(session.token), [session.token]);
  const employeesState = useAsyncResource(() => loadEmployeeOptions(session.token), [session.token]);
  const shiftsState = useAsyncResource(() => loadShiftOptions(session.token), [session.token]);
  const detailState = useAsyncResource(
    () => (selectedRoundId ? api.getTaskDetail(session.token, selectedRoundId) : Promise.resolve(null)),
    [session.token, selectedRoundId],
  );

  const tasks = tasksState.data || [];
  const routes = routesState.data || [];
  const checklistTemplates = checklistTemplatesState.data || [];
  const employeeOptions = employeesState.data || [];
  const shiftOptions = shiftsState.data || [];
  const detailOutcome = detailState.data ? getRoundOutcome(detailState.data) : null;
  const availableChecklistTemplates = useMemo(() => {
    const routeBoundTemplates = checklistTemplates.filter((item) => item.route_id);
    if (!form.route_template_id || routeBoundTemplates.length === 0) {
      return checklistTemplates;
    }
    const filtered = checklistTemplates.filter((item) => item.route_id === form.route_template_id);
    return filtered.length ? filtered : checklistTemplates;
  }, [checklistTemplates, form.route_template_id]);
  const metrics = useMemo(() => {
    const completed = tasks.filter((item) => item.status === "completed").length;
    const active = tasks.filter((item) => item.status === "in_progress").length;
    return {
      total: tasks.length,
      completed,
      active,
    };
  }, [tasks]);

  const startRound = async () => {
    if (!selectedRoundId) {
      return;
    }

    try {
      setActionError("");
      await api.startRound(session.token, selectedRoundId);
      window.location.reload();
    } catch (error) {
      setActionError(error.message);
    }
  };

  const updateForm = (key, value) => {
    setForm((current) => ({ ...current, [key]: value }));
  };

  const handleRouteChange = (value) => {
    const nextTemplates = checklistTemplates.filter((item) => !item.route_id || item.route_id === value);
    setForm((current) => ({
      ...current,
      route_template_id: value,
      checklist_template_id:
        nextTemplates.some((item) => item.id === current.checklist_template_id) ? current.checklist_template_id : "",
    }));
  };

  const createRound = async (event) => {
    event.preventDefault();

    if (!form.route_template_id || !form.checklist_template_id || !form.employee_id || !form.planned_start) {
      setCreateError("Заполните маршрут, шаблон чек-листа, сотрудника и плановое время.");
      return;
    }

    try {
      setCreating(true);
      setCreateError("");
      await api.createRound(session.token, {
        ...(form.id.trim() ? { id: form.id.trim() } : {}),
        route_template_id: form.route_template_id,
        checklist_template_id: form.checklist_template_id,
        employee_id: form.employee_id.trim(),
        planned_start: new Date(form.planned_start).toISOString(),
        ...(form.shift_id.trim() ? { shift_id: form.shift_id.trim() } : {}),
      });
      window.location.reload();
    } catch (error) {
      setCreateError(error.message);
      setCreating(false);
    }
  };

  const hasLegacyObservations = Boolean(detailState.data?.defects?.length || detailState.data?.journal?.length);
  const checklistResultsByItem = new Map((detailState.data?.checklist_results || []).map((item) => [item.item_template_id, item]));

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Контроль исполнения"
        title="Обходы"
        subtitle="Список назначенных обходов, состояние прохождения и детализация выбранного маршрута."
        actions={
          <button
            type="button"
            className="secondary-button"
            onClick={() => {
              setCreateError("");
              setShowCreateForm((current) => !current);
            }}
          >
            {showCreateForm ? "Скрыть форму" : "Новый обход"}
          </button>
        }
      />

      <div className="metrics-grid">
        <MetricCard label="Всего обходов" value={metrics.total} />
        <MetricCard label="Активные" value={metrics.active} tone="info" />
        <MetricCard label="Завершенные" value={metrics.completed} tone="success" />
      </div>

      {showCreateForm ? (
        <Card title="Создать обход" subtitle="Новый обход создается через admin API field-service">
          {routesState.loading || checklistTemplatesState.loading || employeesState.loading || shiftsState.loading ? (
            <LoadingState />
          ) : null}
          {routesState.error ? <ErrorState error={routesState.error} /> : null}
          {checklistTemplatesState.error ? <ErrorState error={checklistTemplatesState.error} /> : null}
          {employeesState.error ? <ErrorState error={employeesState.error} /> : null}
          {shiftsState.error ? <ErrorState error={shiftsState.error} /> : null}
          {createError ? <div className="inline-error">{createError}</div> : null}

          {!routesState.loading &&
          !checklistTemplatesState.loading &&
          !employeesState.loading &&
          !shiftsState.loading ? (
            <form className="inline-form" onSubmit={createRound}>
              <div className="inline-form-row">
                <label>
                  <span>Идентификатор</span>
                  <input
                    value={form.id}
                    onChange={(event) => updateForm("id", event.target.value)}
                    placeholder="Можно оставить пустым"
                  />
                </label>
                <label>
                  <span>Маршрут</span>
                  <select value={form.route_template_id} onChange={(event) => handleRouteChange(event.target.value)}>
                    <option value="">Выберите маршрут</option>
                    {routes.map((route) => (
                      <option key={route.id} value={route.id}>
                        {route.name} ({route.id})
                      </option>
                    ))}
                  </select>
                </label>
              </div>

              <div className="inline-form-row">
                <label>
                  <span>Шаблон чек-листа</span>
                  <select
                    value={form.checklist_template_id}
                    onChange={(event) => updateForm("checklist_template_id", event.target.value)}
                  >
                    <option value="">Выберите шаблон</option>
                    {availableChecklistTemplates.map((template) => (
                      <option key={template.id} value={template.id}>
                        {template.name} ({template.id})
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  <span>Сотрудник</span>
                  <select
                    value={form.employee_id}
                    onChange={(event) => updateForm("employee_id", event.target.value)}
                  >
                    <option value="">Выберите сотрудника</option>
                    {employeeOptions.map((employee) => (
                      <option key={employee.value} value={employee.value}>
                        {employee.label}
                      </option>
                    ))}
                  </select>
                </label>
              </div>

              <div className="inline-form-row">
                <label>
                  <span>Плановый старт</span>
                  <input
                    type="datetime-local"
                    value={form.planned_start}
                    onChange={(event) => updateForm("planned_start", event.target.value)}
                  />
                </label>
                <label>
                  <span>Смена</span>
                  <select
                    value={form.shift_id}
                    onChange={(event) => updateForm("shift_id", event.target.value)}
                  >
                    <option value="">Без смены</option>
                    {shiftOptions.map((shift) => (
                      <option key={shift.value} value={shift.value}>
                        {shift.label}
                      </option>
                    ))}
                  </select>
                </label>
              </div>

              <div className="header-actions">
                <button type="submit" className="primary-button" disabled={creating}>
                  {creating ? "Создание..." : "Создать обход"}
                </button>
              </div>
            </form>
          ) : null}
        </Card>
      ) : null}

      <div className="master-detail">
        <Card title="Список обходов" subtitle="Назначенные и выполняемые обходы">
          {tasksState.loading ? <LoadingState /> : null}
          {tasksState.error ? <ErrorState error={tasksState.error} /> : null}
          {!tasksState.loading && !tasksState.error && tasks.length === 0 ? (
            <EmptyState title="Обходов нет" description="В текущей выборке пока нет назначенных обходов." />
          ) : null}
          <div className="list-column">
            {tasks.map((task) => (
              <button
                type="button"
                key={task.id}
                className={`list-item${selectedRoundId === task.id ? " selected" : ""}`}
                onClick={() => setSelectedRoundId(task.id)}
              >
                <div>
                  <strong>{task.route_name}</strong>
                  <span>{task.planned_start ? `Старт ${formatDateTime(task.planned_start)}` : "Плановое время не задано"}</span>
                </div>
                <div className="list-item-meta">
                  <StatusBadge status={sentenceFromStatus(task.status)} tone={statusTone(task.status)} />
                  <small>{getTaskProgress(task)}</small>
                </div>
              </button>
            ))}
          </div>
        </Card>

        <Card
          title="Карточка обхода"
          subtitle={selectedRoundId ? "Детализация выбранного обхода" : "Выберите запись слева"}
          aside={
            selectedRoundId ? (
              <div className="header-actions">
                {detailOutcome ? <StatusBadge status={detailOutcome.label} tone={detailOutcome.tone} /> : null}
                <button type="button" className="secondary-button" onClick={startRound}>
                  Стартовать
                </button>
              </div>
            ) : null
          }
        >
          {detailState.loading && selectedRoundId ? <LoadingState /> : null}
          {detailState.error ? <ErrorState error={detailState.error} /> : null}
          {actionError ? <div className="inline-error">{actionError}</div> : null}
          {!selectedRoundId ? (
            <EmptyState title="Нет выбранного обхода" description="Для просмотра карточки выберите маршрут из списка." />
          ) : null}
          {detailState.data ? (
            <div className="detail-stack">
              <div className="detail-grid">
                <div>
                  <span className="eyebrow">Статус</span>
                  <strong>{sentenceFromStatus(detailState.data.round.status)}</strong>
                </div>
                <div>
                  <span className="eyebrow">Сотрудник</span>
                  <strong>{detailState.data.round.employee_name || detailState.data.round.employee_id}</strong>
                </div>
                <div>
                  <span className="eyebrow">Плановое окно</span>
                  <strong>{formatDateTime(detailState.data.round.planned_start)}</strong>
                </div>
                <div>
                  <span className="eyebrow">Маршрут</span>
                  <strong>{detailState.data.route.name}</strong>
                </div>
                <div>
                  <span className="eyebrow">Правило планирования</span>
                  <strong>{planningRuleLabel(detailState.data.route.planning_rule)}</strong>
                </div>
                <div>
                  <span className="eyebrow">Квалификация</span>
                  <strong>{qualificationLabel(detailState.data.round.qualification_id || detailState.data.route.qualification_id)}</strong>
                </div>
              </div>

              <Card title="Точки маршрута" subtitle={`${detailState.data.route.steps.length} шагов`}>
                <div className="table-like">
                  {detailState.data.route.steps.map((step) => (
                    <div key={step.id} className="table-row">
                      <span>#{step.seq_no}</span>
                      <strong>Точка маршрута</strong>
                      <span>{step.checkpoint_id ? `Контрольная точка ${step.checkpoint_id}` : "Контрольная точка не указана"}</span>
                      <StatusBadge status={confirmMethodLabel(step.confirm_by)} tone="info" />
                    </div>
                  ))}
                </div>
              </Card>

              <Card title="Чек-лист" subtitle={detailState.data.checklist_template?.name || "Не привязан"}>
                {detailState.data.checklist_template ? (
                  <div className="table-like">
                    {detailState.data.checklist_template.items.map((item) => {
                      const result = checklistResultsByItem.get(item.id);

                      return (
                        <div key={item.id} className="table-row wide">
                          <div>
                            <strong>{item.question}</strong>
                            <span>{item.required_flag ? "Обязательный пункт" : "Необязательный пункт"}</span>
                          </div>
                          <span>{result ? displayValue(result.result_value) : "Не заполнено"}</span>
                          <span>{result ? resultCodeLabel(result.result_code) : answerTypeLabel(item.answer_type)}</span>
                          <span>{result?.comment || "Без комментария"}</span>
                          <StatusBadge
                            status={result ? sentenceFromStatus(result.status) : "Ожидает заполнения"}
                            tone={result ? statusTone(result.status) : "warning"}
                          />
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <EmptyState
                    title="Шаблон чек-листа не найден"
                    description="Для выбранного обхода не найден связанный шаблон."
                  />
                )}
              </Card>

              <Card title="Параметры контроля" subtitle="Нормы и критические диапазоны из task detail backend">
                {detailState.data.equipment_parameters?.length ? (
                  <div className="table-like">
                    {detailState.data.equipment_parameters.map((item) => {
                      const equipment = detailState.data.equipment.find((entry) => entry.id === item.equipment_id);

                      return (
                        <div
                          key={`${item.equipment_id}-${item.parameter_def.id}`}
                          className="table-row wide"
                        >
                          <div>
                            <strong>{equipment?.name || item.equipment_id}</strong>
                            <span>{item.parameter_def.name || "Параметр контроля"}</span>
                          </div>
                          <span>{item.parameter_def.unit ? `Единицы: ${item.parameter_def.unit}` : "Без единиц"}</span>
                          <span>доп. {describeParameterRange(item.parameter_def)}</span>
                          <span>крит. {describeCriticalRange(item.parameter_def)}</span>
                          <StatusBadge status="Контроль" tone="info" />
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <EmptyState title="Параметров нет" description="Backend не вернул контролируемые параметры для выбранного обхода." />
                )}
              </Card>

              {hasLegacyObservations ? (
                <Card title="Замечания и события" subtitle="Дополнительные данные доступны только в mock-режиме">
                  <div className="detail-stack">
                    {detailState.data.defects?.length ? (
                      <div className="table-like">
                        {detailState.data.defects.map((defect) => (
                          <div key={defect.id} className="table-row wide">
                            <div>
                              <strong>{defect.id}</strong>
                              <span>{defect.equipment_id}</span>
                            </div>
                            <span>{defect.comment}</span>
                            <span>{defect.status}</span>
                            <span>{defect.severity}</span>
                            <StatusBadge
                              status={defect.severity === "critical" ? "Критично" : "Замечание"}
                              tone={defect.severity === "critical" ? "danger" : "warning"}
                            />
                          </div>
                        ))}
                      </div>
                    ) : null}

                    {detailState.data.journal?.length ? (
                    <div className="table-like">
                      {detailState.data.journal.map((entry) => (
                        <div key={entry.id} className="table-row wide">
                          <div>
                            <strong>{entry.title}</strong>
                            <span>{eventTypeLabel(entry.event_type)}</span>
                          </div>
                          <span>{formatDateTime(entry.event_ts)}</span>
                          <span />
                          <span />
                          <StatusBadge status="Событие" tone="info" />
                        </div>
                      ))}
                    </div>
                    ) : null}
                  </div>
                </Card>
              ) : null}
            </div>
          ) : null}
        </Card>
      </div>
    </div>
  );
}
