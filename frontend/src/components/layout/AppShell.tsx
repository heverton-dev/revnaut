import * as React from "react";
import {
  BarChart3,
  Users,
  Briefcase,
  MessageSquare,
  Package,
  Truck,
  ShieldCheck,
  LifeBuoy,
  Settings,
  Search,
  Bell,
  CheckCircle,
  Video,
  FileCheck2,
  Database,
  Calendar,
  Sparkles,
  Command,
  Menu,
  X,
  Target,
  Megaphone,
  ScanLine,
  PanelLeftClose,
  PanelLeftOpen,
  ArrowRight,
  LogOut,
  AlertCircle,
  Radar,
} from "lucide-react";
import { Avatar } from "@/components/ui/Avatar";
import { cn } from "@/lib/utils";
import { getActiveUserId, setActiveUserId, ToastPayload } from "@/lib/api";
import { NotificationCenter } from "@/components/layout/NotificationCenter";

export interface NavItem {
  id: string;
  label: string;
  icon: React.ElementType;
  badge?: string;
  scope?: "field" | "inside" | "all";
  shortcut?: string;
}

export interface AuthUserItem {
  id: string;
  name: string;
  email: string;
  role: string;
  account_id?: string;
  team_id?: string | null;
  is_superadmin?: boolean | number;
}

export interface RoleWorkspaceConfig {
  roleKey: string;
  displayName: string;
  visibleRoutes: string[];
  defaultLandingRoute: string;
}

export const ROLE_WORKSPACES: Record<string, RoleWorkspaceConfig> = {
  field_sales: {
    roleKey: "field_sales",
    displayName: "Consultor Externo (Campo)",
    visibleRoutes: ["deals", "contacts", "keypartners", "dentgo", "video_sos", "intelligence", "market_intel"],
    defaultLandingRoute: "deals",
  },
  inside_sales: {
    roleKey: "inside_sales",
    displayName: "Consultor Interno (Atendimento)",
    visibleRoutes: ["omnichannel", "deals", "contacts", "contracts", "scoring", "scheduling", "market_intel"],
    defaultLandingRoute: "omnichannel",
  },
  logistics: {
    roleKey: "logistics",
    displayName: "Logística e Estoque (Expedição)",
    visibleRoutes: ["dentgo", "keypartners", "support", "settings"],
    defaultLandingRoute: "dentgo",
  },
  clinical_support: {
    roleKey: "clinical_support",
    displayName: "Suporte Clínico e Pós-Venda",
    visibleRoutes: ["support", "video_sos", "imaging", "omnichannel", "scheduling"],
    defaultLandingRoute: "support",
  },
  sales_manager: {
    roleKey: "sales_manager",
    displayName: "Gerente Comercial",
    visibleRoutes: ["dashboard", "deals", "contacts", "keypartners", "contracts", "rbac", "marketing", "market_intel"],
    defaultLandingRoute: "dashboard",
  },
  superadmin: {
    roleKey: "superadmin",
    displayName: "Diretoria / Administrador Geral",
    visibleRoutes: [
      "dashboard", "deals", "contacts", "omnichannel", "scoring", "marketing",
      "keypartners", "dentgo", "contracts", "video_sos", "imaging",
      "intelligence", "market_intel", "analytics", "scheduling", "support", "rbac", "settings"
    ],
    defaultLandingRoute: "dashboard",
  },
};

export function resolveRoleConfig(roleString?: string): RoleWorkspaceConfig {
  const s = (roleString || "").toLowerCase();
  if (s.includes("campo") || s.includes("field") || s.includes("externo")) return ROLE_WORKSPACES.field_sales;
  if (s.includes("inside") || s.includes("atendimento") || s.includes("interno")) return ROLE_WORKSPACES.inside_sales;
  if (s.includes("log") || s.includes("estoque") || s.includes("expedição") || s.includes("expedicao")) return ROLE_WORKSPACES.logistics;
  if (s.includes("clínico") || s.includes("clinico") || s.includes("suporte") || s.includes("pós") || s.includes("pos")) return ROLE_WORKSPACES.clinical_support;
  if (s.includes("gerente") || s.includes("manager")) return ROLE_WORKSPACES.sales_manager;
  if (s.includes("admin") || s.includes("diretor") || s.includes("super")) return ROLE_WORKSPACES.superadmin;
  return ROLE_WORKSPACES.superadmin;
}

export interface AppShellProps {
  children: React.ReactNode;
  activeNav?: string;
  onNavigate?: (id: string) => void;
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
  onNavigate,
  userRole = "Super Admin (Dual Field/Inside)",
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

