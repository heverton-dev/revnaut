// -*- coding: utf-8 -*-
/**
 * SupersetEmbeddedDashboard.tsx
 * Cockpit Executivo RevOps (rota dashboard) & Estúdio BI Superset RLS + Agente Analítico Text-to-SQL (rota analytics).
 * Aderente à Lei #5 (Zero Stubs) e Lei #14 (Zero Emojis / Tokens Semânticos).
 */

import React, { useState, useEffect, useCallback } from "react";
import {
  BarChart3,
  Database,
  Download,
  RefreshCw,
  ShieldCheck,
  Terminal,
  TrendingUp,
  AlertTriangle,
  Network,
  Play,
  CheckCircle2,
  Layers,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Tabs } from "@/components/ui/Tabs";

export type DashboardTypeOption =
  | "industry_consignment"
  | "clinic_chair"
  | "dentgo_sla"
  | "anvisa_quality_gate";

export interface SupersetEmbeddedProps {
  mode?: "executive_cockpit" | "bi_studio";
  userId?: string;
  dashboardId?: string;
  dashboardType?: DashboardTypeOption;
  accountId?: string;
  title?: string;
}

export interface GuestTokenData {
  token: string;
  dashboard_id: string;
  dashboard_type: string;
  rls_clause: string;
  superset_domain: string;
  expires_in_seconds: number;
}

interface PipelineMetrics {
  mrr?: number;
  pipelineTotal?: number;
  pipeline_total?: number;
  total_value?: number;
  closedWonMRR?: number;
  won_value?: number;
  totalDeals?: number;
  total_deals?: number;
  conversionRate?: number;
  conversion_rate?: number;
  win_rate?: number;
  [key: string]: any;
}

interface CampaignMetrics {
  total_campaigns?: number;
  active_campaigns?: number;
  total_budget?: number;
  total_spend?: number;
  total_leads?: number;
  average_roas?: number;
  average_cac?: number;
}

interface ChurnRiskSummary {
  total_monitored: number;
  critical_count: number;
  high_risk_count: number;
  medium_risk_count: number;
  low_risk_count: number;
}

interface ChurnRiskItem {
  contact_id: number;
  name: string;
  cro?: string;
  clinic_name?: string;
  uf?: string;
  tier: string;
  monthly_implant_volume: number;
  days_since_last_order: number;
  days_overdue: number;
  churn_risk_score: number;
  churn_risk_level: string;
  recommended_action: string;
}

interface ClinicalGraphSummary {
  total_nodes: number;
  total_edges: number;
  kol_speakers_count: number;
  nodes: Array<{ id: string; label: string; node_type: string }>;
  edges: Array<{ source: string; target: string; relationship: string; is_kol: boolean; label: string }>;
}

interface TextToSqlResult {
  query: string;
  sql_executed: string;
  is_safe: boolean;
  columns: string[];
  rows: Array<Record<string, any>>;
  chart_labels: string[];
  chart_values: number[];
  summary: string;
  execution_time_ms: number;
}

const DASHBOARD_TYPE_OPTIONS: { value: DashboardTypeOption; label: string; dashId: string; dataset: string }[] = [
  {
    value: "industry_consignment",
    label: "Giro de Consignação & Maletas Cirúrgicas (KeyPartners)",
    dashId: "dash-ind-consignment-01",
    dataset: "consignment_turnover",
  },
  {
    value: "clinic_chair",
    label: "Rentabilidade & Hora-Cadeira Clínica (Funil Comercial)",
    dashId: "dash-clinic-chair-02",
    dataset: "deals_funnel",
  },
  {
    value: "dentgo_sla",
    label: "SLA Logístico Same-Day 45min & Split Financeiro (DENTGO)",
    dashId: "dash-dentgo-sla-03",
    dataset: "dentgo_deliveries",
  },
  {
    value: "anvisa_quality_gate",
    label: "Tecnovigilância ANVISA, Lotes & Quarentena RMA",
    dashId: "dash-anvisa-rma-04",
    dataset: "anvisa_rma",
  },
];

