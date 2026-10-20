// -*- coding: utf-8 -*-
/**
 * DealsWorkspace.tsx
 * Workspace completo de Deals / Oportunidades Cirúrgicas (TICKET-DEALS-01).
 * Inclui Drawer Full Integration: seletor de catálogo ANVISA + quantidade,
 * despacho DENTGO 45min, proposta PDF, LiveKit e Copiloto Granola.
 */

import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
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
  Video,
  Truck,
  Package,
  FileDown,
} from "lucide-react";
import { LiveKitDealRoomModal } from "@/features/communications/LiveKitDealRoomModal";
import { GranolaCopilotCard } from "@/features/deals/components/GranolaCopilotCard";

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
}

interface CatalogProduct {
  id: string;
  sku: string;
  name: string;
  category: string;
  anvisa_reg?: string | null;
  base_price: number;
}

export interface DealsWorkspaceProps {
  currentUserId?: string;
  onNavigate?: (route: string, opts?: { stage?: string }) => void;
}

const normalizeUserId = (): string => {
  if (typeof window === "undefined") return "usr-director-br";
  return (
    localStorage.getItem("revnaut_active_user_id") ||
    localStorage.getItem("revnaut_user_id") ||
    "usr-director-br"
  );
};

const isContractOrWon = (stageName: string, stageId: number | string): boolean => {
  const name = (stageName || "").toLowerCase();
  const sid = Number(stageId);
  return (
    name.includes("contrato") ||
    name.includes("ganho") ||
    name.includes("won") ||
    name.includes("fechado") ||
    sid === 104 ||
    sid === 105
  );
};

