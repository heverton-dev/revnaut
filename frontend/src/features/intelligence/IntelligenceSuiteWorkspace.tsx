import React, { useState, useEffect, useCallback } from "react";
import {
  Cpu,
  Layers,
  Activity,
  DollarSign,
  TrendingUp,
  RefreshCw,
  Search,
  Clock,
  Sparkles,
  Database,
  Plus,
  ShieldCheck,
  ChevronRight,
  Package,
  Mic,
  Square,
  Radar,
} from "lucide-react";
import { Tabs } from "@/components/ui/Tabs";
import { RouteHeader } from "@/components/ui/RouteHeader";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";
import { GranolaCopilotCard } from "@/features/deals/components/GranolaCopilotCard";

interface DealItem {
  id: string;
  title: string;
  company?: string;
  value?: number;
  contact_name?: string;
  stage_name?: string;
}

interface TranscriptionSegment {
  speaker: string;
  start: number;
  end: number;
  text: string;
}

interface TranscriptionItem {
  id: string;
  account_id: string;
  call_id: string;
  deal_id?: string;
  full_text: string;
  language: string;
  model_name: string;
  duration_seconds: number;
  speakers_detected: number;
  segments: TranscriptionSegment[];
  created_at: string;
}

interface RagQueryResponse {
  query: string;
  matched: boolean;
  similarity_score: number;
  source_manual?: string;
  page_number?: number;
  implant_line?: string;
  bone_type?: string;
  recommended_implant_torque_ncm?: number;
  recommended_prosthetic_torque_ncm?: number;
  drill_sequence: string[];
  content_chunk?: string;
  answer: string;
}

interface SokResponse {
  agreement_id: string;
  sok_score: number;
  is_idle: boolean;
  days_without_surgery: number;
  contract_limit_days: number;
  kit_immobilized_value: number;
  avg_monthly_revenue: number;
  status: string;
  recommendation: string;
  dentgo_reverse_pickup_suggested: boolean;
  calculated_at: string;
}

interface PrResponse {
  agreement_id: string;
  pr_score: number;
  current_stock: number;
  replenishment_needed: boolean;
  deal_id?: string;
  deal_title?: string;
  whatsapp_sent: boolean;
  recommendation: string;
  calculated_at: string;
}

interface MarginResponse {
  id: string;
  procedure_name: string;
  gross_revenue: float;
  supplies_cost: float;
  lab_cost: float;
  surgeon_fee: float;
  chair_hours: float;
  chair_hour_cost: float;
  total_chair_cost: float;
  tax_rate_percent: float;
  tax_amount: float;
  total_cost: float;
  net_margin_value: float;
  net_margin_percent: float;
  is_low_margin: boolean;
  status: string;
  recommendation: string;
  clinic_id?: string;
  calculated_at: string;
}

type float = number;

interface HscResponse {
  id: string;
  partner_id: string;
  partner_name: string;
  f_cirurgica: number;
  g_consignado: number;
  s_atendimento: number;
  e_canal: number;
  hsc_score: number;
  classification: string;
  rescue_task_id?: string;
  dentgo_voucher_code?: string;
  upsell_eligible: boolean;
  mgm_eligible: boolean;
  recommendation: string;
}

