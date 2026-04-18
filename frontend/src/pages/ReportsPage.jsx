import { useEffect, useState } from "react";
import { useAuth } from "../auth/AuthContext";
import { Card, EmptyState, ErrorState, LoadingState, MetricCard, PageHeader, SegmentedControl, StatusBadge } from "../components/Ui";
import { api } from "../lib/api";
import { useAsyncResource } from "../lib/hooks";
import { formatDateTime, formatPercent, sentenceFromStatus, statusTone } from "../lib/format";

const EXPORT_FORMAT_OPTIONS = [
  { value: "pdf", label: "PDF" },
  { value: "json", label: "JSON" },
  { value: "csv", label: "CSV" },
];

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

function isImageAttachment(attachment) {
  return String(attachment?.mime_type || "").startsWith("image/");
}

export function ReportsPage() {
  const { session } = useAuth();
  const [selectedRoundId, setSelectedRoundId] = useState(null);
  const [exportFormat, setExportFormat] = useState("pdf");
  const [exporting, setExporting] = useState(false);
  const [downloadError, setDownloadError] = useState("");
  const [photoPreview, setPhotoPreview] = useState(null);
  const [photoError, setPhotoError] = useState("");
  const [openingPhotoId, setOpeningPhotoId] = useState("");
  const reportState = useAsyncResource(() => loadReportProjection(session.token), [session.token]);
  const detailState = useAsyncResource(
    () => (selectedRoundId ? api.getRoundReport(session.token, selectedRoundId) : Promise.resolve(null)),
    [session.token, selectedRoundId],
  );
  const rows = reportState.data?.rows || [];
  const summary = reportState.data?.summary;
  const selectedRow = rows.find((row) => row.id === selectedRoundId) || null;
  const selectedStatus = detailState.data?.round?.status || selectedRow?.status || null;
  const canExport = selectedStatus === "completed";

  useEffect(() => {
    return () => {
      if (photoPreview?.url) {
        window.URL.revokeObjectURL(photoPreview.url);
      }
    };
  }, [photoPreview]);

  const exportRoundReport = async () => {
    if (!selectedRoundId || !canExport) {
      return;
    }

    try {
      setDownloadError("");
      setExporting(true);
      const blob = await api.exportRoundReport(session.token, selectedRoundId, { format: exportFormat });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${selectedRoundId}.${exportFormat}`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      setDownloadError(error.message || "Не удалось экспортировать отчет обхода.");
    } finally {
      setExporting(false);
    }
  };

  const openDefectPhoto = async (attachment) => {
    try {
      setPhotoError("");
      setOpeningPhotoId(attachment.id);
      const blob = await api.downloadFile(session.token, attachment.download_url);
      const url = window.URL.createObjectURL(blob);
      setPhotoPreview((current) => {
        if (current?.url) {
          window.URL.revokeObjectURL(current.url);
        }
        return {
          url,
          title: attachment.file_name || "Фото дефекта",
        };
      });
    } catch (error) {
      setPhotoError(error.message || "Не удалось открыть фотографию дефекта.");
    } finally {
      setOpeningPhotoId("");
    }
  };

  const closePhotoPreview = () => {
    setPhotoPreview((current) => {
      if (current?.url) {
        window.URL.revokeObjectURL(current.url);
      }
      return null;
    });
  };

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Отчеты по обходам"
        title="Отчеты"
        subtitle="Лента обходов из report-service с прогрессом, замечаниями и статусом выполнения."
      />

      <div className="metrics-grid reports-metrics-grid">
        <MetricCard label="Сводок" value={rows.length} />
        <MetricCard label="Запланировано" value={summary?.rounds_planned || 0} tone="warning" />
        <MetricCard label="В работе" value={summary?.rounds_in_progress || 0} tone="info" />
        <MetricCard label="Завершено" value={summary?.rounds_completed || 0} tone="success" />
      </div>

      <Card title="Лента результатов" subtitle="Текущий список обходов, который возвращает report-service">
        {reportState.loading ? <LoadingState /> : null}
        {reportState.error ? <ErrorState error={reportState.error} /> : null}
        {downloadError ? <ErrorState error={{ message: downloadError }} /> : null}
        {photoError ? <ErrorState error={{ message: photoError }} /> : null}
        {!reportState.loading && !reportState.error && rows.length === 0 ? (
          <EmptyState title="Нет отчетов" description="Backend пока не вернул ни одного обхода для отчётной ленты." />
        ) : null}

        <div className="table-like">
          {rows.map((row) => {
            const outcome = getOutcome(row);

            return (
              <button
                type="button"
                key={row.id}
                className={`table-row wide report-row ${outcome.tone}${selectedRoundId === row.id ? " selected" : ""}`}
                onClick={() => setSelectedRoundId(row.id)}
              >
                <div>
                  <strong>{row.route_name}</strong>
                  <span>{row.id}</span>
                </div>
                <div>
                  <strong>{row.employee_name}</strong>
                  <span>Исполнитель обхода</span>
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
              </button>
            );
          })}
        </div>
      </Card>

      <Card
        title="Детальный отчет"
        subtitle={selectedRoundId ? `Карточка обхода ${selectedRoundId}` : "Выберите обход в ленте выше"}
        aside={
          selectedRoundId && canExport ? (
            <div className="header-actions">
              <SegmentedControl
                value={exportFormat}
                onChange={setExportFormat}
                options={EXPORT_FORMAT_OPTIONS}
                ariaLabel="Формат экспорта отчета"
              />
              <button type="button" className="secondary-button" onClick={exportRoundReport} disabled={exporting}>
                {exporting ? "Экспорт..." : "Скачать отчет"}
              </button>
            </div>
          ) : null
        }
      >
        {detailState.loading && selectedRoundId ? <LoadingState /> : null}
        {detailState.error ? <ErrorState error={detailState.error} /> : null}
        {!selectedRoundId ? (
          <EmptyState title="Обход не выбран" description="Выберите строку в ленте результатов, чтобы открыть детали и файлы." />
        ) : null}
        {detailState.data ? (
          <div className="detail-stack">
            <div className="detail-grid">
              <div>
                <span className="eyebrow">Маршрут</span>
                <strong>{detailState.data.round.route_name}</strong>
              </div>
              <div>
                <span className="eyebrow">Исполнитель</span>
                <strong>{detailState.data.round.employee_name}</strong>
              </div>
              <div>
                <span className="eyebrow">Статус</span>
                <strong>{sentenceFromStatus(detailState.data.round.status)}</strong>
              </div>
              <div>
                <span className="eyebrow">Плановый старт</span>
                <strong>{formatDateTime(detailState.data.round.planned_start)}</strong>
              </div>
            </div>

            <Card title="Дефекты" subtitle="Замечания, зафиксированные в рамках обхода">
              {detailState.data.defects.length ? (
                <div className="table-like">
                  {detailState.data.defects.map((defect) => {
                    const defectPhotos = detailState.data.attachments.filter(
                      (attachment) => attachment.entity_type === "defect" && attachment.entity_id === defect.id && isImageAttachment(attachment),
                    );

                    return (
                      <div key={defect.id} className="table-row wide">
                        <div>
                          <strong>{defect.title}</strong>
                          <span>{defect.equipment_name}</span>
                        </div>
                        <span>{formatDateTime(defect.detected_at)}</span>
                        <span>{defect.severity}</span>
                        <span>{defect.description || "Описание не указано"}</span>
                        <StatusBadge status={sentenceFromStatus(defect.status)} tone={statusTone(defect.status)} />
                        {defectPhotos.length ? (
                          <button
                            type="button"
                            className="secondary-button"
                            onClick={() => openDefectPhoto(defectPhotos[0])}
                            disabled={openingPhotoId === defectPhotos[0].id}
                          >
                            {openingPhotoId === defectPhotos[0].id
                              ? "Открытие..."
                              : defectPhotos.length > 1
                                ? `Фото (${defectPhotos.length})`
                                : "Фото"}
                          </button>
                        ) : (
                          <span className="inline-note compact">Без фото</span>
                        )}
                      </div>
                    );
                  })}
                </div>
              ) : (
                <EmptyState title="Дефектов нет" description="Для выбранного обхода backend не вернул зарегистрированных дефектов." />
              )}
            </Card>
          </div>
        ) : null}
      </Card>

      {photoPreview ? (
        <div className="image-modal" onClick={closePhotoPreview}>
          <div className="image-modal-card" onClick={(event) => event.stopPropagation()}>
            <div className="card-head">
              <div>
                <h3>{photoPreview.title}</h3>
              </div>
              <button type="button" className="ghost-button modal-close" onClick={closePhotoPreview}>
                Закрыть
              </button>
            </div>
            <img className="image-preview" src={photoPreview.url} alt={photoPreview.title} />
          </div>
        </div>
      ) : null}
    </div>
  );
}
