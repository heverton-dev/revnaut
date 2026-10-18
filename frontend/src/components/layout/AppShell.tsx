import * as React from "react";
import {
  BarChart3,
  Users,
  Briefcase,
  Layers,
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
}

export interface AppShellProps {
  children: React.ReactNode;
  activeNav?: string;
  onNavigate?: (id: string) => void;
  userRole?: string;
  userName?: string;
  accountName?: string;
}

export function AppShell({
  children,
  activeNav = "deals",
  onNavigate,
  userRole = "Super Admin (Dual Field/Inside)",
  userName = "Heverton Eduardo Peres",
  accountName = "Sales Rocket",
}: AppShellProps) {
  const [isCommandOpen, setIsCommandOpen] = React.useState(false);
  const [searchQuery, setSearchQuery] = React.useState("");

  // Atalho Cmd+K / Ctrl+K
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setIsCommandOpen((prev) => !prev);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const navSections: { title: string; items: NavItem[] }[] = [
    {
      title: "Core CRM & Vendas",
      items: [
        { id: "dashboard", label: "Cockpit Executivo", icon: BarChart3, scope: "all" },
        { id: "deals", label: "Pipeline & Deals", icon: Briefcase, scope: "all", badge: "Live" },
        { id: "contacts", label: "Cirurgiões & Clínicas", icon: Users, scope: "all" },
        { id: "omnichannel", label: "Inbox Omnichannel", icon: MessageSquare, scope: "inside", badge: "3" },
      ],
    },
    {
      title: "Consignação & Cirurgia",
      items: [
        { id: "keypartners", label: "KeyPartners (Consignados)", icon: Package, scope: "all", badge: "ANVISA" },
        { id: "dentgo", label: "DENTGO (Same-Day)", icon: Truck, scope: "field", badge: "45min" },
        { id: "video_sos", label: "Vídeo Suporte SOS", icon: Video, scope: "all" },
        { id: "contracts", label: "Contratos Documenso", icon: FileCheck2, scope: "inside" },
      ],
    },
    {
      title: "Governança & Inteligência",
      items: [
        { id: "intelligence", label: "IA Copilot Granola", icon: Sparkles, scope: "all" },
        { id: "analytics", label: "BI Superset RLS", icon: Database, scope: "inside" },
        { id: "scheduling", label: "Cal.com Reativação", icon: Calendar, scope: "field" },
        { id: "rbac", label: "RBAC & Hierarquia", icon: ShieldCheck, scope: "inside" },
        { id: "support", label: "Suporte & RMA", icon: LifeBuoy, scope: "inside" },
        { id: "settings", label: "Configurações & ERP", icon: Settings, scope: "inside" },
      ],
    },
  ];

  return (
    <div className="flex h-screen w-full bg-surface-bg text-text-main overflow-hidden font-sans">
      {/* Sidebar Lateral RBAC Dual */}
      <aside className="w-64 shrink-0 border-r border-border bg-surface-sidebar text-text-inverse flex flex-col justify-between">
        <div>
          {/* Logo Brand Header */}
          <div className="h-16 flex items-center px-5 border-b border-white/10 gap-3">
            <div className="h-8 w-8 rounded-md bg-brand-primary flex items-center justify-center font-bold text-base text-text-inverse shadow-sm">
              RN
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-sm tracking-wide text-white">REVNAULT</span>
              <span className="text-[10px] text-text-muted uppercase tracking-wider">{accountName}</span>
            </div>
          </div>

          {/* Seletor de Escopo Operacional Dual */}
          <div className="px-3 py-3">
            <div className="flex items-center justify-between px-3 py-2 rounded-md bg-white/5 border border-white/10">
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-status-success" />
                <span className="text-xs font-medium text-white/90">Dual Tree Active</span>
              </div>
              <Badge variant="navy" className="text-[10px] uppercase">
                Field + Inside
              </Badge>
            </div>
          </div>

          {/* Navegação Vertical por Módulos */}
          <nav className="px-3 space-y-5 overflow-y-auto max-h-[calc(100vh-210px)]">
            {navSections.map((sec) => (
              <div key={sec.title}>
                <div className="px-3 mb-1.5 text-[10px] font-semibold uppercase tracking-wider text-white/40">
                  {sec.title}
                </div>
                <div className="space-y-0.5">
                  {sec.items.map((item) => {
                    const Icon = item.icon;
                    const isActive = activeNav === item.id;
                    return (
                      <button
                        key={item.id}
                        onClick={() => onNavigate && onNavigate(item.id)}
                        className={cn(
                          "w-full flex items-center justify-between px-3 py-2 rounded-md text-xs font-medium transition-colors text-left",
                          isActive
                            ? "bg-brand-primary text-white shadow-sm"
                            : "text-white/70 hover:text-white hover:bg-surface-sidebar-hover"
                        )}
                      >
                        <div className="flex items-center gap-2.5">
                          <Icon className="h-4 w-4 shrink-0 stroke-[1.8]" />
                          <span>{item.label}</span>
                        </div>
                        {item.badge && (
                          <span
                            className={cn(
                              "text-[10px] px-1.5 py-0.5 rounded-full font-semibold",
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

        {/* Footer do Usuário na Sidebar */}
        <div className="p-3 border-t border-white/10">
          <div className="flex items-center gap-3 px-2 py-2 rounded-md bg-white/5">
            <Avatar fallback={userName} size="sm" className="border-white/20 text-white bg-brand-primary" />
            <div className="flex flex-col min-w-0 flex-1">
              <span className="text-xs font-semibold text-white truncate">{userName}</span>
              <span className="text-[10px] text-white/60 truncate">{userRole}</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Área Principal de Conteúdo */}
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        {/* Topbar Superior */}
        <header className="h-16 border-b border-border bg-surface-card px-6 flex items-center justify-between shrink-0">
          {/* Campo de Busca & Command Palette Trigger */}
          <button
            onClick={() => setIsCommandOpen(true)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-md border border-border bg-surface-bg text-text-secondary hover:text-text-main text-xs transition-colors w-72 justify-between"
          >
            <div className="flex items-center gap-2">
              <Search className="h-3.5 w-3.5 text-text-muted" />
              <span>Buscar cirurgião, lote ou comando...</span>
            </div>
            <kbd className="inline-flex items-center gap-0.5 rounded border border-border bg-surface-card px-1.5 py-0.5 text-[10px] text-text-muted font-mono">
              <Command className="h-2.5 w-2.5" /> K
            </kbd>
          </button>

          {/* Ações Rápidas do Topbar */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-2.5 py-1 rounded-full bg-status-success-subtle text-status-success text-xs font-medium border border-status-success/20">
              <CheckCircle className="h-3.5 w-3.5" />
              <span>PostgreSQL 16 WAL Active</span>
            </div>

            <button
              className="relative p-2 rounded-md text-text-secondary hover:text-text-main hover:bg-surface-bg transition-colors"
              aria-label="Notificações"
            >
              <Bell className="h-4 w-4" />
              <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-status-danger" />
            </button>
          </div>
        </header>

        {/* Viewport Principal com Scroll */}
        <main className="flex-1 overflow-y-auto p-6 bg-surface-bg">
          {children}
        </main>
      </div>

      {/* Modal Command Palette (Cmd+K) */}
      {isCommandOpen && (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 p-4">
          <div
            className="fixed inset-0 bg-text-main/50 backdrop-blur-xs"
            onClick={() => setIsCommandOpen(false)}
          />
          <div className="relative z-50 w-full max-w-lg rounded-xl border border-border bg-surface-card p-4 shadow-modal">
            <div className="flex items-center gap-2 pb-3 border-b border-border-subtle">
              <Search className="h-4 w-4 text-text-muted" />
              <input
                autoFocus
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Digite para buscar ou executar uma ação rápida..."
                className="w-full bg-transparent text-sm text-text-main placeholder:text-text-muted focus:outline-none"
              />
            </div>
            <div className="py-3 text-xs text-text-secondary space-y-1">
              <div className="px-2 py-1.5 hover:bg-surface-bg rounded cursor-pointer flex justify-between items-center">
                <span>Criar Novo Negócio / Deal Cirúrgico</span>
                <span className="text-[10px] text-text-muted font-mono">D</span>
              </div>
              <div className="px-2 py-1.5 hover:bg-surface-bg rounded cursor-pointer flex justify-between items-center">
                <span>Solicitar Entrega DENTGO Same-Day (45min)</span>
                <span className="text-[10px] text-text-muted font-mono">G</span>
              </div>
              <div className="px-2 py-1.5 hover:bg-surface-bg rounded cursor-pointer flex justify-between items-center">
                <span>Verificar Custódia de Kit KeyPartners (Lote ANVISA)</span>
                <span className="text-[10px] text-text-muted font-mono">K</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
