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
  original_pdf_r2_key?: string;
  signed_pdf_r2_key?: string;
  sha256_hash?: string;
  signer_name?: string;
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
        const dList: DealOption[] = Array.isArray(dJson) ? dJson : dJson.deals || [];
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

  const handleSimulateDocumensoWebhook = async (contract: ContractItem) => {
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
            meta: { deal_id: contract.deal_id || selectedDealId },
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
          items: [{ sku: selectedSku, quantity: Math.max(1, Number(quantity) || 1) }],
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
            Central de Contratos Digitais Documenso, Catálogo ANVISA & Alçadas
          </h1>
          <p className="text-xs sm:text-sm text-text-secondary mt-1">
            Emissão de minutas de comodato cirúrgico com assinatura SHA-256, calculadora de propostas multi-tabela e custódia no Cloudflare R2.
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
          { id: "documenso_lifecycle", label: "Ciclo de Vida de Contratos Documenso", count: contracts.length },
          { id: "anvisa_catalog_pricing", label: "Catálogo ANVISA & Simulador de Proposta", count: products.length },
          { id: "r2_custody", label: "Custódia de Minutas PDF no R2" },
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
                              {isSigned ? "ASSINADO SHA-256" : c.status}
                            </Badge>
                          </div>
                          <p className="text-xs text-text-secondary">
                            Signatário: {c.signer_name || signerName} • Doc ID:{" "}
                            <code className="font-mono">{c.documenso_document_id || c.id}</code>
                          </p>
                          {c.sha256_hash && (
                            <p className="text-[11px] font-mono text-status-success break-all">
                              SHA-256: {c.sha256_hash}
                            </p>
                          )}
                        </div>

                        {!isSigned && (
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={() => handleSimulateDocumensoWebhook(c)}
                            className="shrink-0 gap-1.5"
                          >
                            <ShieldCheck className="h-3.5 w-3.5 text-status-success" />
                            Simular Assinatura SHA-256
                          </Button>
                        )}
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
              <CardTitle>Upload Direto de Minutas PDF no Cloudflare R2</CardTitle>
              <CardDescription>
                Envio criptografado via Presigned PUT URL S3 v4 com isolamento por tenant.
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
    </div>
  );
};

export default ContractsDocumensoWorkspace;
