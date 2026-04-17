import { useAuth } from "../auth/AuthContext";
import { Card, EmptyState, ErrorState, LoadingState, MetricCard, PageHeader, StatusBadge } from "../components/Ui";
import { api } from "../lib/api";
import { useAsyncResource } from "../lib/hooks";
import { formatDateTime, getRoundOutcome, sentenceFromStatus, statusTone } from "../lib/format";

async function loadReportProjection(token) {
  const tasks = await api.listTasks(token);
  const details = await Promise.all(tasks.map((task) => api.getTaskDetail(token, task.id)));

  return details.map((detail) => {
    const checklistItems = detail.checklist_template?.items || [];
    const outcome = getRoundOutcome(detail);
    return {
      roundId: detail.round.id,
      routeName: detail.route.name,
      employeeId: detail.round.employee_id,
      status: detail.round.status,
      plannedStart: detail.round.planned_start,
      equipmentCount: detail.equipment.length,
      checklistName: detail.checklist_template?.name || "Не привязан",
      checklistItems: checklistItems.length,
      checklistCompletion: detail.checklist_instance?.completion_pct || 0,
      outcomeLabel: outcome.label,
      outcomeTone: outcome.tone,
    };
  });
}

export function ReportsPage() {
  const { session } = useAuth();
  const reportState = useAsyncResource(() => loadReportProjection(session.token), [session.token]);
  const rows = reportState.data || [];

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Сводки и результаты"
        title="Сводки"
        subtitle="Название изменено с «Отчёты» на более операционное: здесь сводная лента результатов обходов."
      />

      <div className="metrics-grid">
        <MetricCard label="Сводок" value={rows.length} />
        <MetricCard label="С чек-листом" value={rows.filter((row) => row.checklistItems > 0).length} tone="info" />
        <MetricCard
          label="Завершенные обходы"
          value={rows.filter((row) => row.status === "completed").length}
          tone="success"
        />
      </div>

      <Card title="Лента результатов" subtitle="Сводка по результатам выполненных и активных обходов">
        {reportState.loading ? <LoadingState /> : null}
        {reportState.error ? <ErrorState error={reportState.error} /> : null}
        {!reportState.loading && !reportState.error && rows.length === 0 ? (
          <EmptyState title="Нет данных для сводки" description="В текущей выборке пока нет результатов обходов." />
        ) : null}

        <div className="table-like">
          {rows.map((row) => (
            <div key={row.roundId} className={`table-row wide report-row ${row.outcomeTone}`}>
              <div>
                <strong>{row.routeName}</strong>
                <span>{row.roundId}</span>
              </div>
              <span>{row.employeeId}</span>
              <span>{formatDateTime(row.plannedStart)}</span>
              <span>{row.equipmentCount} ед.</span>
              <div>
                <strong>{row.checklistName}</strong>
                <span>{row.checklistCompletion}% заполнения</span>
              </div>
              <div className="report-row-statuses">
                <StatusBadge status={row.outcomeLabel} tone={row.outcomeTone} />
                <StatusBadge status={sentenceFromStatus(row.status)} tone={statusTone(row.status)} />
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
