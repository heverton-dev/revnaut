import * as React from "react";
import { AppShell } from "@/components/layout/AppShell";
import { ErrorBoundary } from "@/components/ui/ErrorBoundary";
import { AppRouter } from "./router";
import { LoginPage } from "@/features/auth/LoginPage";

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
  const raw = window.location.hash.replace(/^#!?\/?/, "").split("?")[0].trim();
  if (raw && VALID_ROUTES.has(raw)) {
    return raw;
  }
  return "deals";
}

export function App() {
  const [authToken, setAuthToken] = React.useState<string | null>(() => {
    if (typeof window === "undefined") return "demo-token";
    return localStorage.getItem("revnaut_auth_token");
  });
  const [activeNav, setActiveNav] = React.useState<string>(getInitialRouteFromHash);
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

  const handleLoginSuccess = React.useCallback((token: string, user: any) => {
    setAuthToken(token);
    if (user?.id) {
      setCurrentUserId(user.id);
    }
  }, []);

  React.useEffect(() => {
    const onHashChange = () => {
      const parsed = getInitialRouteFromHash();
      setActiveNav((prev) => (prev !== parsed ? parsed : prev));
    };
    window.addEventListener("hashchange", onHashChange);
    window.addEventListener("popstate", onHashChange);
    return () => {
      window.removeEventListener("hashchange", onHashChange);
      window.removeEventListener("popstate", onHashChange);
    };
  }, []);

  const handleNavigate = React.useCallback((routeId: string) => {
    setActiveNav(routeId);
    if (typeof window !== "undefined") {
      const targetHash = `#!/${routeId}`;
      if (window.location.hash !== targetHash) {
        window.location.hash = targetHash;
      }
    }
  }, []);

  if (!authToken) {
    return <LoginPage onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <AppShell
      activeNav={activeNav}
      onNavigate={handleNavigate}
      currentUserId={currentUserId}
      onSelectUser={setCurrentUserId}
      onLogout={handleLogout}
    >
      <ErrorBoundary key={activeNav} onReset={() => window.location.reload()}>
        <AppRouter currentRoute={activeNav} onNavigate={handleNavigate} />
      </ErrorBoundary>
    </AppShell>
  );
}

export default App;
