import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import { AppShell } from "@/components/layout/AppShell";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { DataTable, Column } from "@/components/ui/DataTable";
import { KanbanBoard, KanbanStage } from "@/components/ui/KanbanBoard";
import { Dialog } from "@/components/ui/Dialog";
import { Sheet } from "@/components/ui/Sheet";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorBoundary } from "@/components/ui/ErrorBoundary";
import { Deal } from "@/types/api_contracts";
import {
  Plus,
  RefreshCw,
  FileText,
  AlertCircle,
  Download,
  LayoutGrid,
  List,
  Search,
  CheckCircle2,
  Clock,
  ShieldCheck,
  CheckSquare,
  Square,
  Save,
} from "lucide-react";
import { AppRouter } from "./router";
import { LoginPage } from "@/features/auth/LoginPage";

interface MetricsSummary {
  total_deals?: number;
  totalDeals?: number;
  pipeline_value?: number;
  pipelineTotal?: number;
  mrr?: number;
  closedWonMRR?: number;
  conversion_rate?: number;
  conversionRate?: number;
}

interface PipelineItem {
  id: number;
  name: string;
}

interface StageItem {
  id: number;
  name: string;
  pipeline_id?: number;
}

interface TaskItem {
  id: string;
  title: string;
  due_date: string;
  assignee: string;
  priority: string;
  completed: number | boolean;
}

