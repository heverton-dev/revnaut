import * as React from "react";
import {
  Plus,
  Upload,
  Search,
  Building2,
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  Link2,
  Trash2,
  MessageSquarePlus,
  Clock,
  RefreshCw,
  Briefcase,
  MessageCircle,
  Truck,
  ClipboardCheck,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { RouteHeader } from "@/components/ui/RouteHeader";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Tabs } from "@/components/ui/Tabs";
import { DataTable, Column } from "@/components/ui/DataTable";
import { Dialog } from "@/components/ui/Dialog";
import { Sheet } from "@/components/ui/Sheet";
import { CroVerifiedInput } from "@/features/contacts/components/CroVerifiedInput";
import { IcpScoringDashboard } from "@/features/scoring/IcpScoringDashboard";

interface ContactRecord {
  id: number;
  name: string;
  email?: string;
  phone?: string;
  company?: string;
  score?: number;
  cro?: string;
  cro_uf?: string;
  cro_verified?: boolean;
  specialty?: string;
  work_model?: string;
  monthly_implants_volume?: string;
  customer_type?: string;
  city?: string;
  state?: string;
}

interface ContactProfile {
  id: number;
  name: string;
  email?: string;
  company?: string;
  score?: number;
  deals: Array<Record<string, any>>;
  timeline: Array<Record<string, any>>;
}

interface InstitutionRecord {
  id: string;
  name: string;
  institution_type: string;
  city: string;
  state: string;
  coordinator_name: string;
  active_students_count: number;
  accreditation_status: string;
}

interface ContactLinkRecord {
  id: string;
  contact_id: number;
  institution_id: string;
  relationship_type: string;
  role_title?: string;
  is_kol: boolean;
  notes?: string;
  institution_name?: string;
}

interface CfoValidationResult {
  is_compliant: boolean;
  violations: string[];
  warnings: string[];
  has_responsible_cro: boolean;
  detected_cro?: string | null;
}

