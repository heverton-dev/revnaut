import React, { useState, useEffect } from "react";
import {
  Phone,
  PhoneOff,
  Video,
  VideoOff,
  Mic,
  MicOff,
  Disc,
  Users,
  X,
  Shield,
  PhoneCall,
  Play,
  FileVideo,
} from "lucide-react";

export interface DealOption {
  id: string;
  title: string;
  contact_name?: string;
  company?: string;
}

export interface CallRecording {
  id: string;
  account_id: string;
  room_name: string;
  deal_id: string;
  caller_identity: string;
  receiver_identity?: string;
  call_type: string;
  status: string;
  duration_seconds: number;
  r2_recording_url?: string;
  r2_audio_key?: string;
  egress_id?: string;
  created_at: string;
}

export interface LiveKitDealRoomModalProps {
  isOpen?: boolean;
  inline?: boolean;
  onClose?: () => void;
  dealId?: string;
  dealTitle?: string;
  contactName?: string;
  contactPhone?: string;
}

export const LiveKitDealRoomModal: React.FC<LiveKitDealRoomModalProps> = ({
  isOpen = true,
  inline = false,
  onClose,
  dealId,
  dealTitle = "Suporte Emergencial SOS Mesa Cirúrgica",
  contactName = "Cirurgião em Campo Operatório",
  contactPhone = "",
}) => {
  const [deals, setDeals] = useState<DealOption[]>([]);
  const [selectedDealId, setSelectedDealId] = useState<string>(dealId || "");
  const [activeTab, setActiveTab] = useState<"video" | "voip" | "recordings">("video");
  const [isConnected, setIsConnected] = useState(false);
  const [isMicMuted, setIsMicMuted] = useState(false);
  const [isVideoMuted, setIsVideoMuted] = useState(false);
  const [isRecording] = useState(true);
  const [phoneInput, setPhoneInput] = useState(contactPhone);
  const [callStatus, setCallStatus] = useState<string>("idle");
  const [recordings, setRecordings] = useState<CallRecording[]>([]);
  const [loadingRecordings, setLoadingRecordings] = useState(false);
  const [simulatingEgress, setSimulatingEgress] = useState(false);

  // 1. Carregar Oportunidades (Deals) Dinâmicas
  useEffect(() => {
    async function loadDeals() {
      try {
        const res = await fetch("/api/v1/deals");
        if (res.ok) {
          const data = await res.json();
          const list = Array.isArray(data) ? data : Array.isArray(data?.deals) ? data.deals : [];
          setDeals(list);
          if (list.length > 0 && !dealId) {
            setSelectedDealId(list[0].id);
          }
        }
      } catch {
        // Fallback silencioso
      }
    }
    loadDeals();
  }, [dealId]);

  // 2. Carregar Gravações do Deal Selecionado
  const fetchRecordings = async () => {
    if (!selectedDealId) return;
    setLoadingRecordings(true);
    try {
      const res = await fetch(`/api/v1/communications/deals/${selectedDealId}/recordings`);
      if (res.ok) {
        const data = await res.json();
        const recList = Array.isArray(data) ? data : Array.isArray(data?.recordings) ? data.recordings : [];
        setRecordings(recList);
      }
    } catch {
      // fallback
    } finally {
      setLoadingRecordings(false);
    }
  };

  useEffect(() => {
    fetchRecordings();
  }, [selectedDealId]);

  if (!isOpen && !inline) return null;

  const currentDeal = (Array.isArray(deals) ? deals : []).find((d) => d.id === selectedDealId);
  const activeTitle = currentDeal ? currentDeal.title : dealTitle;
  const activeContact = currentDeal?.contact_name || contactName;

  const handleStartRoom = async () => {
    setCallStatus("connecting");
    try {
      const res = await fetch("/api/v1/communications/rooms/token", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          room_name: `deal-${selectedDealId}`,
          identity: "consultant_current",
          name: "Consultor Especialista Revnaut",
          deal_id: selectedDealId,
        }),
      });
      if (res.ok) {
        setIsConnected(true);
        setCallStatus("connected");
      } else {
        setCallStatus("error");
      }
    } catch {
      setCallStatus("error");
    }
  };

  const handleDialVoip = async () => {
    if (!phoneInput) return;
    setCallStatus("dialing");
    try {
      const res = await fetch("/api/v1/communications/voip/dial", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          phone_number: phoneInput,
          room_name: `deal-${selectedDealId}`,
          deal_id: selectedDealId,
        }),
      });
      if (res.ok) {
        setIsConnected(true);
        setCallStatus("calling");
      } else {
        setCallStatus("error");
      }
    } catch {
      setCallStatus("error");
    }
  };

  const handleDisconnect = () => {
    setIsConnected(false);
    setCallStatus("idle");
  };

  // 3. Simular Finalização de Gravação Egress LiveKit no R2
  const handleSimulateEgressCompleted = async () => {
    setSimulatingEgress(true);
    try {
      const payload = {
        event: "egress_ended",
        egressInfo: {
          egressId: `egress-${Date.now().toString().slice(-6)}`,
          roomName: `deal-${selectedDealId}`,
          fileResults: [
            {
              filename: `recordings/0f14ffff/${selectedDealId}_procedimento_cirurgico_${Date.now()}.mp4`,
              duration: 360,
            },
          ],
        },
      };
      const res = await fetch("/api/v1/communications/livekit/webhook", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        await fetchRecordings();
      }
    } catch {
      // fallback
    } finally {
      setSimulatingEgress(false);
    }
  };

  const content = (
    <div className="w-full max-w-3xl mx-auto rounded-2xl bg-surface-card border border-border p-6 shadow-card text-text-main">
      {/* Header com Seletor de Deal */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-border pb-4 gap-3">
        <div className="flex items-center space-x-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-primary-subtle text-brand-primary">
            <Video className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-lg font-semibold tracking-tight text-text-main">
              Comunicações WebRTC & VoIP SIP (SOS Mesa Cirúrgica)
            </h3>
            <p className="text-xs text-text-secondary">
              {activeTitle} • {activeContact}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {(Array.isArray(deals) ? deals : []).length > 0 && (
            <select
              value={selectedDealId}
              onChange={(e) => setSelectedDealId(e.target.value)}
              className="px-2.5 py-1.5 rounded-lg border border-border bg-surface-bg text-xs font-mono text-text-main"
            >
              {(Array.isArray(deals) ? deals : []).map((d) => (
                <option key={d.id} value={d.id}>
                  {d.id} - {d.title} ({d.contact_name || "Cirurgião"})
                </option>
              ))}
            </select>
          )}

          {onClose && (
            <button
              onClick={onClose}
              className="rounded-lg p-2 text-text-secondary hover:bg-surface-bg hover:text-text-main transition"
            >
              <X className="h-5 w-5" />
            </button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="mt-4 flex space-x-2 border-b border-border pb-2">
        <button
          onClick={() => setActiveTab("video")}
          className={`flex items-center space-x-2 px-4 py-2 text-sm font-medium rounded-lg transition ${
            activeTab === "video"
              ? "bg-brand-primary-subtle text-brand-primary border border-brand-primary/30"
              : "text-text-secondary hover:text-text-main hover:bg-surface-bg"
          }`}
        >
          <Video className="h-4 w-4" />
          <span>Videoconferência HD</span>
        </button>
        <button
          onClick={() => setActiveTab("voip")}
          className={`flex items-center space-x-2 px-4 py-2 text-sm font-medium rounded-lg transition ${
            activeTab === "voip"
              ? "bg-brand-primary-subtle text-brand-primary border border-brand-primary/30"
              : "text-text-secondary hover:text-text-main hover:bg-surface-bg"
          }`}
        >
          <Phone className="h-4 w-4" />
          <span>Telefonia VoIP SIP</span>
        </button>
        <button
          onClick={() => setActiveTab("recordings")}
          className={`flex items-center space-x-2 px-4 py-2 text-sm font-medium rounded-lg transition ${
            activeTab === "recordings"
              ? "bg-brand-primary-subtle text-brand-primary border border-brand-primary/30"
              : "text-text-secondary hover:text-text-main hover:bg-surface-bg"
          }`}
        >
          <Disc className="h-4 w-4" />
          <span>Gravações R2 ({recordings.length})</span>
        </button>
      </div>

      <div className="mt-6">
        {activeTab === "video" ? (
          <div className="space-y-4">
            <div className="relative aspect-video w-full rounded-xl bg-surface-bg border border-border flex flex-col items-center justify-center overflow-hidden">
              {isConnected ? (
                <div className="flex flex-col items-center space-y-3">
                  <div className="relative flex h-20 w-20 items-center justify-center rounded-full bg-brand-primary-subtle text-brand-primary animate-pulse">
                    <Users className="h-10 w-10" />
                  </div>
                  <span className="text-sm font-medium text-text-main font-mono">
                    Sala ao vivo: deal-{selectedDealId}
                  </span>
                  <div className="flex items-center space-x-2 text-xs text-status-success">
                    <span className="h-2 w-2 rounded-full bg-status-success animate-ping" />
                    <span>Egress gravando no Cloudflare R2</span>
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center space-y-3">
                  <Video className="h-12 w-12 text-text-muted" />
                  <p className="text-sm text-text-secondary">
                    Pronto para iniciar videoconferência com o cirurgião ({activeContact})
                  </p>
                  <button
                    onClick={handleStartRoom}
                    disabled={callStatus === "connecting"}
                    className="rounded-xl bg-brand-primary px-5 py-2.5 text-sm font-semibold text-text-inverse shadow-card hover:bg-brand-primary-hover transition disabled:opacity-50 cursor-pointer"
                  >
                    {callStatus === "connecting" ? "Conectando..." : "Entrar na Sala"}
                  </button>
                </div>
              )}

              {isRecording && (
                <div className="absolute top-3 left-3 flex items-center space-x-1.5 rounded-full bg-status-danger-subtle border border-status-danger/30 px-3 py-1 text-xs text-status-danger whitespace-nowrap shrink-0">
                  <Disc className="h-3 w-3 animate-spin" />
                  <span>REC R2</span>
                </div>
              )}
              <div className="absolute top-3 right-3 flex items-center space-x-1.5 rounded-full bg-surface-card border border-border px-3 py-1 text-xs text-text-secondary whitespace-nowrap shrink-0">
                <Shield className="h-3 w-3 text-brand-navy" />
                <span>Criptografia E2EE</span>
              </div>
            </div>
          </div>
        ) : activeTab === "voip" ? (
          <div className="space-y-4">
            <div className="rounded-xl bg-surface-bg border border-border p-6 space-y-4">
              <div>
                <label className="block text-xs font-medium text-text-secondary uppercase tracking-wider mb-2">
                  Número do Cirurgião / Clínica (E.164)
                </label>
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={phoneInput}
                    onChange={(e) => setPhoneInput(e.target.value)}
                    placeholder="+5511999998888"
                    className="flex-1 rounded-xl bg-surface-card border border-border px-4 py-2.5 text-sm text-text-main placeholder:text-text-muted focus:border-brand-primary focus:outline-none focus:ring-1 focus:ring-brand-primary font-mono"
                  />
                  <button
                    onClick={handleDialVoip}
                    disabled={callStatus === "dialing" || !phoneInput}
                    className="flex items-center space-x-2 rounded-xl bg-status-success px-5 py-2.5 text-sm font-semibold text-text-inverse shadow-card transition disabled:opacity-50 cursor-pointer"
                  >
                    <PhoneCall className="h-4 w-4" />
                    <span>{callStatus === "dialing" ? "Discando..." : "Discar"}</span>
                  </button>
                </div>
              </div>

              <div className="rounded-lg bg-surface-card border border-border p-3 text-xs text-text-secondary flex items-center justify-between">
                <span>Tronco SIP: LiveKit Gateway E.164</span>
                <span className="text-status-success font-semibold">Ativo</span>
              </div>
            </div>
          </div>
        ) : (
          /* Aba 3: Gravações da Sala no Cloudflare R2 */
          <div className="space-y-4">
            <div className="flex items-center justify-between bg-surface-bg p-3 rounded-xl border border-border">
              <div>
                <span className="text-xs font-bold text-text-main block">
                  Auditoria de Gravações Egress (Deal: {selectedDealId})
                </span>
                <span className="text-[11px] text-text-secondary">
                  Arquivamento seguro em bucket Cloudflare R2 com hash SHA-256 e LGPD.
                </span>
              </div>
              <button
                onClick={handleSimulateEgressCompleted}
                disabled={simulatingEgress}
                className="px-3 py-1.5 rounded-lg bg-brand-primary text-text-inverse text-xs font-medium transition hover:bg-brand-primary-hover flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
              >
                <Play className="h-3.5 w-3.5" />
                {simulatingEgress ? "Simulando..." : "Simular Webhook Egress"}
              </button>
            </div>

            {loadingRecordings ? (
              <p className="text-xs text-text-muted text-center py-6">Carregando gravações...</p>
            ) : (!Array.isArray(recordings) || recordings.length === 0) ? (
              <div className="p-8 text-center border border-border rounded-xl bg-surface-bg">
                <FileVideo className="h-8 w-8 text-text-muted mx-auto mb-2" />
                <p className="text-xs text-text-secondary">
                  Nenhuma gravação de sala WebRTC salva para esta oportunidade.
                </p>
                <button
                  onClick={handleSimulateEgressCompleted}
                  className="mt-3 px-3 py-1.5 rounded-lg border border-border bg-surface-card text-xs text-text-main hover:bg-surface-bg"
                >
                  Criar Gravação de Teste via Webhook
                </button>
              </div>
            ) : (
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {(Array.isArray(recordings) ? recordings : []).map((rec) => (
                  <div
                    key={rec.id}
                    className="p-3 rounded-xl border border-border bg-surface-bg flex items-center justify-between text-xs"
                  >
                    <div className="space-y-0.5">
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-brand-primary">{rec.id}</span>
                        <span className="px-1.5 py-0.5 rounded text-[10px] uppercase font-mono bg-status-success-subtle text-status-success border border-status-success/30 whitespace-nowrap shrink-0">
                          {rec.status}
                        </span>
                        <span className="text-[10px] text-text-muted font-mono">
                          {rec.duration_seconds}s
                        </span>
                      </div>
                      <p className="text-[11px] text-text-secondary font-mono truncate max-w-md">
                        {rec.r2_audio_key || rec.r2_recording_url || "Gravação R2"}
                      </p>
                    </div>
                    <div className="text-[10px] text-text-muted font-mono text-right">
                      {rec.created_at || "Recente"}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {isConnected && (
          <div className="mt-6 flex items-center justify-center space-x-4 border-t border-border pt-4">
            <button
              onClick={() => setIsMicMuted(!isMicMuted)}
              className={`flex h-12 w-12 items-center justify-center rounded-full transition ${
                isMicMuted
                  ? "bg-status-danger-subtle text-status-danger border border-status-danger/40"
                  : "bg-surface-bg text-text-main border border-border"
              }`}
              title={isMicMuted ? "Desmutar Microfone" : "Mutar Microfone"}
            >
              {isMicMuted ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
            </button>

            <button
              onClick={() => setIsVideoMuted(!isVideoMuted)}
              className={`flex h-12 w-12 items-center justify-center rounded-full transition ${
                isVideoMuted
                  ? "bg-status-danger-subtle text-status-danger border border-status-danger/40"
                  : "bg-surface-bg text-text-main border border-border"
              }`}
              title={isVideoMuted ? "Ligar Câmera" : "Desligar Câmera"}
            >
              {isVideoMuted ? <VideoOff className="h-5 w-5" /> : <Video className="h-5 w-5" />}
            </button>

            <button
              onClick={handleDisconnect}
              className="flex h-12 w-12 items-center justify-center rounded-full bg-status-danger text-text-inverse shadow-card transition cursor-pointer"
              title="Encerrar Chamada"
            >
              <PhoneOff className="h-5 w-5" />
            </button>
          </div>
        )}
      </div>
    </div>
  );

  if (inline) {
    return content;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-text-main/60 backdrop-blur-sm p-4">
      {content}
    </div>
  );
};

export default LiveKitDealRoomModal;
