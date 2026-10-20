import * as React from "react";
import {
  Building2,
  Percent,
  Plus,
  Shield,
  Target,
  DollarSign,
  TrendingUp,
  Sparkles,
  GitFork,
  Sliders,
  Download,
  Lock,
} from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Tabs } from "@/components/ui/Tabs";

export interface BusinessUnit {
  id: string;
  name: string;
  code: string;
  description?: string;
  created_at?: string;
}

export interface Team {
  id: string;
  business_unit_id: string;
  parent_id?: string | null;
  name: string;
  leader_id?: string | null;
  created_at?: string;
}

export interface RoleItem {
  id: string;
  name: string;
  description?: string;
  default_data_scope: string;
  is_admin: number;
  permissions: string[];
}

export interface PermissionCatalogItem {
  resource: string;
  resource_label: string;
  actions: { action: string; label: string; code: string }[];
}

export interface TargetItem {
  id: string;
  period: string;
  entity_name?: string;
  target_amount: number;
  achieved_amount: number;
  achievement_rate_pct: number;
  calculation_basis: string;
  growth_rate_pct: number;
}

export interface CommissionRule {
  id: string;
  role_id: string;
  role_name?: string;
  base_percentage: number;
  accelerator_threshold_pct: number;
  accelerator_percentage: number;
  is_active: number;
}

export interface RbacHierarchyTreeProps {
  accountId?: string;
  className?: string;
}

