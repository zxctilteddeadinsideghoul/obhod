import { useAuth } from "../auth/AuthContext";
import { Card, EmptyState, ErrorState, LoadingState, MetricCard, PageHeader, StatusBadge } from "../components/Ui";
import { api } from "../lib/api";
import { useAsyncResource } from "../lib/hooks";
import { sentenceFromStatus, statusTone } from "../lib/format";

async function loadEmployeesProjection(token) {
  const tasks = await api.listTasks(token);
  const detailList = await Promise.all(tasks.map((task) => api.getTaskDetail(token, task.id)));
  const index = new Map();

  detailList.forEach((detail) => {
    const employeeId = detail.round.employee_id;
    const current = index.get(employeeId) || {
      id: employeeId,
      rounds: 0,
      completed: 0,
      active: 0,
      routes: new Set(),
      lastRoundStatus: detail.round.status,
    };

    current.rounds += 1;
    current.completed += detail.round.status === "completed" ? 1 : 0;
    current.active += detail.round.status === "in_progress" ? 1 : 0;
    current.routes.add(detail.route.name);
    current.lastRoundStatus = detail.round.status;
    index.set(employeeId, current);
  });

  return Array.from(index.values()).map((employee) => ({
    ...employee,
    routes: Array.from(employee.routes),
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
        subtitle="Сводная картина по исполнителям, маршрутам и статусам выполнения обходов."
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
            <div key={employee.id} className="table-row wide">
              <div>
                <strong>{employee.id}</strong>
                <span>{employee.routes.join(", ") || "Маршруты не найдены"}</span>
              </div>
              <span>Обходов: {employee.rounds}</span>
              <span>Завершено: {employee.completed}</span>
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
