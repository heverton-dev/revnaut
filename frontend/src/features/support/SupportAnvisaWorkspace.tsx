import * as React from "react";
import {
  ShieldAlert,
  Siren,
  HeartPulse,
  CheckCircle2,
  AlertTriangle,
  Search,
  Truck,
  RefreshCw,
  FileWarning,
  Video,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Tabs } from "@/components/ui/Tabs";
import { DataTable, Column } from "@/components/ui/DataTable";
import { R2DirectUploader } from "@/components/shared/R2DirectUploader";
import { LiveKitDealRoomModal } from "@/features/communications/LiveKitDealRoomModal";

interface RmaClaimItem {
  id: string;
  ticket_id: string;
  surgeon_name?: string;
  surgeon_cro_uf: string;
  product_id: string;
  product_name: string;
  batch_number: string;
  fdi_tooth_region: string;
  radiograph_r2_key?: string;
  insertion_torque_ncm: number;
  failure_reason: string;
  status: string;
  warranty_approved: boolean;
  quarantine_triggered: boolean;
  batch_failure_rate_percent: number;
  created_at: string;
}

interface QuarantineStatusInfo {
  batch_number: string;
  total_distributed: number;
  total_failures: number;
  failure_rate_percent: number;
  status: string;
  reason: string;
  blocked_at: string;
}

interface SosTicketDetail {
  id: string;
  ticket_id?: string;
  title: string;
  customer_name: string;
  customer_phone?: string;
  cro_uf?: string;
  priority: string;
  status: string;
  livekit_room_url?: string;
  dentgo_order_id?: string;
}

interface PostOpScheduleItem {
  id: string;
  patient_name: string;
  patient_phone: string;
  surgeon_name: string;
  procedure_name: string;
  surgery_date: string;
  status: string;
  alert_ticket_id?: string | null;
  milestones: Array<{
    code: string;
    target_date: string;
    title: string;
    status: string;
    feedback_received?: string | null;
  }>;
}

const FDI_UPPER = ["18", "17", "16", "15", "14", "13", "12", "11", "21", "22", "23", "24", "25", "26", "27", "28"];
const FDI_LOWER = ["48", "47", "46", "45", "44", "43", "42", "41", "31", "32", "33", "34", "35", "36", "37", "38"];

interface FdiOdontogramProps {
  selected: string;
  onSelect: (tooth: string) => void;
}

const FdiOdontogram: React.FC<FdiOdontogramProps> = ({ selected, onSelect }) => {
  const renderArch = (teeth: string[], label: string) => (
    <div className="space-y-1">
      <span className="text-[10px] uppercase font-semibold text-text-secondary">{label}</span>
      <div className="grid grid-cols-16 gap-0.5" style={{ gridTemplateColumns: "repeat(16, minmax(0, 1fr))" }}>
        {teeth.map((t, i) => (
          <button
            key={t}
            type="button"
            aria-label={`Dente FDI ${t}`}
            aria-pressed={selected === t}
            onClick={() => onSelect(t)}
            className={`py-1.5 text-[9px] font-mono border transition ${
              i === 7 ? "mr-1" : ""
            } ${
              selected === t
                ? "bg-brand-primary text-text-inverse border-brand-primary font-bold"
                : "bg-surface-card text-text-secondary border-border hover:border-brand-primary"
            } ${i < 8 ? "rounded-l-full rounded-r-md" : "rounded-r-full rounded-l-md"}`}
          >
            {t}
          </button>
        ))}
      </div>
    </div>
  );

  return (
    <div className="p-2 rounded-lg border border-border bg-surface-bg space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-text-main">Odontograma FDI (32 dentes)</span>
        <Badge variant="navy">Selecionado: {selected || "-"}</Badge>
      </div>
      {renderArch(FDI_UPPER, "Arcada Superior")}
      {renderArch(FDI_LOWER, "Arcada Inferior")}
    </div>
  );
};