export function RbacHierarchyTree({
  accountId: initialAccountId,
  className,
}: RbacHierarchyTreeProps) {
  const [accountId, setAccountId] = React.useState<string>(initialAccountId || "");

  React.useEffect(() => {
    if (!initialAccountId) {
      fetch("/api/v1/hierarchy/business-units")
        .then((r) => r.json())
        .then((data) => {
          if (Array.isArray(data) && data.length > 0 && data[0].account_id) {
            setAccountId(data[0].account_id);
          } else {
            setAccountId("0f14ffff");
          }
        })
        .catch(() => setAccountId("0f14ffff"));
    }
  }, [initialAccountId]);

  const [activeTab, setActiveTab] = React.useState<string>("tree");

  // ==========================================
  // TAB 1: DAG DUAL TREE & BU / TEAMS
  // ==========================================
  const [businessUnits, setBusinessUnits] = React.useState<BusinessUnit[]>([]);
  const [teams, setTeams] = React.useState<Team[]>([]);
  const [, setLoadingTree] = React.useState<boolean>(true);
  const [selectedPreset, setSelectedPreset] = React.useState<string>("fabrica_enxuta");
  const [presetFeedback, setPresetFeedback] = React.useState<string | null>(null);

  // Criar BU
  const [newBuName, setNewBuName] = React.useState<string>("");
  const [newBuCode, setNewBuCode] = React.useState<string>("");
  const [showBuModal, setShowBuModal] = React.useState<boolean>(false);

  // Criar Equipe
  const [newTeamName, setNewTeamName] = React.useState<string>("");
  const [newTeamBuId, setNewTeamBuId] = React.useState<string>("");
  const [newTeamParentId, setNewTeamParentId] = React.useState<string>("");
  const [showTeamModal, setShowTeamModal] = React.useState<boolean>(false);

  // Reparent Equipe
  const [reparentTeamId, setReparentTeamId] = React.useState<string>("");
  const [reparentParentId, setReparentParentId] = React.useState<string>("");

  // ==========================================
  // TAB 2: CARGOS & PERMISSÕES GRANULARES
  // ==========================================
  const [roles, setRoles] = React.useState<RoleItem[]>([]);
  const [catalog, setCatalog] = React.useState<PermissionCatalogItem[]>([]);
  const [selectedRoleId, setSelectedRoleId] = React.useState<string>("");
  const [rolePermissions, setRolePermissions] = React.useState<string[]>([]);
  const [savingPermissions, setSavingPermissions] = React.useState<boolean>(false);

  // Criar Cargo
  const [newRoleName, setNewRoleName] = React.useState<string>("");
  const [newRoleDesc, setNewRoleDesc] = React.useState<string>("");
  const [newRoleScope, setNewRoleScope] = React.useState<string>("self");
  const [showRoleModal, setShowRoleModal] = React.useState<boolean>(false);

  // ==========================================
  // TAB 3: METAS COMERCIAIS & SUGESTÃO PREDITIVA
  // ==========================================
  const [targets, setTargets] = React.useState<TargetItem[]>([]);
  const [targetPeriod, setTargetPeriod] = React.useState<string>("2026-Q4");
  const [targetAmount, setTargetAmount] = React.useState<number>(150000);
  const [targetGrowth, setTargetGrowth] = React.useState<number>(15);
  const [targetEntityId, setTargetEntityId] = React.useState<string>("");
  const [targetEntityType, setTargetEntityType] = React.useState<string>("team");
  const [suggestionResult, setSuggestionResult] = React.useState<any>(null);

  // ==========================================
  // TAB 4: COMISSIONAMENTO BIPARTIDO (70/30)
  // ==========================================
  const [commissionRules, setCommissionRules] = React.useState<CommissionRule[]>([]);
  const [newCommRoleId, setNewCommRoleId] = React.useState<string>("");
  const [newCommBase, setNewCommBase] = React.useState<number>(5.0);
  const [newCommThreshold, setNewCommThreshold] = React.useState<number>(100.0);
  const [newCommAccelerator, setNewCommAccelerator] = React.useState<number>(7.5);
  const [statementUserId, setStatementUserId] = React.useState<string>("u_cons_sp_01");
  const [statementPeriod, setStatementPeriod] = React.useState<string>("2026-Q4");
  const [statementResult, setStatementResult] = React.useState<any>(null);
  // TICKET-RBAC-01: Bloqueio temporário de usuário
  const [userBlockToggle, setUserBlockToggle] = React.useState<boolean>(false);

  // Carregar Dados da Tab 1 (BU & Teams)
  const fetchTreeData = React.useCallback(async () => {
    setLoadingTree(true);
    try {
      const [resBu, resTeams] = await Promise.all([
        fetch(`/api/v1/hierarchy/business-units?account_id=${accountId}`),
        fetch(`/api/v1/hierarchy/teams?account_id=${accountId}`),
      ]);
      if (resBu.ok) {
        const buData = await resBu.json();
        const list = Array.isArray(buData) ? buData : (Array.isArray(buData?.business_units) ? buData.business_units : []);
        setBusinessUnits(list);
        if (list.length > 0 && !newTeamBuId) setNewTeamBuId(list[0].id);
      }
      if (resTeams.ok) {
        const teamsData = await resTeams.json();
        const list = Array.isArray(teamsData) ? teamsData : (Array.isArray(teamsData?.teams) ? teamsData.teams : []);
        setTeams(list);
        if (list.length > 0) {
          setReparentTeamId(list[0].id);
          setTargetEntityId(list[0].id);
        }
      }
    } catch {
      // fallback
    } finally {
      setLoadingTree(false);
    }
  }, [accountId, newTeamBuId]);

  // Carregar Dados da Tab 2 (Roles & Catalog)
  const fetchRolesData = React.useCallback(async () => {
    try {
      const [resRoles, resCatalog] = await Promise.all([
        fetch(`/api/v1/hierarchy/roles?account_id=${accountId}`),
        fetch("/api/v1/hierarchy/catalog"),
      ]);
      if (resRoles.ok) {
        const rolesData = await resRoles.json();
        const list = Array.isArray(rolesData) ? rolesData : (Array.isArray(rolesData?.roles) ? rolesData.roles : []);
        setRoles(list);
        if (list.length > 0 && !selectedRoleId) {
          setSelectedRoleId(list[0].id);
          setRolePermissions(Array.isArray(list[0].permissions) ? list[0].permissions : []);
          setNewCommRoleId(list[0].id);
        }
      }
      if (resCatalog.ok) {
        const catalogData = await resCatalog.json();
        const list = Array.isArray(catalogData) ? catalogData : (Array.isArray(catalogData?.catalog) ? catalogData.catalog : []);
        setCatalog(list);
      }
    } catch {
      // fallback
    }
  }, [accountId, selectedRoleId]);

  // Carregar Dados da Tab 3 (Targets)
  const fetchTargetsData = React.useCallback(async () => {
    try {
      const res = await fetch(`/api/v1/hierarchy/targets?account_id=${accountId}`);
      if (res.ok) {
        const data = await res.json();
        const list = Array.isArray(data) ? data : (Array.isArray(data?.targets) ? data.targets : []);
        setTargets(list);
      }
    } catch {
      // fallback
    }
  }, [accountId]);

  // Carregar Dados da Tab 4 (Commissions)
  const fetchCommissionsData = React.useCallback(async () => {
    try {
      const res = await fetch(`/api/v1/hierarchy/commissions/rules?account_id=${accountId}`);
      if (res.ok) {
        const data = await res.json();
        const list = Array.isArray(data) ? data : (Array.isArray(data?.rules) ? data.rules : []);
        setCommissionRules(list);
      }
    } catch {
      // fallback
    }
  }, [accountId]);

  React.useEffect(() => {
    fetchTreeData();
    fetchRolesData();
    fetchTargetsData();
    fetchCommissionsData();
  }, [fetchTreeData, fetchRolesData, fetchTargetsData, fetchCommissionsData]);

  // Selecionar Role para editar permissões
  const handleSelectRole = async (roleId: string) => {
    setSelectedRoleId(roleId);
    try {
      const res = await fetch(`/api/v1/hierarchy/roles/${roleId}/permissions?account_id=${accountId}`);
      if (res.ok) {
        const data = await res.json();
        setRolePermissions(Array.isArray(data?.permissions) ? data.permissions : []);
      }
    } catch {
      // fallback
    }
  };

  // Salvar Matriz de Permissões
  const handleSavePermissions = async () => {
    if (!selectedRoleId) return;
    setSavingPermissions(true);
    try {
      const res = await fetch(`/api/v1/hierarchy/roles/${selectedRoleId}/permissions?account_id=${accountId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ permissions: rolePermissions }),
      });
      if (!res.ok) throw new Error("Erro ao atualizar matriz de permissões");
      alert("Matriz de permissões atualizada com sucesso!");
      await fetchRolesData();
    } catch (err: any) {
      alert(err.message || "Erro");
    } finally {
      setSavingPermissions(false);
    }
  };

  const togglePermission = (code: string) => {
    setRolePermissions((prev) =>
      prev.includes(code) ? prev.filter((p) => p !== code) : [...prev, code]
    );
  };

  // Aplicar Preset Organizacional
  const handleApplyPreset = async () => {
    setPresetFeedback(null);
    try {
      const res = await fetch(`/api/v1/hierarchy/presets/apply?account_id=${accountId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ preset_name: selectedPreset }),
      });
      if (!res.ok) throw new Error("Erro ao aplicar preset");
      const data = await res.json();
      setPresetFeedback(`Preset '${selectedPreset}' aplicado! ${data.teams_created || 0} equipes estruturadas.`);
      await fetchTreeData();
      await fetchRolesData();
    } catch (err: any) {
      setPresetFeedback(`Erro: ${err.message}`);
    }
  };

  // Criar BU
  const handleCreateBu = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newBuName || !newBuCode) return;
    try {
      const res = await fetch(`/api/v1/hierarchy/business-units?account_id=${accountId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: newBuName, code: newBuCode }),
      });
      if (!res.ok) throw new Error("Falha ao criar Business Unit");
      setShowBuModal(false);
      setNewBuName("");
      setNewBuCode("");
      await fetchTreeData();
    } catch (err: any) {
      alert(err.message || "Erro");
    }
  };

  // Criar Equipe
  const handleCreateTeam = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTeamName || !newTeamBuId) return;
    try {
      const res = await fetch(`/api/v1/hierarchy/teams?account_id=${accountId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: newTeamName,
          business_unit_id: newTeamBuId,
          parent_id: newTeamParentId || null,
        }),
      });
      if (!res.ok) throw new Error("Falha ao criar Equipe");
      setShowTeamModal(false);
      setNewTeamName("");
      await fetchTreeData();
    } catch (err: any) {
      alert(err.message || "Erro");
    }
  };

  // Reparent Equipe
  const handleReparentTeam = async () => {
    if (!reparentTeamId) return;
    try {
      const res = await fetch(`/api/v1/hierarchy/teams/${reparentTeamId}/parent?account_id=${accountId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ parent_id: reparentParentId || null }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Erro no reparenting");
      }
      alert("Equipe re-alocada na hierarquia sem loops de dependência!");
      await fetchTreeData();
    } catch (err: any) {
      alert(err.message || "Erro");
    }
  };

  // Criar Cargo
  const handleCreateRole = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newRoleName) return;
    try {
      const res = await fetch(`/api/v1/hierarchy/roles?account_id=${accountId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: newRoleName,
          description: newRoleDesc,
          default_data_scope: newRoleScope,
          is_admin: 0,
          permissions: [],
        }),
      });
      if (!res.ok) throw new Error("Falha ao criar cargo");
      setShowRoleModal(false);
      setNewRoleName("");
      setNewRoleDesc("");
      await fetchRolesData();
    } catch (err: any) {
      alert(err.message || "Erro");
    }
  };

  // Criar Meta
  const handleCreateTarget = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch(`/api/v1/hierarchy/targets?account_id=${accountId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          period: targetPeriod,
          team_id: targetEntityType === "team" ? targetEntityId : undefined,
          target_amount: Number(targetAmount),
          growth_rate_pct: Number(targetGrowth),
          calculation_basis: "manual",
        }),
      });
      if (!res.ok) throw new Error("Falha ao registrar meta comercial");
      await fetchTargetsData();
    } catch (err: any) {
      alert(err.message || "Erro");
    }
  };

  // Sugestão Algorítmica de Meta
  const handleGetTargetSuggestion = async () => {
    try {
      const res = await fetch(
        `/api/v1/hierarchy/targets/suggestion?entity_type=${targetEntityType}&entity_id=${targetEntityId || "tm-default"}&period=${targetPeriod}&growth_rate_pct=${targetGrowth}&account_id=${accountId}`
      );
      if (res.ok) {
        const data = await res.json();
        setSuggestionResult(data);
      }
    } catch {
      // fallback
    }
  };

  // Criar Regra de Comissão
  const handleCreateCommissionRule = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch(`/api/v1/hierarchy/commissions/rules?account_id=${accountId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          role_id: newCommRoleId,
          base_percentage: Number(newCommBase),
          accelerator_threshold_pct: Number(newCommThreshold),
          accelerator_percentage: Number(newCommAccelerator),
        }),
      });
      if (!res.ok) throw new Error("Falha ao salvar regra de comissão");
      await fetchCommissionsData();
    } catch (err: any) {
      alert(err.message || "Erro");
    }
  };

  // Consultar Extrato de Comissões
  const handleGetStatement = async () => {
    try {
      const res = await fetch(
        `/api/v1/hierarchy/commissions/statement?user_id=${encodeURIComponent(statementUserId)}&period=${statementPeriod}&account_id=${accountId}`
      );
      if (res.ok) {
        const data = await res.json();
        setStatementResult(data);
      }
    } catch (err: any) {
      alert(err.message || "Extrato não encontrado");
    }
  };

  return (
    <div className={`space-y-4 ${className || ""}`}>
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-border pb-3">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-text-main flex items-center gap-2">
              <Shield className="h-5 w-5 text-brand-primary" />
              Equipes, Metas e Comissões
            </h1>
            <Badge variant="outline" className="border-brand-primary/30 text-brand-primary bg-brand-primary-subtle text-xs">
              18 Endpoints Expostos
            </Badge>
          </div>
          <p className="text-xs text-text-secondary mt-0.5">
            Estrutura de equipes e unidades de negócio, metas de vendas e comissionamento.
          </p>
        </div>
      </div>

      {/* Tabs */}
      <Tabs
        activeTab={activeTab}
        onChange={(tabId) => setActiveTab(tabId)}
        tabs={[
          { id: "tree", label: "Estrutura de Equipes e Unidades", count: teams.length },
          { id: "permissions", label: "Cargos & Matriz de Permissões", count: roles.length },
          { id: "targets", label: "Metas Comerciais & Sugestão", count: targets.length },
          { id: "commissions", label: "Comissionamento Bipartido (70/30)", count: commissionRules.length },
        ]}
      />

      {/* ========================================================================= */}
      {/* TAB 1: ESTRUTURA DE EQUIPES E UNIDADES */}
      {/* ========================================================================= */}
      {activeTab === "tree" && (
        <div className="space-y-4">
          {/* Preset e Ações Rápidas */}
          <Card className="p-4 border border-border bg-surface-card space-y-3">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-border pb-2.5">
              <div className="flex items-center gap-2">
                <Sliders className="h-4 w-4 text-brand-primary" />
                <h3 className="text-xs font-bold text-text-main uppercase tracking-wider">
                  Presets Organizacionais Odontológicos Plug & Play
                </h3>
              </div>
              <div className="flex items-center gap-2">
                <Button size="sm" variant="outline" onClick={() => setShowBuModal(true)} className="text-xs">
                  <Plus className="h-3.5 w-3.5 mr-1" />
                  Nova Unidade de Negócio
                </Button>
                <Button size="sm" variant="default" onClick={() => setShowTeamModal(true)} className="text-xs">
                  <Plus className="h-3.5 w-3.5 mr-1" />
                  Nova Equipe
                </Button>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <select
                value={selectedPreset}
                onChange={(e) => setSelectedPreset(e.target.value)}
                className="px-3 py-1.5 rounded-lg border border-border bg-surface-bg text-xs font-mono text-text-main"
              >
                <option value="fabrica_enxuta">Fábrica Enxuta (1 BU, 2 Equipes SP/Interior)</option>
                <option value="nacional_expansao">Expansão Nacional (4 BUs Regionais)</option>
                <option value="multidivisao_produtos">Multi-Divisão (Implantes, Prótese, Biomateriais)</option>
                <option value="multinacional_enterprise">Multinacional Enterprise (Holdings e Exportação)</option>
              </select>
              <Button size="sm" variant="secondary" onClick={handleApplyPreset} className="text-xs">
                Aplicar Preset
              </Button>
            </div>

            {presetFeedback && (
              <p className="text-xs font-mono text-status-success bg-status-success-subtle p-2 rounded border border-status-success/30">
                {presetFeedback}
              </p>
            )}
          </Card>

          {/* Grid de Business Units e Equipes */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Coluna 1: Business Units */}
            <Card className="p-4 border border-border bg-surface-card space-y-3">
              <div className="flex items-center justify-between border-b border-border pb-2">
                <h3 className="text-xs font-bold text-text-main flex items-center gap-1.5">
                  <Building2 className="h-4 w-4 text-brand-primary" />
                  Unidades de Negócio ({businessUnits.length})
                </h3>
              </div>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {businessUnits.map((bu) => (
                  <div key={bu.id} className="p-2.5 rounded-lg border border-border bg-surface-bg text-xs space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-text-main">{bu.name}</span>
                      <span className="font-mono text-[10px] bg-brand-navy-subtle text-brand-navy px-1.5 py-0.5 rounded border border-border">
                        {bu.code}
                      </span>
                    </div>
                    <span className="font-mono text-[10px] text-text-muted">ID: {bu.id}</span>
                  </div>
                ))}
              </div>
            </Card>

            {/* Coluna 2: Equipes Regionais */}
            <Card className="lg:col-span-2 p-4 border border-border bg-surface-card space-y-3">
              <div className="flex items-center justify-between border-b border-border pb-2">
                <h3 className="text-xs font-bold text-text-main flex items-center gap-1.5">
                  <GitFork className="h-4 w-4 text-status-success" />
                  Estrutura de Equipes e Unidades ({teams.length})
                </h3>
                <span className="text-[10px] text-text-muted font-mono">
                  Validação de Hierarquia Ativa
                </span>
              </div>

              {/* Reparenting Toolbar */}
              <div className="p-3 bg-surface-bg border border-border rounded-lg flex flex-wrap items-center gap-2 text-xs">
                <span className="font-semibold text-text-secondary">Mover Equipe:</span>
                <select
                  value={reparentTeamId}
                  onChange={(e) => setReparentTeamId(e.target.value)}
                  className="px-2 py-1 rounded border border-border bg-surface-card font-mono text-xs"
                >
                  {teams.map((t) => (
                    <option key={t.id} value={t.id}>{t.name} ({t.id})</option>
                  ))}
                </select>
                <span className="font-semibold text-text-secondary">Sob a Equipe Pai:</span>
                <select
                  value={reparentParentId}
                  onChange={(e) => setReparentParentId(e.target.value)}
                  className="px-2 py-1 rounded border border-border bg-surface-card font-mono text-xs"
                >
                  <option value="">Raiz (Sem Pai)</option>
                  {teams.filter((t) => t.id !== reparentTeamId).map((t) => (
                    <option key={t.id} value={t.id}>{t.name}</option>
                  ))}
                </select>
                <Button size="sm" variant="secondary" onClick={handleReparentTeam} className="text-xs h-7 py-0">
                  Re-alocar
                </Button>
              </div>

              {/* Lista de Equipes */}
              <div className="space-y-2 max-h-80 overflow-y-auto">
                {teams.map((team) => (
                  <div key={team.id} className="p-2.5 rounded-lg border border-border bg-surface-bg flex items-center justify-between text-xs">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-text-main">{team.name}</span>
                        <span className="font-mono text-[10px] text-brand-primary">
                          {team.id}
                        </span>
                      </div>
                      <div className="text-[11px] text-text-secondary font-mono mt-0.5">
                        Unidade: {team.business_unit_id} {team.parent_id ? `| Pai: ${team.parent_id}` : "| Top Level (Raiz)"}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          {/* Modal Criar Unidade */}
          {showBuModal && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
              <Card className="w-full max-w-sm p-4 bg-surface-card border border-border space-y-3 shadow-xl text-xs">
                <h3 className="font-bold text-text-main text-sm">Nova Unidade de Negócio</h3>
                <form onSubmit={handleCreateBu} className="space-y-2">
                  <Input
                    placeholder="Nome da Unidade (ex: Divisão Implantes)"
                    value={newBuName}
                    onChange={(e) => setNewBuName(e.target.value)}
                    required
                  />
                  <Input
                    placeholder="Código (ex: BU-IMP)"
                    value={newBuCode}
                    onChange={(e) => setNewBuCode(e.target.value)}
                    required
                  />
                  <div className="flex justify-end gap-2 pt-2">
                    <Button type="button" variant="outline" size="sm" onClick={() => setShowBuModal(false)}>Cancelar</Button>
                    <Button type="submit" variant="default" size="sm">Criar Unidade</Button>
                  </div>
                </form>
              </Card>
            </div>
          )}

          {/* Modal Criar Equipe */}
          {showTeamModal && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
              <Card className="w-full max-w-sm p-4 bg-surface-card border border-border space-y-3 shadow-xl text-xs">
                <h3 className="font-bold text-text-main text-sm">Nova Equipe Comercial</h3>
                <form onSubmit={handleCreateTeam} className="space-y-2">
                  <Input
                    placeholder="Nome da Equipe (ex: Field Sales SP Capital)"
                    value={newTeamName}
                    onChange={(e) => setNewTeamName(e.target.value)}
                    required
                  />
                  <div>
                    <label className="text-[11px] text-text-secondary block mb-1">Unidade de Negócio</label>
                    <select
                      value={newTeamBuId}
                      onChange={(e) => setNewTeamBuId(e.target.value)}
                      className="w-full p-1.5 rounded border border-border bg-surface-bg text-xs"
                      required
                    >
                      {businessUnits.map((bu) => (
                        <option key={bu.id} value={bu.id}>{bu.name} ({bu.code})</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="text-[11px] text-text-secondary block mb-1">Equipe Pai (Opcional)</label>
                    <select
                      value={newTeamParentId}
                      onChange={(e) => setNewTeamParentId(e.target.value)}
                      className="w-full p-1.5 rounded border border-border bg-surface-bg text-xs"
                    >
                      <option value="">Nenhuma (Raiz da Unidade)</option>
                      {teams.map((t) => (
                        <option key={t.id} value={t.id}>{t.name}</option>
                      ))}
                    </select>
                  </div>
                  <div className="flex justify-end gap-2 pt-2">
                    <Button type="button" variant="outline" size="sm" onClick={() => setShowTeamModal(false)}>Cancelar</Button>
                    <Button type="submit" variant="default" size="sm">Criar Equipe</Button>
                  </div>
                </form>
              </Card>
            </div>
          )}
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 2: CARGOS & MATRIZ DE PERMISSÕES GRANULARES */}
      {/* ========================================================================= */}
      {activeTab === "permissions" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-text-secondary">
              Perfis de Acesso & Matriz de Escopo de Dados
            </h3>
            <Button size="sm" variant="default" onClick={() => setShowRoleModal(true)} className="text-xs">
              <Plus className="h-3.5 w-3.5 mr-1" />
              Novo Cargo / Perfil
            </Button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
            {/* Lista de Cargos */}
            <Card className="p-3 border border-border bg-surface-card space-y-2">
              <span className="text-xs font-bold text-text-main block mb-1">Cargos ({roles.length})</span>
              <div className="space-y-1 max-h-96 overflow-y-auto">
                {roles.map((r) => {
                  const isSelected = r.id === selectedRoleId;
                  return (
                    <div
                      key={r.id}
                      onClick={() => handleSelectRole(r.id)}
                      className={`p-2 rounded-lg border cursor-pointer text-xs transition ${
                        isSelected
                          ? "bg-brand-primary-subtle border-brand-primary text-brand-primary font-semibold"
                          : "bg-surface-bg border-border text-text-main hover:bg-surface-card"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span>{r.name}</span>
                        <span className="text-[10px] font-mono uppercase text-text-muted">{r.default_data_scope}</span>
                      </div>
                      <span className="text-[10px] font-mono text-text-secondary block mt-0.5">
                        {r.permissions?.length || 0} permissões
                      </span>
                    </div>
                  );
                })}
              </div>
            </Card>

            {/* Matriz de Permissões do Cargo Selecionado */}
            <Card className="lg:col-span-3 p-4 border border-border bg-surface-card space-y-4">
              <div className="flex items-center justify-between border-b border-border pb-3">
                <div>
                  <h4 className="text-sm font-bold text-text-main">
                    Permissões: {roles.find((r) => r.id === selectedRoleId)?.name || "Selecione um Cargo"}
                  </h4>
                  <p className="text-xs text-text-secondary">
                    Escopo padrão: <code>{roles.find((r) => r.id === selectedRoleId)?.default_data_scope}</code>
                  </p>
                </div>
                <Button
                  size="sm"
                  variant="default"
                  onClick={handleSavePermissions}
                  disabled={savingPermissions || !selectedRoleId}
                  className="text-xs"
                >
                  {savingPermissions ? "Salvando..." : "Salvar Matriz"}
                </Button>
              </div>

              {/* Catálogo de Recursos e Ações */}
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {catalog.map((cat) => (
                  <div key={cat.resource} className="p-3 rounded-lg border border-border bg-surface-bg text-xs space-y-2">
                    <div className="font-bold text-text-main flex items-center justify-between">
                      <span>{cat.resource_label} ({cat.resource})</span>
                    </div>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                      {cat.actions.map((act) => {
                        const checked = rolePermissions.includes(act.code);
                        return (
                          <label
                            key={act.code}
                            className={`flex items-center gap-2 p-1.5 rounded border text-[11px] cursor-pointer transition ${
                              checked
                                ? "bg-status-success-subtle/50 border-status-success/30 text-text-main font-semibold"
                                : "bg-surface-card border-border text-text-secondary"
                            }`}
                          >
                            <input
                              type="checkbox"
                              checked={checked}
                              onChange={() => togglePermission(act.code)}
                              className="rounded border-border text-brand-primary"
                            />
                            <span>{act.label}</span>
                          </label>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          {/* Modal Criar Cargo */}
          {showRoleModal && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
              <Card className="w-full max-w-sm p-4 bg-surface-card border border-border space-y-3 shadow-xl text-xs">
                <h3 className="font-bold text-text-main text-sm">Novo Cargo / Perfil RBAC</h3>
                <form onSubmit={handleCreateRole} className="space-y-2">
                  <Input
                    placeholder="Nome do Cargo (ex: Inside Sales Specialist)"
                    value={newRoleName}
                    onChange={(e) => setNewRoleName(e.target.value)}
                    required
                  />
                  <Input
                    placeholder="Descrição do Perfil"
                    value={newRoleDesc}
                    onChange={(e) => setNewRoleDesc(e.target.value)}
                  />
                  <div>
                    <label className="text-[11px] text-text-secondary block mb-1">Escopo de Dados Inicial</label>
                    <select
                      value={newRoleScope}
                      onChange={(e) => setNewRoleScope(e.target.value)}
                      className="w-full p-1.5 rounded border border-border bg-surface-bg text-xs"
                    >
                      <option value="self">Individual (Apenas registros atribuídos)</option>
                      <option value="team">Equipe (Registros da regional)</option>
                      <option value="subtree">Sub-árvore (Time e equipes subordinadas)</option>
                      <option value="business_unit">Unidade de Negócio</option>
                      <option value="tenant_global">Global (Toda a empresa)</option>
                    </select>
                  </div>
                  <div className="flex justify-end gap-2 pt-2">
                    <Button type="button" variant="outline" size="sm" onClick={() => setShowRoleModal(false)}>Cancelar</Button>
                    <Button type="submit" variant="default" size="sm">Criar Cargo</Button>
                  </div>
                </form>
              </Card>
            </div>
          )}
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 3: METAS COMERCIAIS & SUGESTÃO PREDITIVA */}
      {/* ========================================================================= */}
      {activeTab === "targets" && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Cadastro e Sugestão Preditiva */}
            <Card className="p-4 border border-border bg-surface-card space-y-3">
              <div className="flex items-center justify-between border-b border-border pb-2">
                <h3 className="text-xs font-bold text-text-main flex items-center gap-1.5">
                  <Target className="h-4 w-4 text-brand-primary" />
                  Atribuir Meta Comercial
                </h3>
              </div>

              <form onSubmit={handleCreateTarget} className="space-y-2.5 text-xs">
                <div>
                  <label className="text-[11px] font-semibold text-text-secondary block mb-1">Período</label>
                  <Input
                    value={targetPeriod}
                    onChange={(e) => setTargetPeriod(e.target.value)}
                    placeholder="2026-Q4"
                    required
                  />
                </div>

                <div>
                  <label className="text-[11px] font-semibold text-text-secondary block mb-1">Tipo de Entidade</label>
                  <select
                    value={targetEntityType}
                    onChange={(e) => setTargetEntityType(e.target.value)}
                    className="w-full p-1.5 rounded border border-border bg-surface-bg text-xs"
                  >
                    <option value="team">Equipe Regional</option>
                    <option value="user">Consultor Individual</option>
                    <option value="bu">Unidade de Negócio</option>
                  </select>
                </div>

                <div>
                  <label className="text-[11px] font-semibold text-text-secondary block mb-1">ID da Entidade</label>
                  <Input
                    value={targetEntityId}
                    onChange={(e) => setTargetEntityId(e.target.value)}
                    placeholder="ex: tm_reg_capital"
                    required
                  />
                </div>

                <div>
                  <label className="text-[11px] font-semibold text-text-secondary block mb-1">Meta em R$</label>
                  <Input
                    type="number"
                    value={targetAmount}
                    onChange={(e) => setTargetAmount(Number(e.target.value))}
                    required
                  />
                </div>

                <div>
                  <label className="text-[11px] font-semibold text-text-secondary block mb-1">Taxa de Crescimento (%)</label>
                  <Input
                    type="number"
                    value={targetGrowth}
                    onChange={(e) => setTargetGrowth(Number(e.target.value))}
                    required
                  />
                </div>

                <div className="flex gap-2 pt-2">
                  <Button type="button" variant="outline" size="sm" onClick={handleGetTargetSuggestion} className="flex-1 text-xs">
                    <Sparkles className="h-3 w-3 mr-1" />
                    Sugerir Meta
                  </Button>
                  <Button type="submit" variant="default" size="sm" className="flex-1 text-xs">
                    Salvar Meta
                  </Button>
                </div>
              </form>

              {suggestionResult && (
                <div className="p-3 bg-brand-primary-subtle border border-brand-primary/30 rounded-lg text-xs space-y-1">
                  <div className="font-bold text-brand-primary">Sugestão Algorítmica:</div>
                  <div className="font-mono text-text-main text-[11px]">
                    Sugerido: R$ {suggestionResult.suggested_target?.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                  </div>
                  <div className="text-[10px] text-text-secondary">{suggestionResult.explanation}</div>
                </div>
              )}
            </Card>

            {/* Lista de Metas Registradas */}
            <Card className="lg:col-span-2 p-4 border border-border bg-surface-card space-y-3">
              <div className="flex items-center justify-between border-b border-border pb-2">
                <h3 className="text-xs font-bold text-text-main flex items-center gap-1.5">
                  <TrendingUp className="h-4 w-4 text-status-success" />
                  Metas Comerciais em Tempo Real ({targets.length})
                </h3>
              </div>

              <div className="space-y-2 max-h-96 overflow-y-auto">
                {targets.map((tgt) => (
                  <div key={tgt.id} className="p-3 rounded-lg border border-border bg-surface-bg text-xs space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-text-main">{tgt.entity_name || tgt.id}</span>
                      <span className="font-mono text-[10px] text-brand-primary font-bold">{tgt.period}</span>
                    </div>
                    <div className="grid grid-cols-3 gap-2 font-mono text-[11px]">
                      <div>
                        <span className="text-[10px] text-text-secondary block">Meta Prevista</span>
                        <span>R$ {tgt.target_amount?.toLocaleString("pt-BR")}</span>
                      </div>
                      <div>
                        <span className="text-[10px] text-text-secondary block">Atingido</span>
                        <span className="text-status-success">R$ {tgt.achieved_amount?.toLocaleString("pt-BR")}</span>
                      </div>
                      <div>
                        <span className="text-[10px] text-text-secondary block">% Atingimento</span>
                        <span className="font-bold">{tgt.achievement_rate_pct?.toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 4: COMISSIONAMENTO BIPARTIDO (70% FIELD / 30% INSIDE) */}
      {/* ========================================================================= */}
      {activeTab === "commissions" && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Cadastro de Regra de Comissionamento */}
            <Card className="p-4 border border-border bg-surface-card space-y-3">
              <div className="flex items-center justify-between border-b border-border pb-2">
                <h3 className="text-xs font-bold text-text-main flex items-center gap-1.5">
                  <Percent className="h-4 w-4 text-brand-primary" />
                  Nova Regra de Comissionamento
                </h3>
              </div>

              <form onSubmit={handleCreateCommissionRule} className="space-y-2.5 text-xs">
                <div>
                  <label className="text-[11px] font-semibold text-text-secondary block mb-1">Cargo Beneficiário</label>
                  <select
                    value={newCommRoleId}
                    onChange={(e) => setNewCommRoleId(e.target.value)}
                    className="w-full p-1.5 rounded border border-border bg-surface-bg text-xs"
                    required
                  >
                    {roles.map((r) => (
                      <option key={r.id} value={r.id}>{r.name}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="text-[11px] font-semibold text-text-secondary block mb-1">Comissão Base (%)</label>
                  <Input
                    type="number"
                    step="0.1"
                    value={newCommBase}
                    onChange={(e) => setNewCommBase(Number(e.target.value))}
                    required
                  />
                </div>

                <div>
                  <label className="text-[11px] font-semibold text-text-secondary block mb-1">Gatilho do Acelerador (% Meta)</label>
                  <Input
                    type="number"
                    value={newCommThreshold}
                    onChange={(e) => setNewCommThreshold(Number(e.target.value))}
                    required
                  />
                </div>

                <div>
                  <label className="text-[11px] font-semibold text-text-secondary block mb-1">Comissão Acelerada (%)</label>
                  <Input
                    type="number"
                    step="0.1"
                    value={newCommAccelerator}
                    onChange={(e) => setNewCommAccelerator(Number(e.target.value))}
                    required
                  />
                </div>

                <Button type="submit" variant="default" size="sm" className="w-full text-xs mt-2">
                  Salvar Regra de Comissão
                </Button>
              </form>
            </Card>

            {/* Extrato Auditável e Regras */}
            <Card className="lg:col-span-2 p-4 border border-border bg-surface-card space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-border pb-3">
                <h3 className="text-xs font-bold text-text-main flex items-center gap-1.5">
                  <DollarSign className="h-4 w-4 text-status-success" />
                  Extrato Auditável de Comissões
                </h3>
                <div className="flex items-center gap-2">
                  <Input
                    placeholder="User ID (ex: u_cons_sp_01)"
                    value={statementUserId}
                    onChange={(e) => setStatementUserId(e.target.value)}
                    className="h-7 text-xs font-mono w-36"
                  />
                  <Input
                    placeholder="Período"
                    value={statementPeriod}
                    onChange={(e) => setStatementPeriod(e.target.value)}
                    className="h-7 text-xs font-mono w-24"
                  />
                  <Button size="sm" variant="secondary" onClick={handleGetStatement} className="text-xs h-7 py-0">
                    Consultar
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    className="text-xs h-7 py-0 gap-1"
                    onClick={() => {
                      const rows = [
                        "user_id,user_name,period,total_commission_payout",
                        `${statementResult?.user_id || statementUserId},${statementResult?.user_name || "-"},${statementResult?.period || statementPeriod},${statementResult?.total_commission_payout || 0}`,
                      ].join("\n");
                      const blob = new Blob([rows], { type: "text/csv;charset=utf-8;" });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement("a");
                      a.href = url;
                      a.download = "folha_comissoes_erp.csv";
                      a.click();
                      URL.revokeObjectURL(url);
                    }}
                  >
                    <Download className="h-3 w-3" />
                    Exportar Folha ERP
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    className="text-xs h-7 py-0 gap-1"
                    onClick={() => {
                      setUserBlockToggle(!userBlockToggle);
                    }}
                  >
                    <Lock className="h-3 w-3" />
                    {userBlockToggle ? "Desbloquear Usuario" : "Bloqueio Temporario"}
                  </Button>
                </div>
              </div>

              {/* Statement Result */}
              {statementResult && (
                <div className="p-3 bg-surface-bg rounded-lg border border-border space-y-2 text-xs">
                  <div className="flex justify-between items-center font-bold text-text-main">
                    <span>{statementResult.user_name} ({statementResult.user_id})</span>
                    <span className="font-mono text-status-success text-sm">
                      Total: R$ {statementResult.total_commission_payout?.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                  <div className="text-[10px] text-text-secondary font-mono">
                    Período: {statementResult.period} | Atingimento: {statementResult.target_achievement_pct?.toFixed(1)}% | Acelerador Ativo: {statementResult.is_accelerator_active ? "SIM" : "NÃO"}
                  </div>
                </div>
              )}

              {/* Regras Ativas */}
              <div>
                <span className="text-[11px] font-bold text-text-secondary block mb-2 uppercase">
                  Regras de Comissionamento Cadastradas ({commissionRules.length})
                </span>
                <div className="space-y-1.5 max-h-56 overflow-y-auto">
                  {commissionRules.map((cr) => (
                    <div key={cr.id} className="p-2 rounded border border-border bg-surface-bg flex items-center justify-between text-xs">
                      <div>
                        <span className="font-bold text-text-main">{cr.role_name || cr.role_id}</span>
                        <span className="font-mono text-[10px] text-text-muted ml-2">Base: {cr.base_percentage}%</span>
                      </div>
                      <div className="font-mono text-[11px] text-brand-primary">
                        Acelerador &ge; {cr.accelerator_threshold_pct}%: <strong>{cr.accelerator_percentage}%</strong>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}

export default RbacHierarchyTree;
