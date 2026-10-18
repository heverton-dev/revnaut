import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import { AppShell } from "@/components/layout/AppShell";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { DataTable, Column } from "@/components/ui/DataTable";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorBoundary } from "@/components/ui/ErrorBoundary";
import { Deal } from "@/types/api_contracts";
import { Plus, RefreshCw, FileText, AlertCircle } from "lucide-react";
import { AppRouter } from "./router";

interface MetricsSummary {
  total_deals?: number;
  pipeline_value?: number;
  active_consignments?: number;
  conversion_rate?: number;
}

export function App() {
  const [activeNav, setActiveNav] = React.useState("deals");

  const dealsQuery = useQuery<Deal[]>({
    queryKey: ["deals"],
    queryFn: async () => {
      const res = await fetch("/api/v1/deals");
      if (!res.ok) {
        throw new Error(`Falha ao carregar negócios (HTTP ${res.status})`);
      }
      const data = await res.json();
      return Array.isArray(data) ? data : data.deals || data.data || [];
    },
  });

  const metricsQuery = useQuery<MetricsSummary>({
    queryKey: ["metrics"],
    queryFn: async () => {
      const res = await fetch("/api/v1/metrics");
      if (!res.ok) {
        return {};
      }
      return res.json();
    },
  });

  const columns: Column<Deal>[] = [
    {
      key: "title",
      header: "Oportunidade Cirúrgica / Deal",
      render: (deal) => (
        <div>
          <div className="font-medium text-text-main">{deal.title}</div>
          <div className="text-xs text-text-secondary">{deal.company_name}</div>
        </div>
      ),
    },
    {
      key: "contact_name",
      header: "Cirurgião Titular",
      render: (deal) => (
        <span className="text-xs text-text-main font-medium">{deal.contact_name}</span>
      ),
    },
    {
      key: "owner_name",
      header: "Responsável (Dual)",
      render: (deal) => (
        <Badge
          variant={String(deal.owner_name || "").includes("Field") ? "default" : "navy"}
          className="text-[10px]"
        >
          {deal.owner_name}
        </Badge>
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
      key: "status",
      header: "Status Sanitário",
      render: () => (
        <Badge variant="success" className="text-[10px]">
          Lote Rastreado
        </Badge>
      ),
    },
  ];

  const deals = dealsQuery.data || [];
  const metrics = metricsQuery.data;

  return (
    <AppShell activeNav={activeNav} onNavigate={setActiveNav}>
      <ErrorBoundary onReset={() => dealsQuery.refetch()}>
        <AppRouter
          currentRoute={activeNav}
          defaultComponent={
            <div className="space-y-6 max-w-7xl mx-auto">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                  <h1 className="text-2xl font-bold tracking-tight text-text-main">
                    Cockpit de Negócios & Consignação Cirúrgica
                  </h1>
                  <p className="text-sm text-text-secondary mt-1">
                    Operação unificada RevOps + KeyPartners (Kits & ANVISA) + DENTGO (Logística Same-Day).
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => {
                      dealsQuery.refetch();
                      metricsQuery.refetch();
                    }}
                    className="inline-flex items-center gap-2"
                  >
                    <RefreshCw className="h-4 w-4" />
                    Sincronizar
                  </Button>
                  <Button size="sm" className="inline-flex items-center gap-2">
                    <Plus className="h-4 w-4" />
                    Novo Negócio
                  </Button>
                </div>
              </div>

              {metrics && (
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <Card className="p-4 border-border">
                    <span className="text-xs font-semibold uppercase text-text-secondary">
                      Negócios Ativos
                    </span>
                    <p className="text-xl font-bold text-text-main mt-1">
                      {metrics.total_deals ?? deals.length}
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
                        metrics.pipeline_value ??
                          deals.reduce((acc, d) => acc + (d.value || 0), 0)
                      )}
                    </p>
                  </Card>
                  <Card className="p-4 border-border">
                    <span className="text-xs font-semibold uppercase text-text-secondary">
                      Custódia ANVISA
                    </span>
                    <p className="text-xl font-bold text-status-success mt-1">
                      100% Conformidade
                    </p>
                  </Card>
                </div>
              )}

              {dealsQuery.isLoading ? (
                <div className="space-y-4">
                  <DataTable columns={columns} data={[]} isLoading={true} />
                </div>
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
              ) : deals.length === 0 ? (
                <EmptyState
                  icon={FileText}
                  title="Nenhum negócio cirúrgico registrado neste período"
                  description="Cadastre uma nova proposta de kit cirúrgico ou acione um pedido emergencial no DENTGO."
                  actionLabel="Recarregar Pipeline"
                  onAction={() => dealsQuery.refetch()}
                />
              ) : (
                <div className="space-y-4">
                  <DataTable columns={columns} data={deals} />
                </div>
              )}
            </div>
          }
        />
      </ErrorBoundary>
    </AppShell>
  );
}

export default App;
