import { createContext, useContext, useEffect, useMemo, useState } from "react";

const AUTH_STORAGE_KEY = "obhod.auth";
const AuthContext = createContext(null);

function readStoredSession() {
  try {
    const raw = localStorage.getItem(AUTH_STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }) {
  const [session, setSession] = useState(readStoredSession);
  const [profile, setProfile] = useState(() => readStoredSession()?.profile || null);
  const [initializing, setInitializing] = useState(true);

  useEffect(() => {
    setInitializing(false);
  }, []);

  const createMockSession = async (name) => {
    const nextProfile = {
      id: "chief-local",
      role: "MANAGER",
      name: name?.trim() || "Руководитель",
    };
    const nextSession = {
      mode: "mock",
      token: "mock-manager-token",
      label: "local-mock-session",
      profile: nextProfile,
    };
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
      login: createMockSession,
      register: createMockSession,
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
