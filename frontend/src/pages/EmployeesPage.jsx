import { useAuth } from "../auth/AuthContext";
import { Card, EmptyState, ErrorState, LoadingState, MetricCard, PageHeader, StatusBadge } from "../components/Ui";
import { api } from "../lib/api";
import { useAsyncResource } from "../lib/hooks";
import { sentenceFromStatus, statusTone } from "../lib/format";

async function loadEmployeesProjection(token) {
  const [employees, rounds] = await Promise.all([
    api.getEmployeeAnalytics(token, { limit: 20 }),
    api.listRoundReports(token, { limit: 200 }),
  ]);

  const latestStatuses = rounds.reduce((index, round) => {
    if (!index.has(round.employee_id)) {
      index.set(round.employee_id, round.status);
    }
    return index;
  }, new Map());

  return employees.map((employee) => ({
    ...employee,
    active: employee.rounds_total - employee.rounds_completed,
    lastRoundStatus: latestStatuses.get(employee.employee_id) || "planned",
  }));
}

export function EmployeesPage() {
  const { session } = useAuth();
  const projectionState = useAsyncResource(() => loadEmployeesProjection(session.token), [session.token]);
  const employees = projectionState.data || [];

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Исполнители"
        title="Сотрудники"
        subtitle="Агрегированная статистика по сотрудникам из report-service."
      />

      <div className="metrics-grid">
        <MetricCard label="Сотрудников в выборке" value={employees.length} />
        <MetricCard
          label="Активные исполнители"
          value={employees.filter((item) => item.active > 0).length}
          tone="info"
        />
      </div>

      <Card title="Проекция сотрудников" subtitle="Агрегация по данным обходов">
        {projectionState.loading ? <LoadingState /> : null}
        {projectionState.error ? <ErrorState error={projectionState.error} /> : null}
        {!projectionState.loading && !projectionState.error && employees.length === 0 ? (
          <EmptyState title="Данных нет" description="В списке обходов нет назначенных исполнителей." />
        ) : null}
        <div className="table-like">
          {employees.map((employee) => (
            <div key={employee.employee_id} className="table-row wide">
              <div>
                <strong>{employee.employee_name}</strong>
                <span>Исполнитель</span>
              </div>
              <span>Обходов: {employee.rounds_total}</span>
              <span>Завершено: {employee.rounds_completed}</span>
              <span>Точек подтверждено: {employee.confirmed_steps_count}</span>
              <StatusBadge
                status={sentenceFromStatus(employee.lastRoundStatus)}
                tone={statusTone(employee.lastRoundStatus)}
              />
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
