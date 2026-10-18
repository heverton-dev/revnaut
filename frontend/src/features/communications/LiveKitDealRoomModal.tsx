import React, { useState } from "react";
import { Phone, PhoneOff, Video, VideoOff, Mic, MicOff, Disc, Users, X, Shield, PhoneCall } from "lucide-react";

export interface LiveKitDealRoomModalProps {
  isOpen?: boolean;
  inline?: boolean;
  onClose?: () => void;
  dealId: string;
  dealTitle: string;
  contactName: string;
  contactPhone?: string;
}

export const LiveKitDealRoomModal: React.FC<LiveKitDealRoomModalProps> = ({
  isOpen = true,
  inline = false,
  onClose,
  dealId,
  dealTitle,
  contactName,
  contactPhone = "",
}) => {
  const [activeTab, setActiveTab] = useState<"video" | "voip">("video");
  const [isConnected, setIsConnected] = useState(false);
  const [isMicMuted, setIsMicMuted] = useState(false);
  const [isVideoMuted, setIsVideoMuted] = useState(false);
  const [isRecording] = useState(true);
  const [phoneInput, setPhoneInput] = useState(contactPhone);
  const [callStatus, setCallStatus] = useState<string>("idle");

  if (!isOpen && !inline) return null;

  const handleStartRoom = async () => {
    setCallStatus("connecting");
    try {
      const res = await fetch("/api/v1/communications/rooms/token", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          room_name: `deal-${dealId}`,
          identity: "consultant_current",
          name: "Consultor Revnaut",
          deal_id: dealId,
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
          room_name: `deal-${dealId}`,
          deal_id: dealId,
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

  const content = (
    <div className="w-full max-w-3xl mx-auto rounded-2xl bg-surface-card border border-border p-6 shadow-card text-text-main">
      <div className="flex items-center justify-between border-b border-border pb-4">
        <div className="flex items-center space-x-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-primary-subtle text-brand-primary">
            <Video className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-lg font-semibold tracking-tight text-text-main">
              Comunicações WebRTC & VoIP SIP (SOS Mesa Cirúrgica)
            </h3>
            <p className="text-xs text-text-secondary">
              {dealTitle} • {contactName}
            </p>
          </div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="rounded-lg p-2 text-text-secondary hover:bg-surface-bg hover:text-text-main transition"
          >
            <X className="h-5 w-5" />
          </button>
        )}
      </div>

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
                  <span className="text-sm font-medium text-text-main">
                    Sala ao vivo: deal-{dealId}
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
                    Pronto para iniciar videoconferência com o cirurgião
                  </p>
                  <button
                    onClick={handleStartRoom}
                    disabled={callStatus === "connecting"}
                    className="rounded-xl bg-brand-primary px-5 py-2.5 text-sm font-semibold text-text-inverse shadow-card hover:bg-brand-primary-hover transition disabled:opacity-50"
                  >
                    {callStatus === "connecting" ? "Conectando..." : "Entrar na Sala"}
                  </button>
                </div>
              )}

              {isRecording && (
                <div className="absolute top-3 left-3 flex items-center space-x-1.5 rounded-full bg-status-danger-subtle border border-status-danger/30 px-3 py-1 text-xs text-status-danger">
                  <Disc className="h-3 w-3 animate-spin" />
                  <span>REC R2</span>
                </div>
              )}
              <div className="absolute top-3 right-3 flex items-center space-x-1.5 rounded-full bg-surface-card border border-border px-3 py-1 text-xs text-text-secondary">
                <Shield className="h-3 w-3 text-brand-navy" />
                <span>Criptografia E2EE</span>
              </div>
            </div>
          </div>
        ) : (
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
                    className="flex-1 rounded-xl bg-surface-card border border-border px-4 py-2.5 text-sm text-text-main placeholder:text-text-muted focus:border-brand-primary focus:outline-none focus:ring-1 focus:ring-brand-primary"
                  />
                  <button
                    onClick={handleDialVoip}
                    disabled={callStatus === "dialing" || !phoneInput}
                    className="flex items-center space-x-2 rounded-xl bg-status-success px-5 py-2.5 text-sm font-semibold text-text-inverse shadow-card transition disabled:opacity-50"
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
              className="flex h-12 w-12 items-center justify-center rounded-full bg-status-danger text-text-inverse shadow-card transition"
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