export const SupportAnvisaWorkspace: React.FC = () => {
  const [activeTab, setActiveTab] = React.useState<string>("anvisa_rma");
  const [feedbackMsg, setFeedbackMsg] = React.useState<string | null>(null);
  const [errorMsg, setErrorMsg] = React.useState<string | null>(null);

  // Estados Aba 1: Tecnovigilância ANVISA & Quarentena de Lotes (RMA)
  const [rmaClaims, setRmaClaims] = React.useState<RmaClaimItem[]>([]);
  const [loadingRma, setLoadingRma] = React.useState<boolean>(true);
  const [selectedClaim, setSelectedClaim] = React.useState<RmaClaimItem | null>(null);
  const [rmaCroUf, setRmaCroUf] = React.useState<string>("CRO-SP 54321");
  const [rmaSurgeonName, setRmaSurgeonName] = React.useState<string>("Dr. Lucas Cirurgião");
  const [rmaProductId, setRmaProductId] = React.useState<string>("IMP-CM-3513");
  const [rmaProductName, setRmaProductName] = React.useState<string>("Implante Cone Morse 3.5x13");
  const [rmaBatchNumber, setRmaBatchNumber] = React.useState<string>("LOTE-1122");
  const [rmaFdiTooth, setRmaFdiTooth] = React.useState<string>("16");
  const [rmaTorque, setRmaTorque] = React.useState<string>("40");
  const [rmaFailureReason, setRmaFailureReason] = React.useState<string>("loss_of_osseointegration");
  const [rmaRadiographKey, setRmaRadiographKey] = React.useState<string>(
    "0f14ffff/dicom/raiox_periapical_16.png"
  );
  const [submittingRma, setSubmittingRma] = React.useState<boolean>(false);

  // Inspetor de Quarentena de Lote
  const [quarantineBatchInput, setQuarantineBatchInput] = React.useState<string>("LOTE-9988");
  const [quarantineInfo, setQuarantineInfo] = React.useState<QuarantineStatusInfo | null>(null);
  const [quarantineMessage, setQuarantineMessage] = React.useState<string | null>(null);

  // Estados Aba 2: SOS Mesa Cirúrgica & Despacho Emergencial
  const [sosSurgeonName, setSosSurgeonName] = React.useState<string>("Dr. Alexandre Neves");
  const [sosPhone, setSosPhone] = React.useState<string>("+5511999991234");
  const [sosCroUf, setSosCroUf] = React.useState<string>("CRO-SP-88771");
  const [sosProcedureDetails, setSosProcedureDetails] = React.useState<string>(
    "Perda de travamento primário em osso Tipo IV — necessita implante curto 4.3x8.5 de emergência"
  );
  const [activeSosTicket, setActiveSosTicket] = React.useState<SosTicketDetail | null>(null);
  const [sosDispatchAddress, setSosDispatchAddress] = React.useState<string>(
    "Hospital Santa Catarina, Centro Cirúrgico Sala 04 - Av. Paulista, 200"
  );
  const [sosDispatchProduct, setSosDispatchProduct] = React.useState<string>("IMP-CM-37511");
  const [dispatchingSos, setDispatchingSos] = React.useState<boolean>(false);

  // Estados Aba 3: Linha de Cuidado Pós-Operatória B2C (24h/48h/72h/7d)
  const [postOpSchedules, setPostOpSchedules] = React.useState<PostOpScheduleItem[]>([]);
  const [selectedSchedule, setSelectedSchedule] = React.useState<PostOpScheduleItem | null>(null);
  const [poPatientName, setPoPatientName] = React.useState<string>("Carlos Eduardo Silveira");
  const [poPatientPhone, setPoPatientPhone] = React.useState<string>("+5511998877665");
  const [poSurgeonName, setPoSurgeonName] = React.useState<string>("Dr. Roberto Implantodontista");
  const [poSurgeonPhone, setPoSurgeonPhone] = React.useState<string>("+5511988776655");
  const [poProcedure, setPoProcedure] = React.useState<string>(
    "Protocolo All-on-4 Superior com Carga Imediata"
  );
  const [poSurgeryDate, setPoSurgeryDate] = React.useState<string>("2026-10-18");
  const [feedbackMilestone, setFeedbackMilestone] = React.useState<string>("24h");
  const [feedbackText, setFeedbackText] = React.useState<string>(
    "Estou com sangramento forte na gengiva e inchaço intenso no rosto, muita dor!"
  );

  const loadRmaClaims = React.useCallback(async () => {
    setLoadingRma(true);
    try {
      const res = await fetch("/api/v1/tickets/anvisa-rma");
      if (res.ok) {
        const data = await res.json();
        setRmaClaims(Array.isArray(data) ? data : []);
      }
    } catch {
      setRmaClaims([]);
    } finally {
      setLoadingRma(false);
    }
  }, []);

  const loadPostOpSchedules = React.useCallback(async () => {
    try {
      const res = await fetch("/api/v1/automations/postop-care");
      if (res.ok) {
        const data: PostOpScheduleItem[] = await res.json();
        setPostOpSchedules(Array.isArray(data) ? data : []);
        if (Array.isArray(data) && data.length > 0 && !selectedSchedule) {
          setSelectedSchedule(data[0]);
        }
      }
    } catch {
      setPostOpSchedules([]);
    }
  }, [selectedSchedule]);

  React.useEffect(() => {
    loadRmaClaims();
    loadPostOpSchedules();
  }, [loadRmaClaims, loadPostOpSchedules]);

  const handleCreateRma = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmittingRma(true);
    setErrorMsg(null);
    setFeedbackMsg(null);
    try {
      const res = await fetch("/api/v1/tickets/anvisa-rma", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          surgeon_cro_uf: rmaCroUf,
          surgeon_name: rmaSurgeonName,
          product_id: rmaProductId,
          product_name: rmaProductName,
          batch_number: rmaBatchNumber,
          fdi_tooth_region: rmaFdiTooth,
          insertion_torque_ncm: Number(rmaTorque) || 35,
          surgery_date: "2026-07-10",
          explant_date: "2026-09-20",
          failure_reason: rmaFailureReason,
          radiograph_r2_key: rmaRadiographKey,
          notes: "Notificação técnica de tecnovigilância ANVISA com laudo radiográfico anexado.",
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data.detail || "Falha ao registrar RMA ANVISA.");
      }
      setFeedbackMsg(
        `RMA #${data.id} protocolado! Status: ${data.status} (Taxa de falha do lote: ${data.batch_failure_rate_percent}%)`
      );
      await loadRmaClaims();
    } catch (err: any) {
      setErrorMsg(err.message);
    } finally {
      setSubmittingRma(false);
    }
  };

  const handleInspectClaim = async (claim: RmaClaimItem) => {
    try {
      const res = await fetch(`/api/v1/tickets/anvisa-rma/${claim.id}`);
      if (res.ok) {
        setSelectedClaim(await res.json());
      } else {
        setSelectedClaim(claim);
      }
    } catch {
      setSelectedClaim(claim);
    }
  };

  const handleUpdateTicketStatus = async (ticketId: string, nextStatus: string) => {
    try {
      const res = await fetch(`/api/v1/tickets/${ticketId}/status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: nextStatus }),
      });
      if (res.ok) {
        setFeedbackMsg(`Ticket #${ticketId} atualizado para '${nextStatus}'.`);
        await loadRmaClaims();
      }
    } catch {
      // Silencioso
    }
  };

  const handleCheckQuarantine = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!quarantineBatchInput.trim()) return;
    setQuarantineInfo(null);
    setQuarantineMessage(null);
    try {
      const res = await fetch(
        `/api/v1/tickets/anvisa-rma/quarantine/${encodeURIComponent(quarantineBatchInput.trim())}`
      );
      if (res.status === 404) {
        setQuarantineMessage(
          `Lote ${quarantineBatchInput.trim()} liberado e em conformidade sanitária (0 bloqueios de quarentena).`
        );
        return;
      }
      if (res.ok) {
        setQuarantineInfo(await res.json());
      }
    } catch {
      setQuarantineMessage("Erro ao consultar status de quarentena do lote.");
    }
  };

  const handleTriggerSurgicalSos = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setFeedbackMsg(null);
    try {
      const res = await fetch("/api/v1/tickets/surgical-sos", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          customer_name: sosSurgeonName,
          customer_phone: sosPhone,
          cro_uf: sosCroUf,
          procedure_details: sosProcedureDetails,
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || "Falha ao acionar SOS Mesa Cirúrgica.");
      const tId = data.ticket_id || data.id;
      const getRes = await fetch(`/api/v1/tickets/surgical-sos/${tId}`);
      if (getRes.ok) {
        setActiveSosTicket(await getRes.json());
      } else {
        setActiveSosTicket({ ...data, id: tId });
      }
      setFeedbackMsg(`Chamado P0 #${tId} aberto! Sala de Vídeo LiveKit pronta.`);
    } catch (err: any) {
      setErrorMsg(err.message);
    }
  };

  const handleDispatchDentgoSos = async () => {
    if (!activeSosTicket) return;
    setDispatchingSos(true);
    setErrorMsg(null);
    try {
      const tId = activeSosTicket.id || activeSosTicket.ticket_id;
      const res = await fetch(`/api/v1/tickets/surgical-sos/${tId}/dispatch-dentgo`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          product_id: sosDispatchProduct,
          quantity: 1,
          delivery_address: sosDispatchAddress,
          delivery_lat: -23.566,
          delivery_lng: -46.666,
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data.detail || "Nenhum Micro-Hub DENTGO com estoque ativo para este SKU.");
      }
      setFeedbackMsg(
        `Entrega Expressa DENTGO #${data.dentgo_order_id} despachada! ETA: ${data.estimated_eta_minutes} min.`
      );
      const getRes = await fetch(`/api/v1/tickets/surgical-sos/${tId}`);
      if (getRes.ok) {
        setActiveSosTicket(await getRes.json());
      }
    } catch (err: any) {
      setErrorMsg(err.message);
    } finally {
      setDispatchingSos(false);
    }
  };

  const handleStartPostOp = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    try {
      const res = await fetch("/api/v1/automations/postop-care/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          patient_name: poPatientName,
          patient_phone: poPatientPhone,
          surgeon_name: poSurgeonName,
          surgeon_phone: poSurgeonPhone,
          procedure_name: poProcedure,
          surgery_date: poSurgeryDate,
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || "Falha ao iniciar régua pós-operatória.");
      setSelectedSchedule(data);
      setFeedbackMsg(
        `Régua Pós-Operatória #${data.id} iniciada com 4 marcos clínicos (24h, 48h, 72h e 7d).`
      );
      await loadPostOpSchedules();
    } catch (err: any) {
      setErrorMsg(err.message);
    }
  };

  const handleInspectSchedule = async (scheduleId: string) => {
    try {
      const res = await fetch(`/api/v1/automations/postop-care/${scheduleId}`);
      if (res.ok) {
        setSelectedSchedule(await res.json());
      }
    } catch {
      // Silencioso
    }
  };

  const handleSendPatientFeedback = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSchedule) return;
    setErrorMsg(null);
    try {
      const res = await fetch(
        `/api/v1/automations/postop-care/${selectedSchedule.id}/feedback`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            feedback_text: feedbackText,
            milestone_code: feedbackMilestone,
          }),
        }
      );
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || "Erro ao processar feedback do paciente.");
      if (data.is_critical) {
        setFeedbackMsg(
          `ALERTA VERMELHO PÓS-OP DISPARADO! Ticket Crítico #${data.alert_ticket_id} enviado ao cirurgião (Gatilhos: ${data.detected_triggers.join(", ")}).`
        );
      } else {
        setFeedbackMsg(`Evolução clínica normal registrada no marco ${feedbackMilestone}.`);
      }
      await handleInspectSchedule(selectedSchedule.id);
      await loadPostOpSchedules();
    } catch (err: any) {
      setErrorMsg(err.message);
    }
  };

  const rmaColumns: Column<RmaClaimItem>[] = [
    {
      key: "id",
      header: "Protocolo RMA / Lote",
      render: (r) => (
        <div>
          <div className="font-semibold text-text-main">{r.id}</div>
          <div className="text-xs font-mono text-text-secondary">Lote: {r.batch_number}</div>
        </div>
      ),
    },
    {
      key: "surgeon_cro_uf",
      header: "Cirurgião Solicitante",
      render: (r) => (
        <div>
          <div className="text-xs font-medium text-text-main">{r.surgeon_name || "Cirurgião"}</div>
          <div className="text-[11px] text-text-secondary">{r.surgeon_cro_uf}</div>
        </div>
      ),
    },
    {
      key: "product_name",
      header: "Implante & Região FDI",
      render: (r) => (
        <span className="text-xs text-text-main">
          {r.product_name} (Dente {r.fdi_tooth_region} • {r.insertion_torque_ncm} N.cm)
        </span>
      ),
    },
    {
      key: "status",
      header: "Status & Quarentena",
      render: (r) => (
        <div className="flex items-center gap-1.5">
          <Badge variant={r.quarantine_triggered ? "danger" : "success"} className="text-[10px]">
            {r.quarantine_triggered ? "LOTE BLOQUEADO" : r.status}
          </Badge>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-text-main">
            Tecnovigilância ANVISA (RMA), SOS Mesa Cirúrgica & Pós-Operatório B2C
          </h1>
          <p className="text-xs sm:text-sm text-text-secondary mt-1">
            Garantia de osseointegração com bloqueio preventivo de lote fabril, socorro imediato de centro cirúrgico e monitoramento clínico 24h/48h/72h/7d.
          </p>
        </div>
        <Button
          variant="secondary"
          size="sm"
          onClick={() => {
            loadRmaClaims();
            loadPostOpSchedules();
          }}
          className="gap-1.5 self-start sm:self-auto"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          Atualizar Central
        </Button>
      </div>

      {feedbackMsg && (
        <div className="p-3 rounded-lg bg-status-success-subtle border border-status-success/30 text-xs text-status-success flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 shrink-0" />
            <span>{feedbackMsg}</span>
          </div>
          <button type="button" onClick={() => setFeedbackMsg(null)} className="underline">
            Fechar
          </button>
        </div>
      )}

      {errorMsg && (
        <div className="p-3 rounded-lg bg-status-danger-subtle border border-status-danger/30 text-xs text-status-danger flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 shrink-0" />
            <span>{errorMsg}</span>
          </div>
          <button type="button" onClick={() => setErrorMsg(null)} className="underline">
            Fechar
          </button>
        </div>
      )}

      <Tabs
        activeTab={activeTab}
        onChange={setActiveTab}
        tabs={[
          { id: "anvisa_rma", label: "Tecnovigilância ANVISA & Quarentena (RMA)", count: rmaClaims.length },
          { id: "surgical_sos", label: "SOS Mesa Cirúrgica & Despacho Emergencial" },
          { id: "postop_b2c", label: "Linha de Cuidado Pós-Operatória B2C (24h-7d)", count: postOpSchedules.length },
        ]}
      />

      {/* ABA 1: TECNOVIGILÂNCIA ANVISA & QUARENTENA DE LOTES (RMA) */}
      {activeTab === "anvisa_rma" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card className="border-border">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileWarning className="h-4 w-4 text-brand-primary" />
                  Abrir Processo de Garantia RMA
                </CardTitle>
                <CardDescription>
                  Exige laudo radiográfico no R2 e verifica automaticamente o teto regulatório de 2,5% de falhas do lote.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleCreateRma} className="space-y-3">
                  <div className="grid grid-cols-2 gap-2">
                    <Input
                      required
                      value={rmaCroUf}
                      onChange={(e) => setRmaCroUf(e.target.value)}
                      placeholder="CRO-UF *"
                    />
                    <Input
                      required
                      value={rmaSurgeonName}
                      onChange={(e) => setRmaSurgeonName(e.target.value)}
                      placeholder="Cirurgião *"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <Input
                      required
                      value={rmaProductId}
                      onChange={(e) => setRmaProductId(e.target.value)}
                      placeholder="SKU Implante *"
                    />
                    <Input
                      required
                      value={rmaBatchNumber}
                      onChange={(e) => setRmaBatchNumber(e.target.value)}
                      placeholder="Lote ANVISA *"
                    />
                  </div>
                  <Input
                    required
                    value={rmaProductName}
                    onChange={(e) => setRmaProductName(e.target.value)}
                    placeholder="Descrição do Implante *"
                  />
                  <FdiOdontogram selected={rmaFdiTooth} onSelect={setRmaFdiTooth} />
                  <div className="grid grid-cols-2 gap-2">
                    <Input
                      required
                      value={rmaFdiTooth}
                      onChange={(e) => setRmaFdiTooth(e.target.value)}
                      placeholder="Dente FDI (ex: 16)"
                    />
                    <Input
                      type="number"
                      required
                      value={rmaTorque}
                      onChange={(e) => setRmaTorque(e.target.value)}
                      placeholder="Torque (N.cm)"
                    />
                  </div>
                  <Select
                    label="Classificação Técnica da Falha"
                    value={rmaFailureReason}
                    onChange={(e) => setRmaFailureReason(e.target.value)}
                    options={[
                      { value: "loss_of_osseointegration", label: "Perda de Osseointegração (Fibrointegração)" },
                      { value: "fracture", label: "Fratura Mecânica de Componente/Implante" },
                      { value: "periimplantitis", label: "Peri-implantite Aguda Precoce" },
                      { value: "contamination", label: "Suspeita de Violação de Esterilização" },
                    ]}
                  />
                  <R2DirectUploader
                    module="dicom"
                    accept=".dcm,.png,.jpg,.pdf"
                    onUploadComplete={({ key }) => setRmaRadiographKey(key)}
                  />
                  <Button type="submit" size="sm" disabled={submittingRma} className="w-full">
                    {submittingRma ? "Protocolando RMA..." : "Protocolar Queixa Técnica ANVISA"}
                  </Button>
                </form>
              </CardContent>
            </Card>

            <div className="lg:col-span-2 space-y-6">
              {/* Inspetor de Quarentena de Lote Fabril */}
              <Card className="border-border">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <ShieldAlert className="h-4 w-4 text-status-danger" />
                    Verificador de Quarentena Sanitária de Lote Fabril
                  </CardTitle>
                  <CardDescription>
                    Consulta se um lote atingiu o gatilho automático de bloqueio (&gt; 2,5% de falhas) nos Hubs DENTGO e Maletas KeyPartners.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <form onSubmit={handleCheckQuarantine} className="flex gap-2">
                    <Input
                      value={quarantineBatchInput}
                      onChange={(e) => setQuarantineBatchInput(e.target.value)}
                      placeholder="Digite o número do lote (ex: LOTE-9988 ou LOTE-1122)..."
                    />
                    <Button type="submit" size="sm" variant="secondary" className="gap-1.5 shrink-0">
                      <Search className="h-3.5 w-3.5" />
                      Inspecionar Lote
                    </Button>
                  </form>

                  {quarantineMessage && (
                    <div className="p-3 rounded-lg bg-status-success-subtle border border-status-success/30 text-xs text-status-success">
                      {quarantineMessage}
                    </div>
                  )}

                  {quarantineInfo && (
                    <div className="p-4 rounded-lg bg-status-danger-subtle border border-status-danger/40 text-xs space-y-1.5">
                      <div className="flex items-center justify-between font-bold text-status-danger">
                        <span>ALERTA SANITÁRIO: LOTE {quarantineInfo.batch_number} EM QUARENTENA</span>
                        <Badge variant="danger">{quarantineInfo.status}</Badge>
                      </div>
                      <p className="text-text-main">{quarantineInfo.reason}</p>
                      <div className="flex gap-4 text-text-secondary pt-1">
                        <span>Distribuídos: {quarantineInfo.total_distributed}</span>
                        <span>Falhas: {quarantineInfo.total_failures}</span>
                        <span>Taxa: {quarantineInfo.failure_rate_percent}%</span>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Tabela de Processos RMA */}
              <DataTable
                columns={rmaColumns}
                data={rmaClaims}
                isLoading={loadingRma}
                onRowClick={handleInspectClaim}
                emptyTitle="Nenhuma queixa técnica RMA registrada"
                emptyDescription="Registre uma ocorrência de tecnovigilância ao lado para auditar o lote."
              />

              {selectedClaim && (
                <Card className="p-4 border-border bg-surface-bg/50 text-xs space-y-2">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="font-bold text-sm text-text-main">
                      Detalhes do Processo RMA #{selectedClaim.id} (Ticket #{selectedClaim.ticket_id})
                    </span>
                    <div className="flex gap-1.5">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleUpdateTicketStatus(selectedClaim.ticket_id, "em_andamento")}
                      >
                        Marcar Em Análise
                      </Button>
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => handleUpdateTicketStatus(selectedClaim.ticket_id, "resolvido")}
                      >
                        Concluir Laudo Ticket
                      </Button>
                    </div>
                  </div>
                  <p className="text-text-secondary">
                    Chave Radiográfica R2: <code className="font-mono">{selectedClaim.id}</code> • Taxa de falha acumulada do lote:{" "}
                    <strong>{selectedClaim.batch_failure_rate_percent}%</strong>
                  </p>
                  {selectedClaim.radiograph_r2_key && (
                    <a
                      href={`/api/v1/storage/files/${selectedClaim.radiograph_r2_key}`}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1 text-brand-primary underline font-medium"
                    >
                      <FileWarning className="h-3.5 w-3.5" />
                      Abrir radiografia da ocorrência
                    </a>
                  )}
                </Card>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ABA 2: SOS MESA CIRÚRGICA & DESPACHO EMERGENCIAL */}
      {activeTab === "surgical_sos" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Siren className="h-5 w-5 text-status-danger" />
                Acionar Ticket P0 — SOS Mesa Cirúrgica
              </CardTitle>
              <CardDescription>
                Abre sala de vídeo WebRTC LiveKit instantânea com engenheiro clínico e prepara remessa de emergência.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleTriggerSurgicalSos} className="space-y-3">
                <div>
                  <label className="block text-xs font-medium text-text-secondary mb-1">
                    Nome do Cirurgião em Campo Operatório *
                  </label>
                  <Input
                    required
                    value={sosSurgeonName}
                    onChange={(e) => setSosSurgeonName(e.target.value)}
                  />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-xs font-medium text-text-secondary mb-1">
                      CRO/UF *
                    </label>
                    <Input
                      required
                      value={sosCroUf}
                      onChange={(e) => setSosCroUf(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-text-secondary mb-1">
                      WhatsApp Centro Cirúrgico *
                    </label>
                    <Input
                      required
                      value={sosPhone}
                      onChange={(e) => setSosPhone(e.target.value)}
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-medium text-text-secondary mb-1">
                    Intercorrência Clínica / Instrumental Necessário *
                  </label>
                  <textarea
                    rows={3}
                    required
                    value={sosProcedureDetails}
                    onChange={(e) => setSosProcedureDetails(e.target.value)}
                    className="w-full rounded-md border border-border bg-surface-card p-2.5 text-xs text-text-main"
                  />
                </div>
                <Button type="submit" variant="danger" size="sm" className="w-full gap-1.5">
                  <Siren className="h-4 w-4" />
                  Abrir Chamado P0 & Gerar Sala LiveKit
                </Button>
              </form>
            </CardContent>
          </Card>

          <Card className="border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Truck className="h-5 w-5 text-brand-primary" />
                Despacho Emergencial DENTGO Express (1 Clique)
              </CardTitle>
              <CardDescription>
                Localiza o Micro-Hub mais próximo via Haversine e envia implante/componente reserva em até 45 min.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {!activeSosTicket ? (
                <div className="p-6 rounded-lg border border-dashed border-border text-center text-xs text-text-muted">
                  Acione um chamado SOS Mesa Cirúrgica ao lado para habilitar o despacho emergencial DENTGO.
                </div>
              ) : (
                <div className="space-y-4 text-xs">
                  <div className="p-3 rounded-lg bg-status-danger-subtle border border-status-danger/30 space-y-1">
                    <div className="flex items-center justify-between font-bold text-status-danger">
                      <span>Ticket Ativo: #{activeSosTicket.id || activeSosTicket.ticket_id}</span>
                      <Badge variant="danger">{activeSosTicket.priority}</Badge>
                    </div>
                    <p className="text-text-main">Cirurgião: {activeSosTicket.customer_name}</p>
                    {activeSosTicket.livekit_room_url && (
                      <p className="flex items-center gap-1.5 font-mono text-[11px] text-brand-primary pt-1">
                        <Video className="h-3.5 w-3.5" />
                        {activeSosTicket.livekit_room_url}
                      </p>
                    )}
                    {activeSosTicket.dentgo_order_id && (
                      <Badge variant="success" className="mt-1">
                        Pedido DENTGO Vinculado: #{activeSosTicket.dentgo_order_id}
                      </Badge>
                    )}
                  </div>

                  <div className="rounded-lg border border-border overflow-hidden">
                    <LiveKitDealRoomModal
                      inline
                      dealId={String(activeSosTicket.id)}
                      dealTitle={activeSosTicket.title}
                      contactName={activeSosTicket.customer_name}
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="block font-medium text-text-secondary">
                      SKU de Emergência
                    </label>
                    <Input
                      value={sosDispatchProduct}
                      onChange={(e) => setSosDispatchProduct(e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="block font-medium text-text-secondary">
                      Endereço do Hospital / Sala Cirúrgica
                    </label>
                    <Input
                      value={sosDispatchAddress}
                      onChange={(e) => setSosDispatchAddress(e.target.value)}
                    />
                  </div>
                  <Button
                    type="button"
                    size="sm"
                    onClick={handleDispatchDentgoSos}
                    disabled={dispatchingSos}
                    className="w-full gap-1.5"
                  >
                    <Truck className="h-4 w-4" />
                    {dispatchingSos
                      ? "Despachando Courier..."
                      : "Acionar Entrega Expressa DENTGO (SLA 45min)"}
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* ABA 3: LINHA DE CUIDADO PÓS-OPERATÓRIA B2C (24h/48h/72h/7d) */}
      {activeTab === "postop_b2c" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <HeartPulse className="h-5 w-5 text-brand-primary" />
                Iniciar Régua Pós-Operatória B2C (24h / 48h / 72h / 7d)
              </CardTitle>
              <CardDescription>
                Programa checkpoints automáticos de triagem de dor, edema, sangramento e remoção de sutura.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <form onSubmit={handleStartPostOp} className="space-y-3">
                <div className="grid grid-cols-2 gap-2">
                  <Input
                    required
                    value={poPatientName}
                    onChange={(e) => setPoPatientName(e.target.value)}
                    placeholder="Nome do Paciente *"
                  />
                  <Input
                    required
                    value={poPatientPhone}
                    onChange={(e) => setPoPatientPhone(e.target.value)}
                    placeholder="WhatsApp Paciente *"
                  />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <Input
                    required
                    value={poSurgeonName}
                    onChange={(e) => setPoSurgeonName(e.target.value)}
                    placeholder="Cirurgião Responsável *"
                  />
                  <Input
                    required
                    value={poSurgeonPhone}
                    onChange={(e) => setPoSurgeonPhone(e.target.value)}
                    placeholder="WhatsApp Cirurgião *"
                  />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <Input
                    required
                    value={poProcedure}
                    onChange={(e) => setPoProcedure(e.target.value)}
                    placeholder="Procedimento *"
                  />
                  <Input
                    type="date"
                    required
                    value={poSurgeryDate}
                    onChange={(e) => setPoSurgeryDate(e.target.value)}
                  />
                </div>
                <Button type="submit" size="sm" className="w-full">
                  Iniciar Linha de Cuidado Pós-Operatória
                </Button>
              </form>

              <div className="divide-y divide-border-subtle max-h-52 overflow-y-auto text-xs pt-2">
                {postOpSchedules.map((s) => (
                  <button
                    key={s.id}
                    type="button"
                    onClick={() => handleInspectSchedule(s.id)}
                    className="w-full py-2.5 flex items-center justify-between text-left hover:bg-surface-bg px-2 rounded"
                  >
                    <div>
                      <div className="font-semibold text-text-main">{s.patient_name}</div>
                      <div className="text-text-secondary">
                        {s.procedure_name} • Cirurgião: {s.surgeon_name}
                      </div>
                    </div>
                    <Badge
                      variant={s.status === "ALERT_TRIGGERED" ? "danger" : "success"}
                      className="text-[10px]"
                    >
                      {s.status}
                    </Badge>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="border-border">
            <CardHeader>
              <CardTitle>Triagem Clínica de Sintomas & Alerta Vermelho ao Cirurgião</CardTitle>
              <CardDescription>
                Processa o relato do paciente (texto/áudio transcrito) e abre chamado P0 caso detecte intercorrência.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {!selectedSchedule ? (
                <p className="text-xs text-text-muted py-6 text-center">
                  Inicie ou selecione uma régua pós-operatória ao lado para registrar o feedback do paciente.
                </p>
              ) : (
                <div className="space-y-4 text-xs">
                  <div className="p-3 rounded-lg bg-surface-bg border border-border space-y-1">
                    <div className="flex justify-between font-semibold text-text-main">
                      <span>Paciente: {selectedSchedule.patient_name}</span>
                      <Badge
                        variant={selectedSchedule.status === "ALERT_TRIGGERED" ? "danger" : "success"}
                      >
                        {selectedSchedule.status}
                      </Badge>
                    </div>
                    <p className="text-text-secondary">
                      Marcos Programados:{" "}
                      {selectedSchedule.milestones
                        ?.map((m) => `${m.code} (${m.target_date})`)
                        .join(" • ")}
                    </p>
                  </div>

                  <form onSubmit={handleSendPatientFeedback} className="space-y-3">
                    <Select
                      label="Marco Pós-Operatório"
                      value={feedbackMilestone}
                      onChange={(e) => setFeedbackMilestone(e.target.value)}
                      options={[
                        { value: "24h", label: "24 Horas (Triagem de Sangramento, Dor e Gelo)" },
                        { value: "48h", label: "48 Horas (Pico de Edema e Medicação)" },
                        { value: "72h", label: "72 Horas (Estabilidade de Sutura e Higienização)" },
                        { value: "7d", label: "7 Dias (Retorno Clínico para Remoção de Pontos)" },
                      ]}
                    />
                    <div>
                      <label className="block font-medium text-text-secondary mb-1">
                        Relato do Paciente via WhatsApp
                      </label>
                      <textarea
                        rows={3}
                        value={feedbackText}
                        onChange={(e) => setFeedbackText(e.target.value)}
                        className="w-full rounded-md border border-border bg-surface-card p-2.5 text-xs text-text-main"
                      />
                    </div>
                    <Button type="submit" size="sm" className="w-full">
                      Avaliar Sintomas & Disparar Protocolo Clínico
                    </Button>
                  </form>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default SupportAnvisaWorkspace;
