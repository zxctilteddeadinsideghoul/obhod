import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

const navigation = [
  { to: "/rounds", label: "Обходы" },
  { to: "/routes", label: "Маршруты" },
  { to: "/equipment", label: "Оборудование" },
  { to: "/employees", label: "Сотрудники" },
  { to: "/reports", label: "Сводки" },
  { to: "/analytics", label: "Аналитика" },
];

export function AppLayout() {
  const { profile, logout } = useAuth();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-block">
          <div className="brand-chip">ТОиР / Обход</div>
          <h1>Кабинет руководителя</h1>
          <p>Управление маршрутами, результатами обходов и отклонениями.</p>
        </div>

        <nav className="nav-list">
          {navigation.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="profile-mini">
            <span className="eyebrow">Текущий пользователь</span>
            <strong>{profile?.name || "Не авторизован"}</strong>
            <span>{profile?.role || "—"}</span>
          </div>

          <NavLink to="/profile" className="ghost-link">
            Профиль
          </NavLink>
          <button type="button" className="ghost-button" onClick={logout}>
            Выйти
          </button>
        </div>
      </aside>

      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
