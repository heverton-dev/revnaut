import * as React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { OmnichannelContextSidebar } from "./OmnichannelContextSidebar";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import {
  MessageSquare,
  Send,
  Smartphone,
  Plus,
  RefreshCw,
  Video,
  Search,
  Mic,
  Square,
  Paperclip,
  QrCode,
  PhoneCall,
  X,
} from "lucide-react";
import { QrCodeSvg } from "@/components/shared/QrCodeSvg";

export interface OmnichannelWorkspaceProps {
  onOpenSosVideo?: (croUf: string) => void;
}

interface ConversationItem {
  id: string;
  account_id: string;
  contact_name: string;
  company?: string;
  channel: string;
  unread: number;
  updated_at?: string;
}

interface MessageItem {
  id: number;
  conversation_id: string;
  sender: "user" | "contact" | "system";
  text: string;
  created_at: string;
}

interface ContactItem {
  id: number;
  name: string;
  phone?: string;
  cro_uf?: string;
  company?: string;
  score?: number;
}

interface WhatsappInstance {
  id: string;
  account_id: string;
  instance_name: string;
  consultant_user_id: string;
  shard_node_url: string;
  phone_number?: string;
  status: string;
  qr_code_base64?: string;
  created_at: string;
}

export const OmnichannelWorkspace: React.FC<OmnichannelWorkspaceProps> = ({
  onOpenSosVideo,
}) => {
  const queryClient = useQueryClient();
  const [selectedChatId, setSelectedChatId] = React.useState<string>("chat-1");
  const [selectedContactId, setSelectedContactId] = React.useState<number | null>(null);
  const [messageText, setMessageText] = React.useState<string>("");
  const [activeTabCol1, setActiveTabCol1] = React.useState<"chats" | "contacts" | "instances">("chats");
  const [newInstanceName, setNewInstanceName] = React.useState<string>("");
  const [newInstancePhone, setNewInstancePhone] = React.useState<string>("");
  const [consultantId, setConsultantId] = React.useState<string>("usr-sp-01");
  const [showInstanceModal, setShowInstanceModal] = React.useState<boolean>(false);
  const [searchFilter, setSearchFilter] = React.useState<string>("");
  const [recording, setRecording] = React.useState<boolean>(false);
  const [uploadingMedia, setUploadingMedia] = React.useState<boolean>(false);
  const [composerError, setComposerError] = React.useState<string | null>(null);
  const [qrInstance, setQrInstance] = React.useState<WhatsappInstance | null>(null);
  const [callFeedback, setCallFeedback] = React.useState<string | null>(null);
  const recorderRef = React.useRef<MediaRecorder | null>(null);
  const chunksRef = React.useRef<Blob[]>([]);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const quickReplies = [
    "Bom dia, doutor(a). Segue o planejamento do caso para sua avaliação.",
    "Confirmo o envio do kit cirúrgico hoje, com rastreabilidade ANVISA.",
    "Poderia enviar a radiografia panorâmica para eu validar o torque e o diâmetro?",
    "Seu lote está em trânsito pelo DENTGO Express. Envio o PIN de entrega em seguida.",
    "Posso agendar uma teleconsulta de 15 minutos para alinhar o protocolo?",
  ];

  // 1. Carregar Conversas
  const { data: rawConversations = [], isLoading: loadingConversations, refetch: refetchConversations } = useQuery<ConversationItem[]>({
    queryKey: ["chat-conversations"],
    queryFn: async () => {
      const res = await fetch("/api/v1/chat/conversations");
      if (!res.ok) throw new Error("Erro ao carregar conversas");
      const d = await res.json();
      return Array.isArray(d) ? d : (Array.isArray(d?.conversations) ? d.conversations : []);
    },
  });
  const conversations = Array.isArray(rawConversations) ? rawConversations : [];

  // 2. Carregar Contatos (Cirurgiões)
  const { data: rawContacts = [] } = useQuery<ContactItem[]>({
    queryKey: ["crm-contacts"],
    queryFn: async () => {
      const res = await fetch("/api/v1/contacts");
      if (!res.ok) throw new Error("Erro ao carregar contatos");
      const d = await res.json();
      return Array.isArray(d) ? d : (Array.isArray(d?.contacts) ? d.contacts : []);
    },
  });
  const contacts = Array.isArray(rawContacts) ? rawContacts : [];

  // 3. Carregar Instâncias Evolution API
  const { data: rawInstances = [], refetch: refetchInstances } = useQuery<WhatsappInstance[]>({
    queryKey: ["whatsapp-instances"],
    queryFn: async () => {
      const res = await fetch("/api/v1/omnichannel/whatsapp/instances");
      if (!res.ok) throw new Error("Erro ao carregar instâncias do Evolution API");
      const d = await res.json();
      return Array.isArray(d) ? d : (Array.isArray(d?.instances) ? d.instances : []);
    },
  });
  const instances = Array.isArray(rawInstances) ? rawInstances : [];

  // 4. Carregar Mensagens do Chat Selecionado
  const { data: rawMessages = [], isLoading: loadingMessages, refetch: refetchMessages } = useQuery<MessageItem[]>({
    queryKey: ["chat-messages", selectedChatId],
    queryFn: async () => {
      if (!selectedChatId) return [];
      const res = await fetch(`/api/v1/chat/${encodeURIComponent(selectedChatId)}/messages`);
      if (!res.ok) throw new Error("Erro ao carregar mensagens");
      const d = await res.json();
      return Array.isArray(d) ? d : (Array.isArray(d?.messages) ? d.messages : []);
    },
    enabled: Boolean(selectedChatId),
    refetchInterval: 5000,
  });
  const messages = Array.isArray(rawMessages) ? rawMessages : [];

  // 5. Mutation Envio de Mensagem
  const sendMessageMutation = useMutation({
    mutationFn: async (text: string) => {
      const res = await fetch(`/api/v1/chat/messages`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          conversation_id: selectedChatId,
          text,
        }),
      });
      if (!res.ok) throw new Error("Falha no envio da mensagem");
      return res.json();
    },
    onSuccess: () => {
      setMessageText("");
      queryClient.invalidateQueries({ queryKey: ["chat-messages", selectedChatId] });
      queryClient.invalidateQueries({ queryKey: ["chat-conversations"] });
    },
  });

  // 6. Mutation Criar Instância Evolution WhatsApp
  const createInstanceMutation = useMutation({
    mutationFn: async () => {
      const res = await fetch("/api/v1/omnichannel/whatsapp/instances", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          instance_name: newInstanceName.trim(),
          consultant_user_id: consultantId,
          phone_number: newInstancePhone.trim() || undefined,
          account_id: "0f14ffff",
        }),
      });
      if (!res.ok) throw new Error("Falha ao provisionar instância WhatsApp");
      return res.json();
    },
    onSuccess: () => {
      setNewInstanceName("");
      setNewInstancePhone("");
      setShowInstanceModal(false);
      refetchInstances();
    },
  });

  // Selecionar primeiro contato disponível como default se nenhum selecionado
  React.useEffect(() => {
    if (!selectedContactId && contacts.length > 0) {
      setSelectedContactId(contacts[0].id);
    }
  }, [contacts, selectedContactId]);

  const activeContact = (Array.isArray(contacts) ? contacts : []).find((c) => c.id === selectedContactId) || contacts[0];
  const activeConversation = (Array.isArray(conversations) ? conversations : []).find((c) => c.id === selectedChatId) || conversations[0];

  const uploadMedia = async (blob: Blob, filename: string): Promise<string> => {
    const presign = await fetch("/api/v1/storage/presign-upload", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Account-ID": "0f14ffff" },
      body: JSON.stringify({
        filename,
        module: "media",
        content_type: blob.type || "application/octet-stream",
      }),
    });
    if (!presign.ok) throw new Error("Falha ao obter autorização de upload");
    const { upload_url, key } = await presign.json();
    const put = await fetch(upload_url, {
      method: "PUT",
      headers: { "Content-Type": blob.type || "application/octet-stream" },
      body: blob,
    });
    if (!put.ok) throw new Error("Falha no upload do arquivo");
    return key as string;
  };

  const sendMediaMessage = async (blob: Blob, filename: string, label: string) => {
    setComposerError(null);
    setUploadingMedia(true);
    try {
      const key = await uploadMedia(blob, filename);
      sendMessageMutation.mutate(`${label}: /api/v1/storage/files/${key}`);
    } catch (err: any) {
      setComposerError(err.message || "Falha ao enviar mídia");
    } finally {
      setUploadingMedia(false);
    }
  };

  const toggleRecording = async () => {
    setComposerError(null);
    if (recording) {
      recorderRef.current?.stop();
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      chunksRef.current = [];
      recorder.ondataavailable = (ev) => {
        if (ev.data.size > 0) chunksRef.current.push(ev.data);
      };
      recorder.onstop = () => {
        stream.getTracks().forEach((t) => t.stop());
        setRecording(false);
        const blob = new Blob(chunksRef.current, { type: recorder.mimeType || "audio/webm" });
        const ext = blob.type.includes("ogg") ? "ogg" : "webm";
        void sendMediaMessage(blob, `nota-de-voz-${Date.now()}.${ext}`, "Nota de voz");
      };
      recorderRef.current = recorder;
      recorder.start();
      setRecording(true);
    } catch {
      setComposerError("Microfone indisponível ou permissão negada.");
    }
  };

  const handleAttachFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    void sendMediaMessage(file, file.name, `Anexo (${file.name})`);
  };

  const handleSimulateCallOffer = async (inst: WhatsappInstance) => {
    setCallFeedback(null);
    try {
      const res = await fetch("/api/v1/webhooks/evolution", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          event: "CALL_OFFER",
          instance: inst.instance_name,
          data: {
            id: `call-${Date.now()}`,
            from: `${(inst.phone_number || "5511999998888").replace(/\D/g, "")}@s.whatsapp.net`,
            isVideo: true,
            status: "offer",
          },
        }),
      });
      const data = await res.json().catch(() => ({}));
      setCallFeedback(
        res.ok
          ? `CALL_OFFER enviado para ${inst.instance_name}.`
          : `Webhook respondeu ${res.status}: ${typeof data.detail === "string" ? data.detail : "verifique a assinatura HMAC"}`,
      );
    } catch (err: any) {
      setCallFeedback(`Erro: ${err.message}`);
    }
  };

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!messageText.trim() || sendMessageMutation.isPending) return;
    sendMessageMutation.mutate(messageText.trim());
  };

  const filteredConversations = conversations.filter((c) =>
    c.contact_name.toLowerCase().includes(searchFilter.toLowerCase()) ||
    (c.company && c.company.toLowerCase().includes(searchFilter.toLowerCase()))
  );

  const filteredContacts = contacts.filter((c) =>
    c.name.toLowerCase().includes(searchFilter.toLowerCase()) ||
    (c.cro_uf && c.cro_uf.toLowerCase().includes(searchFilter.toLowerCase()))
  );

  return (
    <div className="space-y-4">
      {/* Top Header / Breadcrumb */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3 border-b border-border pb-3">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-text-main flex items-center gap-2">
              <MessageSquare className="h-5 w-5 text-brand-primary" />
              Central Omnichannel & Shards Evolution API
            </h1>
            <Badge variant="outline" className="border-brand-primary/30 text-brand-primary bg-brand-primary-subtle text-xs">
              LiveKit & Chatwoot Sync
            </Badge>
          </div>
          <p className="text-xs text-text-secondary mt-0.5">
            Mensageria multicanal unificada com distribuição de carga entre shards Evolution API e contexto cirúrgico 360°.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              refetchConversations();
              refetchMessages();
              refetchInstances();
            }}
            className="flex items-center gap-1.5"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Atualizar
          </Button>
          <Button
            variant="default"
            size="sm"
            onClick={() => setShowInstanceModal(true)}
            className="flex items-center gap-1.5"
          >
            <Plus className="h-3.5 w-3.5" />
            Nova Instância WhatsApp
          </Button>
        </div>
      </div>

      {/* 3-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-start">
        {/* Coluna 1: Lista de Conversas / Cirurgiões / Shards WhatsApp (4 cols) */}
        <div className="lg:col-span-4 space-y-3">
          <Card className="p-3 border border-border bg-surface-card">
            {/* Tabs da Coluna 1 */}
            <div className="flex border-b border-border mb-3 gap-1">
              <button
                onClick={() => setActiveTabCol1("chats")}
                className={`flex-1 py-1.5 text-xs font-semibold border-b-2 text-center transition ${
                  activeTabCol1 === "chats"
                    ? "border-brand-primary text-brand-primary"
                    : "border-transparent text-text-secondary hover:text-text-main"
                }`}
              >
                Conversas ({conversations.length})
              </button>
              <button
                onClick={() => setActiveTabCol1("contacts")}
                className={`flex-1 py-1.5 text-xs font-semibold border-b-2 text-center transition ${
                  activeTabCol1 === "contacts"
                    ? "border-brand-primary text-brand-primary"
                    : "border-transparent text-text-secondary hover:text-text-main"
                }`}
              >
                Cirurgiões ({contacts.length})
              </button>
              <button
                onClick={() => setActiveTabCol1("instances")}
                className={`flex-1 py-1.5 text-xs font-semibold border-b-2 text-center transition ${
                  activeTabCol1 === "instances"
                    ? "border-brand-primary text-brand-primary"
                    : "border-transparent text-text-secondary hover:text-text-main"
                }`}
              >
                Shards ({instances.length})
              </button>
            </div>

            {/* Input de Busca */}
            <div className="relative mb-3">
              <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-text-muted" />
              <Input
                placeholder="Filtrar por nome, CRO ou empresa..."
                value={searchFilter}
                onChange={(e) => setSearchFilter(e.target.value)}
                className="pl-8 text-xs py-1.5"
              />
            </div>

            {/* Conteúdo Aba 1: Conversas Ativas */}
            {activeTabCol1 === "chats" && (
              <div className="space-y-1.5 max-h-[500px] overflow-y-auto">
                {loadingConversations ? (
                  <p className="text-xs text-text-muted py-4 text-center">Carregando conversas...</p>
                ) : filteredConversations.length === 0 ? (
                  <p className="text-xs text-text-muted py-4 text-center">Nenhuma conversa encontrada</p>
                ) : (
                  filteredConversations.map((c) => {
                    const isSelected = c.id === selectedChatId;
                    return (
                      <div
                        key={c.id}
                        onClick={() => setSelectedChatId(c.id)}
                        className={`p-2.5 rounded-lg border cursor-pointer transition ${
                          isSelected
                            ? "bg-brand-primary-subtle/50 border-brand-primary text-text-main"
                            : "bg-surface-bg border-border hover:bg-surface-card text-text-main"
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-xs truncate">{c.contact_name}</span>
                          <span className="text-[10px] text-text-muted">{c.channel.toUpperCase()}</span>
                        </div>
                        {c.company && (
                          <p className="text-[11px] text-text-secondary truncate mt-0.5">{c.company}</p>
                        )}
                        <div className="flex items-center justify-between mt-1 text-[10px] text-text-muted">
                          <span>Chat ID: {c.id}</span>
                          {c.unread > 0 && (
                            <Badge variant="warning" className="text-[9px] px-1 py-0">
                              {c.unread} novas
                            </Badge>
                          )}
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            )}

            {/* Conteúdo Aba 2: Cirurgiões (Contatos CRM) */}
            {activeTabCol1 === "contacts" && (
              <div className="space-y-1.5 max-h-[500px] overflow-y-auto">
                {filteredContacts.map((contact) => {
                  const isSelected = contact.id === selectedContactId;
                  return (
                    <div
                      key={contact.id}
                      onClick={() => setSelectedContactId(contact.id)}
                      className={`p-2.5 rounded-lg border cursor-pointer transition ${
                        isSelected
                          ? "bg-brand-navy-subtle border-brand-navy text-text-main"
                          : "bg-surface-bg border-border hover:bg-surface-card text-text-main"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-xs">{contact.name}</span>
                        {contact.score !== undefined && (
                          <Badge variant="secondary" className="text-[9px] px-1 py-0">
                            Score {contact.score}
                          </Badge>
                        )}
                      </div>
                      <div className="flex items-center gap-2 mt-1 text-[11px] text-text-secondary">
                        <span className="font-mono text-xs text-brand-navy font-bold">
                          {contact.cro_uf || "SEM CRO"}
                        </span>
                        {contact.phone && <span className="font-mono text-[10px]">{contact.phone}</span>}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Conteúdo Aba 3: Shards WhatsApp Evolution API */}
            {activeTabCol1 === "instances" && (
              <div className="space-y-2 max-h-[500px] overflow-y-auto">
                {instances.map((inst) => (
                  <div key={inst.id} className="p-2.5 rounded-lg border border-border bg-surface-bg text-xs space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="font-bold font-mono text-brand-primary">{inst.instance_name}</span>
                      <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-status-success-subtle text-status-success border border-status-success/30">
                        {inst.status}
                      </span>
                    </div>
                    <p className="text-[11px] text-text-secondary truncate">
                      Shard: <code className="text-text-muted">{inst.shard_node_url}</code>
                    </p>
                    <div className="flex items-center justify-between text-[10px] text-text-muted pt-1 border-t border-border/50">
                      <span>Cons.: {inst.consultant_user_id}</span>
                      <span>{inst.phone_number || "Sem linha fixa"}</span>
                    </div>
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      <button
                        type="button"
                        onClick={() => setQrInstance(inst)}
                        className="flex items-center gap-1 px-2 py-1 rounded border border-border bg-surface-card text-[10px] text-text-main hover:border-brand-primary"
                      >
                        <QrCode className="h-3 w-3 text-brand-primary" />
                        Ver QR Code
                      </button>
                      <button
                        type="button"
                        onClick={() => handleSimulateCallOffer(inst)}
                        className="flex items-center gap-1 px-2 py-1 rounded border border-border bg-surface-card text-[10px] text-text-main hover:border-brand-primary"
                      >
                        <PhoneCall className="h-3 w-3 text-brand-primary" />
                        Simular Chamada Vídeo (CALL_OFFER)
                      </button>
                    </div>
                  </div>
                ))}
                {callFeedback && (
                  <p className="text-[10px] font-mono text-text-secondary bg-surface-bg border border-border rounded p-2">
                    {callFeedback}
                  </p>
                )}
              </div>
            )}
          </Card>
        </div>

        {/* Coluna 2: Janela de Chat em Tempo Real (5 cols) */}
        <div className="lg:col-span-5 space-y-3">
          <Card className="border border-border bg-surface-card flex flex-col h-[580px]">
            {/* Header do Chat */}
            <div className="p-3 border-b border-border flex items-center justify-between bg-surface-bg/50">
              <div className="flex items-center gap-2">
                <div className="p-1.5 rounded-full bg-brand-primary-subtle text-brand-primary">
                  <Smartphone className="h-4 w-4" />
                </div>
                <div>
                  <h3 className="text-xs font-bold text-text-main truncate">
                    {activeConversation?.contact_name || activeContact?.name || "Conversa Ativa"}
                  </h3>
                  <span className="text-[10px] text-text-muted">
                    ID: {selectedChatId} • Canal: WhatsApp Evolution API
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-1.5">
                {onOpenSosVideo && (
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={() => onOpenSosVideo(activeContact?.cro_uf || "CRO-SP-54321")}
                    className="flex items-center gap-1 text-xs py-1 h-7"
                  >
                    <Video className="h-3.5 w-3.5" />
                    SOS Vídeo
                  </Button>
                )}
              </div>
            </div>

            {/* Histórico de Mensagens */}
            <div className="flex-1 p-3 overflow-y-auto space-y-2.5 bg-surface-bg/30">
              {loadingMessages ? (
                <div className="flex items-center justify-center h-full text-xs text-text-muted">
                  Carregando mensagens do chat...
                </div>
              ) : messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-xs text-text-muted">
                  <MessageSquare className="h-8 w-8 text-text-muted/40 mb-2" />
                  Nenhuma mensagem registrada nesta conversa.
                </div>
              ) : (
                messages.map((m) => {
                  const isMe = m.sender === "user";
                  return (
                    <div
                      key={m.id}
                      className={`flex flex-col ${isMe ? "items-end" : "items-start"}`}
                    >
                      <div
                        className={`max-w-[85%] rounded-xl px-3 py-2 text-xs shadow-sm ${
                          isMe
                            ? "bg-brand-primary text-white rounded-br-none"
                            : "bg-surface-card border border-border text-text-main rounded-bl-none"
                        }`}
                      >
                        <p className="whitespace-pre-wrap break-words">{m.text}</p>
                        <span
                          className={`block text-[9px] mt-1 text-right ${
                            isMe ? "text-white/70" : "text-text-muted"
                          }`}
                        >
                          {m.created_at || "Agora"}
                        </span>
                      </div>
                    </div>
                  );
                })
              )}
            </div>

            {/* Composer de Mensagem */}
            <form onSubmit={handleSendMessage} className="p-3 border-t border-border bg-surface-card space-y-2">
              <div className="flex flex-wrap gap-1.5">
                {quickReplies.map((q, i) => (
                  <button
                    key={i}
                    type="button"
                    onClick={() => setMessageText(q)}
                    className="px-2 py-1 rounded-full border border-border bg-surface-bg text-[10px] text-text-secondary hover:text-text-main hover:border-brand-primary max-w-full truncate"
                    title={q}
                  >
                    {q.length > 44 ? `${q.slice(0, 44)}...` : q}
                  </button>
                ))}
              </div>
              {composerError && <p className="text-[11px] text-status-danger">{composerError}</p>}
              <div className="flex items-center gap-2">
                <input ref={fileInputRef} type="file" accept="image/*,.pdf,.dcm" className="hidden" onChange={handleAttachFile} />
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={uploadingMedia}
                  aria-label="Anexar arquivo ou radiografia"
                  title="Anexar arquivo ou radiografia"
                >
                  <Paperclip className="h-3.5 w-3.5" />
                </Button>
                <Button
                  type="button"
                  variant={recording ? "default" : "outline"}
                  size="sm"
                  onClick={toggleRecording}
                  disabled={uploadingMedia}
                  aria-label={recording ? "Parar e enviar nota de voz" : "Gravar nota de voz"}
                  title={recording ? "Parar e enviar nota de voz" : "Gravar nota de voz"}
                >
                  {recording ? <Square className="h-3.5 w-3.5 text-status-danger" /> : <Mic className="h-3.5 w-3.5" />}
                </Button>
                <Input
                  value={messageText}
                  onChange={(e) => setMessageText(e.target.value)}
                  placeholder="Escreva sua mensagem para o cirurgião..."
                  className="flex-1 text-xs"
                  disabled={sendMessageMutation.isPending}
                />
                <Button
                  type="submit"
                  variant="default"
                  size="sm"
                  disabled={!messageText.trim() || sendMessageMutation.isPending}
                  className="flex items-center gap-1"
                >
                  <Send className="h-3.5 w-3.5" />
                  Enviar
                </Button>
              </div>
            </form>
          </Card>
        </div>

        {/* Coluna 3: OmnichannelContextSidebar Dinâmica (3 cols) */}
        <div className="lg:col-span-3">
          <OmnichannelContextSidebar
            contactIdentifier={activeContact?.cro_uf || activeContact?.phone || (activeContact ? String(activeContact.id) : "cnt-01")}
            contactId={activeContact ? String(activeContact.id) : undefined}
            currentDealId="deal-01"
            onOpenSosVideo={(cro) => onOpenSosVideo && onOpenSosVideo(cro)}
          />
        </div>
      </div>

      {qrInstance && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-text-main/60 p-4">
          <Card className="w-full max-w-sm p-5 bg-surface-card border border-border space-y-3 shadow-xl">
            <div className="flex items-center justify-between border-b border-border pb-2.5">
              <h3 className="text-sm font-bold text-text-main">QR Code: {qrInstance.instance_name}</h3>
              <button
                type="button"
                aria-label="Fechar QR Code"
                onClick={() => setQrInstance(null)}
                className="text-text-muted hover:text-text-main"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="flex justify-center">
              {qrInstance.qr_code_base64 ? (
                <img
                  src={
                    qrInstance.qr_code_base64.startsWith("data:")
                      ? qrInstance.qr_code_base64
                      : `data:image/png;base64,${qrInstance.qr_code_base64}`
                  }
                  alt={`QR Code da instância ${qrInstance.instance_name}`}
                  className="w-56 h-56"
                />
              ) : (
                <QrCodeSvg value={`evolution://pair/${qrInstance.instance_name}`} size={224} />
              )}
            </div>
            <p className="text-[11px] text-text-secondary text-center">
              WhatsApp &gt; Aparelhos conectados &gt; Conectar um aparelho e aponte a câmera para o código.
            </p>
          </Card>
        </div>
      )}

      {/* Modal / Criação de Instância WhatsApp */}
      {showInstanceModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <Card className="w-full max-w-md p-5 bg-surface-card border border-border space-y-4 shadow-xl">
            <div className="flex items-center justify-between border-b border-border pb-2.5">
              <h3 className="text-sm font-bold text-text-main flex items-center gap-2">
                <Smartphone className="h-4 w-4 text-brand-primary" />
                Nova Instância Evolution API
              </h3>
              <button
                onClick={() => setShowInstanceModal(false)}
                className="text-text-muted hover:text-text-main text-sm"
              >
                ✕
              </button>
            </div>
            <div className="space-y-3">
              <div>
                <label className="text-xs font-semibold text-text-secondary block mb-1">
                  Nome da Instância (Slug Único)
                </label>
                <Input
                  placeholder="ex: consultor-sp-shard-03"
                  value={newInstanceName}
                  onChange={(e) => setNewInstanceName(e.target.value)}
                  className="text-xs"
                />
              </div>
              <div>
                <label className="text-xs font-semibold text-text-secondary block mb-1">
                  ID do Consultor Responsável
                </label>
                <Input
                  placeholder="ex: usr-sp-01"
                  value={consultantId}
                  onChange={(e) => setConsultantId(e.target.value)}
                  className="text-xs"
                />
              </div>
              <div>
                <label className="text-xs font-semibold text-text-secondary block mb-1">
                  Número Telefônico E.164 (Opcional)
                </label>
                <Input
                  placeholder="ex: +5511988889999"
                  value={newInstancePhone}
                  onChange={(e) => setNewInstancePhone(e.target.value)}
                  className="text-xs"
                />
              </div>
            </div>
            <div className="flex items-center justify-end gap-2 pt-2 border-t border-border">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowInstanceModal(false)}
              >
                Cancelar
              </Button>
              <Button
                variant="default"
                size="sm"
                onClick={() => createInstanceMutation.mutate()}
                disabled={!newInstanceName.trim() || createInstanceMutation.isPending}
              >
                {createInstanceMutation.isPending ? "Provisionando..." : "Provisionar Shard"}
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};

export default OmnichannelWorkspace;
