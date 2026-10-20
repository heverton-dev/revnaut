import * as React from "react";
import {
  ShieldCheck,
  Plus,
  Trash2,
  Server,
  RefreshCw,
  FileText,
  Zap,
  UserPlus,
  Users,
  BookOpen,
  Code2,
  Webhook,
  FileDown,
  FileCode2,
  ChevronDown,
  ChevronUp,
  History,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { RouteHeader } from "@/components/ui/RouteHeader";
import { Input } from "@/components/ui/Input";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { Tabs } from "@/components/ui/Tabs";
import { Dialog } from "@/components/ui/Dialog";

export interface VaultAuditLogItem {
  id: string;
  secret_id: string;
  service_name: string;
  action: string;
  actor_email: string;
  ip_address: string;
  timestamp: string;
  status: string;
}

export interface VaultCredential {
  id: string;
  service_name: string;
  credential_type: string;
  masked_value: string;
  metadata?: Record<string, any>;
  created_at?: string;
}

export interface ErpInvoice {
  id: string;
  account_id: string;
  deal_id?: string;
  flow_type: string;
  cfop: string;
  nfe_access_key: string;
  nfe_number: string;
  danfe_url?: string;
  danfe_pdf_r2_key?: string;
  xml_r2_key?: string;
  total_amount: number;
  status: string;
  erp_type: string;
  created_at?: string;
}

export interface WebhookSub {
  id: string;
  name: string;
  target_url: string;
  subscribed_events: string[];
  is_active: boolean;
  consecutive_failures: number;
  circuit_breaker_tripped: boolean;
  signing_secret?: string;
}

export interface WebhookLog {
  id: string;
  subscription_id: string;
  event_name: string;
  target_url: string;
  http_status_code: number;
  duration_ms: number;
  status: string;
  delivered_at: string;
}

export interface UserItem {
  id: string;
  name: string;
  email: string;
  role: string;
  is_active: boolean;
  is_superadmin: boolean;
  team_name?: string;
  bu_name?: string;
}

export interface QuartetoManual {
  route_id: string;
  title: string;
  path: string;
  module: string;
  status: string;
}

export function CredentialsVaultPage({ initialTab = "vault" }: { initialTab?: string }) {
  const [activeTab, setActiveTab] = React.useState<string>(initialTab);

  // ==========================================
  // TAB 1: COFRE DE CREDENCIAIS AES-256-GCM
  // TICKET-SET-02: Log de Acesso ao Cofre
  const [showVaultAudit, setShowVaultAudit] = React.useState<boolean>(false);
  const [vaultAuditLogs, setVaultAuditLogs] = React.useState<VaultAuditLogItem[]>([]);
  const [loadingVaultAudit, setLoadingVaultAudit] = React.useState<boolean>(false);

  const fetchVaultAuditLogs = async () => {
    setLoadingVaultAudit(true);
    try {
      const res = await fetch("/api/v1/auth/credentials/audit-logs");
      if (res.ok) {
        const data = await res.json();
        setVaultAuditLogs(Array.isArray(data) ? data : []);
      }
    } catch {
      // Silencioso
    } finally {
      setLoadingVaultAudit(false);
    }
  };
  // ==========================================
  const [credentials, setCredentials] = React.useState<VaultCredential[]>([]);
  const [, setLoadingCreds] = React.useState(true);
  const [serviceName, setServiceName] = React.useState("evolution_api_v2");
  const [credentialType, setCredentialType] = React.useState("api_token");
  const [secretPayload, setSecretPayload] = React.useState("");
  const [showCredModal, setShowCredModal] = React.useState(false);
  const [feedbackMsg, setFeedbackMsg] = React.useState<string | null>(null);
  const clearFeedback = React.useCallback(() => setFeedbackMsg(null), []);

  // ==========================================
  // TAB 2: HUB FISCAL ERP WINDMILL & TOTVS
  // ==========================================
  const [invoices, setInvoices] = React.useState<ErpInvoice[]>([]);
  const [outboxItems, setOutboxItems] = React.useState<any[]>([]);
  const [, setLoadingInvoices] = React.useState(false);
  const [remittanceFeedback, setRemittanceFeedback] = React.useState<string | null>(null);
  const [erpType, setErpType] = React.useState<string>("TOTVS_PROTHEUS");

  // Formulário Emissão Remessa CFOP 5917
  const [remittanceDealId, setRemittanceDealId] = React.useState("deal-01");
  const [remittancePartnerName, setRemittancePartnerName] = React.useState("Dr. Roberto Silveira");
  const [remittanceCro, setRemittanceCro] = React.useState("CRO-SP-54321");
  const [remittanceValue, setRemittanceValue] = React.useState(24500.0);

  // Formulário Liquidação Pós-Cirúrgica 1918 + 5113
  const [settlementDealId, setSettlementDealId] = React.useState("deal-01");
  const [settlementConsumedValue, setSettlementConsumedValue] = React.useState(18500.0);
  const [settlementReturnedValue, setSettlementReturnedValue] = React.useState(6000.0);
  const [settlementFeedback, setSettlementFeedback] = React.useState<string | null>(null);

  // ==========================================
  // TAB 3: WEBHOOKS OUTBOUND & CIRCUIT BREAKER
  // ==========================================
  const [subscriptions, setSubscriptions] = React.useState<WebhookSub[]>([]);
  const [deliveryLogs, setDeliveryLogs] = React.useState<WebhookLog[]>([]);
  const [, setLoadingWebhooks] = React.useState(false);
  const [newSubName, setNewSubName] = React.useState("Webhook Protheus ERP");
  const [newSubUrl, setNewSubUrl] = React.useState("https://api.empresa.com.br/hooks/protheus");
  const [newSubSecret, setNewSubSecret] = React.useState("whsec_protheus_hmac_2026");
  const [showSubModal, setShowSubModal] = React.useState(false);
  const [testDispatchFeedback, setTestDispatchFeedback] = React.useState<any>(null);

  // ==========================================
  // TAB 4: USUÁRIOS & QUARTETO CANÔNICO
  // ==========================================
  const [users, setUsers] = React.useState<UserItem[]>([]);
  const [manuais, setManuais] = React.useState<QuartetoManual[]>([]);
  const [, setLoadingUsers] = React.useState(false);
  const [showUserModal, setShowUserModal] = React.useState(false);
  const [newUserName, setNewUserName] = React.useState("Dr. Consultor Comercial");
  const [newUserEmail, setNewUserEmail] = React.useState("consultor.novo@revnault.com");
  const [newUserRole, setNewUserRole] = React.useState("Consultor Comercial");
  const [newUserPassword, setNewUserPassword] = React.useState("RevNault@2026");

  // Carregar Credenciais
  const fetchCredentials = React.useCallback(async () => {
    setLoadingCreds(true);
    try {
      const res = await fetch("/api/v1/auth/credentials");
      if (res.ok) {
        const data = await res.json();
        setCredentials(Array.isArray(data) ? data : data.credentials || []);
      }
    } catch {
      // fallback
    } finally {
      setLoadingCreds(false);
    }
  }, []);

  // Carregar ERP & TOTVS
  const fetchErpData = React.useCallback(async () => {
    setLoadingInvoices(true);
    try {
      const [resInv, resOutbox] = await Promise.all([
        fetch("/api/v1/integrations/erp/invoices"),
        fetch("/api/v1/integrations/totvs/outbox"),
      ]);
      if (resInv.ok) {
        const invData = await resInv.json();
        const list = Array.isArray(invData) ? invData : (Array.isArray(invData?.invoices) ? invData.invoices : []);
        setInvoices(list);
      }
      if (resOutbox.ok) {
        const outboxData = await resOutbox.json();
        const list = Array.isArray(outboxData) ? outboxData : (Array.isArray(outboxData?.items) ? outboxData.items : []);
        setOutboxItems(list);
      }
    } catch {
      // fallback
    } finally {
      setLoadingInvoices(false);
    }
  }, []);

  // Carregar Webhooks
  const fetchWebhooksData = React.useCallback(async () => {
    setLoadingWebhooks(true);
    try {
      const [resSubs, resLogs] = await Promise.all([
        fetch("/api/v1/webhooks/subscriptions"),
        fetch("/api/v1/webhooks/logs"),
      ]);
      if (resSubs.ok) {
        const subsData = await resSubs.json();
        const list = Array.isArray(subsData?.subscriptions) ? subsData.subscriptions : (Array.isArray(subsData) ? subsData : []);
        setSubscriptions(list);
      }
      if (resLogs.ok) {
        const logsData = await resLogs.json();
        const list = Array.isArray(logsData?.logs) ? logsData.logs : (Array.isArray(logsData) ? logsData : []);
        setDeliveryLogs(list);
      }
    } catch {
      // fallback
    } finally {
      setLoadingWebhooks(false);
    }
  }, []);

  // Carregar Usuários & Quarteto
  const fetchUsersAndQuarteto = React.useCallback(async () => {
    setLoadingUsers(true);
    try {
      const [resUsers, resManuais] = await Promise.all([
        fetch("/api/v1/auth/users", {
          headers: { "x-user-id": "usr-superadmin-god" },
        }),
        fetch("/api/v1/quarteto/manuais"),
      ]);
      if (resUsers.ok) {
        const usersData = await resUsers.json();
        const list = Array.isArray(usersData) ? usersData : (Array.isArray(usersData?.users) ? usersData.users : []);
        setUsers(list);
      }
      if (resManuais.ok) {
        const manuaisData = await resManuais.json();
        const list = Array.isArray(manuaisData?.manuais) ? manuaisData.manuais : (Array.isArray(manuaisData) ? manuaisData : []);
        setManuais(list);
      }
    } catch {
      // fallback
    } finally {
      setLoadingUsers(false);
    }
  }, []);

  React.useEffect(() => {
    if (activeTab === "vault") fetchCredentials();
    if (activeTab === "erp") fetchErpData();
    if (activeTab === "webhooks") fetchWebhooksData();
    if (activeTab === "users") fetchUsersAndQuarteto();
  }, [activeTab, fetchCredentials, fetchErpData, fetchWebhooksData, fetchUsersAndQuarteto]);

  // Ações Tab 1: Credenciais
  const handleSaveCredential = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!secretPayload.trim()) return;
    try {
      const res = await fetch("/api/v1/auth/credentials", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          service_name: serviceName,
          credential_type: credentialType,
          secret_value: secretPayload,
        }),
      });
      if (!res.ok) throw new Error("Falha ao salvar credencial");
      setShowCredModal(false);
      setSecretPayload("");
      await fetchCredentials();
    } catch (err: any) {
      alert(err.message || "Erro");
    }
  };

  const handleDeleteCredential = async (id: string) => {
    if (!confirm("Confirma remoção permanente desta credencial do cofre AES-256-GCM?")) return;
    try {
      const res = await fetch(`/api/v1/auth/credentials/${id}`, { method: "DELETE" });
      if (res.ok) await fetchCredentials();
    } catch {
      // fallback
    }
  };

  // Ações Tab 2: Emissão NF-e
  const handleEmitRemittance = async (e: React.FormEvent) => {
    e.preventDefault();
    setRemittanceFeedback(null);
    try {
      const res = await fetch("/api/v1/integrations/erp/remittance/emit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          deal_id: remittanceDealId,
          partner_name: remittancePartnerName,
          partner_cro_uf: remittanceCro,
          total_amount: Number(remittanceValue),
          erp_type: erpType,
          account_id: "0f14ffff",
        }),
      });
      if (!res.ok) throw new Error("Erro ao emitir NF-e de Remessa");
      const data = await res.json();
      setRemittanceFeedback(`NF-e Remessa emitido! Chave: ${data.nfe_access_key} | CFOP: ${data.cfop}`);
      await fetchErpData();
    } catch (err: any) {
      setRemittanceFeedback(`Erro: ${err.message}`);
    }
  };

  const handleEmitSettlement = async (e: React.FormEvent) => {
    e.preventDefault();
    setSettlementFeedback(null);
    try {
      const res = await fetch("/api/v1/integrations/erp/settlement/emit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          deal_id: settlementDealId,
          consumed_amount: Number(settlementConsumedValue),
          returned_amount: Number(settlementReturnedValue),
          erp_type: erpType,
          account_id: "0f14ffff",
        }),
      });
      if (!res.ok) throw new Error("Erro ao emitir liquidação pós-operatória");
      const data = await res.json();
      setSettlementFeedback(`Liquidação concluída! Venda: ${data.sale_invoice?.nfe_access_key} | Retorno: ${data.symbolic_return_invoice?.nfe_access_key}`);
      await fetchErpData();
    } catch (err: any) {
      setSettlementFeedback(`Erro: ${err.message}`);
    }
  };

  // Ações Tab 3: Webhooks
  const handleCreateWebhookSub = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch("/api/v1/webhooks/subscriptions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: newSubName,
          target_url: newSubUrl,
          signing_secret: newSubSecret,
          subscribed_events: ["*"],
          account_id: "0f14ffff",
        }),
      });
      if (!res.ok) throw new Error("Erro ao criar webhook");
      setShowSubModal(false);
      await fetchWebhooksData();
    } catch (err: any) {
      alert(err.message || "Erro");
    }
  };

  const handleDeleteWebhookSub = async (id: string) => {
    if (!confirm("Remover esta assinatura de webhook outbound?")) return;
    try {
      const res = await fetch(`/api/v1/webhooks/subscriptions/${id}`, { method: "DELETE" });
      if (res.ok) await fetchWebhooksData();
    } catch {
      // fallback
    }
  };

  const handleResetCircuitBreaker = async (id: string) => {
    try {
      const res = await fetch(`/api/v1/webhooks/subscriptions/${id}/reset-circuit`, { method: "PATCH" });
      if (res.ok) {
        alert("Circuit breaker resetado com sucesso!");
        await fetchWebhooksData();
      }
    } catch {
      // fallback
    }
  };

  const handleTestWebhookDispatch = async (subId: string) => {
    setTestDispatchFeedback(null);
    try {
      const res = await fetch("/api/v1/webhooks/test-dispatch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          subscription_id: subId,
          event_name: "deal.stage_changed",
          account_id: "0f14ffff",
        }),
      });
      const data = await res.json();
      setTestDispatchFeedback(data);
      await fetchWebhooksData();
    } catch (err: any) {
      setTestDispatchFeedback({ error: err.message });
    }
  };

  // Ações Tab 4: Usuários
  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch("/api/v1/auth/users", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-user-id": "usr-superadmin-god",
        },
        body: JSON.stringify({
          name: newUserName,
          email: newUserEmail,
          role: newUserRole,
          password: newUserPassword,
        }),
      });
      if (!res.ok) throw new Error("Erro ao criar usuário");
      setShowUserModal(false);
      await fetchUsersAndQuarteto();
    } catch (err: any) {
      alert(err.message || "Erro");
    }
  };

  const handleToggleUserStatus = async (userId: string, currentActive: boolean) => {
    try {
      const res = await fetch(`/api/v1/auth/users/${userId}/status`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "x-user-id": "usr-superadmin-god",
        },
        body: JSON.stringify({ is_active: !currentActive }),
      });
      if (res.ok) await fetchUsersAndQuarteto();
    } catch {
      // fallback
    }
  };

  const handleResetUserPassword = async (userId: string) => {
    const pwd = prompt("Informe a nova senha temporária para o usuário:", "RevNault@2026Nova");
    if (!pwd) return;
    try {
      const res = await fetch(`/api/v1/auth/users/${userId}/reset-password`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-user-id": "usr-superadmin-god",
        },
        body: JSON.stringify({ new_password: pwd }),
      });
      if (res.ok) alert("Senha redefinida com sucesso!");
    } catch {
      // fallback
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <RouteHeader
        title="Configurações Enterprise, Hub Fiscal ERP & Governança"
        description="Cofre cifrado AES-256-GCM, emissão de NF-e CFOP 5917/1918/5113, webhooks com circuit breaker e canais canônicos."
        badge={
          <Badge variant="outline" className="border-brand-primary/30 text-brand-primary bg-brand-primary-subtle text-xs">
            Windmill + Protheus + Webhooks + Quarteto
          </Badge>
        }
      />

      {/* Tabs */}
      <Tabs
        activeTab={activeTab}
        onChange={(tabId) => setActiveTab(tabId)}
        hideOnDesktop
        tabs={[
          { id: "vault", label: "Cofre Cifrado AES-256", count: credentials.length },
          { id: "erp", label: "Hub Fiscal ERP & TOTVS", count: invoices.length },
          { id: "webhooks", label: "Webhooks & Circuit Breaker", count: subscriptions.length },
          { id: "users", label: "Usuários & Quarteto Canônico", count: users.length },
        ]}
      />

      {/* ========================================================================= */}
      {/* TAB 1: COFRE DE CREDENCIAIS AES-256-GCM */}
      {/* ========================================================================= */}
      {activeTab === "vault" && (
        <div className="space-y-4">
          {feedbackMsg && (
            <div className="p-3 rounded-lg bg-status-success-subtle border border-status-success/30 text-xs text-status-success flex items-center justify-between">
              <span>{feedbackMsg}</span>
              <button type="button" onClick={clearFeedback} className="underline">Fechar</button>
            </div>
          )}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <ShieldCheck className="h-4 w-4 text-status-success" />
              <span className="text-xs font-semibold text-text-main">
                Segredos protegidos por chave mestra AES-256-GCM e rotação de credenciais
              </span>
            </div>
            <Button size="sm" variant="default" onClick={() => setShowCredModal(true)} className="text-xs">
              <Plus className="h-3.5 w-3.5 mr-1" />
              Nova Credencial
            </Button>
          </div>

          <Card className="p-4 border border-border bg-surface-card space-y-3">
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {credentials.map((c) => (
                <div key={c.id} className="p-3 rounded-lg border border-border bg-surface-bg flex items-center justify-between text-xs">
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-text-main">{c.service_name}</span>
                      <span className="px-1.5 py-0.5 rounded text-[10px] uppercase font-mono bg-brand-navy-subtle text-brand-navy border border-border">
                        {c.credential_type}
                      </span>
                    </div>
                    <div className="font-mono text-text-muted text-[11px]">
                      {c.masked_value}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] text-text-muted font-mono">{c.id}</span>
                    <button
                      onClick={async () => {
                        try {
                          const newRotatedSecret = `sk_live_${Math.random().toString(36).substring(2)}${Math.random().toString(36).substring(2)}`;
                          const res = await fetch("/api/v1/auth/credentials", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({
                              service_name: c.service_name,
                              credential_type: c.credential_type,
                              secret_payload: newRotatedSecret,
                              metadata: { rotated_at: new Date().toISOString() },
                            }),
                          });
                          if (!res.ok) throw new Error("Falha ao rotacionar credencial no cofre.");
                          await fetchCredentials();
                          setFeedbackMsg(`Chave do serviço ${c.service_name} rotacionada e persistida no cofre (AES-256-GCM).`);
                        } catch (err: any) {
                          alert(err.message || "Erro na rotação da credencial.");
                        }
                      }}
                      className="p-1 rounded text-brand-primary hover:bg-brand-primary-subtle"
                      title="Rotacionar Chave Automaticamente"
                    >
                      <RefreshCw className="h-3.5 w-3.5" />
                    </button>
                    <button
                      onClick={() => handleDeleteCredential(c.id)}
                      className="p-1 rounded text-status-danger hover:bg-status-danger-subtle"
                      title="Excluir Credencial"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {/* TICKET-SET-02: Painel Colapsável de Log de Acesso ao Cofre (AES-256-GCM) */}
          <Card className="border border-border bg-surface-card overflow-hidden">
            <button
              type="button"
              onClick={() => {
                const next = !showVaultAudit;
                setShowVaultAudit(next);
                if (next && vaultAuditLogs.length === 0) {
                  fetchVaultAuditLogs();
                }
              }}
              className="w-full p-4 flex items-center justify-between text-left hover:bg-surface-bg/50 transition cursor-pointer"
            >
              <div className="flex items-center gap-2">
                <History className="h-4 w-4 text-brand-primary" />
                <div>
                  <h4 className="text-xs font-bold text-text-main">
                    Log de Acesso ao Cofre (AES-256-GCM)
                  </h4>
                  <p className="text-[11px] text-text-secondary">
                    Registro forense de consultas, rotações e acessos aos segredos criptografados
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="text-[10px]">
                  {vaultAuditLogs.length > 0 ? `${vaultAuditLogs.length} acessos registrados` : "Clique para expandir"}
                </Badge>
                {showVaultAudit ? (
                  <ChevronUp className="h-4 w-4 text-text-muted" />
                ) : (
                  <ChevronDown className="h-4 w-4 text-text-muted" />
                )}
              </div>
            </button>

            {showVaultAudit && (
              <div className="border-t border-border p-4 space-y-3 bg-surface-bg/30">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-mono text-text-secondary">
                    Trilha de Auditoria Criptográfica (Zero Stubs)
                  </span>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={fetchVaultAuditLogs}
                    disabled={loadingVaultAudit}
                    className="text-xs h-7 gap-1"
                  >
                    <RefreshCw className={`h-3 w-3 ${loadingVaultAudit ? "animate-spin" : ""}`} />
                    Atualizar Logs
                  </Button>
                </div>

                {loadingVaultAudit ? (
                  <div className="py-6 text-center text-xs text-text-secondary">
                    Carregando trilha de auditoria do cofre...
                  </div>
                ) : vaultAuditLogs.length === 0 ? (
                  <div className="py-6 text-center text-xs text-text-secondary">
                    Nenhum registro de acesso recente encontrado no cofre.
                  </div>
                ) : (
                  <div className="space-y-2 max-h-72 overflow-y-auto">
                    {vaultAuditLogs.map((log) => (
                      <div
                        key={log.id}
                        className="p-2.5 rounded-lg border border-border bg-surface-card flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs"
                      >
                        <div className="space-y-0.5">
                          <div className="flex items-center gap-2">
                            <Badge
                              variant={log.action === "ROTATE" ? "warning" : log.action === "CREATE" ? "success" : "outline"}
                              className="text-[10px] font-mono uppercase"
                            >
                              {log.action}
                            </Badge>
                            <span className="font-semibold text-text-main">{log.service_name}</span>
                            <span className="text-[10px] font-mono text-text-muted">({log.secret_id})</span>
                          </div>
                          <div className="text-[11px] text-text-secondary">
                            Operador: <span className="font-mono text-text-main">{log.actor_email}</span> - IP:{" "}
                            <span className="font-mono">{log.ip_address}</span>
                          </div>
                        </div>
                        <div className="text-left sm:text-right">
                          <span className="text-[10px] font-mono text-text-secondary block">
                            {new Date(log.timestamp).toLocaleString("pt-BR")}
                          </span>
                          <span className="text-[10px] font-mono uppercase text-status-success font-semibold">
                            {log.status}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </Card>

          {/* Modal Nova Credencial Padronizado */}
          <Dialog
            isOpen={showCredModal}
            onClose={() => setShowCredModal(false)}
            size="confirm"
            title="Adicionar Credencial Cifrada"
            description="Armazenamento seguro com cifragem AES-256 no cofre operacional."
          >
            <form onSubmit={handleSaveCredential} className="space-y-2.5">
                  <div>
                    <label className="text-[11px] text-text-secondary block mb-1">Serviço de Destino</label>
                    <select
                      value={serviceName}
                      onChange={(e) => setServiceName(e.target.value)}
                      className="w-full p-1.5 rounded border border-border bg-surface-bg text-xs"
                    >
                      <option value="evolution_api_v2">Evolution API v2 WhatsApp</option>
                      <option value="cloudflare_r2">Cloudflare R2 Storage</option>
                      <option value="windmill_erp">Windmill ERP Engine</option>
                      <option value="totvs_protheus">TOTVS Protheus REST API</option>
                      <option value="listmonk_engine">Listmonk Marketing</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-[11px] text-text-secondary block mb-1">Tipo de Segredo</label>
                    <select
                      value={credentialType}
                      onChange={(e) => setCredentialType(e.target.value)}
                      className="w-full p-1.5 rounded border border-border bg-surface-bg text-xs"
                    >
                      <option value="api_token">Bearer Token / API Key</option>
                      <option value="a1_certificate">Certificado Digital A1 (.pfx)</option>
                      <option value="basic_auth">Basic Auth (user:pass)</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-[11px] text-text-secondary block mb-1">Valor do Segredo (Será Cifrado)</label>
                    <Input
                      type="password"
                      value={secretPayload}
                      onChange={(e) => setSecretPayload(e.target.value)}
                      placeholder="token_secreto_ou_chave"
                      required
                    />
                  </div>
                  <div className="flex justify-end gap-2 pt-3 border-t border-border-subtle">
                    <Button type="button" variant="outline" size="sm" onClick={() => setShowCredModal(false)}>Cancelar</Button>
                    <Button type="submit" variant="default" size="sm">Cifrar & Salvar</Button>
                  </div>
                </form>
          </Dialog>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 2: HUB FISCAL ERP WINDMILL & TOTVS PROTHEUS */}
      {/* ========================================================================= */}
      {activeTab === "erp" && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Emissão de Remessa CFOP 5917 */}
            <Card className="p-4 border border-border bg-surface-card space-y-3">
              <div className="flex items-center justify-between border-b border-border pb-2">
                <h3 className="text-xs font-bold text-text-main flex items-center gap-1.5">
                  <FileText className="h-4 w-4 text-brand-primary" />
                  Emitir NF-e de Remessa em Consignação (CFOP 5.917 / 6.917)
                </h3>
                <Badge variant="outline" className="text-[10px]">ERP Windmill</Badge>
              </div>

              <form onSubmit={handleEmitRemittance} className="space-y-2 text-xs">
                <div>
                  <label className="text-[11px] font-semibold text-text-secondary block mb-0.5">ID da Oportunidade / Deal</label>
                  <Input value={remittanceDealId} onChange={(e) => setRemittanceDealId(e.target.value)} required />
                </div>
                <div>
                  <label className="text-[11px] font-semibold text-text-secondary block mb-0.5">Nome do Parceiro Cirurgião</label>
                  <Input value={remittancePartnerName} onChange={(e) => setRemittancePartnerName(e.target.value)} required />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-[11px] font-semibold text-text-secondary block mb-0.5">CRO/UF</label>
                    <Input value={remittanceCro} onChange={(e) => setRemittanceCro(e.target.value)} required />
                  </div>
                  <div>
                    <label className="text-[11px] font-semibold text-text-secondary block mb-0.5">Valor Remessa R$</label>
                    <Input type="number" value={remittanceValue} onChange={(e) => setRemittanceValue(Number(e.target.value))} required />
                  </div>
                </div>
                <div>
                  <label className="text-[11px] font-semibold text-text-secondary block mb-0.5">ERP de Destino</label>
                  <select
                    value={erpType}
                    onChange={(e) => setErpType(e.target.value)}
                    className="w-full px-2.5 py-1.5 rounded-lg border border-border bg-surface-bg text-xs text-text-main"
                  >
                    <option value="TOTVS_PROTHEUS">TOTVS Protheus</option>
                    <option value="SAP_B1">SAP Business One</option>
                    <option value="SANKHYA">Sankhya</option>
                  </select>
                </div>
                <Button type="submit" variant="default" size="sm" className="w-full text-xs mt-2">
                  Despachar NF-e Remessa ao ERP
                </Button>
              </form>

              {remittanceFeedback && (
                <p className="text-xs font-mono text-status-success bg-status-success-subtle p-2 rounded border border-status-success/30">
                  {remittanceFeedback}
                </p>
              )}
            </Card>

            {/* Liquidação Pós-Cirúrgica 1918 + 5113 */}
            <Card className="p-4 border border-border bg-surface-card space-y-3">
              <div className="flex items-center justify-between border-b border-border pb-2">
                <h3 className="text-xs font-bold text-text-main flex items-center gap-1.5">
                  <Zap className="h-4 w-4 text-status-warning" />
                  Liquidação Pós-Op: Retorno 1.918 + Venda 5.113
                </h3>
                <Badge variant="outline" className="text-[10px]">Dupla Emissão</Badge>
              </div>

              <form onSubmit={handleEmitSettlement} className="space-y-2 text-xs">
                <div>
                  <label className="text-[11px] font-semibold text-text-secondary block mb-0.5">ID do Deal Faturado</label>
                  <Input value={settlementDealId} onChange={(e) => setSettlementDealId(e.target.value)} required />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-[11px] font-semibold text-text-secondary block mb-0.5">Valor Consumido R$ (Venda 5113)</label>
                    <Input type="number" value={settlementConsumedValue} onChange={(e) => setSettlementConsumedValue(Number(e.target.value))} required />
                  </div>
                  <div>
                    <label className="text-[11px] font-semibold text-text-secondary block mb-0.5">Valor Retornado R$ (Simbólico 1918)</label>
                    <Input type="number" value={settlementReturnedValue} onChange={(e) => setSettlementReturnedValue(Number(e.target.value))} required />
                  </div>
                </div>
                <div>
                  <label className="text-[11px] font-semibold text-text-secondary block mb-0.5">ERP de Destino</label>
                  <select
                    value={erpType}
                    onChange={(e) => setErpType(e.target.value)}
                    className="w-full px-2.5 py-1.5 rounded-lg border border-border bg-surface-bg text-xs text-text-main"
                  >
                    <option value="TOTVS_PROTHEUS">TOTVS Protheus</option>
                    <option value="SAP_B1">SAP Business One</option>
                    <option value="SANKHYA">Sankhya</option>
                  </select>
                </div>
                <Button type="submit" variant="secondary" size="sm" className="w-full text-xs mt-2">
                  Liquidar Cirurgia no ERP
                </Button>
              </form>

              {settlementFeedback && (
                <p className="text-xs font-mono text-status-success bg-status-success-subtle p-2 rounded border border-status-success/30">
                  {settlementFeedback}
                </p>
              )}
            </Card>
          </div>

          {/* Tabela de Notas Fiscais Emitidas */}
          <Card className="p-4 border border-border bg-surface-card space-y-3">
            <div className="flex items-center justify-between border-b border-border pb-2">
              <div className="flex items-center gap-2">
                <h3 className="text-xs font-bold text-text-main">Histórico de Notas Fiscais Emitidas ({invoices.length})</h3>
                <span className="text-[11px] font-mono text-text-secondary">Outbox TOTVS: {outboxItems.length} pendentes</span>
              </div>
              <Button size="sm" variant="outline" onClick={fetchErpData} className="text-xs h-7 py-0">
                <RefreshCw className="h-3 w-3 mr-1" /> Atualizar
              </Button>
            </div>

            <div className="space-y-2 max-h-72 overflow-y-auto">
              {invoices.map((inv) => (
                <div key={inv.id} className="p-2.5 rounded-lg border border-border bg-surface-bg flex items-center justify-between text-xs">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-text-main font-mono">{inv.cfop}</span>
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-brand-navy-subtle text-brand-navy font-semibold">
                        {inv.flow_type}
                      </span>
                      <span className="font-mono text-text-muted">{inv.nfe_number}</span>
                    </div>
                    <div className="text-[10px] text-text-secondary font-mono truncate max-w-md mt-0.5">
                      Chave: {inv.nfe_access_key}
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <div className="text-right font-mono">
                      <span className="font-bold text-text-main block">
                        R$ {inv.total_amount?.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                      </span>
                      <span className="text-[10px] text-status-success">{inv.status}</span>
                    </div>
                    <div className="flex gap-1.5">
                      <a
                        href={`/api/v1/storage/files/${inv.danfe_pdf_r2_key || `0f14ffff/erp_invoices/${inv.nfe_number}.pdf`}`}
                        target="_blank"
                        rel="noreferrer"
                        className="flex items-center gap-1 px-2 py-1 rounded border border-border bg-surface-card text-[10px] text-brand-primary hover:border-brand-primary"
                      >
                        <FileDown className="h-3 w-3" />
                        Abrir DANFE (PDF)
                      </a>
                      <a
                        href={`/api/v1/storage/files/${inv.xml_r2_key || `0f14ffff/erp_invoices/${inv.nfe_number}.xml`}`}
                        download
                        className="flex items-center gap-1 px-2 py-1 rounded border border-border bg-surface-card text-[10px] text-brand-primary hover:border-brand-primary"
                      >
                        <FileCode2 className="h-3 w-3" />
                        Baixar XML NF-e
                      </a>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 3: WEBHOOKS OUTBOUND & CIRCUIT BREAKER */}
      {/* ========================================================================= */}
      {activeTab === "webhooks" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-text-secondary">
              Endpoints de Destino & Proteção de Resiliência
            </h3>
            <Button size="sm" variant="default" onClick={() => setShowSubModal(true)} className="text-xs">
              <Plus className="h-3.5 w-3.5 mr-1" />
              Novo Webhook
            </Button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Assinaturas */}
            <Card className="p-4 border border-border bg-surface-card space-y-3">
              <h4 className="text-xs font-bold text-text-main">Assinaturas Ativas ({subscriptions.length})</h4>
              <div className="space-y-2 max-h-80 overflow-y-auto">
                {subscriptions.map((sub) => (
                  <div key={sub.id} className="p-3 rounded-lg border border-border bg-surface-bg text-xs space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-text-main">{sub.name}</span>
                      <span
                        className={`text-[10px] font-bold px-1.5 py-0.5 rounded border ${
                          sub.circuit_breaker_tripped
                            ? "bg-status-danger-subtle text-status-danger border-status-danger/30"
                            : "bg-status-success-subtle text-status-success border-status-success/30"
                        }`}
                      >
                        {sub.circuit_breaker_tripped ? "CIRCUIT TRIPPED (BLOQUEADO)" : "OPERACIONAL"}
                      </span>
                    </div>

                    <div className="font-mono text-[10px] text-text-secondary truncate">
                      {sub.target_url}
                    </div>

                    <div className="flex items-center justify-between pt-1 border-t border-border/50 text-[10px]">
                      <span>Falhas seguidas: <strong>{sub.consecutive_failures}</strong></span>
                      <div className="flex gap-1.5">
                        {sub.circuit_breaker_tripped && (
                          <button
                            onClick={() => handleResetCircuitBreaker(sub.id)}
                            className="px-2 py-0.5 rounded bg-status-warning-subtle text-status-warning hover:bg-status-warning/20 font-semibold"
                          >
                            Reset Circuit
                          </button>
                        )}
                        <button
                          onClick={() => handleTestWebhookDispatch(sub.id)}
                          className="px-2 py-0.5 rounded bg-brand-primary text-text-inverse hover:bg-brand-primary-hover font-semibold"
                        >
                          Disparo Teste
                        </button>
                        <button
                          onClick={() => handleDeleteWebhookSub(sub.id)}
                          className="px-1 text-status-danger hover:bg-status-danger-subtle rounded"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Logs de Entrega */}
            <Card className="p-4 border border-border bg-surface-card space-y-3">
              <h4 className="text-xs font-bold text-text-main">Telemetria de Entrega HMAC-SHA256</h4>
              <div className="space-y-1.5 max-h-80 overflow-y-auto">
                {deliveryLogs.map((log) => (
                  <div key={log.id} className="p-2 rounded border border-border bg-surface-bg flex items-center justify-between text-[11px] font-mono">
                    <div>
                      <span className="font-bold text-brand-primary">{log.event_name}</span>
                      <span className="text-text-muted ml-2">{log.duration_ms}ms</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      {!(log.status === "DELIVERED" || log.http_status_code === 200) && (
                        <button
                          onClick={async () => {
                            try {
                              const res = await fetch("/api/v1/webhooks/outbound/dispatch-test", {
                                method: "POST",
                                headers: { "Content-Type": "application/json" },
                                body: JSON.stringify({
                                  subscription_id: log.subscription_id,
                                  event_name: log.event_name || "dentgo.order_delivered",
                                }),
                              });
                              const data = await res.json().catch(() => ({}));
                              setTestDispatchFeedback(data);
                              await fetchWebhooksData();
                            } catch (err: any) {
                              setTestDispatchFeedback({ replayed_log_id: log.id, error: err.message });
                            }
                          }}
                          className="px-2 py-0.5 rounded bg-brand-primary-subtle text-brand-primary border border-brand-primary/30 hover:bg-brand-primary hover:text-text-inverse text-[10px] font-semibold"
                          title="Re-tentativa Manual (Replay)"
                        >
                          Replay
                        </button>
                      )}
                      <span
                        className={`font-bold px-1.5 py-0.5 rounded text-[10px] ${
                          log.status === "DELIVERED" || log.http_status_code === 200
                            ? "text-status-success bg-status-success-subtle"
                            : "text-status-danger bg-status-danger-subtle"
                        }`}
                      >
                        HTTP {log.http_status_code || 200}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              {testDispatchFeedback && (
                <div className="p-2 bg-surface-bg rounded border border-border text-[10px] font-mono">
                  <div className="font-bold text-text-main">Disparo de Teste:</div>
                  <pre className="text-text-secondary overflow-x-auto mt-0.5">
                    {JSON.stringify(testDispatchFeedback, null, 2)}
                  </pre>
                </div>
              )}
            </Card>
          </div>

          {/* Modal Criar Assinatura Webhook Padronizado */}
          <Dialog
            isOpen={showSubModal}
            onClose={() => setShowSubModal(false)}
            size="confirm"
            title="Novo Endpoint Webhook Outbound"
            description="Cadastre um endpoint para receber eventos de negócios assinados com HMAC SHA-256."
          >
            <form onSubmit={handleCreateWebhookSub} className="space-y-2">
                  <Input
                    placeholder="Nome da Integração"
                    value={newSubName}
                    onChange={(e) => setNewSubName(e.target.value)}
                    required
                  />
                  <Input
                    placeholder="URL de Destino (HTTPS)"
                    value={newSubUrl}
                    onChange={(e) => setNewSubUrl(e.target.value)}
                    required
                  />
                  <Input
                    placeholder="Chave Secreta HMAC (Signing Secret)"
                    value={newSubSecret}
                    onChange={(e) => setNewSubSecret(e.target.value)}
                    required
                  />
                  <div className="flex justify-end gap-2 pt-3 border-t border-border-subtle">
                    <Button type="button" variant="outline" size="sm" onClick={() => setShowSubModal(false)}>Cancelar</Button>
                    <Button type="submit" variant="default" size="sm">Salvar Webhook</Button>
                  </div>
                </form>
          </Dialog>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 4: GESTÃO DE USUÁRIOS & QUARTETO CANÔNICO */}
      {/* ========================================================================= */}
      {activeTab === "users" && (
        <div className="space-y-4">
          {/* Quarteto Canônico Ativo */}
          <Card className="p-4 border border-border bg-surface-card space-y-3">
            <div className="flex items-center justify-between border-b border-border pb-2">
              <div className="flex items-center gap-2">
                <BookOpen className="h-4 w-4 text-brand-primary" />
                <h3 className="text-xs font-bold text-text-main uppercase tracking-wider">
                  Os 4 Pilares Canônicos de Auto-Documentação (Lei #10)
                </h3>
              </div>
              <Badge variant="navy" className="text-[10px]">Sine Qua Non</Badge>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <a
                href="/docs"
                target="_blank"
                rel="noreferrer"
                className="p-3 rounded-lg border border-border bg-surface-bg hover:border-brand-primary transition flex flex-col items-center text-center gap-1.5"
              >
                <Code2 className="h-5 w-5 text-brand-primary" />
                <span className="font-bold text-xs text-text-main">Swagger Studio</span>
                <span className="text-[10px] text-text-muted font-mono">/docs (OpenAPI 3.1)</span>
              </a>

              <a
                href="/webhooks"
                target="_blank"
                rel="noreferrer"
                className="p-3 rounded-lg border border-border bg-surface-bg hover:border-brand-primary transition flex flex-col items-center text-center gap-1.5"
              >
                <Webhook className="h-5 w-5 text-brand-primary" />
                <span className="font-bold text-xs text-text-main">Webhook Studio</span>
                <span className="text-[10px] text-text-muted font-mono">/webhooks</span>
              </a>

              <a
                href="/mcp"
                target="_blank"
                rel="noreferrer"
                className="p-3 rounded-lg border border-border bg-surface-bg hover:border-brand-primary transition flex flex-col items-center text-center gap-1.5"
              >
                <Server className="h-5 w-5 text-brand-primary" />
                <span className="font-bold text-xs text-text-main">MCP Studio</span>
                <span className="text-[10px] text-text-muted font-mono">/mcp (Tools AI)</span>
              </a>

              <a
                href="/docs/guia"
                target="_blank"
                rel="noreferrer"
                className="p-3 rounded-lg border border-border bg-surface-bg hover:border-brand-primary transition flex flex-col items-center text-center gap-1.5"
              >
                <BookOpen className="h-5 w-5 text-brand-primary" />
                <span className="font-bold text-xs text-text-main">Guia Canônico</span>
                <span className="text-[10px] text-text-muted font-mono">/docs/guia ({manuais.length} rotas)</span>
              </a>
            </div>
          </Card>

          {/* Gestão de Colaboradores */}
          <Card className="p-4 border border-border bg-surface-card space-y-3">
            <div className="flex items-center justify-between border-b border-border pb-2">
              <h3 className="text-xs font-bold text-text-main flex items-center gap-1.5">
                <Users className="h-4 w-4 text-brand-primary" />
                Colaboradores do Tenant ({users.length})
              </h3>
              <Button size="sm" variant="default" onClick={() => setShowUserModal(true)} className="text-xs">
                <UserPlus className="h-3.5 w-3.5 mr-1" />
                Novo Colaborador
              </Button>
            </div>

            <div className="space-y-2 max-h-80 overflow-y-auto">
              {users.map((u) => (
                <div key={u.id} className="p-2.5 rounded-lg border border-border bg-surface-bg flex items-center justify-between text-xs">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-text-main">{u.name}</span>
                      <span className="text-[10px] font-mono text-text-secondary font-semibold">({u.role})</span>
                      {u.is_superadmin && (
                        <Badge variant="navy" className="text-[9px]">Super Admin</Badge>
                      )}
                    </div>
                    <div className="text-[11px] text-text-muted font-mono mt-0.5">
                      {u.email} | {u.team_name || "Sem equipe fixa"}
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleToggleUserStatus(u.id, u.is_active)}
                      className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${
                        u.is_active
                          ? "bg-status-success-subtle text-status-success border-status-success/30"
                          : "bg-surface-card text-text-muted border-border"
                      }`}
                    >
                      {u.is_active ? "ATIVO" : "INATIVO"}
                    </button>
                    <button
                      onClick={() => handleResetUserPassword(u.id)}
                      className="px-2 py-0.5 rounded bg-surface-card hover:bg-surface-bg border border-border text-[10px] text-text-secondary"
                    >
                      Reset Senha
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {/* Modal Criar Colaborador Padronizado */}
          <Dialog
            isOpen={showUserModal}
            onClose={() => setShowUserModal(false)}
            size="confirm"
            title="Cadastrar Colaborador"
            description="Adicione novos membros da equipe e configure credenciais de acesso inicial."
          >
            <form onSubmit={handleCreateUser} className="space-y-2">
                  <Input
                    placeholder="Nome Completo"
                    value={newUserName}
                    onChange={(e) => setNewUserName(e.target.value)}
                    required
                  />
                  <Input
                    type="email"
                    placeholder="E-mail"
                    value={newUserEmail}
                    onChange={(e) => setNewUserEmail(e.target.value)}
                    required
                  />
                  <Input
                    placeholder="Cargo / Função"
                    value={newUserRole}
                    onChange={(e) => setNewUserRole(e.target.value)}
                    required
                  />
                  <Input
                    type="password"
                    placeholder="Senha Inicial"
                    value={newUserPassword}
                    onChange={(e) => setNewUserPassword(e.target.value)}
                    required
                  />
                  <div className="flex justify-end gap-2 pt-3 border-t border-border-subtle">
                    <Button type="button" variant="outline" size="sm" onClick={() => setShowUserModal(false)}>Cancelar</Button>
                    <Button type="submit" variant="default" size="sm">Cadastrar</Button>
                  </div>
                </form>
          </Dialog>
        </div>
      )}
    </div>
  );
}

export default CredentialsVaultPage;