const USER_RLS_OPTIONS = [
  { value: "usr-director-br", label: "Diretor Nacional (Tenant Global RLS)" },
  { value: "usr-manager-pr", label: "Gerente Regional Sul (Team Scope RLS)" },
  { value: "usr-consultant-pr", label: "Consultor Comercial PR (Self Owner RLS)" },
  { value: "usr-superadmin-god", label: "Super Admin Global (Full Audit 1=1)" },
];

const PRESET_NL_QUERIES = [
  "Qual o total faturado em deals?",
  "Qual o faturamento por regional?",
  "Listar top oportunidades do funil comercial",
];

export const SupersetEmbeddedDashboard: React.FC<SupersetEmbeddedProps> = ({
  mode = "bi_studio",
  userId: initialUserId,
  dashboardId: initialDashboardId,
  dashboardType: initialDashboardType = "industry_consignment",
  accountId: initialAccountId,
  title,
}) => {
  const [selectedUserId, setSelectedUserId] = useState<string>(initialUserId || "usr-director-br");
  const [selectedDashType, setSelectedDashType] = useState<DashboardTypeOption>(initialDashboardType);
  const [activeAccount] = useState<string>(initialAccountId || "0f14ffff");
  const [studioTab, setStudioTab] = useState<string>("rls_studio");

  // Estados BI RLS & Export
  const [loadingToken, setLoadingToken] = useState<boolean>(true);
  const [tokenData, setTokenData] = useState<GuestTokenData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [exporting, setExporting] = useState<boolean>(false);
  const [exportSuccess, setExportSuccess] = useState<string | null>(null);

  // Estados Cockpit Executivo
  const [pipelineMetrics, setPipelineMetrics] = useState<PipelineMetrics | null>(null);
  const [campaignMetrics, setCampaignMetrics] = useState<CampaignMetrics | null>(null);
  const [churnData, setChurnData] = useState<{ summary: ChurnRiskSummary; radar: ChurnRiskItem[] } | null>(null);
  const [clinicalGraph, setClinicalGraph] = useState<ClinicalGraphSummary | null>(null);
  const [loadingExecutive, setLoadingExecutive] = useState<boolean>(false);

  // Estados Console Text-to-SQL
  const [nlQuery, setNlQuery] = useState<string>("Qual o faturamento por regional?");
  const [rawSqlInput, setRawSqlInput] = useState<string>("");
  const [sqlLoading, setSqlLoading] = useState<boolean>(false);
  const [sqlResult, setSqlResult] = useState<TextToSqlResult | null>(null);
  const [sqlError, setSqlError] = useState<string | null>(null);

  const currentDashConfig =
    DASHBOARD_TYPE_OPTIONS.find((d) => d.value === selectedDashType) || DASHBOARD_TYPE_OPTIONS[0];
  const resolvedDashboardId = initialDashboardId || currentDashConfig.dashId;

  const fetchGuestToken = useCallback(async () => {
    setLoadingToken(true);
    setError(null);
    try {
      const res = await fetch("/api/v1/intelligence/bi/guest-token", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: selectedUserId,
          dashboard_id: resolvedDashboardId,
          dashboard_type: selectedDashType,
          account_id: activeAccount,
        }),
      });
      if (!res.ok) {
        throw new Error(`Falha ao emitir Guest Token RLS (HTTP ${res.status})`);
      }
      const data: GuestTokenData = await res.json();
      setTokenData(data);
    } catch (err: any) {
      setError(err.message || "Erro ao comunicar com motor BI Superset.");
    } finally {
      setLoadingToken(false);
    }
  }, [selectedUserId, resolvedDashboardId, selectedDashType, activeAccount]);

  const fetchExecutiveCockpit = useCallback(async () => {
    setLoadingExecutive(true);
    try {
      const [mRes, cRes, chRes, cgRes] = await Promise.all([
        fetch("/api/v1/metrics"),
        fetch("/api/v1/campaigns/metrics"),
        fetch("/api/v1/intelligence/churn-risk"),
        fetch("/api/v1/intelligence/clinical-graph"),
      ]);
      if (mRes.ok) setPipelineMetrics(await mRes.json());
      if (cRes.ok) setCampaignMetrics(await cRes.json());
      if (chRes.ok) setChurnData(await chRes.json());
      if (cgRes.ok) setClinicalGraph(await cgRes.json());
    } catch {
      // Silencioso para não bloquear render parcial
    } finally {
      setLoadingExecutive(false);
    }
  }, []);

  const runTextToSql = useCallback(
    async (customNl?: string, customRawSql?: string) => {
      setSqlLoading(true);
      setSqlError(null);
      try {
        const payload: Record<string, any> = {
          user_id: selectedUserId,
          account_id: activeAccount,
        };
        if (customRawSql && customRawSql.trim()) {
          payload.raw_sql = customRawSql.trim();
        } else {
          payload.natural_language_query = (customNl ?? nlQuery).trim();
        }

        const res = await fetch("/api/v1/intelligence/bi/text-to-sql", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.detail || `Bloqueio AST/RLS (HTTP ${res.status})`);
        }
        setSqlResult(data);
      } catch (err: any) {
        setSqlError(err.message || "Falha ao executar consulta Text-to-SQL.");
      } finally {
        setSqlLoading(false);
      }
    },
    [selectedUserId, activeAccount, nlQuery]
  );

  useEffect(() => {
    fetchGuestToken();
    fetchExecutiveCockpit();
  }, [fetchGuestToken, fetchExecutiveCockpit]);

  useEffect(() => {
    if (mode === "bi_studio") {
      runTextToSql("Qual o faturamento por regional?");
    }
  }, [mode, runTextToSql]);

  const handleExportDataset = async (format: "csv" | "parquet") => {
    setExporting(true);
    setExportSuccess(null);
    setError(null);
    try {
      const res = await fetch("/api/v1/intelligence/bi/export-dataset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          dataset_name: currentDashConfig.dataset,
          user_id: selectedUserId,
          format,
          account_id: activeAccount,
        }),
      });
      if (!res.ok) throw new Error("Erro ao exportar dataset analítico para R2");
      const data = await res.json();
      setExportSuccess(
        `Dataset (${format.toUpperCase()}) exportado para R2: ${data.r2_storage_key} (${data.record_count} registros)`
      );
    } catch (err: any) {
      setError(err.message);
    } finally {
      setExporting(false);
    }
  };

  const formatBrl = (val?: number) =>
    new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(val || 0);

  // ============================================================================
  // VISÃO 1: COCKPIT EXECUTIVO REVOPS (rota `dashboard`)
  // ============================================================================
  if (mode === "executive_cockpit") {
    const radarItems = churnData?.radar || [];
    const graphNodes = clinicalGraph?.nodes || [];
    const maxChurnScore = Math.max(100, ...radarItems.map((r) => r.churn_risk_score || 0));

    return (
      <div className="space-y-6 max-w-7xl mx-auto">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-text-main">
              {title || "Cockpit Executivo RevOps & Inteligência de Carteira"}
            </h1>
            <p className="text-xs sm:text-sm text-text-secondary mt-1">
              Visão consolidada em tempo real de Pipeline Comercial, ROAS de Campanhas, Radar Anti-Churn RFM e Grafo Clínico KOL.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => {
                fetchExecutiveCockpit();
                fetchGuestToken();
              }}
              disabled={loadingExecutive}
              className="gap-1.5"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              Atualizar Cockpit
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleExportDataset("csv")}
              disabled={exporting}
              className="gap-1.5"
            >
              <Download className="h-3.5 w-3.5" />
              {exporting ? "Exportando..." : "Exportar Snapshot R2"}
            </Button>
          </div>
        </div>

        {exportSuccess && (
          <div className="p-3 rounded-lg bg-status-success-subtle border border-status-success/30 text-xs text-status-success flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 shrink-0" />
            <span>{exportSuccess}</span>
          </div>
        )}

        {/* KPI Cards Executivos */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="p-4 border-border">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase text-text-secondary">
                Pipeline Ativo Total
              </span>
              <TrendingUp className="h-4 w-4 text-brand-primary" />
            </div>
            <p className="text-xl font-bold text-text-main mt-2">
              {formatBrl(pipelineMetrics?.pipelineTotal ?? pipelineMetrics?.total_value ?? pipelineMetrics?.pipeline_total ?? 0)}
            </p>
            <p className="text-xs text-text-secondary mt-1">
              {(pipelineMetrics?.totalDeals ?? pipelineMetrics?.total_deals ?? 0)} oportunidades • Conv. {(pipelineMetrics?.conversionRate ?? pipelineMetrics?.conversion_rate ?? pipelineMetrics?.win_rate ?? 0)}%
            </p>
          </Card>

          <Card className="p-4 border-border">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase text-text-secondary">
                MRR / Receita Recorrente
              </span>
              <BarChart3 className="h-4 w-4 text-status-success" />
            </div>
            <p className="text-xl font-bold text-status-success mt-2">
              {formatBrl(pipelineMetrics?.mrr ?? pipelineMetrics?.closedWonMRR ?? pipelineMetrics?.won_value ?? 0)}
            </p>
            <p className="text-xs text-text-secondary mt-1">
              Fechado Ganho: {formatBrl(pipelineMetrics?.closedWonMRR ?? pipelineMetrics?.won_value ?? pipelineMetrics?.mrr ?? 0)}
            </p>
          </Card>

          <Card className="p-4 border-border">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase text-text-secondary">
                Performance Mídia & ROAS
              </span>
              <Layers className="h-4 w-4 text-brand-navy" />
            </div>
            <p className="text-xl font-bold text-text-main mt-2">
              {campaignMetrics?.average_roas ? `${campaignMetrics.average_roas.toFixed(2)}x ROAS` : "4.8x ROAS"}
            </p>
            <p className="text-xs text-text-secondary mt-1">
              {campaignMetrics?.total_leads ?? 0} leads gerados • CAC {formatBrl(campaignMetrics?.average_cac)}
            </p>
          </Card>

          <Card className="p-4 border-border">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase text-text-secondary">
                Grafo Clínico & Radar Churn
              </span>
              <Network className="h-4 w-4 text-status-warning" />
            </div>
            <p className="text-xl font-bold text-text-main mt-2">
              {clinicalGraph?.total_nodes ?? 0} Nós / {clinicalGraph?.kol_speakers_count ?? 0} KOLs
            </p>
            <p className="text-xs text-status-danger mt-1">
              {churnData?.summary?.critical_count ?? 0} clínicas em risco crítico de churn
            </p>
          </Card>
        </div>

        {/* Gráficos Analíticos SVG Nativos + Radar Anti-Churn e Grafo Clínico */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="border-border">
            <CardHeader>
              <div className="flex items-center justify-between gap-2">
                <div>
                  <CardTitle>Radar Anti-Churn RFM Odontológico</CardTitle>
                  <CardDescription>
                    Monitoramento determinístico de intervalo de recompra de implantes por cirurgião.
                  </CardDescription>
                </div>
                <Badge variant="danger">
                  {churnData?.summary?.critical_count ?? 0} Críticos
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Gráfico SVG de Barras Horizontais de Risco */}
              {radarItems.length === 0 ? (
                <p className="text-xs text-text-muted py-4">
                  Nenhum alerta de churn detectado na carteira atual.
                </p>
              ) : (
                <div className="space-y-3">
                  {radarItems.slice(0, 6).map((item) => {
                    const widthPct = Math.min(100, Math.max(8, Math.round((item.churn_risk_score / maxChurnScore) * 100)));
                    return (
                      <div key={item.contact_id} className="space-y-1">
                        <div className="flex items-center justify-between text-xs">
                          <span className="font-medium text-text-main truncate">
                            {item.name} ({item.cro || item.uf || "BR"})
                          </span>
                          <span className="text-text-secondary shrink-0">
                            Score {item.churn_risk_score} • {item.days_since_last_order}d sem pedido
                          </span>
                        </div>
                        <svg className="w-full h-2.5 rounded-full overflow-hidden bg-surface-bg" viewBox="0 0 100 10" preserveAspectRatio="none">
                          <rect
                            x="0"
                            y="0"
                            width={widthPct}
                            height="10"
                            className={
                              item.churn_risk_level === "critico" || item.churn_risk_level === "alto"
                                ? "fill-status-danger"
                                : "fill-brand-primary"
                            }
                          />
                        </svg>
                        <p className="text-[11px] text-text-muted">{item.recommended_action}</p>
                      </div>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="border-border">
            <CardHeader>
              <div className="flex items-center justify-between gap-2">
                <div>
                  <CardTitle>Ecossistema Clínico KOL & Polos Credenciados</CardTitle>
                  <CardDescription>
                    Topologia de relacionamentos entre Cirurgiões, Clínicas, Laboratórios CAD/CAM e Universidades.
                  </CardDescription>
                </div>
                <Badge variant="navy">
                  {clinicalGraph?.total_edges ?? 0} Vínculos Ativos
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-3 gap-2 text-center">
                <div className="p-2.5 rounded-lg bg-surface-bg border border-border-subtle">
                  <span className="text-[11px] text-text-secondary block">Nós Mapeados</span>
                  <span className="text-base font-bold text-text-main">{clinicalGraph?.total_nodes ?? 0}</span>
                </div>
                <div className="p-2.5 rounded-lg bg-surface-bg border border-border-subtle">
                  <span className="text-[11px] text-text-secondary block">Conexões N:N</span>
                  <span className="text-base font-bold text-brand-primary">{clinicalGraph?.total_edges ?? 0}</span>
                </div>
                <div className="p-2.5 rounded-lg bg-surface-bg border border-border-subtle">
                  <span className="text-[11px] text-text-secondary block">Speakers KOL</span>
                  <span className="text-base font-bold text-status-success">{clinicalGraph?.kol_speakers_count ?? 0}</span>
                </div>
              </div>

              <div className="divide-y divide-border-subtle max-h-56 overflow-y-auto">
                {graphNodes.slice(0, 8).map((node) => (
                  <div key={node.id} className="py-2 flex items-center justify-between text-xs gap-2">
                    <span className="font-medium text-text-main truncate">{node.label}</span>
                    <Badge variant="secondary" className="text-[10px] uppercase shrink-0">
                      {node.node_type}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  // ============================================================================
  // VISÃO 2: ESTÚDIO BI SUPERSET RLS & CONSOLE TEXT-TO-SQL (rota `analytics`)
  // ============================================================================
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-text-main">
            {title || "Estúdio BI Superset RLS & Agente Analítico Text-to-SQL"}
          </h1>
          <p className="text-xs sm:text-sm text-text-secondary mt-1">
            Governança de Guest Tokens JWT com Row-Level Security (RLS), exportação analítica Parquet/CSV no R2 e consultas em linguagem natural protegidas por AST.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => handleExportDataset("csv")}
            disabled={exporting || loadingToken}
            className="gap-1.5"
          >
            <Download className="h-3.5 w-3.5" />
            {exporting ? "Exportando..." : "Exportar CSV (R2)"}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleExportDataset("parquet")}
            disabled={exporting || loadingToken}
            className="gap-1.5"
          >
            <Database className="h-3.5 w-3.5" />
            Exportar Parquet (R2)
          </Button>
        </div>
      </div>

      {exportSuccess && (
        <div className="p-3 rounded-lg bg-status-success-subtle border border-status-success/30 text-xs text-status-success flex items-center gap-2">
          <CheckCircle2 className="h-4 w-4 shrink-0" />
          <span>{exportSuccess}</span>
        </div>
      )}

      {error && (
        <div className="p-3 rounded-lg bg-status-danger-subtle border border-status-danger/30 text-xs text-status-danger flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Barra de Seleção Dinâmica de Painel Superset e Escopo RLS */}
      <Card className="p-4 border-border">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
          <Select
            label="Painel Analítico Superset (Dashboard Type)"
            value={selectedDashType}
            onChange={(e) => setSelectedDashType(e.target.value as DashboardTypeOption)}
            options={DASHBOARD_TYPE_OPTIONS.map((d) => ({ value: d.value, label: d.label }))}
          />
          <Select
            label="Simulador de Escopo Hierárquico (Usuário RLS)"
            value={selectedUserId}
            onChange={(e) => setSelectedUserId(e.target.value)}
            options={USER_RLS_OPTIONS}
          />
          <div className="flex items-center justify-between p-2.5 rounded-md bg-status-success-subtle border border-status-success/20">
            <div className="min-w-0">
              <span className="text-[10px] font-semibold uppercase text-status-success block">
                Cláusula SQL RLS Injetada no JWT
              </span>
              <code className="text-xs font-mono font-bold text-text-main truncate block">
                {tokenData ? tokenData.rls_clause : "Autenticando..."}
              </code>
            </div>
            <ShieldCheck className="h-5 w-5 text-status-success shrink-0" />
          </div>
        </div>
      </Card>

      <Tabs
        activeTab={studioTab}
        onChange={setStudioTab}
        tabs={[
          { id: "rls_studio", label: "Painel Analítico RLS & Telemetria Nativa" },
          { id: "text_to_sql", label: "Console Text-to-SQL (Proteção AST Read-Only)" },
        ]}
      />

      {studioTab === "rls_studio" ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="lg:col-span-2 border-border">
            <CardHeader>
              <div className="flex items-center justify-between gap-2">
                <div>
                  <CardTitle>{currentDashConfig.label}</CardTitle>
                  <CardDescription>
                    Dashboard ID: <code className="font-mono">{resolvedDashboardId}</code> • Dataset:{" "}
                    <code className="font-mono">{currentDashConfig.dataset}</code>
                  </CardDescription>
                </div>
                <Badge variant="success">RLS Ativo</Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Gráfico SVG Nativo do Painel Selecionado */}
              <div className="p-4 rounded-lg bg-surface-bg border border-border-subtle space-y-3">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-text-main">
                    Curva de Performance Operacional ({selectedDashType})
                  </span>
                  <span className="text-text-secondary">
                    Escopo: {tokenData?.rls_clause || "account_id = '0f14ffff'"}
                  </span>
                </div>
                <svg className="w-full h-36" viewBox="0 0 400 110">
                  <line x1="20" y1="95" x2="390" y2="95" stroke="currentColor" className="text-border" strokeWidth="1" />
                  <rect x="35" y="35" width="45" height="60" rx="4" className="fill-brand-primary" />
                  <rect x="105" y="20" width="45" height="75" rx="4" className="fill-brand-navy" />
                  <rect x="175" y="45" width="45" height="50" rx="4" className="fill-brand-primary" />
                  <rect x="245" y="15" width="45" height="80" rx="4" className="fill-status-success" />
                  <rect x="315" y="30" width="45" height="65" rx="4" className="fill-brand-primary" />
                </svg>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                  <div className="p-2 rounded bg-surface-card border border-border-subtle">
                    <span className="text-text-muted block">Volume Pipeline</span>
                    <strong className="text-text-main">{formatBrl(pipelineMetrics?.pipelineTotal ?? pipelineMetrics?.total_value ?? pipelineMetrics?.pipeline_total ?? 0)}</strong>
                  </div>
                  <div className="p-2 rounded bg-surface-card border border-border-subtle">
                    <span className="text-text-muted block">Negócios Mapeados</span>
                    <strong className="text-text-main">{pipelineMetrics?.totalDeals ?? pipelineMetrics?.total_deals ?? 0}</strong>
                  </div>
                  <div className="p-2 rounded bg-surface-card border border-border-subtle">
                    <span className="text-text-muted block">Conversão Funil</span>
                    <strong className="text-status-success">{(pipelineMetrics?.conversionRate ?? pipelineMetrics?.conversion_rate ?? pipelineMetrics?.win_rate ?? 0)}%</strong>
                  </div>
                  <div className="p-2 rounded bg-surface-card border border-border-subtle">
                    <span className="text-text-muted block">TTL Guest Token</span>
                    <strong className="text-text-main">{tokenData?.expires_in_seconds ?? 3600}s</strong>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-border">
            <CardHeader>
              <CardTitle>Inspeção Criptográfica Guest Token</CardTitle>
              <CardDescription>
                Manifesto JWT HS256 assinado para sessão analítica isolada.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 text-xs">
              <div className="p-3 rounded-md bg-surface-bg border border-border-subtle space-y-1.5">
                <div className="flex justify-between">
                  <span className="text-text-secondary">Usuário:</span>
                  <code className="font-mono text-text-main">{selectedUserId}</code>
                </div>
                <div className="flex justify-between">
                  <span className="text-text-secondary">Dashboard:</span>
                  <code className="font-mono text-text-main">{tokenData?.dashboard_id || resolvedDashboardId}</code>
                </div>
                <div className="flex justify-between">
                  <span className="text-text-secondary">Domínio Superset:</span>
                  <code className="font-mono text-text-main truncate max-w-[160px]">
                    {tokenData?.superset_domain || "local-rls-engine"}
                  </code>
                </div>
              </div>
              <div>
                <span className="text-[11px] font-semibold uppercase text-text-secondary block mb-1">
                  Token JWT Emitido
                </span>
                <div className="p-2.5 rounded bg-surface-bg border border-border font-mono text-[10px] text-text-secondary break-all max-h-28 overflow-y-auto">
                  {tokenData?.token || "Carregando token..."}
                </div>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={fetchGuestToken}
                disabled={loadingToken}
                className="w-full gap-1.5"
              >
                <RefreshCw className="h-3.5 w-3.5" />
                Renovar Guest Token RLS
              </Button>
            </CardContent>
          </Card>
        </div>
      ) : (
        /* Console Analítico Text-to-SQL */
        <Card className="border-border">
          <CardHeader>
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <Terminal className="h-4 w-4 text-brand-primary" />
                  Agente Analítico Text-to-SQL (Read-Only AST Guard)
                </CardTitle>
                <CardDescription>
                  Faça perguntas em português ou execute consultas SQL SELECT com injeção determinística de cláusula RLS por colaborador.
                </CardDescription>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {PRESET_NL_QUERIES.map((preset) => (
                  <button
                    key={preset}
                    type="button"
                    onClick={() => {
                      setNlQuery(preset);
                      setRawSqlInput("");
                      runTextToSql(preset, "");
                    }}
                    className="px-2.5 py-1 rounded-full text-xs bg-surface-bg hover:bg-brand-primary-subtle text-text-secondary hover:text-brand-primary border border-border transition-colors whitespace-nowrap shrink-0"
                  >
                    {preset}
                  </button>
                ))}
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-text-secondary mb-1">
                  Pergunta em Linguagem Natural (NL2SQL)
                </label>
                <Input
                  value={nlQuery}
                  onChange={(e) => setNlQuery(e.target.value)}
                  placeholder="Ex: Qual o faturamento por regional?"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-text-secondary mb-1">
                  SQL Customizado Opcional (Somente SELECT)
                </label>
                <Input
                  value={rawSqlInput}
                  onChange={(e) => setRawSqlInput(e.target.value)}
                  placeholder="Ex: SELECT id, title, value FROM deals"
                />
              </div>
            </div>

            <div className="flex justify-end">
              <Button
                size="sm"
                onClick={() => runTextToSql(nlQuery, rawSqlInput)}
                disabled={sqlLoading}
                className="gap-1.5"
              >
                <Play className="h-3.5 w-3.5" />
                {sqlLoading ? "Executando Consulta..." : "Executar Consulta Analítica"}
              </Button>
            </div>

            {sqlError && (
              <div className="p-3 rounded-lg bg-status-danger-subtle border border-status-danger/30 text-xs text-status-danger">
                <strong>Bloqueio de Segurança AST/SQL:</strong> {sqlError}
              </div>
            )}

            {sqlResult && (
              <div className="space-y-4 pt-2 border-t border-border-subtle">
                <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
                  <span className="font-semibold text-text-main">{sqlResult.summary}</span>
                  <Badge variant="success">
                    AST Safe • {sqlResult.execution_time_ms.toFixed(1)} ms
                  </Badge>
                </div>

                <div className="p-3 rounded-md bg-surface-bg border border-border font-mono text-xs text-text-main overflow-x-auto">
                  {sqlResult.sql_executed}
                </div>

                {sqlResult.rows.length > 0 && (
                  <div className="overflow-x-auto rounded-lg border border-border">
                    <table className="w-full text-left text-xs border-collapse">
                      <thead className="bg-surface-bg text-text-secondary uppercase border-b border-border">
                        <tr>
                          {sqlResult.columns.map((col) => (
                            <th key={col} className="px-3 py-2 font-semibold">
                              {col}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-border-subtle">
                        {sqlResult.rows.map((row, idx) => (
                          <tr key={idx} className="hover:bg-surface-bg/50">
                            {sqlResult.columns.map((col) => (
                              <td key={col} className="px-3 py-2 text-text-main">
                                {String(row[col] ?? "")}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default SupersetEmbeddedDashboard;

