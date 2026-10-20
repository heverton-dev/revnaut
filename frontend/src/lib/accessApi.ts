import type { RoleWorkspaceConfig } from "@/components/layout/navConfig";

/** GET /api/v1/access/me — grants de navegação vindos do banco. */
export interface AccessFacility {
  facility_id: string;
  label: string;
  sort_order: number;
}

export interface AccessRoute {
  route_id: string;
  label: string;
  journey_group: string;
  menu_priority: number;
  allow_submenus: boolean;
  facilities: AccessFacility[];
}

export interface AccessMeResponse {
  user_id: string;
  account_id: string;
  role_id: string | null;
  role_name: string;
  display_name: string;
  is_superadmin: boolean;
  can_manage_access: boolean;
  landing_route: string;
  landing_facility: string | null;
  allow_submenus: boolean;
  source: string;
  routes: AccessRoute[];
}

export async function fetchAccessMe(): Promise<AccessMeResponse | null> {
  try {
    const res = await fetch("/api/v1/access/me", {
      headers: { Accept: "application/json" },
    });
    if (!res.ok) return null;
    const data = (await res.json()) as AccessMeResponse;
    if (!data || !Array.isArray(data.routes) || data.routes.length === 0) {
      return data ?? null;
    }
    return data;
  } catch {
    return null;
  }
}

/** Converte payload do banco para o shape que o AppShell já entende. */
export function accessMeToRoleConfig(access: AccessMeResponse): RoleWorkspaceConfig {
  const ordered = [...access.routes].sort(
    (a, b) => a.menu_priority - b.menu_priority || a.route_id.localeCompare(b.route_id)
  );
  const allowSubmenus =
    access.allow_submenus || ordered.some((r) => r.allow_submenus);
  return {
    roleKey: access.role_id || (access.is_superadmin ? "superadmin" : "unknown"),
    displayName: access.display_name || access.role_name || "Workspace",
    visibleRoutes: ordered.map((r) => r.route_id),
    priorityOrder: ordered.map((r) => r.route_id),
    defaultLandingRoute: access.landing_route || ordered[0]?.route_id || "deals",
    defaultFacility: access.landing_facility || undefined,
    allowSubmenus,
  };
}