interface TimelineEntry {
  id?: string | number;
  action?: string;
  event_type?: string;
  description?: string;
  details?: string;
  created_at?: string;
  timestamp?: string;
  user_name?: string;
}

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
    if (typeof window === "undefined") return "usr-superadmin-god";
    return localStorage.getItem("revnaut_user_id") || "usr-superadmin-god";
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

  // Estados de filtro, busca e visão de Deals (HOMOLOG-03)
  const [selectedPipelineId, setSelectedPipelineId] = React.useState<string>("1");
  const [searchTerm, setSearchTerm] = React.useState<string>("");
  const [viewMode, setViewMode] = React.useState<"table" | "kanban">("table");

  // Modal de Criação de Novo Negócio
  const [isNewDealOpen, setIsNewDealOpen] = React.useState<boolean>(false);
  const [newDealTitle, setNewDealTitle] = React.useState<string>("");
  const [newDealCompany, setNewDealCompany] = React.useState<string>("");
  const [newDealContact, setNewDealContact] = React.useState<string>("");
  const [newDealValue, setNewDealValue] = React.useState<string>("18500");
  const [newDealPriority, setNewDealPriority] = React.useState<string>("alta");
  const [newDealStageId, setNewDealStageId] = React.useState<string>("101");
  const [creatingDeal, setCreatingDeal] = React.useState<boolean>(false);
  const [dealActionFeedback, setDealActionFeedback] = React.useState<string | null>(null);
  const [dealActionError, setDealActionError] = React.useState<string | null>(null);

  // Drawer de Detalhes, Edição Inline, Estágio, Aprovação de Crédito, Tarefas e Timeline
  const [selectedDeal, setSelectedDeal] = React.useState<Deal | null>(null);
  const [editTitle, setEditTitle] = React.useState<string>("");
  const [editValue, setEditValue] = React.useState<string>("");
  const [editPriority, setEditPriority] = React.useState<string>("media");
  const [editCloseDate, setEditCloseDate] = React.useState<string>("");
  const [editComment, setEditComment] = React.useState<string>("");
  const [editStageId, setEditStageId] = React.useState<string>("101");
  const [timeline, setTimeline] = React.useState<TimelineEntry[]>([]);
  const [tasks, setTasks] = React.useState<TaskItem[]>([]);
  const [newTaskTitle, setNewTaskTitle] = React.useState<string>("");
  const [savingDrawer, setSavingDrawer] = React.useState<boolean>(false);

  // Sincronização bidirecional de rota com window.location.hash (HOMOLOG-01)
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

  // Consulta de Funis (GET /api/v1/pipelines)
  const pipelinesQuery = useQuery<PipelineItem[]>({
    queryKey: ["pipelines"],
    queryFn: async () => {
      const res = await fetch("/api/v1/pipelines");
      if (!res.ok) return [{ id: 1, name: "Vendas Diretas & Consignação" }];
      return res.json();
    },
  });

  // Consulta de Oportunidades e Estágios (GET /api/v1/deals)
  const dealsQuery = useQuery<{ stages: StageItem[]; deals: Deal[] }>({
    queryKey: ["deals", selectedPipelineId, currentUserId],
    queryFn: async () => {
      const res = await fetch(
        `/api/v1/deals?pipeline_id=${encodeURIComponent(selectedPipelineId)}`,
        {
          headers: { "X-User-Id": currentUserId },
        }
      );
      if (!res.ok) {
        throw new Error(`Falha ao carregar negócios (HTTP ${res.status})`);
      }
      const data = await res.json();
      if (Array.isArray(data)) {
        return { stages: [], deals: data };
      }
      return {
        stages: Array.isArray(data.stages) ? data.stages : [],
        deals: Array.isArray(data.deals) ? data.deals : data.data || [],
      };
    },
  });

  // Consulta de Métricas (GET /api/v1/metrics)
  const metricsQuery = useQuery<MetricsSummary>({
    queryKey: ["metrics"],
    queryFn: async () => {
      const res = await fetch("/api/v1/metrics");
      if (!res.ok) return {};
      return res.json();
    },
  });

  const loadTasks = React.useCallback(async () => {
    try {
      const res = await fetch("/api/v1/tasks");
      if (res.ok) {
        const data = await res.json();
        setTasks(Array.isArray(data) ? data : []);
      }
    } catch {
      // Silencioso
    }
  }, []);

  const loadDealTimeline = React.useCallback(async (dealId: string | number) => {
    try {
      const res = await fetch(`/api/v1/deals/${dealId}/timeline`);
      if (res.ok) {
        const data = await res.json();
        setTimeline(Array.isArray(data.timeline) ? data.timeline : []);
      }
    } catch {
      setTimeline([]);
    }
  }, []);

  const handleOpenDealDrawer = (deal: Deal) => {
    setSelectedDeal(deal);
    setEditTitle(deal.title || "");
    setEditValue(String(deal.value || 0));
    setEditPriority((deal as any).priority || "media");
    setEditCloseDate(deal.expected_close_date || "2026-12-15");
    setEditComment("");
    setEditStageId(String(deal.stage_id || 101));
    setDealActionError(null);
    setDealActionFeedback(null);
    loadDealTimeline(deal.id);
    loadTasks();
  };

  const handleCreateDeal = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newDealTitle.trim() || !newDealCompany.trim() || !newDealContact.trim()) return;
    setCreatingDeal(true);
    setDealActionError(null);
    try {
      const res = await fetch("/api/v1/deals", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-User-Id": currentUserId,
        },
        body: JSON.stringify({
          title: newDealTitle.trim(),
          value: Number(newDealValue) || 15000,
          company: newDealCompany.trim(),
          contact_name: newDealContact.trim(),
          pipeline_id: Number(selectedPipelineId) || 1,
          stage_id: Number(newDealStageId) || 101,
          priority: newDealPriority,
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Erro ao criar oportunidade (HTTP ${res.status})`);
      }
      setIsNewDealOpen(false);
      setNewDealTitle("");
      setNewDealCompany("");
      setNewDealContact("");
      setDealActionFeedback("Nova oportunidade cirúrgica registrada no pipeline com sucesso.");
      dealsQuery.refetch();
      metricsQuery.refetch();
    } catch (err: any) {
      setDealActionError(err.message);
    } finally {
      setCreatingDeal(false);
    }
  };

  const handleUpdateDealInline = async () => {
    if (!selectedDeal) return;
    setSavingDrawer(true);
    setDealActionError(null);
    try {
      const res = await fetch(`/api/v1/deals/${selectedDeal.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "X-User-Id": currentUserId,
        },
        body: JSON.stringify({
          title: editTitle.trim(),
          value: Number(editValue) || selectedDeal.value,
          priority: editPriority,
          expected_close_date: editCloseDate || undefined,
          comment: editComment.trim() || "Atualização inline pelo cockpit comercial",
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Falha ao atualizar negócio.");
      }
      setDealActionFeedback("Dados do negócio atualizados com sucesso.");
      await dealsQuery.refetch();
      await loadDealTimeline(selectedDeal.id);
    } catch (err: any) {
      setDealActionError(err.message);
    } finally {
      setSavingDrawer(false);
    }
  };

  const handleMoveStage = async (targetStageId: string) => {
    if (!selectedDeal) return;
    setEditStageId(targetStageId);
    setSavingDrawer(true);
    setDealActionError(null);
    try {
      const res = await fetch(`/api/v1/deals/${selectedDeal.id}/stage`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "X-User-Id": currentUserId,
        },
        body: JSON.stringify({
          stage_id: Number(targetStageId),
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data.detail || "Transição bloqueada pela política de crédito.");
      }
      setDealActionFeedback(`Estágio atualizado para #${targetStageId}.`);
      await dealsQuery.refetch();
      await loadDealTimeline(selectedDeal.id);
    } catch (err: any) {
      setDealActionError(err.message);
    } finally {
      setSavingDrawer(false);
    }
  };

  const handleApproveCredit = async () => {
    if (!selectedDeal) return;
    setSavingDrawer(true);
    setDealActionError(null);
    try {
      const res = await fetch(`/api/v1/deals/${selectedDeal.id}/approve-credit`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-User-Id": currentUserId,
        },
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data.detail || "Falha ao aprovar limite de crédito.");
      }
      setDealActionFeedback(data.message || "Limite de crédito aprovado para consignação.");
      await dealsQuery.refetch();
      await loadDealTimeline(selectedDeal.id);
    } catch (err: any) {
      setDealActionError(err.message);
    } finally {
      setSavingDrawer(false);
    }
  };

  const handleToggleTask = async (task: TaskItem) => {
    try {
      const nextCompleted = !Boolean(task.completed);
      const res = await fetch(`/api/v1/tasks/${task.id}/toggle`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ completed: nextCompleted }),
      });
      if (res.ok) {
        await loadTasks();
      }
    } catch {
      // Silencioso
    }
  };

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTaskTitle.trim()) return;
    try {
      const res = await fetch("/api/v1/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: newTaskTitle.trim(),
          due_date: "Hoje",
          assignee: "Consultor Especialista",
          priority: "alta",
        }),
      });
      if (res.ok) {
        setNewTaskTitle("");
        await loadTasks();
      }
    } catch {
      // Silencioso
    }
  };

  const handleExportCsv = async () => {
    try {
      const res = await fetch(
        `/api/v1/deals/export/csv?pipeline_id=${encodeURIComponent(selectedPipelineId)}`,
        {
          headers: { "X-User-Id": currentUserId },
        }
      );
      if (!res.ok) throw new Error("Falha ao exportar CSV do pipeline.");
      const csvText = await res.text();
      const blob = new Blob([csvText], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `pipeline_revnault_${selectedPipelineId}.csv`;
      a.click();
      URL.revokeObjectURL(url);
      setDealActionFeedback("Exportação CSV concluída com sucesso.");
    } catch (err: any) {
      setDealActionError(err.message);
    }
  };

  const rawDeals = dealsQuery.data?.deals || [];
  const rawStages = dealsQuery.data?.stages || [
    { id: 101, name: "Qualificação & Triagem CRO" },
    { id: 102, name: "Diagnóstico Clínico & Kit" },
    { id: 103, name: "Proposta & Alçada Comercial" },
    { id: 104, name: "Análise de Crédito & Minuta" },
    { id: 105, name: "Fechado & Ganho (Consignado)" },
  ];

  const filteredDeals = React.useMemo(() => {
    const q = searchTerm.trim().toLowerCase();
    if (!q) return rawDeals;
    return rawDeals.filter(
      (d) =>
        String(d.title || "").toLowerCase().includes(q) ||
        String(d.company_name || (d as any).company || "").toLowerCase().includes(q) ||
        String(d.contact_name || "").toLowerCase().includes(q) ||
        String(d.owner_name || "").toLowerCase().includes(q)
    );
  }, [rawDeals, searchTerm]);

  const kanbanStages: KanbanStage<Deal>[] = React.useMemo(() => {
    const stageList = rawStages.length > 0 ? rawStages : [{ id: 101, name: "Qualificação" }];
    return stageList.map((st) => ({
      id: st.id,
      name: st.name,
      items: filteredDeals.filter((d) => Number(d.stage_id) === Number(st.id)),
    }));
  }, [rawStages, filteredDeals]);

  const stageNameMap = React.useMemo(() => {
    const map: Record<number, string> = {};
    for (const s of rawStages) {
      map[Number(s.id)] = s.name;
    }
    return map;
  }, [rawStages]);

  const columns: Column<Deal>[] = [
    {
      key: "title",
      header: "Oportunidade Cirúrgica / Clínica",
      render: (deal) => (
        <div>
          <div className="font-medium text-text-main">{deal.title}</div>
          <div className="text-xs text-text-secondary">
            {deal.company_name || (deal as any).company || "Clínica Odontológica"}
          </div>
        </div>
      ),
    },
    {
      key: "contact_name",
      header: "Cirurgião Titular",
      render: (deal) => (
        <span className="text-xs text-text-main font-medium">{deal.contact_name || "Dr. Titular"}</span>
      ),
    },
    {
      key: "value",
      header: "Valor (BRL)",
      render: (deal) => (
        <span className="font-semibold text-text-main">
          {new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(
            deal.value || 0
          )}
        </span>
      ),
    },
    {
      key: "stage_id",
      header: "Estágio do Funil",
      render: (deal) => (
        <Badge variant="navy" className="text-[10px]">
          {stageNameMap[Number(deal.stage_id)] || `Estágio ${deal.stage_id}`}
        </Badge>
      ),
    },
    {
      key: "approval_status",
      header: "Governança & Crédito",
      render: (deal) => {
        const creditOk = Boolean((deal as any).credit_approved);
        return (
          <Badge variant={creditOk ? "success" : "secondary"} className="text-[10px]">
            {creditOk ? "Crédito Aprovado" : deal.approval_status || "Lote Rastreado"}
          </Badge>
        );
      },
    },
  ];

  const metrics = metricsQuery.data;
  const pipelines = pipelinesQuery.data || [{ id: 1, name: "Funil Principal RevOps" }];

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
      <ErrorBoundary key={activeNav} onReset={() => dealsQuery.refetch()}>
        <AppRouter
          currentRoute={activeNav}
          onNavigate={handleNavigate}
          defaultComponent={
            <div className="space-y-6 max-w-7xl mx-auto">
              {/* Cabeçalho + Ações Primárias */}
              <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                <div>
                  <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-text-main">
                    Cockpit de Negócios & Consignação Cirúrgica
                  </h1>
                  <p className="text-xs sm:text-sm text-text-secondary mt-1">
                    Operação unificada RevOps + KeyPartners (Kits & ANVISA) + DENTGO (Logística Same-Day). Clique em um negócio para abrir o Dossiê e Aprovação de Crédito.
                  </p>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => {
                      dealsQuery.refetch();
                      metricsQuery.refetch();
                    }}
                    className="gap-1.5"
                  >
                    <RefreshCw className="h-3.5 w-3.5" />
                    Sincronizar
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleExportCsv}
                    className="gap-1.5"
                  >
                    <Download className="h-3.5 w-3.5" />
                    Exportar CSV
                  </Button>
                  <Button
                    size="sm"
                    onClick={() => setIsNewDealOpen(true)}
                    className="gap-1.5"
                  >
                    <Plus className="h-3.5 w-3.5" />
                    Novo Negócio
                  </Button>
                </div>
              </div>

              {dealActionFeedback && (
                <div className="p-3 rounded-lg bg-status-success-subtle border border-status-success/30 text-xs text-status-success flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 shrink-0" />
                    <span>{dealActionFeedback}</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => setDealActionFeedback(null)}
                    className="text-xs underline"
                  >
                    Fechar
                  </button>
                </div>
              )}

              {dealActionError && (
                <div className="p-3 rounded-lg bg-status-danger-subtle border border-status-danger/30 text-xs text-status-danger flex items-center justify-between">
                  <span>{dealActionError}</span>
                  <button
                    type="button"
                    onClick={() => setDealActionError(null)}
                    className="text-xs underline"
                  >
                    Fechar
                  </button>
                </div>
              )}

              {/* KPI Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <Card className="p-4 border-border">
                  <span className="text-xs font-semibold uppercase text-text-secondary">
                    Negócios no Funil ({filteredDeals.length})
                  </span>
                  <p className="text-xl font-bold text-text-main mt-1">
                    {metrics?.totalDeals ?? metrics?.total_deals ?? filteredDeals.length}
                  </p>
                </Card>
                <Card className="p-4 border-border">
                  <span className="text-xs font-semibold uppercase text-text-secondary">
                    Volume em Pipeline
                  </span>
                  <p className="text-xl font-bold text-brand-primary mt-1">
                    {new Intl.NumberFormat("pt-BR", {
                      style: "currency",
                      currency: "BRL",
                    }).format(
                      metrics?.pipelineTotal ??
                        metrics?.pipeline_value ??
                        filteredDeals.reduce((acc, d) => acc + (d.value || 0), 0)
                    )}
                  </p>
                </Card>
                <Card className="p-4 border-border">
                  <span className="text-xs font-semibold uppercase text-text-secondary">
                    Custódia & Alçada ANVISA
                  </span>
                  <p className="text-xl font-bold text-status-success mt-1">
                    100% Rastreável
                  </p>
                </Card>
              </div>

              {/* Barra de Filtros: Seletor de Pipeline, Busca Instantânea e Toggle Tabela/Kanban */}
              <Card className="p-3.5 border-border">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                  <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 flex-1">
                    <div className="w-full sm:w-64">
                      <Select
                        aria-label="Selecionar Funil de Vendas"
                        value={selectedPipelineId}
                        onChange={(e) => setSelectedPipelineId(e.target.value)}
                        options={pipelines.map((p) => ({
                          value: String(p.id),
                          label: p.name,
                        }))}
                      />
                    </div>
                    <div className="relative flex-1">
                      <Search className="h-4 w-4 text-text-muted absolute left-3 top-2.5 pointer-events-none" />
                      <Input
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        placeholder="Filtrar por clínica, cirurgião ou oportunidade..."
                        className="pl-9"
                      />
                    </div>
                  </div>

                  <div className="flex items-center gap-1.5 self-end md:self-auto">
                    <Button
                      type="button"
                      variant={viewMode === "table" ? "default" : "outline"}
                      size="sm"
                      onClick={() => setViewMode("table")}
                      className="gap-1.5"
                    >
                      <List className="h-3.5 w-3.5" />
                      Tabela Paginada
                    </Button>
                    <Button
                      type="button"
                      variant={viewMode === "kanban" ? "default" : "outline"}
                      size="sm"
                      onClick={() => setViewMode("kanban")}
                      className="gap-1.5"
                    >
                      <LayoutGrid className="h-3.5 w-3.5" />
                      Quadro Kanban
                    </Button>
                  </div>
                </div>
              </Card>

              {/* Área de Listagem Paginada ou Quadro Kanban */}
              {dealsQuery.isLoading ? (
                <DataTable columns={columns} data={[]} isLoading={true} />
              ) : dealsQuery.isError ? (
                <Card className="p-8 border-status-danger/30 text-center">
                  <div className="flex flex-col items-center gap-3">
                    <AlertCircle className="h-8 w-8 text-status-danger" />
                    <h3 className="text-base font-semibold text-text-main">
                      Falha ao sincronizar pipeline cirúrgico
                    </h3>
                    <p className="text-xs text-text-secondary">
                      {(dealsQuery.error as Error)?.message || "Erro na consulta de negócios."}
                    </p>
                    <Button size="sm" onClick={() => dealsQuery.refetch()} className="gap-1.5">
                      <RefreshCw className="h-4 w-4" />
                      Tentar Novamente
                    </Button>
                  </div>
                </Card>
              ) : filteredDeals.length === 0 ? (
                <EmptyState
                  icon={FileText}
                  title="Nenhum negócio cirúrgico encontrado para este filtro"
                  description="Limpe o filtro de busca ou cadastre uma nova oportunidade comercial no botão Novo Negócio."
                  actionLabel="Criar Novo Negócio"
                  onAction={() => setIsNewDealOpen(true)}
                />
              ) : viewMode === "table" ? (
                <DataTable
                  columns={columns}
                  data={filteredDeals}
                  defaultPageSize={25}
                  pageSizeOptions={[25, 50]}
                  onRowClick={handleOpenDealDrawer}
                />
              ) : (
                <KanbanBoard
                  stages={kanbanStages}
                  onCardClick={handleOpenDealDrawer}
                  renderCard={(deal) => (
                    <div className="rounded-md border border-border bg-surface-card p-3 shadow-xs space-y-1.5">
                      <div className="font-semibold text-xs text-text-main line-clamp-2">
                        {deal.title}
                      </div>
                      <div className="text-[11px] text-text-secondary truncate">
                        {deal.company_name || (deal as any).company || deal.contact_name}
                      </div>
                      <div className="flex items-center justify-between pt-1">
                        <span className="text-xs font-bold text-brand-primary">
                          {new Intl.NumberFormat("pt-BR", {
                            style: "currency",
                            currency: "BRL",
                          }).format(deal.value || 0)}
                        </span>
                        <Badge variant="secondary" className="text-[10px]">
                          {deal.contact_name || "Titular"}
                        </Badge>
                      </div>
                    </div>
                  )}
                />
              )}

              {/* Modal Dialog: Criar Novo Negócio (POST /api/v1/deals) */}
              <Dialog
                isOpen={isNewDealOpen}
                onClose={() => setIsNewDealOpen(false)}
                title="Registrar Nova Oportunidade Cirúrgica"
                description="Cria um novo Deal vinculado ao funil ativo com validação de escopo RBAC."
              >
                <form onSubmit={handleCreateDeal} className="space-y-3">
                  <div>
                    <label className="block text-xs font-medium text-text-secondary mb-1">
                      Título da Oportunidade / Kit *
                    </label>
                    <Input
                      required
                      value={newDealTitle}
                      onChange={(e) => setNewDealTitle(e.target.value)}
                      placeholder="Ex: Consignação 30 Implantes Cone Morse + Kit Cirúrgico"
                    />
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-medium text-text-secondary mb-1">
                        Clínica / Hospital *
                      </label>
                      <Input
                        required
                        value={newDealCompany}
                        onChange={(e) => setNewDealCompany(e.target.value)}
                        placeholder="Ex: Instituto Odontológico Paulista"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-text-secondary mb-1">
                        Cirurgião Decisor *
                      </label>
                      <Input
                        required
                        value={newDealContact}
                        onChange={(e) => setNewDealContact(e.target.value)}
                        placeholder="Ex: Dr. Roberto Silveira"
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <div>
                      <label className="block text-xs font-medium text-text-secondary mb-1">
                        Valor Estimado (R$) *
                      </label>
                      <Input
                        type="number"
                        min="1"
                        step="0.01"
                        required
                        value={newDealValue}
                        onChange={(e) => setNewDealValue(e.target.value)}
                      />
                    </div>
                    <Select
                      label="Estágio Inicial"
                      value={newDealStageId}
                      onChange={(e) => setNewDealStageId(e.target.value)}
                      options={rawStages.map((s) => ({
                        value: String(s.id),
                        label: s.name,
                      }))}
                    />
                    <Select
                      label="Prioridade"
                      value={newDealPriority}
                      onChange={(e) => setNewDealPriority(e.target.value)}
                      options={[
                        { value: "alta", label: "Alta Prioridade" },
                        { value: "media", label: "Média Prioridade" },
                        { value: "baixa", label: "Baixa Prioridade" },
                      ]}
                    />
                  </div>
                  <div className="flex justify-end gap-2 pt-3 border-t border-border-subtle">
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => setIsNewDealOpen(false)}
                    >
                      Cancelar
                    </Button>
                    <Button type="submit" size="sm" disabled={creatingDeal}>
                      {creatingDeal ? "Salvando..." : "Criar Oportunidade"}
                    </Button>
                  </div>
                </form>
              </Dialog>

              {/* Drawer Sheet: Detalhes do Deal, Edição Inline, Estágio, Aprovação de Crédito, Tarefas e Timeline */}
              <Sheet
                isOpen={Boolean(selectedDeal)}
                onClose={() => setSelectedDeal(null)}
                title={selectedDeal ? `Dossiê do Negócio #${selectedDeal.id}` : "Dossiê"}
                description={
                  selectedDeal
                    ? `${selectedDeal.company_name || (selectedDeal as any).company || ""} • ${selectedDeal.contact_name || ""}`
                    : ""
                }
              >
                {selectedDeal && (
                  <div className="space-y-5 text-xs">
                    {/* Transição de Estágio & Aprovação de Crédito */}
                    <div className="p-3 rounded-lg bg-surface-bg border border-border space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold uppercase text-text-secondary">
                          Governança de Estágio & Crédito
                        </span>
                        <Badge variant="navy">ID: {selectedDeal.id}</Badge>
                      </div>

                      <Select
                        label="Mover Estágio no Funil (PUT /stage)"
                        value={editStageId}
                        onChange={(e) => handleMoveStage(e.target.value)}
                        options={rawStages.map((s) => ({
                          value: String(s.id),
                          label: s.name,
                        }))}
                      />

                      <Button
                        type="button"
                        variant="secondary"
                        size="sm"
                        onClick={handleApproveCredit}
                        disabled={savingDrawer}
                        className="w-full gap-1.5"
                      >
                        <ShieldCheck className="h-4 w-4 text-status-success" />
                        Aprovar Limite de Crédito para Consignação
                      </Button>
                    </div>

                    {/* Edição Inline (PUT /api/v1/deals/{deal_id}) */}
                    <div className="p-3 rounded-lg border border-border space-y-3">
                      <span className="font-semibold uppercase text-text-secondary block">
                        Edição Inline da Oportunidade
                      </span>
                      <div>
                        <label className="block text-text-secondary mb-1">Título</label>
                        <Input
                          value={editTitle}
                          onChange={(e) => setEditTitle(e.target.value)}
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-2">
                        <div>
                          <label className="block text-text-secondary mb-1">Valor (R$)</label>
                          <Input
                            type="number"
                            value={editValue}
                            onChange={(e) => setEditValue(e.target.value)}
                          />
                        </div>
                        <Select
                          label="Prioridade"
                          value={editPriority}
                          onChange={(e) => setEditPriority(e.target.value)}
                          options={[
                            { value: "alta", label: "Alta" },
                            { value: "media", label: "Média" },
                            { value: "baixa", label: "Baixa" },
                          ]}
                        />
                      </div>
                      <div>
                        <label className="block text-text-secondary mb-1">
                          Previsão de Fechamento
                        </label>
                        <Input
                          type="date"
                          value={editCloseDate}
                          onChange={(e) => setEditCloseDate(e.target.value)}
                        />
                      </div>
                      <div>
                        <label className="block text-text-secondary mb-1">
                          Nota de Auditoria
                        </label>
                        <Input
                          value={editComment}
                          onChange={(e) => setEditComment(e.target.value)}
                          placeholder="Motivo da revisão comercial..."
                        />
                      </div>
                      <Button
                        type="button"
                        size="sm"
                        onClick={handleUpdateDealInline}
                        disabled={savingDrawer}
                        className="w-full gap-1.5"
                      >
                        <Save className="h-3.5 w-3.5" />
                        {savingDrawer ? "Salvando..." : "Salvar Alterações Inline"}
                      </Button>
                    </div>

                    {/* Checklist de Tarefas Operacionais (PATCH /api/v1/tasks/{id}/toggle) */}
                    <div className="p-3 rounded-lg border border-border space-y-3">
                      <span className="font-semibold uppercase text-text-secondary block">
                        Checklist de Tarefas Operacionais
                      </span>
                      <form onSubmit={handleCreateTask} className="flex gap-2">
                        <Input
                          value={newTaskTitle}
                          onChange={(e) => setNewTaskTitle(e.target.value)}
                          placeholder="Nova tarefa (ex: Conferir CRO e contrato)..."
                        />
                        <Button type="submit" size="sm" variant="outline">
                          Adicionar
                        </Button>
                      </form>
                      <div className="divide-y divide-border-subtle max-h-40 overflow-y-auto">
                        {tasks.slice(0, 8).map((t) => {
                          const isDone = Boolean(t.completed);
                          return (
                            <button
                              key={t.id}
                              type="button"
                              onClick={() => handleToggleTask(t)}
                              className="w-full py-2 flex items-center justify-between text-left hover:bg-surface-bg px-1 rounded"
                            >
                              <div className="flex items-center gap-2 min-w-0">
                                {isDone ? (
                                  <CheckSquare className="h-4 w-4 text-status-success shrink-0" />
                                ) : (
                                  <Square className="h-4 w-4 text-text-muted shrink-0" />
                                )}
                                <span
                                  className={
                                    isDone
                                      ? "line-through text-text-muted truncate"
                                      : "text-text-main truncate"
                                  }
                                >
                                  {t.title}
                                </span>
                              </div>
                              <Badge variant="secondary" className="text-[10px] shrink-0">
                                {t.due_date}
                              </Badge>
                            </button>
                          );
                        })}
                      </div>
                    </div>

                    {/* Timeline de Auditoria (GET /api/v1/deals/{deal_id}/timeline) */}
                    <div className="p-3 rounded-lg border border-border space-y-2">
                      <span className="font-semibold uppercase text-text-secondary flex items-center gap-1.5">
                        <Clock className="h-3.5 w-3.5" />
                        Linha do Tempo Auditável
                      </span>
                      {timeline.length === 0 ? (
                        <p className="text-text-muted py-2">
                          Nenhum evento registrado para este negócio.
                        </p>
                      ) : (
                        <div className="space-y-2 max-h-48 overflow-y-auto">
                          {timeline.map((ev, idx) => (
                            <div
                              key={ev.id ?? idx}
                              className="p-2 rounded bg-surface-bg border border-border-subtle"
                            >
                              <div className="flex justify-between font-medium text-text-main">
                                <span>{ev.action || ev.event_type || "Evento"}</span>
                                <span className="text-[10px] text-text-muted">
                                  {ev.created_at || ev.timestamp || ""}
                                </span>
                              </div>
                              <p className="text-text-secondary mt-0.5">
                                {ev.description || ev.details || ""}
                              </p>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </Sheet>
            </div>
          }
        />
      </ErrorBoundary>
    </AppShell>
  );
}

export default App;

