import { isMockApiEnabled, mockApi } from "./mockData";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";
const DEV_BACKEND_TOKEN = import.meta.env.VITE_AUTH_TOKEN || "dev-admin-token";

function resolveToken(token) {
  if (isMockApiEnabled()) {
    return token;
  }

  if (!token || token === "mock-manager-token") {
    return DEV_BACKEND_TOKEN;
  }

  return token;
}

async function request(path, options = {}) {
  const token = resolveToken(options.token);
  const headers = {
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  if (options.body) {
    headers["Content-Type"] = "application/json";
  }

  let response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers,
      method: options.method || "GET",
      body: options.body ? JSON.stringify(options.body) : undefined,
    });
  } catch {
    const error = new Error("Сервер недоступен. Проверь адрес API и запущен ли backend.");
    error.status = 0;
    error.path = path;
    throw error;
  }

  if (!response.ok) {
    let detail = `HTTP ${response.status}`;
    try {
      const payload = await response.json();
      detail = payload.detail || payload.message || detail;
    } catch {
      // ignore invalid json
    }

    if (response.status === 502 && path.startsWith("/api/field")) {
      detail = "Сервис обходов сейчас недоступен: backend gateway вернул 502 Bad Gateway.";
    }

    const error = new Error(detail);
    error.status = response.status;
    error.path = path;
    throw error;
  }

  return response.status === 204 ? null : response.json();
}

function withQuery(path, params = {}) {
  const search = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === "") {
      return;
    }
    search.set(key, String(value));
  });

  const query = search.toString();
  return query ? `${path}?${query}` : path;
}

function notImplemented(message) {
  throw new Error(message);
}

export const api = {
  getCurrentUser(token) {
    if (isMockApiEnabled()) {
      return mockApi.getCurrentUser(token);
    }
    return request("/api/auth/me", { token });
  },
  listTasks(token) {
    if (isMockApiEnabled()) {
      return mockApi.listTasks(token);
    }
    return request("/api/field/tasks/my", { token });
  },
  getTaskDetail(token, roundId) {
    if (isMockApiEnabled()) {
      return mockApi.getTaskDetail(token, roundId);
    }
    return request(`/api/field/tasks/${roundId}`, { token });
  },
  startRound(token, roundId) {
    if (isMockApiEnabled()) {
      return mockApi.startRound(token, roundId);
    }
    return request(`/api/field/tasks/${roundId}/start`, {
      method: "POST",
      token,
    });
  },
  listEquipment(token) {
    if (isMockApiEnabled()) {
      return mockApi.listEquipment(token);
    }
    return request("/api/field/equipment", { token });
  },
  getEquipment(token, equipmentId) {
    if (isMockApiEnabled()) {
      return mockApi.getEquipment(token, equipmentId);
    }
    return request(`/api/field/equipment/${equipmentId}`, { token });
  },
  listRoutes(token) {
    if (isMockApiEnabled()) {
      return mockApi.listRoutes(token);
    }
    return request("/api/field/routes", { token });
  },
  getRoute(token, routeId) {
    if (isMockApiEnabled()) {
      return mockApi.getRoute(token, routeId);
    }
    return request(`/api/field/routes/${routeId}`, { token });
  },
  getReportsSummary(token) {
    if (isMockApiEnabled()) {
      return mockApi.getReportsSummary(token);
    }
    return request("/api/reports/analytics/summary", { token });
  },
  listRoundReports(token, params) {
    if (isMockApiEnabled()) {
      return mockApi.listRoundReports(token, params);
    }
    return request(withQuery("/api/reports/rounds", params), { token });
  },
  getEquipmentAnalytics(token, params) {
    if (isMockApiEnabled()) {
      return mockApi.getEquipmentAnalytics(token, params);
    }
    return request(withQuery("/api/reports/analytics/equipment", params), { token });
  },
  getEmployeeAnalytics(token, params) {
    if (isMockApiEnabled()) {
      return mockApi.getEmployeeAnalytics(token, params);
    }
    return request(withQuery("/api/reports/analytics/employees", params), { token });
  },
  updateEquipment() {
    return notImplemented("Редактирование оборудования пока недоступно.");
  },
  updateRoute() {
    return notImplemented("Редактирование маршрутов пока недоступно.");
  },
  updateRound() {
    return notImplemented("Редактирование обходов пока недоступно.");
  },
  register() {
    return notImplemented("Самостоятельная регистрация пока недоступна.");
  },
};
