export function PageHeader({ eyebrow, title, subtitle, actions }) {
  return (
    <header className="page-header">
      <div>
        {eyebrow ? <span className="eyebrow">{eyebrow}</span> : null}
        <h2>{title}</h2>
        {subtitle ? <p>{subtitle}</p> : null}
      </div>
      {actions ? <div className="header-actions">{actions}</div> : null}
    </header>
  );
}

export function Card({ title, subtitle, children, aside }) {
  return (
    <section className="card">
      {(title || aside) && (
        <div className="card-head">
          <div>
            {title ? <h3>{title}</h3> : null}
            {subtitle ? <p>{subtitle}</p> : null}
          </div>
          {aside}
        </div>
      )}
      {children}
    </section>
  );
}

export function MetricCard({ label, value, tone = "default", helper }) {
  return (
    <div className={`metric-card ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      {helper ? <small>{helper}</small> : null}
    </div>
  );
}

export function StatusBadge({ status, tone }) {
  return <span className={`status-badge ${tone || "info"}`}>{status}</span>;
}

export function EmptyState({ title, description }) {
  return (
    <div className="empty-state">
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  );
}

export function ErrorState({ error }) {
  return (
    <div className="error-state">
      <strong>Ошибка загрузки</strong>
      <p>{error?.message || "Не удалось получить данные."}</p>
    </div>
  );
}

export function LoadingState() {
  return <div className="loading-state">Загрузка данных...</div>;
}
