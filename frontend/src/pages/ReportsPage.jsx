import { useAuth } from "../auth/AuthContext";
import { Card, EmptyState, ErrorState, LoadingState, MetricCard, PageHeader, StatusBadge } from "../components/Ui";
import { api } from "../lib/api";
import { useAsyncResource } from "../lib/hooks";
import { formatDateTime, formatPercent, sentenceFromStatus, statusTone } from "../lib/format";

async function loadReportProjection(token) {
  const [summary, rows] = await Promise.all([api.getReportsSummary(token), api.listRoundReports(token)]);
  return { summary, rows };
}

function getOutcome(row) {
  if (row.critical_count > 0) {
    return { label: "Критические отклонения", tone: "danger" };
  }

  if (row.defects_count > 0 || row.warning_count > 0) {
    return { label: "Есть замечания", tone: "warning" };
  }

  if (row.status === "completed") {
    return { label: "Без замечаний", tone: "success" };
  }

  return { label: sentenceFromStatus(row.status), tone: statusTone(row.status) };
}

export function ReportsPage() {
  const { session } = useAuth();
  const reportState = useAsyncResource(() => loadReportProjection(session.token), [session.token]);
  const rows = reportState.data?.rows || [];
  const summary = reportState.data?.summary;

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Отчеты по обходам"
        title="Отчеты"
        subtitle="Лента обходов из report-service с прогрессом, замечаниями и статусом выполнения."
      />

      <div className="metrics-grid">
        <MetricCard label="Сводок" value={rows.length} />
        <MetricCard label="Запланировано" value={summary?.rounds_planned || 0} tone="warning" />
        <MetricCard label="В работе" value={summary?.rounds_in_progress || 0} tone="info" />
        <MetricCard label="Завершено" value={summary?.rounds_completed || 0} tone="success" />
      </div>

      <Card title="Лента результатов" subtitle="Текущий список обходов, который возвращает report-service">
        {reportState.loading ? <LoadingState /> : null}
        {reportState.error ? <ErrorState error={reportState.error} /> : null}
        {!reportState.loading && !reportState.error && rows.length === 0 ? (
          <EmptyState title="Нет отчетов" description="Backend пока не вернул ни одного обхода для отчётной ленты." />
        ) : null}

        <div className="table-like">
          {rows.map((row) => {
            const outcome = getOutcome(row);

            return (
              <div key={row.id} className={`table-row wide report-row ${outcome.tone}`}>
                <div>
                  <strong>{row.route_name}</strong>
                  <span>{row.id}</span>
                </div>
                <div>
                  <strong>{row.employee_name}</strong>
                  <span>{row.employee_id}</span>
                </div>
                <span>{formatDateTime(row.planned_start)}</span>
                <div>
                  <strong>{formatPercent(row.completion_pct)}</strong>
                  <span>
                    {row.completed_items_count}/{row.required_items_total} чек-лист
                  </span>
                </div>
                <div>
                  <strong>
                    {row.confirmed_steps_count}/{row.mandatory_steps_total} точек
                  </strong>
                  <span>
                    D: {row.defects_count} / W: {row.warning_count} / C: {row.critical_count}
                  </span>
                </div>
                <div className="report-row-statuses">
                  <StatusBadge status={outcome.label} tone={outcome.tone} />
                  <StatusBadge status={sentenceFromStatus(row.status)} tone={statusTone(row.status)} />
                </div>
              </div>
            );
          })}
        </div>
      </Card>
    </div>
  );
}
