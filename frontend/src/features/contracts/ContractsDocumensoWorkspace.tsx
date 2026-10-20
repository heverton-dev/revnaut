import * as React from "react";
import {
  FileCheck2,
  Calculator,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Download,
  FileSignature,
  Package,
  RefreshCw,
  Eye,
  PenLine,
  Plus,
  Trash2,
  X,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Tabs } from "@/components/ui/Tabs";
import { DataTable, Column } from "@/components/ui/DataTable";
import { R2DirectUploader } from "@/components/shared/R2DirectUploader";

interface DealOption {
  id: string;
  title: string;
  company_name?: string;
  company?: string;
  contact_name?: string;
  value?: number;
}

interface ContractItem {
  id: string;
  deal_id: string;
  documenso_document_id?: string;
  title: string;
  contract_type: string;
  status: string;
  original_r2_key?: string;
  original_pdf_r2_key?: string;
  signed_pdf_r2_key?: string;
  sha256_hash?: string;
  signer_name?: string;
  signer_email?: string;
  signer_phone?: string;
  signing_url?: string;
  created_at: string;
}

interface CatalogProductItem {
  id: string;
  sku: string;
  name: string;
  category: string;
  anvisa_reg?: string;
  prosthetic_platform?: string;
  recommended_torque?: number;
  base_price: number;
}

interface PriceTableItem {
  id: string;
  table_key: string;
  name: string;
  discount_factor: number;
}

interface ProposalCalculation {
  status: string;
  requires_approval: boolean;
  base_value: number;
  final_value: number;
  requested_discount_pct: number;
  max_allowed_pct: number;
  request_id?: string | null;
}

interface SignaturePadModalProps {
  contractTitle: string;
  onCancel: () => void;
  onConfirm: (dataUrl: string) => void;
}

const SignaturePadModal: React.FC<SignaturePadModalProps> = ({ contractTitle, onCancel, onConfirm }) => {
  const canvasRef = React.useRef<HTMLCanvasElement>(null);
  const drawingRef = React.useRef<boolean>(false);
  const [hasInk, setHasInk] = React.useState<boolean>(false);

  const pointFrom = (clientX: number, clientY: number) => {
    const canvas = canvasRef.current!;
    const rect = canvas.getBoundingClientRect();
    return {
      x: ((clientX - rect.left) / rect.width) * canvas.width,
      y: ((clientY - rect.top) / rect.height) * canvas.height,
    };
  };

  const start = (clientX: number, clientY: number) => {
    const ctx = canvasRef.current?.getContext("2d");
    if (!ctx) return;
    const { x, y } = pointFrom(clientX, clientY);
    ctx.lineWidth = 2.5;
    ctx.lineCap = "round";
    ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue("--color-text-main") || "black";
    ctx.beginPath();
    ctx.moveTo(x, y);
    drawingRef.current = true;
  };

  const move = (clientX: number, clientY: number) => {
    if (!drawingRef.current) return;
    const ctx = canvasRef.current?.getContext("2d");
    if (!ctx) return;
    const { x, y } = pointFrom(clientX, clientY);
    ctx.lineTo(x, y);
    ctx.stroke();
    setHasInk(true);
  };

  const end = () => {
    drawingRef.current = false;
  };

  const clear = () => {
    const canvas = canvasRef.current;
    canvas?.getContext("2d")?.clearRect(0, 0, canvas.width, canvas.height);
    setHasInk(false);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-text-main/50">
      <div className="bg-surface-card border border-border rounded-xl w-full max-w-xl p-4 space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-text-main">Assinar na Tela: {contractTitle}</h3>
          <button type="button" onClick={onCancel} aria-label="Fechar" className="text-text-secondary hover:text-text-main">
            <X className="h-4 w-4" />
          </button>
        </div>
        <p className="text-xs text-text-secondary">Desenhe a assinatura do cirurgião com o mouse ou o dedo.</p>
        <canvas
          ref={canvasRef}
          width={600}
          height={220}
          aria-label="Área de assinatura"
          className="w-full h-44 rounded border border-border bg-surface-bg touch-none"
          onMouseDown={(e) => start(e.clientX, e.clientY)}
          onMouseMove={(e) => move(e.clientX, e.clientY)}
          onMouseUp={end}
          onMouseLeave={end}
          onTouchStart={(e) => start(e.touches[0].clientX, e.touches[0].clientY)}
          onTouchMove={(e) => move(e.touches[0].clientX, e.touches[0].clientY)}
          onTouchEnd={end}
        />
        <div className="flex items-center justify-between">
          <Button type="button" size="sm" variant="secondary" onClick={clear} className="gap-1.5">
            <Trash2 className="h-3.5 w-3.5" />
            Limpar
          </Button>
          <Button
            type="button"
            size="sm"
            disabled={!hasInk}
            onClick={() => onConfirm(canvasRef.current!.toDataURL("image/png"))}
            className="gap-1.5"
          >
            <ShieldCheck className="h-3.5 w-3.5" />
            Confirmar Assinatura
          </Button>
        </div>
      </div>
    </div>
  );
};

