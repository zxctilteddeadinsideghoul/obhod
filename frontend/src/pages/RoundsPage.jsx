import { useMemo, useState } from "react";
import { useAuth } from "../auth/AuthContext";
import { Card, EmptyState, ErrorState, LoadingState, MetricCard, PageHeader, StatusBadge } from "../components/Ui";
import { useAsyncResource } from "../lib/hooks";
import { api } from "../lib/api";
import {
  describeReadingRange,
  formatDateTime,
  formatPercent,
  getReadingTone,
  getRoundOutcome,
  sentenceFromStatus,
  statusTone,
} from "../lib/format";

export function RoundsPage() {
  const { session } = useAuth();
  const [selectedRoundId, setSelectedRoundId] = useState(null);
  const [actionError, setActionError] = useState("");
  const tasksState = useAsyncResource(() => api.listTasks(session.token), [session.token]);
  const detailState = useAsyncResource(
    () => (selectedRoundId ? api.getTaskDetail(session.token, selectedRoundId) : Promise.resolve(null)),
    [session.token, selectedRoundId],
  );

  const tasks = tasksState.data || [];
  const detailOutcome = detailState.data ? getRoundOutcome(detailState.data) : null;
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

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Контроль исполнения"
        title="Обходы"
        subtitle="Список назначенных обходов, состояние прохождения и детализация выбранного маршрута."
      />

      <div className="metrics-grid">
        <MetricCard label="Всего обходов" value={metrics.total} />
        <MetricCard label="Активные" value={metrics.active} tone="info" />
        <MetricCard label="Завершенные" value={metrics.completed} tone="success" />
      </div>

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
                  <span>{task.id}</span>
                </div>
                <div className="list-item-meta">
                  <StatusBadge status={sentenceFromStatus(task.status)} tone={statusTone(task.status)} />
                  <small>{formatPercent(task.completion_pct)}</small>
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
                  <strong>{detailState.data.round.employee_id}</strong>
                </div>
                <div>
                  <span className="eyebrow">Плановое окно</span>
                  <strong>{formatDateTime(detailState.data.round.planned_start)}</strong>
                </div>
                <div>
                  <span className="eyebrow">Маршрут</span>
                  <strong>{detailState.data.route.name}</strong>
                </div>
              </div>

              <Card title="Точки маршрута" subtitle={`${detailState.data.route.steps.length} шагов`}>
                <div className="table-like">
                  {detailState.data.route.steps.map((step) => (
                    <div key={step.id} className="table-row">
                      <span>#{step.seq_no}</span>
                      <strong>{step.equipment_id}</strong>
                      <span>{step.checkpoint_id || "Без checkpoint"}</span>
                      <StatusBadge status={step.confirm_by.toUpperCase()} tone="info" />
                    </div>
                  ))}
                </div>
              </Card>

              <Card title="Чек-лист" subtitle={detailState.data.checklist_template?.name || "Не привязан"}>
                {detailState.data.checklist_template ? (
                  <div className="table-like">
                    {detailState.data.checklist_template.items.map((item) => (
                      <div key={item.id} className="table-row">
                        <span>#{item.seq_no}</span>
                        <strong>{item.question}</strong>
                        <span>{item.answer_type}</span>
                        <span>{item.required_flag ? "Обязательный" : "Необязательный"}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <EmptyState
                    title="Шаблон чек-листа не найден"
                    description="Для выбранного обхода не найден связанный шаблон."
                  />
                )}
              </Card>

              <Card title="Показания и нормы" subtitle="Сопоставление фактических значений с допустимыми диапазонами">
                {detailState.data.readings?.length ? (
                  <div className="table-like">
                    {detailState.data.readings.map((reading, index) => {
                      const equipment = detailState.data.equipment.find((item) => item.id === reading.equipment_id);
                      const parameter = equipment?.parameters?.find((item) => item.code === reading.parameter_code);

                      return (
                        <div key={`${reading.equipment_id}-${reading.parameter_code}-${index}`} className="table-row wide">
                          <div>
                            <strong>{equipment?.name || reading.equipment_id}</strong>
                            <span>{reading.parameter_code}</span>
                          </div>
                          <span>
                            Факт: {reading.value} {reading.unit}
                          </span>
                          <span>Норма: {describeReadingRange(parameter)}</span>
                          <span>{reading.comment || "Без комментария"}</span>
                          <StatusBadge
                            status={reading.within_limits ? "В пределах нормы" : "Вне нормы"}
                            tone={getReadingTone(reading)}
                          />
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <EmptyState title="Показаний нет" description="Для выбранного обхода еще не зафиксированы контрольные значения." />
                )}
              </Card>

              <Card title="Замечания и события" subtitle="Отклонения и ключевые события по выбранному обходу">
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
                  ) : (
                    <EmptyState title="Замечаний нет" description="По выбранному обходу отклонения не зарегистрированы." />
                  )}

                  {detailState.data.journal?.length ? (
                    <div className="table-like">
                      {detailState.data.journal.map((entry) => (
                        <div key={entry.id} className="table-row wide">
                          <div>
                            <strong>{entry.title}</strong>
                            <span>{entry.event_type}</span>
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
            </div>
          ) : null}
        </Card>
      </div>
    </div>
  );
}
