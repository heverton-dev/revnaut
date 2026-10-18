import * as React from "react";
import { AppShell } from "@/components/layout/AppShell";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { DataTable, Column } from "@/components/ui/DataTable";
import { Skeleton } from "@/components/ui/Skeleton";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorBoundary } from "@/components/ui/ErrorBoundary";
import { Tabs } from "@/components/ui/Tabs";
import { Deal } from "@/types/api_contracts";
import { Plus, RefreshCw, FileText, CheckCircle2, ShieldAlert } from "lucide-react";
import { AppRouter } from "./router";

export function App() {
  const [activeTab, setActiveTab] = React.useState<"success" | "loading" | "empty" | "error">("success");
  const [activeNav, setActiveNav] = React.useState("deals");

  // Dados reais de exemplo tipados via Deal contract
  const sampleDeals: Deal[] = [
    {
      id: "d-101",
      title: "Consignação Caixa Cirúrgica Cone Morse — Dr. Roberto Silveira",
      value: 36000.0,
      stage_id: 101,
      pipeline_id: 1,
      contact_name: "Dr. Roberto Silveira",
      company_name: "Grupo Alfa Hospitalar",
      owner_id: "usr-field-01",
      owner_name: "Carlos Mendonça (Field)",
      expected_close_date: "2026-10-30",
      created_at: "2026-10-15T10:00:00Z",
    },
    {
      id: "d-102",
      title: "Reposição Emergencial DENTGO (45 min) — Implantes Cônicos 3.5mm",
      value: 12500.0,
      stage_id: 102,
      pipeline_id: 1,
      contact_name: "Dra. Mariana Alencar",
      company_name: "Clínica Alencar & Associados",
      owner_id: "usr-inside-02",
      owner_name: "Patrícia Diniz (Inside)",
      expected_close_date: "2026-10-20",
      created_at: "2026-10-16T14:30:00Z",
    },
    {
      id: "d-103",
      title: "Contrato Anual de Consignação 5 Caixas — Instituto Mandic",
      value: 180000.0,
      stage_id: 103,
      pipeline_id: 1,
      contact_name: "Prof. Dr. Marcelo Lucchesi",
      company_name: "Faculdade São Leopoldo Mandic",
      owner_id: "usr-field-01",
      owner_name: "Carlos Mendonça (Field)",
      expected_close_date: "2026-11-15",
      created_at: "2026-10-17T09:15:00Z",
    },
  ];

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
        <Badge variant={deal.owner_name.includes("Field") ? "default" : "navy"} className="text-[10px]">
          {deal.owner_name}
        </Badge>
      ),
    },
    {
      key: "value",
      header: "Valor (BRL)",
      render: (deal) => (
        <span className="font-semibold text-text-main">
          {new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(deal.value)}
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

  return (
    <AppShell activeNav={activeNav} onNavigate={setActiveNav}>
      <AppRouter
        currentRoute={activeNav}
        defaultComponent={
          <div className="space-y-6 max-w-7xl mx-auto">
            {/* Cabeçalho da Página */}
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
                <Button variant="secondary" size="sm" className="inline-flex items-center gap-2">
                  <RefreshCw className="h-4 w-4" />
                  Sincronizar
                </Button>
                <Button size="sm" className="inline-flex items-center gap-2">
                  <Plus className="h-4 w-4" />
                  Novo Negócio
                </Button>
              </div>
            </div>

            {/* Seletor de Demonstração dos 4 Estados Obrigatórios */}
            <Card className="border-border">
              <CardHeader className="py-3 px-4">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                  <CardTitle className="text-sm">Auditoria de Estados de Interface (Design System SSOT)</CardTitle>
                  <div className="flex items-center gap-1.5">
                    <Button
                      size="sm"
                      variant={activeTab === "success" ? "default" : "outline"}
                      onClick={() => setActiveTab("success")}
                    >
                      1. Success State
                    </Button>
                    <Button
                      size="sm"
                      variant={activeTab === "loading" ? "default" : "outline"}
                      onClick={() => setActiveTab("loading")}
                    >
                      2. Loading State
                    </Button>
                    <Button
                      size="sm"
                      variant={activeTab === "empty" ? "default" : "outline"}
                      onClick={() => setActiveTab("empty")}
                    >
                      3. Empty State
                    </Button>
                    <Button
                      size="sm"
                      variant={activeTab === "error" ? "danger" : "outline"}
                      onClick={() => setActiveTab("error")}
                    >
                      4. Error State
                    </Button>
                  </div>
                </div>
              </CardHeader>
            </Card>

            {/* Renderização Condicional dos 4 Estados Reais */}
            {activeTab === "success" && (
              <div className="space-y-4">
                <DataTable columns={columns} data={sampleDeals} />
              </div>
            )}

            {activeTab === "loading" && (
              <div className="space-y-4">
                <DataTable columns={columns} data={[]} isLoading={true} />
              </div>
            )}

            {activeTab === "empty" && (
              <EmptyState
                icon={FileText}
                title="Nenhum negócio cirúrgico registrado neste período"
                description="Cadastre uma nova proposta de kit cirúrgico ou acione um pedido emergencial no DENTGO."
                actionLabel="Cadastrar Primeiro Negócio"
                onAction={() => setActiveTab("success")}
              />
            )}

            {activeTab === "error" && (
              <ErrorBoundary>
                <SimulatedErrorComponent onReset={() => setActiveTab("success")} />
              </ErrorBoundary>
            )}
          </div>
        }
      />
    </AppShell>
  );
}

function SimulatedErrorComponent({ onReset }: { onReset: () => void }) {
  // Simulação de erro real capturado pelo ErrorBoundary
  throw new Error("Falha de conexão com réplica analítica OLAP (Timeout 15000ms)");
}

export default App;
