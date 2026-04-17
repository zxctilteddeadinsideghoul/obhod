import { useState } from "react";
import { useAuth } from "../auth/AuthContext";
import { Card, EmptyState, ErrorState, LoadingState, PageHeader, StatusBadge } from "../components/Ui";
import { api } from "../lib/api";
import { sentenceFromStatus, statusTone } from "../lib/format";
import { useAsyncResource } from "../lib/hooks";

export function RoutesPage() {
  const { session } = useAuth();
  const [selectedRouteId, setSelectedRouteId] = useState(null);
  const listState = useAsyncResource(() => api.listRoutes(session.token), [session.token]);
  const detailState = useAsyncResource(
    () => (selectedRouteId ? api.getRoute(session.token, selectedRouteId) : Promise.resolve(null)),
    [session.token, selectedRouteId],
  );

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Нормативная база маршрутов"
        title="Маршруты"
        subtitle="Шаблоны маршрутов вынесены в отдельную вкладку, чтобы выдержать раздельную модель route_template и round_instance."
      />

      <div className="master-detail">
        <Card title="Каталог маршрутов" subtitle="Шаблоны маршрутов и правила обхода">
          {listState.loading ? <LoadingState /> : null}
          {listState.error ? <ErrorState error={listState.error} /> : null}
          {!listState.loading && !listState.error && listState.data?.length === 0 ? (
            <EmptyState title="Маршрутов нет" description="В реестре пока нет доступных шаблонов маршрута." />
          ) : null}
          <div className="list-column">
            {(listState.data || []).map((route) => (
              <button
                type="button"
                key={route.id}
                className={`list-item${selectedRouteId === route.id ? " selected" : ""}`}
                onClick={() => setSelectedRouteId(route.id)}
              >
                <div>
                  <strong>{route.name}</strong>
                  <span>{route.location || route.id}</span>
                </div>
                <div className="list-item-meta">
                  <StatusBadge status={route.is_active ? "Активен" : "Архив"} tone={route.is_active ? "success" : "warning"} />
                  <small>{route.duration_min} мин</small>
                </div>
              </button>
            ))}
          </div>
        </Card>

        <Card title="Структура маршрута" subtitle="Просмотр и подготовка к редактированию">
          {detailState.loading && selectedRouteId ? <LoadingState /> : null}
          {detailState.error ? <ErrorState error={detailState.error} /> : null}
          {!selectedRouteId ? (
            <EmptyState title="Маршрут не выбран" description="Выберите шаблон маршрута для просмотра шагов и атрибутов." />
          ) : null}
          {detailState.data ? (
            <div className="detail-stack">
              <div className="detail-grid">
                <div>
                  <span className="eyebrow">Локация</span>
                  <strong>{detailState.data.location || "—"}</strong>
                </div>
                <div>
                  <span className="eyebrow">Правило планирования</span>
                  <strong>{detailState.data.planning_rule}</strong>
                </div>
                <div>
                  <span className="eyebrow">Квалификация</span>
                  <strong>{detailState.data.qualification_id || "—"}</strong>
                </div>
                <div>
                  <span className="eyebrow">Версия</span>
                  <strong>{detailState.data.version}</strong>
                </div>
              </div>

              <div className="inline-note">
                Вкладка показывает структуру маршрута, состав шагов и ключевые атрибуты шаблона.
              </div>

              <div className="table-like">
                {detailState.data.steps.map((step) => (
                  <div className="table-row" key={step.id}>
                    <span>#{step.seq_no}</span>
                    <strong>{step.equipment_id}</strong>
                    <span>{step.checkpoint_id || "Без checkpoint"}</span>
                    <StatusBadge status={step.confirm_by} tone={statusTone(step.confirm_by)} />
                    <span>{step.mandatory_flag ? "Обязателен" : "Опционален"}</span>
                  </div>
                ))}
              </div>
            </div>
          ) : null}
        </Card>
      </div>
    </div>
  );
}
