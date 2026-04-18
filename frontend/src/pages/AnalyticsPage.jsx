import { useState } from "react";
import { useAuth } from "../auth/AuthContext";
import { Card, EmptyState, ErrorState, LoadingState, MetricCard, PageHeader, SegmentedControl } from "../components/Ui";
import { api } from "../lib/api";
import { formatDateTime } from "../lib/format";
import { useAsyncResource } from "../lib/hooks";

const EXPORT_FORMAT_OPTIONS = [
  { value: "pdf", label: "PDF" },
  { value: "json", label: "JSON" },
  { value: "csv", label: "CSV" },
];

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
  const [exportFormat, setExportFormat] = useState("pdf");
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState("");
  const analyticsState = useAsyncResource(() => loadAnalytics(session.token), [session.token]);
  const data = analyticsState.data;

  const exportAnalytics = async () => {
    try {
      setExporting(true);
      setExportError("");
      const blob = await api.exportAnalytics(session.token, {
        format: exportFormat,
        limit: 20,
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `analytics-report.${exportFormat}`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      setExportError(error.message || "Не удалось экспортировать аналитику.");
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Управленческие метрики"
        title="Аналитика"
        subtitle="Сводные показатели из report-service по обходам, оборудованию и исполнителям."
        actions={
          <div className="header-actions">
            <SegmentedControl
              value={exportFormat}
              onChange={setExportFormat}
              options={EXPORT_FORMAT_OPTIONS}
              ariaLabel="Формат экспорта аналитики"
            />
            <button type="button" className="secondary-button" onClick={exportAnalytics} disabled={exporting}>
              {exporting ? "Экспорт..." : "Скачать сводку"}
            </button>
          </div>
        }
      />

      {analyticsState.loading ? <LoadingState /> : null}
      {analyticsState.error ? <ErrorState error={analyticsState.error} /> : null}
      {exportError ? <ErrorState error={{ message: exportError }} /> : null}

      {data ? (
        <>
          <div className="metrics-grid">
            <MetricCard label="Всего обходов" value={data.summary.rounds_total} />
            <MetricCard label="Завершено" value={data.summary.rounds_completed} tone="success" />
            <MetricCard label="Открытых дефектов" value={data.summary.defects_open} tone="danger" />
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
                        <span>Исполнитель</span>
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
