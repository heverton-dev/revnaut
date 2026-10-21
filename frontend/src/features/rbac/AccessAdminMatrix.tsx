import * as React from "react";
import {
  ShieldCheck,
  Save,
  Loader2,
  Lock,
  ChevronDown,
  ChevronRight,
  Plus,
  UserPlus,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Input } from "@/components/ui/Input";
import { cn } from "@/lib/utils";
import { dispatchToast } from "@/lib/api";

interface Fac {
  facility_id: string;
  label: string;
  sort_order: number;
}

interface CatalogRoute {
  route_id: string;
  label: string;
  journey_group: string;
  default_facility: string | null;
  facilities: Fac[];
}

interface RoleGrants {
  role_id: string;
  role_name: string;
  is_admin: boolean;
  editable: boolean;
  landing_route: string | null;
  landing_facility: string | null;
  allow_submenus: boolean;
  grants: Array<{
    route_id: string;
    label: string;
    journey_group: string;
    menu_priority: number;
    allow_submenus: boolean;
    facilities: Fac[];
  }>;
}

interface Matrix {
  source: string;
  catalog: CatalogRoute[];
  roles: RoleGrants[];
  editable_role_ids: string[];
  viewer_role_id: string | null;
  viewer_is_superadmin: boolean;
}

type Draft = {
  route_id: string;
  allow_submenus: boolean;
  facilities: string[];
};

