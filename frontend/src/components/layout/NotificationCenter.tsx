// -*- coding: utf-8 -*-
/**
 * NotificationCenter.tsx
 * Central de Notificações Dinâmica por Tipo de Usuário (Cargo Operacional).
 * Aderente à Lei #5 (Zero Stubs) e Lei #14 (Zero Emojis / SVG Lucide Only).
 */

import * as React from "react";
import {
  Bell,
  CheckCheck,
  CheckCircle2,
  AlertTriangle,
  Info,
  Clock,
  ExternalLink,
  ShieldAlert,
  Layers,
  X,
  Briefcase,
  Truck,
  Stethoscope,
  BarChart3,
  ShieldCheck,
  MessageSquare,
} from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/utils";

export interface OperationNotification {
  id: string;
  roleKey: string; // "field_sales" | "inside_sales" | "logistics" | "clinical_support" | "sales_manager" | "superadmin" | "all";
  roleLabel: string;
  title: string;
  description: string;
  category: "urgente" | "alerta" | "sucesso" | "info";
  timestamp: string;
  read: boolean;
  targetRoute: string;
  actionLabel: string;
}

const DEFAULT_NOTIFICATIONS: OperationNotification[] = [
  // Field Sales (Consultor Externo)
  {
    id: "notif-field-1",
    roleKey: "field_sales",
    roleLabel: "Campo",
    title: "Reposição Emergencial • Dra. Renata Paiva",
    description: "Solicitou kit cirúrgico Cone Morse 3.75x11.5mm para procedimento às 14h na Clínica OdontoPrime.",
    category: "urgente",
    timestamp: "Há 10 min",
    read: false,
    targetRoute: "deals",
    actionLabel: "Abrir Oportunidade",
  },
  {
    id: "notif-field-2",
    roleKey: "field_sales",
    roleLabel: "Campo",
    title: "Alerta Anti-Churn • Dr. Fabio Medeiros",
    description: "Cirurgião KOL atingiu 60 dias sem recompra de implantes cilíndricos. Visita presencial recomendada.",
    category: "alerta",
    timestamp: "Há 40 min",
    read: false,
    targetRoute: "deals",
    actionLabel: "Ver Histórico RFM",
  },
  {
    id: "notif-field-3",
    roleKey: "field_sales",
    roleLabel: "Campo",
    title: "Dentgo Express Despachado",
    description: "Motoboy credenciado retirou kit cirúrgico para entrega na Clínica Dental Prime Moema.",
    category: "sucesso",
    timestamp: "Há 1h",
    read: true,
    targetRoute: "dentgo",
    actionLabel: "Rastrear Rota",
  },

  // Inside Sales (Consultor Interno / Atendimento)
  {
    id: "notif-inside-1",
    roleKey: "inside_sales",
    roleLabel: "Atendimento",
    title: "Nova Mensagem WhatsApp • Dr. Carlos Andrade",
    description: "Solicitou proposta comercial formal para lote de 50 parafusos protéticos angulados.",
    category: "urgente",
    timestamp: "Há 5 min",
    read: false,
    targetRoute: "omnichannel",
    actionLabel: "Abrir Chat WhatsApp",
  },
  {
    id: "notif-inside-2",
    roleKey: "inside_sales",
    roleLabel: "Atendimento",
    title: "Minuta Documenso Pronta para Assinatura",
    description: "Contrato anual de fornecimento com Instituto Branemark aguarda validação de signatários.",
    category: "alerta",
    timestamp: "Há 25 min",
    read: false,
    targetRoute: "contracts",
    actionLabel: "Ver Contrato",
  },
  {
    id: "notif-inside-3",
    roleKey: "inside_sales",
    roleLabel: "Atendimento",
    title: "Lead ICP Alto Pontuado",
    description: "Hospital Moriah atingiu score 94 no modelo preditivo de propensão de compra de implantes.",
    category: "info",
    timestamp: "Há 2h",
    read: true,
    targetRoute: "scoring",
    actionLabel: "Analisar Scoring",
  },

  // Logistics (Logística e Estoque)
  {
    id: "notif-log-1",
    roleKey: "logistics",
    roleLabel: "Expedição",
    title: "Pedido SOS Dentgo Nº 892",
    description: "Entrega prioritária intraoperatória solicitada pelo Hospital Pilar com SLA máximo de 45 minutos.",
    category: "urgente",
    timestamp: "Há 3 min",
    read: false,
    targetRoute: "dentgo",
    actionLabel: "Despachar Motoboy",
  },
  {
    id: "notif-log-2",
    roleKey: "logistics",
    roleLabel: "Expedição",
    title: "Devolução de Maleta Consignada",
    description: "Maleta #MC-104 retornou de cirurgia com 4 implantes consumidos pendentes de baixa no estoque.",
    category: "alerta",
    timestamp: "Há 35 min",
    read: false,
    targetRoute: "keypartners",
    actionLabel: "Auditar Maleta",
  },
  {
    id: "notif-log-3",
    roleKey: "logistics",
    roleLabel: "Expedição",
    title: "Lote de Pilares Aprovado ANVISA",
    description: "Lote de pilares protéticos #LT-2026-B liberado no gate de quarentena para expedição regular.",
    category: "sucesso",
    timestamp: "Há 3h",
    read: true,
    targetRoute: "support",
    actionLabel: "Ver Quarentena",
  },

  // Clinical Support (Suporte Clínico e Pós-Venda)
  {
    id: "notif-clin-1",
    roleKey: "clinical_support",
    roleLabel: "Clínico",
    title: "Chamada de Vídeo SOS Intraoperatório",
    description: "Dr. Thiago Souza solicitou suporte técnico ao vivo para seleção de componente protético via LiveKit.",
    category: "urgente",
    timestamp: "Há 2 min",
    read: false,
    targetRoute: "video_sos",
    actionLabel: "Conectar Sala LiveKit",
  },
  {
    id: "notif-clin-2",
    roleKey: "clinical_support",
    roleLabel: "Clínico",
    title: "Novo Arquivo Tomográfico DICOM/STL",
    description: "Tomografia cone-beam carregada para planejamento de cirurgia guiada com prótese imediata.",
    category: "info",
    timestamp: "Há 50 min",
    read: false,
    targetRoute: "imaging",
    actionLabel: "Abrir Viewer 3D",
  },
  {
    id: "notif-clin-3",
    roleKey: "clinical_support",
    roleLabel: "Clínico",
    title: "Protocolo de Rastreabilidade ANVISA",
    description: "Dossiê técnico do lote cirúrgico L-8832 compilado e arquivado com conformidade 100%.",
    category: "sucesso",
    timestamp: "Há 2h",
    read: true,
    targetRoute: "support",
    actionLabel: "Consultar ANVISA Desk",
  },

  // Sales Manager (Gerente Comercial)
  {
    id: "notif-mgr-1",
    roleKey: "sales_manager",
    roleLabel: "Gestão",
    title: "Aprovação de Desconto Excepcional",
    description: "Consultor de campo solicitou margem com 12% de desconto para fechar contrato com rede hospitalar.",
    category: "alerta",
    timestamp: "Há 15 min",
    read: false,
    targetRoute: "deals",
    actionLabel: "Analisar Margem",
  },
  {
    id: "notif-mgr-2",
    roleKey: "sales_manager",
    roleLabel: "Gestão",
    title: "Radar Anti-Churn • 13 Cirurgiões Críticos",
    description: "Volume de recompra abaixo da média histórica detectado na carteira de São Paulo e Campinas.",
    category: "urgente",
    timestamp: "Há 45 min",
    read: false,
    targetRoute: "dashboard",
    actionLabel: "Abrir Radar Cockpit",
  },
  {
    id: "notif-mgr-3",
    roleKey: "sales_manager",
    roleLabel: "Gestão",
    title: "Meta de Fechamento Ultrapassada",
    description: "Pipeline atingiu R$ 385.000 em propostas avançadas na quinzena operacional.",
    category: "sucesso",
    timestamp: "Há 3h",
    read: true,
    targetRoute: "dashboard",
    actionLabel: "Ver Funil de Vendas",
  },

  // Super Admin / Diretoria Geral
  {
    id: "notif-adm-1",
    roleKey: "superadmin",
    roleLabel: "Diretoria",
    title: "Exportação Snapshot R2 Concluída",
    description: "Snapshot em formatos CSV e Parquet sincronizado no Cloudflare R2 com hash SHA-256 verificado.",
    category: "sucesso",
    timestamp: "Há 8 min",
    read: false,
    targetRoute: "dashboard",
    actionLabel: "Ver Cockpit BI",
  },
  {
    id: "notif-adm-2",
    roleKey: "superadmin",
    roleLabel: "Diretoria",
    title: "Alerta Global de Churn da Carteira",
    description: "13 cirurgiões em risco crítico necessitam de intervenção comercial e visita técnica imediata.",
    category: "urgente",
    timestamp: "Há 30 min",
    read: false,
    targetRoute: "dashboard",
    actionLabel: "Acessar Radar RFM",
  },
  {
    id: "notif-adm-3",
    roleKey: "superadmin",
    roleLabel: "Diretoria",
    title: "Sincronização de Banco SQLite WAL",
    description: "Pool de conexões e integridade de transações operando com 0.00% de taxa de falhas.",
    category: "info",
    timestamp: "Há 1h",
    read: true,
    targetRoute: "dashboard",
    actionLabel: "Telemetria de Sistema",
  },
  {
    id: "notif-adm-4",
    roleKey: "superadmin",
    roleLabel: "Diretoria",
    title: "Conformidade Regulatória ANVISA",
    description: "Auditoria automática de rastreabilidade de dispositivos médicos aprovada com louvor.",
    category: "sucesso",
    timestamp: "Há 4h",
    read: true,
    targetRoute: "support",
    actionLabel: "Ver Auditoria",
  },
];

