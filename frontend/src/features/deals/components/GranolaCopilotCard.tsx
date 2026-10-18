import React, { useState } from 'react';
import { Sparkles, CheckCircle2, AlertCircle, Calendar, ArrowRight, Brain, Zap, ShieldCheck } from 'lucide-react';

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

interface GranolaCopilotCardProps {
  dealId: string;
  onApplySuccess?: () => void;
}

export const GranolaCopilotCard: React.FC<GranolaCopilotCardProps> = ({ dealId, onApplySuccess }) => {
  const [transcriptionInput, setTranscriptionInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<{
    summary?: string;
    implantSystems?: string[];
    objections?: Objection[];
    tasks?: TaskItem[];
    suggestedValue?: number;
  } | null>(null);

  const handleExtractAndApply = async () => {
    if (!transcriptionInput.trim()) return;
    setIsProcessing(true);
    try {
      const res = await fetch('/api/v1/intelligence/copilot/extract-and-apply', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          deal_id: dealId,
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
      // Falha silenciosa com fallback de estado
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/90 p-5 shadow-xl backdrop-blur-sm text-slate-100 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-500/10 text-indigo-400">
            <Brain className="h-4 w-4" />
          </div>
          <div>
            <h4 className="text-sm font-semibold tracking-tight text-white flex items-center space-x-1.5">
              <span>Copiloto Comercial Granola-like</span>
              <span className="rounded-full bg-indigo-500/20 px-2 py-0.5 text-[10px] font-medium text-indigo-300">
                Zero-Touch
              </span>
            </h4>
            <p className="text-xs text-slate-400">Notas de voz de campo e transcrições de reuniões</p>
          </div>
        </div>
        <div className="flex items-center space-x-1 text-xs text-emerald-400">
          <ShieldCheck className="h-3.5 w-3.5" />
          <span>LiteLLM Ativo</span>
        </div>
      </div>

      {/* Input de Transcrição / Áudio */}
      <div className="space-y-2">
        <label className="text-xs font-medium text-slate-300">
          Transcrição da Reunião ou Áudio do Consultor
        </label>
        <textarea
          rows={3}
          value={transcriptionInput}
          onChange={(e) => setTranscriptionInput(e.target.value)}
          placeholder="Ex: O Dr. Roberto pediu 20 implantes Cone Morse com prazo de 60 dias até sexta-feira..."
          className="w-full rounded-xl border border-slate-700 bg-slate-950 p-3 text-xs text-slate-100 placeholder-slate-500 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
        <div className="flex justify-end">
          <button
            onClick={handleExtractAndApply}
            disabled={isProcessing || !transcriptionInput.trim()}
            className="flex items-center space-x-1.5 rounded-xl bg-indigo-600 px-4 py-2 text-xs font-medium text-white shadow-md hover:bg-indigo-500 transition disabled:opacity-50"
          >
            <Sparkles className="h-3.5 w-3.5" />
            <span>{isProcessing ? 'Extraindo e Atualizando...' : 'Processar & Preencher Deal'}</span>
          </button>
        </div>
      </div>

      {/* Resultado da Extração Cognitiva */}
      {result && (
        <div className="rounded-xl border border-indigo-500/20 bg-indigo-950/20 p-4 space-y-3">
          <div className="flex items-center space-x-2 text-xs font-semibold text-indigo-300">
            <Zap className="h-4 w-4 text-indigo-400" />
            <span>Atualização Zero-Touch Concluída</span>
          </div>

          {result.summary && (
            <div className="text-xs text-slate-300 bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
              <span className="font-medium text-white">Resumo Executivo:</span> {result.summary}
            </div>
          )}

          {result.suggestedValue && (
            <div className="flex items-center justify-between text-xs text-slate-300 bg-slate-900/60 p-2 rounded-lg border border-slate-800">
              <span>Valor Atualizado da Oportunidade:</span>
              <span className="font-semibold text-emerald-400">
                {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(result.suggestedValue)}
              </span>
            </div>
          )}

          {/* Objeções Mapeadas */}
          {result.objections && result.objections.length > 0 && (
            <div className="space-y-1.5">
              <span className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">
                Objeções Mapeadas ({result.objections.length})
              </span>
              {result.objections.map((obj, i) => (
                <div key={i} className="flex items-start space-x-2 text-xs text-slate-300 bg-slate-900/50 p-2 rounded-lg border border-slate-800">
                  <AlertCircle className="h-3.5 w-3.5 text-amber-400 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-medium text-white capitalize">{obj.category}:</span> {obj.objection_text}
                    {obj.suggested_counter_argument && (
                      <p className="mt-1 text-[11px] text-indigo-300">
                        <span className="font-medium">Argumento Sugerido:</span> {obj.suggested_counter_argument}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Tarefas Geradas */}
          {result.tasks && result.tasks.length > 0 && (
            <div className="space-y-1.5">
              <span className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">
                Tarefas Agendadas Automaticamente
              </span>
              {result.tasks.map((task, i) => (
                <div key={i} className="flex items-center justify-between text-xs text-slate-300 bg-slate-900/50 p-2 rounded-lg border border-slate-800">
                  <div className="flex items-center space-x-2">
                    <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                    <span>{task.title}</span>
                  </div>
                  <div className="flex items-center space-x-1 text-[11px] text-slate-400">
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
