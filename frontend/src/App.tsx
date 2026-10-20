import * as React from "react";
import { AppShell } from "@/components/layout/AppShell";
import { ErrorBoundary } from "@/components/ui/ErrorBoundary";
import { AppRouter } from "./router";
import { LoginPage } from "@/features/auth/LoginPage";
import { parseNavHash, setNavHash } from "@/lib/navHash";

const VALID_ROUTES = new Set([
  "dashboard",
  "deals",
  "contacts",
  "omnichannel",
  "keypartners",
  "dentgo",
  "video_sos",
  "contracts",
  "intelligence",
  "market_intel",
  "analytics",
  "scheduling",
  "rbac",
  "support",
  "settings",
  "scoring",
  "marketing",
  "imaging",
]);

function getInitialRouteFromHash(): string {
  if (typeof window === "undefined") return "deals";
  const { route } = parseNavHash(window.location.hash);
  if (route && VALID_ROUTES.has(route)) {
    return route;
  }
  return "deals";
}

function getInitialFacilityFromHash(): string | undefined {
  if (typeof window === "undefined") return undefined;
  return parseNavHash(window.location.hash).facility;
}

export function App() {
  const [authToken, setAuthToken] = React.useState<string | null>(() => {
    if (typeof window === "undefined") return "demo-token";
    return localStorage.getItem("revnaut_auth_token");
  });
  const [activeNav, setActiveNav] = React.useState<string>(getInitialRouteFromHash);
  const [activeFacility, setActiveFacility] = React.useState<string | undefined>(
    getInitialFacilityFromHash
  );
  const [currentUserId, setCurrentUserId] = React.useState<string>(() => {
    if (typeof window === "undefined") return "usr-director-br";
    return (
      localStorage.getItem("revnaut_active_user_id") ||
      localStorage.getItem("revnaut_user_id") ||
      "usr-director-br"
    );
  });

  const handleLogout = React.useCallback(() => {
    try {
      fetch("/api/v1/auth/logout", { method: "POST" });
    } catch {
      // Ignora falha de rede ao deslogar
    }
    localStorage.removeItem("revnaut_auth_token");
    localStorage.removeItem("revnaut_user");
    setAuthToken(null);
    if (typeof window !== "undefined") {
      window.location.hash = "";
    }
  }, []);

  React.useEffect(() => {
    const onSessionExpired = () => {
      localStorage.removeItem("revnaut_user");
      setAuthToken(null);
    };
    window.addEventListener("revnaut:session_expired", onSessionExpired);
    return () => window.removeEventListener("revnaut:session_expired", onSessionExpired);
  }, []);

  const handleLoginSuccess = React.useCallback((token: string, user: any) => {
    setAuthToken(token);
    if (user?.id) {
      setCurrentUserId(user.id);
    }
  }, []);

  React.useEffect(() => {
    const onHashChange = () => {
      const { route, facility } = parseNavHash(window.location.hash);
      const parsed = route && VALID_ROUTES.has(route) ? route : "deals";
      setActiveNav((prev) => (prev !== parsed ? parsed : prev));
      setActiveFacility((prev) => (prev !== facility ? facility : prev));
    };
    window.addEventListener("hashchange", onHashChange);
    window.addEventListener("popstate", onHashChange);
    return () => {
      window.removeEventListener("hashchange", onHashChange);
      window.removeEventListener("popstate", onHashChange);
    };
  }, []);

  const handleNavigate = React.useCallback((routeId: string, facility?: string) => {
    setActiveNav(routeId);
    setActiveFacility(facility);
    setNavHash(routeId, facility);
  }, []);

  if (!authToken) {
    return <LoginPage onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <AppShell
      activeNav={activeNav}
      activeFacility={activeFacility}
      onNavigate={handleNavigate}
      currentUserId={currentUserId}
      onSelectUser={setCurrentUserId}
      onLogout={handleLogout}
    >
      <ErrorBoundary key={`${activeNav}:${activeFacility ?? ""}`} onReset={() => window.location.reload()}>
        <AppRouter
          currentRoute={activeNav}
          initialFacility={activeFacility}
          onNavigate={handleNavigate}
        />
      </ErrorBoundary>
    </AppShell>
  );
}

export default App;
