import React, { useState } from "react";
import { Sparkles, CheckCircle2, AlertCircle, Calendar, Brain, Zap, ShieldCheck } from "lucide-react";

interface Objection {
  category: string;
  objection_text: string;
  suggested_counter_argument?: string;
}

interface TaskItem {
  title: string;
  due_date: string;
  assignee?: string;
  priority?: string;
}

export interface GranolaCopilotCardProps {
  dealId?: string;
  onApplySuccess?: () => void;
}

interface DealOption {
  id: string;
  title: string;
  company?: string;
  value?: number;
}

export const GranolaCopilotCard: React.FC<GranolaCopilotCardProps> = ({ dealId: initialDealId, onApplySuccess }) => {
  const [deals, setDeals] = useState<DealOption[]>([]);
  const [selectedDealId, setSelectedDealId] = useState<string>(initialDealId || "");
  const [transcriptionInput, setTranscriptionInput] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<{
    summary?: string;
    implantSystems?: string[];
    objections?: Objection[];
    tasks?: TaskItem[];
    suggestedValue?: number;
  } | null>(null);

  React.useEffect(() => {
    if (initialDealId) {
      setSelectedDealId(initialDealId);
    }
  }, [initialDealId]);

  React.useEffect(() => {
    const fetchDeals = async () => {
      try {
        const res = await fetch("/api/v1/deals");
        if (res.ok) {
          const data = await res.json();
          const list = Array.isArray(data) ? data : data.deals || [];
          setDeals(list);
          if (!selectedDealId && list.length > 0) {
            setSelectedDealId(list[0].id);
          }
        }
      } catch {
        // Fallback silencioso
      }
    };
    fetchDeals();
  }, []);

  const effectiveDealId = selectedDealId || initialDealId || "d-default";

  const handleExtractAndApply = async () => {
    if (!transcriptionInput.trim() || !effectiveDealId) return;
    setIsProcessing(true);
    try {
      const res = await fetch("/api/v1/intelligence/copilot/extract-and-apply", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          deal_id: effectiveDealId,
          transcription_text: transcriptionInput,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setResult({
          summary: data.extraction.executive_summary,
          implantSystems: data.extraction.implant_systems_mentioned,
          objections: data.extraction.objections_raised,
          tasks: data.extraction.next_steps_tasks,
          suggestedValue: data.extraction.suggested_deal_value,
        });
        if (onApplySuccess) onApplySuccess();
      }
    } catch {
      // Estado mantido em caso de falha de rede
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="rounded-2xl border border-border bg-surface-card p-5 shadow-card text-text-main space-y-4">
      <div className="flex items-center justify-between border-b border-border pb-3">
        <div className="flex items-center space-x-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-navy-subtle text-brand-navy">
            <Brain className="h-4 w-4" />
          </div>
          <div>
            <h4 className="text-sm font-semibold tracking-tight text-text-main flex items-center space-x-1.5">
              <span>Copiloto Comercial Granola-like</span>
              <span className="rounded-full bg-brand-primary-subtle px-2 py-0.5 text-[10px] font-medium text-brand-primary">
                Zero-Touch
              </span>
            </h4>
            <p className="text-xs text-text-secondary">Notas de voz de campo e transcrições de reuniões</p>
          </div>
        </div>
        <div className="flex items-center space-x-1 text-xs text-status-success">
          <ShieldCheck className="h-3.5 w-3.5" />
          <span>LiteLLM Ativo</span>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 bg-surface-bg p-2.5 rounded-xl border border-border">
        <label className="text-xs font-medium text-text-secondary">Oportunidade Comercial (Deal):</label>
        {deals.length > 0 ? (
          <select
            value={effectiveDealId}
            onChange={(e) => setSelectedDealId(e.target.value)}
            className="rounded-lg border border-border bg-surface-card px-2.5 py-1 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary"
          >
            {deals.map((d) => (
              <option key={d.id} value={d.id}>
                {d.id} • {d.title} ({d.company || "Sem empresa"})
              </option>
            ))}
          </select>
        ) : (
          <span className="font-mono text-xs text-brand-primary">{effectiveDealId}</span>
        )}
      </div>

      <div className="space-y-2">
        <label className="text-xs font-medium text-text-secondary">
          Transcrição da Reunião ou Áudio do Consultor
        </label>
        <textarea
          rows={3}
          value={transcriptionInput}
          onChange={(e) => setTranscriptionInput(e.target.value)}
          placeholder="Ex: O Dr. Roberto pediu 20 implantes Cone Morse com prazo de 60 dias até sexta-feira..."
          className="w-full rounded-xl border border-border bg-surface-bg p-3 text-xs text-text-main placeholder:text-text-muted focus:border-brand-primary focus:outline-none focus:ring-1 focus:ring-brand-primary"
        />
        <div className="flex justify-end">
          <button
            onClick={handleExtractAndApply}
            disabled={isProcessing || !transcriptionInput.trim()}
            className="flex items-center space-x-1.5 rounded-xl bg-brand-primary px-4 py-2 text-xs font-medium text-text-inverse shadow-card hover:bg-brand-primary-hover transition disabled:opacity-50"
          >
            <Sparkles className="h-3.5 w-3.5" />
            <span>{isProcessing ? "Extraindo e Atualizando..." : "Processar & Preencher Deal"}</span>
          </button>
        </div>
      </div>

      {result && (
        <div className="rounded-xl border border-border bg-surface-bg p-4 space-y-3">
          <div className="flex items-center space-x-2 text-xs font-semibold text-brand-primary">
            <Zap className="h-4 w-4 text-brand-primary" />
            <span>Atualização Zero-Touch Concluída</span>
          </div>

          {result.summary && (
            <div className="text-xs text-text-secondary bg-surface-card p-2.5 rounded-lg border border-border">
              <span className="font-medium text-text-main">Resumo Executivo:</span> {result.summary}
            </div>
          )}

          {result.suggestedValue && (
            <div className="flex items-center justify-between text-xs text-text-secondary bg-surface-card p-2 rounded-lg border border-border">
              <span>Valor Atualizado da Oportunidade:</span>
              <span className="font-semibold text-status-success">
                {new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(
                  result.suggestedValue
                )}
              </span>
            </div>
          )}

          {result.objections && result.objections.length > 0 && (
            <div className="space-y-1.5">
              <span className="text-[11px] font-medium text-text-secondary uppercase tracking-wider">
                Objeções Mapeadas ({result.objections.length})
              </span>
              {result.objections.map((obj, i) => (
                <div
                  key={i}
                  className="flex items-start space-x-2 text-xs text-text-secondary bg-surface-card p-2 rounded-lg border border-border"
                >
                  <AlertCircle className="h-3.5 w-3.5 text-status-warning shrink-0 mt-0.5" />
                  <div>
                    <span className="font-medium text-text-main capitalize">{obj.category}:</span>{" "}
                    {obj.objection_text}
                    {obj.suggested_counter_argument && (
                      <p className="mt-1 text-[11px] text-brand-navy">
                        <span className="font-medium">Argumento Sugerido:</span>{" "}
                        {obj.suggested_counter_argument}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {result.tasks && result.tasks.length > 0 && (
            <div className="space-y-1.5">
              <span className="text-[11px] font-medium text-text-secondary uppercase tracking-wider">
                Tarefas Agendadas Automaticamente
              </span>
              {result.tasks.map((task, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between text-xs text-text-secondary bg-surface-card p-2 rounded-lg border border-border"
                >
                  <div className="flex items-center space-x-2">
                    <CheckCircle2 className="h-3.5 w-3.5 text-status-success" />
                    <span>{task.title}</span>
                  </div>
                  <div className="flex items-center space-x-1 text-[11px] text-text-muted">
                    <Calendar className="h-3 w-3" />
                    <span>{task.due_date}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
