import React, { useState } from 'react';
import { Phone, PhoneOff, Video, VideoOff, Mic, MicOff, Disc, Users, X, Shield, PhoneCall } from 'lucide-react';

interface LiveKitDealRoomModalProps {
  isOpen: boolean;
  onClose: () => void;
  dealId: string;
  dealTitle: string;
  contactName: string;
  contactPhone?: string;
}

export const LiveKitDealRoomModal: React.FC<LiveKitDealRoomModalProps> = ({
  isOpen,
  onClose,
  dealId,
  dealTitle,
  contactName,
  contactPhone = '',
}) => {
  const [activeTab, setActiveTab] = useState<'video' | 'voip'>('video');
  const [isConnected, setIsConnected] = useState(false);
  const [isMicMuted, setIsMicMuted] = useState(false);
  const [isVideoMuted, setIsVideoMuted] = useState(false);
  const [isRecording, setIsRecording] = useState(true);
  const [phoneInput, setPhoneInput] = useState(contactPhone);
  const [callStatus, setCallStatus] = useState<string>('idle');
  const [callDuration, setCallDuration] = useState<number>(0);

  if (!isOpen) return null;

  const handleStartRoom = async () => {
    setCallStatus('connecting');
    try {
      const res = await fetch('/api/v1/communications/rooms/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          room_name: `deal-${dealId}`,
          identity: 'consultant_current',
          name: 'Consultor Revnaut',
          deal_id: dealId,
        }),
      });
      if (res.ok) {
        setIsConnected(true);
        setCallStatus('connected');
      } else {
        setCallStatus('error');
      }
    } catch {
      setCallStatus('error');
    }
  };

  const handleDialVoip = async () => {
    if (!phoneInput) return;
    setCallStatus('dialing');
    try {
      const res = await fetch('/api/v1/communications/voip/dial', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          phone_number: phoneInput,
          room_name: `deal-${dealId}`,
          deal_id: dealId,
        }),
      });
      if (res.ok) {
        setIsConnected(true);
        setCallStatus('calling');
      } else {
        setCallStatus('error');
      }
    } catch {
      setCallStatus('error');
    }
  };

  const handleDisconnect = () => {
    setIsConnected(false);
    setCallStatus('idle');
    setCallDuration(0);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="w-full max-w-2xl rounded-2xl bg-slate-900 border border-slate-800 p-6 shadow-2xl text-slate-100">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center space-x-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-500/10 text-cyan-400">
              <Video className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-lg font-semibold tracking-tight text-white">
                Comunicações WebRTC & VoIP SIP
              </h3>
              <p className="text-xs text-slate-400">
                {dealTitle} • {contactName}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-2 text-slate-400 hover:bg-slate-800 hover:text-white transition"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Tabs */}
        <div className="mt-4 flex space-x-2 border-b border-slate-800 pb-2">
          <button
            onClick={() => setActiveTab('video')}
            className={`flex items-center space-x-2 px-4 py-2 text-sm font-medium rounded-lg transition ${
              activeTab === 'video'
                ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
          >
            <Video className="h-4 w-4" />
            <span>Videoconferência HD</span>
          </button>
          <button
            onClick={() => setActiveTab('voip')}
            className={`flex items-center space-x-2 px-4 py-2 text-sm font-medium rounded-lg transition ${
              activeTab === 'voip'
                ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
          >
            <Phone className="h-4 w-4" />
            <span>Telefonia VoIP SIP</span>
          </button>
        </div>

        {/* Body Content */}
        <div className="mt-6">
          {activeTab === 'video' ? (
            <div className="space-y-4">
              <div className="relative aspect-video w-full rounded-xl bg-slate-950 border border-slate-800 flex flex-col items-center justify-center overflow-hidden">
                {isConnected ? (
                  <div className="flex flex-col items-center space-y-3">
                    <div className="relative flex h-20 w-20 items-center justify-center rounded-full bg-cyan-500/20 text-cyan-400 animate-pulse">
                      <Users className="h-10 w-10" />
                    </div>
                    <span className="text-sm font-medium text-slate-200">
                      Sala ao vivo: deal-{dealId}
                    </span>
                    <div className="flex items-center space-x-2 text-xs text-emerald-400">
                      <span className="h-2 w-2 rounded-full bg-emerald-500 animate-ping" />
                      <span>Egress gravando no Cloudflare R2</span>
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col items-center space-y-3">
                    <Video className="h-12 w-12 text-slate-600" />
                    <p className="text-sm text-slate-400">
                      Pronto para iniciar videoconferência com o cirurgião
                    </p>
                    <button
                      onClick={handleStartRoom}
                      disabled={callStatus === 'connecting'}
                      className="rounded-xl bg-cyan-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg hover:bg-cyan-500 transition disabled:opacity-50"
                    >
                      {callStatus === 'connecting' ? 'Conectando...' : 'Entrar na Sala'}
                    </button>
                  </div>
                )}

                {/* Status Badges */}
                {isRecording && (
                  <div className="absolute top-3 left-3 flex items-center space-x-1.5 rounded-full bg-rose-500/20 border border-rose-500/30 px-3 py-1 text-xs text-rose-400">
                    <Disc className="h-3 w-3 animate-spin" />
                    <span>REC R2</span>
                  </div>
                )}
                <div className="absolute top-3 right-3 flex items-center space-x-1.5 rounded-full bg-slate-800/80 px-3 py-1 text-xs text-slate-300">
                  <Shield className="h-3 w-3 text-cyan-400" />
                  <span>Criptografia E2EE</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="rounded-xl bg-slate-950 border border-slate-800 p-6 space-y-4">
                <div>
                  <label className="block text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">
                    Número do Cirurgião / Clínica (E.164)
                  </label>
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={phoneInput}
                      onChange={(e) => setPhoneInput(e.target.value)}
                      placeholder="+5511999998888"
                      className="flex-1 rounded-xl bg-slate-900 border border-slate-700 px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500"
                    />
                    <button
                      onClick={handleDialVoip}
                      disabled={callStatus === 'dialing' || !phoneInput}
                      className="flex items-center space-x-2 rounded-xl bg-emerald-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg hover:bg-emerald-500 transition disabled:opacity-50"
                    >
                      <PhoneCall className="h-4 w-4" />
                      <span>{callStatus === 'dialing' ? 'Discando...' : 'Discar'}</span>
                    </button>
                  </div>
                </div>

                <div className="rounded-lg bg-slate-900/60 border border-slate-800 p-3 text-xs text-slate-400 flex items-center justify-between">
                  <span>Tronco SIP: LiveKit Gateway E.164</span>
                  <span className="text-emerald-400">Ativo</span>
                </div>
              </div>
            </div>
          )}

          {/* Call Controls Toolbar */}
          {isConnected && (
            <div className="mt-6 flex items-center justify-center space-x-4 border-t border-slate-800 pt-4">
              <button
                onClick={() => setIsMicMuted(!isMicMuted)}
                className={`flex h-12 w-12 items-center justify-center rounded-full transition ${
                  isMicMuted
                    ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40'
                    : 'bg-slate-800 text-slate-200 hover:bg-slate-700'
                }`}
                title={isMicMuted ? 'Desmutar Microfone' : 'Mutar Microfone'}
              >
                {isMicMuted ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
              </button>

              <button
                onClick={() => setIsVideoMuted(!isVideoMuted)}
                className={`flex h-12 w-12 items-center justify-center rounded-full transition ${
                  isVideoMuted
                    ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40'
                    : 'bg-slate-800 text-slate-200 hover:bg-slate-700'
                }`}
                title={isVideoMuted ? 'Ligar Câmera' : 'Desligar Câmera'}
              >
                {isVideoMuted ? <VideoOff className="h-5 w-5" /> : <Video className="h-5 w-5" />}
              </button>

              <button
                onClick={handleDisconnect}
                className="flex h-12 w-12 items-center justify-center rounded-full bg-rose-600 text-white shadow-lg hover:bg-rose-500 transition"
                title="Encerrar Chamada"
              >
                <PhoneOff className="h-5 w-5" />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
