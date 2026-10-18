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
} from "lucide-react";
import { Avatar } from "@/components/ui/Avatar";
import { Badge } from "@/components/ui/Badge";
import { cn } from "@/lib/utils";

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

  const [selectedUserId, setSelectedUserId] = React.useState<string>(
    propUserId || "usr-superadmin-god"
  );
  const [currentUserProfile, setCurrentUserProfile] = React.useState<AuthUserItem | null>(null);
  const [availableUsers, setAvailableUsers] = React.useState<AuthUserItem[]>([]);
  const [healthStatus, setHealthStatus] = React.useState<{
    status: string;
    sqlite_journal_mode: string;
    accounts_online: number;
  } | null>(null);

  React.useEffect(() => {
    if (propUserId && propUserId !== selectedUserId) {
      setSelectedUserId(propUserId);
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

  const navSections: { title: string; items: NavItem[] }[] = [
    {
      title: "Core CRM & Vendas",
      items: [
        { id: "dashboard", label: "Cockpit Executivo", icon: BarChart3, scope: "all", shortcut: "1" },
        { id: "deals", label: "Pipeline & Deals", icon: Briefcase, scope: "all", badge: "Live", shortcut: "D" },
        { id: "contacts", label: "Cirurgiões & Clínicas", icon: Users, scope: "all", shortcut: "C" },
        { id: "omnichannel", label: "Inbox Omnichannel", icon: MessageSquare, scope: "inside", badge: "3", shortcut: "O" },
        { id: "scoring", label: "Lead Scoring ICP", icon: Target, scope: "all", shortcut: "S" },
        { id: "marketing", label: "Marketing & LPs", icon: Megaphone, scope: "inside", shortcut: "M" },
      ],
    },
    {
      title: "Consignação & Cirurgia",
      items: [
        { id: "keypartners", label: "KeyPartners (Consignados)", icon: Package, scope: "all", badge: "ANVISA", shortcut: "K" },
        { id: "dentgo", label: "DENTGO (Same-Day)", icon: Truck, scope: "field", badge: "45min", shortcut: "G" },
        { id: "video_sos", label: "Vídeo Suporte SOS", icon: Video, scope: "all", shortcut: "V" },
        { id: "contracts", label: "Contratos Documenso", icon: FileCheck2, scope: "inside", shortcut: "T" },
        { id: "imaging", label: "PACS 3D DICOM/STL", icon: ScanLine, scope: "all", shortcut: "P" },
      ],
    },
    {
      title: "Governança & Inteligência",
      items: [
        { id: "intelligence", label: "IA Copilot Granola", icon: Sparkles, scope: "all", shortcut: "I" },
        { id: "analytics", label: "BI Superset RLS", icon: Database, scope: "inside", shortcut: "B" },
        { id: "scheduling", label: "Cal.com Reativação", icon: Calendar, scope: "field", shortcut: "R" },
        { id: "rbac", label: "RBAC & Hierarquia", icon: ShieldCheck, scope: "inside", shortcut: "H" },
        { id: "support", label: "Suporte & RMA", icon: LifeBuoy, scope: "inside", shortcut: "A" },
        { id: "settings", label: "Configurações & ERP", icon: Settings, scope: "inside", shortcut: "E" },
      ],
    },
  ];

  const allNavItems = React.useMemo(
    () => navSections.flatMap((sec) => sec.items.map((item) => ({ ...item, section: sec.title }))),
    []
  );

  const quickCommands = React.useMemo(
    () => [
      { id: "deals", label: "Criar Novo Negócio / Deal Cirúrgico", section: "Ação Rápida", shortcut: "D" },
      { id: "contacts", label: "Validar Registro CRO/UF ou Cadastrar Cirurgião", section: "Ação Rápida", shortcut: "C" },
      { id: "dentgo", label: "Solicitar Entrega DENTGO Same-Day (45min)", section: "Ação Rápida", shortcut: "G" },
      { id: "keypartners", label: "Verificar Custódia de Kit KeyPartners (Lote ANVISA)", section: "Ação Rápida", shortcut: "K" },
      { id: "contracts", label: "Gerar Contrato Digital Documenso SHA-256", section: "Ação Rápida", shortcut: "T" },
      { id: "support", label: "Abrir Queixa Técnica ANVISA RMA ou SOS Cirúrgico", section: "Ação Rápida", shortcut: "A" },
      { id: "analytics", label: "Consultar Agente Analítico Text-to-SQL", section: "Ação Rápida", shortcut: "B" },
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
    if (onSelectUser) {
      onSelectUser(newUserId);
    }
  };

  const displayUserName = currentUserProfile?.name || userName;
  const displayUserRole = currentUserProfile?.role || userRole;

  return (
    <div className="flex h-screen w-full bg-surface-bg text-text-main overflow-hidden font-sans">
      {/* Backdrop do Drawer Mobile/Tablet (< 1024px) */}
      {isMobileDrawerOpen && (
        <div
          className="fixed inset-0 z-40 bg-text-main/50 backdrop-blur-xs lg:hidden"
          onClick={() => setIsMobileDrawerOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Sidebar Lateral RBAC Dual: Gaveta deslizante em <1024px (0px quando fechada) e Fixa/Colapsável em >=1024px */}
      <aside
        className={cn(
          "bg-surface-sidebar text-text-inverse flex flex-col justify-between transition-all duration-200 z-50 shrink-0",
          isMobileDrawerOpen
            ? "max-lg:fixed max-lg:inset-y-0 max-lg:left-0 max-lg:w-64 max-lg:border-r max-lg:border-border max-lg:shadow-modal"
            : "max-lg:fixed max-lg:left-0 max-lg:top-0 max-lg:w-0 max-lg:h-0 max-lg:overflow-hidden max-lg:border-0",
          isCompactSidebar ? "lg:w-16 lg:border-r lg:border-border" : "lg:w-64 lg:border-r lg:border-border"
        )}
      >
        <div className={cn("flex flex-col h-full justify-between", isCompactSidebar ? "w-64 lg:w-16" : "w-64")}>
          <div className="min-h-0 flex-1 flex flex-col">
            {/* Logo Brand Header */}
            <div className="h-16 flex items-center justify-between px-4 border-b border-white/10 gap-2 shrink-0">
              <div className="flex items-center gap-2.5 min-w-0">
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
                onClick={() => setIsCompactSidebar((prev) => !prev)}
                className="hidden lg:inline-flex p-1.5 rounded-md text-white/60 hover:text-white hover:bg-white/10 transition-colors"
                aria-label={isCompactSidebar ? "Expandir menu lateral" : "Recolher menu lateral"}
                title={isCompactSidebar ? "Expandir menu" : "Modo compacto"}
              >
                {isCompactSidebar ? (
                  <PanelLeftOpen className="h-4 w-4" />
                ) : (
                  <PanelLeftClose className="h-4 w-4" />
                )}
              </button>

              <button
                type="button"
                onClick={() => setIsMobileDrawerOpen(false)}
                className="lg:hidden p-1.5 rounded-md text-white/70 hover:text-white hover:bg-white/10"
                aria-label="Fechar menu"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {/* Seletor de Escopo Operacional Dual */}
            {!isCompactSidebar && (
              <div className="px-3 py-2.5 shrink-0">
                <div className="flex items-center justify-between px-3 py-1.5 rounded-md bg-white/5 border border-white/10">
                  <div className="flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full bg-status-success" />
                    <span className="text-xs font-medium text-white/90">Dual Tree Active</span>
                  </div>
                  <Badge variant="navy" className="text-[10px] uppercase">
                    Field + Inside
                  </Badge>
                </div>
              </div>
            )}

            {/* Navegação Vertical pelas 17 Rotas */}
            <nav className="px-2.5 py-2 space-y-4 overflow-y-auto flex-1">
              {navSections.map((sec) => (
                <div key={sec.title}>
                  {!isCompactSidebar && (
                    <div className="px-2.5 mb-1 text-[10px] font-semibold uppercase tracking-wider text-white/40">
                      {sec.title}
                    </div>
                  )}
                  <div className="space-y-0.5">
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
                            "w-full flex items-center justify-between px-2.5 py-2 rounded-md text-xs font-medium transition-colors text-left",
                            isActive
                              ? "bg-brand-primary text-white shadow-sm"
                              : "text-white/70 hover:text-white hover:bg-surface-sidebar-hover"
                          )}
                        >
                          <div className="flex items-center gap-2.5 min-w-0">
                            <Icon className="h-4 w-4 shrink-0 stroke-[1.8]" />
                            <span className={cn("truncate", isCompactSidebar && "lg:hidden")}>
                              {item.label}
                            </span>
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

          {/* Footer do Usuário e Seletor de Contexto RBAC na Sidebar */}
          <div className="p-2.5 border-t border-white/10 shrink-0 space-y-2">
            <div className="flex items-center justify-between gap-1.5 px-2 py-1.5 rounded-md bg-white/5">
              <div className="flex items-center gap-2 min-w-0 flex-1">
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
              <div className="px-1">
                <label className="block text-[10px] uppercase tracking-wider text-white/40 mb-1">
                  Contexto Consultor / RBAC
                </label>
                <select
                  aria-label="Alternar contexto de consultor"
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
            )}
          </div>
        </div>
      </aside>

      {/* Área Principal de Conteúdo (100% da largura em Mobile 375px e Tablet 768px) */}
      <div className="flex flex-col flex-1 min-w-0 w-full overflow-hidden">
        {/* Topbar Superior Responsiva (Zero Overflow em 375px) */}
        <header className="h-14 sm:h-16 border-b border-border bg-surface-card px-3 sm:px-6 flex items-center justify-between gap-2 shrink-0 w-full overflow-hidden">
          <div className="flex items-center gap-2 min-w-0 flex-1">
            {/* Botão Hamburger para Mobile/Tablet (< 1024px) */}
            <button
              type="button"
              onClick={() => setIsMobileDrawerOpen(true)}
              className="lg:hidden inline-flex items-center justify-center p-2 rounded-md border border-border bg-surface-bg text-text-main hover:bg-surface-card shrink-0"
              aria-label="Abrir menu de navegação"
            >
              <Menu className="h-4 w-4" />
            </button>

            {/* Campo de Busca & Command Palette Trigger */}
            <button
              type="button"
              onClick={() => setIsCommandOpen(true)}
              className="flex items-center gap-2 px-2.5 sm:px-3 py-1.5 rounded-md border border-border bg-surface-bg text-text-secondary hover:text-text-main text-xs transition-colors flex-1 max-w-xs sm:max-w-md min-w-0 justify-between"
            >
              <div className="flex items-center gap-2 min-w-0">
                <Search className="h-3.5 w-3.5 text-text-muted shrink-0" />
                <span className="truncate">Buscar rota, cirurgião, lote ou comando...</span>
              </div>
              <kbd className="hidden sm:inline-flex items-center gap-0.5 rounded border border-border bg-surface-card px-1.5 py-0.5 text-[10px] text-text-muted font-mono shrink-0">
                <Command className="h-2.5 w-2.5" /> K
              </kbd>
            </button>
          </div>

          {/* Ações Rápidas do Topbar */}
          <div className="flex items-center gap-2 shrink-0">
            <div className="flex items-center gap-1.5 px-2 sm:px-2.5 py-1 rounded-full bg-status-success-subtle text-status-success text-[11px] sm:text-xs font-medium border border-status-success/20 whitespace-nowrap shrink-0">
              <CheckCircle className="h-3.5 w-3.5 shrink-0" />
              <span className="hidden md:inline">
                {healthStatus
                  ? `SQLite ${String(healthStatus.sqlite_journal_mode).toUpperCase()} • ${healthStatus.accounts_online} Tenant(s)`
                  : "SQLite WAL Active"}
              </span>
              <span className="md:hidden">WAL OK</span>
            </div>

            <button
              type="button"
              onClick={() => setIsCommandOpen(true)}
              className="relative p-2 rounded-md text-text-secondary hover:text-text-main hover:bg-surface-bg transition-colors shrink-0"
              aria-label="Notificações e Comandos"
            >
              <Bell className="h-4 w-4" />
              <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-status-danger" />
            </button>
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
            className="fixed inset-0 bg-text-main/50 backdrop-blur-xs"
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
    </div>
  );
}