export const DealsWorkspace: React.FC<DealsWorkspaceProps> = ({ currentUserId }) => {
  const userId = React.useMemo(() => currentUserId || normalizeUserId(), [currentUserId]);

  const [selectedPipelineId, setSelectedPipelineId] = React.useState<string>("1");
  const [searchTerm, setSearchTerm] = React.useState<string>("");
  const [viewMode, setViewMode] = React.useState<"table" | "kanban">("table");
  const [stageFilter, setStageFilter] = React.useState<string>("");

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
  const [showDealVideoModal, setShowDealVideoModal] = React.useState<boolean>(false);

  // TICKET-DEALS-02: seletor de catálogo dental + quantidade
  const [catalogProducts, setCatalogProducts] = React.useState<CatalogProduct[]>([]);
  const [selectedSku, setSelectedSku] = React.useState<string>("");
  const [itemQty, setItemQty] = React.useState<string>("1");
  const [cartLines, setCartLines] = React.useState<Array<{ sku: string; name: string; qty: number; unitPrice: number }>>([]);

  // TICKET-DEALS-03: despacho DENTGO
  const [dispatching, setDispatching] = React.useState<boolean>(false);

  React.useEffect(() => {
    const rawHash = window.location.hash || "";
    const match = rawHash.match(/stage=([^&]+)/);
    if (match) {
      setStageFilter(decodeURIComponent(match[1]));
    }
  }, []);

  const pipelinesQuery = useQuery<{ id: number; name: string }[]>({
    queryKey: ["pipelines"],
    queryFn: async () => {
      const res = await fetch("/api/v1/pipelines");
      if (!res.ok) return [{ id: 1, name: "Vendas Diretas & Consignação" }];
      return res.json();
    },
  });

  const dealsQuery = useQuery<{ stages: StageItem[]; deals: Deal[] }>({
    queryKey: ["deals", selectedPipelineId, userId],
    queryFn: async () => {
      const res = await fetch(`/api/v1/deals?pipeline_id=${encodeURIComponent(selectedPipelineId)}`, {
        headers: { "X-User-Id": userId },
      });
      if (!res.ok) throw new Error(`Falha ao carregar negócios (HTTP ${res.status})`);
      const data = await res.json();
      if (Array.isArray(data)) return { stages: [], deals: data };
      return {
        stages: Array.isArray(data.stages) ? data.stages : [],
        deals: Array.isArray(data.deals) ? data.deals : data.data || [],
      };
    },
  });
  const refetchDeals = () => dealsQuery.refetch();

  React.useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch("/api/v1/deals/catalog/products", { headers: { "X-User-Id": userId } });
        if (!res.ok) return;
        const data = await res.json();
        if (!cancelled && Array.isArray(data)) {
          setCatalogProducts(data);
        }
      } catch {
        // Silencioso
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [userId]);

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
    setCartLines([]);
    setSelectedSku("");
    setItemQty("1");
    loadDealTimeline(deal.id);
    loadTasks();
  };

  const cartTotal = React.useMemo(
    () => cartLines.reduce((acc, l) => acc + l.qty * l.unitPrice, 0),
    [cartLines]
  );

  const handleAddCartLine = React.useCallback(() => {
    const product = catalogProducts.find((p) => p.sku === selectedSku);
    if (!product) return;
    const qty = Math.max(1, Number(itemQty) || 1);
    setCartLines((prev) => {
      const existing = prev.find((l) => l.sku === product.sku);
      if (existing) {
        return prev.map((l) => (l.sku === product.sku ? { ...l, qty: l.qty + qty } : l));
      }
      return [...prev, { sku: product.sku, name: product.name, qty, unitPrice: Number(product.base_price) || 0 }];
    });
    setSelectedSku("");
    setItemQty("1");
  }, [catalogProducts, selectedSku, itemQty]);

  const handleApplyCartToDealValue = React.useCallback(async () => {
    if (!selectedDeal || cartTotal <= 0) return;
    setEditValue(String(cartTotal));
    setSavingDrawer(true);
    setDealActionError(null);
    try {
      const res = await fetch(`/api/v1/deals/${selectedDeal.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", "X-User-Id": userId },
        body: JSON.stringify({
          title: editTitle.trim() || selectedDeal.title,
          value: cartTotal,
          priority: editPriority,
          expected_close_date: editCloseDate || undefined,
          comment: editComment.trim() || "Valor recalculado a partir do catálogo ANVISA",
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Falha ao atualizar valor do negócio.");
      }
      setDealActionFeedback(`Valor do negócio atualizado para R$ ${cartTotal.toFixed(2)} via catálogo.`);
      await dealsQuery.refetch();
      await loadDealTimeline(selectedDeal.id);
    } catch (err: any) {
      setDealActionError(err.message);
    } finally {
      setSavingDrawer(false);
    }
  }, [selectedDeal, cartTotal, editTitle, editPriority, editCloseDate, editComment, userId, dealsQuery, loadDealTimeline]);

  // TICKET-DEALS-03: Despachar com DENTGO (45 min)
  const handleDispatchDentgo = React.useCallback(async () => {
    if (!selectedDeal) return;
    setDispatching(true);
    setDealActionError(null);
    try {
      const selectedCatalogSku = selectedSku || (cartLines.length > 0 ? cartLines[0].sku : "");
      const catalogQty = Number(itemQty) || (cartLines.length > 0 ? cartLines[0].qty : 2);

      const itemsPayload = cartLines.length > 0
        ? cartLines.map((l) => ({
            product_id: l.sku,
            sku: l.sku,
            product_name: l.name,
            quantity: l.qty,
            unit_price: l.unitPrice,
          }))
        : [{
            product_id: selectedCatalogSku || "IMP-CM-3511",
            sku: selectedCatalogSku || "IMP-CM-3511",
            product_name: "Kit Implante Cone Morse Emerge",
            quantity: catalogQty || 2,
            unit_price: 289.9,
          }];

      const res = await fetch("/api/v1/dentgo/orders/express", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-User-Id": userId },
        body: JSON.stringify({
          customer_cro_uf: "CRO-SP-45892",
          customer_name: selectedDeal.contact_name || selectedDeal.title,
          delivery_address: `Clinica ${selectedDeal.contact_name || selectedDeal.title} - Centro Cirurgico`,
          delivery_lat: -23.5614,
          delivery_lng: -46.6559,
          payment_method: "CORPORATE_CREDIT",
          items: itemsPayload,
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || "Falha ao despachar pedido DENTGO.");
      setDealActionFeedback(`Pedido DENTGO criado com SLA 45 min (${data.order_id || data.id || "OK"}).`);
    } catch (err: any) {
      setDealActionError(err.message);
    } finally {
      setDispatching(false);
    }
  }, [selectedDeal, cartLines, selectedSku, itemQty, userId]);

  // Gerar Proposta Comercial PDF via Documenso
  const [generatingPdf, setGeneratingPdf] = React.useState<boolean>(false);
  const handleGenerateProposalPdf = React.useCallback(async () => {
    if (!selectedDeal) return;
    setGeneratingPdf(true);
    setDealActionError(null);
    try {
      const res = await fetch(`/api/v1/deals/${selectedDeal.id}/generate-contract`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-User-Id": userId },
        body: JSON.stringify({
          contract_type: "commercial_proposal",
          signer_name: selectedDeal.contact_name || "Cirurgião",
          signer_email: `${(selectedDeal.contact_name || "contato").split(" ")[0].toLowerCase()}@clinica.example`,
          signer_phone: "",
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || "Falha ao gerar proposta comercial.");
      const pdfUrl = data.original_file_url || data.pdf_url || data.signing_url || data.r2_original_key;
      if (pdfUrl) {
        window.open(String(pdfUrl).startsWith("http") ? pdfUrl : `/api/v1/storage/files/${String(pdfUrl).replace(/^\//, "")}`, "_blank", "noopener,noreferrer");
      }
      setDealActionFeedback(`Proposta comercial gerada (${data.id || data.contract_id || "PDF"}).`);
      await loadDealTimeline(selectedDeal.id);
    } catch (err: any) {
      setDealActionError(err.message);
    } finally {
      setGeneratingPdf(false);
    }
  }, [selectedDeal, userId, loadDealTimeline]);

  const handleCreateDeal = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newDealTitle.trim() || !newDealCompany.trim() || !newDealContact.trim()) return;
    setCreatingDeal(true);
    setDealActionError(null);
    try {
      const res = await fetch("/api/v1/deals", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-User-Id": userId },
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
        headers: { "Content-Type": "application/json", "X-User-Id": userId },
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
        headers: { "Content-Type": "application/json", "X-User-Id": userId },
        body: JSON.stringify({ stage_id: Number(targetStageId) }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || "Transição bloqueada pela política de crédito.");
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
        headers: { "Content-Type": "application/json", "X-User-Id": userId },
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || "Falha ao aprovar limite de crédito.");
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
      if (res.ok) await loadTasks();
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
      const res = await fetch(`/api/v1/deals/export/csv?pipeline_id=${encodeURIComponent(selectedPipelineId)}`, {
        headers: { "X-User-Id": userId },
      });
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
    let list = rawDeals;
    if (stageFilter) {
      list = list.filter((d) => {
        const stageName = (rawStages.find((s) => Number(s.id) === Number(d.stage_id))?.name || "").toLowerCase();
        return stageName.includes(stageFilter.toLowerCase()) || String(d.stage_id) === stageFilter;
      });
    }
    const q = searchTerm.trim().toLowerCase();
    if (!q) return list;
    return list.filter(
      (d) =>
        String(d.title || "").toLowerCase().includes(q) ||
        String(d.company_name || (d as any).company || "").toLowerCase().includes(q) ||
        String(d.contact_name || "").toLowerCase().includes(q) ||
        String(d.owner_name || "").toLowerCase().includes(q)
    );
  }, [rawDeals, searchTerm, stageFilter, rawStages]);

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
    for (const s of rawStages) map[Number(s.id)] = s.name;
    return map;
  }, [rawStages]);

  const selectedStageName = selectedDeal
    ? stageNameMap[Number(selectedDeal.stage_id)] || ""
    : "";
  const showDentgoDispatch = selectedDeal
    ? isContractOrWon(selectedStageName, selectedDeal.stage_id)
    : false;

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
          {new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(deal.value || 0)}
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

  const pipelines = pipelinesQuery.data || [{ id: 1, name: "Funil Principal RevOps" }];

  return (
    <ErrorBoundary onReset={() => dealsQuery.refetch()}>
      <div className="space-y-6 max-w-7xl mx-auto">
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
            <Button variant="secondary" size="sm" onClick={() => dealsQuery.refetch()} className="gap-1.5">
              <RefreshCw className="h-3.5 w-3.5" />
              Atualizar
            </Button>
            <Button variant="outline" size="sm" onClick={handleExportCsv} className="gap-1.5">
              <Download className="h-3.5 w-3.5" />
              Exportar CSV
            </Button>
            <Button size="sm" onClick={() => setIsNewDealOpen(true)} className="gap-1.5">
              <Plus className="h-3.5 w-3.5" />
              Nova Oportunidade
            </Button>
          </div>
        </div>

        {dealActionFeedback && (
          <div className="p-3 rounded-lg bg-status-success-subtle border border-status-success/30 text-xs text-status-success flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 shrink-0" />
            <span>{dealActionFeedback}</span>
          </div>
        )}
        {dealActionError && (
          <div className="p-3 rounded-lg bg-status-danger-subtle border border-status-danger/30 text-xs text-status-danger flex items-center gap-2">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{dealActionError}</span>
          </div>
        )}

        <div className="flex flex-col md:flex-row gap-3 md:items-end">
          <div className="flex-1">
            <label className="block text-xs font-medium text-text-secondary mb-1">Buscar</label>
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-text-muted" />
              <Input
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Buscar por clínica, cirurgião ou oportunidade..."
                className="pl-8"
              />
            </div>
          </div>
          <Select
            label="Funil"
            value={selectedPipelineId}
            onChange={(e) => setSelectedPipelineId(e.target.value)}
            options={pipelines.map((p) => ({ value: String(p.id), label: p.name }))}
            className="md:w-56"
          />
          <Select
            label="Filtrar Estágio"
            value={stageFilter}
            onChange={(e) => setStageFilter(e.target.value)}
            options={[
              { value: "", label: "Todos os estágios" },
              ...rawStages.map((s) => ({ value: s.name, label: s.name })),
            ]}
            className="md:w-56"
          />
          <div className="flex gap-1">
            <Button
              variant={viewMode === "table" ? "default" : "outline"}
              size="sm"
              onClick={() => setViewMode("table")}
              className="gap-1.5"
            >
              <List className="h-3.5 w-3.5" />
              Lista
            </Button>
            <Button
              variant={viewMode === "kanban" ? "default" : "outline"}
              size="sm"
              onClick={() => setViewMode("kanban")}
              className="gap-1.5"
            >
              <LayoutGrid className="h-3.5 w-3.5" />
              Kanban
            </Button>
          </div>
        </div>

        {dealsQuery.isLoading ? (
          <div className="py-12 text-center text-sm text-text-muted">Carregando oportunidades...</div>
        ) : dealsQuery.isError ? (
          <EmptyState
            title="Erro na consulta de negócios"
            description={(dealsQuery.error as Error)?.message || "Verifique a conectividade."}
          />
        ) : filteredDeals.length === 0 ? (
          <EmptyState title="Nenhuma oportunidade encontrada" description="Ajuste os filtros ou crie um novo negócio." />
        ) : viewMode === "table" ? (
          <DataTable
            data={filteredDeals}
            columns={columns}
            onRowClick={handleOpenDealDrawer}
          />
        ) : (
          <KanbanBoard
            stages={kanbanStages}
            onCardClick={handleOpenDealDrawer}
            renderCard={(deal) => (
              <div className="space-y-1">
                <div className="font-medium text-text-main text-xs truncate">{deal.title}</div>
                <div className="text-[10px] text-text-secondary truncate">
                  {deal.company_name || (deal as any).company || "Clínica"}
                </div>
                <div className="text-xs font-semibold text-brand-primary">
                  {new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(deal.value || 0)}
                </div>
              </div>
            )}
          />
        )}

        <Dialog isOpen={isNewDealOpen} onClose={() => setIsNewDealOpen(false)} title="Nova Oportunidade Cirúrgica">
          <form onSubmit={handleCreateDeal} className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-text-secondary mb-1">Título *</label>
              <Input required value={newDealTitle} onChange={(e) => setNewDealTitle(e.target.value)} placeholder="Ex: Kit Implantes Premium" />
            </div>
            <div>
              <label className="block text-xs font-medium text-text-secondary mb-1">Clínica *</label>
              <Input required value={newDealCompany} onChange={(e) => setNewDealCompany(e.target.value)} placeholder="Ex: Instituto Odontológico Paulista" />
            </div>
            <div>
              <label className="block text-xs font-medium text-text-secondary mb-1">Cirurgião Decisor *</label>
              <Input required value={newDealContact} onChange={(e) => setNewDealContact(e.target.value)} placeholder="Ex: Dr. Roberto Silveira" />
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="block text-xs font-medium text-text-secondary mb-1">Valor Estimado (R$) *</label>
                <Input type="number" min="1" step="0.01" required value={newDealValue} onChange={(e) => setNewDealValue(e.target.value)} />
              </div>
              <Select
                label="Estágio Inicial"
                value={newDealStageId}
                onChange={(e) => setNewDealStageId(e.target.value)}
                options={rawStages.map((s) => ({ value: String(s.id), label: s.name }))}
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
              <Button type="button" variant="outline" size="sm" onClick={() => setIsNewDealOpen(false)}>
                Cancelar
              </Button>
              <Button type="submit" size="sm" disabled={creatingDeal}>
                {creatingDeal ? "Salvando..." : "Criar Oportunidade"}
              </Button>
            </div>
          </form>
        </Dialog>

        <Sheet
          isOpen={Boolean(selectedDeal)}
          onClose={() => setSelectedDeal(null)}
          title={selectedDeal ? `Dossiê do Negócio #${selectedDeal.id}` : "Dossiê"}
          description={selectedDeal ? `${selectedDeal.company_name || (selectedDeal as any).company || ""} • ${selectedDeal.contact_name || ""}` : ""}
        >
          {selectedDeal && (
            <div className="space-y-5 text-xs">
              <div className="p-3 rounded-lg bg-surface-bg border border-border space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-semibold uppercase text-text-secondary">Governança de Estágio & Crédito</span>
                  <Badge variant="navy">ID: {selectedDeal.id}</Badge>
                </div>
                <Select
                  label="Mover Estágio no Funil (PUT /stage)"
                  value={editStageId}
                  onChange={(e) => handleMoveStage(e.target.value)}
                  options={rawStages.map((s) => ({ value: String(s.id), label: s.name }))}
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

              {/* TICKET-DEALS-02: Catálogo Dental + Quantidade → Valor BRL */}
              <div className="p-3 rounded-lg border border-border space-y-3">
                <span className="font-semibold uppercase text-text-secondary flex items-center gap-1.5">
                  <Package className="h-3.5 w-3.5" />
                  Catálogo ANVISA & Cálculo de Valor
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 items-end">
                  <Select
                    label="Produto / SKU"
                    value={selectedSku}
                    onChange={(e) => setSelectedSku(e.target.value)}
                    options={[
                      { value: "", label: "Selecione um SKU" },
                      ...catalogProducts.map((p) => ({
                        value: p.sku,
                        label: `${p.sku} — ${p.name}`,
                      })),
                    ]}
                  />
                  <div>
                    <label className="block text-text-secondary mb-1">Quantidade</label>
                    <Input
                      type="number"
                      min="1"
                      value={itemQty}
                      onChange={(e) => setItemQty(e.target.value)}
                    />
                  </div>
                  <Button type="button" variant="outline" size="sm" onClick={handleAddCartLine} disabled={!selectedSku}>
                    Adicionar Item
                  </Button>
                </div>
                {cartLines.length > 0 && (
                  <div className="space-y-1">
                    {cartLines.map((l) => (
                      <div key={l.sku} className="flex items-center justify-between text-xs p-1.5 rounded bg-surface-bg">
                        <span className="truncate">{l.qty}x {l.name}</span>
                        <span className="font-semibold shrink-0">
                          {new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(l.qty * l.unitPrice)}
                        </span>
                      </div>
                    ))}
                    <div className="flex items-center justify-between pt-1 border-t border-border-subtle">
                      <span className="font-semibold text-text-main">Total do Carrinho</span>
                      <span className="font-bold text-brand-primary">
                        {new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(cartTotal)}
                      </span>
                    </div>
                    <Button type="button" size="sm" onClick={handleApplyCartToDealValue} disabled={savingDrawer} className="w-full">
                      Atualizar Valor do Deal (BRL)
                    </Button>
                  </div>
                )}
              </div>

              {/* Ações Rápidas: PDF / DENTGO / LiveKit */}
              <div className="p-3 rounded-lg border border-border space-y-3">
                <span className="font-semibold uppercase text-text-secondary block">Ações Comerciais & Logísticas</span>
                <Button
                  type="button"
                  variant="secondary"
                  size="sm"
                  onClick={handleGenerateProposalPdf}
                  disabled={generatingPdf}
                  className="w-full gap-1.5"
                >
                  <FileDown className="h-4 w-4 text-brand-primary" />
                  {generatingPdf ? "Gerando Proposta..." : "Gerar Proposta Comercial PDF"}
                </Button>
                {showDentgoDispatch && (
                  <Button
                    type="button"
                    variant="default"
                    size="sm"
                    onClick={handleDispatchDentgo}
                    disabled={dispatching}
                    className="w-full gap-1.5"
                  >
                    <Truck className="h-4 w-4" />
                    {dispatching ? "Despachando..." : "Despachar com DENTGO (45 min)"}
                  </Button>
                )}
                <Button
                  type="button"
                  variant="secondary"
                  size="sm"
                  onClick={() => setShowDealVideoModal(true)}
                  className="w-full gap-1.5"
                >
                  <Video className="h-4 w-4 text-brand-primary" />
                  Abrir Vídeo SOS / Sala LiveKit
                </Button>
              </div>

              <div className="p-3 rounded-lg border border-border space-y-3">
                <span className="font-semibold uppercase text-text-secondary block">Teleconsulta e Copiloto de Reunião</span>
                <GranolaCopilotCard dealId={String(selectedDeal.id)} onApplySuccess={() => refetchDeals()} />
              </div>
              <LiveKitDealRoomModal
                isOpen={showDealVideoModal}
                onClose={() => setShowDealVideoModal(false)}
                dealId={String(selectedDeal.id)}
                dealTitle={selectedDeal.title}
                contactName={selectedDeal.contact_name}
              />

              <div className="p-3 rounded-lg border border-border space-y-3">
                <span className="font-semibold uppercase text-text-secondary block">Edição Inline da Oportunidade</span>
                <div>
                  <label className="block text-text-secondary mb-1">Título</label>
                  <Input value={editTitle} onChange={(e) => setEditTitle(e.target.value)} />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-text-secondary mb-1">Valor (R$)</label>
                    <Input type="number" value={editValue} onChange={(e) => setEditValue(e.target.value)} />
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
                  <label className="block text-text-secondary mb-1">Previsão de Fechamento</label>
                  <Input type="date" value={editCloseDate} onChange={(e) => setEditCloseDate(e.target.value)} />
                </div>
                <div>
                  <label className="block text-text-secondary mb-1">Nota de Auditoria</label>
                  <Input value={editComment} onChange={(e) => setEditComment(e.target.value)} placeholder="Motivo da revisão comercial..." />
                </div>
                <Button type="button" size="sm" onClick={handleUpdateDealInline} disabled={savingDrawer} className="w-full gap-1.5">
                  <Save className="h-3.5 w-3.5" />
                  {savingDrawer ? "Salvando..." : "Salvar Alterações Inline"}
                </Button>
              </div>

              <div className="p-3 rounded-lg border border-border space-y-3">
                <span className="font-semibold uppercase text-text-secondary block">Checklist de Tarefas Operacionais</span>
                <form onSubmit={handleCreateTask} className="flex gap-2">
                  <Input value={newTaskTitle} onChange={(e) => setNewTaskTitle(e.target.value)} placeholder="Nova tarefa..." />
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
                          {isDone ? <CheckSquare className="h-4 w-4 text-status-success shrink-0" /> : <Square className="h-4 w-4 text-text-muted shrink-0" />}
                          <span className={isDone ? "line-through text-text-muted truncate" : "text-text-main truncate"}>{t.title}</span>
                        </div>
                        <Badge variant="secondary" className="text-[10px] shrink-0">{t.due_date}</Badge>
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="p-3 rounded-lg border border-border space-y-2">
                <span className="font-semibold uppercase text-text-secondary flex items-center gap-1.5">
                  <Clock className="h-3.5 w-3.5" />
                  Linha do Tempo Auditável
                </span>
                {timeline.length === 0 ? (
                  <p className="text-text-muted py-2">Nenhum evento registrado para este negócio.</p>
                ) : (
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {timeline.map((ev, idx) => (
                      <div key={ev.id ?? idx} className="p-2 rounded bg-surface-bg border border-border-subtle">
                        <div className="flex justify-between font-medium text-text-main">
                          <span>{ev.action || ev.event_type || "Evento"}</span>
                          <span className="text-[10px] text-text-muted">{ev.created_at || ev.timestamp || ""}</span>
                        </div>
                        <p className="text-text-secondary mt-0.5">{ev.description || ev.details || ""}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </Sheet>
      </div>
    </ErrorBoundary>
  );
};

export default DealsWorkspace;
