import * as React from "react";
import {
  Search,
  Bell,
  CheckCircle,
  Command,
  Menu,
  X,
  PanelLeftClose,
  PanelLeftOpen,
  ArrowRight,
  LogOut,
  AlertCircle,
  ChevronRight,
} from "lucide-react";
import { Avatar } from "@/components/ui/Avatar";
import { cn } from "@/lib/utils";
import { getActiveUserId, setActiveUserId, ToastPayload, dispatchToast } from "@/lib/api";
import { NotificationCenter } from "@/components/layout/NotificationCenter";
import {
  ROLE_WORKSPACES,
  ROLE_ID_TO_WORKSPACE,
  resolveRoleConfig,
  buildNavSections,
  flattenNavItems,
  type NavItem,
  type RoleWorkspaceConfig,
} from "@/components/layout/navConfig";
import { setNavHash } from "@/lib/navHash";
import {
  accessMeToRoleConfig,
  checkAccess,
  fetchAccessMe,
  type AccessMeResponse,
} from "@/lib/accessApi";

export type { NavItem, RoleWorkspaceConfig };
export { ROLE_WORKSPACES, resolveRoleConfig };

export interface AuthUserItem {
  id: string;
  name: string;
  email: string;
  role: string;
  account_id?: string;
  team_id?: string | null;
  is_superadmin?: boolean | number;
  role_id?: string;
}

export interface AppShellProps {
  children: React.ReactNode;
  activeNav?: string;
  activeFacility?: string;
  onNavigate?: (id: string, facility?: string) => void;
  userRole?: string;
  userName?: string;
  accountName?: string;
  currentUserId?: string;
  onSelectUser?: (userId: string) => void;
  onLogout?: () => void;
}

