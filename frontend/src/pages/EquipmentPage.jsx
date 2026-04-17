import { useState } from "react";
import { useAuth } from "../auth/AuthContext";
import { Card, EmptyState, ErrorState, LoadingState, PageHeader, StatusBadge } from "../components/Ui";
import { api } from "../lib/api";
import { useAsyncResource } from "../lib/hooks";
import { describeReadingRange } from "../lib/format";

function renderPairs(record) {
  return Object.entries(record || {}).map(([key, value]) => (
    <div className="kv-row" key={key}>
      <span>{key}</span>
      <strong>{typeof value === "object" ? JSON.stringify(value) : String(value)}</strong>
    </div>
  ));
}

export function EquipmentPage() {
  const { session } = useAuth();
  const [selectedEquipmentId, setSelectedEquipmentId] = useState(null);
  const listState = useAsyncResource(() => api.listEquipment(session.token), [session.token]);
  const detailState = useAsyncResource(
    () => (selectedEquipmentId ? api.getEquipment(session.token, selectedEquipmentId) : Promise.resolve(null)),
    [session.token, selectedEquipmentId],
  );

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Карточки оборудования"
        title="Оборудование"
        subtitle="Просмотр карточек, паспортных полей, тегов QR/NFC и расширенных JSON-атрибутов."
      />

      <div className="master-detail">
        <Card title="Реестр оборудования" subtitle="Карточки, статусы и идентификаторы объектов">
          {listState.loading ? <LoadingState /> : null}
          {listState.error ? <ErrorState error={listState.error} /> : null}
          {!listState.loading && !listState.error && listState.data?.length === 0 ? (
            <EmptyState title="Оборудование отсутствует" description="В реестре пока нет доступных карточек оборудования." />
          ) : null}
          <div className="list-column">
            {(listState.data || []).map((item) => (
              <button
                type="button"
                key={item.id}
                className={`list-item${selectedEquipmentId === item.id ? " selected" : ""}`}
                onClick={() => setSelectedEquipmentId(item.id)}
              >
                <div>
                  <strong>{item.name}</strong>
                  <span>{item.tech_no || item.code || item.id}</span>
                </div>
                <div className="list-item-meta">
                  <StatusBadge status={item.state_id} tone="info" />
                  <small>{item.location || "Без локации"}</small>
                </div>
              </button>
            ))}
          </div>
        </Card>

        <Card title="Карточка оборудования" subtitle="Глубокий просмотр выбранного объекта">
          {detailState.loading && selectedEquipmentId ? <LoadingState /> : null}
          {detailState.error ? <ErrorState error={detailState.error} /> : null}
          {!selectedEquipmentId ? (
            <EmptyState title="Оборудование не выбрано" description="Выберите объект из реестра слева." />
          ) : null}
          {detailState.data ? (
            <div className="detail-stack">
              <div className="detail-grid">
                <div>
                  <span className="eyebrow">Тип</span>
                  <strong>{detailState.data.type_id}</strong>
                </div>
                <div>
                  <span className="eyebrow">Тех. номер</span>
                  <strong>{detailState.data.tech_no || "—"}</strong>
                </div>
                <div>
                  <span className="eyebrow">Паспорт</span>
                  <strong>{detailState.data.passport_no || "—"}</strong>
                </div>
                <div>
                  <span className="eyebrow">Серийный номер</span>
                  <strong>{detailState.data.serial_no || "—"}</strong>
                </div>
              </div>

              <Card title="Теги доступа">
                <div className="detail-grid">
                  <div>
                    <span className="eyebrow">QR</span>
                    <strong>{detailState.data.qr_tag || "—"}</strong>
                  </div>
                  <div>
                    <span className="eyebrow">NFC</span>
                    <strong>{detailState.data.nfc_tag || "—"}</strong>
                  </div>
                </div>
              </Card>

              <Card title="Параметры и нормы" subtitle="Допустимые диапазоны для ввода и контроля показаний">
                {detailState.data.parameters?.length ? (
                  <div className="table-like">
                    {detailState.data.parameters.map((parameter) => (
                      <div key={parameter.code} className="table-row wide">
                        <div>
                          <strong>{parameter.label || parameter.code}</strong>
                          <span>{parameter.code}</span>
                        </div>
                        <span>Ед.: {parameter.unit || "—"}</span>
                        <span>Норма: {describeReadingRange(parameter)}</span>
                        <span>
                          Критично: {parameter.critical_min ?? "—"} - {parameter.critical_max ?? "—"} {parameter.unit || ""}
                        </span>
                        <StatusBadge status="Контроль" tone="info" />
                      </div>
                    ))}
                  </div>
                ) : (
                  <EmptyState title="Параметры не заданы" description="Для выбранного объекта пока нет настроенных диапазонов контроля." />
                )}
              </Card>

              <div className="split-grid">
                <Card title="passport_json">
                  {Object.keys(detailState.data.passport_json || {}).length ? (
                    <div className="kv-list">{renderPairs(detailState.data.passport_json)}</div>
                  ) : (
                    <EmptyState title="Паспортные атрибуты пусты" description="JSON-паспорт пока не заполнен." />
                  )}
                </Card>
                <Card title="snapshot_json">
                  {Object.keys(detailState.data.snapshot_json || {}).length ? (
                    <div className="kv-list">{renderPairs(detailState.data.snapshot_json)}</div>
                  ) : (
                    <EmptyState title="Снимок пуст" description="Расширенные атрибуты для выбранного объекта не заполнены." />
                  )}
                </Card>
              </div>

              <div className="inline-note">
                Страница предназначена для просмотра карточки, паспортных данных и связанных атрибутов объекта.
              </div>
            </div>
          ) : null}
        </Card>
      </div>
    </div>
  );
}