export const IntelligenceSuiteWorkspace: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>("copilot");

  // Global Deals
  const [deals, setDeals] = useState<DealItem[]>([]);
  const [selectedDealId, setSelectedDealId] = useState<string>("");
  const [dealsLoading, setDealsLoading] = useState<boolean>(true);

  // Tab 1: Whisper & Transcriptions
  const [transcriptions, setTranscriptions] = useState<TranscriptionItem[]>([]);
  const [selectedTranscription, setSelectedTranscription] = useState<TranscriptionItem | null>(null);
  const [pttCallId, setPttCallId] = useState<string>("call-field-01");
  const [pttDialogue, setPttDialogue] = useState<string>(
    "Dr. Marcelo confirmou que precisa de 12 implantes Cone Morse 3.75x11 e 4 cicatrizadores para cirurgia de sexta-feira."
  );
  const [pttDuration, setPttDuration] = useState<number>(45.5);
  const [pttRecording, setPttRecording] = useState<boolean>(false);
  const [pttRecordError, setPttRecordError] = useState<string | null>(null);
  const [recordedAudios, setRecordedAudios] = useState<Record<string, string>>({});
  const pttRecorderRef = React.useRef<MediaRecorder | null>(null);
  const pttChunksRef = React.useRef<Blob[]>([]);
  const pttRecognitionRef = React.useRef<any>(null);
  const pttStartedAtRef = React.useRef<number>(0);
  const [pttProcessing, setPttProcessing] = useState<boolean>(false);
  const [pttFeedback, setPttFeedback] = useState<string | null>(null);

  // Tab 2: Catalog RAG
  const [ragQuery, setRagQuery] = useState<string>("Qual o torque recomendado e fresagem para osso Tipo II?");
  const [ragBoneType, setRagBoneType] = useState<string>("Tipo II");
  const [ragMinSim, setRagMinSim] = useState<number>(0.65);
  const [ragQueryLoading, setRagQueryLoading] = useState<boolean>(false);
  const [ragResult, setRagResult] = useState<RagQueryResponse | null>(null);
  // TICKET-INTEL-01/02: copiar resposta RAG
  const [copiedRag, setCopiedRag] = useState<boolean>(false);

  // RAG Ingestion
  const [ingestManual, setIngestManual] = useState<string>("Catálogo Cirúrgico Cone Morse 2026");
  const [ingestPage, setIngestPage] = useState<number>(14);
  const [ingestLine, setIngestLine] = useState<string>("Cone Morse Active");
  const [ingestBone, setIngestBone] = useState<string>("Tipo II");
  const [ingestChunk, setIngestChunk] = useState<string>(
    "Protocolo cirúrgico para osso medular Tipo II: fresa lança 2.0, piloto 2/3, fresa 3.5. Torque cirúrgico limite de 45 N.cm e torque protético de 20 N.cm."
  );
  const [ingestDrills, setIngestDrills] = useState<string>("Lança 2.0, Piloto 2/3, Cônica 3.5");
  const [ingestImplantTorque, setIngestImplantTorque] = useState<number>(45.0);
  const [ingestProsthTorque, setIngestProsthTorque] = useState<number>(20.0);
  const [ingestLoading, setIngestLoading] = useState<boolean>(false);
  const [ingestFeedback, setIngestFeedback] = useState<string | null>(null);

  // Tab 3: SOK & PR
  const [sokAgreementId, setSokAgreementId] = useState<string>("agr-01");
  const [sokDaysWithoutSurgery, setSokDaysWithoutSurgery] = useState<number>(35);
  const [sokContractLimitDays, setSokContractLimitDays] = useState<number>(30);
  const [sokImmobilizedValue, setSokImmobilizedValue] = useState<number>(28000);
  const [sokAvgRevenue, setSokAvgRevenue] = useState<number>(15000);
  const [sokLoading, setSokLoading] = useState<boolean>(false);
  const [sokResult, setSokResult] = useState<SokResponse | null>(null);

  const [prAgreementId, setPrAgreementId] = useState<string>("agr-01");
  const [prDailyConsumption, setPrDailyConsumption] = useState<number>(1.2);
  const [prLeadTime, setPrLeadTime] = useState<number>(2.0);
  const [prSafetyStock, setPrSafetyStock] = useState<number>(5.0);
  const [prCurrentStock, setPrCurrentStock] = useState<number>(6);
  const [prLoading, setPrLoading] = useState<boolean>(false);
  const [prResult, setPrResult] = useState<PrResponse | null>(null);

  const [invReportAgreementId, setInvReportAgreementId] = useState<string>("agr-01");
  const [invReportData, setInvReportData] = useState<any | null>(null);
  const [invReportLoading, setInvReportLoading] = useState<boolean>(false);

  // Tab 4: Margin
  const [marginProcedure, setMarginProcedure] = useState<string>("Protocolo All-on-4 Superior");
  const [marginRevenue, setMarginRevenue] = useState<number>(18000);
  const [marginSupplies, setMarginSupplies] = useState<number>(3800);
  const [marginLab, setMarginLab] = useState<number>(2200);
  const [marginSurgeon, setMarginSurgeon] = useState<number>(4000);
  const [marginChairHours, setMarginChairHours] = useState<number>(4.0);
  const [marginChairHourCost, setMarginChairHourCost] = useState<number>(250);
  const [marginTaxRate, setMarginTaxRate] = useState<number>(10.0);
  const [marginClinicId, setMarginClinicId] = useState<string>("clinic-sp-01");
  const [marginLoading, setMarginLoading] = useState<boolean>(false);
  const [marginResult, setMarginResult] = useState<MarginResponse | null>(null);

  const [marginSummaryClinicId, setMarginSummaryClinicId] = useState<string>("clinic-sp-01");
  const [marginSummaryData, setMarginSummaryData] = useState<any | null>(null);
  const [marginSummaryLoading, setMarginSummaryLoading] = useState<boolean>(false);

  // Tab 5: Health Score
  const [hscPartnerId, setHscPartnerId] = useState<string>("cnt-01");
  const [hscPartnerName, setHscPartnerName] = useState<string>("Dr. Roberto Silveira");
  const [hscFCirurgica, setHscFCirurgica] = useState<number>(85);
  const [hscGConsignado, setHscGConsignado] = useState<number>(70);
  const [hscSAtendimento, setHscSAtendimento] = useState<number>(90);
  const [hscECanal, setHscECanal] = useState<number>(80);
  const [hscLoading, setHscLoading] = useState<boolean>(false);
  const [hscResult, setHscResult] = useState<HscResponse | null>(null);

  const [hscHistoryPartnerId, setHscHistoryPartnerId] = useState<string>("cnt-01");
  const [hscHistoryData, setHscHistoryData] = useState<any | null>(null);
  const [hscHistoryLoading, setHscHistoryLoading] = useState<boolean>(false);

  // Fetch Deals
  const fetchDeals = useCallback(async () => {
    setDealsLoading(true);
    try {
      const res = await fetch("/api/v1/deals");
      if (res.ok) {
        const data = await res.json();
        const list = Array.isArray(data) ? data : (Array.isArray(data?.deals) ? data.deals : []);
        setDeals(list);
        if (list.length > 0 && !selectedDealId) {
          setSelectedDealId(list[0].id);
        }
      }
    } catch {
      // Fallback
    } finally {
      setDealsLoading(false);
    }
  }, [selectedDealId]);

  // Fetch deal transcriptions
  const fetchDealTranscriptions = useCallback(async (dealId: string) => {
    if (!dealId) return;
    try {
      const res = await fetch(`/api/v1/intelligence/transcriptions/deal/${dealId}`);
      if (res.ok) {
        const data = await res.json();
        const list = Array.isArray(data) ? data : [];
        setTranscriptions(list);
        if (list.length > 0) {
          setSelectedTranscription(list[0]);
        } else {
          setSelectedTranscription(null);
        }
      }
    } catch {
      // Fallback
    }
  }, []);

  useEffect(() => {
    fetchDeals();
  }, [fetchDeals]);

  useEffect(() => {
    if (selectedDealId) {
      fetchDealTranscriptions(selectedDealId);
    }
  }, [selectedDealId, fetchDealTranscriptions]);

  // Gravação de voz no microfone (PTT): MediaRecorder + SpeechRecognition (pt-BR)
  const handleTogglePttRecording = async () => {
    setPttRecordError(null);
    if (pttRecording) {
      pttRecognitionRef.current?.stop?.();
      pttRecorderRef.current?.stop();
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      pttChunksRef.current = [];
      pttStartedAtRef.current = Date.now();
      const callKey = pttCallId;
      recorder.ondataavailable = (ev) => {
        if (ev.data.size > 0) pttChunksRef.current.push(ev.data);
      };
      recorder.onstop = () => {
        stream.getTracks().forEach((t) => t.stop());
        setPttRecording(false);
        const blob = new Blob(pttChunksRef.current, { type: recorder.mimeType || "audio/webm" });
        const url = URL.createObjectURL(blob);
        setRecordedAudios((prev) => ({ ...prev, [callKey]: url }));
        setPttDuration(Math.max(1, Math.round((Date.now() - pttStartedAtRef.current) / 100) / 10));
      };
      pttRecorderRef.current = recorder;

      const SR = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SR) {
        const rec = new SR();
        rec.lang = "pt-BR";
        rec.continuous = true;
        rec.interimResults = false;
        rec.onresult = (ev: any) => {
          let text = "";
          for (let i = ev.resultIndex; i < ev.results.length; i++) {
            if (ev.results[i].isFinal) text += `${ev.results[i][0].transcript} `;
          }
          if (text.trim()) setPttDialogue((prev) => `${prev ? `${prev}\n` : ""}${text.trim()}`);
        };
        rec.onerror = () => {
          setPttRecordError("Reconhecimento de fala indisponível; digite a transcrição manualmente.");
        };
        pttRecognitionRef.current = rec;
        setPttDialogue("");
        rec.start();
      } else {
        setPttRecordError("SpeechRecognition não suportado neste navegador; o áudio será gravado sem transcrição automática.");
      }

      recorder.start();
      setPttRecording(true);
    } catch {
      setPttRecordError("Microfone indisponível ou permissão negada.");
    }
  };

  // Handle Process Transcription
  const handleProcessPtt = async () => {
    if (!pttCallId.trim() || !pttDialogue.trim()) return;
    setPttProcessing(true);
    setPttFeedback(null);
    try {
      const res = await fetch("/api/v1/intelligence/transcriptions/process", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          call_id: pttCallId,
          dialogue_text: pttDialogue,
          duration_seconds: pttDuration,
          account_id: "0f14ffff",
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setPttFeedback(`Transcrição ${data.transcription_id} gerada com ${data.speakers_count} oradores.`);
        if (selectedDealId) {
          fetchDealTranscriptions(selectedDealId);
        }
      } else {
        setPttFeedback("Erro no processamento da transcrição.");
      }
    } catch (e: any) {
      setPttFeedback(`Falha de rede: ${e.message}`);
    } finally {
      setPttProcessing(false);
    }
  };

  // Handle RAG Query
  const handleRagQuery = async () => {
    if (!ragQuery.trim()) return;
    setRagQueryLoading(true);
    try {
      const res = await fetch("/api/v1/intelligence/catalog-rag/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: ragQuery,
          bone_type: ragBoneType || undefined,
          min_similarity: ragMinSim,
          account_id: "0f14ffff",
        }),
      });
      if (res.ok) {
        const data: RagQueryResponse = await res.json();
        setRagResult(data);
      }
    } catch {
      // Erro
    } finally {
      setRagQueryLoading(false);
    }
  };

  // Handle RAG Ingestion
  const handleRagIngest = async () => {
    if (!ingestManual.trim() || !ingestChunk.trim()) return;
    setIngestLoading(true);
    setIngestFeedback(null);
    try {
      const drills = ingestDrills
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
      const res = await fetch("/api/v1/intelligence/catalog-rag/ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source_manual: ingestManual,
          page_number: Number(ingestPage),
          implant_line: ingestLine,
          bone_type: ingestBone,
          content_chunk: ingestChunk,
          drill_sequence: drills,
          recommended_implant_torque_ncm: Number(ingestImplantTorque),
          recommended_prosthetic_torque_ncm: Number(ingestProsthTorque),
          account_id: "0f14ffff",
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setIngestFeedback(`Fragmento ${data.chunk_id} indexado com ${data.vector_dimensions} dimensões vetoriais.`);
      } else {
        setIngestFeedback("Erro ao indexar fragmento no catálogo vetorial.");
      }
    } catch (e: any) {
      setIngestFeedback(`Falha: ${e.message}`);
    } finally {
      setIngestLoading(false);
    }
  };

  // Handle SOK Calculation
  const handleCalculateSok = async () => {
    setSokLoading(true);
    try {
      const res = await fetch("/api/v1/intelligence/inventory/sok", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          agreement_id: sokAgreementId,
          days_without_surgery: Number(sokDaysWithoutSurgery),
          contract_limit_days: Number(sokContractLimitDays),
          kit_immobilized_value: Number(sokImmobilizedValue),
          avg_monthly_revenue: Number(sokAvgRevenue),
          account_id: "0f14ffff",
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setSokResult(data);
      }
    } catch {
      // erro
    } finally {
      setSokLoading(false);
    }
  };

  // Handle PR Calculation
  const handleCalculatePr = async () => {
    setPrLoading(true);
    try {
      const res = await fetch("/api/v1/intelligence/inventory/pr", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          agreement_id: prAgreementId,
          avg_daily_consumption: Number(prDailyConsumption),
          delivery_lead_time_days: Number(prLeadTime),
          safety_stock: Number(prSafetyStock),
          current_stock: Number(prCurrentStock),
          trigger_deal: true,
          account_id: "0f14ffff",
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setPrResult(data);
      }
    } catch {
      // erro
    } finally {
      setPrLoading(false);
    }
  };

  // Handle Inventory Report
  const handleFetchInvReport = async () => {
    if (!invReportAgreementId) return;
    setInvReportLoading(true);
    try {
      const res = await fetch(`/api/v1/intelligence/inventory/report/${invReportAgreementId}?account_id=0f14ffff`);
      if (res.ok) {
        const data = await res.json();
        setInvReportData(data);
      }
    } catch {
      // erro
    } finally {
      setInvReportLoading(false);
    }
  };

  // Handle Margin Calculation
  const handleCalculateMargin = async () => {
    setMarginLoading(true);
    try {
      const res = await fetch("/api/v1/intelligence/margin/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          procedure_name: marginProcedure,
          gross_revenue: Number(marginRevenue),
          supplies_cost: Number(marginSupplies),
          lab_cost: Number(marginLab),
          surgeon_fee: Number(marginSurgeon),
          chair_hours: Number(marginChairHours),
          chair_hour_cost: Number(marginChairHourCost),
          tax_rate_percent: Number(marginTaxRate),
          clinic_id: marginClinicId,
          account_id: "0f14ffff",
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setMarginResult(data);
      }
    } catch {
      // erro
    } finally {
      setMarginLoading(false);
    }
  };

  // Handle Clinic Margin Summary
  const handleFetchMarginSummary = async () => {
    if (!marginSummaryClinicId) return;
    setMarginSummaryLoading(true);
    try {
      const res = await fetch(`/api/v1/intelligence/margin/summary/${marginSummaryClinicId}?account_id=0f14ffff`);
      if (res.ok) {
        const data = await res.json();
        setMarginSummaryData(data);
      }
    } catch {
      // erro
    } finally {
      setMarginSummaryLoading(false);
    }
  };

  // Handle Health Score Calculation
  const handleCalculateHsc = async () => {
    setHscLoading(true);
    try {
      const res = await fetch("/api/v1/intelligence/health-score/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          partner_id: hscPartnerId,
          partner_name: hscPartnerName,
          f_cirurgica: Number(hscFCirurgica),
          g_consignado: Number(hscGConsignado),
          s_atendimento: Number(hscSAtendimento),
          e_canal: Number(hscECanal),
          account_id: "0f14ffff",
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setHscResult(data);
      }
    } catch {
      // erro
    } finally {
      setHscLoading(false);
    }
  };

  // Handle HSC History
  const handleFetchHscHistory = async () => {
    if (!hscHistoryPartnerId) return;
    setHscHistoryLoading(true);
    try {
      const res = await fetch(`/api/v1/intelligence/health-score/history/${hscHistoryPartnerId}?account_id=0f14ffff`);
      if (res.ok) {
        const data = await res.json();
        setHscHistoryData(data);
      }
    } catch {
      // erro
    } finally {
      setHscHistoryLoading(false);
    }
  };

  const tabsConfig = [
    { id: "copilot", label: "Resumo Automático de Reuniões e Áudios" },
    { id: "rag", label: "Assistente Cirúrgico Inteligente" },
    { id: "inventory", label: "Maletas Paradas e Reposição Automática" },
    { id: "margin", label: "Margem Líquida Clínica" },
    { id: "health_score", label: "Índice de Saúde do Cliente" },
  ];

  const [intelExportFormat, setIntelExportFormat] = React.useState<"csv" | "parquet">("csv");
  const [isExportingIntel, setIsExportingIntel] = React.useState<boolean>(false);

  const handleExportIntelDataset = async () => {
    setIsExportingIntel(true);
    try {
      const res = await fetch("/api/v1/intelligence/bi/export-dataset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          dataset_name: "deals_funnel",
          format: intelExportFormat,
          user_id: "usr-director-br",
          account_id: "0f14ffff",
        }),
      });
      if (!res.ok) throw new Error("Erro ao exportar dataset de inteligência.");
      const data = await res.json();
      if (data.download_url) {
        window.open(data.download_url, "_blank");
      }
    } catch (err: any) {
      console.error(err);
    } finally {
      setIsExportingIntel(false);
    }
  };

  return (
    <div className="w-full space-y-6 font-sans text-text-main">
      <RouteHeader
        title="Assistente Inteligente & Análise Preditiva"
        description="Resumos de Reuniões, Consulta de Protocolos, Controle de Maletas Paradas e Rentabilidade de Clínicas."
        badge={
          <span className="inline-flex items-center gap-1.5 px-3 py-1 text-xs font-semibold rounded-full bg-status-success-subtle text-status-success border border-status-success/20">
            <ShieldCheck className="w-3.5 h-3.5" />
            7 Motores Ativos
          </span>
        }
        exportConfig={{
          format: intelExportFormat,
          onFormatChange: (fmt) => setIntelExportFormat(fmt as "csv" | "parquet"),
          onExport: handleExportIntelDataset,
          loading: isExportingIntel,
          label: "FORMATO",
          exportLabel: "Exportar",
        }}
        actions={[
          {
            id: "market-intel",
            label: "Radar de Mercado",
            variant: "outline",
            icon: <Radar className="w-3.5 h-3.5" />,
            title: "Abrir Inteligência de Mercado & Radar de Concorrência",
            onClick: () => {
              window.location.hash = "#!/market_intel";
            },
          },
          {
            id: "refresh",
            label: "Atualizar",
            variant: "outline",
            icon: <RefreshCw className="w-3.5 h-3.5" />,
            title: "Atualizar Indicadores",
            onClick: fetchDeals,
          },
        ]}
      />

      {/* Tabs Navigation */}
      <Tabs tabs={tabsConfig} activeTab={activeTab} onChange={setActiveTab} />

      {/* TAB 1: Copiloto Granola & Whisper */}
      {activeTab === "copilot" && (
        <div className="space-y-6">
          {/* Deal Selector Bar */}
          <div className="bg-surface-card border border-border rounded-xl p-4 shadow-card flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-navy-subtle text-brand-navy shrink-0">
                <Database className="h-4 w-4" />
              </div>
              <div>
                <span className="text-xs font-semibold text-text-main block">Deal Comercial Ativo:</span>
                <span className="text-[11px] text-text-secondary">
                  Selecione a oportunidade para sincronizar transcrições e extração Granola
                </span>
              </div>
            </div>
            <div className="w-full md:w-80">
              {dealsLoading ? (
                <Skeleton className="h-9 w-full" />
              ) : (
                <select
                  value={selectedDealId}
                  onChange={(e) => setSelectedDealId(e.target.value)}
                  className="w-full rounded-lg border border-border bg-surface-bg px-3 py-2 text-xs text-text-main font-medium focus:border-brand-primary focus:outline-none focus:ring-1 focus:ring-brand-primary"
                >
                  {deals.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.id} • {d.title} ({d.company || "Empresa"})
                    </option>
                  ))}
                </select>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left: Granola Copilot Zero-Touch */}
            <div className="space-y-4">
              <GranolaCopilotCard
                dealId={selectedDealId}
                onApplySuccess={() => fetchDealTranscriptions(selectedDealId)}
              />
            </div>

            {/* Right: Whisper PTT Processor & Transcriptions History */}
            <div className="space-y-6">
              {/* PTT Processor Card */}
              <div className="bg-surface-card border border-border rounded-2xl p-5 shadow-card space-y-4">
                <div className="flex items-center justify-between border-b border-border pb-3">
                  <div className="flex items-center space-x-2.5">
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-primary-subtle text-brand-primary">
                      <Cpu className="h-4 w-4" />
                    </div>
                    <div>
                      <h4 className="text-sm font-semibold tracking-tight text-text-main">
                        Processador Whisper & Diarização PTT
                      </h4>
                      <p className="text-xs text-text-secondary">
                        Pipeline de diarização e estenotipia cirúrgica Faster-Whisper
                      </p>
                    </div>
                  </div>
                  <span className="text-[10px] font-mono bg-surface-bg px-2 py-0.5 rounded text-text-muted border border-border">
                    POST /transcriptions/process
                  </span>
                </div>

                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="text-xs font-medium text-text-secondary block mb-1">Call ID / Gravação</label>
                      <input
                        type="text"
                        value={pttCallId}
                        onChange={(e) => setPttCallId(e.target.value)}
                        className="w-full rounded-lg border border-border bg-surface-bg px-3 py-1.5 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary"
                      />
                    </div>
                    <div>
                      <label className="text-xs font-medium text-text-secondary block mb-1">Duração (segundos)</label>
                      <input
                        type="number"
                        value={pttDuration}
                        onChange={(e) => setPttDuration(Number(e.target.value))}
                        className="w-full rounded-lg border border-border bg-surface-bg px-3 py-1.5 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="text-xs font-medium text-text-secondary block mb-1">
                      Diálogo de Áudio / Nota de Voz de Campo
                    </label>
                    <textarea
                      rows={3}
                      value={pttDialogue}
                      onChange={(e) => setPttDialogue(e.target.value)}
                      placeholder="Transcrição do áudio..."
                      className="w-full rounded-lg border border-border bg-surface-bg p-2.5 text-xs text-text-main placeholder:text-text-muted focus:outline-none focus:ring-1 focus:ring-brand-primary"
                    />
                  </div>

                  <div className="space-y-2">
                    <Button
                      type="button"
                      size="sm"
                      variant={pttRecording ? "default" : "outline"}
                      onClick={handleTogglePttRecording}
                      className="gap-1.5"
                    >
                      {pttRecording ? (
                        <Square className="w-3.5 h-3.5 text-status-danger" />
                      ) : (
                        <Mic className="w-3.5 h-3.5 text-brand-primary" />
                      )}
                      {pttRecording ? "Parar Gravação" : "Gravar Voz no Microfone (PTT)"}
                    </Button>
                    {pttRecordError && <p className="text-[11px] text-status-warning">{pttRecordError}</p>}
                    {recordedAudios[pttCallId] && (
                      <audio controls src={recordedAudios[pttCallId]} className="w-full h-8" />
                    )}
                  </div>

                  <div className="flex items-center justify-between pt-1">
                    {pttFeedback ? (
                      <span className="text-xs text-status-success font-medium">{pttFeedback}</span>
                    ) : (
                      <span className="text-xs text-text-muted">Modelo faster-whisper-medium pronto</span>
                    )}
                    <Button
                      size="sm"
                      onClick={handleProcessPtt}
                      disabled={pttProcessing || !pttDialogue.trim()}
                      className="gap-1.5"
                    >
                      <Sparkles className="w-3.5 h-3.5" />
                      {pttProcessing ? "Processando..." : "Processar Áudio PTT"}
                    </Button>
                  </div>
                </div>
              </div>

              {/* Deal Transcriptions List */}
              <div className="bg-surface-card border border-border rounded-2xl p-5 shadow-card space-y-3">
                <div className="flex items-center justify-between border-b border-border pb-2.5">
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-brand-primary" />
                    <h4 className="text-xs font-bold uppercase tracking-wider text-text-main">
                      Transcrições Gravadas do Deal ({transcriptions.length})
                    </h4>
                  </div>
                  <span className="text-[11px] font-mono text-brand-primary">{selectedDealId}</span>
                </div>

                {transcriptions.length === 0 ? (
                  <div className="py-6 text-center text-xs text-text-muted border border-dashed border-border rounded-xl">
                    Nenhuma transcrição associada ao Deal selecionado.
                  </div>
                ) : (
                  <div className="space-y-2 max-h-56 overflow-y-auto">
                    {transcriptions.map((t) => (
                      <div
                        key={t.id}
                        onClick={() => setSelectedTranscription(t)}
                        className={`p-3 rounded-lg border transition-all cursor-pointer ${
                          selectedTranscription?.id === t.id
                            ? "bg-surface-bg border-brand-primary shadow-card"
                            : "bg-surface-bg border-border hover:border-brand-primary/40"
                        }`}
                      >
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-mono text-xs text-brand-primary font-semibold">{t.id}</span>
                          <span className="text-[10px] text-text-muted font-mono">{t.created_at}</span>
                        </div>
                        <p className="text-xs text-text-secondary line-clamp-2">{t.full_text}</p>
                        {recordedAudios[t.call_id] && (
                          <audio
                            controls
                            src={recordedAudios[t.call_id]}
                            onClick={(e) => e.stopPropagation()}
                            className="w-full h-8 mt-2"
                          />
                        )}
                        <div className="flex items-center gap-3 mt-2 text-[10px] text-text-muted font-mono">
                          <span>Oradores: {t.speakers_detected}</span>
                          <span>Duração: {t.duration_seconds}s</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {selectedTranscription && (
                  <div className="mt-3 p-3 bg-surface-bg rounded-xl border border-border space-y-2">
                    <span className="text-xs font-semibold text-text-main block">
                      Segmentos Diarizados ({selectedTranscription.id}):
                    </span>
                    <div className="space-y-1.5 max-h-36 overflow-y-auto text-xs">
                      {selectedTranscription.segments && selectedTranscription.segments.length > 0 ? (
                        selectedTranscription.segments.map((seg, i) => (
                          <div key={i} className="p-2 rounded bg-surface-card border border-border">
                            <span className="font-semibold text-brand-primary text-[11px] block">{seg.speaker}:</span>
                            <span className="text-text-secondary">{seg.text}</span>
                          </div>
                        ))
                      ) : (
                        <p className="text-text-secondary">{selectedTranscription.full_text}</p>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: Assistente RAG Cirúrgico */}
      {activeTab === "rag" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Query Console */}
          <div className="bg-surface-card border border-border rounded-2xl p-5 shadow-card space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <div className="flex items-center gap-2.5">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-primary-subtle text-brand-primary">
                  <Search className="h-4 w-4" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-text-main">
                    Consulta Semântica RAG (Protocolos de Fresagem & Torque)
                  </h3>
                  <p className="text-xs text-text-secondary">
                    Busca por similaridade de cosseno com embeddings de catálogos cirúrgicos ANVISA
                  </p>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <div>
                <label className="text-xs font-medium text-text-secondary block mb-1">
                  Pergunta Cirúrgica / Protocolo
                </label>
                <textarea
                  rows={2}
                  value={ragQuery}
                  onChange={(e) => setRagQuery(e.target.value)}
                  placeholder="Ex: Qual o torque de inserção e sequência de brocas para osso Tipo II?"
                  className="w-full rounded-lg border border-border bg-surface-bg p-2.5 text-xs text-text-main placeholder:text-text-muted focus:outline-none focus:ring-1 focus:ring-brand-primary"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-medium text-text-secondary block mb-1">Filtro Classificação Óssea</label>
                  <select
                    value={ragBoneType}
                    onChange={(e) => setRagBoneType(e.target.value)}
                    className="w-full rounded-lg border border-border bg-surface-bg px-2.5 py-1.5 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary"
                  >
                    <option value="">Todos os Tipos</option>
                    <option value="Tipo I">Tipo I (Cortical denso)</option>
                    <option value="Tipo II">Tipo II (Medular denso)</option>
                    <option value="Tipo III">Tipo III (Trabeculado fino)</option>
                    <option value="Tipo IV">Tipo IV (Muito esponjoso)</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs font-medium text-text-secondary block mb-1">
                    Similaridade Mínima ({ragMinSim})
                  </label>
                  <input
                    type="range"
                    min="0.5"
                    max="0.95"
                    step="0.05"
                    value={ragMinSim}
                    onChange={(e) => setRagMinSim(Number(e.target.value))}
                    className="w-full mt-2"
                  />
                </div>
              </div>

              <Button
                size="sm"
                onClick={handleRagQuery}
                disabled={ragQueryLoading || !ragQuery.trim()}
                className="w-full gap-1.5"
              >
                <Search className="w-3.5 h-3.5" />
                {ragQueryLoading ? "Consultando Catálogo..." : "Consultar Copiloto RAG"}
              </Button>
            </div>

            {ragResult && (
              <div className="mt-4 p-4 rounded-xl border border-border bg-surface-bg space-y-3">
                <div className="flex items-center justify-between border-b border-border pb-2">
                  <span className="text-xs font-semibold text-text-main">Resultado da Consulta</span>
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => {
                        const text = ragResult.answer || "";
                        if (navigator.clipboard?.writeText) {
                          navigator.clipboard.writeText(text).catch(() => {});
                        }
                        setCopiedRag(true);
                        setTimeout(() => setCopiedRag(false), 2000);
                      }}
                      className="text-[10px] px-2 py-1 rounded border border-brand-primary/30 bg-brand-primary-subtle text-brand-primary hover:bg-brand-primary hover:text-text-inverse transition-colors"
                    >
                      {copiedRag ? "Copiado" : "Copiar Resposta para o Chat"}
                    </button>
                    <span
                      className={`text-[10px] font-mono px-2 py-0.5 rounded-full ${
                        ragResult.matched
                          ? "bg-status-success-subtle text-status-success border border-status-success/20"
                          : "bg-status-warning-subtle text-status-warning border border-status-warning/20"
                      }`}
                    >
                      Similaridade: {(ragResult.similarity_score * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>

                <div className="text-xs text-text-secondary bg-surface-card p-3 rounded-lg border border-border">
                  <span className="font-semibold text-text-main block mb-1">Recomendação Clínica:</span>
                  <p className="whitespace-pre-line leading-relaxed">{ragResult.answer}</p>
                </div>

                {ragResult.drill_sequence && ragResult.drill_sequence.length > 0 && (
                  <div>
                    <span className="text-[11px] font-semibold text-text-secondary block mb-1.5 uppercase tracking-wider">
                      Sequência de Fresagem / Brocas:
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {ragResult.drill_sequence.map((drill, idx) => (
                        <span
                          key={idx}
                          className="inline-flex items-center gap-1 rounded bg-brand-primary-subtle px-2 py-0.5 text-xs font-mono font-medium text-brand-primary border border-brand-primary/20"
                        >
                          <ChevronRight className="w-3 h-3" />
                          {drill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <div className="grid grid-cols-2 gap-2 text-xs">
                  {ragResult.recommended_implant_torque_ncm !== undefined && (
                    <div className="p-2 bg-surface-card rounded border border-border">
                      <span className="text-text-muted text-[10px] block">Torque de Inserção:</span>
                      <span className="font-mono font-bold text-status-success">
                        {ragResult.recommended_implant_torque_ncm} N.cm
                      </span>
                    </div>
                  )}
                  {ragResult.recommended_prosthetic_torque_ncm !== undefined && (
                    <div className="p-2 bg-surface-card rounded border border-border">
                      <span className="text-text-muted text-[10px] block">Torque Protético:</span>
                      <span className="font-mono font-bold text-brand-navy">
                        {ragResult.recommended_prosthetic_torque_ncm} N.cm
                      </span>
                    </div>
                  )}
                </div>

                {ragResult.source_manual && (
                  <div className="text-[11px] text-text-muted font-mono flex items-center justify-between">
                    <span>Manual: {ragResult.source_manual}</span>
                    <span>Pág: {ragResult.page_number}</span>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Ingestion Console */}
          <div className="bg-surface-card border border-border rounded-2xl p-5 shadow-card space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <div className="flex items-center gap-2.5">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-navy-subtle text-brand-navy">
                  <Database className="h-4 w-4" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-text-main">
                    Ingestão de Fragmento no Catálogo Vetorial
                  </h3>
                  <p className="text-xs text-text-secondary">
                    Cadastre novos manuais técnicos com vetorização semântica automática
                  </p>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <div className="grid grid-cols-3 gap-2">
                <div className="col-span-2">
                  <label className="text-xs font-medium text-text-secondary block mb-1">Manual / Catálogo</label>
                  <input
                    type="text"
                    value={ingestManual}
                    onChange={(e) => setIngestManual(e.target.value)}
                    className="w-full rounded-lg border border-border bg-surface-bg px-2.5 py-1.5 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary"
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-text-secondary block mb-1">Página</label>
                  <input
                    type="number"
                    value={ingestPage}
                    onChange={(e) => setIngestPage(Number(e.target.value))}
                    className="w-full rounded-lg border border-border bg-surface-bg px-2.5 py-1.5 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-xs font-medium text-text-secondary block mb-1">Linha do Implante</label>
                  <input
                    type="text"
                    value={ingestLine}
                    onChange={(e) => setIngestLine(e.target.value)}
                    className="w-full rounded-lg border border-border bg-surface-bg px-2.5 py-1.5 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary"
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-text-secondary block mb-1">Classificação Óssea</label>
                  <input
                    type="text"
                    value={ingestBone}
                    onChange={(e) => setIngestBone(e.target.value)}
                    className="w-full rounded-lg border border-border bg-surface-bg px-2.5 py-1.5 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-medium text-text-secondary block mb-1">
                  Texto Técnico do Fragmento
                </label>
                <textarea
                  rows={3}
                  value={ingestChunk}
                  onChange={(e) => setIngestChunk(e.target.value)}
                  className="w-full rounded-lg border border-border bg-surface-bg p-2 text-xs text-text-main placeholder:text-text-muted focus:outline-none focus:ring-1 focus:ring-brand-primary"
                />
              </div>

              <div>
                <label className="text-xs font-medium text-text-secondary block mb-1">
                  Sequência de Brocas (separadas por vírgula)
                </label>
                <input
                  type="text"
                  value={ingestDrills}
                  onChange={(e) => setIngestDrills(e.target.value)}
                  className="w-full rounded-lg border border-border bg-surface-bg px-2.5 py-1.5 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-xs font-medium text-text-secondary block mb-1">Torque Implante (N.cm)</label>
                  <input
                    type="number"
                    value={ingestImplantTorque}
                    onChange={(e) => setIngestImplantTorque(Number(e.target.value))}
                    className="w-full rounded-lg border border-border bg-surface-bg px-2.5 py-1.5 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary"
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-text-secondary block mb-1">Torque Protético (N.cm)</label>
                  <input
                    type="number"
                    value={ingestProsthTorque}
                    onChange={(e) => setIngestProsthTorque(Number(e.target.value))}
                    className="w-full rounded-lg border border-border bg-surface-bg px-2.5 py-1.5 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary"
                  />
                </div>
              </div>

              <div className="flex items-center justify-between pt-1">
                {ingestFeedback ? (
                  <span className="text-xs text-status-success font-medium">{ingestFeedback}</span>
                ) : (
                  <span className="text-xs text-text-muted">Pronto para vetorização</span>
                )}
                <Button
                  size="sm"
                  variant="outline"
                  onClick={handleRagIngest}
                  disabled={ingestLoading || !ingestChunk.trim()}
                  className="gap-1.5"
                >
                  <Plus className="w-3.5 h-3.5" />
                  {ingestLoading ? "Ingerindo..." : "Ingestar Fragmento"}
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: Estoque Preditivo SOK & PR */}
      {activeTab === "inventory" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* SOK: Score de Ociosidade de Kit */}
            <div className="bg-surface-card border border-border rounded-2xl p-5 shadow-card space-y-4">
              <div className="flex items-center justify-between border-b border-border pb-3">
                <div className="flex items-center gap-2.5">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-status-warning-subtle text-status-warning">
                    <Layers className="h-4 w-4" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-text-main">
                      Score de Ociosidade de Kit Consignado (SOK)
                    </h3>
                    <p className="text-xs text-text-secondary">
                      SOK = (D_sem_cirurgia / D_limite) * 0.6 + (V_kit / V_fat_medio) * 0.4
                    </p>
                  </div>
                </div>
                <span className="text-[10px] font-mono bg-surface-bg px-2 py-0.5 rounded text-text-muted border border-border">
                  POST /inventory/sok
                </span>
              </div>

              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs font-medium text-text-secondary block mb-1">ID do Acordo (Agreement)</label>
                    <input
                      type="text"
                      value={sokAgreementId}
                      onChange={(e) => setSokAgreementId(e.target.value)}
                      className="w-full rounded-lg border border-border bg-surface-bg px-2.5 py-1.5 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-medium text-text-secondary block mb-1">Dias sem Cirurgia</label>
                    <input
                      type="number"
                      value={sokDaysWithoutSurgery}
                      onChange={(e) => setSokDaysWithoutSurgery(Number(e.target.value))}
                      className="w-full rounded-lg border border-border bg-surface-bg px-2.5 py-1.5 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-2">
                  <div>
                    <label className="text-xs font-medium text-text-secondary block mb-1">Limite Contratual (dias)</label>
                    <input
                      type="number"
                      value={sokContractLimitDays}
                      onChange={(e) => setSokContractLimitDays(Number(e.target.value))}
                      className="w-full rounded-lg border border-border bg-surface-bg px-2.5 py-1.5 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-medium text-text-secondary block mb-1">Valor do Kit (R$)</label>
                    <input
                      type="number"
                      value={sokImmobilizedValue}
                      onChange={(e) => setSokImmobilizedValue(Number(e.target.value))}
                      className="w-full rounded-lg border border-border bg-surface-bg px-2.5 py-1.5 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-medium text-text-secondary block mb-1">Faturamento Médio (R$)</label>
                    <input
                      type="number"
                      value={sokAvgRevenue}
                      onChange={(e) => setSokAvgRevenue(Number(e.target.value))}
                      className="w-full rounded-lg border border-border bg-surface-bg px-2.5 py-1.5 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary"
                    />
                  </div>
                </div>

                <Button size="sm" onClick={handleCalculateSok} disabled={sokLoading} className="w-full gap-1.5">
                  <Activity className="w-3.5 h-3.5" />
                  {sokLoading ? "Calculando SOK..." : "Calcular Score SOK"}
                </Button>
              </div>

              {sokResult && (
                <div className="p-4 rounded-xl border border-border bg-surface-bg space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-text-secondary">Resultado SOK:</span>
                    <span
                      className={`text-xs font-mono font-bold px-2 py-0.5 rounded-full ${
                        sokResult.is_idle
                          ? "bg-status-danger-subtle text-status-danger border border-status-danger/20"
                          : "bg-status-success-subtle text-status-success border border-status-success/20"
                      }`}
                    >
                      SOK {sokResult.sok_score.toFixed(2)} • {sokResult.status}
                    </span>
                  </div>
                  <p className="text-xs text-text-main bg-surface-card p-2 rounded border border-border">
                    {sokResult.recommendation}
                  </p>
                  {sokResult.dentgo_reverse_pickup_suggested && (
                    <div className="p-2 bg-status-warning-subtle text-status-warning text-xs rounded border border-status-warning/20 font-medium">
                      Coleta Reversa DENTGO Express sugerida para resgate do ativo imobilizado.
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* PR: Ponto de Reposição */}
            <div className="bg-surface-card border border-border rounded-2xl p-5 shadow-card space-y-4">
              <div className="flex items-center justify-between border-b border-border pb-3">
                <div className="flex items-center gap-2.5">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-primary-subtle text-brand-primary">
                    <TrendingUp className="h-4 w-4" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-text-main">
                      Ponto de Reposição de Estoque Consignado (PR)
                    </h3>
                    <p className="text-xs text-text-secondary">
                      PR = (C_medio_diario * T_entrega_dentgo) + ES
                    </p>
                  </div>
                </div>
                <span className="text-[10px] font-mono bg-surface-bg px-2 py-0.5 rounded text-text-muted border border-border">
                  POST /inventory/pr
                </span>
              </div>

              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs font-medium text-text-secondary block mb-1">ID do Acordo</label>
                    <input
                      type="text"
                      value={prAgreementId}
                      onChange={(e) => setPrAgreementId(e.target.value)}
                      className="w-full rounded-lg border border-border bg-surface-bg px-2.5 py-1.5 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-medium text-text-secondary block mb-1">Consumo Médio Diário (un)</label>
                    <input
                      type="number"
                      step="0.1"
                      value={prDailyConsumption}
                      onChange={(e) => setPrDailyConsumption(Number(e.target.value))}
                      className="w-full rounded-lg border border-border bg-surface-bg px-2.5 py-1.5 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-2">
                  <div>
                    <label className="text-xs font-medium text-text-secondary block mb-1">Prazo DENTGO (dias)</label>
                    <input
                      type="number"
                      step="0.5"
                      value={prLeadTime}
                      onChange={(e) => setPrLeadTime(Number(e.target.value))}
                      className="w-full rounded-lg border border-border bg-surface-bg px-2.5 py-1.5 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-medium text-text-secondary block mb-1">Estoque Segurança</label>
                    <input
                      type="number"
                      value={prSafetyStock}
                      onChange={(e) => setPrSafetyStock(Number(e.target.value))}
                      className="w-full rounded-lg border border-border bg-surface-bg px-2.5 py-1.5 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-medium text-text-secondary block mb-1">Estoque Atual (un)</label>
                    <input
                      type="number"
                      value={prCurrentStock}
                      onChange={(e) => setPrCurrentStock(Number(e.target.value))}
                      className="w-full rounded-lg border border-border bg-surface-bg px-2.5 py-1.5 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary"
                    />
                  </div>
                </div>

                <Button size="sm" onClick={handleCalculatePr} disabled={prLoading} className="w-full gap-1.5">
                  <Activity className="w-3.5 h-3.5" />
                  {prLoading ? "Calculando PR..." : "Calcular Ponto de Reposição (PR)"}
                </Button>
              </div>

              {prResult && (
                <div className="p-4 rounded-xl border border-border bg-surface-bg space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-text-secondary">Resultado PR:</span>
                    <span
                      className={`text-xs font-mono font-bold px-2 py-0.5 rounded-full ${
                        prResult.replenishment_needed
                          ? "bg-status-danger-subtle text-status-danger border border-status-danger/20"
                          : "bg-status-success-subtle text-status-success border border-status-success/20"
                      }`}
                    >
                      PR {prResult.pr_score.toFixed(1)} un •{" "}
                      {prResult.replenishment_needed ? "Reposição Imediata" : "Estoque Adequado"}
                    </span>
                  </div>
                  <p className="text-xs text-text-main bg-surface-card p-2 rounded border border-border">
                    {prResult.recommendation}
                  </p>
                  {prResult.deal_id && (
                    <div className="flex items-center justify-between text-xs text-text-secondary bg-surface-card p-2 rounded border border-border font-mono">
                      <span>Deal de Reposição Aberto:</span>
                      <span className="text-brand-primary font-bold">{prResult.deal_id}</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Historical Scores Report */}
          <div className="bg-surface-card border border-border rounded-2xl p-5 shadow-card space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-border pb-3">
              <div className="flex items-center gap-2">
                <Package className="w-4 h-4 text-brand-primary" />
                <h4 className="text-xs font-bold uppercase tracking-wider text-text-main">
                  Histórico de Scores de Estoque Preditivo
                </h4>
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={invReportAgreementId}
                  onChange={(e) => setInvReportAgreementId(e.target.value)}
                  placeholder="ID do Acordo..."
                  className="rounded-lg border border-border bg-surface-bg px-2.5 py-1 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary font-mono"
                />
                <Button size="sm" variant="outline" onClick={handleFetchInvReport} disabled={invReportLoading}>
                  {invReportLoading ? "Carregando..." : "Consultar Relatório"}
                </Button>
              </div>
            </div>

            {invReportData && (
              <div className="space-y-3">
                <div className="flex items-center justify-between text-xs text-text-secondary font-mono">
                  <span>Parceiro: {invReportData.partner_name}</span>
                  <span>Total de Registros: {invReportData.total_records}</span>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-xs text-left">
                    <thead className="bg-surface-bg text-text-secondary border-b border-border">
                      <tr>
                        <th className="p-2 font-semibold">Tipo</th>
                        <th className="p-2 font-semibold">Score</th>
                        <th className="p-2 font-semibold">Status</th>
                        <th className="p-2 font-semibold">Data</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border">
                      {invReportData.scores_history && invReportData.scores_history.length > 0 ? (
                        invReportData.scores_history.map((row: any, i: number) => (
                          <tr key={i} className="hover:bg-surface-bg">
                            <td className="p-2 font-mono">{row.score_type}</td>
                            <td className="p-2 font-mono font-semibold">{row.score_value}</td>
                            <td className="p-2">
                              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-surface-card border border-border">
                                {row.status}
                              </span>
                            </td>
                            <td className="p-2 text-text-muted font-mono">{row.calculated_at}</td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={4} className="p-4 text-center text-text-muted">
                            Nenhum registro encontrado para este acordo.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 4: Calculadora de Margem Líquida Clínica */}
      {activeTab === "margin" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Simulator Form */}
            <div className="bg-surface-card border border-border rounded-2xl p-5 shadow-card space-y-4">
              <div className="flex items-center justify-between border-b border-border pb-3">
                <div className="flex items-center gap-2.5">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-status-success-subtle text-status-success">
                    <DollarSign className="h-4 w-4" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-text-main">
                      Simulador de Rentabilidade Clínica (ROI Hora-Cadeira)
                    </h3>
                    <p className="text-xs text-text-secondary">
                      Margem Líquida Real descontando insumos, lab CAD/CAM, honorários e custo fixo de cadeira
                    </p>
                  </div>
                </div>
                <span className="text-[10px] font-mono bg-surface-bg px-2 py-0.5 rounded text-text-muted border border-border">
                  POST /margin/calculate
                </span>
              </div>

              <div className="space-y-3">
                <div className="grid grid-cols-3 gap-2">
                  <div className="col-span-2">
                    <label className="text-xs font-medium text-text-secondary block mb-1">Nome do Procedimento</label>
                    <input
                      type="text"
                      value={marginProcedure}
                      onChange={(e) => setMarginProcedure(e.target.value)}
                      className="w-full rounded-lg border border-border bg-surface-bg px-2.5 py-1.5 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-medium text-text-secondary block mb-1">ID da Clínica</label>
                    <input
                      type="text"
                      value={marginClinicId}
                      onChange={(e) => setMarginClinicId(e.target.value)}
                      className="w-full rounded-lg border border-border bg-surface-bg px-2.5 py-1.5 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary font-mono"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs font-medium text-text-secondary block mb-1">Valor Cobrado (R$)</label>
                    <input
                      type="number"
                      value={marginRevenue}
                      onChange={(e) => setMarginRevenue(Number(e.target.value))}
                      className="w-full rounded-lg border border-border bg-surface-bg px-2.5 py-1.5 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-medium text-text-secondary block mb-1">Insumos/Implantes (R$)</label>
                    <input
                      type="number"
                      value={marginSupplies}
                      onChange={(e) => setMarginSupplies(Number(e.target.value))}
                      className="w-full rounded-lg border border-border bg-surface-bg px-2.5 py-1.5 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs font-medium text-text-secondary block mb-1">Laboratório Prótese (R$)</label>
                    <input
                      type="number"
                      value={marginLab}
                      onChange={(e) => setMarginLab(Number(e.target.value))}
                      className="w-full rounded-lg border border-border bg-surface-bg px-2.5 py-1.5 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-medium text-text-secondary block mb-1">Honorários Cirurgião (R$)</label>
                    <input
                      type="number"
                      value={marginSurgeon}
                      onChange={(e) => setMarginSurgeon(Number(e.target.value))}
                      className="w-full rounded-lg border border-border bg-surface-bg px-2.5 py-1.5 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-2">
                  <div>
                    <label className="text-xs font-medium text-text-secondary block mb-1">Horas de Cadeira</label>
                    <input
                      type="number"
                      step="0.5"
                      value={marginChairHours}
                      onChange={(e) => setMarginChairHours(Number(e.target.value))}
                      className="w-full rounded-lg border border-border bg-surface-bg px-2.5 py-1.5 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-medium text-text-secondary block mb-1">Custo/Hora Cadeira (R$)</label>
                    <input
                      type="number"
                      value={marginChairHourCost}
                      onChange={(e) => setMarginChairHourCost(Number(e.target.value))}
                      className="w-full rounded-lg border border-border bg-surface-bg px-2.5 py-1.5 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-medium text-text-secondary block mb-1">Alíquota Imposto (%)</label>
                    <input
                      type="number"
                      value={marginTaxRate}
                      onChange={(e) => setMarginTaxRate(Number(e.target.value))}
                      className="w-full rounded-lg border border-border bg-surface-bg px-2.5 py-1.5 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary"
                    />
                  </div>
                </div>

                <Button size="sm" onClick={handleCalculateMargin} disabled={marginLoading} className="w-full gap-1.5">
                  <DollarSign className="w-3.5 h-3.5" />
                  {marginLoading ? "Calculando..." : "Simular Margem Líquida"}
                </Button>
              </div>
            </div>

            {/* Margin Result Card */}
            <div className="bg-surface-card border border-border rounded-2xl p-5 shadow-card space-y-4">
              <div className="flex items-center justify-between border-b border-border pb-3">
                <h3 className="text-sm font-semibold text-text-main">Extrato de Rentabilidade da Cirurgia</h3>
                {marginResult && (
                  <span
                    className={`text-xs font-mono font-bold px-2 py-0.5 rounded-full ${
                      marginResult.is_low_margin
                        ? "bg-status-danger-subtle text-status-danger border border-status-danger/20"
                        : "bg-status-success-subtle text-status-success border border-status-success/20"
                    }`}
                  >
                    Margem: {marginResult.net_margin_percent.toFixed(1)}%
                  </span>
                )}
              </div>

              {marginResult ? (
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-3 text-xs">
                    <div className="p-3 bg-surface-bg rounded-xl border border-border">
                      <span className="text-text-muted text-[11px] block">Receita Bruta:</span>
                      <span className="font-mono font-bold text-sm text-text-main">
                        R$ {marginResult.gross_revenue.toFixed(2)}
                      </span>
                    </div>
                    <div className="p-3 bg-surface-bg rounded-xl border border-border">
                      <span className="text-text-muted text-[11px] block">Custo Total:</span>
                      <span className="font-mono font-bold text-sm text-status-danger">
                        R$ {marginResult.total_cost.toFixed(2)}
                      </span>
                    </div>
                  </div>

                  <div className="p-4 bg-surface-bg rounded-xl border border-border space-y-2 text-xs">
                    <span className="text-xs font-bold text-text-main block">Detalhamento de Custos:</span>
                    <div className="flex justify-between text-text-secondary">
                      <span>Custo de Cadeira ({marginResult.chair_hours}h x R${marginResult.chair_hour_cost}):</span>
                      <span className="font-mono font-semibold">R$ {marginResult.total_chair_cost.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between text-text-secondary">
                      <span>Insumos & Implantes:</span>
                      <span className="font-mono font-semibold">R$ {marginResult.supplies_cost.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between text-text-secondary">
                      <span>Laboratório CAD/CAM:</span>
                      <span className="font-mono font-semibold">R$ {marginResult.lab_cost.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between text-text-secondary">
                      <span>Honorários do Cirurgião:</span>
                      <span className="font-mono font-semibold">R$ {marginResult.surgeon_fee.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between text-text-secondary pt-1 border-t border-border">
                      <span>Impostos ({marginResult.tax_rate_percent}%):</span>
                      <span className="font-mono font-semibold">R$ {marginResult.tax_amount.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between pt-2 border-t border-border text-sm font-bold">
                      <span className="text-text-main">Margem Líquida Real:</span>
                      <span
                        className={marginResult.is_low_margin ? "text-status-danger" : "text-status-success"}
                      >
                        R$ {marginResult.net_margin_value.toFixed(2)}
                      </span>
                    </div>
                  </div>

                  <p className="text-xs text-text-secondary bg-surface-bg p-3 rounded-xl border border-border">
                    <span className="font-semibold text-text-main block mb-1">Recomendação Comercial:</span>
                    {marginResult.recommendation}
                  </p>
                </div>
              ) : (
                <div className="h-48 flex items-center justify-center text-xs text-text-muted text-center border border-dashed border-border rounded-xl">
                  Preencha os parâmetros e clique em "Simular Margem Líquida".
                </div>
              )}
            </div>
          </div>

          {/* Clinic Summary Report */}
          <div className="bg-surface-card border border-border rounded-2xl p-5 shadow-card space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-border pb-3">
              <div className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-brand-primary" />
                <h4 className="text-xs font-bold uppercase tracking-wider text-text-main">
                  Consolidado de Margem por Clínica / Polo
                </h4>
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={marginSummaryClinicId}
                  onChange={(e) => setMarginSummaryClinicId(e.target.value)}
                  placeholder="ID da Clínica..."
                  className="rounded-lg border border-border bg-surface-bg px-2.5 py-1 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary font-mono"
                />
                <Button size="sm" variant="outline" onClick={handleFetchMarginSummary} disabled={marginSummaryLoading}>
                  {marginSummaryLoading ? "Carregando..." : "Carregar Resumo"}
                </Button>
              </div>
            </div>

            {marginSummaryData && (
              <div className="space-y-3">
                <div className="grid grid-cols-3 gap-3 text-xs">
                  <div className="p-3 bg-surface-bg rounded-lg border border-border">
                    <span className="text-text-muted block text-[10px]">Procedimentos Avaliados:</span>
                    <span className="font-mono font-bold text-sm text-text-main">
                      {marginSummaryData.total_procedures_analyzed}
                    </span>
                  </div>
                  <div className="p-3 bg-surface-bg rounded-lg border border-border">
                    <span className="text-text-muted block text-[10px]">Margem Média:</span>
                    <span className="font-mono font-bold text-sm text-status-success">
                      {marginSummaryData.average_margin_percent.toFixed(1)}%
                    </span>
                  </div>
                  <div className="p-3 bg-surface-bg rounded-lg border border-border">
                    <span className="text-text-muted block text-[10px]">Procedimentos em Baixa Margem:</span>
                    <span className="font-mono font-bold text-sm text-status-warning">
                      {marginSummaryData.low_margin_count}
                    </span>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-xs text-left">
                    <thead className="bg-surface-bg text-text-secondary border-b border-border">
                      <tr>
                        <th className="p-2 font-semibold">Procedimento</th>
                        <th className="p-2 font-semibold">Receita</th>
                        <th className="p-2 font-semibold">Custo</th>
                        <th className="p-2 font-semibold">Margem</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border">
                      {marginSummaryData.items && marginSummaryData.items.length > 0 ? (
                        marginSummaryData.items.map((it: any, idx: number) => (
                          <tr key={idx} className="hover:bg-surface-bg">
                            <td className="p-2 font-medium">{it.procedure_name}</td>
                            <td className="p-2 font-mono">R$ {it.gross_revenue?.toFixed(2)}</td>
                            <td className="p-2 font-mono text-status-danger">R$ {it.total_cost?.toFixed(2)}</td>
                            <td className="p-2 font-mono font-bold">
                              {it.net_margin_percent?.toFixed(1)}%
                            </td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={4} className="p-4 text-center text-text-muted">
                            Nenhum procedimento registrado para esta clínica.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 5: Health Score Cirúrgico (HSC) & Churn */}
      {activeTab === "health_score" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Calculator Card */}
            <div className="bg-surface-card border border-border rounded-2xl p-5 shadow-card space-y-4">
              <div className="flex items-center justify-between border-b border-border pb-3">
                <div className="flex items-center gap-2.5">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-primary-subtle text-brand-primary">
                    <Activity className="h-4 w-4" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-text-main">
                      Health Score Cirúrgico (HSC) & Churn Radar
                    </h3>
                    <p className="text-xs text-text-secondary">
                      HSC = 0.4*F_cirurgica + 0.3*G_consignado + 0.2*S_atendimento + 0.1*E_canal
                    </p>
                  </div>
                </div>
                <span className="text-[10px] font-mono bg-surface-bg px-2 py-0.5 rounded text-text-muted border border-border">
                  POST /health-score/calculate
                </span>
              </div>

              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs font-medium text-text-secondary block mb-1">ID do Parceiro</label>
                    <input
                      type="text"
                      value={hscPartnerId}
                      onChange={(e) => setHscPartnerId(e.target.value)}
                      className="w-full rounded-lg border border-border bg-surface-bg px-2.5 py-1.5 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-medium text-text-secondary block mb-1">Nome do Parceiro</label>
                    <input
                      type="text"
                      value={hscPartnerName}
                      onChange={(e) => setHscPartnerName(e.target.value)}
                      className="w-full rounded-lg border border-border bg-surface-bg px-2.5 py-1.5 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-text-secondary">Frequência Cirúrgica (40%):</span>
                    <span className="font-mono font-bold text-brand-primary">{hscFCirurgica} pts</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={hscFCirurgica}
                    onChange={(e) => setHscFCirurgica(Number(e.target.value))}
                    className="w-full"
                  />
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-text-secondary">Giro do Consignado (30%):</span>
                    <span className="font-mono font-bold text-brand-primary">{hscGConsignado} pts</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={hscGConsignado}
                    onChange={(e) => setHscGConsignado(Number(e.target.value))}
                    className="w-full"
                  />
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-text-secondary">Satisfação & Ausência de RMA (20%):</span>
                    <span className="font-mono font-bold text-brand-primary">{hscSAtendimento} pts</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={hscSAtendimento}
                    onChange={(e) => setHscSAtendimento(Number(e.target.value))}
                    className="w-full"
                  />
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-text-secondary">Engajamento Omnichannel (10%):</span>
                    <span className="font-mono font-bold text-brand-primary">{hscECanal} pts</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={hscECanal}
                    onChange={(e) => setHscECanal(Number(e.target.value))}
                    className="w-full"
                  />
                </div>

                <Button size="sm" onClick={handleCalculateHsc} disabled={hscLoading} className="w-full gap-1.5">
                  <Activity className="w-3.5 h-3.5" />
                  {hscLoading ? "Calculando HSC..." : "Calcular Health Score Cirúrgico"}
                </Button>
              </div>
            </div>

            {/* HSC Result Card */}
            <div className="bg-surface-card border border-border rounded-2xl p-5 shadow-card space-y-4">
              <div className="flex items-center justify-between border-b border-border pb-3">
                <h3 className="text-sm font-semibold text-text-main">Diagnóstico Sanitário da Conta</h3>
                {hscResult && (
                  <span
                    className={`text-xs font-mono font-bold px-2.5 py-1 rounded-full ${
                      hscResult.classification === "EXCELENTE"
                        ? "bg-status-success-subtle text-status-success border border-status-success/20"
                        : hscResult.classification === "ATIVO"
                        ? "bg-brand-primary-subtle text-brand-primary border border-brand-primary/20"
                        : "bg-status-danger-subtle text-status-danger border border-status-danger/20"
                    }`}
                  >
                    HSC {hscResult.hsc_score.toFixed(1)} • {hscResult.classification}
                  </span>
                )}
              </div>

              {hscResult ? (
                <div className="space-y-4 text-xs">
                  <div className="p-4 bg-surface-bg rounded-xl border border-border space-y-2">
                    <span className="font-semibold text-text-main block">Recomendação Anti-Churn:</span>
                    <p className="text-text-secondary leading-relaxed">{hscResult.recommendation}</p>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div className="p-3 bg-surface-bg rounded-lg border border-border">
                      <span className="text-text-muted text-[10px] block">Elegível a Upsell:</span>
                      <span className="font-semibold text-text-main">
                        {hscResult.upsell_eligible ? "Sim (Expandir Consignação)" : "Não"}
                      </span>
                    </div>
                    <div className="p-3 bg-surface-bg rounded-lg border border-border">
                      <span className="text-text-muted text-[10px] block">Elegível ao MGM:</span>
                      <span className="font-semibold text-text-main">
                        {hscResult.mgm_eligible ? "Sim (Indicação Ativa)" : "Não"}
                      </span>
                    </div>
                  </div>

                  {hscResult.rescue_task_id && (
                    <div className="p-3 bg-status-danger-subtle text-status-danger rounded-xl border border-status-danger/20 font-medium">
                      Tarefa de resgate automático disparada: {hscResult.rescue_task_id}
                    </div>
                  )}

                  {hscResult.dentgo_voucher_code && (
                    <div className="p-3 bg-status-success-subtle text-status-success rounded-xl border border-status-success/20 font-mono font-bold">
                      Voucher DENTGO Liberado: {hscResult.dentgo_voucher_code}
                    </div>
                  )}
                </div>
              ) : (
                <div className="h-48 flex items-center justify-center text-xs text-text-muted text-center border border-dashed border-border rounded-xl">
                  Ajuste os 4 pilares ponderados e execute o cálculo de saúde da conta.
                </div>
              )}
            </div>
          </div>

          {/* HSC History Card */}
          <div className="bg-surface-card border border-border rounded-2xl p-5 shadow-card space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-border pb-3">
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-brand-primary" />
                <h4 className="text-xs font-bold uppercase tracking-wider text-text-main">
                  Histórico de Health Scores do Parceiro
                </h4>
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={hscHistoryPartnerId}
                  onChange={(e) => setHscHistoryPartnerId(e.target.value)}
                  placeholder="ID do Parceiro..."
                  className="rounded-lg border border-border bg-surface-bg px-2.5 py-1 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary font-mono"
                />
                <Button size="sm" variant="outline" onClick={handleFetchHscHistory} disabled={hscHistoryLoading}>
                  {hscHistoryLoading ? "Carregando..." : "Consultar Histórico"}
                </Button>
              </div>
            </div>

            {hscHistoryData && (
              <div className="space-y-3">
                <div className="flex items-center justify-between text-xs text-text-secondary font-mono">
                  <span>Parceiro: {hscHistoryData.partner_name}</span>
                  <span>Total de Avaliações: {hscHistoryData.total_evaluations}</span>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-xs text-left">
                    <thead className="bg-surface-bg text-text-secondary border-b border-border">
                      <tr>
                        <th className="p-2 font-semibold">Score</th>
                        <th className="p-2 font-semibold">Classificação</th>
                        <th className="p-2 font-semibold">Frequência</th>
                        <th className="p-2 font-semibold">Giro</th>
                        <th className="p-2 font-semibold">Data</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border">
                      {hscHistoryData.evaluations && hscHistoryData.evaluations.length > 0 ? (
                        hscHistoryData.evaluations.map((ev: any, idx: number) => (
                          <tr key={idx} className="hover:bg-surface-bg">
                            <td className="p-2 font-mono font-bold">{ev.hsc_score?.toFixed(1)}</td>
                            <td className="p-2 font-mono">{ev.classification}</td>
                            <td className="p-2 font-mono">{ev.f_cirurgica} pts</td>
                            <td className="p-2 font-mono">{ev.g_consignado} pts</td>
                            <td className="p-2 text-text-muted font-mono">{ev.calculated_at}</td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={5} className="p-4 text-center text-text-muted">
                            Nenhum registro histórico para este parceiro.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default IntelligenceSuiteWorkspace;