export function AppShell({
  children,
  activeNav = "deals",
  activeFacility,
  onNavigate,
  userRole = "Super Admin",
  userName = "Heverton Eduardo Peres",
  accountName = "Sales Rocket",
  currentUserId: propUserId,
  onSelectUser,
  onLogout,
}: AppShellProps) {
  const [isCommandOpen, setIsCommandOpen] = React.useState(false);
  const [searchQuery, setSearchQuery] = React.useState("");
  const [isMobileDrawerOpen, setIsMobileDrawerOpen] = React.useState(false);
  const [isCompactSidebar, setIsCompactSidebar] = React.useState(false);
  const [isNotificationsOpen, setIsNotificationsOpen] = React.useState(false);
  const [unreadNotifCount, setUnreadNotifCount] = React.useState(0);
  const [expandedGroups, setExpandedGroups] = React.useState<Record<string, boolean>>({});

  const [selectedUserId, setSelectedUserId] = React.useState<string>(
    propUserId || getActiveUserId()
  );
  const [currentUserProfile, setCurrentUserProfile] = React.useState<AuthUserItem | null>(null);
  const [accessMe, setAccessMe] = React.useState<AccessMeResponse | null>(null);
  const [availableUsers, setAvailableUsers] = React.useState<AuthUserItem[]>([]);
  const [toasts, setToasts] = React.useState<(ToastPayload & { id: string })[]>([]);
  const [healthStatus, setHealthStatus] = React.useState<{
    status: string;
    sqlite_journal_mode: string;
    accounts_online: number;
  } | null>(null);

  React.useEffect(() => {
    const handleToastEvent = (e: Event) => {
      const custom = e as CustomEvent<ToastPayload>;
      if (custom.detail) {
        const id = String(Date.now() + Math.random());
        const newToast = { ...custom.detail, id };
        setToasts((prev) => [...prev.slice(-4), newToast]);
        setTimeout(() => {
          setToasts((prev) => prev.filter((t) => t.id !== id));
        }, 5000);
      }
    };
    window.addEventListener("revnaut:toast", handleToastEvent);
    return () => window.removeEventListener("revnaut:toast", handleToastEvent);
  }, []);

  React.useEffect(() => {
    if (propUserId && propUserId !== selectedUserId) {
      setSelectedUserId(propUserId);
      setActiveUserId(propUserId);
    }
  }, [propUserId, selectedUserId]);

  // Atalho Cmd+K / Ctrl+K e Escape
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setIsCommandOpen((prev) => !prev);
      } else if (e.key === "Escape") {
        setIsCommandOpen(false);
        setIsMobileDrawerOpen(false);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  // Health Check real GET /api/v1/health
  React.useEffect(() => {
    let active = true;
    fetch("/api/v1/health")
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (active && data) {
          setHealthStatus(data);
        }
      })
      .catch(() => {});
    return () => {
      active = false;
    };
  }, []);

  // Context Switcher real GET /api/v1/auth/me e GET /api/v1/auth/users
  React.useEffect(() => {
    let active = true;
    const headers = { "X-User-Id": selectedUserId };
    Promise.all([
      fetch("/api/v1/auth/me", { headers }).then((r) => (r.ok ? r.json() : null)),
      fetch("/api/v1/auth/users", { headers }).then((r) => (r.ok ? r.json() : [])),
    ])
      .then(([meData, usersData]) => {
        if (!active) return;
        if (Array.isArray(usersData) && usersData.length > 0) {
          setAvailableUsers(usersData);
          // Simulated profile from the user list wins — /auth/me may fall back to the
          // session owner when X-User-Id impersonation is denied or incomplete.
          const match = usersData.find((u: AuthUserItem) => u.id === selectedUserId);
          if (match) {
            setCurrentUserProfile(match);
          }
        }
        // Only trust /auth/me when it matches the selected identity
        if (meData && meData.id && meData.id === selectedUserId && !usersData?.find?.((u: AuthUserItem) => u.id === selectedUserId)) {
          setCurrentUserProfile(meData);
        }
        // Phase 3: grants from DB (falls back to navConfig if API unavailable)
        return fetchAccessMe().then((access) => {
          if (!active) return;
          if (access && access.user_id && access.user_id === selectedUserId) {
            setAccessMe(access);
          } else if (access && access.user_id && access.user_id !== selectedUserId) {
            // identity mismatch — keep last or clear so seed config is used
            setAccessMe(null);
          } else {
            setAccessMe(null);
          }
        });
      })
      .catch(() => {});
    return () => {
      active = false;
    };
  }, [selectedUserId]);

  const [showAllModules, setShowAllModules] = React.useState(false);

  const displayUserName = currentUserProfile?.name || userName;
  const displayUserRole = currentUserProfile?.role || userRole;

  const currentRoleConfig = React.useMemo(() => {
    // Prefer DB grants (phase 3); fall back to navConfig seed by role_id/label
    if (accessMe && accessMe.routes.length > 0 && accessMe.user_id === selectedUserId) {
      return accessMeToRoleConfig(accessMe);
    }
    return resolveRoleConfig(
      currentUserProfile?.role || userRole,
      currentUserProfile?.role_id ?? null
    );
  }, [
    accessMe,
    selectedUserId,
    currentUserProfile?.role,
    currentUserProfile?.role_id,
    userRole,
  ]);

  /** Only Diretoria/Superadmin may expand beyond their workspace routes. */
  const canSeeAllModules = currentRoleConfig.roleKey === "superadmin";

  // Hard RBAC: non-admin roles can never keep "all modules" mode
  React.useEffect(() => {
    if (!canSeeAllModules && showAllModules) {
      setShowAllModules(false);
    }
  }, [canSeeAllModules, showAllModules]);

  /**
   * Route + facility guard.
   * Source of truth: GET /access/me (banco). Fallback: navConfig seed.
   */
  React.useEffect(() => {
    if (!activeNav) return;

    const dbCheck = checkAccess(accessMe, activeNav, activeFacility);
    const seedAllowed = new Set(currentRoleConfig.visibleRoutes).has(activeNav);
    const routeOk = accessMe ? dbCheck.routeAllowed : seedAllowed;

    if (!routeOk) {
      // Rota fora do grant do banco/seed → landing
      const landing = accessMe?.landing_route || currentRoleConfig.defaultLandingRoute;
      const landingFacility =
        accessMe?.landing_facility ?? currentRoleConfig.defaultFacility;
      const nextHash = landingFacility
        ? `#!/${landing}?f=${landingFacility}`
        : `#!/${landing}`;
      if (typeof window !== "undefined" && window.location.hash !== nextHash) {
        window.location.hash = nextHash;
      }
      if (onNavigate) onNavigate(landing, landingFacility);
      dispatchToast({
        type: "warning",
        title: "Acesso restrito",
        message: `Este endereço não está liberado para ${currentRoleConfig.displayName}.`,
      });
      return;
    }

    // Rota ok: se a facility do hash não está no grant, troca pela primeira liberada
    if (accessMe && !dbCheck.ok) {
      const fixed = dbCheck.facility;
      const nextHash = fixed ? `#!/${activeNav}?f=${fixed}` : `#!/${activeNav}`;
      if (typeof window !== "undefined" && window.location.hash !== nextHash) {
        window.location.hash = nextHash;
      }
      if (onNavigate) onNavigate(activeNav, fixed);
      dispatchToast({
        type: "warning",
        title: "Aba não liberada",
        message: "Abrimos a primeira opção disponível deste módulo.",
      });
      return;
    }

    // Rota ok e facility ok/ausente: normaliza ?f= quando o grant tem facilities
    if (accessMe && dbCheck.facility !== activeFacility) {
      const nextHash = dbCheck.facility
        ? `#!/${activeNav}?f=${dbCheck.facility}`
        : `#!/${activeNav}`;
      if (typeof window !== "undefined" && window.location.hash !== nextHash) {
        window.location.hash = nextHash;
      }
      if (onNavigate) onNavigate(activeNav, dbCheck.facility);
    }
  }, [
    activeNav,
    activeFacility,
    accessMe,
    currentRoleConfig,
    onNavigate,
  ]);

  const navSections = React.useMemo(() => {
    // Non-admin: never honor showAllModules — hard RBAC filter only
    const effectiveShowAll = canSeeAllModules && showAllModules;
    const built = buildNavSections(currentRoleConfig, effectiveShowAll);
    if (built.length === 0 || built.every((s) => s.items.length === 0)) {
      return buildNavSections(
        ROLE_ID_TO_WORKSPACE["role-field"] ?? ROLE_WORKSPACES.field_sales,
        false
      );
    }
    return built;
  }, [currentRoleConfig, showAllModules, canSeeAllModules]);

  const allNavItems = React.useMemo(() => flattenNavItems(navSections), [navSections]);

  const quickCommands = React.useMemo(() => {
    const allowed = new Set(currentRoleConfig.visibleRoutes);
    const all = [
      { id: "deals", label: "Criar Nova Negociação", section: "Ação Rápida", shortcut: "D" },
      { id: "contacts", label: "Cadastrar Dentista ou Clínica", section: "Ação Rápida", shortcut: "C" },
      { id: "dentgo", label: "Solicitar Entrega Rápida (45 min)", section: "Ação Rápida", shortcut: "G", facility: "orders" },
      { id: "keypartners", label: "Consultar Maletas em Consignação", section: "Ação Rápida", shortcut: "K" },
      { id: "contracts", label: "Gerar Proposta Comercial ou Contrato", section: "Ação Rápida", shortcut: "T" },
      { id: "support", label: "Abrir Chamado Pós-Cirúrgico", section: "Ação Rápida", shortcut: "A" },
      { id: "analytics", label: "Consultar Relatórios e Indicadores", section: "Ação Rápida", shortcut: "B" },
      { id: "logout", label: "Encerrar Sessão (Logout)", section: "Sessão & Conta", shortcut: "Q" },
    ];
    if (canSeeAllModules) return all;
    return all.filter((c) => c.id === "logout" || allowed.has(c.id));
  }, [currentRoleConfig, canSeeAllModules]);

  const filteredCommandItems = React.useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    const combined = [
      ...allNavItems.map((it) => ({
        id: it.id,
        facility: it.facility,
        label: `Ir para: ${it.label}`,
        section: it.section,
        shortcut: "",
      })),
      ...quickCommands,
    ];
    if (!q) return combined;
    return combined.filter(
      (item) =>
        item.label.toLowerCase().includes(q) ||
        item.id.toLowerCase().includes(q) ||
        item.section.toLowerCase().includes(q)
    );
  }, [allNavItems, quickCommands, searchQuery]);

  // Accordion: expand only the group of the active route when it CHANGES.
  // Never force-reopen if the user collapsed the same submenu.
  const lastActiveNavKeyRef = React.useRef<string | null>(null);
  React.useEffect(() => {
    const key = `${activeNav}|${activeFacility ?? ""}`;
    if (lastActiveNavKeyRef.current === key) return;
    lastActiveNavKeyRef.current = key;

    let parentId: string | null = null;
    for (const sec of navSections) {
      for (const item of sec.items) {
        if (!item.children?.length) continue;
        const hit = item.children.some(
          (c) => c.id === activeNav && (c.facility === activeFacility || (!activeFacility && c === item.children?.[0]))
        );
        if (hit || item.id === activeNav) {
          parentId = item.id;
          break;
        }
      }
      if (parentId) break;
    }

    // Accordion: only one submenu open
    setExpandedGroups((prev) => {
      const next: Record<string, boolean> = {};
      if (parentId) next[parentId] = true;
      const same =
        Object.keys(prev).length === Object.keys(next).length &&
        Object.keys(next).every((k) => prev[k] === next[k]);
      return same ? prev : next;
    });
  }, [activeNav, activeFacility, navSections]);

  const handleSelectNav = (routeId: string, facility?: string) => {
    if (routeId === "logout") {
      setIsMobileDrawerOpen(false);
      setIsCommandOpen(false);
      setSearchQuery("");
      if (onLogout) onLogout();
      return;
    }

    const check = checkAccess(accessMe, routeId, facility);
    const seedOk = currentRoleConfig.visibleRoutes.includes(routeId);
    const routeOk = accessMe ? check.routeAllowed : seedOk;

    if (!routeOk) {
      dispatchToast({
        type: "warning",
        title: "Acesso restrito",
        message: `Este módulo não está liberado para ${currentRoleConfig.displayName}.`,
      });
      return;
    }

    // Facility corrigida pelo grant do banco (1ª liberada quando inválida)
    const nextFacility = accessMe ? check.facility : facility;

    setNavHash(routeId, nextFacility);
    if (onNavigate) {
      onNavigate(routeId, nextFacility);
    }
    setIsMobileDrawerOpen(false);
    setIsCommandOpen(false);
    setSearchQuery("");
  };

  /** Pure expand/collapse. Accordion: opening one closes the others. */
  const toggleGroup = (itemId: string) => {
    setExpandedGroups((prev) => {
      const isOpen = prev[itemId] === true;
      if (isOpen) return { ...prev, [itemId]: false };
      const next: Record<string, boolean> = { [itemId]: true };
      return next;
    });
  };

  const handleUserChange = (newUserId: string) => {
    setSelectedUserId(newUserId);
    setActiveUserId(newUserId);
    const targetUser = availableUsers.find((u) => u.id === newUserId);
    if (targetUser) {
      setCurrentUserProfile(targetUser);
      // Profile switch always re-applies hard RBAC focus (no leftover "all modules")
      setShowAllModules(false);
      const newRole = resolveRoleConfig(targetUser.role, targetUser.role_id ?? null);
      if (!newRole.visibleRoutes.includes(activeNav)) {
        handleSelectNav(newRole.defaultLandingRoute, newRole.defaultFacility);
      }
    }
    if (onSelectUser) {
      onSelectUser(newUserId);
    }
  };

  return (
    <div className="flex h-screen h-[100dvh] max-h-screen w-full bg-surface-bg text-text-main overflow-hidden font-sans">
      {/* Backdrop do Drawer Mobile/Tablet (< 1024px) */}
      {isMobileDrawerOpen && (
        <div
          className="fixed inset-0 z-40 bg-surface-overlay backdrop-blur-sm transition-all duration-200 animate-in fade-in-0 lg:hidden"
          onClick={() => setIsMobileDrawerOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Sidebar Lateral RBAC Dual (Fixa e Imóvel ao Scroll da Tela) */}
      <aside
        className={cn(
          "bg-surface-sidebar text-text-inverse flex flex-col justify-between transition-all duration-200 z-40 shrink-0 h-screen h-[100dvh] max-h-screen sticky top-0 left-0 self-start overflow-hidden",
          isMobileDrawerOpen
            ? "max-lg:fixed max-lg:inset-y-0 max-lg:left-0 max-lg:w-64 max-lg:border-r max-lg:border-border max-lg:shadow-modal"
            : "max-lg:fixed max-lg:left-0 max-lg:top-0 max-lg:w-0 max-lg:h-0 max-lg:overflow-hidden max-lg:border-0",
          isCompactSidebar ? "lg:w-16 lg:border-r lg:border-border" : "lg:w-64 lg:border-r lg:border-border"
        )}
      >
        <div className={cn("flex flex-col h-full justify-between", isCompactSidebar ? "w-64 lg:w-16" : "w-64")}>
          <div className="min-h-0 flex-1 flex flex-col">
            {/* Logo Brand Header - Livre de Sobreposições */}
            <div className={cn("h-16 flex items-center border-b border-white/10 shrink-0", isCompactSidebar ? "justify-center px-0" : "justify-between px-4 gap-2")}>
              <div className={cn("flex items-center min-w-0", isCompactSidebar ? "justify-center" : "gap-2.5")}>
                <div className="h-8 w-8 rounded-md bg-brand-primary flex items-center justify-center font-bold text-sm text-text-inverse shadow-sm shrink-0">
                  RN
                </div>
                {!isCompactSidebar && (
                  <div className="flex flex-col min-w-0">
                    <span className="font-bold text-sm tracking-wide text-white truncate">RevNault</span>
                    <span className="text-[10px] text-text-muted uppercase tracking-wider truncate">
                      {accountName}
                    </span>
                  </div>
                )}
              </div>

              <button
                type="button"
                onClick={() => setIsMobileDrawerOpen(false)}
                className="lg:hidden p-1.5 rounded-md text-white/70 hover:text-white hover:bg-white/10"
                aria-label="Fechar menu"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {/* Indicador de Perfil Operacional Focado */}
            {!isCompactSidebar && (
              <div className="px-3 py-2.5 shrink-0">
                <div className="flex items-center justify-between px-3 py-1.5 rounded-md bg-white/5 border border-white/10">
                  <div className="flex items-center gap-2 min-w-0">
                    <span className="h-2 w-2 rounded-full bg-status-success shrink-0" />
                    <span className="text-xs font-medium text-white/90 truncate">
                      Área de Trabalho: {currentRoleConfig.displayName}
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Navegação Vertical pelas Rotas com RBAC Cognitivo */}
            <nav className={cn("py-2 space-y-4 overflow-y-auto flex-1", isCompactSidebar ? "px-2" : "px-2.5")}>
              {navSections.map((sec) => (
                <div key={sec.title}>
                  {!isCompactSidebar ? (
                    <div className="px-2.5 mb-1 text-[10px] font-semibold uppercase tracking-wider text-white/40">
                      {sec.title}
                    </div>
                  ) : (
                    <div className="my-2 border-t border-white/10 mx-1" />
                  )}
                  <div className="space-y-1">
                    {sec.items.map((item) => {
                      const Icon = item.icon;
                      const hasChildren = Boolean(item.children?.length);
                      const isExpanded = hasChildren && expandedGroups[item.id] === true;
                      const isActive = activeNav === item.id;

                      return (
                        <div key={`${item.id}-${item.label}`}>
                          <button
                            type="button"
                            title={item.label}
                            onClick={() => {
                              if (hasChildren) {
                                // Expand/collapse only — never force navigate when closing
                                if (isExpanded) {
                                  toggleGroup(item.id);
                                  return;
                                }
                                toggleGroup(item.id);
                                // Opening from another route: land on first subdestination
                                if (!isActive) {
                                  handleSelectNav(item.id, item.children?.[0]?.facility);
                                }
                                return;
                              }
                              handleSelectNav(item.id, undefined);
                            }}
                            className={cn(
                              "rounded-md text-xs font-medium transition-colors flex items-center",
                              isCompactSidebar
                                ? "w-10 h-10 mx-auto justify-center p-0"
                                : "w-full justify-between px-2.5 py-2 text-left",
                              isActive
                                ? "bg-brand-primary text-white shadow-sm"
                                : "text-white/70 hover:text-white hover:bg-surface-sidebar-hover"
                            )}
                          >
                            <div className={cn("flex items-center min-w-0", isCompactSidebar ? "justify-center" : "gap-2.5")}>
                              <Icon className="h-4 w-4 shrink-0 stroke-[1.8]" />
                              {!isCompactSidebar && <span className="truncate">{item.label}</span>}
                            </div>
                            {!isCompactSidebar && hasChildren && (
                              <ChevronRight
                                className={cn(
                                  "h-3.5 w-3.5 shrink-0 transition-transform",
                                  isExpanded && "rotate-90"
                                )}
                              />
                            )}
                            {!isCompactSidebar && !hasChildren && item.badge && (
                              <span
                                className={cn(
                                  "text-[10px] px-1.5 py-0.5 rounded-full font-semibold shrink-0 whitespace-nowrap",
                                  isActive ? "bg-white/20 text-white" : "bg-white/10 text-white/80"
                                )}
                              >
                                {item.badge}
                              </span>
                            )}
                          </button>
                          {hasChildren && isExpanded && (
                            <div
                              className={cn(
                                isCompactSidebar
                                  ? "mt-0.5 space-y-0.5"
                                  : "ml-5 mt-0.5 space-y-0.5 border-l border-white/10 pl-2"
                              )}
                            >
                              {(item.children ?? []).map((child) => {
                                const ChildIcon = child.icon;
                                const childActive =
                                  activeNav === child.id &&
                                  (child.facility === activeFacility ||
                                    (!activeFacility && child === item.children?.[0]));
                                return (
                                  <button
                                    key={`${child.id}-${child.facility ?? "root"}-${child.label}`}
                                    type="button"
                                    title={child.label}
                                    aria-label={child.label}
                                    aria-current={childActive ? "page" : undefined}
                                    onClick={() => handleSelectNav(child.id, child.facility)}
                                    className={cn(
                                      "rounded-md text-[11px] font-medium transition-colors flex items-center",
                                      isCompactSidebar
                                        ? "w-10 h-8 mx-auto justify-center p-0"
                                        : "w-full gap-2 px-2 py-1.5 text-left",
                                      childActive
                                        ? "bg-white/15 text-white"
                                        : "text-white/55 hover:text-white hover:bg-white/10"
                                    )}
                                  >
                                    <ChildIcon className="h-3.5 w-3.5 shrink-0 stroke-[1.8]" />
                                    {!isCompactSidebar && <span className="truncate">{child.label}</span>}
                                  </button>
                                );
                              })}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </nav>
          </div>

          {/* Footer do Usuário e Seletor de Perfil na Sidebar */}
          <div className={cn("border-t border-white/10 shrink-0 space-y-2", isCompactSidebar ? "p-2" : "p-2.5")}>
            <div className={cn("flex items-center rounded-md bg-white/5", isCompactSidebar ? "w-10 h-10 mx-auto justify-center p-0" : "justify-between gap-1.5 px-2 py-1.5")}>
              <div className={cn("flex items-center min-w-0", isCompactSidebar ? "justify-center" : "gap-2 flex-1")}>
                <Avatar
                  fallback={displayUserName}
                  size="sm"
                  className="border-white/20 text-white bg-brand-primary shrink-0"
                />
                {!isCompactSidebar && (
                  <div className="flex flex-col min-w-0 flex-1">
                    <span className="text-xs font-semibold text-white truncate">{displayUserName}</span>
                    <span className="text-[10px] text-white/60 truncate">{displayUserRole}</span>
                  </div>
                )}
              </div>

            </div>

            {!isCompactSidebar && availableUsers.length > 0 && (
              <div className="px-1 space-y-2">
                <div>
                  <label className="block text-[10px] uppercase tracking-wider text-white/40 mb-1">
                    Simular Visão do Perfil
                  </label>
                  <select
                    aria-label="Simular Visão do Perfil"
                    value={selectedUserId}
                    onChange={(e) => handleUserChange(e.target.value)}
                    className="w-full rounded border border-white/15 bg-white/10 px-2 py-1 text-[11px] text-white focus:outline-none"
                  >
                    {availableUsers.map((u) => (
                      <option key={u.id} value={u.id} className="text-text-main bg-surface-card">
                        {u.name} ({u.role})
                      </option>
                    ))}
                  </select>
                </div>

                {canSeeAllModules && (
                  <button
                    type="button"
                    onClick={() => setShowAllModules((prev) => !prev)}
                    className="w-full text-center py-1 text-[10px] text-white/60 hover:text-white transition-colors border border-white/10 rounded bg-white/5"
                  >
                    {showAllModules ? "Modo Focado no Cargo" : "Mostrar todos os módulos (18)"}
                  </button>
                )}
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* Área Principal de Conteúdo */}
      <div className="flex flex-col flex-1 min-w-0 h-screen h-[100dvh] max-h-screen overflow-hidden">
        {/* Topbar Superior */}
        <header className="sticky top-0 z-30 h-14 sm:h-16 border-b border-border bg-surface-card px-3 sm:px-6 flex items-center justify-between gap-2 shrink-0 w-full shadow-2xs">
          <div className="flex items-center gap-2 min-w-0 flex-1">
            {/* Botão Hamburger para Mobile/Tablet */}
            <button
              type="button"
              onClick={() => setIsMobileDrawerOpen(true)}
              className="lg:hidden inline-flex items-center justify-center p-2 rounded-md border border-border bg-surface-bg text-text-main hover:bg-surface-card shrink-0"
              aria-label="Abrir menu de navegação"
            >
              <Menu className="h-4 w-4" />
            </button>

            {/* Botão Desktop na Topbar para Recolher/Expandir Menu Lateral */}
            <button
              type="button"
              onClick={() => setIsCompactSidebar((prev) => !prev)}
              className="hidden lg:inline-flex items-center justify-center p-2 rounded-md border border-border bg-surface-bg text-text-secondary hover:text-text-main hover:bg-surface-card transition-colors shrink-0"
              title={isCompactSidebar ? "Expandir menu lateral" : "Recolher menu lateral"}
              aria-label={isCompactSidebar ? "Expandir menu lateral" : "Recolher menu lateral"}
            >
              {isCompactSidebar ? (
                <PanelLeftOpen className="h-4 w-4" />
              ) : (
                <PanelLeftClose className="h-4 w-4" />
              )}
            </button>

            {/* Campo de Busca & Command Palette Trigger */}
            <button
              type="button"
              onClick={() => setIsCommandOpen(true)}
              className="flex items-center gap-2 px-2.5 sm:px-3 py-1.5 rounded-md border border-border bg-surface-bg text-text-secondary hover:text-text-main text-xs transition-colors flex-1 max-w-xs sm:max-w-md min-w-0 justify-between"
            >
              <div className="flex items-center gap-2 min-w-0">
                <Search className="h-3.5 w-3.5 text-text-muted shrink-0" />
                <span className="truncate">Buscar cliente, negociação, maleta ou funcionalidade...</span>
              </div>
              <kbd className="hidden sm:inline-flex items-center gap-0.5 rounded border border-border bg-surface-card px-1.5 py-0.5 text-[10px] text-text-muted font-mono shrink-0">
                <Command className="h-2.5 w-2.5" /> K
              </kbd>
            </button>
          </div>

          {/* Ações Rápidas do Topbar */}
          <div className="flex items-center gap-2 shrink-0">
            {canSeeAllModules && (
              <button
                type="button"
                onClick={() => setShowAllModules((prev) => !prev)}
                className={cn(
                  "hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-medium border transition-colors cursor-pointer",
                  showAllModules
                    ? "bg-brand-primary text-white border-brand-primary"
                    : "bg-surface-bg text-text-secondary border-border hover:text-text-main"
                )}
                title="Somente Diretoria: alternar entre workspace do cargo e todos os módulos"
              >
                {showAllModules ? "Visão Completa" : "Focado no Cargo"}
              </button>
            )}

            <div
              className="flex items-center gap-1.5 px-2 sm:px-2.5 py-1 rounded-full bg-status-success-subtle text-status-success text-[11px] sm:text-xs font-medium border border-status-success/20 whitespace-nowrap shrink-0"
              title={healthStatus ? `Status: ${healthStatus.status} • SQLite WAL` : "Sistema operacional e sincronizado"}
            >
              <CheckCircle className="h-3.5 w-3.5 shrink-0" />
              <span>Sistema Online</span>
            </div>

            <div className="relative">
              <button
                type="button"
                onClick={() => setIsNotificationsOpen((prev) => !prev)}
                className={cn(
                  "relative p-2 rounded-md transition-colors shrink-0 cursor-pointer",
                  isNotificationsOpen
                    ? "bg-surface-card text-brand-primary border border-border"
                    : "text-text-secondary hover:text-text-main hover:bg-surface-bg"
                )}
                aria-label="Notificações e Comandos"
                aria-expanded={isNotificationsOpen}
                title="Central de Notificações Dinâmica por Cargo"
              >
                <Bell className="h-4 w-4" />
                {unreadNotifCount > 0 && (
                  <span className="absolute -top-1 -right-1 min-w-[17px] h-[17px] px-1 rounded-full bg-status-danger text-text-inverse text-[10px] font-bold flex items-center justify-center leading-none shadow-xs border border-surface-card">
                    {unreadNotifCount > 9 ? "9+" : unreadNotifCount}
                  </span>
                )}
              </button>

            </div>

            {onLogout && (
              <button
                type="button"
                onClick={onLogout}
                title="Sair da Aplicação (Logout)"
                aria-label="Sair da aplicação"
                className="p-2 rounded-md text-text-secondary hover:text-status-danger hover:bg-surface-bg transition-colors shrink-0 cursor-pointer"
              >
                <LogOut className="h-4 w-4" />
              </button>
            )}
          </div>
        </header>

        {/* Viewport Principal com Scroll */}
        <main className="flex-1 overflow-y-auto overflow-x-hidden p-3 sm:p-6 bg-surface-bg w-full max-w-full">
          {children}
        </main>
      </div>

      {/* Central de Notificações Canônica na Raiz (desfoca e sobrepõe tela inteira, inclusive a sidebar lateral) */}
      <NotificationCenter
        currentRoleKey={currentRoleConfig.roleKey}
        roleDisplayName={currentRoleConfig.displayName}
        isOpen={isNotificationsOpen}
        onClose={() => setIsNotificationsOpen(false)}
        onNavigate={(routeId) => handleSelectNav(routeId)}
        onUnreadCountChange={setUnreadNotifCount}
      />

      {/* Modal Command Palette Funcional (Cmd+K) */}
      {isCommandOpen && (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-16 sm:pt-24 p-4">
          <div
            className="fixed inset-0 bg-surface-overlay backdrop-blur-sm transition-all duration-200 animate-in fade-in-0"
            onClick={() => setIsCommandOpen(false)}
          />
          <div
            role="dialog"
            aria-modal="true"
            aria-label="Paleta de Comandos e Rotas"
            className="relative z-50 w-full max-w-lg rounded-xl border border-border bg-surface-card p-4 shadow-modal"
          >
            <div className="flex items-center gap-2 pb-3 border-b border-border-subtle">
              <Search className="h-4 w-4 text-text-muted shrink-0" />
              <input
                autoFocus
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && filteredCommandItems.length > 0) {
                    e.preventDefault();
                    handleSelectNav(filteredCommandItems[0].id);
                  }
                }}
                placeholder="Filtrar 17 módulos ou disparar comando rápido (Enter para abrir)..."
                className="w-full bg-transparent text-sm text-text-main placeholder:text-text-muted focus:outline-none"
              />
              <button
                type="button"
                onClick={() => setIsCommandOpen(false)}
                className="text-text-muted hover:text-text-main p-1"
                aria-label="Fechar paleta de comandos"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="py-2 max-h-80 overflow-y-auto divide-y divide-border-subtle">
              {filteredCommandItems.length === 0 ? (
                <div className="py-6 text-center text-xs text-text-muted">
                  Nenhum módulo ou comando encontrado para "{searchQuery}".
                </div>
              ) : (
                filteredCommandItems.map((cmd, idx) => (
                  <button
                    key={`${cmd.id}-${idx}`}
                    type="button"
                    onClick={() => handleSelectNav(cmd.id, "facility" in cmd ? cmd.facility : undefined)}
                    className="w-full px-2.5 py-2 hover:bg-surface-bg rounded-md cursor-pointer flex justify-between items-center text-left transition-colors group"
                  >
                    <div className="flex flex-col min-w-0">
                      <span className="text-xs font-medium text-text-main group-hover:text-brand-primary truncate">
                        {cmd.label}
                      </span>
                      <span className="text-[10px] text-text-muted">{cmd.section}</span>
                    </div>
                    <div className="flex items-center gap-1.5 shrink-0">
                      {cmd.shortcut && (
                        <span className="text-[10px] text-text-muted font-mono px-1.5 py-0.5 rounded border border-border bg-surface-bg">
                          {cmd.shortcut}
                        </span>
                      )}
                      <ArrowRight className="h-3.5 w-3.5 text-text-muted group-hover:text-brand-primary" />
                    </div>
                  </button>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* Toast Notifications Container (revnaut:toast) */}
      <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-sm pointer-events-none">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={cn(
              "pointer-events-auto flex items-start gap-2.5 p-3 rounded-lg shadow-lg border text-xs transition-all animate-in fade-in slide-in-from-top-2",
              t.type === "success"
                ? "bg-surface-card border-status-success/40 text-text-main"
                : t.type === "error"
                ? "bg-surface-card border-status-danger/50 text-text-main"
                : "bg-surface-card border-border text-text-main"
            )}
          >
            {t.type === "success" ? (
              <CheckCircle className="h-4 w-4 text-status-success shrink-0 mt-0.5" />
            ) : (
              <AlertCircle className="h-4 w-4 text-status-danger shrink-0 mt-0.5" />
            )}
            <div className="flex-1 min-w-0">
              <p className={cn("font-semibold", t.type === "success" ? "text-status-success" : "text-status-danger")}>
                {t.title}
              </p>
              <p className="text-text-secondary mt-0.5 break-words line-clamp-3">
                {t.message}
              </p>
            </div>
            <button
              type="button"
              onClick={() => setToasts((prev) => prev.filter((item) => item.id !== t.id))}
              className="text-text-muted hover:text-text-main shrink-0 cursor-pointer p-0.5"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

