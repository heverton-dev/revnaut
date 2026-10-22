// -*- coding: utf-8 -*-
/**
 * MarketIntelRadarWorkspace.tsx
 * Inteligência de Mercado, Radar Autônomo de Concorrência e Disparo Determinístico com
 * Trava Anti-Spam de 15 dias (TICKET-MKTINTEL-09). Matriz RBAC territorial da Seção 5
 * simulável no cabeçalho via X-User-Role / X-User-Region.
 * Lei #14: zero emojis; ícones SVG Lucide; somente classes semânticas de tokens.css.
 */

import React from "react";
import {
  Radar,
  Globe2,
  Building2,
  Target,
  Send,
  ShieldCheck,
  ShieldAlert,
  Clock,
  Hash,
  Timer,
  RefreshCw,
  Plus,
  ExternalLink,
  FileText,
  Lock,
  CheckCircle2,
  Smartphone,
} from "lucide-react";
import { Tabs } from "@/components/ui/Tabs";
import { RouteHeader } from "@/components/ui/RouteHeader";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { Select } from "@/components/ui/Select";
import { Input } from "@/components/ui/Input";
import { Dialog } from "@/components/ui/Dialog";
import { EmptyState } from "@/components/ui/EmptyState";
import { Skeleton } from "@/components/ui/Skeleton";
import type {
  MarketSignal,
  MarketSignalPage,
  MarketOpportunity,
  TargetedCampaign,
  CampaignDispatchResult,
  CompetitorListResponse,
  CompetitorSnapshot,
  TacticalInsightsResponse,
  MarketIntelRole,
  MarketIntelPrincipal,
} from "@/types/api_contracts";

type TabId = "signals" | "competitors" | "opportunities" | "campaigns";

interface RoleOption {
  role: MarketIntelRole;
  label: string;
  region: string;
}

const ROLE_OPTIONS: RoleOption[] = [
  { role: "director", label: "Diretor Nacional (Global)", region: "GLOBAL" },
  { role: "regional_manager", label: "Gerente Regional", region: "BR-SP" },
  { role: "inside_sales", label: "Consultor Interno (SDR/Inside)", region: "BR-SP" },
  { role: "field_sales", label: "Consultor Externo (Campo)", region: "BR-SP" },
];

const REGION_OPTIONS = ["GLOBAL", "BR-SP", "BR-PR", "BR-PE", "US-FL", "LATAM"];
const SOURCE_TYPE_LABELS: Record<string, string> = {
  regulatory_anvisa: "Regulatório (ANVISA/FDA)",
  scientific_journal: "Periódico Científico",
  congress_ciosp: "Congresso (CIOSP)",
  news: "Notícia Setorial",
};
const SPECIALTIES = ["Implantodontia", "Protese Digital", "Periodontia", "Cirurgia Bucomaxilofacial"];
const BU_OPTIONS = ["Implantodontia", "Prótese Digital", "Biomateriais"];
const OPP_TYPE_LABELS: Record<string, string> = {
  PRICE_COUNTER_ATTACK: "Contra-ataque de Preço",
  CLINICAL_UPGRADE: "Atualização Clínica",
  EVENT_SURGE: "Pico de Evento",
};

const formatBrl = (v: number | null | undefined) =>
  typeof v === "number" ? v.toLocaleString("pt-BR", { style: "currency", currency: "BRL" }) : "-";

const formatDateTime = (iso?: string | null) => {
  if (!iso) return "-";
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? iso : d.toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
};

async function readError(res: Response): Promise<string> {
  try {
    const data = await res.json();
    if (typeof data.detail === "string") return data.detail;
    if (data.detail?.message) {
      const v: string[] = data.detail.violations || [];
      return v.length ? `${data.detail.message} ${v.join(" ")}` : data.detail.message;
    }
    return `HTTP ${res.status}`;
  } catch {
    return `HTTP ${res.status}`;
  }
}

export interface MarketIntelRadarWorkspaceProps {
  initialTab?: TabId;
}