/** Tela Admin de Acesso — matriz cargo × rota × facility (fase 4). */
export function AccessAdminMatrix() {
  const [matrix, setMatrix] = React.useState<Matrix | null>(null);
  const [selectedRoleId, setSelectedRoleId] = React.useState<string | null>(null);
  const [draft, setDraft] = React.useState<Draft[]>([]);
  const [dirty, setDirty] = React.useState(false);
  const [saving, setSaving] = React.useState(false);
  const [loading, setLoading] = React.useState(true);
  const [expanded, setExpanded] = React.useState<Record<string, boolean>>({});
  const [showCreate, setShowCreate] = React.useState(false);
  const [newRoleName, setNewRoleName] = React.useState("");
  const [newRoleDesc, setNewRoleDesc] = React.useState("");
  const [creating, setCreating] = React.useState(false);
  const [roleUsers, setRoleUsers] = React.useState<
    Array<{
      user_id: string;
      name: string;
      email: string;
      role_label: string;
      is_superadmin: boolean;
    }>
  >([]);
  const [allUsers, setAllUsers] = React.useState<
    Array<{ id: string; name: string; email: string; role: string; role_id?: string | null }>
  >([]);
  const [assignUserId, setAssignUserId] = React.useState("");
  const [assigning, setAssigning] = React.useState(false);
  const [showAssign, setShowAssign] = React.useState(false);

  const load = React.useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/v1/access/matrix", {
        headers: { Accept: "application/json" },
      });
      if (!res.ok) throw new Error(String(res.status));
      const data = (await res.json()) as Matrix;
      setMatrix(data);
      const firstEditable =
        data.roles.find((r) => r.editable)?.role_id ?? data.roles[0]?.role_id ?? null;
      setSelectedRoleId((prev) => prev ?? firstEditable);
    } catch {
      dispatchToast({
        type: "error",
        title: "Falha ao carregar matriz",
        message: "Sem permissão ou API indisponível.",
      });
      setMatrix(null);
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    void load();
  }, [load]);

  const selectedRole = matrix?.roles.find((r) => r.role_id === selectedRoleId) || null;

  // Sincroniza rascunho ao trocar de cargo
  React.useEffect(() => {
    if (!selectedRole) {
      setDraft([]);
      setDirty(false);
      setRoleUsers([]);
      return;
    }
    setDraft(
      selectedRole.grants.map((g) => ({
        route_id: g.route_id,
        allow_submenus: g.allow_submenus,
        facilities: g.facilities.map((f) => f.facility_id),
      }))
    );
    setDirty(false);
    const next: Record<string, boolean> = {};
    selectedRole.grants.forEach((g) => {
      if (g.allow_submenus) next[g.route_id] = true;
    });
    setExpanded(next);
    setAssignUserId("");
    setShowAssign(false);

    let alive = true;
    if (selectedRole.editable) {
      void (async () => {
        try {
          const [usersRes, allRes] = await Promise.all([
            fetch(`/api/v1/access/roles/${encodeURIComponent(selectedRole.role_id)}/users`),
            fetch("/api/v1/auth/users"),
          ]);
          if (!alive) return;
          if (usersRes.ok) setRoleUsers(await usersRes.json());
          if (allRes.ok) {
            const list = await allRes.json();
            if (Array.isArray(list)) setAllUsers(list);
          }
        } catch {
          /* silencioso — painel de membros opcional */
        }
      })();
    } else {
      setRoleUsers([]);
    }
    return () => {
      alive = false;
    };
  }, [selectedRole?.role_id, selectedRole?.editable]); // eslint-disable-line react-hooks/exhaustive-deps

  const toggleRoute = (routeId: string, enabled: boolean) => {
    if (!matrix) return;
    setDirty(true);
    setDraft((prev) => {
      if (!enabled) return prev.filter((d) => d.route_id !== routeId);
      if (prev.some((d) => d.route_id === routeId)) return prev;
      const cat = matrix.catalog.find((c) => c.route_id === routeId);
      const hasFac = (cat?.facilities.length ?? 0) > 0;
      return [
        ...prev,
        {
          route_id: routeId,
          allow_submenus: hasFac,
          facilities: hasFac ? cat!.facilities.map((f) => f.facility_id) : [],
        },
      ];
    });
  };

  const toggleSub = (routeId: string, on: boolean) => {
    if (!matrix) return;
    setDirty(true);
    setExpanded((e) => ({ ...e, [routeId]: on }));
    setDraft((prev) =>
      prev.map((d) => {
        if (d.route_id !== routeId) return d;
        const cat = matrix.catalog.find((c) => c.route_id === routeId);
        const all = (cat?.facilities || []).map((f) => f.facility_id);
        if (!on) {
          const def = cat?.default_facility;
          return { ...d, allow_submenus: false, facilities: def ? [def] : [] };
        }
        return { ...d, allow_submenus: true, facilities: all };
      })
    );
  };

  const toggleFac = (routeId: string, facId: string, on: boolean) => {
    setDirty(true);
    setDraft((prev) =>
      prev.map((d) => {
        if (d.route_id !== routeId) return d;
        const set = new Set(d.facilities);
        if (on) set.add(facId);
        else set.delete(facId);
        return { ...d, facilities: Array.from(set) };
      })
    );
  };

  const canCreateRole =
    matrix?.viewer_is_superadmin ||
    matrix?.viewer_role_id === "role-access-admin";

  const createRole = async () => {
    const name = newRoleName.trim();
    if (name.length < 2) {
      dispatchToast({
        type: "warning",
        title: "Nome curto",
        message: "Informe um nome de cargo com ao menos 2 caracteres.",
      });
      return;
    }
    setCreating(true);
    try {
      const res = await fetch("/api/v1/access/roles", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          description: newRoleDesc.trim() || null,
          default_data_scope: "team",
          routes: [],
        }),
      });
      const body = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(body.detail || String(res.status));
      }
      dispatchToast({
        type: "success",
        title: "Cargo criado",
        message: `${name} · marque as rotas e clique em Salvar.`,
      });
      setNewRoleName("");
      setNewRoleDesc("");
      setShowCreate(false);
      await load();
      if (body.role_id) setSelectedRoleId(body.role_id);
    } catch (err: unknown) {
      dispatchToast({
        type: "error",
        title: "Erro ao criar cargo",
        message: err instanceof Error ? err.message : "Falha inesperada.",
      });
    } finally {
      setCreating(false);
    }
  };

  const unassignUser = async (userId: string, userName: string) => {
    if (!selectedRoleId) return;
    setAssigning(true);
    try {
      const res = await fetch(
        `/api/v1/access/roles/${encodeURIComponent(selectedRoleId)}/users/${encodeURIComponent(userId)}`,
        { method: "DELETE" }
      );
      const body = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(body.detail || String(res.status));
      dispatchToast({
        type: "success",
        title: "Usuário desvinculado",
        message: `${userName} ficou “Sem cargo” (menu mínimo até novo vínculo).`,
      });
      const usersRes = await fetch(
        `/api/v1/access/roles/${encodeURIComponent(selectedRoleId)}/users`
      );
      if (usersRes.ok) setRoleUsers(await usersRes.json());
      const allRes = await fetch("/api/v1/auth/users");
      if (allRes.ok) {
        const list = await allRes.json();
        if (Array.isArray(list)) setAllUsers(list);
      }
    } catch (err: unknown) {
      dispatchToast({
        type: "error",
        title: "Erro ao desvincular",
        message: err instanceof Error ? err.message : "Falha inesperada.",
      });
    } finally {
      setAssigning(false);
    }
  };

  const assignUser = async () => {
    if (!selectedRoleId || !assignUserId) return;
    setAssigning(true);
    try {
      const res = await fetch(
        `/api/v1/access/roles/${encodeURIComponent(selectedRoleId)}/users/${encodeURIComponent(assignUserId)}`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: assignUserId, sync_role_label: true }),
        }
      );
      const body = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(body.detail || String(res.status));
      dispatchToast({
        type: "success",
        title: "Usuário atribuído",
        message: `${body.role_name} · ${body.user_id}`,
      });
      setAssignUserId("");
      setShowAssign(false);
      // recarrega membros
      const usersRes = await fetch(
        `/api/v1/access/roles/${encodeURIComponent(selectedRoleId)}/users`
      );
      if (usersRes.ok) setRoleUsers(await usersRes.json());
      // lista global pode ter role atualizado
      const allRes = await fetch("/api/v1/auth/users");
      if (allRes.ok) {
        const list = await allRes.json();
        if (Array.isArray(list)) setAllUsers(list);
      }
    } catch (err: unknown) {
      dispatchToast({
        type: "error",
        title: "Erro ao atribuir",
        message: err instanceof Error ? err.message : "Falha inesperada.",
      });
    } finally {
      setAssigning(false);
    }
  };

  const save = async () => {
    if (!selectedRoleId || !selectedRole?.editable) return;
    // Respeita ordem do catálogo
    const ordered = (matrix?.catalog || [])
      .map((c) => draft.find((d) => d.route_id === c.route_id))
      .filter(Boolean)
      .map((d, i) => ({
        route_id: d!.route_id,
        menu_priority: i + 1,
        allow_submenus: d!.allow_submenus,
        facilities: d!.facilities,
      }));

    setSaving(true);
    try {
      const res = await fetch(
        `/api/v1/access/roles/${encodeURIComponent(selectedRoleId)}/grants`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ routes: ordered }),
        }
      );
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || String(res.status));
      }
      dispatchToast({
        type: "success",
        title: "Permissões salvas",
        message: `${ordered.length} rota(s) atualizada(s) em ${selectedRole.role_name}.`,
      });
      await load();
    } catch (err: unknown) {
      dispatchToast({
        type: "error",
        title: "Erro ao salvar",
        message: err instanceof Error ? err.message : "Falha inesperada.",
      });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-xs text-text-secondary p-4">
        <Loader2 className="h-4 w-4 animate-spin" />
        Carregando matriz de permissões…
      </div>
    );
  }

  if (!matrix || matrix.roles.length === 0) {
    return (
      <div className="p-4 text-xs text-text-muted border border-border rounded-lg bg-surface-card">
        Matriz indisponível — sem acesso ou API offline.
      </div>
    );
  }

  const viewerCanManage =
    matrix.viewer_is_superadmin ||
    matrix.roles.some((r) => r.editable) ||
    (matrix.editable_role_ids?.length ?? 0) > 0;

  const groups: { title: string; routes: CatalogRoute[] }[] = [];
  for (const r of matrix.catalog) {
    let g = groups.find((x) => x.title === r.journey_group);
    if (!g) {
      g = { title: r.journey_group, routes: [] };
      groups.push(g);
    }
    g.routes.push(r);
  }

  return (
    <div className="space-y-3 border border-border rounded-xl bg-surface-card p-4">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border pb-2">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-4 w-4 text-brand-primary" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-text-main">
            Matriz Granular · Rotas e Subrotas
          </h3>
          <Badge variant="outline">banco · {matrix.source}</Badge>
        </div>
        <div className="flex items-center gap-2">
          {!viewerCanManage && (
            <span className="text-[11px] text-text-muted flex items-center gap-1">
              <Lock className="h-3.5 w-3.5" /> somente leitura
            </span>
          )}
          {canCreateRole && (
            <Button
              size="sm"
              variant="outline"
              className="text-xs"
              onClick={() => setShowCreate((v) => !v)}
            >
              <UserPlus className="h-3.5 w-3.5 mr-1" />
              Novo cargo
            </Button>
          )}
        </div>
      </div>

      {canCreateRole && showCreate && (
        <div className="border border-border rounded-lg bg-surface-bg p-3 space-y-2">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <div className="space-y-1">
              <label className="text-[10px] uppercase text-text-muted" htmlFor="new-role-name">
                Nome do cargo *
              </label>
              <Input
                id="new-role-name"
                value={newRoleName}
                onChange={(e) => setNewRoleName(e.target.value)}
                placeholder="Ex.: Especialista de Implantes"
                className="h-8 text-xs"
                maxLength={120}
              />
            </div>
            <div className="space-y-1">
              <label className="text-[10px] uppercase text-text-muted" htmlFor="new-role-desc">
                Descrição
              </label>
              <Input
                id="new-role-desc"
                value={newRoleDesc}
                onChange={(e) => setNewRoleDesc(e.target.value)}
                placeholder="Escopo de atuação"
                className="h-8 text-xs"
                maxLength={240}
              />
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <Button
              size="sm"
              variant="ghost"
              className="text-xs"
              onClick={() => setShowCreate(false)}
            >
              Cancelar
            </Button>
            <Button
              size="sm"
              variant="default"
              className="text-xs"
              disabled={creating || newRoleName.trim().length < 2}
              onClick={() => void createRole()}
            >
              {creating ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin mr-1" />
              ) : (
                <Plus className="h-3.5 w-3.5 mr-1" />
              )}
              Criar e marcar rotas
            </Button>
          </div>
          <p className="text-[10px] text-text-muted">
            O cargo nasce sem rotas: selecione na matriz e salve no banco.
            Admin de Acesso só cria cargos operacionais.
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Cargos */}
        <div className="space-y-1.5 max-h-96 overflow-y-auto">
          <span className="text-[10px] uppercase text-text-muted font-semibold">Cargos</span>
          {matrix.roles.map((role) => (
            <button
              key={role.role_id}
              type="button"
              onClick={() => setSelectedRoleId(role.role_id)}
              className={cn(
                "w-full text-left px-2.5 py-2 rounded-lg border text-xs transition",
                selectedRoleId === role.role_id
                  ? "bg-brand-primary-subtle border-brand-primary text-brand-primary font-semibold"
                  : "bg-surface-bg border-border text-text-main hover:border-border"
              )}
            >
              <div className="flex items-center justify-between gap-2">
                <span className="truncate">{role.role_name}</span>
                {role.is_admin && (
                  <span className="text-[9px] uppercase text-text-muted">admin</span>
                )}
              </div>
              <span className="text-[10px] text-text-muted font-mono">
                {role.role_id} · {role.grants.length} rotas
                {role.editable ? "" : " · trancado"}
              </span>
            </button>
          ))}
        </div>

        {/* Checkbox por rota/facility */}
        <div className="lg:col-span-3 space-y-3 max-h-[28rem] overflow-y-auto pr-1">
          {!selectedRole ? (
            <p className="text-xs text-text-muted">Selecione um cargo.</p>
          ) : !selectedRole.editable ? (
            <div className="text-xs text-text-secondary bg-surface-bg border border-border rounded-lg p-4 flex gap-2">
              <Lock className="h-4 w-4 shrink-0 mt-0.5" />
              <div>
                <strong>{selectedRole.role_name}</strong> é protegido. Apenas Super Admin
                pode alterar cargos de governança (diretoria / admin de acesso).
              </div>
            </div>
          ) : (
            groups.map((g) => (
              <div key={g.title} className="space-y-1">
                <div className="text-[10px] uppercase font-semibold text-text-muted">
                  {g.title}
                </div>
                {g.routes.map((cat) => {
                  const d = draft.find((x) => x.route_id === cat.route_id);
                  const on = Boolean(d);
                  const isOpen = on && expanded[cat.route_id];
                  return (
                    <div
                      key={cat.route_id}
                      className="border border-border rounded-lg bg-surface-bg p-2.5"
                    >
                      <label className="flex items-center justify-between gap-3 cursor-pointer">
                        <span className="flex items-center gap-2 text-xs font-medium text-text-main">
                          <input
                            type="checkbox"
                            checked={on}
                            onChange={(e) => toggleRoute(cat.route_id, e.target.checked)}
                            className="rounded border-border"
                          />
                          {cat.label}
                          <span className="font-mono text-[10px] text-text-muted">
                            /{cat.route_id}
                          </span>
                        </span>
                        {on && cat.facilities.length > 0 && (
                          <button
                            type="button"
                            onClick={() => toggleSub(cat.route_id, !isOpen)}
                            className="text-[10px] text-text-secondary hover:text-brand-primary flex items-center gap-1"
                          >
                            {isOpen ? (
                              <ChevronDown className="h-3 w-3" />
                            ) : (
                              <ChevronRight className="h-3 w-3" />
                            )}
                            {d?.allow_submenus ? "Subrotas on" : "Subrotas"}
                          </button>
                        )}
                      </label>

                      {isOpen && (
                        <div className="mt-2 ml-6 space-y-1 border-l border-border pl-3">
                          <label className="flex items-center gap-2 text-[11px] text-text-secondary cursor-pointer">
                            <input
                              type="checkbox"
                              checked={Boolean(d?.allow_submenus)}
                              onChange={(e) =>
                                toggleSub(cat.route_id, e.target.checked)
                              }
                            />
                            Permitir menu aninhado (submenu)
                          </label>
                          {cat.facilities.map((f) => (
                            <label
                              key={f.facility_id}
                              className="flex items-center gap-2 text-[11px] text-text-main cursor-pointer"
                            >
                              <input
                                type="checkbox"
                                checked={d?.facilities.includes(f.facility_id) ?? false}
                                onChange={(e) =>
                                  toggleFac(cat.route_id, f.facility_id, e.target.checked)
                                }
                              />
                              {f.label}
                              <span className="font-mono text-[10px] text-text-muted">
                                ?f={f.facility_id}
                              </span>
                            </label>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            ))
          )}

          {selectedRole?.editable && (
            <div className="border border-border rounded-lg bg-surface-bg p-3 space-y-2">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span className="text-[10px] uppercase font-semibold text-text-muted">
                  Usuários neste cargo ({roleUsers.length})
                </span>
                <Button
                  size="sm"
                  variant="outline"
                  className="text-xs h-7"
                  onClick={() => setShowAssign((v) => !v)}
                >
                  <UserPlus className="h-3.5 w-3.5 mr-1" />
                  Atribuir usuário
                </Button>
              </div>

              {roleUsers.length === 0 ? (
                <p className="text-[11px] text-text-muted">
                  Nenhum usuário ainda com este cargo.
                </p>
              ) : (
                <ul className="space-y-1">
                  {roleUsers.map((u) => (
                    <li
                      key={u.user_id}
                      className="flex flex-wrap items-center justify-between gap-2 text-[11px] px-2 py-1.5 rounded border border-border bg-surface-card"
                    >
                      <div className="min-w-0">
                        <span className="font-medium text-text-main">{u.name}</span>
                        <span className="text-text-muted font-mono ml-2">{u.email}</span>
                      </div>
                      <button
                        type="button"
                        disabled={assigning}
                        title="Desvincular do cargo"
                        aria-label={`Desvincular ${u.name} do cargo`}
                        onClick={() => void unassignUser(u.user_id, u.name)}
                        className="shrink-0 px-2 py-0.5 rounded border border-border text-[10px] text-text-secondary hover:text-status-danger hover:border-status-danger/40 transition"
                      >
                        Desvincular
                      </button>
                    </li>
                  ))}
                </ul>
              )}

              {showAssign && (
                <div className="flex flex-wrap items-end gap-2 pt-1 border-t border-border">
                  <div className="flex-1 min-w-[12rem] space-y-1">
                    <label
                      className="block text-[10px] uppercase text-text-muted"
                      htmlFor="assign-user"
                    >
                      Usuário existente
                    </label>
                    <select
                      id="assign-user"
                      value={assignUserId}
                      onChange={(e) => setAssignUserId(e.target.value)}
                      className="w-full rounded border border-border bg-surface-card px-2 py-1.5 text-xs text-text-main"
                    >
                      <option value="">Selecione…</option>
                      {allUsers
                        .filter((u) => u.id && u.role_id !== selectedRoleId)
                        .map((u) => (
                          <option key={u.id} value={u.id}>
                            {u.name} — {u.role}
                          </option>
                        ))}
                    </select>
                  </div>
                  <Button
                    size="sm"
                    variant="default"
                    className="text-xs h-8"
                    disabled={!assignUserId || assigning}
                    onClick={() => void assignUser()}
                  >
                    {assigning ? (
                      <Loader2 className="h-3.5 w-3.5 animate-spin mr-1" />
                    ) : (
                      <Plus className="h-3.5 w-3.5 mr-1" />
                    )}
                    Atribuir cargo
                  </Button>
                </div>
              )}
              <p className="text-[10px] text-text-muted">
                Atualiza users.role_id e o rótulo. Registrado em access_audit_log.
              </p>
            </div>
          )}

          {selectedRole?.editable && (
            <div className="flex items-center justify-between gap-3 pt-2 border-t border-border">
              <span className="text-[11px] text-text-muted">
                {draft.length} rota(s) no rascunho
                {dirty ? " · alterado" : ""}
              </span>
              <Button
                size="sm"
                variant="default"
                disabled={!dirty || saving}
                onClick={() => void save()}
                className="text-xs"
              >
                {saving ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin mr-1" />
                ) : (
                  <Save className="h-3.5 w-3.5 mr-1" />
                )}
                Salvar no banco
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
