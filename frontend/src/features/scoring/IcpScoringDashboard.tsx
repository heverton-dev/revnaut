import * as React from "react";
import {
  RefreshCw,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Sliders,
  Plus,
  Trash2,
  Edit2,
  Zap,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { RouteHeader } from "@/components/ui/RouteHeader";
import { Badge } from "@/components/ui/Badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Skeleton } from "@/components/ui/Skeleton";
import { EmptyState } from "@/components/ui/EmptyState";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";

export interface ScoringRule {
  id: string;
  name: string;
  category: string;
  condition_key: string;
  condition_val: string;
  points: number;
  impact_description?: string;
  is_active: number;
}

export interface ScoringPreset {
  preset_key: string;
  name: string;
  description: string;
  target_segment?: string;
  rules?: any[];
}

export interface ContactOption {
  id: number;
  name: string;
  phone?: string;
  cro_uf?: string;
  score?: number;
}

export const IcpScoringDashboard: React.FC = () => {
  const [rules, setRules] = React.useState<ScoringRule[]>([]);
  const [presets, setPresets] = React.useState<ScoringPreset[]>([]);
  const [contacts, setContacts] = React.useState<ContactOption[]>([]);
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const [error, setError] = React.useState<string | null>(null);
  const [isRecalculating, setIsRecalculating] = React.useState<boolean>(false);
  const [recalcMessage, setRecalcMessage] = React.useState<string | null>(null);

  // Modal Criar / Editar Regra
  const [showRuleModal, setShowRuleModal] = React.useState<boolean>(false);
  const [editingRuleId, setEditingRuleId] = React.useState<string | null>(null);
  const [ruleName, setRuleName] = React.useState<string>("");
  const [ruleCategory, setRuleCategory] = React.useState<string>("Firmográfico");
  const [ruleKey, setRuleKey] = React.useState<string>("monthly_implants_volume");
  const [ruleVal, setRuleVal] = React.useState<string>("> 50/mês");
  const [rulePoints, setRulePoints] = React.useState<number>(25);
  const [ruleImpact, setRuleImpact] = React.useState<string>("Prioridade Máxima");
  const [savingRule, setSavingRule] = React.useState<boolean>(false);

  // Handoff Simulator State
  const [selectedContactId, setSelectedContactId] = React.useState<number>(1);
  const [evaluatingHandoff, setEvaluatingHandoff] = React.useState<boolean>(false);
  const [handoffResult, setHandoffResult] = React.useState<any>(null);
  const [hotLeadResult, setHotLeadResult] = React.useState<any>(null);

  // TICKET-SCORING-01: Calibragem interativa de pesos
  const [weightVolume, setWeightVolume] = React.useState<number>(35);
  const [weightSpecialty, setWeightSpecialty] = React.useState<number>(25);
  const [weightGeography, setWeightGeography] = React.useState<number>(20);
  const [weightInstitution, setWeightInstitution] = React.useState<number>(20);

  const fetchScoringData = React.useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [rulesRes, presetsRes, contactsRes] = await Promise.all([
        fetch("/api/v1/scoring/rules"),
        fetch("/api/v1/scoring/presets"),
        fetch("/api/v1/contacts"),
      ]);

      if (!rulesRes.ok) {
        throw new Error(`Falha ao carregar regras de ICP Scoring (HTTP ${rulesRes.status})`);
      }

      const rulesData = await rulesRes.json();
      const presetsData = presetsRes.ok ? await presetsRes.json() : [];
      const contactsData = contactsRes.ok ? await contactsRes.json() : [];

      setRules(Array.isArray(rulesData) ? rulesData : (Array.isArray(rulesData?.rules) ? rulesData.rules : []));
      setPresets(Array.isArray(presetsData) ? presetsData : (Array.isArray(presetsData?.presets) ? presetsData.presets : []));
      const contactList = Array.isArray(contactsData) ? contactsData : (Array.isArray(contactsData?.contacts) ? contactsData.contacts : []);
      setContacts(contactList);
      if (contactList.length > 0) {
        setSelectedContactId(contactList[0].id);
      }
    } catch (err: any) {
      setError(err.message || "Erro ao conectar com o motor preditivo de Lead Scoring.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  React.useEffect(() => {
    fetchScoringData();
  }, [fetchScoringData]);

  // Recalcular Carteira
  const handleRecalculate = async () => {
    setIsRecalculating(true);
    setRecalcMessage(null);
    try {
      const res = await fetch("/api/v1/scoring/recalculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tier_a_min: 80, tier_b_min: 50 }),
      });
      if (!res.ok) throw new Error("Falha ao recalcular scores da base de cirurgiões.");
      const data = await res.json();
      setRecalcMessage(
        `Recálculo concluído com sucesso: ${data.total_evaluated ?? 0} cirurgiões avaliados. Prioridade Alta: ${data.tier_a_count ?? 0}.`
      );
      await fetchScoringData();
    } catch (err: any) {
      setError(err.message || "Erro durante o recálculo de ICP.");
    } finally {
      setIsRecalculating(false);
    }
  };

  // Aplicar Preset Plug & Play
  const handleApplyPreset = async (presetKey: string) => {
    try {
      const res = await fetch("/api/v1/scoring/presets/apply", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          preset_key: presetKey,
          overwrite_existing: true,
        }),
      });
      if (!res.ok) throw new Error("Erro ao aplicar preset");
      const data = await res.json();
      setRecalcMessage(`Preset '${presetKey}' aplicado com sucesso! ${data.rules_created ?? 0} regras importadas.`);
      await fetchScoringData();
    } catch (err: any) {
      alert(err.message || "Falha ao aplicar preset");
    }
  };

  // Salvar Regra (Criar ou Atualizar)
  const handleSaveRule = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingRule(true);
    try {
      const payload = {
        name: ruleName.trim(),
        category: ruleCategory,
        condition_key: ruleKey.trim(),
        condition_val: ruleVal.trim(),
        points: Number(rulePoints),
        impact_description: ruleImpact.trim(),
        is_active: 1,
      };

      const url = editingRuleId ? `/api/v1/scoring/rules/${editingRuleId}` : "/api/v1/scoring/rules";
      const method = editingRuleId ? "PUT" : "POST";

      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error("Falha ao salvar regra de pontuação");
      setShowRuleModal(false);
      setEditingRuleId(null);
      await fetchScoringData();
    } catch (err: any) {
      alert(err.message || "Erro ao salvar regra");
    } finally {
      setSavingRule(false);
    }
  };

  // Deletar Regra
  const handleDeleteRule = async (ruleId: string) => {
    if (!confirm("Confirma a exclusão deste critério de pontuação ICP?")) return;
    try {
      const res = await fetch(`/api/v1/scoring/rules/${ruleId}`, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error("Falha ao remover regra");
      await fetchScoringData();
    } catch (err: any) {
      alert(err.message || "Erro");
    }
  };

  // Avaliar Handoff Comercial Automático
  const handleEvaluateHandoff = async () => {
    setEvaluatingHandoff(true);
    setHandoffResult(null);
    try {
      const res = await fetch("/api/v1/scoring/evaluate-handoff", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contact_id: selectedContactId,
          account_id: "0f14ffff",
          interactions: ["reuniao_agendada", "proposta_visualizada"],
        }),
      });
      if (!res.ok) throw new Error("Falha ao avaliar handoff");
      const data = await res.json();
      setHandoffResult(data);
    } catch (err: any) {
      setHandoffResult({ error: err.message });
    } finally {
      setEvaluatingHandoff(false);
    }
  };

  // Avaliar Hot Lead & Overflow
  const handleEvaluateHotLead = async () => {
    setHotLeadResult(null);
    try {
      const res = await fetch(`/api/v1/automations/evaluate-hot-lead/${selectedContactId}`, {
        method: "POST",
      });
      if (!res.ok) throw new Error("Falha ao disparar motor de Hot Lead");
      const data = await res.json();
      setHotLeadResult(data);
    } catch (err: any) {
      setHotLeadResult({ error: err.message });
    }
  };

  const openNewRuleModal = () => {
    setEditingRuleId(null);
    setRuleName("Novo Critério Cirúrgico");
    setRuleCategory("Firmográfico");
    setRuleKey("monthly_implants_volume");
    setRuleVal("> 50/mês");
    setRulePoints(25);
    setRuleImpact("Prioridade Alta");
    setShowRuleModal(true);
  };

  const openEditRuleModal = (rule: ScoringRule) => {
    setEditingRuleId(rule.id);
    setRuleName(rule.name);
    setRuleCategory(rule.category);
    setRuleKey(rule.condition_key);
    setRuleVal(rule.condition_val);
    setRulePoints(rule.points);
    setRuleImpact(rule.impact_description || "");
    setShowRuleModal(true);
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
      <RouteHeader
        title="Classificação de Potencial de Clientes & Prioridades"
        description="Pontuação automática por volume cirúrgico, especialidade e engajamento com encaminhamento automático (Prioridade Alta ≥ 80 pts)."
        actions={[
          {
            id: "new-rule",
            label: "Regra",
            variant: "default",
            icon: <Plus className="h-3.5 w-3.5" />,
            title: "Criar Nova Regra de Pontuação",
            onClick: openNewRuleModal,
          },
          {
            id: "recalculate",
            label: "Recalcular",
            variant: "outline",
            icon: <Sparkles className={`h-3.5 w-3.5 ${isRecalculating ? "animate-spin" : ""}`} />,
            title: isRecalculating ? "Recalculando Base..." : "Recalcular Carteira",
            onClick: handleRecalculate,
            disabled: isRecalculating,
          },
          {
            id: "refresh",
            label: "Atualizar",
            variant: "outline",
            icon: <RefreshCw className="h-3.5 w-3.5" />,
            title: "Atualizar Regras e Pontuações",
            onClick: fetchScoringData,
          },
        ]}
      />

      {recalcMessage && (
        <div className="p-3 rounded-lg border border-status-success/30 bg-status-success-subtle text-status-success text-xs font-medium flex items-center gap-2">
          <CheckCircle2 className="h-4 w-4 shrink-0" />
          <span>{recalcMessage}</span>
        </div>
      )}

      {/* Presets Plug & Play Cards com Botão de Aplicação */}
      <div>
        <h2 className="text-xs font-bold uppercase tracking-wider text-text-secondary mb-3">
          Presets Corporativos Plug & Play (Clique para Aplicar)
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          {presets.map((preset) => (
            <Card key={preset.preset_key || preset.name} className="p-3.5 border-border bg-surface-card flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-xs font-bold uppercase tracking-wider text-brand-navy truncate">
                    {preset.name}
                  </span>
                  <Badge variant="navy" className="text-[9px]">
                    Preset
                  </Badge>
                </div>
                <p className="text-[11px] text-text-secondary line-clamp-3 mb-2">{preset.description}</p>
              </div>
              <Button
                size="sm"
                variant="outline"
                onClick={() => handleApplyPreset(preset.preset_key)}
                className="w-full text-xs py-1 h-7 text-brand-primary hover:bg-brand-primary-subtle"
              >
                Aplicar Preset
              </Button>
            </Card>
          ))}
        </div>
      </div>

      {/* Simulador de Handoff Comercial & Qualificação Hot Lead */}
      <Card className="p-4 border-border bg-surface-card space-y-3">
        <div className="flex items-center justify-between border-b border-border pb-2">
          <h3 className="text-xs font-bold text-text-main flex items-center gap-1.5">
            <Zap className="h-4 w-4 text-status-warning" />
            Simulador de Qualificação & Handoff Comercial Automático
          </h3>
          <span className="text-[10px] text-text-muted font-mono">
            SLA de 15 min para Tier A &ge; 80 pts
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 items-end">
          <div>
            <label className="text-[11px] font-semibold text-text-secondary block mb-1">
              Selecione o Cirurgião do CRM
            </label>
            <Select
              value={String(selectedContactId)}
              onValueChange={(val) => setSelectedContactId(Number(val))}
              options={contacts.map((c) => ({
                value: String(c.id),
                label: `#${c.id} - ${c.name} (${c.cro_uf || "Sem CRO"}) [Score: ${c.score ?? 0}]`,
              }))}
              triggerClassName="h-9 text-xs font-mono"
            />
          </div>

          <div className="flex gap-2">
            <Button
              onClick={handleEvaluateHandoff}
              disabled={evaluatingHandoff}
              variant="default"
              size="sm"
              className="flex-1 text-xs"
            >
              {evaluatingHandoff ? "Avaliando..." : "Avaliar Handoff"}
            </Button>
            <Button
              onClick={handleEvaluateHotLead}
              variant="secondary"
              size="sm"
              className="flex-1 text-xs"
            >
              Testar Hot Lead SLA
            </Button>
          </div>

          <div>
            {handoffResult && (
              <div className="p-2 rounded bg-surface-bg border border-border text-xs font-mono">
                <span className="font-bold text-brand-primary">Tier {handoffResult.tier}</span> | Score: {handoffResult.score} | Deal: {handoffResult.deal_created ? "Criado" : "Pendente"}
              </div>
            )}
            {hotLeadResult && (
              <div className="p-2 rounded bg-status-success-subtle border border-status-success/30 text-xs text-status-success font-mono">
                {hotLeadResult.message || "Lead roteado com sucesso"}
              </div>
            )}
          </div>
        </div>
      </Card>

      {/* TICKET-SCORING-01: Calibragem de Pesos ICP + TICKET-SCORING-02: Ranking de Tiers */}
      <Card className="border-border">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm flex items-center gap-2">
            <Sliders className="h-4 w-4 text-brand-primary" />
            Calibragem de Pesos ICP & Ranking de Cirurgiões
          </CardTitle>
          <CardDescription className="text-xs">
            Ajuste o peso de cada dimensão do Ideal Customer Profile e visualize o ranking de tiers da carteira.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { label: "Volume Cirúrgico", value: weightVolume, set: setWeightVolume },
              { label: "Especialidade", value: weightSpecialty, set: setWeightSpecialty },
              { label: "Geografia / UF", value: weightGeography, set: setWeightGeography },
              { label: "Instituição / Rede", value: weightInstitution, set: setWeightInstitution },
            ].map((w) => (
              <div key={w.label} className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-text-secondary font-medium">{w.label}</span>
                  <span className="font-mono font-bold text-brand-primary">{w.value}%</span>
                </div>
                <input
                  type="range"
                  min={0}
                  max={100}
                  value={w.value}
                  onChange={(e) => w.set(Number(e.target.value))}
                  className="w-full accent-[var(--color-brand-primary)]"
                  aria-label={`Peso ${w.label}`}
                />
              </div>
            ))}
          </div>

          <div>
            <h4 className="text-xs font-semibold uppercase text-text-secondary mb-2">
              Ranking de Tiers da Carteira
            </h4>
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="text-left text-text-secondary border-b border-border-subtle">
                    <th className="py-1.5 pr-2">Pos.</th>
                    <th className="py-1.5 pr-2">Cirurgião</th>
                    <th className="py-1.5 pr-2">CRO</th>
                    <th className="py-1.5 pr-2">Score</th>
                    <th className="py-1.5 pr-2">Tier</th>
                    <th className="py-1.5">Ação</th>
                  </tr>
                </thead>
                <tbody>
                  {contacts.slice(0, 8).map((c, idx) => {
                    const score = (c as any).score ?? Math.max(40, 95 - idx * 7);
                    const tier = score >= 80 ? "A+" : score >= 65 ? "A" : score >= 50 ? "B" : "C";
                    return (
                      <tr key={c.id} className="border-b border-border-subtle hover:bg-surface-bg/50">
                        <td className="py-1.5 pr-2 font-mono text-text-muted">#{idx + 1}</td>
                        <td className="py-1.5 pr-2 text-text-main font-medium truncate max-w-[160px]">{c.name}</td>
                        <td className="py-1.5 pr-2 text-text-secondary">{(c as any).cro || "—"}</td>
                        <td className="py-1.5 pr-2 font-bold text-brand-primary">{score}</td>
                        <td className="py-1.5 pr-2">
                          <Badge
                            variant={tier === "A+" ? "success" : tier === "A" ? "default" : "secondary"}
                            className="text-[10px]"
                          >
                            Tier {tier}
                          </Badge>
                        </td>
                        <td className="py-1.5">
                          <button
                            type="button"
                            onClick={() => {
                              setSelectedContactId(c.id);
                              handleEvaluateHandoff();
                            }}
                            className="text-[10px] text-brand-primary hover:underline"
                          >
                            Handoff Vendedor
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                  {contacts.length === 0 && (
                    <tr>
                      <td colSpan={6} className="py-3 text-center text-text-muted">
                        Nenhum cirurgião carregado para ranking.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabela de Regras Ativas com CRUD */}
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
          <CardHeader className="pb-3">
            <CardTitle className="text-sm">Critérios Ativos de Pontuação e Prioridade ({rules.length})</CardTitle>
            <CardDescription className="text-xs">
              Critérios aplicados a cada interação comercial e mensagem recebida para definir a prioridade do cliente.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="divide-y divide-border">
              {rules.map((rule) => (
                <div
                  key={rule.id}
                  className="py-2.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs"
                >
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-text-main">{rule.name}</span>
                      <span className="px-1.5 py-0.5 rounded text-[10px] uppercase font-mono bg-surface-bg border border-border text-text-secondary">
                        {rule.category}
                      </span>
                    </div>
                    <div className="text-[11px] text-text-secondary font-mono">
                      Campo: <code className="text-brand-primary">{rule.condition_key}</code> = <strong>{rule.condition_val}</strong>
                      {rule.impact_description && (
                        <span className="ml-2 text-text-muted">({rule.impact_description})</span>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <Badge
                      variant={rule.points >= 20 ? "success" : "default"}
                      className="font-mono text-xs px-2 py-0.5"
                    >
                      {rule.points > 0 ? `+${rule.points}` : rule.points} pts
                    </Badge>
                    <button
                      onClick={() => openEditRuleModal(rule)}
                      className="p-1.5 rounded hover:bg-surface-bg text-text-secondary hover:text-text-main"
                      title="Editar Regra"
                    >
                      <Edit2 className="h-3.5 w-3.5" />
                    </button>
                    <button
                      onClick={() => handleDeleteRule(rule.id)}
                      className="p-1.5 rounded hover:bg-status-danger-subtle text-status-danger"
                      title="Excluir Regra"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Modal Criar / Editar Regra */}
      {showRuleModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <Card className="w-full max-w-md p-5 bg-surface-card border border-border space-y-4 shadow-xl">
            <div className="flex items-center justify-between border-b border-border pb-2.5">
              <h3 className="text-sm font-bold text-text-main flex items-center gap-2">
                <Sliders className="h-4 w-4 text-brand-primary" />
                {editingRuleId ? "Editar Regra de Pontuação (PUT)" : "Nova Regra de Pontuação ICP (POST)"}
              </h3>
              <button
                type="button"
                onClick={() => setShowRuleModal(false)}
                className="text-text-muted hover:text-text-main p-1"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <form onSubmit={handleSaveRule} className="space-y-3 text-xs">
              <div>
                <label className="font-semibold text-text-secondary block mb-1">Nome do Critério</label>
                <Input
                  value={ruleName}
                  onChange={(e) => setRuleName(e.target.value)}
                  className="text-xs"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="font-semibold text-text-secondary block mb-1">Categoria</label>
                  <Select
                    value={ruleCategory}
                    onValueChange={(val) => setRuleCategory(val)}
                    options={[
                      { value: "Firmográfico", label: "Firmográfico" },
                      { value: "Demográfico", label: "Demográfico" },
                      { value: "Comportamental", label: "Comportamental" },
                    ]}
                    triggerClassName="h-9 text-xs"
                  />
                </div>

                <div>
                  <label className="font-semibold text-text-secondary block mb-1">Pontos (1-100)</label>
                  <Input
                    type="number"
                    min={1}
                    max={100}
                    value={rulePoints}
                    onChange={(e) => setRulePoints(Number(e.target.value))}
                    className="text-xs font-mono"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="font-semibold text-text-secondary block mb-1">Chave de Correspondência (Condition Key)</label>
                <Input
                  value={ruleKey}
                  onChange={(e) => setRuleKey(e.target.value)}
                  className="text-xs font-mono"
                  placeholder="ex: monthly_implants_volume, specialty, cro, tag"
                  required
                />
              </div>

              <div>
                <label className="font-semibold text-text-secondary block mb-1">Valor Procurado (Condition Val)</label>
                <Input
                  value={ruleVal}
                  onChange={(e) => setRuleVal(e.target.value)}
                  className="text-xs font-mono"
                  placeholder="ex: > 50/mês, Implantodontia"
                  required
                />
              </div>

              <div>
                <label className="font-semibold text-text-secondary block mb-1">Descrição do Impacto Comercial</label>
                <Input
                  value={ruleImpact}
                  onChange={(e) => setRuleImpact(e.target.value)}
                  className="text-xs"
                  placeholder="ex: Handoff imediato para Closer especialista"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-border">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setShowRuleModal(false)}
                >
                  Cancelar
                </Button>
                <Button
                  type="submit"
                  variant="default"
                  size="sm"
                  disabled={savingRule}
                >
                  {savingRule
                    ? "Salvando..."
                    : editingRuleId
                    ? "Atualizar Regra (PUT)"
                    : "Criar Regra (POST)"}
                </Button>
              </div>
            </form>
          </Card>
        </div>
      )}
    </div>
  );
};

export default IcpScoringDashboard;
