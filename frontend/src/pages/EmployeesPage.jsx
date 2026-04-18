import { useState } from "react";
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
    lastRoundStatus: latestStatuses.get(employee.employee_id) || "free",
  }));
}

export function EmployeesPage() {
  const { session } = useAuth();
  const [reloadKey, setReloadKey] = useState(0);
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState("");
  const [createSuccess, setCreateSuccess] = useState("");
  const [form, setForm] = useState({
    username: "",
    full_name: "",
    password: "",
    employee_id: "",
    qualification_id: "OPERATOR-TU",
    department_id: "DEPT-UGP",
  });
  const projectionState = useAsyncResource(() => loadEmployeesProjection(session.token), [session.token, reloadKey]);
  const employees = projectionState.data || [];

  const updateForm = (key, value) => {
    setForm((current) => ({ ...current, [key]: value }));
  };

  const createWorker = async (event) => {
    event.preventDefault();

    if (!form.username.trim() || !form.full_name.trim() || !form.password.trim()) {
      setCreateError("Заполните логин, имя и пароль.");
      setCreateSuccess("");
      return;
    }

    try {
      setCreating(true);
      setCreateError("");
      setCreateSuccess("");
      await api.createWorker(session.token, {
        username: form.username.trim(),
        full_name: form.full_name.trim(),
        password: form.password,
        ...(form.employee_id.trim() ? { employee_id: form.employee_id.trim() } : {}),
        ...(form.qualification_id.trim() ? { qualification_id: form.qualification_id.trim() } : {}),
        ...(form.department_id.trim() ? { department_id: form.department_id.trim() } : {}),
      });
      setCreateSuccess("Работник создан.");
      setForm({
        username: "",
        full_name: "",
        password: "",
        employee_id: "",
        qualification_id: "OPERATOR-TU",
        department_id: "DEPT-UGP",
      });
      setReloadKey((current) => current + 1);
    } catch (error) {
      setCreateError(error.message || "Не удалось создать работника.");
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Исполнители"
        title="Сотрудники"
        subtitle="Агрегированная статистика по сотрудникам."
      />

      <div className="metrics-grid">
        <MetricCard label="Сотрудников в выборке" value={employees.length} />
        <MetricCard
          label="Активные исполнители"
          value={employees.filter((item) => item.active > 0).length}
          tone="info"
        />
      </div>

      <Card title="Создать работника" subtitle="">
        {createError ? <div className="inline-error">{createError}</div> : null}
        {createSuccess ? <div className="inline-note">{createSuccess}</div> : null}
        <form className="inline-form" onSubmit={createWorker}>
          <div className="inline-form-row">
            <label>
              <span>Логин</span>
              <input
                value={form.username}
                onChange={(event) => updateForm("username", event.target.value)}
                placeholder="worker-3"
              />
            </label>
            <label>
              <span>Имя</span>
              <input
                value={form.full_name}
                onChange={(event) => updateForm("full_name", event.target.value)}
                placeholder="Новый работник"
              />
            </label>
          </div>
          <div className="inline-form-row">
            <label>
              <span>Пароль</span>
              <input
                type="password"
                value={form.password}
                onChange={(event) => updateForm("password", event.target.value)}
                placeholder="Введите пароль"
              />
            </label>
            <label>
              <span>Табельный номер</span>
              <input
                value={form.employee_id}
                onChange={(event) => updateForm("employee_id", event.target.value)}
                placeholder="EMP-201"
              />
            </label>
          </div>
          <div className="inline-form-row">
            <label>
              <span>Квалификация</span>
              <input
                value={form.qualification_id}
                onChange={(event) => updateForm("qualification_id", event.target.value)}
                placeholder="OPERATOR-TU"
              />
            </label>
            <label>
              <span>Подразделение</span>
              <input
                value={form.department_id}
                onChange={(event) => updateForm("department_id", event.target.value)}
                placeholder="DEPT-UGP"
              />
            </label>
          </div>
          <div className="header-actions">
            <button type="submit" className="primary-button" disabled={creating}>
              {creating ? "Создание..." : "Создать работника"}
            </button>
          </div>
        </form>
      </Card>

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
