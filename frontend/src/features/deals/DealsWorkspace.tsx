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
import { ModalTabBar } from "@/components/ui/ModalTabBar";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorBoundary } from "@/components/ui/ErrorBoundary";
import { RouteHeader } from "@/components/ui/RouteHeader";
import { Deal } from "@/types/api_contracts";
import {
  Plus,
  RefreshCw,
  AlertCircle,
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
  BadgeCheck,
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
    localStorage.getItem("revnault_active_user_id") ||
    localStorage.getItem("revnault_user_id") ||
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
  const [dealModalTab, setDealModalTab] = React.useState<"overview" | "catalog" | "copilot" | "timeline">("overview");
  const [tasksPage, setTasksPage] = React.useState<number>(1);
  const [timelinePage, setTimelinePage] = React.useState<number>(1);
  const [cartPage, setCartPage] = React.useState<number>(1);
  const TASKS_PER_PAGE = 4;
  const TIMELINE_PER_PAGE = 4;
  const CART_PER_PAGE = 4;
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

  // TICKET-DEALS-01: Aprovação Rápida de Desconto
  const handleQuickApproveDiscount = async (targetDealId?: string) => {
    const dealId = targetDealId || selectedDeal?.id;
    if (!dealId) return;
    setSavingDrawer(true);
    setDealActionError(null);
    try {
      const res = await fetch("/api/v1/deals/catalog/approve-discount", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          request_id: `disc-req-${dealId}`,
          approver_user_id: userId || "usr_dir_comercial",
          account_id: "0f14ffff",
        }),
      });
      if (!res.ok) {
        const resCredit = await fetch(`/api/v1/deals/${dealId}/approve-credit`, {
          method: "POST",
          headers: { "Content-Type": "application/json", "X-User-Id": userId },
        });
        if (!resCredit.ok) throw new Error("Falha ao aprovar desconto no catálogo.");
      }
      setDealActionFeedback("Aprovação rápida de desconto/crédito homologada com sucesso (1-Clique)!");
      await dealsQuery.refetch();
      if (selectedDeal?.id === dealId) {
        await loadDealTimeline(dealId);
      }
    } catch (err: any) {
      setDealActionError(err.message || "Erro na aprovação rápida de desconto.");
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

  const [exportFormat, setExportFormat] = React.useState<"csv" | "parquet">("csv");
  const [isExporting, setIsExporting] = React.useState<boolean>(false);

  const handleExportDeals = async () => {
    setIsExporting(true);
    try {
      const res = await fetch(`/api/v1/deals/export?format=${exportFormat}&pipeline_id=${encodeURIComponent(selectedPipelineId)}`, {
        headers: { "X-User-Id": userId },
      });
      if (!res.ok) throw new Error(`Falha ao exportar ${exportFormat.toUpperCase()} do pipeline.`);
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `pipeline_revnault_${selectedPipelineId}.${exportFormat}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      setDealActionFeedback(`Exportação ${exportFormat.toUpperCase()} concluída com sucesso.`);
    } catch (err: any) {
      setDealActionError(err.message || "Erro ao exportar arquivo.");
    } finally {
      setIsExporting(false);
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

  // TICKET-DEALS-02: Reordenação dinâmica de estágios no Kanban
  const [customStageOrder, setCustomStageOrder] = React.useState<number[]>([]);

  React.useEffect(() => {
    if (rawStages.length > 0 && customStageOrder.length === 0) {
      setCustomStageOrder(rawStages.map((s) => Number(s.id)));
    }
  }, [rawStages, customStageOrder.length]);

  const orderedStages = React.useMemo(() => {
    if (customStageOrder.length === 0) return rawStages;
    return [...rawStages].sort((a, b) => {
      const idxA = customStageOrder.indexOf(Number(a.id));
      const idxB = customStageOrder.indexOf(Number(b.id));
      if (idxA === -1 && idxB === -1) return 0;
      if (idxA === -1) return 1;
      if (idxB === -1) return -1;
      return idxA - idxB;
    });
  }, [rawStages, customStageOrder]);

  const handleReorderStage = (stageId: string | number, direction: "left" | "right") => {
    const numId = Number(stageId);
    const current = customStageOrder.length > 0 ? [...customStageOrder] : rawStages.map((s) => Number(s.id));
    const idx = current.indexOf(numId);
    if (idx === -1) return;
    if (direction === "left" && idx > 0) {
      const temp = current[idx - 1];
      current[idx - 1] = current[idx];
      current[idx] = temp;
      setCustomStageOrder(current);
      setDealActionFeedback(`Estágio movido para a esquerda.`);
    } else if (direction === "right" && idx < current.length - 1) {
      const temp = current[idx + 1];
      current[idx + 1] = current[idx];
      current[idx] = temp;
      setCustomStageOrder(current);
      setDealActionFeedback(`Estágio movido para a direita.`);
    }
  };

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
    const stageList = orderedStages.length > 0 ? orderedStages : [{ id: 101, name: "Qualificação" }];
    return stageList.map((st) => ({
      id: st.id,
      name: st.name,
      items: filteredDeals.filter((d) => Number(d.stage_id) === Number(st.id)),
    }));
  }, [orderedStages, filteredDeals]);

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

  const pipelines = pipelinesQuery.data || [{ id: 1, name: "Funil Principal RevNault" }];

  return (
    <ErrorBoundary onReset={() => dealsQuery.refetch()}>
      <div className="space-y-6 max-w-7xl mx-auto">
        <RouteHeader
          title="Cockpit de Negócios & Consignação Cirúrgica"
          description="Operação unificada RevNault + KeyPartners (Kits & ANVISA) + DENTGO (Logística Same-Day). Clique em um negócio para abrir o Dossiê e Aprovação de Crédito."
          exportConfig={{
            format: exportFormat,
            onFormatChange: (fmt) => setExportFormat(fmt as "csv" | "parquet"),
            onExport: handleExportDeals,
            loading: isExporting,
            label: "FORMATO",
            exportLabel: "Exportar",
          }}
          actions={[
            {
              id: "new-deal",
              label: "Oportunidade",
              variant: "default",
              icon: <Plus className="h-3.5 w-3.5" />,
              title: "Cadastrar Nova Oportunidade",
              onClick: () => setIsNewDealOpen(true),
            },
            {
              id: "refresh",
              label: "Atualizar",
              variant: "outline",
              icon: <RefreshCw className={`h-3.5 w-3.5 ${dealsQuery.isFetching ? "animate-spin" : ""}`} />,
              title: "Atualizar Negócios",
              onClick: () => dealsQuery.refetch(),
              disabled: dealsQuery.isFetching,
            },
          ]}
        />

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
          <Button
            variant="secondary"
            size="sm"
            onClick={() => {
              const pendingDeal = rawDeals.find((d) => !Boolean((d as any).credit_approved) || d.stage_id === 103) || rawDeals[0];
              if (pendingDeal) {
                handleQuickApproveDiscount(String(pendingDeal.id));
              } else {
                setDealActionFeedback("Nenhum deal pendente de aprovação no momento.");
              }
            }}
            disabled={savingDrawer}
            className="gap-1.5 shrink-0"
          >
            <BadgeCheck className="h-3.5 w-3.5 text-status-success" />
            Aprovação Rápida de Desconto
          </Button>
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
            onReorderStage={handleReorderStage}
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

        <Dialog isOpen={isNewDealOpen} onClose={() => setIsNewDealOpen(false)} title="Nova Oportunidade Cirúrgica" size="form">
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

        <Dialog
          isOpen={Boolean(selectedDeal)}
          onClose={() => setSelectedDeal(null)}
          size="80vh"
          title={selectedDeal ? `Dossiê do Negócio #${selectedDeal.id}` : "Dossiê"}
          description={selectedDeal ? `${selectedDeal.company_name || (selectedDeal as any).company || ""} • ${selectedDeal.contact_name || ""}` : ""}
          footer={
            <div className="flex items-center justify-between w-full">
              <span className="text-xs text-text-muted">
                Governança RevNault • Negociação #{selectedDeal?.id}
              </span>
              <Button variant="secondary" size="sm" onClick={() => setSelectedDeal(null)}>
                Fechar Dossiê
              </Button>
            </div>
          }
        >
          {selectedDeal && (
            <div className="flex flex-col min-h-full text-xs pb-6">
              {/* Barra de Abas Padronizada via ModalTabBar */}
              <ModalTabBar
                tabs={[
                  { id: "overview", label: "Visão Geral", icon: <ShieldCheck className="h-4 w-4" /> },
                  { id: "catalog", label: "Catálogo & Itens", count: cartLines.length, icon: <Package className="h-4 w-4" /> },
                  { id: "copilot", label: "Tarefas & Copiloto", count: tasks.filter((t) => !t.completed).length, icon: <CheckSquare className="h-4 w-4" /> },
                  { id: "timeline", label: "Linha do Tempo", count: timeline.length, icon: <Clock className="h-4 w-4" /> },
                ]}
                activeTab={dealModalTab}
                onChange={(t) => setDealModalTab(t as any)}
              />

              {/* ABA 1: Visão Geral, Edição & Governança */}
              {dealModalTab === "overview" && (
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
                  {/* Coluna Esquerda: Edição dos Dados */}
                  <div className="lg:col-span-7 space-y-4">
                    <div className="p-4 rounded-xl border border-border bg-surface-card space-y-3 shadow-2xs">
                      <span className="font-semibold uppercase text-text-secondary flex items-center justify-between">
                        <span>Dados Comerciais da Oportunidade</span>
                        <Badge variant="navy">ID: {selectedDeal.id}</Badge>
                      </span>

                      <div>
                        <label className="block text-text-secondary mb-1 font-medium">Título da Negociação</label>
                        <Input value={editTitle} onChange={(e) => setEditTitle(e.target.value)} />
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <div>
                          <label className="block text-text-secondary mb-1 font-medium">Valor Estimado (R$)</label>
                          <Input type="number" value={editValue} onChange={(e) => setEditValue(e.target.value)} />
                        </div>
                        <Select
                          label="Nível de Prioridade"
                          value={editPriority}
                          onChange={(e) => setEditPriority(e.target.value)}
                          options={[
                            { value: "alta", label: "Alta" },
                            { value: "media", label: "Média" },
                            { value: "baixa", label: "Baixa" },
                          ]}
                        />
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <div>
                          <label className="block text-text-secondary mb-1 font-medium">Previsão de Fechamento</label>
                          <Input type="date" value={editCloseDate} onChange={(e) => setEditCloseDate(e.target.value)} />
                        </div>
                        <div>
                          <label className="block text-text-secondary mb-1 font-medium">Nota de Auditoria</label>
                          <Input value={editComment} onChange={(e) => setEditComment(e.target.value)} placeholder="Motivo da revisão..." />
                        </div>
                      </div>

                      <Button type="button" size="sm" onClick={handleUpdateDealInline} disabled={savingDrawer} className="w-full gap-1.5 mt-2">
                        <Save className="h-3.5 w-3.5" />
                        {savingDrawer ? "Salvando..." : "Salvar Alterações da Oportunidade"}
                      </Button>
                    </div>
                  </div>

                  {/* Coluna Direita: Governança & Ações Rápidas */}
                  <div className="lg:col-span-5 space-y-4">
                    {/* Bloco de Governança de Estágio */}
                    <div className="p-4 rounded-xl bg-surface-bg border border-border space-y-3 shadow-2xs">
                      <span className="font-semibold uppercase text-text-secondary block">
                        Governança de Estágio & Crédito
                      </span>
                      <Select
                        label="Mover Estágio no Funil"
                        value={editStageId}
                        onChange={(e) => handleMoveStage(e.target.value)}
                        options={rawStages.map((s) => ({ value: String(s.id), label: s.name }))}
                      />
                      <div className="grid grid-cols-1 gap-2 pt-1">
                        <Button
                          type="button"
                          variant="default"
                          size="sm"
                          onClick={() => handleQuickApproveDiscount()}
                          disabled={savingDrawer}
                          className="w-full gap-1.5"
                        >
                          <BadgeCheck className="h-4 w-4" />
                          Aprovação Rápida de Desconto (1-Clique)
                        </Button>
                        <Button
                          type="button"
                          variant="secondary"
                          size="sm"
                          onClick={handleApproveCredit}
                          disabled={savingDrawer}
                          className="w-full gap-1.5"
                        >
                          <ShieldCheck className="h-4 w-4 text-status-success" />
                          Aprovar Limite de Crédito
                        </Button>
                      </div>
                    </div>

                    {/* Bloco de Ações Comerciais Rápidas */}
                    <div className="p-4 rounded-xl border border-border bg-surface-card space-y-2.5 shadow-2xs">
                      <span className="font-semibold uppercase text-text-secondary block">
                        Ações Comerciais & Logísticas
                      </span>
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
                  </div>
                </div>
              )}

              {/* ABA 2: Catálogo ANVISA & Itens */}
              {dealModalTab === "catalog" && (
                <div className="space-y-4">
                  <div className="p-4 rounded-xl border border-border bg-surface-card space-y-4 shadow-2xs">
                    <span className="font-semibold uppercase text-text-secondary flex items-center gap-1.5">
                      <Package className="h-4 w-4 text-brand-primary" />
                      Adicionar Produtos do Catálogo ANVISA
                    </span>
                    <div className="grid grid-cols-1 sm:grid-cols-12 gap-3 items-end">
                      <div className="sm:col-span-7">
                        <Select
                          label="Produto / SKU Dental"
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
                      </div>
                      <div className="sm:col-span-2">
                        <label className="block text-text-secondary mb-1 font-medium">Qtd</label>
                        <Input
                          type="number"
                          min="1"
                          value={itemQty}
                          onChange={(e) => setItemQty(e.target.value)}
                        />
                      </div>
                      <div className="sm:col-span-3">
                        <Button type="button" variant="outline" size="sm" onClick={handleAddCartLine} disabled={!selectedSku} className="w-full">
                          Adicionar Item
                        </Button>
                      </div>
                    </div>
                  </div>

                  {/* Listagem de Itens e Resumo Paginado */}
                  <div className="p-4 rounded-xl border border-border bg-surface-card space-y-3 shadow-2xs">
                    <span className="font-semibold uppercase text-text-secondary flex items-center justify-between">
                      <span>Itens Incluídos na Oportunidade ({cartLines.length})</span>
                      {cartLines.length > CART_PER_PAGE && (
                        <span className="text-text-muted text-[11px] font-mono">
                          Pág. {cartPage}/{Math.ceil(cartLines.length / CART_PER_PAGE)}
                        </span>
                      )}
                    </span>

                    {cartLines.length === 0 ? (
                      <div className="py-8 text-center text-text-muted border border-dashed border-border rounded-lg">
                        Nenhum item adicionado ao carrinho desta negociação.
                      </div>
                    ) : (
                      <div className="space-y-2">
                        <div className="divide-y divide-border-subtle rounded-lg border border-border overflow-hidden">
                          {cartLines.slice((cartPage - 1) * CART_PER_PAGE, cartPage * CART_PER_PAGE).map((l) => (
                            <div key={l.sku} className="flex items-center justify-between p-3 bg-surface-card hover:bg-surface-bg/50">
                              <div className="min-w-0 pr-3">
                                <span className="font-semibold text-text-main block truncate">{l.name}</span>
                                <span className="text-[11px] text-text-secondary font-mono">SKU: {l.sku} • Qtd: {l.qty} un</span>
                              </div>
                              <span className="font-bold text-text-main font-mono shrink-0">
                                {new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(l.qty * l.unitPrice)}
                              </span>
                            </div>
                          ))}
                        </div>

                        {/* Paginação do Carrinho */}
                        {Math.ceil(cartLines.length / CART_PER_PAGE) > 1 && (
                          <div className="flex items-center justify-between pt-1 text-xs">
                            <span className="text-text-muted text-[11px]">
                              Mostrando {((cartPage - 1) * CART_PER_PAGE) + 1}–{Math.min(cartPage * CART_PER_PAGE, cartLines.length)} de {cartLines.length} itens
                            </span>
                            <div className="flex items-center gap-1.5">
                              <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                disabled={cartPage <= 1}
                                onClick={() => setCartPage((p) => Math.max(1, p - 1))}
                                className="h-6 px-2 text-[11px]"
                              >
                                Anterior
                              </Button>
                              <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                disabled={cartPage >= Math.ceil(cartLines.length / CART_PER_PAGE)}
                                onClick={() => setCartPage((p) => Math.min(Math.ceil(cartLines.length / CART_PER_PAGE), p + 1))}
                                className="h-6 px-2 text-[11px]"
                              >
                                Próxima
                              </Button>
                            </div>
                          </div>
                        )}

                        <div className="flex items-center justify-between p-3 rounded-lg bg-surface-bg border border-border-subtle mt-2">
                          <span className="font-bold text-text-main text-sm">Valor Total do Pedido</span>
                          <span className="font-extrabold text-base text-brand-primary font-mono">
                            {new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(cartTotal)}
                          </span>
                        </div>

                        <Button type="button" size="sm" onClick={handleApplyCartToDealValue} disabled={savingDrawer} className="w-full mt-1">
                          Atualizar Valor do Negócio com o Total do Carrinho
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* ABA 3: Tarefas Operacionais & Copiloto IA */}
              {dealModalTab === "copilot" && (
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
                  {/* Checklist de Tarefas Paginado (Zero Scroll Vertical) */}
                  <div className="lg:col-span-5 p-4 rounded-xl border border-border bg-surface-card space-y-3 shadow-2xs">
                    <span className="font-semibold uppercase text-text-secondary flex items-center justify-between">
                      <span>Tarefas Operacionais ({tasks.length})</span>
                      {Math.ceil(tasks.length / TASKS_PER_PAGE) > 1 && (
                        <span className="text-text-muted text-[11px] font-mono">
                          Pág. {tasksPage}/{Math.ceil(tasks.length / TASKS_PER_PAGE)}
                        </span>
                      )}
                    </span>
                    <form onSubmit={handleCreateTask} className="flex gap-2">
                      <Input value={newTaskTitle} onChange={(e) => setNewTaskTitle(e.target.value)} placeholder="Nova tarefa..." />
                      <Button type="submit" size="sm" variant="outline" className="shrink-0">
                        Adicionar
                      </Button>
                    </form>
                    <div className="divide-y divide-border-subtle rounded-lg border border-border overflow-hidden">
                      {tasks.length === 0 ? (
                        <p className="text-text-muted py-6 text-center text-xs">Nenhuma tarefa pendente.</p>
                      ) : (
                        tasks.slice((tasksPage - 1) * TASKS_PER_PAGE, tasksPage * TASKS_PER_PAGE).map((t) => {
                          const isDone = Boolean(t.completed);
                          return (
                            <button
                              key={t.id}
                              type="button"
                              onClick={() => handleToggleTask(t)}
                              className="w-full py-2.5 flex items-center justify-between text-left hover:bg-surface-bg px-2.5 transition bg-surface-card"
                            >
                              <div className="flex items-center gap-2 min-w-0 pr-2">
                                {isDone ? <CheckSquare className="h-4 w-4 text-status-success shrink-0" /> : <Square className="h-4 w-4 text-text-muted shrink-0" />}
                                <span className={isDone ? "line-through text-text-muted truncate text-xs" : "text-text-main truncate text-xs"}>{t.title}</span>
                              </div>
                              <Badge variant="secondary" className="text-[10px] shrink-0 font-mono">{t.due_date}</Badge>
                            </button>
                          );
                        })
                      )}
                    </div>

                    {/* Controles de Paginação de Tarefas */}
                    {Math.ceil(tasks.length / TASKS_PER_PAGE) > 1 && (
                      <div className="flex items-center justify-between pt-1 border-t border-border-subtle text-xs">
                        <span className="text-text-muted text-[11px]">
                          {tasks.filter((t) => !t.completed).length} pendentes
                        </span>
                        <div className="flex items-center gap-1.5">
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            disabled={tasksPage <= 1}
                            onClick={() => setTasksPage((p) => Math.max(1, p - 1))}
                            className="h-6 px-2 text-[11px]"
                          >
                            Anterior
                          </Button>
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            disabled={tasksPage >= Math.ceil(tasks.length / TASKS_PER_PAGE)}
                            onClick={() => setTasksPage((p) => Math.min(Math.ceil(tasks.length / TASKS_PER_PAGE), p + 1))}
                            className="h-6 px-2 text-[11px]"
                          >
                            Próxima
                          </Button>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Copiloto de IA */}
                  <div className="lg:col-span-7 p-4 rounded-xl border border-border bg-surface-card space-y-3 shadow-2xs min-w-0">
                    <span className="font-semibold uppercase text-text-secondary block">
                      Copiloto IA & Transcrição de Reunião
                    </span>
                    <GranolaCopilotCard dealId={String(selectedDeal.id)} onApplySuccess={() => refetchDeals()} />
                  </div>
                </div>
              )}

              {/* ABA 4: Linha do Tempo Auditável Paginada (Zero Scroll Vertical) */}
              {dealModalTab === "timeline" && (
                <div className="p-4 rounded-xl border border-border bg-surface-card space-y-3 shadow-2xs">
                  <div className="flex items-center justify-between pb-1 border-b border-border-subtle">
                    <span className="font-semibold uppercase text-text-secondary flex items-center gap-1.5">
                      <Clock className="h-4 w-4 text-brand-primary" />
                      Histórico Auditável ({timeline.length} eventos)
                    </span>
                    {Math.ceil(timeline.length / TIMELINE_PER_PAGE) > 1 && (
                      <span className="text-text-muted text-[11px] font-mono">
                        Página {timelinePage} de {Math.ceil(timeline.length / TIMELINE_PER_PAGE)}
                      </span>
                    )}
                  </div>

                  {timeline.length === 0 ? (
                    <p className="text-text-muted py-8 text-center text-xs">Nenhum evento registrado para este negócio.</p>
                  ) : (
                    <div className="space-y-2.5">
                      {timeline.slice((timelinePage - 1) * TIMELINE_PER_PAGE, timelinePage * TIMELINE_PER_PAGE).map((ev, idx) => (
                        <div key={ev.id ?? idx} className="p-3 rounded-lg bg-surface-bg border border-border-subtle hover:border-brand-primary/30 transition">
                          <div className="flex justify-between items-center font-medium text-text-main mb-1">
                            <span className="font-semibold text-xs">{ev.action || ev.event_type || "Evento"}</span>
                            <span className="text-[10px] text-text-muted font-mono">{ev.created_at || ev.timestamp || ""}</span>
                          </div>
                          <p className="text-text-secondary text-xs">{ev.description || ev.details || ""}</p>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Controles de Paginação da Linha do Tempo */}
                  {Math.ceil(timeline.length / TIMELINE_PER_PAGE) > 1 && (
                    <div className="flex items-center justify-between pt-2 border-t border-border-subtle text-xs">
                      <span className="text-text-muted text-[11px]">
                        Eventos {((timelinePage - 1) * TIMELINE_PER_PAGE) + 1}–{Math.min(timelinePage * TIMELINE_PER_PAGE, timeline.length)} de {timeline.length}
                      </span>
                      <div className="flex items-center gap-1.5">
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          disabled={timelinePage <= 1}
                          onClick={() => setTimelinePage((p) => Math.max(1, p - 1))}
                          className="h-6 px-2 text-[11px]"
                        >
                          Anterior
                        </Button>
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          disabled={timelinePage >= Math.ceil(timeline.length / TIMELINE_PER_PAGE)}
                          onClick={() => setTimelinePage((p) => Math.min(Math.ceil(timeline.length / TIMELINE_PER_PAGE), p + 1))}
                          className="h-6 px-2 text-[11px]"
                        >
                          Próxima
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Modal do LiveKit mantido */}
              <LiveKitDealRoomModal
                isOpen={showDealVideoModal}
                onClose={() => setShowDealVideoModal(false)}
                dealId={String(selectedDeal.id)}
                dealTitle={selectedDeal.title}
                contactName={selectedDeal.contact_name}
              />
            </div>
          )}
        </Dialog>
      </div>
    </ErrorBoundary>
  );
};

export default DealsWorkspace;
