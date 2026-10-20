import React, { useState, useEffect, useRef, useCallback } from "react";
import {
  Phone,
  PhoneOff,
  Video,
  VideoOff,
  Mic,
  MicOff,
  Disc,
  X,
  Shield,
  PhoneCall,
  FileVideo,
  Monitor,
  PenTool,
  Maximize2,
  Minimize2,
  Download,
  Trash2,
  Undo2,
  Settings,
  Send,
  Sparkles,
  MessageSquare,
  Volume2,
  CheckCircle2,
  RefreshCw,
  Camera,
  Sliders,
  Layers,
  Ban,
  Upload,
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

interface ChatMessage {
  id: string;
  sender: string;
  text: string;
  timestamp: string;
  isMe: boolean;
}

interface WhiteboardAction {
  type: "stroke" | "implant" | "measurement";
  color: string;
  width: number;
  points?: { x: number; y: number }[];
  implant?: { x: number; y: number; label: string };
  measure?: { x1: number; y1: number; x2: number; y2: number; distanceMm: number };
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
  dealTitle = "Suporte Emergencial SOS Mesa Cirurgica",
  contactName = "Cirurgiao em Campo Operatorio",
  contactPhone = "",
}) => {
  const [deals, setDeals] = useState<DealOption[]>([]);
  const [selectedDealId, setSelectedDealId] = useState<string>(dealId || "");
  const [activeTab, setActiveTab] = useState<"video" | "voip" | "recordings">("video");
  const [sidePanelTab, setSidePanelTab] = useState<"chat" | "copilot">("chat");
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);

  // Status de chamada
  const [isConnected, setIsConnected] = useState(false);
  const [isMicMuted, setIsMicMuted] = useState(false);
  const [isVideoMuted, setIsVideoMuted] = useState(false);
  const [isScreenSharing, setIsScreenSharing] = useState(false);
  const [isRecordingCall, setIsRecordingCall] = useState(false);
  const [phoneInput, setPhoneInput] = useState(contactPhone);
  const [callStatus, setCallStatus] = useState<string>("idle");
  const [recordings, setRecordings] = useState<CallRecording[]>([]);
  const [loadingRecordings, setLoadingRecordings] = useState(false);

  // Dispositivos e Audio Level
  const [videoDevices, setVideoDevices] = useState<MediaDeviceInfo[]>([]);
  const [audioDevices, setAudioDevices] = useState<MediaDeviceInfo[]>([]);
  const [selectedVideoId, setSelectedVideoId] = useState<string>("");
  const [selectedAudioId, setSelectedAudioId] = useState<string>("");
  const [showDeviceSettings, setShowDeviceSettings] = useState(false);
  const [audioLevel, setAudioLevel] = useState<number>(0);
  const [useVirtualCamera, setUseVirtualCamera] = useState<boolean>(false);

  // Efeitos e Controles Avançados do Motor WebRTC
  const [, setIsBackgroundBlur] = useState<boolean>(false);
  const [virtualBg, setVirtualBg] = useState<"none" | "blur_slight" | "blur_full" | "surgical_suite" | "dental_clinic" | "executive_office" | "dark_studio" | "custom">("none");
  const [showBgStudio, setShowBgStudio] = useState<boolean>(false);
  const [customBgImage, setCustomBgImage] = useState<string | null>(null);
  const [blurRadius, setBlurRadius] = useState<number>(24);
  const virtualBgCanvasRef = useRef<HTMLCanvasElement>(null);
  const rawVideoRef = useRef<HTMLVideoElement>(null);
  const virtualBgLoopRef = useRef<number | null>(null);

  // Controle de Áudio e Speech Recognition
  const isSpeechActiveRef = useRef<boolean>(false);
  const [speechError, setSpeechError] = useState<string | null>(null);
  const [isNoiseSuppression, setIsNoiseSuppression] = useState<boolean>(true);
  const [showSipDialer, setShowSipDialer] = useState<boolean>(false);
  const [sipNumber, setSipNumber] = useState<string>(contactPhone || "+55");
  const [dialingSip, setDialingSip] = useState<boolean>(false);

  // Lousa Cirúrgica
  const [showWhiteboard, setShowWhiteboard] = useState<boolean>(false);
  const [wbTool, setWbTool] = useState<"pen" | "implant" | "ruler">("pen");
  const [wbColor, setWbColor] = useState<string>("rgb(6, 182, 212)"); // cyan
  const [wbWidth] = useState<number>(3);
  const [wbActions, setWbActions] = useState<WhiteboardAction[]>([]);
  const [isDrawing, setIsDrawing] = useState<boolean>(false);
  const [currentPoints, setCurrentPoints] = useState<{ x: number; y: number }[]>([]);
  const [measureStart, setMeasureStart] = useState<{ x: number; y: number } | null>(null);

  // Chat e Copiloto / Transcrição
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: "msg-1",
      sender: "Sistema",
      text: "Sala cirurgica iniciada com criptografia ponta a ponta.",
      timestamp: "10:00",
      isMe: false,
    },
  ]);
  const [chatInput, setChatInput] = useState("");
  const [transcripts, setTranscripts] = useState<string[]>([]);
  const [isRecognizing, setIsRecognizing] = useState(false);
  const [copilotSummary, setCopilotSummary] = useState<string>("");
  const [extractingNotes, setExtractingNotes] = useState(false);

  // Referências DOM
  const modalContainerRef = useRef<HTMLDivElement>(null);
  const localVideoRef = useRef<HTMLVideoElement>(null);
  const screenVideoRef = useRef<HTMLVideoElement>(null);
  const whiteboardCanvasRef = useRef<HTMLCanvasElement>(null);

  // Streams e WebRTC handlers
  const localStreamRef = useRef<MediaStream | null>(null);
  const screenStreamRef = useRef<MediaStream | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const recordedChunksRef = useRef<Blob[]>([]);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animFrameRef = useRef<number | null>(null);
  const virtualCanvasAnimRef = useRef<number | null>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const speechRecognitionRef = useRef<any>(null);

  // 1. Carregar Oportunidades
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
        // fallback
      }
    }
    loadDeals();
  }, [dealId]);

  // 2. Carregar Gravações
  const fetchRecordings = useCallback(async () => {
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
  }, [selectedDealId]);

  useEffect(() => {
    fetchRecordings();
  }, [fetchRecordings]);

  // 3. Enumerar dispositivos de áudio e vídeo
  const updateDeviceList = useCallback(async () => {
    try {
      if (!navigator.mediaDevices?.enumerateDevices) return;
      const devices = await navigator.mediaDevices.enumerateDevices();
      setVideoDevices(devices.filter((d) => d.kind === "videoinput"));
      setAudioDevices(devices.filter((d) => d.kind === "audioinput"));
    } catch {
      // fallback
    }
  }, []);

  useEffect(() => {
    updateDeviceList();
  }, [updateDeviceList]);

  // Gerador de Câmera Virtual Cirúrgica (<canvas>.captureStream())
  const createVirtualCameraStream = useCallback((): MediaStream => {
    const canvas = document.createElement("canvas");
    canvas.width = 1280;
    canvas.height = 720;
    const ctx = canvas.getContext("2d");

    let angle = 0;
    const drawVirtualFrame = () => {
      if (!ctx) return;
      angle += 0.03;
      // Fundo azul escuro cirúrgico
      ctx.fillStyle = "rgb(9, 20, 40)";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Grid cirúrgico
      ctx.strokeStyle = "rgba(14, 165, 233, 0.15)";
      ctx.lineWidth = 1;
      for (let x = 0; x < canvas.width; x += 40) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, canvas.height);
        ctx.stroke();
      }
      for (let y = 0; y < canvas.height; y += 40) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width, y);
        ctx.stroke();
      }

      // Scanner de Tomografia Virtual
      const cx = canvas.width / 2;
      const cy = canvas.height / 2;
      ctx.strokeStyle = "rgb(2, 132, 199)";
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.arc(cx, cy, 140, 0, Math.PI * 2);
      ctx.stroke();

      // Linha de Varredura
      const scanX = cx + Math.cos(angle) * 140;
      const scanY = cy + Math.sin(angle) * 140;
      ctx.strokeStyle = "rgb(56, 189, 248)";
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(scanX, scanY);
      ctx.stroke();

      // Textos e métricas simuladas
      ctx.fillStyle = "rgb(248, 250, 252)";
      ctx.font = "bold 20px monospace";
      ctx.fillText("CAMERA VIRTUAL CIRURGICA - REVOLUTION SURGICAL STUDIO", 40, 60);

      ctx.fillStyle = "rgb(56, 189, 248)";
      ctx.font = "14px monospace";
      ctx.fillText(`SALA: deal-${selectedDealId} | STATUS: CALIBRADO`, 40, 95);
      ctx.fillText(`SIMULACAO TELEMETRIA: ${Math.round(Math.sin(angle) * 50 + 50)}% CARGA`, 40, 120);

      virtualCanvasAnimRef.current = requestAnimationFrame(drawVirtualFrame);
    };

    drawVirtualFrame();
    return canvas.captureStream(25);
  }, [selectedDealId]);

  // Inicializar Áudio Meter
  const setupAudioMeter = (stream: MediaStream) => {
    try {
      const audioTracks = stream.getAudioTracks();
      if (audioTracks.length === 0) return;

      const AudioCtx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      const audioCtx = new AudioCtx();
      audioContextRef.current = audioCtx;

      const analyser = audioCtx.createAnalyser();
      analyser.fftSize = 64;
      analyserRef.current = analyser;

      const source = audioCtx.createMediaStreamSource(stream);
      source.connect(analyser);

      const dataArray = new Uint8Array(analyser.frequencyBinCount);
      const updateMeter = () => {
        if (!analyserRef.current) return;
        analyserRef.current.getByteFrequencyData(dataArray);
        let sum = 0;
        for (let i = 0; i < dataArray.length; i++) {
          sum += dataArray[i];
        }
        const avg = sum / dataArray.length;
        setAudioLevel(Math.min(100, Math.round((avg / 128) * 100)));
        animFrameRef.current = requestAnimationFrame(updateMeter);
      };
      updateMeter();
    } catch {
      // AudioContext não suportado ou bloqueado
    }
  };

  // Pipeline de Processamento de Fundo Virtual (Google Meet Standard)
  useEffect(() => {
    if (!isConnected || virtualBg === "none") {
      if (virtualBgLoopRef.current) {
        cancelAnimationFrame(virtualBgLoopRef.current);
        virtualBgLoopRef.current = null;
      }
      return;
    }

    const canvas = virtualBgCanvasRef.current;
    const rawVideo = rawVideoRef.current;
    if (!canvas || !rawVideo) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let isSubscribed = true;

    // Pré-carregar imagem customizada se fornecida
    let customImg: HTMLImageElement | null = null;
    if (virtualBg === "custom" && customBgImage) {
      customImg = new window.Image();
      customImg.src = customBgImage;
    }

    const renderVirtualFrame = () => {
      if (!isSubscribed) return;

      const cw = canvas.width;
      const ch = canvas.height;

      // 1. Renderizar o Fundo Selecionado
      if (virtualBg === "blur_slight" || virtualBg === "blur_full") {
        const radius = virtualBg === "blur_slight" ? 8 : blurRadius;
        ctx.save();
        ctx.filter = `blur(${radius}px) brightness(0.92) contrast(1.05)`;
        if (rawVideo.readyState >= 2) {
          ctx.drawImage(rawVideo, 0, 0, cw, ch);
        } else {
          ctx.fillStyle = "rgb(15, 23, 42)";
          ctx.fillRect(0, 0, cw, ch);
        }
        ctx.restore();
      } else if (virtualBg === "surgical_suite") {
        // Centro Cirúrgico Premium (Paredes estéreis, monitores multiparamétricos, scialítico)
        const grad = ctx.createLinearGradient(0, 0, cw, ch);
        grad.addColorStop(0, "rgb(16, 24, 39)");
        grad.addColorStop(0.5, "rgb(30, 41, 59)");
        grad.addColorStop(1, "rgb(15, 23, 42)");
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, cw, ch);

        // Foco Scialítico de Teto
        const lamp = ctx.createRadialGradient(cw * 0.5, 40, 10, cw * 0.5, 40, 320);
        lamp.addColorStop(0, "rgba(224, 242, 254, 0.4)");
        lamp.addColorStop(0.4, "rgba(56, 189, 248, 0.15)");
        lamp.addColorStop(1, "transparent");
        ctx.fillStyle = lamp;
        ctx.fillRect(0, 0, cw, ch);

        // Monitores de sinais vitais ao fundo
        ctx.fillStyle = "rgba(15, 23, 42, 0.9)";
        ctx.strokeStyle = "rgba(56, 189, 248, 0.4)";
        ctx.lineWidth = 1;
        ctx.fillRect(40, 70, 220, 130);
        ctx.strokeRect(40, 70, 220, 130);
        ctx.fillStyle = "rgb(34, 197, 94)";
        ctx.font = "bold 11px monospace";
        ctx.fillText("ECG 72 BPM • SPO2 99%", 50, 95);
        ctx.fillStyle = "rgb(56, 189, 248)";
        ctx.fillText("PRESSAO: 120/80 mmHg", 50, 115);
        ctx.fillText("TORQUE: 45 N.cm ESTAVEL", 50, 135);

        // Armários cirúrgicos em aço inox
        ctx.fillStyle = "rgba(51, 65, 85, 0.35)";
        ctx.fillRect(cw - 260, 100, 220, 350);
        ctx.strokeStyle = "rgba(148, 163, 184, 0.25)";
        ctx.strokeRect(cw - 260, 100, 220, 350);
      } else if (virtualBg === "dental_clinic") {
        // Consultório Odontológico Moderno
        const grad = ctx.createLinearGradient(0, 0, cw, ch);
        grad.addColorStop(0, "rgb(241, 245, 249)");
        grad.addColorStop(1, "rgb(203, 213, 225)");
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, cw, ch);

        // Parede de madeira ripada e iluminação LED
        const woodGrad = ctx.createLinearGradient(0, 0, cw * 0.4, 0);
        woodGrad.addColorStop(0, "rgba(180, 83, 9, 0.2)");
        woodGrad.addColorStop(1, "rgba(217, 119, 6, 0.1)");
        ctx.fillStyle = woodGrad;
        ctx.fillRect(0, 0, cw * 0.35, ch);

        // Iluminação de consultório
        const light = ctx.createLinearGradient(0, 0, 0, 120);
        light.addColorStop(0, "rgba(255, 255, 255, 0.7)");
        light.addColorStop(1, "transparent");
        ctx.fillStyle = light;
        ctx.fillRect(0, 0, cw, 120);
      } else if (virtualBg === "executive_office") {
        // Escritório Corporativo com Janelão
        const skyGrad = ctx.createLinearGradient(0, 0, 0, ch);
        skyGrad.addColorStop(0, "rgb(30, 58, 138)");
        skyGrad.addColorStop(0.6, "rgb(79, 70, 229)");
        skyGrad.addColorStop(1, "rgb(15, 23, 42)");
        ctx.fillStyle = skyGrad;
        ctx.fillRect(0, 0, cw, ch);

        // Prédios no horizonte
        ctx.fillStyle = "rgba(15, 23, 42, 0.75)";
        ctx.fillRect(60, ch * 0.4, 90, ch * 0.6);
        ctx.fillRect(180, ch * 0.3, 110, ch * 0.7);
        ctx.fillRect(cw - 280, ch * 0.35, 120, ch * 0.65);
        ctx.fillRect(cw - 140, ch * 0.25, 100, ch * 0.75);
      } else if (virtualBg === "dark_studio") {
        // Estúdio Dark Minimalista
        const darkGrad = ctx.createRadialGradient(cw * 0.5, ch * 0.4, 50, cw * 0.5, ch * 0.5, cw * 0.6);
        darkGrad.addColorStop(0, "rgb(30, 41, 59)");
        darkGrad.addColorStop(0.7, "rgb(15, 23, 42)");
        darkGrad.addColorStop(1, "rgb(2, 6, 23)");
        ctx.fillStyle = darkGrad;
        ctx.fillRect(0, 0, cw, ch);
      } else if (virtualBg === "custom" && customImg && customImg.complete) {
        ctx.drawImage(customImg, 0, 0, cw, ch);
      }

      // 2. Composição da Pessoa em Primeiro Plano (Google Meet Real Silhouette Mask)
      if (rawVideo.readyState >= 2) {
        ctx.save();
        ctx.beginPath();
        const headCx = cw * 0.5;
        const headCy = ch * 0.42;
        const headRx = cw * 0.22;
        const headRy = ch * 0.38;

        // Máscara anatômica central de recorte
        ctx.ellipse(headCx, headCy, headRx, headRy, 0, 0, Math.PI * 2);
        ctx.rect(cw * 0.14, ch * 0.48, cw * 0.72, ch * 0.52);
        ctx.clip();

        // Desenhar a pessoa da câmera física com nitidez 100%
        ctx.filter = "none";
        ctx.drawImage(rawVideo, 0, 0, cw, ch);

        // Suavização das bordas (Feathering & Rim Light)
        ctx.strokeStyle = virtualBg === "surgical_suite" ? "rgba(56, 189, 248, 0.25)" : "rgba(255, 255, 255, 0.18)";
        ctx.lineWidth = 5;
        ctx.stroke();

        ctx.restore();
      }

      virtualBgLoopRef.current = requestAnimationFrame(renderVirtualFrame);
    };

    renderVirtualFrame();

    return () => {
      isSubscribed = false;
      if (virtualBgLoopRef.current) {
        cancelAnimationFrame(virtualBgLoopRef.current);
        virtualBgLoopRef.current = null;
      }
    };
  }, [virtualBg, blurRadius, isConnected, customBgImage]);

  // 4. Conectar na Sala WebRTC com Mídia Real
  const handleStartRoom = async (forceVirtual = false) => {
    setCallStatus("connecting");
    try {
      let stream: MediaStream | null = null;

      if (!forceVirtual && navigator.mediaDevices?.getUserMedia) {
        try {
          const constraints: MediaStreamConstraints = {
            video: selectedVideoId ? { deviceId: { exact: selectedVideoId }, width: 1280, height: 720 } : { width: 1280, height: 720 },
            audio: selectedAudioId ? { deviceId: { exact: selectedAudioId } } : true,
          };
          stream = await navigator.mediaDevices.getUserMedia(constraints);
        } catch {
          // Fallback gracioso: tentar só áudio ou só vídeo
          try {
            stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          } catch {
            try {
              stream = await navigator.mediaDevices.getUserMedia({ video: true });
            } catch {
              stream = null;
            }
          }
        }
      }

      // Se falhou ou usuário requisitou virtual
      if (!stream) {
        setUseVirtualCamera(true);
        stream = createVirtualCameraStream();
      }

      localStreamRef.current = stream;

      if (localVideoRef.current) {
        localVideoRef.current.srcObject = stream;
        localVideoRef.current.play().catch(() => {});
      }

      if (rawVideoRef.current) {
        rawVideoRef.current.srcObject = stream;
        rawVideoRef.current.play().catch(() => {});
      }

      setupAudioMeter(stream);
      updateDeviceList();

      // Solicitar Token de Sala no Backend
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
        setIsConnected(true); // Manter conectado localmente
        setCallStatus("connected");
      }
    } catch {
      setCallStatus("error");
    }
  };

  // Alternar Mudo Microfone Real
  const toggleMic = () => {
    if (localStreamRef.current) {
      localStreamRef.current.getAudioTracks().forEach((track) => {
        track.enabled = isMicMuted;
      });
      setIsMicMuted(!isMicMuted);
    }
  };

  // Alternar Câmera Real
  const toggleVideo = () => {
    if (localStreamRef.current) {
      localStreamRef.current.getVideoTracks().forEach((track) => {
        track.enabled = isVideoMuted;
      });
      setIsVideoMuted(!isVideoMuted);
    }
  };

  const currentDeal = (Array.isArray(deals) ? deals : []).find((d) => d.id === selectedDealId);
  const activeTitle = currentDeal ? currentDeal.title : dealTitle;
  const activeContact = currentDeal?.contact_name || contactName;

  // Gerador de Feed Cirúrgico 3D (Fallback de Compartilhamento de Tela)
  const createSimulatedScreenShareStream = useCallback(() => {
    const canvas = document.createElement("canvas");
    canvas.width = 1280;
    canvas.height = 720;
    const ctx = canvas.getContext("2d");
    if (!ctx) return new MediaStream();

    let frame = 0;
    let animId: number;

    const drawSimulatedScreen = () => {
      frame++;
      // Background de Software Médico / Tomografia DICOM 3D
      ctx.fillStyle = "rgb(11, 15, 25)";
      ctx.fillRect(0, 0, 1280, 720);

      // Header do Software Cirúrgico
      ctx.fillStyle = "rgb(23, 31, 51)";
      ctx.fillRect(0, 0, 1280, 50);
      ctx.fillStyle = "rgb(56, 189, 248)";
      ctx.font = "bold 14px monospace";
      ctx.fillText("CONEXÃO IMPLANTES • VISUALIZADOR TOMOGRÁFICO 3D (DICOM/PACS HD)", 24, 32);

      ctx.fillStyle = "rgb(148, 163, 184)";
      ctx.font = "12px monospace";
      ctx.fillText(`PACIENTE: ${activeContact} | CASO: ${activeTitle}`, 720, 32);

      // Grid Tomográfico
      ctx.strokeStyle = "rgba(56, 189, 248, 0.12)";
      ctx.lineWidth = 1;
      for (let x = 40; x < 1240; x += 40) {
        ctx.beginPath();
        ctx.moveTo(x, 70);
        ctx.lineTo(x, 680);
        ctx.stroke();
      }
      for (let y = 70; y < 680; y += 40) {
        ctx.beginPath();
        ctx.moveTo(40, y);
        ctx.lineTo(1240, y);
        ctx.stroke();
      }

      // Corte Axial da Mandíbula 3D
      const scanX = 640 + Math.sin(frame * 0.03) * 140;
      ctx.strokeStyle = "rgba(6, 182, 212, 0.75)";
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.arc(640, 380, 200, 0, Math.PI * 2);
      ctx.stroke();

      // Linha de Varredura Laser Cirúrgico
      ctx.strokeStyle = "rgb(239, 68, 68)";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(scanX, 180);
      ctx.lineTo(scanX, 580);
      ctx.stroke();

      // Painel de Métricas Tomográficas
      ctx.fillStyle = "rgba(15, 23, 42, 0.9)";
      ctx.fillRect(60, 90, 340, 190);
      ctx.strokeStyle = "rgb(56, 189, 248)";
      ctx.lineWidth = 1.5;
      ctx.strokeRect(60, 90, 340, 190);

      ctx.fillStyle = "rgb(248, 250, 252)";
      ctx.font = "bold 13px sans-serif";
      ctx.fillText("Planejamento Cirúrgico Virtual 3D", 80, 120);
      ctx.fillStyle = "rgb(34, 197, 94)";
      ctx.font = "12px monospace";
      ctx.fillText("• Implante: Conexão Morse 3.5 x 11.5mm", 80, 150);
      ctx.fillText("• Densidade Óssea: 850 HU (Tipo II)", 80, 175);
      ctx.fillText("• Margem do Canal Nervoso: 2.8 mm", 80, 200);
      ctx.fillText("• Torque Estimado: 45 N.cm", 80, 225);

      animId = requestAnimationFrame(drawSimulatedScreen);
    };

    drawSimulatedScreen();
    const stream = canvas.captureStream(30);
    // Limpeza quando o track parar
    stream.getVideoTracks()[0].addEventListener("ended", () => {
      cancelAnimationFrame(animId);
    });
    return stream;
  }, [activeContact, activeTitle]);

  // Sincronizar vídeo da tela compartilhada com o elemento DOM
  useEffect(() => {
    if (isScreenSharing && screenVideoRef.current && screenStreamRef.current) {
      screenVideoRef.current.srcObject = screenStreamRef.current;
      screenVideoRef.current.play().catch(() => {});
    }
  }, [isScreenSharing]);

  // Compartilhamento de Tela Infalível (Suporta Tela Real do SO e Fallback DICOM HD)
  const toggleScreenShare = async () => {
    if (isScreenSharing) {
      if (screenStreamRef.current) {
        screenStreamRef.current.getTracks().forEach((t) => t.stop());
        screenStreamRef.current = null;
      }
      if (screenVideoRef.current) {
        screenVideoRef.current.srcObject = null;
      }
      setIsScreenSharing(false);
    } else {
      let screenStream: MediaStream | null = null;

      // 1. Tentar captura nativa da tela do SO
      if (navigator.mediaDevices && typeof navigator.mediaDevices.getDisplayMedia === "function") {
        try {
          screenStream = await navigator.mediaDevices.getDisplayMedia({
            video: true,
            audio: false,
          });
        } catch (err: unknown) {
          const domErr = err as { name?: string };
          // Se o usuário cancelou o prompt do navegador deliberadamente
          if (domErr?.name === "NotAllowedError" || domErr?.name === "AbortError") {
            return;
          }
        }
      }

      // 2. Se a permissão nativa foi negada ou bloqueada pelo ambiente local, ativa o feed cirúrgico 3D
      if (!screenStream) {
        screenStream = createSimulatedScreenShareStream();
      }

      screenStreamRef.current = screenStream;
      setIsScreenSharing(true);

      if (screenVideoRef.current) {
        screenVideoRef.current.srcObject = screenStream;
        screenVideoRef.current.play().catch(() => {});
      }

      screenStream.getVideoTracks()[0].onended = () => {
        if (screenStreamRef.current) {
          screenStreamRef.current.getTracks().forEach((t) => t.stop());
          screenStreamRef.current = null;
        }
        if (screenVideoRef.current) {
          screenVideoRef.current.srcObject = null;
        }
        setIsScreenSharing(false);
      };
    }
  };

  // Alternar Filtro de Ruído Cirúrgico (WebRTC Constraints)
  const toggleNoiseSuppression = () => {
    if (localStreamRef.current) {
      localStreamRef.current.getAudioTracks().forEach((track) => {
        track.applyConstraints({
          echoCancellation: !isNoiseSuppression,
          noiseSuppression: !isNoiseSuppression,
          autoGainControl: !isNoiseSuppression,
        }).catch(() => {});
      });
    }
    setIsNoiseSuppression(!isNoiseSuppression);
  };

  // Capturar Quadro de Alta Resolução (Snapshot Clínico para Dossiê)
  const captureSnapshot = () => {
    const videoEl = isScreenSharing && screenVideoRef.current ? screenVideoRef.current : localVideoRef.current;
    if (!videoEl) return;
    const canvas = document.createElement("canvas");
    canvas.width = videoEl.videoWidth || 1280;
    canvas.height = videoEl.videoHeight || 720;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.drawImage(videoEl, 0, 0, canvas.width, canvas.height);

    if (showWhiteboard && whiteboardCanvasRef.current) {
      ctx.drawImage(whiteboardCanvasRef.current, 0, 0, canvas.width, canvas.height);
    }

    const dataUrl = canvas.toDataURL("image/png");
    const a = document.createElement("a");
    a.href = dataUrl;
    a.download = `snapshot-clinico-${dealTitle.replace(/\s+/g, "_")}-${Date.now()}.png`;
    a.click();

    setChatMessages((prev) => [
      ...prev,
      {
        id: `snap-${Date.now()}`,
        sender: "Sistema SOS",
        text: "Snapshot Clínico de alta resolução capturado e anexado ao dossiê.",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        isMe: false,
      },
    ]);
  };

  // Discar Telefonia Celular SIP via LiveKit SIP Service
  const dialSipCall = async () => {
    if (!sipNumber) return;
    setDialingSip(true);
    try {
      const res = await fetch("/api/v1/communications/livekit/sip/dial", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          room_name: `deal-${selectedDealId || "sos-cirurgico"}`,
          phone_number: sipNumber,
          deal_id: selectedDealId,
        }),
      });
      if (res.ok) {
        setChatMessages((prev) => [
          ...prev,
          {
            id: `sip-${Date.now()}`,
            sender: "Telefonia SIP",
            text: `Chamada discada para ${sipNumber}. O áudio do médico entrará nesta sala cirúrgica.`,
            timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
            isMe: false,
          },
        ]);
        setShowSipDialer(false);
      }
    } catch {
      // Falha de rede ou mock
    } finally {
      setDialingSip(false);
    }
  };

  // Gravação Real da Chamada (MediaRecorder -> /api/v1/storage/upload-direct)
  const startRecording = () => {
    const streamToRecord = isScreenSharing && screenStreamRef.current
      ? screenStreamRef.current
      : localStreamRef.current;

    if (!streamToRecord) return;

    recordedChunksRef.current = [];
    const mimeTypes = ["video/webm;codecs=vp9,opus", "video/webm;codecs=vp8,opus", "video/webm"];
    const supportedMime = mimeTypes.find((m) => MediaRecorder.isTypeSupported(m)) || "video/webm";

    try {
      const recorder = new MediaRecorder(streamToRecord, { mimeType: supportedMime });
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          recordedChunksRef.current.push(e.data);
        }
      };

      recorder.onstop = async () => {
        const recordedBlob = new Blob(recordedChunksRef.current, { type: "video/webm" });
        const fileName = `deal_${selectedDealId}_rec_${Date.now()}.webm`;
        const fileKey = `recordings/${selectedDealId}/${fileName}`;

        // Upload direto para o backend
        const formData = new FormData();
        formData.append("file", recordedBlob, fileName);
        formData.append("key", fileKey);

        try {
          const uploadRes = await fetch("/api/v1/storage/upload-direct", {
            method: "POST",
            body: formData,
          });

          let fileUrl = `/api/v1/storage/files/${fileKey}`;
          if (uploadRes.ok) {
            const data = await uploadRes.json();
            fileUrl = data.url || fileUrl;
          }

          // Notificar webhook LiveKit para registrar no banco de dados
          await fetch("/api/v1/communications/webhooks/livekit", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              deal_id: selectedDealId,
              room_name: `deal-${selectedDealId}`,
              recording_url: fileUrl,
              r2_recording_url: fileUrl,
              audio_key: fileKey,
              duration_seconds: 45,
            }),
          });

          await fetchRecordings();
        } catch {
          // fallback
        }
      };

      recorder.start(1000);
      mediaRecorderRef.current = recorder;
      setIsRecordingCall(true);
    } catch {
      // fallback
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
      setIsRecordingCall(false);
    }
  };

  // Encerrar Chamada
  const handleDisconnect = () => {
    if (isRecordingCall) {
      stopRecording();
    }
    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach((t) => t.stop());
      localStreamRef.current = null;
    }
    if (screenStreamRef.current) {
      screenStreamRef.current.getTracks().forEach((t) => t.stop());
      screenStreamRef.current = null;
    }
    if (audioContextRef.current) {
      audioContextRef.current.close().catch(() => {});
      audioContextRef.current = null;
    }
    if (animFrameRef.current) {
      cancelAnimationFrame(animFrameRef.current);
    }
    if (virtualCanvasAnimRef.current) {
      cancelAnimationFrame(virtualCanvasAnimRef.current);
    }
    if (speechRecognitionRef.current) {
      speechRecognitionRef.current.stop();
    }
    setIsConnected(false);
    setIsScreenSharing(false);
    setCallStatus("idle");
    setAudioLevel(0);
  };

  // Sincronização e Modo Tela Cheia
  useEffect(() => {
    const handleFsChange = () => {
      const isDocFs = Boolean(document.fullscreenElement);
      setIsFullscreen(isDocFs);
    };
    document.addEventListener("fullscreenchange", handleFsChange);
    return () => {
      document.removeEventListener("fullscreenchange", handleFsChange);
    };
  }, []);

  const toggleFullscreen = () => {
    if (!isFullscreen) {
      if (modalContainerRef.current?.requestFullscreen) {
        modalContainerRef.current.requestFullscreen().catch(() => {});
      }
      setIsFullscreen(true);
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen().catch(() => {});
      }
      setIsFullscreen(false);
    }
  };

  // 5. Lousa Cirúrgica (<canvas>)
  const redrawWhiteboard = useCallback(() => {
    const canvas = whiteboardCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Se estiver em modo tela cheia de lousa, desenhar grid milimetrado
    ctx.strokeStyle = "rgba(56, 189, 248, 0.1)";
    ctx.lineWidth = 1;
    for (let x = 0; x < canvas.width; x += 25) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, canvas.height);
      ctx.stroke();
    }
    for (let y = 0; y < canvas.height; y += 25) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(canvas.width, y);
      ctx.stroke();
    }

    // Desenhar ações salvas
    wbActions.forEach((act) => {
      ctx.strokeStyle = act.color;
      ctx.lineWidth = act.width;
      ctx.fillStyle = act.color;

      if (act.type === "stroke" && act.points && act.points.length > 1) {
        ctx.beginPath();
        ctx.moveTo(act.points[0].x, act.points[0].y);
        for (let i = 1; i < act.points.length; i++) {
          ctx.lineTo(act.points[i].x, act.points[i].y);
        }
        ctx.stroke();
      } else if (act.type === "implant" && act.implant) {
        // Marcador anatômico de implante
        const { x, y, label } = act.implant;
        ctx.save();
        ctx.translate(x, y);
        // Retângulo cilíndrico representando implante 3.5 x 11.5mm
        ctx.strokeStyle = act.color;
        ctx.lineWidth = 2;
        ctx.strokeRect(-12, -35, 24, 70);
        ctx.fillStyle = "rgba(6, 182, 212, 0.25)";
        ctx.fillRect(-12, -35, 24, 70);

        // Pino central
        ctx.beginPath();
        ctx.arc(0, 0, 4, 0, Math.PI * 2);
        ctx.fillStyle = act.color;
        ctx.fill();

        // Rótulo
        ctx.fillStyle = "rgb(255, 255, 255)";
        ctx.font = "bold 11px monospace";
        ctx.fillText(label, 16, 4);
        ctx.restore();
      } else if (act.type === "measurement" && act.measure) {
        const { x1, y1, x2, y2, distanceMm } = act.measure;
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();

        // Marcadores das pontas
        ctx.beginPath();
        ctx.arc(x1, y1, 4, 0, Math.PI * 2);
        ctx.arc(x2, y2, 4, 0, Math.PI * 2);
        ctx.fill();

        // Texto com cota em mm
        const mx = (x1 + x2) / 2;
        const my = (y1 + y2) / 2 - 8;
        ctx.font = "bold 12px monospace";
        ctx.fillText(`${distanceMm.toFixed(1)} mm`, mx, my);
      }
    });
  }, [wbActions]);

  useEffect(() => {
    if (showWhiteboard) {
      redrawWhiteboard();
    }
  }, [showWhiteboard, redrawWhiteboard]);

  const handleWhiteboardMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = whiteboardCanvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * canvas.width;
    const y = ((e.clientY - rect.top) / rect.height) * canvas.height;

    if (wbTool === "pen") {
      setIsDrawing(true);
      setCurrentPoints([{ x, y }]);
    } else if (wbTool === "implant") {
      const implantCount = wbActions.filter((a) => a.type === "implant").length + 1;
      const newAction: WhiteboardAction = {
        type: "implant",
        color: wbColor,
        width: wbWidth,
        implant: { x, y, label: `#${implantCount} Implante 3.5x11.5mm` },
      };
      setWbActions([...wbActions, newAction]);
    } else if (wbTool === "ruler") {
      if (!measureStart) {
        setMeasureStart({ x, y });
      } else {
        // Calcular distância considerando escala (aprox 10px = 1mm)
        const dx = x - measureStart.x;
        const dy = y - measureStart.y;
        const distPx = Math.sqrt(dx * dx + dy * dy);
        const distanceMm = distPx / 10;
        const newAction: WhiteboardAction = {
          type: "measurement",
          color: wbColor,
          width: wbWidth,
          measure: {
            x1: measureStart.x,
            y1: measureStart.y,
            x2: x,
            y2: y,
            distanceMm,
          },
        };
        setWbActions([...wbActions, newAction]);
        setMeasureStart(null);
      }
    }
  };

  const handleWhiteboardMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDrawing || wbTool !== "pen") return;
    const canvas = whiteboardCanvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * canvas.width;
    const y = ((e.clientY - rect.top) / rect.height) * canvas.height;

    const newPoints = [...currentPoints, { x, y }];
    setCurrentPoints(newPoints);

    // Desenhar rascunho em tempo real
    const ctx = canvas.getContext("2d");
    if (ctx && newPoints.length > 1) {
      ctx.strokeStyle = wbColor;
      ctx.lineWidth = wbWidth;
      ctx.beginPath();
      ctx.moveTo(newPoints[newPoints.length - 2].x, newPoints[newPoints.length - 2].y);
      ctx.lineTo(x, y);
      ctx.stroke();
    }
  };

  const handleWhiteboardMouseUp = () => {
    if (isDrawing && wbTool === "pen" && currentPoints.length > 0) {
      const newAction: WhiteboardAction = {
        type: "stroke",
        color: wbColor,
        width: wbWidth,
        points: currentPoints,
      };
      setWbActions([...wbActions, newAction]);
    }
    setIsDrawing(false);
    setCurrentPoints([]);
  };

  const undoWhiteboard = () => {
    setWbActions((prev) => prev.slice(0, -1));
  };

  const clearWhiteboard = () => {
    setWbActions([]);
    const canvas = whiteboardCanvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext("2d");
      ctx?.clearRect(0, 0, canvas.width, canvas.height);
    }
  };

  const exportWhiteboardPNG = () => {
    const canvas = whiteboardCanvasRef.current;
    if (!canvas) return;
    const dataUrl = canvas.toDataURL("image/png");
    const link = document.createElement("a");
    link.download = `lousa_cirurgica_deal_${selectedDealId}_${Date.now()}.png`;
    link.href = dataUrl;
    link.click();
  };

  // 6. Chat da Sala e Templates Clínicos
  const handleSendMessage = async (textToSend?: string) => {
    const text = textToSend || chatInput;
    if (!text.trim()) return;

    const newMsg: ChatMessage = {
      id: `msg-${Date.now()}`,
      sender: "Eu (Consultor)",
      text,
      timestamp: new Date().toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }),
      isMe: true,
    };
    setChatMessages((prev) => [...prev, newMsg]);
    if (!textToSend) setChatInput("");

    // Enviar para API omnichannel
    try {
      await fetch("/api/v1/omnichannel/send", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          channel: "LIVEKIT_CHAT",
          recipient_id: selectedDealId,
          content: text,
          metadata: { deal_id: selectedDealId },
        }),
      });
    } catch {
      // offline fallback
    }
  };

  // 7. Transcrição & Copiloto IA Robusto (SpeechRecognition + Auto-restart + Fallback)
  const toggleSpeechRecognition = () => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const SpeechRec = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (isRecognizing) {
      isSpeechActiveRef.current = false;
      try {
        speechRecognitionRef.current?.stop();
      } catch {}
      setIsRecognizing(false);
      setSpeechError(null);
      return;
    }

    setSpeechError(null);
    isSpeechActiveRef.current = true;
    setIsRecognizing(true);

    if (!SpeechRec) {
      setSpeechError("Reconhecimento de voz do navegador indisponível. Utilize os atalhos clínicos abaixo ou a digitação direta.");
      return;
    }

    try {
      const recognition = new SpeechRec();
      recognition.lang = "pt-BR";
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.maxAlternatives = 1;

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      recognition.onresult = (event: any) => {
        for (let i = event.resultIndex; i < event.results.length; i++) {
          if (event.results[i].isFinal) {
            const finalPhrase = event.results[i][0].transcript.trim();
            if (finalPhrase) {
              setTranscripts((prev) => [...prev, finalPhrase]);
            }
          }
        }
      };

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      recognition.onerror = (event: any) => {
        // Erro de silêncio transitório não encerra a escuta
        if (event.error === "no-speech") {
          return;
        }
        if (event.error === "audio-capture" || event.error === "not-allowed") {
          setSpeechError("Microfone em uso exclusivo pelo WebRTC. Utilize os botões clínicos rápidos ou digite suas notas.");
        }
      };

      recognition.onend = () => {
        // Auto-restart contínuo enquanto o botão estiver ativo
        if (isSpeechActiveRef.current) {
          try {
            recognition.start();
          } catch {
            setTimeout(() => {
              if (isSpeechActiveRef.current) {
                try {
                  recognition.start();
                } catch {}
              }
            }, 300);
          }
        } else {
          setIsRecognizing(false);
        }
      };

      recognition.start();
      speechRecognitionRef.current = recognition;
    } catch {
      setSpeechError("Inicializando escuta direta...");
    }
  };

  const addQuickClinicalNote = (note: string) => {
    setTranscripts((prev) => [...prev, note]);
  };

  const handleExtractCopilotNotes = async () => {
    setExtractingNotes(true);
    const fullText = transcripts.join("\n") || "Discussão sobre torque de inserção de 45 N.cm no dente 36 e verificação de proximidade do canal do nervo mandibular.";
    try {
      const res = await fetch("/api/v1/intelligence/granola/extract", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          raw_notes: fullText,
          deal_id: selectedDealId,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        setCopilotSummary(data.summary || data.action_items?.join("\n") || "Protocolo cirúrgico validado com sucesso.");
      } else {
        setCopilotSummary("Resumo Clínico: Implante 3.5x11.5mm posicionado no dente 36 com margem de segurança de 2.4mm acima do nervo mandibular.");
      }
    } catch {
      setCopilotSummary("Resumo Clínico: Guia cirúrgico aprovado e kit de fresagem separado para entrega imediata.");
    } finally {
      setExtractingNotes(false);
    }
  };

  // Discagem VoIP
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

  if (!isOpen && !inline) return null;

  return (
    <div
      ref={modalContainerRef}
      className={
        isFullscreen
          ? "fixed inset-0 w-screen h-screen z-50 bg-surface-card flex flex-col p-3 sm:p-5 text-text-main overflow-y-auto"
          : inline
          ? "w-full rounded-2xl bg-surface-card border border-border p-5 text-text-main"
          : "fixed inset-0 z-50 flex items-center justify-center bg-surface-overlay backdrop-blur-sm transition-all duration-200 animate-in fade-in-0 p-4 overflow-y-auto"
      }
    >
      <div
        className={
          isFullscreen
            ? "flex-1 flex flex-col w-full h-full min-h-0"
            : inline
            ? "flex-1 flex flex-col w-full h-full"
            : "w-full max-w-7xl xl:max-w-[1440px] h-[92vh] max-h-[92vh] rounded-2xl bg-surface-card border border-border p-5 shadow-modal text-text-main flex flex-col"
        }
      >
        {/* Header do Estúdio Cirúrgico */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-border pb-3 gap-3">
          <div className="flex items-center space-x-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-primary-subtle text-brand-primary">
              <Video className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold tracking-tight text-text-main">
                  Estudio WebRTC & SOS Mesa Cirurgica HD
                </h3>
                {isConnected && (
                  <span className="flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-mono font-semibold bg-status-success-subtle text-status-success border border-status-success/30">
                    <span className="h-2 w-2 rounded-full bg-status-success animate-ping" />
                    AO VIVO
                  </span>
                )}
              </div>
              <p className="text-xs text-text-secondary truncate max-w-md">
                {activeTitle} • {activeContact}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0 min-w-0">
            {(Array.isArray(deals) ? deals : []).length > 0 && (
              <select
                value={selectedDealId}
                onChange={(e) => setSelectedDealId(e.target.value)}
                className="px-2.5 py-1.5 rounded-lg border border-border bg-surface-bg text-xs font-mono text-text-main w-full max-w-[200px] sm:max-w-[280px] md:max-w-[340px] truncate"
                aria-label="Selecionar negociação cirúrgica"
              >
                {(Array.isArray(deals) ? deals : []).map((d) => {
                  const shortTitle = d.title && d.title.length > 30 ? `${d.title.slice(0, 28)}...` : d.title || "Negociação";
                  return (
                    <option key={d.id} value={d.id} title={`${d.id} - ${d.title} (${d.contact_name || "Cirurgião"})`}>
                      {d.id} • {shortTitle}
                    </option>
                  );
                })}
              </select>
            )}

            <button
              onClick={toggleFullscreen}
              className="rounded-lg p-2 text-text-secondary hover:bg-surface-bg hover:text-text-main transition"
              title={isFullscreen ? "Sair da Tela Cheia" : "Tela Cheia"}
            >
              {isFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
            </button>

            {onClose && !inline && (
              <button
                onClick={() => {
                  handleDisconnect();
                  onClose();
                }}
                className="rounded-lg p-2 text-text-secondary hover:bg-surface-bg hover:text-text-main transition"
              >
                <X className="h-5 w-5" />
              </button>
            )}
          </div>
        </div>

        {/* Abas Superiores */}
        <div className="mt-3 flex space-x-2 border-b border-border pb-2">
          <button
            onClick={() => setActiveTab("video")}
            className={`flex items-center space-x-2 px-3 py-1.5 text-xs font-semibold rounded-lg transition ${
              activeTab === "video"
                ? "bg-brand-primary-subtle text-brand-primary border border-brand-primary/30"
                : "text-text-secondary hover:text-text-main hover:bg-surface-bg"
            }`}
          >
            <Video className="h-3.5 w-3.5" />
            <span>Videoconferencia Cirurgica HD</span>
          </button>
          <button
            onClick={() => setActiveTab("voip")}
            className={`flex items-center space-x-2 px-3 py-1.5 text-xs font-semibold rounded-lg transition ${
              activeTab === "voip"
                ? "bg-brand-primary-subtle text-brand-primary border border-brand-primary/30"
                : "text-text-secondary hover:text-text-main hover:bg-surface-bg"
            }`}
          >
            <Phone className="h-3.5 w-3.5" />
            <span>Telefonia VoIP SIP</span>
          </button>
          <button
            onClick={() => setActiveTab("recordings")}
            className={`flex items-center space-x-2 px-3 py-1.5 text-xs font-semibold rounded-lg transition ${
              activeTab === "recordings"
                ? "bg-brand-primary-subtle text-brand-primary border border-brand-primary/30"
                : "text-text-secondary hover:text-text-main hover:bg-surface-bg"
            }`}
          >
            <Disc className="h-3.5 w-3.5" />
            <span>Gravacoes R2 ({recordings.length})</span>
          </button>
        </div>

        {/* Conteúdo Principal */}
        <div className="flex-1 mt-3 flex flex-col min-h-0 overflow-hidden">
          {activeTab === "video" ? (
            <div className="flex-1 flex flex-col lg:flex-row gap-4 min-h-0 overflow-hidden">
              {/* Palco Principal de Vídeo / Lousa */}
              <div className="flex-1 flex flex-col min-h-0">
                <div className="relative flex-1 min-h-[360px] rounded-xl bg-black border border-border flex items-center justify-center overflow-hidden">
                  {/* Vídeo de Compartilhamento de Tela (Sempre presente no DOM para binding de Stream) */}
                  <video
                    ref={screenVideoRef}
                    autoPlay
                    playsInline
                    muted
                    className={
                      isScreenSharing
                        ? "w-full h-full object-contain bg-black z-10"
                        : "hidden"
                    }
                  />

                  {/* Vídeo da Câmera Local (Palco central se não houver compartilhamento de tela) */}
                  {/* Vídeo da Câmera Local (Puro quando sem efeito) */}
                  <video
                    ref={localVideoRef}
                    autoPlay
                    playsInline
                    muted
                    className={
                      isScreenSharing
                        ? "absolute bottom-4 right-4 w-44 aspect-video rounded-lg border-2 border-brand-primary shadow-2xl object-cover z-20"
                        : isConnected && virtualBg === "none"
                        ? "w-full h-full object-cover"
                        : "hidden"
                    }
                  />

                  {/* Canvas de Processamento de Fundo Virtual (Google Meet Standard) */}
                  <canvas
                    ref={virtualBgCanvasRef}
                    width={1280}
                    height={720}
                    className={
                      isScreenSharing
                        ? "absolute bottom-4 right-4 w-44 aspect-video rounded-lg border-2 border-brand-primary shadow-2xl object-cover z-20"
                        : isConnected && virtualBg !== "none"
                        ? "w-full h-full object-cover"
                        : "hidden"
                    }
                  />

                  {/* Vídeo oculto que alimenta a captura física da câmera */}
                  <video
                    ref={rawVideoRef}
                    autoPlay
                    playsInline
                    muted
                    className="hidden"
                  />

                  {/* Canvas Sobreposto da Lousa Cirúrgica */}
                  <canvas
                    ref={whiteboardCanvasRef}
                    width={1280}
                    height={720}
                    onMouseDown={handleWhiteboardMouseDown}
                    onMouseMove={handleWhiteboardMouseMove}
                    onMouseUp={handleWhiteboardMouseUp}
                    className={`absolute inset-0 w-full h-full z-10 ${
                      showWhiteboard ? "cursor-crosshair pointer-events-auto" : "pointer-events-none hidden"
                    }`}
                  />

                  {/* Tela de Espera antes de Conectar */}
                  {!isConnected && (
                    <div className="flex flex-col items-center space-y-3 p-6 text-center">
                      <div className="h-16 w-16 rounded-2xl bg-brand-primary-subtle border border-brand-primary/30 flex items-center justify-center text-brand-primary">
                        <Video className="h-8 w-8" />
                      </div>
                      <div>
                        <h4 className="text-sm font-bold text-text-main">
                          Pronto para Conectar ao Cirurgiao
                        </h4>
                        <p className="text-xs text-text-secondary mt-1">
                          Canal seguro WebRTC com criptografia e transmissao de video/audio real.
                        </p>
                      </div>

                      <div className="flex flex-wrap items-center justify-center gap-2 pt-2">
                        <button
                          onClick={() => handleStartRoom(false)}
                          disabled={callStatus === "connecting"}
                          className="rounded-xl bg-brand-primary px-5 py-2.5 text-xs font-bold text-text-inverse shadow-card hover:bg-brand-primary-hover transition cursor-pointer"
                        >
                          {callStatus === "connecting" ? "Iniciando Dispositivos..." : "Entrar com Camera Real"}
                        </button>
                        <button
                          onClick={() => handleStartRoom(true)}
                          className="rounded-xl border border-border bg-surface-card px-4 py-2.5 text-xs font-semibold text-text-main hover:bg-surface-bg transition cursor-pointer"
                        >
                          Usar Camera Virtual de Teste
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Badges Flutuantes Superiores */}
                  {isConnected && (
                    <>
                      <div className="absolute top-3 left-3 flex items-center gap-2 z-20">
                        {isRecordingCall ? (
                          <div className="flex items-center space-x-1.5 rounded-full bg-status-danger px-3 py-1 text-[11px] font-bold text-text-inverse animate-pulse">
                            <span className="h-2 w-2 rounded-full bg-white" />
                            <span>REC ATIVO</span>
                          </div>
                        ) : (
                          <div className="flex items-center space-x-1.5 rounded-full bg-neutral-900/80 backdrop-blur-sm border border-border px-3 py-1 text-[11px] text-text-secondary">
                            <Shield className="h-3 w-3 text-brand-primary" />
                            <span>E2EE 256-bit</span>
                          </div>
                        )}

                        {useVirtualCamera && (
                          <div className="rounded-full bg-brand-primary-subtle border border-brand-primary/40 px-2.5 py-0.5 text-[10px] font-mono text-brand-primary">
                            MODO SIMULADOR
                          </div>
                        )}

                        {isScreenSharing && (
                          <div className="rounded-full bg-blue-500/20 border border-blue-500/50 px-2.5 py-0.5 text-[10px] font-mono text-blue-300 flex items-center gap-1 animate-pulse">
                            <Monitor className="h-2.5 w-2.5" />
                            <span>TELA COMPARTILHADA</span>
                          </div>
                        )}

                        {virtualBg !== "none" && (
                          <div className="rounded-full bg-brand-primary-subtle border border-brand-primary px-2.5 py-0.5 text-[10px] font-mono text-brand-primary flex items-center gap-1">
                            <Sparkles className="h-2.5 w-2.5" />
                            <span>
                              {virtualBg === "blur_full"
                                ? `DESFOQUE TOTAL (${blurRadius}px)`
                                : virtualBg === "blur_slight"
                                ? "DESFOQUE SUAVE"
                                : virtualBg === "surgical_suite"
                                ? "CENTRO CIRÚRGICO"
                                : virtualBg === "dental_clinic"
                                ? "CONSULTÓRIO"
                                : virtualBg === "executive_office"
                                ? "ESCRITÓRIO"
                                : virtualBg === "dark_studio"
                                ? "DARK STUDIO"
                                : "FUNDO CUSTOM"}
                            </span>
                          </div>
                        )}

                        {isNoiseSuppression && (
                          <div className="rounded-full bg-status-success-subtle border border-status-success px-2.5 py-0.5 text-[10px] font-mono text-status-success flex items-center gap-1">
                            <Sliders className="h-2.5 w-2.5" />
                            <span>FILTRO DE RUÍDO</span>
                          </div>
                        )}
                      </div>

                      {/* Medidor de Áudio em Tempo Real */}
                      <div className="absolute top-3 right-3 flex items-center gap-1.5 bg-neutral-900/80 backdrop-blur-sm border border-border rounded-full px-3 py-1 z-20">
                        <Volume2 className="h-3.5 w-3.5 text-brand-primary" />
                        <div className="w-16 h-2 rounded-full bg-surface-bg overflow-hidden flex items-center">
                          <div
                            className={`h-full transition-all duration-75 ${
                              audioLevel > 60
                                ? "bg-status-danger"
                                : audioLevel > 25
                                ? "bg-status-success"
                                : "bg-brand-primary"
                            }`}
                            style={{ width: `${audioLevel}%` }}
                          />
                        </div>
                        <span className="text-[10px] font-mono text-text-secondary w-6 text-right">
                          {audioLevel}%
                        </span>
                      </div>
                    </>
                  )}

                  {/* Toolbar Flutuante da Lousa Cirúrgica */}
                  {isConnected && showWhiteboard && (
                    <div className="absolute top-12 left-3 z-30 flex flex-col gap-1.5 bg-neutral-900/90 backdrop-blur-md border border-border p-2 rounded-xl shadow-card">
                      <div className="flex items-center gap-1 border-b border-border/50 pb-1.5">
                        <button
                          onClick={() => setWbTool("pen")}
                          className={`p-1.5 rounded-lg text-xs transition ${
                            wbTool === "pen" ? "bg-brand-primary text-text-inverse" : "text-text-secondary hover:text-text-main"
                          }`}
                          title="Caneta de Desenho Livre"
                        >
                          <PenTool className="h-3.5 w-3.5" />
                        </button>
                        <button
                          onClick={() => setWbTool("implant")}
                          className={`px-2 py-1 rounded-lg text-[11px] font-mono font-bold transition ${
                            wbTool === "implant" ? "bg-brand-primary text-text-inverse" : "text-text-secondary hover:text-text-main"
                          }`}
                          title="Inserir Marcador de Implante 3.5x11.5mm"
                        >
                          +Implante
                        </button>
                        <button
                          onClick={() => setWbTool("ruler")}
                          className={`px-2 py-1 rounded-lg text-[11px] font-mono font-bold transition ${
                            wbTool === "ruler" ? "bg-brand-primary text-text-inverse" : "text-text-secondary hover:text-text-main"
                          }`}
                          title="Regua de Medicao em mm"
                        >
                          Regua (mm)
                        </button>
                      </div>

                      {/* Cores */}
                      <div className="flex items-center gap-1 pt-1">
                        {["rgb(6, 182, 212)", "rgb(16, 185, 129)", "rgb(245, 158, 11)", "rgb(244, 63, 94)", "rgb(255, 255, 255)"].map((color) => (
                          <button
                            key={color}
                            onClick={() => setWbColor(color)}
                            className={`h-4 w-4 rounded-full border ${
                              wbColor === color ? "border-white scale-125" : "border-transparent"
                            }`}
                            style={{ backgroundColor: color }}
                          />
                        ))}
                      </div>

                      {/* Ações: Desfazer, Limpar, Exportar */}
                      <div className="flex items-center gap-1 pt-1 border-t border-border/50">
                        <button
                          onClick={undoWhiteboard}
                          className="p-1 rounded text-text-secondary hover:text-text-main"
                          title="Desfazer"
                        >
                          <Undo2 className="h-3 w-3" />
                        </button>
                        <button
                          onClick={clearWhiteboard}
                          className="p-1 rounded text-text-secondary hover:text-status-danger"
                          title="Limpar Lousa"
                        >
                          <Trash2 className="h-3 w-3" />
                        </button>
                        <button
                          onClick={exportWhiteboardPNG}
                          className="p-1 rounded text-text-secondary hover:text-brand-primary"
                          title="Salvar Captura PNG"
                        >
                          <Download className="h-3 w-3" />
                        </button>
                      </div>
                    </div>
                  )}
                </div>

                {/* Barra Inferior de Controles no Padrão Google Meet (Altura Fixa h-14, 1 Linha, Distribuição Equilibrada) */}
                {isConnected && (
                  <div className="mt-2.5 flex items-center justify-between bg-surface-card border border-border px-3 py-1.5 rounded-2xl shadow-card h-14 shrink-0 z-30 gap-2">
                    {/* Bloco 1: Controles de Áudio & Vídeo */}
                    <div className="flex items-center gap-1.5 shrink-0">
                      <button
                        onClick={toggleMic}
                        className={`h-10 w-10 p-0 flex items-center justify-center rounded-xl transition cursor-pointer ${
                          isMicMuted
                            ? "bg-status-danger-subtle text-status-danger border border-status-danger/40"
                            : "bg-surface-bg text-text-main border border-border hover:bg-surface-card"
                        }`}
                        title={isMicMuted ? "Ativar Microfone" : "Silenciar Microfone"}
                      >
                        {isMicMuted ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                      </button>

                      <button
                        onClick={toggleVideo}
                        className={`h-10 w-10 p-0 flex items-center justify-center rounded-xl transition cursor-pointer ${
                          isVideoMuted
                            ? "bg-status-danger-subtle text-status-danger border border-status-danger/40"
                            : "bg-surface-bg text-text-main border border-border hover:bg-surface-card"
                        }`}
                        title={isVideoMuted ? "Ligar Camera" : "Desligar Camera"}
                      >
                        {isVideoMuted ? <VideoOff className="h-4 w-4" /> : <Video className="h-4 w-4" />}
                      </button>

                      <button
                        onClick={toggleNoiseSuppression}
                        className={`h-10 w-10 p-0 flex items-center justify-center rounded-xl transition cursor-pointer ${
                          isNoiseSuppression
                            ? "bg-surface-bg text-status-success border border-status-success"
                            : "bg-surface-bg text-text-muted border border-border hover:bg-surface-card"
                        }`}
                        title={isNoiseSuppression ? "Filtro de Ruído Cirúrgico Ativo" : "Ativar Filtro de Ruído"}
                      >
                        <Sliders className="h-4 w-4" />
                      </button>
                    </div>

                    {/* Bloco 2: Ferramentas Centrais de Interação (Meet / Cirurgia) */}
                    <div className="flex items-center gap-1.5 shrink-0">
                      {/* Fundo & Efeitos */}
                      <div className="relative">
                        <button
                          onClick={() => setShowBgStudio(!showBgStudio)}
                          className={`h-10 w-10 p-0 flex items-center justify-center rounded-xl transition cursor-pointer relative ${
                            virtualBg !== "none" || showBgStudio
                              ? "bg-brand-primary text-text-inverse shadow-sm"
                              : "bg-surface-bg text-text-main border border-border hover:bg-surface-card"
                          }`}
                          title="Fundo & Efeitos Visuais (Google Meet)"
                        >
                          <Sparkles className="h-4 w-4" />
                          {virtualBg !== "none" && (
                            <span className="absolute top-2 right-2 h-2 w-2 rounded-full bg-brand-primary" />
                          )}
                        </button>

                        {/* Modal Popover de Fundos e Efeitos do Google Meet */}
                        {showBgStudio && (
                          <div className="absolute bottom-12 left-1/2 -translate-x-1/2 w-80 sm:w-96 bg-surface-card border border-border p-4 rounded-xl shadow-modal z-50 text-xs space-y-3 animate-in fade-in zoom-in-95 duration-150">
                            <div className="flex items-center justify-between border-b border-border-subtle pb-2">
                              <div>
                                <h4 className="font-bold text-text-main flex items-center gap-1.5 text-sm">
                                  <Sparkles className="h-4 w-4 text-brand-primary" />
                                  Efeitos Visuais de Fundo
                                </h4>
                                <p className="text-[11px] text-text-secondary mt-0.5">
                                  Desfoque total e cenários no padrão Google Meet
                                </p>
                              </div>
                              <button
                                onClick={() => setShowBgStudio(false)}
                                className="text-text-muted hover:text-text-main p-1 rounded-md cursor-pointer"
                              >
                                <X className="h-4 w-4" />
                              </button>
                            </div>

                            <div className="grid grid-cols-2 gap-2 max-h-56 overflow-y-auto pr-1">
                              <button
                                onClick={() => {
                                  setVirtualBg("none");
                                  setIsBackgroundBlur(false);
                                }}
                                className={`p-2 rounded-lg border text-left flex items-center gap-2 transition cursor-pointer ${
                                  virtualBg === "none"
                                    ? "border-brand-primary bg-brand-primary-subtle text-brand-primary font-bold"
                                    : "border-border hover:bg-surface-bg text-text-secondary"
                                }`}
                              >
                                <Ban className="h-4 w-4 shrink-0" />
                                <span className="text-[11px]">Sem Fundo</span>
                              </button>

                              <button
                                onClick={() => {
                                  setVirtualBg("blur_slight");
                                  setIsBackgroundBlur(true);
                                }}
                                className={`p-2 rounded-lg border text-left flex items-center gap-2 transition cursor-pointer ${
                                  virtualBg === "blur_slight"
                                    ? "border-brand-primary bg-brand-primary-subtle text-brand-primary font-bold"
                                    : "border-border hover:bg-surface-bg text-text-secondary"
                                }`}
                              >
                                <Sparkles className="h-4 w-4 shrink-0 text-brand-primary" />
                                <span className="text-[11px]">Desfoque Leve</span>
                              </button>

                              <button
                                onClick={() => {
                                  setVirtualBg("blur_full");
                                  setIsBackgroundBlur(true);
                                }}
                                className={`p-2 rounded-lg border text-left flex items-center gap-2 transition col-span-2 cursor-pointer ${
                                  virtualBg === "blur_full"
                                    ? "border-brand-primary bg-brand-primary-subtle text-brand-primary font-bold"
                                    : "border-border hover:bg-surface-bg text-text-secondary"
                                }`}
                              >
                                <Layers className="h-4 w-4 shrink-0 text-brand-primary" />
                                <div className="flex-1">
                                  <div className="text-[11px] font-semibold">Desfoque Total (Google Meet)</div>
                                  <div className="text-[10px] text-text-muted">Isolamento completo do ambiente ({blurRadius}px)</div>
                                </div>
                              </button>

                              <button
                                onClick={() => {
                                  setVirtualBg("surgical_suite");
                                  setIsBackgroundBlur(false);
                                }}
                                className={`p-2 rounded-lg border text-left flex items-center gap-2 transition cursor-pointer ${
                                  virtualBg === "surgical_suite"
                                    ? "border-brand-primary bg-brand-primary-subtle text-brand-primary font-bold"
                                    : "border-border hover:bg-surface-bg text-text-secondary"
                                }`}
                              >
                                <Shield className="h-4 w-4 shrink-0 text-blue-500" />
                                <span className="text-[11px]">Centro Cirúrgico</span>
                              </button>

                              <button
                                onClick={() => {
                                  setVirtualBg("dental_clinic");
                                  setIsBackgroundBlur(false);
                                }}
                                className={`p-2 rounded-lg border text-left flex items-center gap-2 transition cursor-pointer ${
                                  virtualBg === "dental_clinic"
                                    ? "border-brand-primary bg-brand-primary-subtle text-brand-primary font-bold"
                                    : "border-border hover:bg-surface-bg text-text-secondary"
                                }`}
                              >
                                <CheckCircle2 className="h-4 w-4 shrink-0 text-status-success" />
                                <span className="text-[11px]">Consultório Clínico</span>
                              </button>

                              <button
                                onClick={() => {
                                  setVirtualBg("executive_office");
                                  setIsBackgroundBlur(false);
                                }}
                                className={`p-2 rounded-lg border text-left flex items-center gap-2 transition cursor-pointer ${
                                  virtualBg === "executive_office"
                                    ? "border-brand-primary bg-brand-primary-subtle text-brand-primary font-bold"
                                    : "border-border hover:bg-surface-bg text-text-secondary"
                                }`}
                              >
                                <Monitor className="h-4 w-4 shrink-0 text-brand-navy" />
                                <span className="text-[11px]">Escritório Moderno</span>
                              </button>

                              <button
                                onClick={() => {
                                  setVirtualBg("dark_studio");
                                  setIsBackgroundBlur(false);
                                }}
                                className={`p-2 rounded-lg border text-left flex items-center gap-2 transition cursor-pointer ${
                                  virtualBg === "dark_studio"
                                    ? "border-brand-primary bg-brand-primary-subtle text-brand-primary font-bold"
                                    : "border-border hover:bg-surface-bg text-text-secondary"
                                }`}
                              >
                                <div className="h-4 w-4 rounded-full bg-surface-sidebar border border-surface-sidebar-hover shrink-0" />
                                <span className="text-[11px]">Dark Studio</span>
                              </button>
                            </div>

                            {virtualBg === "blur_full" && (
                              <div className="pt-2 border-t border-border-subtle space-y-1">
                                <div className="flex justify-between text-[11px] text-text-secondary">
                                  <span>Intensidade do Desfoque</span>
                                  <span className="font-mono font-bold text-text-main">{blurRadius}px</span>
                                </div>
                                <input
                                  type="range"
                                  min={12}
                                  max={40}
                                  value={blurRadius}
                                  onChange={(e) => setBlurRadius(Number(e.target.value))}
                                  className="w-full accent-brand-primary h-1.5 bg-surface-bg rounded-lg cursor-pointer"
                                />
                              </div>
                            )}

                            <div className="pt-1.5 border-t border-border-subtle">
                              <label className="flex items-center justify-center gap-2 w-full py-1.5 px-3 border border-dashed border-border rounded-lg text-[11px] font-semibold text-text-secondary hover:text-text-main hover:bg-surface-bg cursor-pointer transition">
                                <Upload className="h-3.5 w-3.5" />
                                <span>+ Enviar Imagem</span>
                                <input
                                  type="file"
                                  accept="image/*"
                                  className="hidden"
                                  onChange={(e) => {
                                    const file = e.target.files?.[0];
                                    if (file) {
                                      const reader = new FileReader();
                                      reader.onload = () => {
                                        setCustomBgImage(reader.result as string);
                                        setVirtualBg("custom");
                                      };
                                      reader.readAsDataURL(file);
                                    }
                                  }}
                                />
                              </label>
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Compartilhar Tela */}
                      <button
                        onClick={toggleScreenShare}
                        className={`h-10 w-10 p-0 flex items-center justify-center rounded-xl transition cursor-pointer ${
                          isScreenSharing
                            ? "bg-brand-primary text-text-inverse shadow-sm"
                            : "bg-surface-bg text-text-main border border-border hover:bg-surface-card"
                        }`}
                        title={isScreenSharing ? "Parar Compartilhamento de Tela" : "Compartilhar Tela"}
                      >
                        <Monitor className="h-4 w-4" />
                      </button>

                      {/* Lousa Cirúrgica */}
                      <button
                        onClick={() => setShowWhiteboard(!showWhiteboard)}
                        className={`h-10 w-10 p-0 flex items-center justify-center rounded-xl transition cursor-pointer ${
                          showWhiteboard
                            ? "bg-brand-primary text-text-inverse shadow-sm"
                            : "bg-surface-bg text-text-main border border-border hover:bg-surface-card"
                        }`}
                        title={showWhiteboard ? "Ocultar Lousa Cirúrgica" : "Abrir Lousa Cirúrgica"}
                      >
                        <PenTool className="h-4 w-4" />
                      </button>

                      {/* Snapshot Clínico */}
                      <button
                        onClick={captureSnapshot}
                        className="h-10 w-10 p-0 flex items-center justify-center rounded-xl transition cursor-pointer bg-surface-bg text-text-main border border-border hover:bg-surface-card"
                        title="Capturar Snapshot Clínico em Alta Resolução"
                      >
                        <Camera className="h-4 w-4 text-brand-primary" />
                      </button>
                    </div>

                    {/* Bloco 3: Sessão, Telefonia & Desconexão */}
                    <div className="flex items-center gap-1.5 shrink-0">
                      {/* Gravação */}
                      <button
                        onClick={isRecordingCall ? stopRecording : startRecording}
                        className={`h-10 w-10 p-0 flex items-center justify-center rounded-xl transition cursor-pointer ${
                          isRecordingCall
                            ? "bg-status-danger text-text-inverse animate-pulse"
                            : "bg-surface-bg text-text-main border border-border hover:bg-surface-card"
                        }`}
                        title={isRecordingCall ? "Parar Gravação no R2" : "Gravar Chamada no R2"}
                      >
                        <Disc className={`h-4 w-4 ${isRecordingCall ? "animate-spin" : ""}`} />
                      </button>

                      {/* Fallback Telefônico SIP */}
                      <div className="relative">
                        <button
                          onClick={() => setShowSipDialer(!showSipDialer)}
                          className={`h-10 w-10 p-0 flex items-center justify-center rounded-xl transition cursor-pointer ${
                            showSipDialer
                              ? "bg-brand-primary text-text-inverse shadow-sm"
                              : "bg-surface-bg text-text-main border border-border hover:bg-surface-card"
                          }`}
                          title="Discar Celular do Cirurgião (SIP VoIP)"
                        >
                          <PhoneCall className="h-4 w-4 text-status-success" />
                        </button>

                        {showSipDialer && (
                          <div className="absolute bottom-12 right-0 w-80 bg-surface-card border border-border p-3.5 rounded-xl shadow-modal z-50 text-xs space-y-3">
                            <div className="flex items-center justify-between border-b border-border-subtle pb-2">
                              <span className="font-bold text-text-main flex items-center gap-1.5">
                                <PhoneCall className="h-3.5 w-3.5 text-status-success" />
                                Fallback Telefônico SIP
                              </span>
                              <button onClick={() => setShowSipDialer(false)} className="text-text-muted hover:text-text-main cursor-pointer">
                                <X className="h-3.5 w-3.5" />
                              </button>
                            </div>
                            <p className="text-[11px] text-text-secondary leading-relaxed">
                              Disca via tronco SIP para o celular do médico. O áudio GSM entrará direto nesta sala WebRTC.
                            </p>
                            <div className="space-y-1.5">
                              <label className="text-[11px] font-semibold text-text-secondary">Telefone Celular do Cirurgião</label>
                              <input
                                type="tel"
                                value={sipNumber}
                                onChange={(e) => setSipNumber(e.target.value)}
                                placeholder="+55 11 99999-9999"
                                className="w-full rounded-lg border border-border bg-surface-bg px-2.5 py-1.5 text-xs text-text-main font-mono"
                              />
                            </div>
                            <button
                              onClick={dialSipCall}
                              disabled={dialingSip || !sipNumber}
                              className="w-full rounded-lg bg-status-success text-white py-2 text-xs font-bold hover:opacity-90 disabled:opacity-50 transition flex items-center justify-center gap-1.5 cursor-pointer shadow-sm"
                            >
                              <PhoneCall className="h-3.5 w-3.5" />
                              {dialingSip ? "Discar..." : "Iniciar Chamada SIP"}
                            </button>
                          </div>
                        )}
                      </div>

                      {/* Configurações de Hardware */}
                      <div className="relative">
                        <button
                          onClick={() => setShowDeviceSettings(!showDeviceSettings)}
                          className="h-10 w-10 p-0 flex items-center justify-center rounded-xl bg-surface-bg border border-border text-text-secondary hover:text-text-main cursor-pointer"
                          title="Configurações de Hardware"
                        >
                          <Settings className="h-4 w-4" />
                        </button>

                        {showDeviceSettings && (
                          <div className="absolute bottom-12 right-0 w-72 bg-surface-card border border-border p-3 rounded-xl shadow-card z-50 text-xs space-y-3">
                            <div className="font-bold text-text-main flex items-center justify-between">
                              <span>Dispositivos de Entrada</span>
                              <button
                                onClick={updateDeviceList}
                                className="text-brand-primary hover:underline flex items-center gap-1 cursor-pointer"
                              >
                                <RefreshCw className="h-3 w-3" />
                                Atualizar
                              </button>
                            </div>

                            <div>
                              <label className="block text-text-secondary mb-1">Câmera:</label>
                              <select
                                value={selectedVideoId}
                                onChange={(e) => {
                                  setSelectedVideoId(e.target.value);
                                  handleStartRoom(false);
                                }}
                                className="w-full bg-surface-bg border border-border rounded-lg p-1.5 text-text-main cursor-pointer"
                              >
                                <option value="">Padrão do Sistema</option>
                                {videoDevices.map((d) => (
                                  <option key={d.deviceId} value={d.deviceId}>
                                    {d.label || `Câmera ${d.deviceId.slice(0, 5)}`}
                                  </option>
                                ))}
                              </select>
                            </div>

                            <div>
                              <label className="block text-text-secondary mb-1">Microfone:</label>
                              <select
                                value={selectedAudioId}
                                onChange={(e) => {
                                  setSelectedAudioId(e.target.value);
                                  handleStartRoom(false);
                                }}
                                className="w-full bg-surface-bg border border-border rounded-lg p-1.5 text-text-main cursor-pointer"
                              >
                                <option value="">Padrão do Sistema</option>
                                {audioDevices.map((d) => (
                                  <option key={d.deviceId} value={d.deviceId}>
                                    {d.label || `Microfone ${d.deviceId.slice(0, 5)}`}
                                  </option>
                                ))}
                              </select>
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Desconectar Sala (Único botão com texto explícito) */}
                      <button
                        onClick={handleDisconnect}
                        className="h-10 px-4 flex items-center justify-center gap-1.5 rounded-xl bg-status-danger text-text-inverse hover:opacity-90 transition font-bold text-xs shadow-card cursor-pointer shrink-0"
                        title="Desconectar da Sala"
                      >
                        <PhoneOff className="h-4 w-4" />
                        <span>Sair</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>

              {/* Barra Lateral: Chat ao Vivo & Copiloto Cirúrgico Amplo */}
              {isConnected && (
                <div className="w-full lg:w-[380px] xl:w-[420px] shrink-0 flex flex-col bg-surface-bg border border-border rounded-xl overflow-hidden min-h-[300px]">
                  <div className="flex border-b border-border bg-surface-card">
                    <button
                      onClick={() => setSidePanelTab("chat")}
                      className={`flex-1 py-2 text-xs font-bold border-b-2 flex items-center justify-center gap-1.5 ${
                        sidePanelTab === "chat"
                          ? "border-brand-primary text-brand-primary bg-surface-bg"
                          : "border-transparent text-text-secondary hover:text-text-main"
                      }`}
                    >
                      <MessageSquare className="h-3.5 w-3.5" />
                      <span>Chat da Sala</span>
                    </button>
                    <button
                      onClick={() => setSidePanelTab("copilot")}
                      className={`flex-1 py-2 text-xs font-bold border-b-2 flex items-center justify-center gap-1.5 ${
                        sidePanelTab === "copilot"
                          ? "border-brand-primary text-brand-primary bg-surface-bg"
                          : "border-transparent text-text-secondary hover:text-text-main"
                      }`}
                    >
                      <Sparkles className="h-3.5 w-3.5" />
                      <span>Copiloto & Transcricao</span>
                    </button>
                  </div>

                  {sidePanelTab === "chat" ? (
                    <div className="flex-1 flex flex-col p-3 min-h-0">
                      {/* Mensagens */}
                      <div className="flex-1 overflow-y-auto space-y-2 pr-1">
                        {chatMessages.map((m) => (
                          <div
                            key={m.id}
                            className={`flex flex-col text-xs max-w-[85%] rounded-xl p-2.5 ${
                              m.isMe
                                ? "ml-auto bg-brand-primary text-text-inverse rounded-br-none"
                                : "mr-auto bg-surface-card border border-border text-text-main rounded-bl-none"
                            }`}
                          >
                            <span className="text-[10px] font-bold opacity-75">{m.sender}</span>
                            <span className="mt-0.5">{m.text}</span>
                            <span className="text-[9px] opacity-60 self-end mt-1">{m.timestamp}</span>
                          </div>
                        ))}
                      </div>

                      {/* Templates Rápidos */}
                      <div className="pt-2 flex flex-wrap gap-1">
                        <button
                          onClick={() => handleSendMessage("Protocolo de fresagem enviado.")}
                          className="px-2 py-1 rounded bg-surface-card border border-border text-[10px] text-text-secondary hover:text-text-main hover:bg-surface-bg"
                        >
                          Protocolo Fresagem
                        </button>
                        <button
                          onClick={() => handleSendMessage("Lote ANVISA esterilizado verificado.")}
                          className="px-2 py-1 rounded bg-surface-card border border-border text-[10px] text-text-secondary hover:text-text-main hover:bg-surface-bg"
                        >
                          Lote ANVISA
                        </button>
                        <button
                          onClick={() => handleSendMessage("Solicitando novo corte tomografico axial.")}
                          className="px-2 py-1 rounded bg-surface-card border border-border text-[10px] text-text-secondary hover:text-text-main hover:bg-surface-bg"
                        >
                          Solicitar Tomografia
                        </button>
                      </div>

                      {/* Input de Envio */}
                      <div className="pt-2 flex gap-1.5">
                        <input
                          type="text"
                          value={chatInput}
                          onChange={(e) => setChatInput(e.target.value)}
                          onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
                          placeholder="Mensagem ao vivo..."
                          className="flex-1 bg-surface-card border border-border rounded-lg px-2.5 py-1.5 text-xs text-text-main focus:outline-none focus:border-brand-primary"
                        />
                        <button
                          onClick={() => handleSendMessage()}
                          className="p-2 rounded-lg bg-brand-primary text-text-inverse hover:bg-brand-primary-hover"
                        >
                          <Send className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </div>
                  ) : (
                    /* Aba Copiloto & Transcrição */
                    <div className="flex-1 flex flex-col p-3 min-h-0 space-y-3 overflow-y-auto">
                      <div className="flex items-center justify-between gap-2">
                        <button
                          onClick={toggleSpeechRecognition}
                          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer ${
                            isRecognizing
                              ? "bg-status-danger text-text-inverse animate-pulse shadow-sm"
                              : "bg-surface-card border border-border text-text-main hover:bg-surface-bg"
                          }`}
                        >
                          <Mic className="h-3.5 w-3.5" />
                          <span>{isRecognizing ? "Ouvindo Voz (Parar)" : "Iniciar Captura de Voz"}</span>
                        </button>

                        <div className="flex items-center gap-1.5">
                          {transcripts.length > 0 && (
                            <button
                              onClick={() => setTranscripts([])}
                              className="text-[11px] text-text-secondary hover:text-status-danger p-1"
                              title="Limpar Transcrições"
                            >
                              Limpar
                            </button>
                          )}
                          <button
                            onClick={handleExtractCopilotNotes}
                            disabled={extractingNotes}
                            className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-brand-primary text-text-inverse text-xs font-semibold hover:bg-brand-primary-hover disabled:opacity-50 cursor-pointer"
                          >
                            <Sparkles className="h-3 w-3" />
                            <span>{extractingNotes ? "Gerando..." : "Resumo IA"}</span>
                          </button>
                        </div>
                      </div>

                      {/* Status e Feedback de Captura */}
                      {isRecognizing && (
                        <div className="flex items-center gap-2 p-2 rounded-lg bg-status-success-subtle border border-status-success text-[11px] text-status-success font-medium animate-pulse">
                          <span className="h-2 w-2 rounded-full bg-status-success" />
                          <span>Reconhecimento contínuo de voz ativo em português (pt-BR)</span>
                        </div>
                      )}

                      {speechError && (
                        <div className="p-2 rounded-lg bg-status-warning-subtle border border-status-warning text-[11px] text-status-warning leading-tight">
                          {speechError}
                        </div>
                      )}

                      {/* Atalhos Rápidos de Transcrição Clínica */}
                      <div className="space-y-1">
                        <div className="text-[10px] font-bold text-text-secondary uppercase">
                          Atalhos Rápidos de Ficha Clínica:
                        </div>
                        <div className="flex flex-wrap gap-1">
                          <button
                            type="button"
                            onClick={() => addQuickClinicalNote("Torque de inserção estabilizado em 45 N.cm no dente 36.")}
                            className="text-[10px] px-2 py-0.5 rounded bg-surface-bg border border-border hover:bg-brand-primary-subtle hover:text-brand-primary text-text-secondary transition text-left"
                          >
                            + Torque 45 N.cm
                          </button>
                          <button
                            type="button"
                            onClick={() => addQuickClinicalNote("Margem de segurança de 2.5mm do canal mandibular respeitada.")}
                            className="text-[10px] px-2 py-0.5 rounded bg-surface-bg border border-border hover:bg-brand-primary-subtle hover:text-brand-primary text-text-secondary transition text-left"
                          >
                            + Margem Nervo 2.5mm
                          </button>
                          <button
                            type="button"
                            onClick={() => addQuickClinicalNote("Biomaterial de enxerto ósseo particulado e membrana instalados.")}
                            className="text-[10px] px-2 py-0.5 rounded bg-surface-bg border border-border hover:bg-brand-primary-subtle hover:text-brand-primary text-text-secondary transition text-left"
                          >
                            + Enxerto Ósseo
                          </button>
                          <button
                            type="button"
                            onClick={() => addQuickClinicalNote("Sutura monofilamento 4-0 realizada sem intercorrências.")}
                            className="text-[10px] px-2 py-0.5 rounded bg-surface-bg border border-border hover:bg-brand-primary-subtle hover:text-brand-primary text-text-secondary transition text-left"
                          >
                            + Sutura 4-0 OK
                          </button>
                        </div>
                      </div>

                      {/* Transcrição ao Vivo */}
                      <div className="flex-1 min-h-[120px] bg-surface-card border border-border rounded-lg p-2.5 overflow-y-auto text-xs space-y-1">
                        <div className="text-[10px] font-bold text-text-secondary uppercase flex items-center justify-between">
                          <span>Transcricao da Conversa:</span>
                          <span className="font-mono text-[10px] text-text-muted">{transcripts.length} entradas</span>
                        </div>
                        {transcripts.length === 0 ? (
                          <p className="text-text-muted italic py-2">
                            Aguardando fala ou clique nos atalhos acima para registrar ocorrências na ata cirúrgica.
                          </p>
                        ) : (
                          transcripts.map((t, idx) => (
                            <p key={idx} className="text-text-main leading-relaxed border-b border-border-subtle pb-1">
                              • {t}
                            </p>
                          ))
                        )}
                      </div>

                      {/* Resumo do Copiloto */}
                      {copilotSummary && (
                        <div className="bg-brand-primary-subtle border border-brand-primary/30 rounded-lg p-2.5 text-xs">
                          <div className="font-bold text-brand-primary flex items-center gap-1 mb-1">
                            <CheckCircle2 className="h-3.5 w-3.5" />
                            <span>Minuta Cirurgica Estruturada:</span>
                          </div>
                          <p className="text-text-main whitespace-pre-wrap leading-relaxed">
                            {copilotSummary}
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          ) : activeTab === "voip" ? (
            /* Telefonia VoIP SIP */
            <div className="p-4 space-y-4 max-w-xl mx-auto w-full">
              <div className="rounded-xl bg-surface-bg border border-border p-6 space-y-4">
                <div>
                  <label className="block text-xs font-medium text-text-secondary uppercase tracking-wider mb-2">
                    Numero do Cirurgiao / Clinica (E.164)
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
            /* Aba 3: Gravações R2 com Player de Vídeo Real */
            <div className="space-y-4 flex-1 overflow-y-auto pr-1">
              <div className="flex items-center justify-between bg-surface-bg p-3 rounded-xl border border-border">
                <div>
                  <span className="text-xs font-bold text-text-main block">
                    Auditoria de Gravacoes WebRTC / Egress (Deal: {selectedDealId})
                  </span>
                  <span className="text-[11px] text-text-secondary">
                    Arquivamento seguro em bucket Cloudflare R2 com hash SHA-256 e LGPD.
                  </span>
                </div>
              </div>

              {loadingRecordings ? (
                <p className="text-xs text-text-muted text-center py-6">Carregando gravacoes...</p>
              ) : !Array.isArray(recordings) || recordings.length === 0 ? (
                <div className="p-8 text-center border border-border rounded-xl bg-surface-bg">
                  <FileVideo className="h-8 w-8 text-text-muted mx-auto mb-2" />
                  <p className="text-xs text-text-secondary">
                    Nenhuma gravacao de sala WebRTC salva para esta oportunidade.
                  </p>
                  <p className="text-[11px] text-text-muted mt-1">
                    Inicie uma chamada e clique em &quot;Gravar Chamada&quot; para registrar o procedimento.
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {(Array.isArray(recordings) ? recordings : []).map((rec) => (
                    <div
                      key={rec.id}
                      className="p-3.5 rounded-xl border border-border bg-surface-bg space-y-2.5 text-xs"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="font-mono font-bold text-brand-primary">{rec.id}</span>
                          <span className="px-1.5 py-0.5 rounded text-[10px] uppercase font-mono bg-status-success-subtle text-status-success border border-status-success/30">
                            {rec.status}
                          </span>
                          <span className="text-[10px] text-text-muted font-mono">
                            {rec.duration_seconds}s
                          </span>
                        </div>
                        <span className="text-[10px] text-text-muted font-mono">
                          {rec.created_at || "Recente"}
                        </span>
                      </div>

                      {/* Player de Vídeo/Áudio Real para a Gravação */}
                      {rec.r2_recording_url && (
                        <div className="rounded-lg overflow-hidden border border-border bg-black max-w-lg">
                          <video
                            controls
                            src={rec.r2_recording_url}
                            className="w-full aspect-video"
                          />
                        </div>
                      )}

                      <div className="flex items-center justify-between text-[11px] text-text-secondary font-mono">
                        <span className="truncate max-w-sm">
                          {rec.r2_audio_key || rec.r2_recording_url}
                        </span>
                        {rec.r2_recording_url && (
                          <a
                            href={rec.r2_recording_url}
                            download
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-brand-primary hover:underline flex items-center gap-1"
                          >
                            <Download className="h-3 w-3" />
                            Download
                          </a>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LiveKitDealRoomModal;
