import { useMemo, useState } from "react";
import { Link, Navigate, useLocation, useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export function AuthPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { mode = "login" } = useParams();
  const { login, register, isAuthenticated } = useAuth();
  const [name, setName] = useState("Руководитель");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const isRegisterMode = mode === "register";

  const nextPath = useMemo(() => location.state?.from?.pathname || "/", [location.state]);

  if (isAuthenticated) {
    return <Navigate to={nextPath} replace />;
  }

  const handleLogin = async (event) => {
    event.preventDefault();
    setBusy(true);
    setError("");

    try {
      await login(name || email || "Руководитель");
      navigate(nextPath, { replace: true });
    } catch (nextError) {
      setError(nextError.message || "Не удалось войти.");
    } finally {
      setBusy(false);
    }
  };

  const handleRegister = async (event) => {
    event.preventDefault();
    setBusy(true);
    setError("");

    try {
      await register(name || email || "Руководитель");
      navigate(nextPath, { replace: true });
    } catch (nextError) {
      setError(nextError.message || "Не удалось создать локальную сессию.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="auth-screen">
      <div className="auth-panel">
        <div className="auth-intro">
          <span className="brand-chip">Обход / web</span>
          <h1>Кабинет руководителя</h1>
          <p>Управление обходами, оборудованием, сводками и аналитикой в одном интерфейсе.</p>
        </div>

        <div className="auth-card">
          <div className="tab-strip">
            <Link className={!isRegisterMode ? "tab active" : "tab"} to="/auth/login">
              Вход
            </Link>
            <Link className={isRegisterMode ? "tab active" : "tab"} to="/auth/register">
              Регистрация
            </Link>
          </div>

          {!isRegisterMode ? (
            <form className="auth-form" onSubmit={handleLogin}>
              <label>
                Имя
                <input value={name} onChange={(event) => setName(event.target.value)} />
              </label>
              <label>
                Email
                <input
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="manager@company.local"
                />
              </label>
              <label>
                Пароль
                <input
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="Введите пароль"
                />
              </label>

              {error ? <div className="inline-error">{error}</div> : null}

              <button type="submit" className="primary-button" disabled={busy}>
                {busy ? "Вход..." : "Войти"}
              </button>
            </form>
          ) : (
            <form className="auth-form" onSubmit={handleRegister}>
              <label>
                Имя
                <input value={name} onChange={(event) => setName(event.target.value)} placeholder="Начальник участка" />
              </label>
              <label>
                Email
                <input
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="chief@company.local"
                />
              </label>
              <label>
                Пароль
                <input
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="Минимум 8 символов"
                />
              </label>

              {error ? <div className="inline-error">{error}</div> : null}

              <button type="submit" className="primary-button" disabled={busy}>
                {busy ? "Создание..." : "Зарегистрироваться"}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
