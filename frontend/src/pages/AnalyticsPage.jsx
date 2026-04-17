import { useAuth } from "../auth/AuthContext";
import { Card, EmptyState, ErrorState, LoadingState, MetricCard, PageHeader } from "../components/Ui";
import { api } from "../lib/api";
import { useAsyncResource } from "../lib/hooks";

async function loadAnalytics(token) {
  const tasks = await api.listTasks(token);
  const details = await Promise.all(tasks.map((task) => api.getTaskDetail(token, task.id)));

  const routeCounts = new Map();
  const equipmentCounts = new Map();

  details.forEach((detail) => {
    routeCounts.set(detail.route.name, (routeCounts.get(detail.route.name) || 0) + 1);
    detail.equipment.forEach((equipment) => {
      equipmentCounts.set(equipment.name, (equipmentCounts.get(equipment.name) || 0) + 1);
    });
  });

  return {
    totalRounds: details.length,
    totalEquipmentTouches: Array.from(equipmentCounts.values()).reduce((sum, value) => sum + value, 0),
    topRoutes: Array.from(routeCounts.entries()).sort((a, b) => b[1] - a[1]).slice(0, 5),
    topEquipment: Array.from(equipmentCounts.entries()).sort((a, b) => b[1] - a[1]).slice(0, 5),
    completedRounds: details.filter((detail) => detail.round.status === "completed").length,
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
        subtitle="Сводные метрики по обходам, маршрутам и оборудованию."
      />

      {analyticsState.loading ? <LoadingState /> : null}
      {analyticsState.error ? <ErrorState error={analyticsState.error} /> : null}

      {data ? (
        <>
          <div className="metrics-grid">
            <MetricCard label="Всего обходов" value={data.totalRounds} />
            <MetricCard label="Завершено" value={data.completedRounds} tone="success" />
            <MetricCard label="Касаний оборудования" value={data.totalEquipmentTouches} tone="info" />
          </div>

          <div className="split-grid">
            <Card title="Топ маршрутов">
              {data.topRoutes.length ? (
                <div className="table-like">
                  {data.topRoutes.map(([name, count]) => (
                    <div key={name} className="table-row">
                      <strong>{name}</strong>
                      <span>{count} обходов</span>
                    </div>
                  ))}
                </div>
              ) : (
                <EmptyState title="Нет маршрутов" description="Аналитика появится после загрузки обходов." />
              )}
            </Card>

            <Card title="Топ оборудования">
              {data.topEquipment.length ? (
                <div className="table-like">
                  {data.topEquipment.map(([name, count]) => (
                    <div key={name} className="table-row">
                      <strong>{name}</strong>
                      <span>{count} упоминаний</span>
                    </div>
                  ))}
                </div>
              ) : (
                <EmptyState title="Нет оборудования" description="Аналитика появится после загрузки обходов." />
              )}
            </Card>
          </div>
        </>
      ) : null}
    </div>
  );
}
