import * as React from "react";
import { Target, RefreshCw, Sparkles, CheckCircle2, AlertCircle, Sliders } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Skeleton } from "@/components/ui/Skeleton";
import { EmptyState } from "@/components/ui/EmptyState";

export interface ScoringRule {
  id: number | string;
  field: string;
  operator: string;
  value: string;
  points: number;
  category?: string;
}

export interface ScoringPreset {
  id: string;
  name: string;
  description: string;
  rules_count?: number;
}

export const IcpScoringDashboard: React.FC = () => {
  const [rules, setRules] = React.useState<ScoringRule[]>([]);
  const [presets, setPresets] = React.useState<ScoringPreset[]>([]);
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const [error, setError] = React.useState<string | null>(null);
  const [isRecalculating, setIsRecalculating] = React.useState<boolean>(false);
  const [recalcMessage, setRecalcMessage] = React.useState<string | null>(null);

  const fetchScoringData = React.useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [rulesRes, presetsRes] = await Promise.all([
        fetch("/api/v1/scoring/rules"),
        fetch("/api/v1/scoring/presets"),
      ]);

      if (!rulesRes.ok) {
        throw new Error(`Falha ao carregar regras de ICP Scoring (HTTP ${rulesRes.status})`);
      }

      const rulesData = await rulesRes.json();
      const presetsData = presetsRes.ok ? await presetsRes.json() : [];

      setRules(Array.isArray(rulesData) ? rulesData : rulesData.rules || []);
      setPresets(Array.isArray(presetsData) ? presetsData : presetsData.presets || []);
    } catch (err: any) {
      setError(err.message || "Erro ao conectar com o motor preditivo de Lead Scoring.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  React.useEffect(() => {
    fetchScoringData();
  }, [fetchScoringData]);

  const handleRecalculate = async () => {
    setIsRecalculating(true);
    setRecalcMessage(null);
    try {
      const res = await fetch("/api/v1/scoring/recalculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      if (!res.ok) {
        throw new Error("Falha ao recalcular scores da base de cirurgiões.");
      }
      const data = await res.json();
      setRecalcMessage(
        `Recálculo concluído com sucesso: ${data.updated_count ?? data.total_evaluated ?? 0} cirurgiões avaliados.`
      );
      await fetchScoringData();
    } catch (err: any) {
      setError(err.message || "Erro durante o recálculo de ICP.");
    } finally {
      setIsRecalculating(false);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-4 max-w-6xl mx-auto">
        <Card className="p-6 border-border">
          <Skeleton className="h-6 w-64 mb-4" />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <Skeleton className="h-24 w-full" />
            <Skeleton className="h-24 w-full" />
            <Skeleton className="h-24 w-full" />
          </div>
          <Skeleton className="h-40 w-full" />
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <Card className="p-8 border-status-danger/30 bg-status-danger-subtle/20 text-center max-w-3xl mx-auto">
        <div className="flex flex-col items-center gap-3">
          <AlertCircle className="h-8 w-8 text-status-danger" />
          <h3 className="text-base font-semibold text-text-main">
            Falha ao carregar o Motor Preditivo de Lead Scoring (ICP)
          </h3>
          <p className="text-xs text-text-secondary max-w-md">{error}</p>
          <Button size="sm" onClick={fetchScoringData} className="mt-2 gap-1.5">
            <RefreshCw className="h-4 w-4" />
            Tentar Novamente
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-text-main flex items-center gap-2">
            <Target className="h-6 w-6 text-brand-primary" />
            Motor Preditivo de Lead Scoring Odontológico & ICP Fit
          </h1>
          <p className="text-sm text-text-secondary mt-1">
            Classificação ponderada por volume mensal de implantes, especialidade CRO e engajamento com handoff automático (Tier A &ge; 80 pts).
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            onClick={fetchScoringData}
            className="inline-flex items-center gap-1.5"
          >
            <RefreshCw className="h-4 w-4" />
            Atualizar
          </Button>
          <Button
            size="sm"
            onClick={handleRecalculate}
            disabled={isRecalculating}
            className="inline-flex items-center gap-1.5"
          >
            <Sparkles className="h-4 w-4" />
            {isRecalculating ? "Recalculando Base..." : "Recalcular Carteira ICP"}
          </Button>
        </div>
      </div>

      {recalcMessage && (
        <div className="p-3 rounded-lg border border-status-success/30 bg-status-success-subtle text-status-success text-xs font-medium flex items-center gap-2">
          <CheckCircle2 className="h-4 w-4 shrink-0" />
          <span>{recalcMessage}</span>
        </div>
      )}

      {presets.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {presets.map((preset) => (
            <Card key={preset.id || preset.name} className="p-4 border-border bg-surface-card">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold uppercase tracking-wider text-brand-navy">
                  {preset.name}
                </span>
                <Badge variant="navy" className="text-[10px]">
                  Preset ICP
                </Badge>
              </div>
              <p className="text-xs text-text-secondary">{preset.description}</p>
            </Card>
          ))}
        </div>
      )}

      {rules.length === 0 ? (
        <EmptyState
          icon={Sliders}
          title="Nenhuma regra de pontuação ICP ativa"
          description="Aplique um preset odontológico ou cadastre critérios de volume cirúrgico e especialidade para qualificar leads automaticamente."
          actionLabel="Recarregar Regras"
          onAction={fetchScoringData}
        />
      ) : (
        <Card className="border-border">
          <CardHeader>
            <CardTitle>Regras Ativas de Qualificação & Handoff Comercial</CardTitle>
            <CardDescription>
              Critérios determinísticos avaliados a cada interação omnichannel e submissão de landing page.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="divide-y divide-border-subtle">
              {rules.map((rule) => (
                <div
                  key={rule.id}
                  className="py-3 flex items-center justify-between gap-4 text-sm"
                >
                  <div>
                    <span className="font-semibold text-text-main">{rule.field}</span>
                    <span className="mx-2 text-xs font-mono text-text-muted">
                      {rule.operator}
                    </span>
                    <span className="text-text-secondary font-medium">{rule.value}</span>
                  </div>
                  <Badge
                    variant={rule.points >= 20 ? "success" : "default"}
                    className="font-mono text-xs"
                  >
                    {rule.points > 0 ? `+${rule.points}` : rule.points} pts
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default IcpScoringDashboard;
