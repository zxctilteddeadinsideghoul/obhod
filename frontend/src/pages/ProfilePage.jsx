import { useAuth } from "../auth/AuthContext";
import { Card, PageHeader } from "../components/Ui";

export function ProfilePage() {
  const { profile, session } = useAuth();

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Учетная запись"
        title="Профиль"
        subtitle="Данные текущего пользователя и параметры активной сессии."
      />

      <Card title="Текущая сессия">
        <div className="detail-grid">
          <div>
            <span className="eyebrow">Имя</span>
            <strong>{profile?.name || "—"}</strong>
          </div>
          <div>
            <span className="eyebrow">Роль</span>
            <strong>{profile?.role || "—"}</strong>
          </div>
          <div>
            <span className="eyebrow">ID</span>
            <strong>{profile?.id || "—"}</strong>
          </div>
          <div>
            <span className="eyebrow">Метка сессии</span>
            <strong>{session?.label || "—"}</strong>
          </div>
        </div>
      </Card>
    </div>
  );
}