export const MarketIntelRadarWorkspace: React.FC<MarketIntelRadarWorkspaceProps> = ({ initialTab = "signals" }) => {
  const [activeTab, setActiveTab] = React.useState<TabId>(initialTab);
  // Perfil real vem do backend (token de sessão); simulação só é permitida para Diretoria.
  const [me, setMe] = React.useState<MarketIntelPrincipal | null>(null);
  const [role, setRole] = React.useState<MarketIntelRole>("field_sales");
  const [region, setRegion] = React.useState<string>("BR-SP");
  const [feedback, setFeedback] = React.useState<string | null>(null);
  const [error, setError] = React.useState<string | null>(null);

  const canSimulate = me?.can_simulate === true;
  const canManageCompetitors = me?.can_manage_competitors === true;
  const canGenerateDraft = me?.can_generate_draft === true;
  const canDispatch = me?.can_dispatch === true;
  const isFieldView = (me?.effective_role || role) === "field_sales";

  const rbacHeaders = React.useMemo(() => {
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    const token = typeof window !== "undefined" ? localStorage.getItem("revnault_auth_token") : null;
    if (token) headers.Authorization = `Bearer ${token}`;
    if (canSimulate) {
      headers["X-User-Role"] = role;
      headers["X-User-Region"] = region;
    }
    return headers;
  }, [canSimulate, role, region]);

  const api = React.useCallback(
    async <T,>(path: string, init?: RequestInit): Promise<T> => {
      const res = await fetch(path, { ...init, headers: { ...rbacHeaders, ...(init?.headers || {}) } });
      if (!res.ok) throw new Error(await readError(res));
      return (await res.json()) as T;
    },
    [rbacHeaders]
  );

  // Tab 1: Sinais
  const [signalScope, setSignalScope] = React.useState<string>("");
  const [signalSpecialty, setSignalSpecialty] = React.useState<string>("");
  const [signalSource, setSignalSource] = React.useState<string>("");
  const [signals, setSignals] = React.useState<MarketSignalPage | null>(null);
  const [loadingSignals, setLoadingSignals] = React.useState(false);

  // Tab 2: Concorrentes
  const [competitors, setCompetitors] = React.useState<CompetitorListResponse | null>(null);
  const [selectedCompetitorId, setSelectedCompetitorId] = React.useState<string>("");
  const [snapshots, setSnapshots] = React.useState<CompetitorSnapshot[]>([]);
  const [insights, setInsights] = React.useState<TacticalInsightsResponse | null>(null);
  const [showCompetitorModal, setShowCompetitorModal] = React.useState(false);
  const [newCompName, setNewCompName] = React.useState("");
  const [newCompDomain, setNewCompDomain] = React.useState("");
  const [newCompFrequency, setNewCompFrequency] = React.useState("72");
  const [savingCompetitor, setSavingCompetitor] = React.useState(false);

  // Tab 3: Oportunidades
  const [oppBu, setOppBu] = React.useState<string>("");
  const [oppRegion, setOppRegion] = React.useState<string>("");
  const [oppStatus, setOppStatus] = React.useState<string>("");
  const [opportunities, setOpportunities] = React.useState<MarketOpportunity[]>([]);
  const [loadingOpps, setLoadingOpps] = React.useState(false);
  const [draftChannel, setDraftChannel] = React.useState<"WHATSAPP" | "EMAIL">("WHATSAPP");
  const [generatingFor, setGeneratingFor] = React.useState<string | null>(null);

  // Tab 4: Campanhas
  const [campaigns, setCampaigns] = React.useState<TargetedCampaign[]>([]);
  const [selectedCampaignId, setSelectedCampaignId] = React.useState<string>("");
  const [dispatchingId, setDispatchingId] = React.useState<string | null>(null);
  const [lastDispatch, setLastDispatch] = React.useState<CampaignDispatchResult | null>(null);

  const notify = (ok: string | null, err: string | null = null) => {
    setFeedback(ok);
    setError(err);
  };

  const loadSignals = React.useCallback(async () => {
    setLoadingSignals(true);
    try {
      const qs = new URLSearchParams({ limit: "50" });
      if (signalScope) qs.set("scope", signalScope);
      if (signalSpecialty) qs.set("specialty", signalSpecialty);
      if (signalSource) qs.set("source_type", signalSource);
      setSignals(await api<MarketSignalPage>(`/api/v1/market-intel/signals?${qs.toString()}`));
    } catch (e: any) {
      setSignals(null);
      notify(null, e.message);
    } finally {
      setLoadingSignals(false);
    }
  }, [api, signalScope, signalSpecialty, signalSource]);

  const loadCompetitors = React.useCallback(async () => {
    try {
      const [list, ins] = await Promise.all([
        api<CompetitorListResponse>("/api/v1/competitors"),
        api<TacticalInsightsResponse>("/api/v1/competitors/tactical-insights"),
      ]);
      setCompetitors(list);
      setInsights(ins);
      if (!selectedCompetitorId && list.items.length > 0) setSelectedCompetitorId(list.items[0].id);
    } catch (e: any) {
      notify(null, e.message);
    }
  }, [api, selectedCompetitorId]);

  const loadSnapshots = React.useCallback(async () => {
    if (!selectedCompetitorId) return;
    try {
      setSnapshots(await api<CompetitorSnapshot[]>(`/api/v1/competitors/${encodeURIComponent(selectedCompetitorId)}/snapshots`));
    } catch (e: any) {
      setSnapshots([]);
      notify(null, e.message);
    }
  }, [api, selectedCompetitorId]);

  const loadOpportunities = React.useCallback(async () => {
    setLoadingOpps(true);
    try {
      const qs = new URLSearchParams();
      if (oppBu) qs.set("bu_target", oppBu);
      if (oppRegion) qs.set("region_code", oppRegion);
      if (oppStatus) qs.set("status", oppStatus);
      setOpportunities(await api<MarketOpportunity[]>(`/api/v1/market-intel/opportunities?${qs.toString()}`));
    } catch (e: any) {
      setOpportunities([]);
      notify(null, e.message);
    } finally {
      setLoadingOpps(false);
    }
  }, [api, oppBu, oppRegion, oppStatus]);

  const loadCampaigns = React.useCallback(async () => {
    try {
      const list = await api<TargetedCampaign[]>("/api/v1/market-intel/campaigns");
      setCampaigns(list);
      if (list.length > 0 && !list.some((c) => c.id === selectedCampaignId)) setSelectedCampaignId(list[0].id);
    } catch (e: any) {
      setCampaigns([]);
      notify(null, e.message);
    }
  }, [api, selectedCampaignId]);

  const loadMe = React.useCallback(async (): Promise<MarketIntelPrincipal | null> => {
    try {
      const data = await api<MarketIntelPrincipal>("/api/v1/market-intel/me");
      setMe(data);
      return data;
    } catch (e: any) {
      setMe(null);
      notify(null, e.message);
      return null;
    }
  }, [api]); // eslint-disable-line react-hooks/exhaustive-deps

  // Perfil real do usuário autenticado define o estado inicial do seletor.
  React.useEffect(() => {
    void (async () => {
      const data = await loadMe();
      if (data) {
        setRole(data.effective_role);
        setRegion(data.region);
      }
    })();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  React.useEffect(() => {
    if (canSimulate) void loadMe();
    if (activeTab === "signals") void loadSignals();
    if (activeTab === "competitors") void loadCompetitors();
    if (activeTab === "opportunities") void loadOpportunities();
    if (activeTab === "campaigns") void loadCampaigns();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab, role, region]);

  React.useEffect(() => {
    if (activeTab === "signals") void loadSignals();
  }, [signalScope, signalSpecialty, signalSource]); // eslint-disable-line react-hooks/exhaustive-deps

  React.useEffect(() => {
    if (activeTab === "opportunities") void loadOpportunities();
  }, [oppBu, oppRegion, oppStatus]); // eslint-disable-line react-hooks/exhaustive-deps

  React.useEffect(() => {
    if (activeTab === "competitors") void loadSnapshots();
  }, [selectedCompetitorId, activeTab, loadSnapshots]);

  const handleRoleChange = (value: string) => {
    if (!canSimulate) return;
    const opt = ROLE_OPTIONS.find((o) => o.role === value) || ROLE_OPTIONS[0];
    setRole(opt.role);
    setRegion(opt.region);
    setSignalScope("");
    setOppRegion("");
    notify(`Perfil simulado: ${opt.label} (${opt.region}).`);
  };

  const handleCreateCompetitor = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingCompetitor(true);
    try {
      const created = await api<{ name: string; next_scheduled_crawl_at: string }>("/api/v1/competitors", {
        method: "POST",
        body: JSON.stringify({
          name: newCompName,
          domain: newCompDomain,
          crawl_frequency_hours: Number(newCompFrequency) || 72,
        }),
      });
      setShowCompetitorModal(false);
      setNewCompName("");
      setNewCompDomain("");
      notify(`${created.name} registrado na fila passiva. Primeira coleta agendada para ${formatDateTime(created.next_scheduled_crawl_at)}.`);
      await loadCompetitors();
    } catch (err: any) {
      notify(null, err.message);
    } finally {
      setSavingCompetitor(false);
    }
  };

  const handleGenerateDraft = async (opp: MarketOpportunity) => {
    setGeneratingFor(opp.id);
    try {
      const draft = await api<TargetedCampaign>("/api/v1/market-intel/campaigns/generate-draft", {
        method: "POST",
        body: JSON.stringify({ opportunity_id: opp.id, channel: draftChannel, target_region: role === "director" ? opp.region_code : region }),
      });
      notify(`Minuta ${draft.id} criada em DRAFT (${draft.channel}) e aprovada no validador CFO 196/2019.`);
      setSelectedCampaignId(draft.id);
      setActiveTab("campaigns");
    } catch (err: any) {
      notify(null, err.message);
    } finally {
      setGeneratingFor(null);
    }
  };

  const [matchingSignalId, setMatchingSignalId] = React.useState<string | null>(null);

  const handleMatchOpportunity = async (signalId: string) => {
    setMatchingSignalId(signalId);
    try {
      const matchRes = await api<any>("/api/v1/market-intel/opportunities/match", {
        method: "POST",
        body: JSON.stringify({
          signal_id: signalId,
          region_code: role === "director" ? undefined : region,
        }),
      });
      notify(`Oportunidade cruzada com sucesso! ${matchRes.matches_count || 1} correspondência(s) encontrada(s) no catálogo.`);
      await loadOpportunities();
      setActiveTab("opportunities");
    } catch (err: any) {
      notify(null, err.message || "Erro ao cruzar sinal com catálogo.");
    } finally {
      setMatchingSignalId(null);
    }
  };

  const handleDispatch = async (campaign: TargetedCampaign) => {
    setDispatchingId(campaign.id);
    try {
      const result = await api<CampaignDispatchResult>(`/api/v1/market-intel/campaigns/${encodeURIComponent(campaign.id)}/dispatch`, {
        method: "POST",
      });
      setLastDispatch(result);
      notify(
        `Campanha executada: ${result.sent_count} enviados, ${result.skipped_cooldown_15d_count} bloqueados pela trava de 15 dias.`
      );
      await loadCampaigns();
    } catch (err: any) {
      notify(null, err.message);
    } finally {
      setDispatchingId(null);
    }
  };

  const selectedCampaign = campaigns.find((c) => c.id === selectedCampaignId) || null;
  const selectedCompetitor = competitors?.items.find((c) => c.id === selectedCompetitorId) || null;

  const tabs = [
    { id: "signals", label: "Sinais de Mercado", icon: <Globe2 className="h-4 w-4" />, count: signals?.total },
    { id: "competitors", label: "Concorrentes", icon: <Radar className="h-4 w-4" />, count: competitors?.items.length },
    { id: "opportunities", label: "Oportunidades x BUs", icon: <Target className="h-4 w-4" />, count: opportunities.length || undefined },
    { id: "campaigns", label: "Disparos & Trava 15d", icon: <Send className="h-4 w-4" />, count: campaigns.length || undefined },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <RouteHeader
        title="Inteligência de Mercado & Radar Tático"
        description="Sinais setoriais, monitoramento passivo de concorrentes e campanhas determinísticas por praça."
        badge={<Badge variant="navy">RBAC Territorial</Badge>}
        actions={[
          {
            id: "refresh",
            label: "Atualizar",
            icon: <RefreshCw className="h-4 w-4" />,
            variant: "outline",
            onClick: () => {
              if (activeTab === "signals") void loadSignals();
              if (activeTab === "competitors") void loadCompetitors();
              if (activeTab === "opportunities") void loadOpportunities();
              if (activeTab === "campaigns") void loadCampaigns();
            },
          },
        ]}
      />

      <Card className="p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 items-end">
          <Select
            label={canSimulate ? "Perfil simulado (Matriz RBAC Seção 5)" : "Seu perfil (Matriz RBAC Seção 5)"}
            value={role}
            disabled={!canSimulate}
            aria-label={canSimulate ? "Perfil simulado" : "Seu perfil (somente a Diretoria simula outros perfis)"}
            onChange={(e) => handleRoleChange(e.target.value)}
            options={ROLE_OPTIONS.map((o) => ({ value: o.role, label: o.label }))}
          />
          <Select
            label="Praça do perfil"
            value={region}
            disabled={!canSimulate || role === "director"}
            onChange={(e) => setRegion(e.target.value)}
            options={Array.from(new Set([...REGION_OPTIONS, region]))
              .filter((r) => role === "director" || r !== "GLOBAL")
              .map((r) => ({ value: r, label: r }))}
          />
          <div className="flex flex-wrap gap-1.5 text-xs">
            <Badge variant={canManageCompetitors ? "success" : "secondary"}>
              {canManageCompetitors ? "Configura concorrentes" : "Concorrentes: leitura"}
            </Badge>
            <Badge variant={canGenerateDraft ? "success" : "secondary"}>
              {canGenerateDraft ? "Gera minuta" : "Sem minuta"}
            </Badge>
            <Badge variant={canDispatch ? "success" : "secondary"}>{canDispatch ? "Aprova disparo" : "Sem disparo"}</Badge>
            {isFieldView && (
              <Badge variant="warning" className="gap-1">
                <Smartphone className="h-3 w-3" /> Visão Mobile de Campo
              </Badge>
            )}
          </div>
        </div>
      </Card>

      {(feedback || error) && (
        <div
          role="status"
          className={
            error
              ? "rounded-lg border border-status-danger bg-status-danger-subtle text-status-danger px-3 py-2 text-sm flex items-center gap-2"
              : "rounded-lg border border-status-success bg-status-success-subtle text-status-success px-3 py-2 text-sm flex items-center gap-2"
          }
        >
          {error ? <ShieldAlert className="h-4 w-4 shrink-0" /> : <CheckCircle2 className="h-4 w-4 shrink-0" />}
          <span>{error || feedback}</span>
        </div>
      )}

      <Tabs tabs={tabs} activeTab={activeTab} onChange={(id) => setActiveTab(id as TabId)} hideOnDesktop />

      {activeTab === "signals" && (
        <div className="space-y-3">
          <Card className="p-4 grid grid-cols-1 md:grid-cols-3 gap-3">
            <Select
              label="Escopo geográfico"
              value={signalScope}
              onChange={(e) => setSignalScope(e.target.value)}
              options={[{ value: "", label: "Todos os escopos visíveis" }, ...REGION_OPTIONS.map((r) => ({ value: r, label: r }))]}
            />
            <Select
              label="Especialidade"
              value={signalSpecialty}
              onChange={(e) => setSignalSpecialty(e.target.value)}
              options={[{ value: "", label: "Todas" }, ...SPECIALTIES.map((s) => ({ value: s, label: s }))]}
            />
            <Select
              label="Tipo de fonte"
              value={signalSource}
              onChange={(e) => setSignalSource(e.target.value)}
              options={[{ value: "", label: "Todas" }, ...Object.entries(SOURCE_TYPE_LABELS).map(([v, l]) => ({ value: v, label: l }))]}
            />
          </Card>
          {loadingSignals ? (
            <Skeleton className="h-40 w-full" />
          ) : !signals || signals.items.length === 0 ? (
            <EmptyState icon={Globe2} title="Nenhum sinal no escopo" description="Ajuste os filtros ou o perfil simulado." />
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
              {signals.items.map((s: MarketSignal) => (
                <Card key={s.id} className="p-4 space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="text-sm font-semibold text-text-main">{s.title}</h3>
                    <Badge variant="outline" className="shrink-0">{s.geographic_scope}</Badge>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    <Badge variant="navy">{SOURCE_TYPE_LABELS[s.source_type] || s.source_type}</Badge>
                    {s.structured_payload.target_specialties.map((sp) => (
                      <Badge key={sp} variant="secondary">{sp}</Badge>
                    ))}
                  </div>
                  <p className="text-xs text-text-secondary line-clamp-3">{s.raw_content}</p>
                  <div className="text-xs space-y-1">
                    <div>
                      <span className="font-semibold text-text-main">Tópicos: </span>
                      <span className="text-text-secondary">{s.structured_payload.topics.join(", ") || "-"}</span>
                    </div>
                    <div>
                      <span className="font-semibold text-text-main">Tendências: </span>
                      <span className="text-text-secondary">{s.structured_payload.detected_trends.join(", ") || "-"}</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between pt-2 border-t border-border">
                    <a
                      href={s.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-xs text-brand-primary hover:underline"
                    >
                      <ExternalLink className="h-3.5 w-3.5" /> Fonte original
                    </a>
                    <Button
                      size="sm"
                      variant="outline"
                      disabled={matchingSignalId === s.id}
                      onClick={() => handleMatchOpportunity(s.id)}
                      className="gap-1"
                    >
                      <Target className="h-3.5 w-3.5" />
                      {matchingSignalId === s.id ? "Cruzando..." : "Cruzar Sinal com Catálogo (Match Vetorial)"}
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === "competitors" && (
        <div className="space-y-3">
          <Card className="p-3 flex flex-wrap items-center gap-3 text-xs bg-brand-navy-subtle border-border">
            <ShieldCheck className="h-4 w-4 text-brand-navy" />
            <span className="font-semibold text-text-main">Fila passiva anti-bloqueio:</span>
            <span className="inline-flex items-center gap-1 text-text-secondary">
              <Clock className="h-3.5 w-3.5" /> Janela Noturna {competitors?.passive_queue.dead_window_utc || "01:00-05:00"} UTC
            </span>
            <span className="inline-flex items-center gap-1 text-text-secondary">
              <Timer className="h-3.5 w-3.5" /> Jitter {competitors?.passive_queue.jitter_seconds_min ?? 7}-{competitors?.passive_queue.jitter_seconds_max ?? 22}s
            </span>
            <span className="inline-flex items-center gap-1 text-text-secondary">
              <Hash className="h-3.5 w-3.5" /> Dedup SHA-256
            </span>
            <span className="text-text-muted">Sem raspagem sob demanda: coletas ocorrem somente no lote agendado do worker.</span>
            <div className="ml-auto">
              <Button size="sm" onClick={() => setShowCompetitorModal(true)} disabled={!canManageCompetitors} className="gap-1.5">
                <Plus className="h-3.5 w-3.5" /> Registrar Concorrente
              </Button>
            </div>
          </Card>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
            <Card className="p-3 space-y-2">
              <h3 className="text-xs font-semibold uppercase text-text-secondary">Concorrentes monitorados</h3>
              {(competitors?.items || []).map((c) => (
                <button
                  key={c.id}
                  type="button"
                  onClick={() => setSelectedCompetitorId(c.id)}
                  className={
                    c.id === selectedCompetitorId
                      ? "w-full text-left rounded-lg border border-brand-primary bg-brand-primary-subtle p-2"
                      : "w-full text-left rounded-lg border border-border hover:bg-surface-bg p-2"
                  }
                >
                  <div className="text-sm font-medium text-text-main">{c.name}</div>
                  <div className="text-xs text-text-secondary">{c.domain}</div>
                  <div className="text-[11px] text-text-muted mt-1">
                    {c.snapshots_count} capturas | próxima coleta {formatDateTime(c.next_scheduled_crawl_at)}
                  </div>
                </button>
              ))}
            </Card>

            <Card className="p-3 space-y-2 lg:col-span-2">
              <h3 className="text-xs font-semibold uppercase text-text-secondary">
                Timeline de capturas {selectedCompetitor ? `- ${selectedCompetitor.name}` : ""}
              </h3>
              {snapshots.length === 0 ? (
                <p className="text-xs text-text-muted">Nenhuma captura registrada ainda.</p>
              ) : (
                snapshots.map((snap) => (
                  <div key={snap.id} className="rounded-lg border border-border p-3 space-y-1.5">
                    <div className="flex flex-wrap items-center gap-2 text-xs">
                      <Badge variant="secondary">{snap.page_type}</Badge>
                      <span className="text-text-secondary">{formatDateTime(snap.created_at)}</span>
                      <span className="font-mono text-text-muted" title={snap.content_hash}>
                        sha256 {snap.content_hash.slice(0, 12)}
                      </span>
                    </div>
                    <div className="text-sm font-medium text-text-main">{snap.extracted_title}</div>
                    {snap.detected_offers.length > 0 && (
                      <ul className="text-xs text-text-secondary space-y-0.5">
                        {snap.detected_offers.map((o, i) => (
                          <li key={`${snap.id}-${i}`}>
                            {o.product}: <span className="font-semibold text-text-main">{formatBrl(o.price)}</span> ({o.discount})
                          </li>
                        ))}
                      </ul>
                    )}
                    <p className="text-xs text-text-secondary">{snap.tactical_summary}</p>
                  </div>
                ))
              )}
            </Card>
          </div>

          <Card className="p-3 space-y-2">
            <h3 className="text-xs font-semibold uppercase text-text-secondary">Contra-ataque B2B (Tactical Insights)</h3>
            <div className="flex flex-wrap gap-1.5">
              {(insights?.value_pillars || []).map((p) => (
                <Badge key={p} variant="success">{p}</Badge>
              ))}
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="text-left text-text-secondary border-b border-border">
                    <th className="py-1.5 pr-2">Concorrente</th>
                    <th className="py-1.5 pr-2">Oferta detectada</th>
                    <th className="py-1.5 pr-2">Nosso SKU</th>
                    <th className="py-1.5 pr-2">Diferença</th>
                    <th className="py-1.5">Ação recomendada</th>
                  </tr>
                </thead>
                <tbody>
                  {(insights?.insights || []).map((ins, idx) => (
                    <tr key={`${ins.snapshot_id}-${idx}`} className="border-b border-border align-top">
                      <td className="py-1.5 pr-2 text-text-main font-medium">{ins.competitor_name}</td>
                      <td className="py-1.5 pr-2 text-text-secondary">
                        {ins.competitor_product} - {formatBrl(ins.competitor_price)} ({ins.competitor_discount})
                      </td>
                      <td className="py-1.5 pr-2 text-text-secondary">
                        {ins.matched_sku ? `${ins.matched_sku} (${formatBrl(ins.our_base_price)})` : "-"}
                      </td>
                      <td className={typeof ins.price_gap_pct === "number" && ins.price_gap_pct > 0 ? "py-1.5 pr-2 text-status-warning" : "py-1.5 pr-2 text-status-success"}>
                        {typeof ins.price_gap_pct !== "number" ? "-" : `${ins.price_gap_pct > 0 ? "+" : ""}${ins.price_gap_pct}%`}
                      </td>
                      <td className="py-1.5 text-text-secondary">{ins.counter_attack}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      )}

      {activeTab === "opportunities" && (
        <div className="space-y-3">
          <Card className="p-4 grid grid-cols-1 md:grid-cols-4 gap-3">
            <Select
              label="Unidade de Negócio"
              value={oppBu}
              onChange={(e) => setOppBu(e.target.value)}
              options={[{ value: "", label: "Todas" }, ...BU_OPTIONS.map((b) => ({ value: b, label: b }))]}
            />
            <Select
              label="Praça"
              value={oppRegion}
              onChange={(e) => setOppRegion(e.target.value)}
              options={[{ value: "", label: "Todas as visíveis" }, ...REGION_OPTIONS.map((r) => ({ value: r, label: r }))]}
            />
            <Select
              label="Status"
              value={oppStatus}
              onChange={(e) => setOppStatus(e.target.value)}
              options={[
                { value: "", label: "Todos" },
                { value: "PENDING", label: "Pendente" },
                { value: "CAMPAIGN_TRIGGERED", label: "Campanha disparada" },
                { value: "DISMISSED", label: "Descartada" },
              ]}
            />
            <Select
              label="Canal da minuta"
              value={draftChannel}
              onChange={(e) => setDraftChannel(e.target.value as "WHATSAPP" | "EMAIL")}
              options={[
                { value: "WHATSAPP", label: "WhatsApp" },
                { value: "EMAIL", label: "E-mail" },
              ]}
            />
          </Card>
          {loadingOpps ? (
            <Skeleton className="h-40 w-full" />
          ) : opportunities.length === 0 ? (
            <EmptyState icon={Target} title="Nenhuma oportunidade" description="Nenhum cruzamento no escopo e filtros atuais." />
          ) : (
            <div className={isFieldView ? "grid grid-cols-1 gap-3" : "grid grid-cols-1 lg:grid-cols-2 gap-3"}>
              {opportunities.map((opp) => (
                <Card key={opp.id} className="p-4 space-y-2">
                  <div className="flex flex-wrap items-center gap-1.5">
                    <Badge variant={opp.opportunity_type === "PRICE_COUNTER_ATTACK" ? "warning" : "navy"}>
                      {OPP_TYPE_LABELS[opp.opportunity_type]}
                    </Badge>
                    <Badge variant="secondary">
                      <Building2 className="h-3 w-3 mr-1" />
                      {opp.bu_target}
                    </Badge>
                    <Badge variant="outline">{opp.region_code}</Badge>
                    <Badge variant={opp.status === "CAMPAIGN_TRIGGERED" ? "success" : "secondary"}>{opp.status}</Badge>
                  </div>
                  {opp.source_title && <div className="text-xs text-text-muted">Origem: {opp.source_title}</div>}
                  <p className="text-sm text-text-main">{opp.suggested_action}</p>
                  {opp.recommended_products.length > 0 && (
                    <div className="space-y-1">
                      <span className="text-xs font-semibold uppercase text-text-secondary">SKUs recomendados</span>
                      {opp.recommended_products.map((p) => (
                        <div key={p.sku} className="flex justify-between text-xs rounded border border-border px-2 py-1">
                          <span className="text-text-main">
                            <span className="font-mono">{p.sku}</span> - {p.name}
                          </span>
                          <span className="text-text-secondary">{formatBrl(p.base_price)}</span>
                        </div>
                      ))}
                    </div>
                  )}
                  <Button
                    size="sm"
                    className="w-full gap-1.5"
                    disabled={!canGenerateDraft || opp.status === "DISMISSED" || generatingFor === opp.id}
                    title={canGenerateDraft ? undefined : "Consultor Externo não gera minutas (RBAC Seção 5)"}
                    onClick={() => handleGenerateDraft(opp)}
                  >
                    <FileText className="h-3.5 w-3.5" />
                    {generatingFor === opp.id ? "Gerando..." : "Gerar Minuta de Campanha Tatica"}
                  </Button>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === "campaigns" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
          <Card className="p-3 space-y-2">
            <h3 className="text-xs font-semibold uppercase text-text-secondary">Campanhas táticas</h3>
            {campaigns.length === 0 ? (
              <p className="text-xs text-text-muted">Nenhuma campanha no escopo.</p>
            ) : (
              campaigns.map((c) => (
                <button
                  key={c.id}
                  type="button"
                  onClick={() => setSelectedCampaignId(c.id)}
                  className={
                    c.id === selectedCampaignId
                      ? "w-full text-left rounded-lg border border-brand-primary bg-brand-primary-subtle p-2"
                      : "w-full text-left rounded-lg border border-border hover:bg-surface-bg p-2"
                  }
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-mono text-xs text-text-main">{c.id}</span>
                    <Badge variant={c.dispatch_status === "EXECUTED" ? "success" : "warning"}>{c.dispatch_status}</Badge>
                  </div>
                  <div className="text-[11px] text-text-secondary mt-1">
                    {c.channel} | {c.target_audience_filter.region} | {c.bu_target}
                  </div>
                </button>
              ))
            )}
          </Card>

          <Card className="p-4 space-y-3 lg:col-span-2">
            {!selectedCampaign ? (
              <EmptyState icon={Send} title="Selecione uma campanha" description="Gere minutas na aba de oportunidades." />
            ) : (
              <>
                <div className="flex flex-wrap items-center gap-2">
                  <h3 className="text-sm font-semibold text-text-main">Minuta {selectedCampaign.id}</h3>
                  <Badge variant="success" className="gap-1">
                    <ShieldCheck className="h-3 w-3" /> CFO 196/2019 validado
                  </Badge>
                  <Badge variant="outline">{selectedCampaign.channel}</Badge>
                </div>
                <div className="text-xs text-text-secondary">
                  Público: praça {selectedCampaign.target_audience_filter.region}
                  {selectedCampaign.target_audience_filter.specialty ? ` | ${selectedCampaign.target_audience_filter.specialty}` : ""}
                  {` | janela de compra ${selectedCampaign.target_audience_filter.purchase_window} dias`}
                </div>
                <textarea
                  readOnly
                  value={selectedCampaign.message_template}
                  className="w-full min-h-[140px] rounded-lg border border-border bg-surface-bg p-3 text-sm text-text-main"
                />
                <div className="grid grid-cols-2 gap-3">
                  <div className="rounded-lg border border-border p-3">
                    <div className="text-xs text-text-secondary flex items-center gap-1">
                      <Send className="h-3.5 w-3.5" /> Enviados
                    </div>
                    <div className="text-2xl font-bold text-status-success">
                      {lastDispatch?.campaign_id === selectedCampaign.id ? lastDispatch.sent_count : selectedCampaign.sent_count}
                    </div>
                  </div>
                  <div className="rounded-lg border border-border p-3">
                    <div className="text-xs text-text-secondary flex items-center gap-1">
                      <Lock className="h-3.5 w-3.5" /> Bloqueados pela Trava de 15 Dias
                    </div>
                    <div className="text-2xl font-bold text-status-warning">
                      {lastDispatch?.campaign_id === selectedCampaign.id
                        ? lastDispatch.skipped_cooldown_15d_count
                        : selectedCampaign.skipped_cooldown_15d_count}
                    </div>
                  </div>
                </div>
                {selectedCampaign.executed_at && (
                  <div className="text-xs text-text-muted">
                    Executada em {formatDateTime(selectedCampaign.executed_at)} | aprovada por {selectedCampaign.approved_by_user_id || "-"}
                  </div>
                )}
                <Button
                  className="w-full gap-1.5"
                  disabled={!canDispatch || selectedCampaign.dispatch_status === "EXECUTED" || dispatchingId === selectedCampaign.id}
                  title={canDispatch ? undefined : "Somente Diretoria e Gerente Regional aprovam disparos"}
                  onClick={() => handleDispatch(selectedCampaign)}
                >
                  <Send className="h-4 w-4" />
                  {dispatchingId === selectedCampaign.id ? "Disparando..." : "Aprovar & Disparar Campanha (Trava 15d)"}
                </Button>
              </>
            )}
          </Card>
        </div>
      )}

      <Dialog
        isOpen={showCompetitorModal}
        onClose={() => setShowCompetitorModal(false)}
        size="form"
        title="Registrar concorrente na fila passiva"
        description="O domínio entra no lote noturno (01:00-05:00 UTC). Nenhuma coleta é executada agora."
      >
        <form onSubmit={handleCreateCompetitor} className="space-y-3">
          <div>
            <label className="block text-xs font-medium text-text-secondary mb-1">Nome</label>
            <Input required minLength={2} value={newCompName} onChange={(e) => setNewCompName(e.target.value)} />
          </div>
          <div>
            <label className="block text-xs font-medium text-text-secondary mb-1">Domínio público</label>
            <Input required placeholder="concorrente.com.br" value={newCompDomain} onChange={(e) => setNewCompDomain(e.target.value)} />
          </div>
          <Select
            label="Frequência de coleta"
            value={newCompFrequency}
            onChange={(e) => setNewCompFrequency(e.target.value)}
            options={[
              { value: "24", label: "A cada 24 horas" },
              { value: "72", label: "A cada 72 horas" },
              { value: "168", label: "Semanal" },
            ]}
          />
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" size="sm" onClick={() => setShowCompetitorModal(false)}>
              Cancelar
            </Button>
            <Button type="submit" size="sm" disabled={savingCompetitor}>
              {savingCompetitor ? "Registrando..." : "Registrar"}
            </Button>
          </div>
        </form>
      </Dialog>
    </div>
  );
};

export default MarketIntelRadarWorkspace;
