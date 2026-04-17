import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { api } from "../lib/api";

const AUTH_STORAGE_KEY = "obhod.auth";
const AuthContext = createContext(null);

function getDataSource() {
  return String(import.meta.env.VITE_DATA_SOURCE || "mock").toLowerCase();
}

function getBackendToken() {
  return import.meta.env.VITE_AUTH_TOKEN || "dev-admin-token";
}

function createBaseProfile(name) {
  return {
    id: "chief-local",
    role: "MANAGER",
    name: name?.trim() || "Руководитель",
  };
}

function normalizeSession(session) {
  if (!session) {
    return null;
  }

  if (getDataSource() !== "backend") {
    return session;
  }

  return {
    ...session,
    mode: "backend",
    token: getBackendToken(),
    label: "backend-session",
  };
}

function readStoredSession() {
  try {
    const raw = localStorage.getItem(AUTH_STORAGE_KEY);
    return raw ? normalizeSession(JSON.parse(raw)) : null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }) {
  const [session, setSession] = useState(readStoredSession);
  const [profile, setProfile] = useState(() => readStoredSession()?.profile || null);
  const [initializing, setInitializing] = useState(true);

  useEffect(() => {
    const bootstrap = async () => {
      const isBackendMode = getDataSource() === "backend";
      const normalized = readStoredSession();

      if (normalized) {
        localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(normalized));
        setSession(normalized);
        setProfile(normalized.profile || null);
        setInitializing(false);
        return;
      }

      if (!isBackendMode) {
        setInitializing(false);
        return;
      }

      const nextSession = normalizeSession({
        mode: "backend",
        token: getBackendToken(),
        label: "backend-session",
        profile: createBaseProfile("Руководитель"),
      });

      try {
        const backendProfile = await api.getCurrentUser(nextSession.token);
        nextSession.profile = {
          id: backendProfile.id || nextSession.profile.id,
          role: backendProfile.role || nextSession.profile.role,
          name: backendProfile.name || backendProfile.full_name || nextSession.profile.name,
        };
      } catch {
        // keep fallback profile for dev backend mode
      }

      localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(nextSession));
      setSession(nextSession);
      setProfile(nextSession.profile);
      setInitializing(false);
    };

    bootstrap();
  }, []);

  const createSession = async (name) => {
    const isBackendMode = getDataSource() === "backend";
    const baseProfile = createBaseProfile(name);
    const nextSession = normalizeSession({
      mode: isBackendMode ? "backend" : "mock",
      token: isBackendMode ? getBackendToken() : "mock-manager-token",
      label: isBackendMode ? "backend-session" : "local-mock-session",
      profile: baseProfile,
    });
    let nextProfile = baseProfile;

    if (isBackendMode) {
      try {
        const backendProfile = await api.getCurrentUser(nextSession.token);
        nextProfile = {
          id: backendProfile.id || baseProfile.id,
          role: backendProfile.role || baseProfile.role,
          name: backendProfile.name || backendProfile.full_name || baseProfile.name,
        };
      } catch {
        nextProfile = baseProfile;
      }
    }

    nextSession.profile = nextProfile;
    localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(nextSession));
    setSession(nextSession);
    setProfile(nextProfile);
  };

  const value = useMemo(
    () => ({
      initializing,
      isAuthenticated: Boolean(profile),
      session,
      profile,
      login: createSession,
      register: createSession,
      logout() {
        localStorage.removeItem(AUTH_STORAGE_KEY);
        setSession(null);
        setProfile(null);
      },
    }),
    [initializing, profile, session],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }

  return context;
}
