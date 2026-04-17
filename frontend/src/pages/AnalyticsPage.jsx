import { useAuth } from "../auth/AuthContext";
import { Card, EmptyState, ErrorState, LoadingState, MetricCard, PageHeader } from "../components/Ui";
import { api } from "../lib/api";
import { formatDateTime, formatPercent } from "../lib/format";
import { useAsyncResource } from "../lib/hooks";

async function loadAnalytics(token) {
  const [summary, equipment, employees] = await Promise.all([
    api.getReportsSummary(token),
    api.getEquipmentAnalytics(token, { limit: 5 }),
    api.getEmployeeAnalytics(token, { limit: 5 }),
  ]);

  return {
    summary,
    equipment,
    employees,
  };
}

export function AnalyticsPage() {
  const { session } = useAuth();
  const analyticsState = useAsyncResource(() => loadAnalytics(session.token), [session.token]);
  const data = analyticsState.data;

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Управленческие метрики"
        title="Аналитика"
        subtitle="Сводные показатели из report-service по обходам, оборудованию и исполнителям."
      />

      {analyticsState.loading ? <LoadingState /> : null}
      {analyticsState.error ? <ErrorState error={analyticsState.error} /> : null}

      {data ? (
        <>
          <div className="metrics-grid">
            <MetricCard label="Всего обходов" value={data.summary.rounds_total} />
            <MetricCard label="Завершено" value={data.summary.rounds_completed} tone="success" />
            <MetricCard label="Открытых дефектов" value={data.summary.defects_open} tone="danger" />
            <MetricCard
              label="Среднее заполнение"
              value={formatPercent(Math.round(data.summary.avg_completion_pct || 0))}
              tone="info"
            />
          </div>

          <div className="split-grid">
            <Card title="Риск по оборудованию">
              {data.equipment.length ? (
                <div className="table-like">
                  {data.equipment.map((item) => (
                    <div key={item.equipment_id} className="table-row wide">
                      <div>
                        <strong>{item.equipment_name}</strong>
                        <span>{item.location || "Локация не указана"}</span>
                      </div>
                      <span>Дефекты: {item.defects_count}</span>
                      <span>Предупр.: {item.warning_count}</span>
                      <span>Критич.: {item.critical_count}</span>
                      <span>{formatDateTime(item.last_reading_at)}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <EmptyState title="Нет данных по оборудованию" description="Аналитика появится после первых измерений." />
              )}
            </Card>

            <Card title="Топ исполнителей">
              {data.employees.length ? (
                <div className="table-like">
                  {data.employees.map((item) => (
                    <div key={item.employee_id} className="table-row wide">
                      <div>
                        <strong>{item.employee_name}</strong>
                        <span>{item.employee_id}</span>
                      </div>
                      <span>Обходов: {item.rounds_total}</span>
                      <span>Завершено: {item.rounds_completed}</span>
                      <span>Точек: {item.confirmed_steps_count}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <EmptyState title="Нет данных по исполнителям" description="Аналитика появится после выполнения обходов." />
              )}
            </Card>
          </div>
        </>
      ) : null}
    </div>
  );
}