  const [selectedUserId, setSelectedUserId] = React.useState<string>(
    propUserId || getActiveUserId()
  );
  const [currentUserProfile, setCurrentUserProfile] = React.useState<AuthUserItem | null>(null);
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
        if (meData && meData.id) {
          setCurrentUserProfile(meData);
        }
        if (Array.isArray(usersData) && usersData.length > 0) {
          setAvailableUsers(usersData);
        }
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
    return resolveRoleConfig(currentUserProfile?.role || userRole);
  }, [currentUserProfile?.role, userRole]);

  const rawNavSections: { title: string; items: NavItem[] }[] = [
    {
      title: "Vendas e Atendimento",
      items: [
        { id: "dashboard", label: "Visão do Dia", icon: BarChart3, shortcut: "1" },
        { id: "deals", label: "Negociações (Funil)", icon: Briefcase, badge: "Ativo", shortcut: "D" },
        { id: "contacts", label: "Dentistas e Clínicas", icon: Users, shortcut: "C" },
        { id: "scoring", label: "Qualificação de Clientes", icon: Target, shortcut: "S" },
        { id: "marketing", label: "Campanhas e Indicações", icon: Megaphone, shortcut: "M" },
        { id: "omnichannel", label: "Atendimento WhatsApp", icon: MessageSquare, badge: "3", shortcut: "O" },
      ],
    },
    {
      title: "Consignação e Logística",
      items: [
        { id: "keypartners", label: "Malas em Consignação", icon: Package, badge: "ANVISA", shortcut: "K" },
        { id: "dentgo", label: "Entregas Expressas", icon: Truck, badge: "45min", shortcut: "G" },
        { id: "video_sos", label: "Chamadas e Vídeo", icon: Video, shortcut: "V" },
        { id: "contracts", label: "Propostas e Contratos", icon: FileCheck2, shortcut: "T" },
        { id: "imaging", label: "Exames 3D e Tomografias", icon: ScanLine, shortcut: "P" },
      ],
    },
    {
      title: "Gestão e Suporte",
      items: [
        { id: "intelligence", label: "Assistente Comercial", icon: Sparkles, shortcut: "I" },
        { id: "market_intel", label: "Radar de Mercado e Concorrência", icon: Radar, shortcut: "N" },
        { id: "analytics", label: "Relatórios e Metas", icon: Database, shortcut: "B" },
        { id: "scheduling", label: "Retorno de Pacientes", icon: Calendar, shortcut: "R" },
        { id: "support", label: "Suporte Clínico e Garantias", icon: LifeBuoy, shortcut: "A" },
        { id: "rbac", label: "Equipes e Acessos", icon: ShieldCheck, shortcut: "H" },
        { id: "settings", label: "Configurações e Notas Fiscais", icon: Settings, shortcut: "E" },
      ],
    },
  ];

  const navSections = React.useMemo(() => {
    if (showAllModules) return rawNavSections;
    const allowed = new Set(currentRoleConfig.visibleRoutes);
    return rawNavSections
      .map((sec) => ({
        ...sec,
        items: sec.items.filter((item) => allowed.has(item.id)),
      }))
      .filter((sec) => sec.items.length > 0);
  }, [showAllModules, currentRoleConfig]);

  const allNavItems = React.useMemo(
    () => rawNavSections.flatMap((sec) => sec.items.map((item) => ({ ...item, section: sec.title }))),
    []
  );

  const quickCommands = React.useMemo(
    () => [
      { id: "deals", label: "Criar Nova Negociação", section: "Ação Rápida", shortcut: "D" },
      { id: "contacts", label: "Cadastrar Dentista ou Clínica", section: "Ação Rápida", shortcut: "C" },
      { id: "dentgo", label: "Solicitar Entrega Rápida (45 min)", section: "Ação Rápida", shortcut: "G" },
      { id: "keypartners", label: "Consultar Maletas em Consignação", section: "Ação Rápida", shortcut: "K" },
      { id: "contracts", label: "Gerar Proposta Comercial ou Contrato", section: "Ação Rápida", shortcut: "T" },
      { id: "support", label: "Abrir Chamado Pós-Cirúrgico", section: "Ação Rápida", shortcut: "A" },
      { id: "analytics", label: "Consultar Relatórios e Indicadores", section: "Ação Rápida", shortcut: "B" },
      { id: "logout", label: "Encerrar Sessão (Logout)", section: "Sessão & Conta", shortcut: "Q" },
    ],
    []
  );

  const filteredCommandItems = React.useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    const combined = [
      ...allNavItems.map((it) => ({
        id: it.id,
        label: `Ir para: ${it.label}`,
        section: it.section,
        shortcut: it.shortcut || "",
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

  const handleSelectNav = (routeId: string) => {
    if (routeId === "logout") {
      setIsMobileDrawerOpen(false);
      setIsCommandOpen(false);
      setSearchQuery("");
      if (onLogout) onLogout();
      return;
    }
    const nextHash = `#!/${routeId}`;
    if (typeof window !== "undefined" && window.location.hash !== nextHash) {
      window.location.hash = nextHash;
    }
    if (onNavigate) {
      onNavigate(routeId);
    }
    setIsMobileDrawerOpen(false);
    setIsCommandOpen(false);
    setSearchQuery("");
  };

  const handleUserChange = (newUserId: string) => {
    setSelectedUserId(newUserId);
    setActiveUserId(newUserId);
    const targetUser = availableUsers.find((u) => u.id === newUserId);
    if (targetUser) {
      setCurrentUserProfile(targetUser);
      const newRole = resolveRoleConfig(targetUser.role);
      if (!showAllModules && !newRole.visibleRoutes.includes(activeNav)) {
        handleSelectNav(newRole.defaultLandingRoute);
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
                    <span className="font-bold text-sm tracking-wide text-white truncate">REVNAULT</span>
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
                      const isActive = activeNav === item.id;
                      return (
                        <button
                          key={item.id}
                          type="button"
                          title={item.label}
                          onClick={() => handleSelectNav(item.id)}
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
                            {!isCompactSidebar && (
                              <span className="truncate">
                                {item.label}
                              </span>
                            )}
                          </div>
                          {!isCompactSidebar && item.badge && (
                            <span
                              className={cn(
                                "text-[10px] px-1.5 py-0.5 rounded-full font-semibold shrink-0 whitespace-nowrap",
                                isActive
                                  ? "bg-white/20 text-white"
                                  : "bg-white/10 text-white/80"
                              )}
                            >
                              {item.badge}
                            </span>
                          )}
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))}
            </nav>
          </div>

          {/* Footer do Usuário e Seletor de Perfil na Sidebar */}
          <div className={cn("border-t border-white/10 shrink-0 space-y-2", isCompactSidebar ? "p-2" : "p-2.5")}>
            {/* Botão de Toggle da Sidebar no Rodapé (sem sobrepor logo ou dados) */}
            <button
              type="button"
              onClick={() => setIsCompactSidebar((prev) => !prev)}
              className={cn(
                "hidden lg:flex items-center rounded-md text-white/60 hover:text-white hover:bg-white/10 transition-colors text-xs font-medium cursor-pointer",
                isCompactSidebar ? "w-10 h-10 mx-auto justify-center p-0" : "w-full justify-between px-2.5 py-1.5"
              )}
              title={isCompactSidebar ? "Expandir menu lateral" : "Recolher menu lateral"}
              aria-label={isCompactSidebar ? "Expandir menu lateral" : "Recolher menu lateral"}
            >
              <div className={cn("flex items-center min-w-0", isCompactSidebar ? "justify-center" : "gap-2")}>
                {isCompactSidebar ? (
                  <PanelLeftOpen className="h-4 w-4 shrink-0 text-white/70" />
                ) : (
                  <PanelLeftClose className="h-4 w-4 shrink-0 text-white/70" />
                )}
                {!isCompactSidebar && <span className="truncate">Recolher menu lateral</span>}
              </div>
            </button>
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
              {onLogout && (
                <button
                  type="button"
                  onClick={onLogout}
                  title="Sair da Aplicação (Logout)"
                  aria-label="Sair da aplicação"
                  className="p-1.5 rounded text-white/60 hover:text-status-danger hover:bg-white/10 transition-colors shrink-0 cursor-pointer"
                >
                  <LogOut className="h-3.5 w-3.5" />
                </button>
              )}
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

                <button
                  type="button"
                  onClick={() => setShowAllModules((prev) => !prev)}
                  className="w-full text-center py-1 text-[10px] text-white/60 hover:text-white transition-colors border border-white/10 rounded bg-white/5"
                >
                  {showAllModules ? "Modo Focado no Cargo" : "Mostrar todos os módulos (17)"}
                </button>
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
            <button
              type="button"
              onClick={() => setShowAllModules((prev) => !prev)}
              className={cn(
                "hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-medium border transition-colors cursor-pointer",
                showAllModules
                  ? "bg-brand-primary text-white border-brand-primary"
                  : "bg-surface-bg text-text-secondary border-border hover:text-text-main"
              )}
              title="Alternar entre visualização filtrada por cargo e visualização de todos os 17 módulos"
            >
              {showAllModules ? "Modo Visão Completa (Admin)" : "Modo Focado no Cargo"}
            </button>

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

              <NotificationCenter
                currentRoleKey={currentRoleConfig.roleKey}
                roleDisplayName={currentRoleConfig.displayName}
                isOpen={isNotificationsOpen}
                onClose={() => setIsNotificationsOpen(false)}
                onNavigate={(routeId) => handleSelectNav(routeId)}
                onUnreadCountChange={setUnreadNotifCount}
              />
            </div>
          </div>
        </header>

        {/* Viewport Principal com Scroll */}
        <main className="flex-1 overflow-y-auto overflow-x-hidden p-3 sm:p-6 bg-surface-bg w-full max-w-full">
          {children}
        </main>
      </div>

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
                    onClick={() => handleSelectNav(cmd.id)}
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