export const ContractsDocumensoWorkspace: React.FC = () => {
  const [activeTab, setActiveTab] = React.useState<string>("documenso_lifecycle");
  const [feedbackMsg, setFeedbackMsg] = React.useState<string | null>(null);
  const [errorMsg, setErrorMsg] = React.useState<string | null>(null);

  // Estados Tab 1: Contratos Documenso
  const [deals, setDeals] = React.useState<DealOption[]>([]);
  const [selectedDealId, setSelectedDealId] = React.useState<string>("d-1");
  const [contracts, setContracts] = React.useState<ContractItem[]>([]);
  const [loadingContracts, setLoadingContracts] = React.useState<boolean>(false);
  const [contractType, setContractType] = React.useState<string>("termo_consignacao");
  const [signerName, setSignerName] = React.useState<string>("Dr. Roberto Silveira");
  const [signerEmail, setSignerEmail] = React.useState<string>("roberto@clinica.med.br");
  const [signerPhone, setSignerPhone] = React.useState<string>("+5511998877665");
  const [generatingContract, setGeneratingContract] = React.useState<boolean>(false);

  // Estados Tab 2: Catálogo ANVISA & Simulador de Proposta Comercial
  const [products, setProducts] = React.useState<CatalogProductItem[]>([]);
  const [priceTables, setPriceTables] = React.useState<PriceTableItem[]>([]);
  const [selectedTableKey, setSelectedTableKey] = React.useState<string>("BALCAO");
  const [selectedSku, setSelectedSku] = React.useState<string>("IMP-CM-37511");
  const [quantity, setQuantity] = React.useState<string>("20");
  const [discountPct, setDiscountPct] = React.useState<string>("12");
  const [userRole, setUserRole] = React.useState<string>("consultor");
  const [proposalResult, setProposalResult] = React.useState<ProposalCalculation | null>(null);
  const [calculatingProposal, setCalculatingProposal] = React.useState<boolean>(false);
  const [approvingDiscount, setApprovingDiscount] = React.useState<boolean>(false);
  const [proposalItems, setProposalItems] = React.useState<Array<{ sku: string; quantity: number; name: string }>>([]);
  const [previewContract, setPreviewContract] = React.useState<ContractItem | null>(null);
  const [signingContract, setSigningContract] = React.useState<ContractItem | null>(null);

  // Estados Tab 3: Custódia R2 & Download Pré-Assinado
  const [r2KeyInput, setR2KeyInput] = React.useState<string>(
    "0f14ffff/contracts/minuta_comodato_padrao.pdf"
  );
  const [presignedDownloadUrl, setPresignedDownloadUrl] = React.useState<string | null>(null);

  const loadInitialData = React.useCallback(async () => {
    try {
      const [dealsRes, prodRes, tabRes] = await Promise.all([
        fetch("/api/v1/deals"),
        fetch("/api/v1/deals/catalog/products"),
        fetch("/api/v1/deals/catalog/price-tables"),
      ]);

      if (dealsRes.ok) {
        const dJson = await dealsRes.json();
        const dList: DealOption[] = Array.isArray(dJson) ? dJson : (Array.isArray(dJson?.deals) ? dJson.deals : []);
        setDeals(dList);
        if (dList.length > 0) {
          setSelectedDealId(String(dList[0].id));
        }
      }

      if (prodRes.ok) {
        const pList: CatalogProductItem[] = await prodRes.json();
        setProducts(Array.isArray(pList) ? pList : []);
        if (Array.isArray(pList) && pList.length > 0) {
          setSelectedSku(pList[0].sku);
        }
      }

      if (tabRes.ok) {
        const tList: PriceTableItem[] = await tabRes.json();
        setPriceTables(Array.isArray(tList) ? tList : []);
        if (Array.isArray(tList) && tList.length > 0) {
          setSelectedTableKey(tList[0].table_key);
        }
      }
    } catch {
      // Silencioso
    }
  }, []);

  const loadDealContracts = React.useCallback(async (dealId: string) => {
    if (!dealId) return;
    setLoadingContracts(true);
    try {
      const res = await fetch(`/api/v1/deals/${dealId}/contracts`);
      if (res.ok) {
        const list = await res.json();
        setContracts(Array.isArray(list) ? list : []);
      }
    } catch {
      setContracts([]);
    } finally {
      setLoadingContracts(false);
    }
  }, []);

  React.useEffect(() => {
    loadInitialData();
  }, [loadInitialData]);

  React.useEffect(() => {
    if (selectedDealId) {
      loadDealContracts(selectedDealId);
    }
  }, [selectedDealId, loadDealContracts]);

  const handleGenerateContract = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDealId) return;
    setGeneratingContract(true);
    setErrorMsg(null);
    setFeedbackMsg(null);
    try {
      const res = await fetch(`/api/v1/deals/${selectedDealId}/generate-contract`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          deal_id: selectedDealId,
          contract_type: contractType,
          signer_name: signerName,
          signer_email: signerEmail,
          signer_phone: signerPhone,
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data.detail || "Falha ao emitir contrato digital Documenso.");
      }
      setFeedbackMsg(
        `Contrato Documenso (${data.documenso_document_id}) emitido e enviado para assinatura!`
      );
      await loadDealContracts(selectedDealId);
    } catch (err: any) {
      setErrorMsg(err.message);
    } finally {
      setGeneratingContract(false);
    }
  };

  const handleAddProposalItem = () => {
    const qty = Math.max(1, Number(quantity) || 1);
    const name = products.find((p) => p.sku === selectedSku)?.name || selectedSku;
    setProposalItems((prev) => {
      const existing = prev.find((i) => i.sku === selectedSku);
      if (existing) {
        return prev.map((i) => (i.sku === selectedSku ? { ...i, quantity: i.quantity + qty } : i));
      }
      return [...prev, { sku: selectedSku, quantity: qty, name }];
    });
  };

  const handleSimulateDocumensoWebhook = async (contract: ContractItem, signatureDataUrl?: string) => {
    setErrorMsg(null);
    setFeedbackMsg(null);
    try {
      const docId = contract.documenso_document_id || contract.id;
      const res = await fetch("/api/v1/webhooks/documenso/document-completed", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          event: "DOCUMENT_COMPLETED",
          data: {
            id: docId,
            title: contract.title,
            status: "COMPLETED",
            meta: {
              deal_id: contract.deal_id || selectedDealId,
              ...(signatureDataUrl ? { signature_png: signatureDataUrl } : {}),
            },
          },
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data.detail || "Erro ao simular conclusão de assinatura.");
      }
      setFeedbackMsg(
        `Assinatura concluída! Manifesto SHA-256: ${String(data.sha256_hash || "").slice(0, 24)}... (Deal movido para Estágio #${data.new_stage_id})`
      );
      await loadDealContracts(selectedDealId);
    } catch (err: any) {
      setErrorMsg(err.message);
    }
  };

  // TICKET-DOC-02: Renovação Automática de Vigência (+12m)
  const handleRenewContract = async (contract: ContractItem) => {
    setErrorMsg(null);
    setFeedbackMsg(null);
    try {
      const res = await fetch(`/api/v1/deals/${contract.deal_id || selectedDealId}/generate-contract`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contract_type: "renewal",
          signer_name: contract.signer_name || signerName,
          signer_email: contract.signer_email || signerEmail,
          signer_phone: contract.signer_phone || signerPhone,
          renewal_months: 12,
          parent_contract_id: contract.id,
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || "Erro ao renovar vigência do contrato.");
      setFeedbackMsg(`Renovação de +12 meses emitida (${data.id || data.contract_id || "OK"}). Nova vigência encerra em 12 meses.`);
      await loadDealContracts(selectedDealId);
    } catch (err: any) {
      setErrorMsg(err.message);
    }
  };

  const handleCalculateProposal = async (e: React.FormEvent) => {
    e.preventDefault();
    setCalculatingProposal(true);
    setErrorMsg(null);
    try {
      const res = await fetch("/api/v1/deals/catalog/calculate-proposal", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          deal_id: selectedDealId || "d-1",
          table_key: selectedTableKey,
          items:
            proposalItems.length > 0
              ? proposalItems.map((i) => ({ sku: i.sku, quantity: i.quantity }))
              : [{ sku: selectedSku, quantity: Math.max(1, Number(quantity) || 1) }],
          requested_discount_pct: Number(discountPct) || 0,
          user_id: "usr-consultant-pr",
          user_role: userRole,
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data.detail || "Erro ao calcular proposta comercial.");
      }
      setProposalResult(data);
    } catch (err: any) {
      setErrorMsg(err.message);
    } finally {
      setCalculatingProposal(false);
    }
  };

  const handleApproveDiscount = async () => {
    if (!proposalResult?.request_id) return;
    setApprovingDiscount(true);
    setErrorMsg(null);
    try {
      const res = await fetch("/api/v1/deals/catalog/approve-discount", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          request_id: proposalResult.request_id,
          approver_user_id: "usr-director-br",
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data.detail || "Falha ao aprovar alçada de desconto.");
      }
      setProposalResult({
        ...proposalResult,
        status: "APPROVED",
        requires_approval: false,
      });
      setFeedbackMsg(`Alçada de desconto #${data.request_id} aprovada pela Diretoria Comercial.`);
    } catch (err: any) {
      setErrorMsg(err.message);
    } finally {
      setApprovingDiscount(false);
    }
  };

  const handlePresignDownload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!r2KeyInput.trim()) return;
    setErrorMsg(null);
    try {
      const res = await fetch(
        `/api/v1/storage/presign-download?key=${encodeURIComponent(r2KeyInput.trim())}`,
        {
          headers: { "X-Account-ID": "0f14ffff" },
        }
      );
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data.detail || "Acesso negado ou chave R2 inválida para este tenant.");
      }
      setPresignedDownloadUrl(data.download_url || data.url || r2KeyInput);
      setFeedbackMsg("URL pré-assinada S3 v4 gerada com isolamento multi-tenant.");
    } catch (err: any) {
      setErrorMsg(err.message);
    }
  };

  const productColumns: Column<CatalogProductItem>[] = [
    {
      key: "sku",
      header: "SKU / Implante",
      render: (p) => (
        <div>
          <div className="font-semibold text-text-main">{p.name}</div>
          <div className="text-xs font-mono text-text-secondary">{p.sku}</div>
        </div>
      ),
    },
    {
      key: "anvisa_reg",
      header: "Registro ANVISA",
      render: (p) => (
        <Badge variant="success" className="text-[10px]">
          {p.anvisa_reg || "ANVISA Ativo"}
        </Badge>
      ),
    },
    {
      key: "prosthetic_platform",
      header: "Plataforma & Torque",
      render: (p) => (
        <span className="text-xs text-text-main">
          {p.prosthetic_platform || p.category} • {p.recommended_torque ?? 35} N.cm
        </span>
      ),
    },
    {
      key: "base_price",
      header: "Preço Base",
      render: (p) => (
        <span className="font-semibold text-text-main">
          {new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(
            p.base_price || 0
          )}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-text-main">
            Propostas e Contratos com Assinatura Digital
          </h1>
          <p className="text-xs sm:text-sm text-text-secondary mt-1">
            Emissão de propostas comerciais e contratos com assinatura digital, catálogo de produtos e custódia segura de arquivos.
          </p>
        </div>
        <Button
          variant="secondary"
          size="sm"
          onClick={() => {
            loadInitialData();
            loadDealContracts(selectedDealId);
          }}
          className="gap-1.5 self-start sm:self-auto"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          Sincronizar Central
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
          { id: "documenso_lifecycle", label: "Propostas e Contratos Digitais", count: contracts.length },
          { id: "anvisa_catalog_pricing", label: "Catálogo & Simulador de Proposta", count: products.length },
          { id: "r2_custody", label: "Arquivos Salvos e Minutas PDF" },
        ]}
      />

      {/* ABA 1: CICLO DE VIDA DE CONTRATOS DOCUMENSO */}
      {activeTab === "documenso_lifecycle" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileSignature className="h-4 w-4 text-brand-primary" />
                Emitir Contrato Digital
              </CardTitle>
              <CardDescription>
                Gera minuta PDF no R2 e dispara link de assinatura via Documenso.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleGenerateContract} className="space-y-3">
                <Select
                  label="Negócio / Oportunidade Vinculada"
                  value={selectedDealId}
                  onChange={(e) => setSelectedDealId(e.target.value)}
                  options={
                    deals.length > 0
                      ? deals.slice(0, 40).map((d) => ({
                          value: String(d.id),
                          label: `#${d.id} - ${d.title}`,
                        }))
                      : [{ value: "d-1", label: "#d-1 - Oportunidade Padrão" }]
                  }
                />
                <Select
                  label="Modalidade Contratual"
                  value={contractType}
                  onChange={(e) => setContractType(e.target.value)}
                  options={[
                    { value: "termo_consignacao", label: "Contrato de Comodato & Consignação" },
                    { value: "fornecimento_implantes", label: "Contrato de Fornecimento de Implantes" },
                    { value: "proposta", label: "Termo de Proposta Comercial Fechada" },
                  ]}
                />
                <div>
                  <label className="block text-xs font-medium text-text-secondary mb-1">
                    Cirurgião Signatário
                  </label>
                  <Input
                    required
                    value={signerName}
                    onChange={(e) => setSignerName(e.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-text-secondary mb-1">
                    E-mail para Manifesto ICP
                  </label>
                  <Input
                    type="email"
                    required
                    value={signerEmail}
                    onChange={(e) => setSignerEmail(e.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-text-secondary mb-1">
                    WhatsApp para Link Rápido
                  </label>
                  <Input
                    value={signerPhone}
                    onChange={(e) => setSignerPhone(e.target.value)}
                  />
                </div>
                <Button type="submit" size="sm" disabled={generatingContract} className="w-full gap-1.5">
                  <FileCheck2 className="h-4 w-4" />
                  {generatingContract ? "Gerando Minuta..." : "Gerar Contrato Digital"}
                </Button>
              </form>
            </CardContent>
          </Card>

          <Card className="lg:col-span-2 border-border">
            <CardHeader>
              <CardTitle>Contratos Vinculados ao Deal #{selectedDealId}</CardTitle>
              <CardDescription>
                Acompanhe o status de assinatura e valide o manifesto criptográfico SHA-256.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loadingContracts ? (
                <p className="text-xs text-text-muted py-6">Carregando contratos...</p>
              ) : contracts.length === 0 ? (
                <div className="p-6 rounded-lg border border-dashed border-border text-center space-y-2">
                  <p className="text-sm font-medium text-text-main">
                    Nenhuma minuta emitida para o Deal #{selectedDealId}
                  </p>
                  <p className="text-xs text-text-secondary">
                    Utilize o formulário ao lado para gerar um Contrato Digital Documenso.
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {contracts.map((c) => {
                    const isSigned = c.status === "SIGNED" || c.status === "SIGNED_COMPLETED";
                    return (
                      <div
                        key={c.id}
                        className="p-4 rounded-lg border border-border bg-surface-bg/50 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                      >
                        <div className="space-y-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="font-semibold text-sm text-text-main truncate">
                              {c.title}
                            </span>
                            <Badge variant={isSigned ? "success" : "warning"}>
                              {isSigned ? "ASSINADO DIGITALMENTE" : c.status}
                            </Badge>
                          </div>
                          <p className="text-xs text-text-secondary">
                            Signatário: {c.signer_name || signerName} • Código:{" "}
                            <code className="font-mono">{c.documenso_document_id || c.id}</code>
                          </p>
                          {c.sha256_hash && (
                            <p className="text-[11px] font-mono text-status-success break-all">
                              Validação Digital: {c.sha256_hash.slice(0, 24)}...
                            </p>
                          )}
                        </div>

                        <div className="flex flex-wrap gap-2 shrink-0">
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={() => setPreviewContract(c)}
                            className="gap-1.5"
                          >
                            <Eye className="h-3.5 w-3.5 text-brand-primary" />
                            Visualizar Minuta PDF
                          </Button>
                          {!isSigned && (
                            <Button
                              size="sm"
                              variant="secondary"
                              onClick={() => setSigningContract(c)}
                              className="gap-1.5"
                            >
                              <PenLine className="h-3.5 w-3.5 text-brand-primary" />
                              Assinar na Tela (Signature Pad)
                            </Button>
                          )}
                          {!isSigned && (
                            <Button
                              size="sm"
                              variant="secondary"
                              onClick={() => handleSimulateDocumensoWebhook(c)}
                              className="gap-1.5"
                            >
                              <ShieldCheck className="h-3.5 w-3.5 text-status-success" />
                              Simular Assinatura Digital
                            </Button>
                          )}
                          {isSigned && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleRenewContract(c)}
                              className="gap-1.5"
                            >
                              <RefreshCw className="h-3.5 w-3.5 text-brand-navy" />
                              Renovar Vigência (+12m)
                            </Button>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* ABA 2: CATÁLOGO ANVISA & SIMULADOR DE PROPOSTA COMERCIAL */}
      {activeTab === "anvisa_catalog_pricing" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card className="border-border">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calculator className="h-4 w-4 text-brand-primary" />
                  Simulador de Proposta & Alçada
                </CardTitle>
                <CardDescription>
                  Valida automaticamente o limite de desconto por cargo (Consultor vs. Gestor/Diretor).
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleCalculateProposal} className="space-y-3">
                  <Select
                    label="Tabela de Preço Comercial"
                    value={selectedTableKey}
                    onChange={(e) => setSelectedTableKey(e.target.value)}
                    options={
                      priceTables.length > 0
                        ? priceTables.map((t) => ({
                            value: t.table_key,
                            label: `${t.name} (${t.table_key})`,
                          }))
                        : [
                            { value: "BALCAO", label: "Tabela Balcão Padrão" },
                            { value: "FRANQUIA", label: "Tabela Redes & Franquias" },
                          ]
                    }
                  />
                  <Select
                    label="Produto do Catálogo ANVISA"
                    value={selectedSku}
                    onChange={(e) => setSelectedSku(e.target.value)}
                    options={
                      products.length > 0
                        ? products.map((p) => ({
                            value: p.sku,
                            label: `${p.sku} - ${p.name}`,
                          }))
                        : [{ value: "IMP-CM-37511", label: "IMP-CM-37511 - Implante Cone Morse" }]
                    }
                  />
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="block text-xs font-medium text-text-secondary mb-1">
                        Quantidade
                      </label>
                      <Input
                        type="number"
                        min="1"
                        value={quantity}
                        onChange={(e) => setQuantity(e.target.value)}
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-text-secondary mb-1">
                        Desconto (%)
                      </label>
                      <Input
                        type="number"
                        min="0"
                        max="80"
                        step="0.5"
                        value={discountPct}
                        onChange={(e) => setDiscountPct(e.target.value)}
                      />
                    </div>
                  </div>
                  <Button
                    type="button"
                    size="sm"
                    variant="secondary"
                    onClick={handleAddProposalItem}
                    className="w-full gap-1.5"
                  >
                    <Plus className="h-3.5 w-3.5 text-brand-primary" />
                    Adicionar Item ao Carrinho da Proposta
                  </Button>
                  {proposalItems.length > 0 && (
                    <ul className="rounded-lg border border-border divide-y divide-border text-xs">
                      {proposalItems.map((i) => (
                        <li key={i.sku} className="flex items-center justify-between gap-2 p-2">
                          <span className="min-w-0 truncate">
                            <code className="font-mono">{i.sku}</code> x {i.quantity} - {i.name}
                          </span>
                          <button
                            type="button"
                            aria-label={`Remover ${i.sku}`}
                            onClick={() => setProposalItems((prev) => prev.filter((x) => x.sku !== i.sku))}
                            className="text-status-danger shrink-0"
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </button>
                        </li>
                      ))}
                    </ul>
                  )}
                  <Select
                    label="Alçada do Proponente"
                    value={userRole}
                    onChange={(e) => setUserRole(e.target.value)}
                    options={[
                      { value: "consultor", label: "Consultor Comercial (Teto 5%)" },
                      { value: "gerente", label: "Gerente Regional (Teto 15%)" },
                      { value: "diretor", label: "Diretor Nacional (Teto 30%)" },
                    ]}
                  />
                  <Button type="submit" size="sm" disabled={calculatingProposal} className="w-full">
                    {calculatingProposal ? "Calculando..." : "Calcular Proposta & Validar Alçada"}
                  </Button>
                </form>

                {proposalResult && (
                  <div className="mt-4 p-3 rounded-lg bg-surface-bg border border-border space-y-2 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-text-main">Status da Alçada:</span>
                      <Badge variant={proposalResult.requires_approval ? "warning" : "success"}>
                        {proposalResult.status}
                      </Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-text-secondary">Valor Base:</span>
                      <span>
                        {new Intl.NumberFormat("pt-BR", {
                          style: "currency",
                          currency: "BRL",
                        }).format(proposalResult.base_value)}
                      </span>
                    </div>
                    <div className="flex justify-between font-bold text-text-main">
                      <span>Valor Final Líquido:</span>
                      <span className="text-brand-primary">
                        {new Intl.NumberFormat("pt-BR", {
                          style: "currency",
                          currency: "BRL",
                        }).format(proposalResult.final_value)}
                      </span>
                    </div>
                    {proposalResult.requires_approval && proposalResult.request_id && (
                      <Button
                        type="button"
                        size="sm"
                        variant="secondary"
                        onClick={handleApproveDiscount}
                        disabled={approvingDiscount}
                        className="w-full mt-2 gap-1.5"
                      >
                        <ShieldCheck className="h-3.5 w-3.5 text-status-success" />
                        {approvingDiscount
                          ? "Aprovando..."
                          : `Aprovar Desconto como Gestor (#${proposalResult.request_id})`}
                      </Button>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>

            <div className="lg:col-span-2">
              <Card className="border-border">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Package className="h-4 w-4 text-brand-primary" />
                    Catálogo Técnico de Implantes & Componentes Homologados ANVISA
                  </CardTitle>
                  <CardDescription>
                    Todos os itens possuem registro sanitário ativo e torque recomendado de inserção.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <DataTable
                    columns={productColumns}
                    data={products}
                    defaultPageSize={25}
                    enablePagination={false}
                  />
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      )}

      {/* ABA 3: CUSTÓDIA DE MINUTAS PDF NO R2 */}
      {activeTab === "r2_custody" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="border-border">
            <CardHeader>
              <CardTitle>Upload Direto de Minutas PDF (Arquivos Salvos)</CardTitle>
              <CardDescription>
                Armazenamento seguro com isolamento por conta.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <R2DirectUploader
                module="contracts"
                accept=".pdf"
                onUploadComplete={({ key }) => {
                  setR2KeyInput(key);
                  setFeedbackMsg(`Minuta arquivada no R2 com chave: ${key}`);
                }}
              />
            </CardContent>
          </Card>

          <Card className="border-border">
            <CardHeader>
              <CardTitle>Consulta & Download Pré-Assinado de Minuta R2</CardTitle>
              <CardDescription>
                Valida isolamento multi-tenant antes de emitir link temporário de leitura.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <form onSubmit={handlePresignDownload} className="space-y-3">
                <div>
                  <label className="block text-xs font-medium text-text-secondary mb-1">
                    Chave do Objeto no Bucket R2
                  </label>
                  <Input
                    value={r2KeyInput}
                    onChange={(e) => setR2KeyInput(e.target.value)}
                    placeholder="0f14ffff/contracts/arquivo.pdf"
                  />
                </div>
                <Button type="submit" size="sm" className="gap-1.5">
                  <Download className="h-3.5 w-3.5" />
                  Gerar Link de Download Pré-Assinado
                </Button>
              </form>

              {presignedDownloadUrl && (
                <div className="p-3 rounded-lg bg-surface-bg border border-border text-xs space-y-1">
                  <span className="font-semibold text-status-success block">
                    URL Temporária Autorizada (900s TTL):
                  </span>
                  <code className="font-mono text-[11px] text-text-main break-all block">
                    {presignedDownloadUrl}
                  </code>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {previewContract && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-text-main/50">
          <div className="bg-surface-card border border-border rounded-xl w-full max-w-3xl p-4 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-text-main truncate">{previewContract.title}</h3>
              <div className="flex items-center gap-2">
                <a
                  href={`/api/v1/storage/files/${previewContract.original_r2_key || previewContract.original_pdf_r2_key || "0f14ffff/contracts/minuta.pdf"}`}
                  download
                  className="inline-flex items-center gap-1.5 h-8 px-3 rounded-md border border-border text-xs text-text-main hover:bg-surface-bg"
                >
                  <Download className="h-3.5 w-3.5" />
                  Baixar Minuta PDF
                </a>
                <button
                  type="button"
                  aria-label="Fechar visualização"
                  onClick={() => setPreviewContract(null)}
                  className="text-text-secondary hover:text-text-main"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>
            <iframe
              title="Pré-visualização do PDF do contrato"
              src={`/api/v1/storage/files/${previewContract.original_r2_key || previewContract.original_pdf_r2_key || "0f14ffff/contracts/minuta.pdf"}`}
              className="w-full h-96 rounded border border-border"
            />
          </div>
        </div>
      )}

      {signingContract && (
        <SignaturePadModal
          contractTitle={signingContract.title}
          onCancel={() => setSigningContract(null)}
          onConfirm={async (dataUrl) => {
            const target = signingContract;
            setSigningContract(null);
            await handleSimulateDocumensoWebhook(target, dataUrl);
          }}
        />
      )}
    </div>
  );
};

export default ContractsDocumensoWorkspace;
