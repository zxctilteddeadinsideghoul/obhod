import { isMockApiEnabled, mockApi } from "./mockData";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.token ? { Authorization: `Bearer ${options.token}` } : {}),
      ...options.headers,
    },
    method: options.method || "GET",
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  if (!response.ok) {
    let detail = `HTTP ${response.status}`;
    try {
      const payload = await response.json();
      detail = payload.detail || payload.message || detail;
    } catch {
      // ignore invalid json
    }
    throw new Error(detail);
  }

  return response.status === 204 ? null : response.json();
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