export const ContactsCrmWorkspace: React.FC = () => {
  const [activeTab, setActiveTab] = React.useState<string>("crm_surgeons");

  // Estados Tab 1: Base de Cirurgiões
  const [contacts, setContacts] = React.useState<ContactRecord[]>([]);
  const [loadingContacts, setLoadingContacts] = React.useState<boolean>(true);
  const [searchQuery, setSearchQuery] = React.useState<string>("");
  const [ufFilter, setUfFilter] = React.useState<string>("ALL");
  const [feedbackMsg, setFeedbackMsg] = React.useState<string | null>(null);
  const [errorMsg, setErrorMsg] = React.useState<string | null>(null);

  // Modal Novo Cirurgião
  const [isNewContactOpen, setIsNewContactOpen] = React.useState<boolean>(false);
  const [newName, setNewName] = React.useState<string>("");
  const [newEmail, setNewEmail] = React.useState<string>("");
  const [newPhone, setNewPhone] = React.useState<string>("");
  const [newCompany, setNewCompany] = React.useState<string>("");
  const [newSpecialty, setNewSpecialty] = React.useState<string>("Implantodontia");
  const [newVolume, setNewVolume] = React.useState<string>("20-50/mês");
  const [newCroData, setNewCroData] = React.useState<{
    cro: string;
    uf: string;
    verified: boolean;
    canonicalCro: string;
  }>({ cro: "123456", uf: "SP", verified: true, canonicalCro: "CRO-SP 123456" });
  const [savingContact, setSavingContact] = React.useState<boolean>(false);

  // Modal Importar CSV
  const [isImportCsvOpen, setIsImportCsvOpen] = React.useState<boolean>(false);
  const [csvStrategy, setCsvStrategy] = React.useState<string>("territorial");
  const [csvRawText, setCsvRawText] = React.useState<string>(
    "name,email,phone,company,cro,cro_uf,specialty,state\nDr. Henrique Bastos,henrique@clinica.med.br,+5511988881111,Clínica Bastos,123456,SP,Implantodontia,SP"
  );
  const [importingCsv, setImportingCsv] = React.useState<boolean>(false);

  // Drawer Dossiê 360° & Timeline
  const [selectedContact, setSelectedContact] = React.useState<ContactRecord | null>(null);
  const [contactProfile, setContactProfile] = React.useState<ContactProfile | null>(null);
  const [contactTimeline, setContactTimeline] = React.useState<Array<Record<string, any>>>([]);
  const [newCommentText, setNewCommentText] = React.useState<string>("");
  const [postingComment, setPostingComment] = React.useState<boolean>(false);

  // Estados Tab 2: Clínicas, Hospitais & Vínculos
  const [institutions, setInstitutions] = React.useState<InstitutionRecord[]>([]);
  const [instName, setInstName] = React.useState<string>("");
  const [instType, setInstType] = React.useState<string>("Faculdade / Pós-Graduação");
  const [instCity, setInstCity] = React.useState<string>("Campinas");
  const [instState, setInstState] = React.useState<string>("SP");
  const [instCoordinator, setInstCoordinator] = React.useState<string>("Prof. Dr. Carlos Alberto");
  const [instStudents, setInstStudents] = React.useState<string>("45");
  const [selectedSurgeonForLink, setSelectedSurgeonForLink] = React.useState<string>("");
  const [selectedInstForLink, setSelectedInstForLink] = React.useState<string>("");
  const [linkRelationType, setLinkRelationType] = React.useState<string>("operates_at");
  const [linkRoleTitle, setLinkRoleTitle] = React.useState<string>("Cirurgião Chefe");
  const [linkIsKol, setLinkIsKol] = React.useState<boolean>(true);
  const [contactLinks, setContactLinks] = React.useState<ContactLinkRecord[]>([]);

  // Estados Tab 3: Auditor Ético CFO 196/2019
  const [cfoCopyText, setCfoCopyText] = React.useState<string>(
    "Reabilitação oral com implantes Cone Morse guiados por tomografia 3D. Responsável Técnico: Dr. Roberto Silveira - CRO-SP 123456."
  );
  const [cfoHasResponsibleCro, setCfoHasResponsibleCro] = React.useState<boolean>(true);
  const [cfoResponsibleCro, setCfoResponsibleCro] = React.useState<string>("CRO-SP 123456");
  const [cfoResult, setCfoResult] = React.useState<CfoValidationResult | null>(null);
  const [validatingCfo, setValidatingCfo] = React.useState<boolean>(false);

  const loadContacts = React.useCallback(async (query?: string) => {
    setLoadingContacts(true);
    setErrorMsg(null);
    try {
      const qParam = query ? `?q=${encodeURIComponent(query)}` : "";
      const res = await fetch(`/api/v1/contacts${qParam}`, {
        headers: { "X-User-Id": "usr-superadmin-god" },
      });
      if (!res.ok) throw new Error(`Falha ao listar contatos (HTTP ${res.status})`);
      const data = await res.json();
      const list: ContactRecord[] = Array.isArray(data) ? data : data.contacts || [];
      setContacts(list);
      if (list.length > 0 && !selectedSurgeonForLink) {
        setSelectedSurgeonForLink(String(list[0].id));
      }
    } catch (err: any) {
      setErrorMsg(err.message);
    } finally {
      setLoadingContacts(false);
    }
  }, [selectedSurgeonForLink]);

  const loadInstitutions = React.useCallback(async () => {
    try {
      const res = await fetch("/api/v1/institutions");
      if (res.ok) {
        const data: InstitutionRecord[] = await res.json();
        setInstitutions(Array.isArray(data) ? data : []);
        if (Array.isArray(data) && data.length > 0 && !selectedInstForLink) {
          setSelectedInstForLink(data[0].id);
        }
      }
    } catch {
      // Silencioso
    }
  }, [selectedInstForLink]);

  const loadContactLinks = React.useCallback(async (contactId: string) => {
    if (!contactId) return;
    try {
      const res = await fetch(`/api/v1/intelligence/links/contact/${contactId}`);
      if (res.ok) {
        const data = await res.json();
        setContactLinks(Array.isArray(data) ? data : []);
      }
    } catch {
      setContactLinks([]);
    }
  }, []);

  React.useEffect(() => {
    loadContacts();
    loadInstitutions();
  }, [loadContacts, loadInstitutions]);

  React.useEffect(() => {
    if (selectedSurgeonForLink) {
      loadContactLinks(selectedSurgeonForLink);
    }
  }, [selectedSurgeonForLink, loadContactLinks]);

  const handleOpenContactDrawer = async (contact: ContactRecord) => {
    setSelectedContact(contact);
    setContactProfile(null);
    setContactTimeline([]);
    try {
      const [profRes, timeRes] = await Promise.all([
        fetch(`/api/v1/contacts/${contact.id}/profile`),
        fetch(`/api/v1/contacts/${contact.id}/timeline`),
      ]);
      if (profRes.ok) {
        setContactProfile(await profRes.json());
      }
      if (timeRes.ok) {
        const tData = await timeRes.json();
        setContactTimeline(Array.isArray(tData.timeline) ? tData.timeline : []);
      }
    } catch {
      // Silencioso
    }
  };

  const handleAddTimelineComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedContact || !newCommentText.trim()) return;
    setPostingComment(true);
    try {
      const res = await fetch(`/api/v1/contacts/${selectedContact.id}/timeline/comments`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-User-Id": "usr-superadmin-god",
        },
        body: JSON.stringify({
          comment: newCommentText.trim(),
          author_name: "Consultor Especialista",
        }),
      });
      if (res.ok) {
        setNewCommentText("");
        const timeRes = await fetch(`/api/v1/contacts/${selectedContact.id}/timeline`);
        if (timeRes.ok) {
          const tData = await timeRes.json();
          setContactTimeline(Array.isArray(tData.timeline) ? tData.timeline : []);
        }
      }
    } finally {
      setPostingComment(false);
    }
  };

  const handleCreateContact = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim() || !newEmail.trim()) return;
    setSavingContact(true);
    setErrorMsg(null);
    try {
      const res = await fetch("/api/v1/contacts", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-User-Id": "usr-superadmin-god",
        },
        body: JSON.stringify({
          name: newName.trim(),
          email: newEmail.trim(),
          phone: newPhone.trim() || "+5511999990000",
          company: newCompany.trim() || "Clínica Odontológica",
          cro: newCroData.cro,
          cro_uf: newCroData.uf,
          cro_verified: newCroData.verified,
          specialty: newSpecialty,
          monthly_implants_volume: newVolume,
          customer_type: "Cirurgião",
          state: newCroData.uf,
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data.detail || `Falha ao cadastrar cirurgião (HTTP ${res.status})`);
      }
      setIsNewContactOpen(false);
      setNewName("");
      setNewEmail("");
      setNewPhone("");
      setNewCompany("");
      setFeedbackMsg(`Cirurgião ${data.name || newName} homologado e cadastrado com sucesso.`);
      await loadContacts();
    } catch (err: any) {
      setErrorMsg(err.message);
    } finally {
      setSavingContact(false);
    }
  };

  const handleImportCsv = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!csvRawText.trim()) return;
    setImportingCsv(true);
    setErrorMsg(null);
    try {
      const res = await fetch("/api/v1/contacts/import", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-User-Id": "usr-superadmin-god",
        },
        body: JSON.stringify({
          strategy: csvStrategy,
          csv_raw: csvRawText,
          contacts: [],
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data.detail || "Falha ao importar lote CSV.");
      }
      setIsImportCsvOpen(false);
      setFeedbackMsg(
        `Importação concluída (${data.strategy_used}): ${data.created_count} criados, ${data.updated_count} atualizados.`
      );
      await loadContacts();
    } catch (err: any) {
      setErrorMsg(err.message);
    } finally {
      setImportingCsv(false);
    }
  };

  const handleCreateInstitution = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!instName.trim()) return;
    setErrorMsg(null);
    try {
      const res = await fetch("/api/v1/institutions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: instName.trim(),
          institution_type: instType,
          city: instCity.trim() || "São Paulo",
          state: instState.trim() || "SP",
          coordinator_name: instCoordinator.trim() || "Coordenador Acadêmico",
          active_students_count: Number(instStudents) || 30,
          accreditation_status: "credenciada",
        }),
      });
      if (!res.ok) throw new Error("Falha ao credenciar instituição.");
      setInstName("");
      setFeedbackMsg("Instituição credenciada com sucesso.");
      await loadInstitutions();
    } catch (err: any) {
      setErrorMsg(err.message);
    }
  };

  const handleCreateLink = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSurgeonForLink || !selectedInstForLink) return;
    setErrorMsg(null);
    try {
      const res = await fetch("/api/v1/intelligence/links", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contact_id: Number(selectedSurgeonForLink),
          institution_id: selectedInstForLink,
          relationship_type: linkRelationType,
          role_title: linkRoleTitle,
          is_kol: linkIsKol,
          notes: "Vínculo societário/clínico homologado",
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Erro ao criar vínculo institucional.");
      }
      setFeedbackMsg("Vínculo multi-clínica registrado no Grafo Clínico.");
      await loadContactLinks(selectedSurgeonForLink);
    } catch (err: any) {
      setErrorMsg(err.message);
    }
  };

  const handleDeleteLink = async (linkId: string) => {
    try {
      const res = await fetch(`/api/v1/intelligence/links/${linkId}`, {
        method: "DELETE",
      });
      if (res.ok) {
        setFeedbackMsg("Vínculo societário removido.");
        await loadContactLinks(selectedSurgeonForLink);
      }
    } catch {
      // Silencioso
    }
  };

  const handleValidateCfoCopy = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!cfoCopyText.trim()) return;
    setValidatingCfo(true);
    try {
      const res = await fetch("/api/v1/contacts/validate-cfo-compliance", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: cfoCopyText,
          has_responsible_cro: cfoHasResponsibleCro,
          responsible_cro: cfoResponsibleCro,
        }),
      });
      if (res.ok) {
        setCfoResult(await res.json());
      }
    } finally {
      setValidatingCfo(false);
    }
  };

  const filteredContacts = React.useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    return contacts.filter((c) => {
      const matchUf =
        ufFilter === "ALL" ||
        c.cro_uf === ufFilter ||
        c.state === ufFilter ||
        String(c.cro || "").includes(ufFilter);
      if (!matchUf) return false;
      if (!q) return true;
      return (
        String(c.name || "").toLowerCase().includes(q) ||
        String(c.company || "").toLowerCase().includes(q) ||
        String(c.cro || "").toLowerCase().includes(q) ||
        String(c.specialty || "").toLowerCase().includes(q)
      );
    });
  }, [contacts, searchQuery, ufFilter]);

  const contactColumns: Column<ContactRecord>[] = [
    {
      key: "name",
      header: "Cirurgião-Dentista / Clínica",
      render: (c) => (
        <div>
          <div className="font-semibold text-text-main">{c.name}</div>
          <div className="text-xs text-text-secondary">{c.company || c.email || "Consultório"}</div>
        </div>
      ),
    },
    {
      key: "cro",
      header: "Registro CRO/UF",
      render: (c) => (
        <div className="flex items-center gap-1.5">
          <Badge variant={c.cro_verified ? "success" : "secondary"} className="text-[10px]">
            {c.cro || `CRO-${c.cro_uf || "SP"} Ativo`}
          </Badge>
        </div>
      ),
    },
    {
      key: "specialty",
      header: "Especialidade",
      render: (c) => (
        <span className="text-xs text-text-main">{c.specialty || "Implantodontia"}</span>
      ),
    },
    {
      key: "score",
      header: "Score ICP",
      render: (c) => (
        <Badge variant={(c.score || 50) >= 75 ? "default" : "navy"} className="text-[10px]">
          {c.score ?? 70} pts
        </Badge>
      ),
    },
  ];

  const [exportFormat, setExportFormat] = React.useState<"csv" | "parquet">("csv");
  const [isExporting, setIsExporting] = React.useState<boolean>(false);

  const handleExportContacts = async () => {
    setIsExporting(true);
    try {
      const res = await fetch(`/api/v1/contacts/export?format=${exportFormat}`, {
        headers: { "X-User-Id": "usr-director-br" },
      });
      if (!res.ok) throw new Error(`Falha ao exportar ${exportFormat.toUpperCase()} da carteira.`);
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `carteira_cirurgioes_${new Date().toISOString().split("T")[0]}.${exportFormat}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      setFeedbackMsg(`Exportação ${exportFormat.toUpperCase()} gerada com sucesso.`);
    } catch (err: any) {
      setErrorMsg(err.message || "Erro ao exportar carteira.");
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <RouteHeader
        title="CRM de Cirurgiões-Dentistas, Clínicas & Compliance CRO/CFO"
        description="Gestão 360° da carteira de implantodontistas, homologação junto ao Conselho Regional de Odontologia, vínculos hospitalares e auditoria ética CFO 196/2019."
        exportConfig={{
          format: exportFormat,
          onFormatChange: (fmt) => setExportFormat(fmt as "csv" | "parquet"),
          onExport: handleExportContacts,
          loading: isExporting,
          label: "FORMATO",
          exportLabel: "Exportar",
        }}
        actions={[
          {
            id: "new-contact",
            label: "Cirurgião",
            variant: "default",
            icon: <Plus className="h-3.5 w-3.5" />,
            title: "Cadastrar Novo Cirurgião-Dentista",
            onClick: () => setIsNewContactOpen(true),
          },
          {
            id: "import-csv",
            label: "Importar",
            variant: "outline",
            icon: <Upload className="h-3.5 w-3.5" />,
            title: "Importar Base CSV",
            onClick: () => setIsImportCsvOpen(true),
          },
          {
            id: "refresh",
            label: "Atualizar",
            variant: "outline",
            icon: <RefreshCw className={`h-3.5 w-3.5 ${loadingContacts ? "animate-spin" : ""}`} />,
            title: "Atualizar Carteira",
            onClick: loadContacts,
            disabled: loadingContacts,
          },
        ]}
      />

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
          { id: "crm_surgeons", label: "Base de Cirurgiões (CRM)", count: filteredContacts.length },
          { id: "institutions_links", label: "Clínicas, Hospitais & Vínculos", count: institutions.length },
          { id: "cfo_compliance", label: "Auditor Ético CFO 196/2019" },
          { id: "icp_scoring", label: "Qualificação & Score ICP" },
        ]}
      />

      {/* ABA 1: BASE DE CIRURGIÕES (CRM) */}
      {activeTab === "crm_surgeons" && (
        <div className="space-y-4">
          <Card className="p-3.5 border-border">
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
              <div className="relative flex-1">
                <Search className="h-4 w-4 text-text-muted absolute left-3 top-2.5 pointer-events-none" />
                <Input
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Buscar cirurgião por nome, CRO, clínica ou especialidade..."
                  className="pl-9"
                />
              </div>
              <div className="w-full sm:w-44">
                <Select
                  aria-label="Filtrar por UF"
                  value={ufFilter}
                  onChange={(e) => setUfFilter(e.target.value)}
                  options={[
                    { value: "ALL", label: "Todas as UFs (BR)" },
                    { value: "SP", label: "CRO-SP" },
                    { value: "PR", label: "CRO-PR" },
                    { value: "RJ", label: "CRO-RJ" },
                    { value: "MG", label: "CRO-MG" },
                    { value: "RS", label: "CRO-RS" },
                  ]}
                />
              </div>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => loadContacts(searchQuery)}
                className="gap-1.5"
              >
                <RefreshCw className="h-3.5 w-3.5" />
                Atualizar
              </Button>
            </div>
          </Card>

          <DataTable
            columns={contactColumns}
            data={filteredContacts}
            isLoading={loadingContacts}
            defaultPageSize={25}
            pageSizeOptions={[25, 50]}
            onRowClick={handleOpenContactDrawer}
            emptyTitle="Nenhum cirurgião encontrado"
            emptyDescription="Cadastre um novo cirurgião-dentista com validação CRO ou importe sua planilha CSV."
          />
        </div>
      )}

      {/* ABA 2: CLÍNICAS, HOSPITAIS & VÍNCULOS SOCIETÁRIOS */}
      {activeTab === "institutions_links" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building2 className="h-4 w-4 text-brand-primary" />
                Instituições, Hospitais & Polos de Pós-Graduação
              </CardTitle>
              <CardDescription>
                Credencie faculdades (Mandic, ABO, APCD), clínicas radiológicas e centros cirúrgicos.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <form onSubmit={handleCreateInstitution} className="space-y-3 p-3 rounded-lg bg-surface-bg border border-border">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  <Input
                    required
                    value={instName}
                    onChange={(e) => setInstName(e.target.value)}
                    placeholder="Nome da Instituição / Hospital *"
                  />
                  <Select
                    value={instType}
                    onChange={(e) => setInstType(e.target.value)}
                    options={[
                      { value: "Faculdade / Pós-Graduação", label: "Faculdade / Pós-Graduação" },
                      { value: "Clínica Odontológica / DSO", label: "Clínica Odontológica / DSO" },
                      { value: "Laboratório Prótese CAD/CAM", label: "Laboratório CAD/CAM" },
                      { value: "Hospital / Centro Cirúrgico", label: "Hospital / Centro Cirúrgico" },
                    ]}
                  />
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  <Input
                    value={instCity}
                    onChange={(e) => setInstCity(e.target.value)}
                    placeholder="Cidade"
                  />
                  <Input
                    value={instState}
                    onChange={(e) => setInstState(e.target.value)}
                    maxLength={2}
                    placeholder="UF"
                  />
                  <Input
                    value={instCoordinator}
                    onChange={(e) => setInstCoordinator(e.target.value)}
                    placeholder="Coordenador"
                  />
                  <Input
                    type="number"
                    value={instStudents}
                    onChange={(e) => setInstStudents(e.target.value)}
                    placeholder="Alunos"
                  />
                </div>
                <Button type="submit" size="sm" className="w-full gap-1.5">
                  <Plus className="h-3.5 w-3.5" />
                  Credenciar Nova Instituição
                </Button>
              </form>

              <div className="divide-y divide-border-subtle max-h-64 overflow-y-auto text-xs">
                {institutions.map((inst) => (
                  <div key={inst.id} className="py-2.5 flex items-center justify-between gap-2">
                    <div>
                      <div className="font-semibold text-text-main">{inst.name}</div>
                      <div className="text-text-secondary">
                        {inst.institution_type} • {inst.city}/{inst.state} • Coord. {inst.coordinator_name}
                      </div>
                    </div>
                    <Badge variant="success" className="text-[10px]">
                      {inst.active_students_count} alunos
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Link2 className="h-4 w-4 text-brand-primary" />
                Vínculos Societários & Atuação Multi-Clínica (N:N)
              </CardTitle>
              <CardDescription>
                Mapeie em quais clínicas o cirurgião opera, quais laboratórios CAD/CAM utiliza e onde leciona como KOL.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <form onSubmit={handleCreateLink} className="space-y-3 p-3 rounded-lg bg-surface-bg border border-border">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  <Select
                    label="Cirurgião-Dentista"
                    value={selectedSurgeonForLink}
                    onChange={(e) => setSelectedSurgeonForLink(e.target.value)}
                    options={
                      contacts.length > 0
                        ? contacts.slice(0, 50).map((c) => ({
                            value: String(c.id),
                            label: `${c.name} (${c.cro || "CRO"})`,
                          }))
                        : [{ value: "1", label: "Cirurgião #1" }]
                    }
                  />
                  <Select
                    label="Instituição / Clínica"
                    value={selectedInstForLink}
                    onChange={(e) => setSelectedInstForLink(e.target.value)}
                    options={
                      institutions.length > 0
                        ? institutions.map((i) => ({ value: i.id, label: i.name }))
                        : [{ value: "inst-1", label: "São Leopoldo Mandic" }]
                    }
                  />
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  <Select
                    label="Natureza do Vínculo"
                    value={linkRelationType}
                    onChange={(e) => setLinkRelationType(e.target.value)}
                    options={[
                      { value: "operates_at", label: "Opera / Atende na Clínica" },
                      { value: "teaches_at", label: "Professor / Coordenador no Polo" },
                      { value: "partner_cadcam", label: "Cliente de Fluxo Digital CAD/CAM" },
                      { value: "kol_speaker", label: "Speaker Oficial / KOL" },
                    ]}
                  />
                  <div>
                    <label className="block text-xs font-medium text-text-secondary mb-1.5">
                      Cargo / Papel Clínico
                    </label>
                    <Input
                      value={linkRoleTitle}
                      onChange={(e) => setLinkRoleTitle(e.target.value)}
                      placeholder="Ex: Diretor Clínico"
                    />
                  </div>
                </div>
                <div className="flex items-center justify-between pt-1">
                  <label className="flex items-center gap-2 text-xs text-text-main cursor-pointer">
                    <input
                      type="checkbox"
                      checked={linkIsKol}
                      onChange={(e) => setLinkIsKol(e.target.checked)}
                    />
                    Atua como Key Opinion Leader (Speaker KOL)
                  </label>
                  <Button type="submit" size="sm" className="gap-1.5">
                    <Link2 className="h-3.5 w-3.5" />
                    Vincular ao Ecossistema
                  </Button>
                </div>
              </form>

              <div className="divide-y divide-border-subtle max-h-56 overflow-y-auto text-xs">
                {contactLinks.length === 0 ? (
                  <p className="text-text-muted py-4 text-center">
                    Nenhum vínculo institucional registrado para este cirurgião.
                  </p>
                ) : (
                  contactLinks.map((lnk) => (
                    <div key={lnk.id} className="py-2.5 flex items-center justify-between gap-2">
                      <div>
                        <div className="font-semibold text-text-main">
                          {lnk.institution_name || lnk.institution_id}
                        </div>
                        <div className="text-text-secondary">
                          {lnk.relationship_type} • {lnk.role_title || "Cirurgião Associado"}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {lnk.is_kol && <Badge variant="navy">KOL Speaker</Badge>}
                        <button
                          type="button"
                          onClick={() => handleDeleteLink(lnk.id)}
                          className="p-1 text-text-muted hover:text-status-danger"
                          aria-label="Remover vínculo"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* ABA 3: AUDITOR ÉTICO CFO 196/2019 */}
      {activeTab === "cfo_compliance" && (
        <Card className="border-border max-w-4xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ShieldCheck className="h-5 w-5 text-status-success" />
              Scanner Determinístico de Conformidade Ética CFO (Resolução 196/2019 & Código de Ética Art. 44)
            </CardTitle>
            <CardDescription>
              Audita textos de anúncios, landing pages e campanhas odontológicas contra promessas de resultado 100% garantido, gratuidade mercantilista e ausência de Responsável Técnico CRO.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <form onSubmit={handleValidateCfoCopy} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold uppercase text-text-secondary mb-1.5">
                  Texto da Peça Publicitária / Copy da Campanha
                </label>
                <textarea
                  rows={4}
                  value={cfoCopyText}
                  onChange={(e) => setCfoCopyText(e.target.value)}
                  className="w-full rounded-md border border-border bg-surface-card p-3 text-sm text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary"
                  placeholder="Cole o texto da peça publicitária para validação ética junto ao CFO..."
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 items-center">
                <Input
                  value={cfoResponsibleCro}
                  onChange={(e) => setCfoResponsibleCro(e.target.value)}
                  placeholder="CRO do Responsável Técnico (ex: CRO-SP 123456)"
                />
                <label className="flex items-center gap-2 text-xs text-text-main cursor-pointer">
                  <input
                    type="checkbox"
                    checked={cfoHasResponsibleCro}
                    onChange={(e) => setCfoHasResponsibleCro(e.target.checked)}
                  />
                  Peça inclui identificação explícita do Responsável Técnico
                </label>
              </div>

              <div className="flex flex-wrap gap-2">
                <Button type="submit" size="sm" disabled={validatingCfo} className="gap-1.5">
                  <ShieldCheck className="h-4 w-4" />
                  {validatingCfo ? "Auditando Copy..." : "Executar Auditoria Ética CFO"}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setCfoCopyText(
                      "Implante dentário com resultado 100% garantido e totalmente sem dor! Avaliação grátis hoje!"
                    );
                    setCfoHasResponsibleCro(false);
                  }}
                >
                  Testar Exemplo Infrator (Bloqueio Art. 44)
                </Button>
              </div>
            </form>

            {cfoResult && (
              <div
                className={`p-4 rounded-lg border space-y-2 text-xs ${
                  cfoResult.is_compliant
                    ? "bg-status-success-subtle border-status-success/30 text-status-success"
                    : "bg-status-danger-subtle border-status-danger/30 text-status-danger"
                }`}
              >
                <div className="flex items-center justify-between font-bold text-sm">
                  <span>
                    {cfoResult.is_compliant
                      ? "APROVADO: Peça Publicitária em Conformidade com o CFO"
                      : "REPROVADO: Infrações Éticas Detectadas (Risco de Processo Ético CRO)"}
                  </span>
                  <Badge variant={cfoResult.is_compliant ? "success" : "danger"}>
                    {cfoResult.is_compliant ? "CONFORME" : `${cfoResult.violations.length} VIOLAÇÕES`}
                  </Badge>
                </div>
                {cfoResult.violations.length > 0 && (
                  <ul className="list-disc pl-5 space-y-1 text-text-main">
                    {cfoResult.violations.map((v, i) => (
                      <li key={i}>{v}</li>
                    ))}
                  </ul>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* ABA 4: QUALIFICAÇÃO & SCORE ICP */}
      {activeTab === "icp_scoring" && <IcpScoringDashboard />}

      {/* Modal Dialog: Novo Cirurgião (CroVerifiedInput + POST /api/v1/contacts) */}
      <Dialog
        isOpen={isNewContactOpen}
        onClose={() => setIsNewContactOpen(false)}
        title="Homologar e Cadastrar Novo Cirurgião-Dentista"
        description="Valida o registro profissional junto ao CRO antes de liberar consignação de implantes."
      >
        <form onSubmit={handleCreateContact} className="space-y-3">
          <CroVerifiedInput
            required
            value={newCroData.cro}
            uf={newCroData.uf}
            onChange={(val) => setNewCroData(val)}
          />
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
            <div>
              <label className="block text-xs font-medium text-text-secondary mb-1">
                Nome Completo do Cirurgião *
              </label>
              <Input
                required
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="Ex: Dra. Juliana Prado"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-text-secondary mb-1">
                E-mail Profissional *
              </label>
              <Input
                type="email"
                required
                value={newEmail}
                onChange={(e) => setNewEmail(e.target.value)}
                placeholder="juliana@clinica.med.br"
              />
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-text-secondary mb-1">
                WhatsApp / Telefone
              </label>
              <Input
                value={newPhone}
                onChange={(e) => setNewPhone(e.target.value)}
                placeholder="+5511988887777"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-text-secondary mb-1">
                Clínica / Instituto
              </label>
              <Input
                value={newCompany}
                onChange={(e) => setNewCompany(e.target.value)}
                placeholder="Instituto Prado Odontologia"
              />
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Select
              label="Especialidade Principal"
              value={newSpecialty}
              onChange={(e) => setNewSpecialty(e.target.value)}
              options={[
                { value: "Implantodontia", label: "Implantodontia" },
                { value: "Cirurgia Bucomaxilofacial", label: "Cirurgia Bucomaxilofacial" },
                { value: "Prótese Dentária", label: "Prótese Dentária" },
                { value: "Periodontia", label: "Periodontia" },
              ]}
            />
            <Select
              label="Volume Mensal de Implantes"
              value={newVolume}
              onChange={(e) => setNewVolume(e.target.value)}
              options={[
                { value: "50+/mês", label: "Acima de 50 implantes/mês (Black)" },
                { value: "20-50/mês", label: "20 a 50 implantes/mês (Gold)" },
                { value: "5-20/mês", label: "5 a 20 implantes/mês (Silver)" },
              ]}
            />
          </div>
          <div className="flex justify-end gap-2 pt-3 border-t border-border-subtle">
            <Button type="button" variant="outline" size="sm" onClick={() => setIsNewContactOpen(false)}>
              Cancelar
            </Button>
            <Button type="submit" size="sm" disabled={savingContact}>
              {savingContact ? "Salvando..." : "Salvar Cirurgião"}
            </Button>
          </div>
        </form>
      </Dialog>

      {/* Modal Dialog: Importar CSV (POST /api/v1/contacts/import) */}
      <Dialog
        isOpen={isImportCsvOpen}
        onClose={() => setIsImportCsvOpen(false)}
        title="Importação em Lote de Cirurgiões (CSV)"
        description="Distribuição automática por território (UF), especialidade ou round-robin."
      >
        <form onSubmit={handleImportCsv} className="space-y-3">
          <Select
            label="Estratégia de Distribuição de Carteira"
            value={csvStrategy}
            onChange={(e) => setCsvStrategy(e.target.value)}
            options={[
              { value: "territorial", label: "Distribuição Territorial por UF (CRO)" },
              { value: "specialty", label: "Por Especialidade (Implantodontia / Buco)" },
              { value: "round_robin", label: "Round-Robin Balanceado" },
            ]}
          />
          <div>
            <label className="block text-xs font-medium text-text-secondary mb-1">
              Conteúdo CSV (Cabeçalho + Linhas)
            </label>
            <textarea
              rows={5}
              value={csvRawText}
              onChange={(e) => setCsvRawText(e.target.value)}
              className="w-full rounded-md border border-border bg-surface-bg p-2.5 font-mono text-xs text-text-main"
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" size="sm" onClick={() => setIsImportCsvOpen(false)}>
              Cancelar
            </Button>
            <Button type="submit" size="sm" disabled={importingCsv}>
              {importingCsv ? "Importando..." : "Processar Lote CSV"}
            </Button>
          </div>
        </form>
      </Dialog>

      {/* Drawer Sheet: Dossiê 360° & Timeline do Cirurgião */}
      <Sheet
        isOpen={Boolean(selectedContact)}
        onClose={() => setSelectedContact(null)}
        title={selectedContact ? `Dossiê 360° • ${selectedContact.name}` : "Dossiê 360°"}
        description={
          selectedContact
            ? `${selectedContact.cro || "CRO Verificado"} • ${selectedContact.specialty || "Implantodontia"}`
            : ""
        }
      >
        {selectedContact && (
          <div className="space-y-5 text-xs">
            <div className="grid grid-cols-2 gap-2 p-3 rounded-lg bg-surface-bg border border-border">
              <div>
                <span className="text-text-secondary block">Clínica Principal</span>
                <strong className="text-text-main">{selectedContact.company || "Consultório"}</strong>
              </div>
              <div>
                <span className="text-text-secondary block">Score Preditivo ICP</span>
                <strong className="text-brand-primary">{contactProfile?.score ?? selectedContact.score ?? 75} pts</strong>
              </div>
              <div>
                <span className="text-text-secondary block">E-mail</span>
                <strong className="text-text-main truncate block">{selectedContact.email || "N/D"}</strong>
              </div>
              <div>
                <span className="text-text-secondary block">Negócios Vinculados</span>
                <strong className="text-text-main">{contactProfile?.deals?.length ?? 0} oportunidades</strong>
              </div>
            </div>

            {/* TICKET-CONTACTS-01..03: Ações rápidas do cirurgião */}
            <div className="grid grid-cols-2 gap-2">
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="gap-1.5 text-xs"
                onClick={() => {
                  window.location.hash = "#!/keypartners";
                }}
              >
                <Briefcase className="h-3.5 w-3.5 text-brand-primary" />
                Vincular Maleta em Consignação
              </Button>
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="gap-1.5 text-xs"
                onClick={() => {
                  const phone = String(selectedContact.phone || "").replace(/\D/g, "");
                  const wa = phone ? (phone.startsWith("55") ? phone : `55${phone}`) : "";
                  window.open(
                    `https://wa.me/${wa}?text=${encodeURIComponent(`Olá Dr(a). ${selectedContact.name}, tudo bem? Aqui é da Revnault.`)}`,
                    "_blank",
                    "noopener,noreferrer"
                  );
                }}
              >
                <MessageCircle className="h-3.5 w-3.5 text-status-whatsapp" />
                Disparar Conversa WhatsApp
              </Button>
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="gap-1.5 text-xs"
                onClick={() => {
                  window.location.hash = "#!/dentgo";
                }}
              >
                <Truck className="h-3.5 w-3.5 text-brand-navy" />
                Solicitar Entrega Expressa
              </Button>
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="gap-1.5 text-xs"
                onClick={async () => {
                  const targets = filteredContacts.filter((c) => c.cro && c.cro.trim());
                  if (targets.length === 0) {
                    setErrorMsg("Nenhum cirurgião visível possui CRO cadastrado.");
                    return;
                  }
                  setLoadingContacts(true);
                  try {
                    let validCount = 0;
                    await Promise.all(
                      targets.map(async (c) => {
                        const res = await fetch("/api/v1/contacts/validate-cro", {
                          method: "POST",
                          headers: { "Content-Type": "application/json" },
                          body: JSON.stringify({
                            cro: c.cro,
                            uf: c.cro_uf || "SP",
                            category: "CD",
                          }),
                        });
                        if (res.ok) validCount++;
                      })
                    );
                    setFeedbackMsg(`Validação em Lote: ${validCount}/${targets.length} cirurgiões validados com sucesso no CFO.`);
                    await loadContacts(searchQuery);
                  } catch (err: any) {
                    setErrorMsg(err.message || "Falha na validação em lote de CROs.");
                  } finally {
                    setLoadingContacts(false);
                  }
                }}
              >
                <ClipboardCheck className="h-3.5 w-3.5 text-status-success" />
                Validar CROs em Lote
              </Button>
            </div>

            {/* Adicionar Nota na Timeline (POST /api/v1/contacts/{id}/timeline/comments) */}
            <form onSubmit={handleAddTimelineComment} className="space-y-2">
              <label className="font-semibold uppercase text-text-secondary flex items-center gap-1.5">
                <MessageSquarePlus className="h-3.5 w-3.5" />
                Registrar Apontamento Clínico / Visita Field
              </label>
              <div className="flex gap-2">
                <Input
                  value={newCommentText}
                  onChange={(e) => setNewCommentText(e.target.value)}
                  placeholder="Ex: Cirurgião solicitou demonstração do Kit Guiado Cone Morse..."
                />
                <Button type="submit" size="sm" disabled={postingComment}>
                  Registrar
                </Button>
              </div>
            </form>

            {/* Timeline Auditável */}
            <div className="space-y-2">
              <span className="font-semibold uppercase text-text-secondary flex items-center gap-1.5">
                <Clock className="h-3.5 w-3.5" />
                Histórico de Interações & Auditoria ({contactTimeline.length})
              </span>
              {contactTimeline.length === 0 ? (
                <p className="text-text-muted py-3">Nenhuma interação registrada até o momento.</p>
              ) : (
                <div className="space-y-2 max-h-72 overflow-y-auto">
                  {contactTimeline.map((item, idx) => (
                    <div key={item.id ?? idx} className="p-2.5 rounded bg-surface-bg border border-border-subtle">
                      <div className="flex justify-between font-medium text-text-main">
                        <span>{item.author_name || item.event_type || "Interação"}</span>
                        <span className="text-[10px] text-text-muted">{item.created_at || ""}</span>
                      </div>
                      <p className="text-text-secondary mt-1">
                        {item.comment || item.description || item.details || ""}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </Sheet>
    </div>
  );
};

export default ContactsCrmWorkspace;