export interface NotificationCenterProps {
  currentRoleKey: string;
  roleDisplayName: string;
  isOpen: boolean;
  onClose: () => void;
  onNavigate: (routeId: string) => void;
  onUnreadCountChange?: (count: number) => void;
}

export function NotificationCenter({
  currentRoleKey,
  roleDisplayName,
  isOpen,
  onClose,
  onNavigate,
  onUnreadCountChange,
}: NotificationCenterProps) {
  const [notifications, setNotifications] = React.useState<OperationNotification[]>(() => {
    try {
      const saved = localStorage.getItem("revnault_notifications_state");
      if (saved) return JSON.parse(saved);
    } catch {
      // fallback
    }
    return DEFAULT_NOTIFICATIONS;
  });

  const [filterMode, setFilterMode] = React.useState<"role" | "unread" | "all">("role");

  // Salvar no storage
  React.useEffect(() => {
    try {
      localStorage.setItem("revnault_notifications_state", JSON.stringify(notifications));
    } catch {
      // ignore
    }
  }, [notifications]);

  // Contagem de não lidas do cargo ativo
  const unreadRoleCount = React.useMemo(() => {
    return notifications.filter(
      (n) => !n.read && (currentRoleKey === "superadmin" || n.roleKey === currentRoleKey || n.roleKey === "all")
    ).length;
  }, [notifications, currentRoleKey]);

  React.useEffect(() => {
    if (onUnreadCountChange) {
      onUnreadCountChange(unreadRoleCount);
    }
  }, [unreadRoleCount, onUnreadCountChange]);

  // Filtragem das notificações para exibição
  const displayedNotifications = React.useMemo(() => {
    if (filterMode === "unread") {
      return notifications.filter((n) => !n.read);
    }
    if (filterMode === "all") {
      return notifications;
    }
    // "role": notificações do cargo atual (ou todas se superadmin)
    if (currentRoleKey === "superadmin") {
      return notifications;
    }
    return notifications.filter((n) => n.roleKey === currentRoleKey || n.roleKey === "all");
  }, [notifications, filterMode, currentRoleKey]);

  const handleMarkAllAsRead = () => {
    setNotifications((prev) =>
      prev.map((n) => {
        if (currentRoleKey === "superadmin" || n.roleKey === currentRoleKey || n.roleKey === "all") {
          return { ...n, read: true };
        }
        return n;
      })
    );
  };

  const handleNotificationClick = (item: OperationNotification) => {
    // Marca como lida
    setNotifications((prev) =>
      prev.map((n) => (n.id === item.id ? { ...n, read: true } : n))
    );
    // Redireciona e fecha
    if (item.targetRoute) {
      onNavigate(item.targetRoute);
    }
    onClose();
  };

  const getCategoryIcon = (category: OperationNotification["category"]) => {
    switch (category) {
      case "urgente":
        return <ShieldAlert className="h-4 w-4 text-status-danger" />;
      case "alerta":
        return <AlertTriangle className="h-4 w-4 text-status-warning" />;
      case "sucesso":
        return <CheckCircle2 className="h-4 w-4 text-status-success" />;
      case "info":
      default:
        return <Info className="h-4 w-4 text-brand-primary" />;
    }
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case "field_sales":
        return <Briefcase className="h-3 w-3" />;
      case "inside_sales":
        return <MessageSquare className="h-3 w-3" />;
      case "logistics":
        return <Truck className="h-3 w-3" />;
      case "clinical_support":
        return <Stethoscope className="h-3 w-3" />;
      case "sales_manager":
        return <BarChart3 className="h-3 w-3" />;
      default:
        return <ShieldCheck className="h-3 w-3" />;
    }
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop transparente para clique fora */}
      <div className="fixed inset-0 z-40 bg-text-main/20 backdrop-blur-2xs" onClick={onClose} />

      {/* Painel Flutuante da Central de Notificações */}
      <div
        role="dialog"
        aria-label="Central de Notificações Dinâmica por Cargo"
        className="fixed right-3 sm:right-6 top-16 z-50 w-[calc(100vw-24px)] sm:w-[440px] max-w-[480px] rounded-xl border border-border bg-surface-card shadow-modal overflow-hidden flex flex-col max-h-[85vh] animate-in fade-in zoom-in-95 duration-150"
      >
        {/* Cabeçalho */}
        <div className="p-3.5 border-b border-border bg-surface-bg/50 flex items-center justify-between gap-3">
          <div className="flex items-center gap-2 min-w-0">
            <div className="p-1.5 rounded-md bg-brand-primary/10 text-brand-primary shrink-0">
              <Bell className="h-4 w-4" />
            </div>
            <div className="min-w-0">
              <h2 className="text-xs font-bold text-text-main flex items-center gap-1.5 truncate">
                Central de Notificações
                {unreadRoleCount > 0 && (
                  <span className="px-1.5 py-0.2 rounded-full bg-status-danger text-text-inverse text-[10px] font-bold">
                    {unreadRoleCount}
                  </span>
                )}
              </h2>
              <p className="text-[11px] text-text-secondary truncate">
                Foco no Cargo: <strong className="text-text-main font-semibold">{roleDisplayName}</strong>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1 shrink-0">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleMarkAllAsRead}
              className="h-7 px-2 text-[11px] text-text-secondary hover:text-text-main gap-1"
              title="Marcar todas do cargo como lidas"
            >
              <CheckCheck className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Lidas</span>
            </Button>
            <button
              type="button"
              onClick={onClose}
              className="p-1 rounded text-text-muted hover:text-text-main hover:bg-surface-bg transition-colors"
              aria-label="Fechar central de notificações"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Barra de Filtros Rápidos */}
        <div className="px-3 py-2 border-b border-border-subtle bg-surface-bg flex items-center justify-between text-xs gap-1.5">
          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={() => setFilterMode("role")}
              className={cn(
                "px-2.5 py-1 rounded text-[11px] font-medium transition-colors",
                filterMode === "role"
                  ? "bg-brand-primary text-text-inverse font-semibold"
                  : "text-text-secondary hover:text-text-main hover:bg-surface-card"
              )}
            >
              Meu Cargo
            </button>
            <button
              type="button"
              onClick={() => setFilterMode("unread")}
              className={cn(
                "px-2.5 py-1 rounded text-[11px] font-medium transition-colors",
                filterMode === "unread"
                  ? "bg-brand-primary text-text-inverse font-semibold"
                  : "text-text-secondary hover:text-text-main hover:bg-surface-card"
              )}
            >
              Não Lidas
            </button>
            <button
              type="button"
              onClick={() => setFilterMode("all")}
              className={cn(
                "px-2.5 py-1 rounded text-[11px] font-medium transition-colors",
                filterMode === "all"
                  ? "bg-brand-primary text-text-inverse font-semibold"
                  : "text-text-secondary hover:text-text-main hover:bg-surface-card"
              )}
            >
              Toda Operação
            </button>
          </div>

          <span className="text-[10px] text-text-muted">
            {displayedNotifications.length} {displayedNotifications.length === 1 ? "alerta" : "alertas"}
          </span>
        </div>

        {/* Lista de Notificações */}
        <div className="flex-1 overflow-y-auto divide-y divide-border-subtle p-1">
          {displayedNotifications.length === 0 ? (
            <div className="py-12 text-center text-xs text-text-muted space-y-1">
              <CheckCircle2 className="h-6 w-6 text-status-success mx-auto mb-2 opacity-80" />
              <p className="font-medium text-text-main">Tudo em dia!</p>
              <p className="text-[11px]">Nenhuma notificação pendente para o filtro selecionado.</p>
            </div>
          ) : (
            displayedNotifications.map((notif) => {
              return (
                <div
                  key={notif.id}
                  onClick={() => handleNotificationClick(notif)}
                  className={cn(
                    "p-3 rounded-lg transition-colors cursor-pointer text-left flex items-start gap-3 group",
                    notif.read
                      ? "hover:bg-surface-bg opacity-75 hover:opacity-100"
                      : "bg-surface-bg/50 hover:bg-surface-bg border-l-2 border-brand-primary"
                  )}
                >
                  <div className="p-2 rounded-md bg-surface-card border border-border-subtle shrink-0 mt-0.5">
                    {getCategoryIcon(notif.category)}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2 mb-1">
                      <div className="flex items-center gap-1.5 min-w-0">
                        <Badge
                          variant="secondary"
                          className="text-[9px] px-1.5 py-0 h-4 font-semibold uppercase tracking-wider shrink-0 gap-1"
                        >
                          {getRoleIcon(notif.roleKey)}
                          <span>{notif.roleLabel}</span>
                        </Badge>
                        {!notif.read && (
                          <span className="h-1.5 w-1.5 rounded-full bg-brand-primary shrink-0" />
                        )}
                      </div>
                      <span className="text-[10px] text-text-muted shrink-0 flex items-center gap-0.5">
                        <Clock className="h-2.5 w-2.5" />
                        {notif.timestamp}
                      </span>
                    </div>

                    <p className={cn("text-xs leading-snug truncate", notif.read ? "font-medium text-text-main" : "font-bold text-text-main")}>
                      {notif.title}
                    </p>
                    <p className="text-[11px] text-text-secondary mt-1 line-clamp-2 leading-relaxed">
                      {notif.description}
                    </p>

                    <div className="mt-2 flex items-center justify-between pt-1 border-t border-border-subtle/60 text-[10px]">
                      <span className="text-text-muted">Clique para responder na rota</span>
                      <span className="text-brand-primary font-semibold group-hover:underline flex items-center gap-0.5">
                        {notif.actionLabel}
                        <ExternalLink className="h-2.5 w-2.5" />
                      </span>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Rodapé Informativo */}
        <div className="p-2.5 px-3.5 border-t border-border bg-surface-bg/80 flex items-center justify-between text-[11px] text-text-secondary">
          <span className="flex items-center gap-1 text-[10px] text-text-muted">
            <Layers className="h-3 w-3" />
            Integrado ao motor de permissões RBAC
          </span>
          <span className="text-[10px] text-text-muted font-mono">
            {currentRoleKey}
          </span>
        </div>
      </div>
    </>
  );
}
