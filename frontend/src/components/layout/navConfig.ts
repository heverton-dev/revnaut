import type { ElementType } from "react";
import {
  BarChart3,
  Users,
  Briefcase,
  MessageSquare,
  Package,
  Truck,
  ShieldCheck,
  LifeBuoy,
  Settings,
  Video,
  FileCheck2,
  Database,
  Calendar,
  Sparkles,
  Target,
  Megaphone,
  ScanLine,
  Radar,
} from "lucide-react";

export interface NavItem {
  id: string;
  label: string;
  icon: ElementType;
  badge?: string;
  /** Facility tab id in hash: #!/route?f=<facility> */
  facility?: string;
  children?: NavItem[];
}

export interface RoleWorkspaceConfig {
  roleKey: string;
  displayName: string;
  /** Route ids allowed for the role (parents). Children inherit parent access. */
  visibleRoutes: string[];
  /** Top-to-bottom priority for the day; omitted = canonical section order. */
  priorityOrder?: string[];
  defaultLandingRoute: string;
  defaultFacility?: string;
  /** Expand nested children under modules (power roles). Field mobile stays flat. */
  allowSubmenus: boolean;
}

/** Journey order: Operação do Dia → Pipeline → Entrega/Pós-venda → Gestão */
export const rawNavSections: { title: string; items: NavItem[] }[] = [
  {
    title: "Operação do Dia",
    items: [
      { id: "dashboard", label: "Visão do Dia", icon: BarChart3 },
      {
        id: "omnichannel",
        label: "Atendimento",
        icon: MessageSquare,
        children: [
          { id: "omnichannel", label: "Fila de Chats", facility: "chats", icon: MessageSquare },
          { id: "omnichannel", label: "Contatos", facility: "contacts", icon: Users },
          { id: "omnichannel", label: "Instâncias", facility: "instances", icon: Sparkles },
        ],
      },
      { id: "scheduling", label: "Agenda e Retornos", icon: Calendar },
    ],
  },
  {
    title: "Pipeline Comercial",
    items: [
      { id: "scoring", label: "Qualificação (ICP)", icon: Target },
      {
        id: "contacts",
        label: "Dentistas e Clínicas",
        icon: Users,
        children: [
          { id: "contacts", label: "Base de Cirurgiões", facility: "crm_surgeons", icon: Users },
          {
            id: "contacts",
            label: "Clínicas e Vínculos",
            facility: "institutions_links",
            icon: Package,
          },
          { id: "contacts", label: "Auditor CFO 196", facility: "cfo_compliance", icon: ShieldCheck },
          { id: "contacts", label: "Score ICP", facility: "icp_scoring", icon: Target },
        ],
      },
      { id: "deals", label: "Funil de Negociações", icon: Briefcase },
      {
        id: "contracts",
        label: "Propostas e Contratos",
        icon: FileCheck2,
        children: [
          {
            id: "contracts",
            label: "Assinaturas Documenso",
            facility: "documenso_lifecycle",
            icon: FileCheck2,
          },
          {
            id: "contracts",
            label: "Catálogo e Preços",
            facility: "anvisa_catalog_pricing",
            icon: Package,
          },
          {
            id: "contracts",
            label: "Custódia R2",
            facility: "r2_custody",
            icon: Package,
          },
        ],
      },
      { id: "imaging", label: "Exames e Diagnóstico 3D", icon: ScanLine },
      { id: "marketing", label: "Campanhas e Indicações", icon: Megaphone },
    ],
  },
  {
    title: "Entrega e Pós-Venda",
    items: [
      {
        id: "dentgo",
        label: "Entregas Expressas",
        icon: Truck,
        children: [
          { id: "dentgo", label: "Despacho 45 min", facility: "orders", icon: Truck },
          { id: "dentgo", label: "Hubs de Estoque", facility: "hubs", icon: Package },
          { id: "dentgo", label: "Ofertas FEFO", facility: "fefo", icon: Calendar },
          { id: "dentgo", label: "Repasses e Custos", facility: "split", icon: Database },
        ],
      },
      {
        id: "keypartners",
        label: "Consignação (Maletas)",
        icon: Package,
        children: [
          { id: "keypartners", label: "Board Cirúrgico", facility: "board", icon: Briefcase },
          { id: "keypartners", label: "Acordos", facility: "agreements", icon: FileCheck2 },
          { id: "keypartners", label: "KOL e Speakers", facility: "kol", icon: Users },
          { id: "keypartners", label: "Fidelidade", facility: "loyalty", icon: Target },
        ],
      },
      { id: "video_sos", label: "Chamadas e Vídeo", icon: Video },
      {
        id: "support",
        label: "Suporte e Garantias",
        icon: LifeBuoy,
        children: [
          {
            id: "support",
            label: "ANVISA e RMA",
            facility: "anvisa_rma",
            icon: ShieldCheck,
          },
          {
            id: "support",
            label: "SOS Mesa Cirúrgica",
            facility: "surgical_sos",
            icon: Video,
          },
          {
            id: "support",
            label: "Pós-operatório B2C",
            facility: "postop_b2c",
            icon: LifeBuoy,
          },
        ],
      },
    ],
  },
  {
    title: "Inteligência e Gestão",
    items: [
      {
        id: "intelligence",
        label: "Assistente Comercial",
        icon: Sparkles,
        children: [
          {
            id: "intelligence",
            label: "Resumo de Reuniões",
            facility: "copilot",
            icon: Sparkles,
          },
          {
            id: "intelligence",
            label: "Assistente Cirúrgico",
            facility: "rag",
            icon: LifeBuoy,
          },
          {
            id: "intelligence",
            label: "Maletas Paradas",
            facility: "inventory",
            icon: Package,
          },
          { id: "intelligence", label: "Margem Clínica", facility: "margin", icon: Database },
          {
            id: "intelligence",
            label: "Health Score",
            facility: "health_score",
            icon: Target,
          },
        ],
      },
      {
        id: "market_intel",
        label: "Radar de Mercado",
        icon: Radar,
        children: [
          { id: "market_intel", label: "Sinais", facility: "signals", icon: Radar },
          { id: "market_intel", label: "Concorrentes", facility: "competitors", icon: Target },
          {
            id: "market_intel",
            label: "Oportunidades",
            facility: "opportunities",
            icon: Briefcase,
          },
          { id: "market_intel", label: "Disparos", facility: "campaigns", icon: Megaphone },
        ],
      },
      {
        id: "analytics",
        label: "Relatórios e Metas",
        icon: Database,
        children: [
          {
            id: "analytics",
            label: "Studio BI e RLS",
            facility: "rls_studio",
            icon: Database,
          },
          {
            id: "analytics",
            label: "Text-to-SQL",
            facility: "text_to_sql",
            icon: Sparkles,
          },
        ],
      },
      {
        id: "rbac",
        label: "Equipes e Acessos",
        icon: ShieldCheck,
        children: [
          { id: "rbac", label: "Estrutura de Equipes", facility: "tree", icon: Users },
          { id: "rbac", label: "Permissões", facility: "permissions", icon: ShieldCheck },
          { id: "rbac", label: "Metas Comerciais", facility: "targets", icon: Target },
          {
            id: "rbac",
            label: "Comissionamento",
            facility: "commissions",
            icon: Database,
          },
        ],
      },
      {
        id: "settings",
        label: "Configurações",
        icon: Settings,
        children: [
          { id: "settings", label: "Cofre Cifrado", facility: "vault", icon: Settings },
          { id: "settings", label: "ERP e Fiscal", facility: "erp", icon: Database },
          { id: "settings", label: "Webhooks", facility: "webhooks", icon: Sparkles },
          { id: "settings", label: "Usuários e Quarteto", facility: "users", icon: Users },
        ],
      },
    ],
  },
];

export const ROLE_WORKSPACES: Record<string, RoleWorkspaceConfig> = {
  field_sales: {
    roleKey: "field_sales",
    displayName: "Consultor Externo (Campo)",
    visibleRoutes: [
      "deals",
      "contacts",
      "keypartners",
      "dentgo",
      "video_sos",
      "intelligence",
      "market_intel",
    ],
    priorityOrder: [
      "deals",
      "dentgo",
      "contacts",
      "keypartners",
      "video_sos",
      "intelligence",
      "market_intel",
    ],
    defaultLandingRoute: "deals",
    allowSubmenus: false,
  },
  inside_sales: {
    roleKey: "inside_sales",
    displayName: "Consultor Interno (Atendimento)",
    visibleRoutes: [
      "omnichannel",
      "deals",
      "contacts",
      "contracts",
      "scoring",
      "scheduling",
      "market_intel",
    ],
    priorityOrder: [
      "omnichannel",
      "scheduling",
      "deals",
      "scoring",
      "contacts",
      "contracts",
      "market_intel",
    ],
    defaultLandingRoute: "omnichannel",
    defaultFacility: "chats",
    allowSubmenus: false,
  },
  logistics: {
    roleKey: "logistics",
    displayName: "Logística e Estoque (Expedição)",
    visibleRoutes: ["dentgo", "keypartners", "support", "settings"],
    priorityOrder: ["dentgo", "keypartners", "support", "settings"],
    defaultLandingRoute: "dentgo",
    defaultFacility: "orders",
    allowSubmenus: true,
  },
  clinical_support: {
    roleKey: "clinical_support",
    displayName: "Suporte Clínico e Pós-Venda",
    visibleRoutes: ["support", "video_sos", "imaging", "omnichannel", "scheduling"],
    priorityOrder: ["support", "video_sos", "imaging", "scheduling", "omnichannel"],
    defaultLandingRoute: "support",
    defaultFacility: "anvisa_rma",
    allowSubmenus: true,
  },
  sales_manager: {
    roleKey: "sales_manager",
    displayName: "Gerente Comercial",
    visibleRoutes: [
      "dashboard",
      "deals",
      "contacts",
      "keypartners",
      "contracts",
      "rbac",
      "marketing",
      "market_intel",
    ],
    priorityOrder: [
      "dashboard",
      "deals",
      "market_intel",
      "contacts",
      "keypartners",
      "contracts",
      "marketing",
      "rbac",
    ],
    defaultLandingRoute: "dashboard",
    allowSubmenus: true,
  },
  superadmin: {
    roleKey: "superadmin",
    displayName: "Diretoria / Administrador Geral",
    visibleRoutes: [
      "dashboard",
      "deals",
      "contacts",
      "omnichannel",
      "scoring",
      "marketing",
      "keypartners",
      "dentgo",
      "contracts",
      "video_sos",
      "imaging",
      "intelligence",
      "market_intel",
      "analytics",
      "scheduling",
      "support",
      "rbac",
      "settings",
    ],
    defaultLandingRoute: "dashboard",
    allowSubmenus: true,
  },
};

/** Seed roles table → workspace (authoritative when present). */
export const ROLE_ID_TO_WORKSPACE: Record<string, RoleWorkspaceConfig> = {
  "role-field": ROLE_WORKSPACES.field_sales,
  "role-inside": ROLE_WORKSPACES.inside_sales,
  "role-logistics": ROLE_WORKSPACES.logistics,
  "role-clinical": ROLE_WORKSPACES.clinical_support,
  "role-manager": ROLE_WORKSPACES.sales_manager,
  "role-ceo": ROLE_WORKSPACES.superadmin,
};

/**
 * Prefer role_id (stable seed key), then specific label matching.
 * NEVER match bare "field" — it false-positives on "Dual Field/Inside".
 */
export function resolveRoleConfig(roleString?: string, roleId?: string | null): RoleWorkspaceConfig {
  if (roleId && ROLE_ID_TO_WORKSPACE[roleId]) {
    return ROLE_ID_TO_WORKSPACE[roleId];
  }

  const s = (roleString || "").toLowerCase();

  if (
    s.includes("super admin") ||
    s.includes("superadmin") ||
    s.includes("diretoria") ||
    s.includes("diretor") ||
    s.includes("administrador") ||
    s.includes("ceo")
  ) {
    return ROLE_WORKSPACES.superadmin;
  }

  if (s.includes("gerente") || s.includes("manager")) return ROLE_WORKSPACES.sales_manager;

  if (
    s.includes("logística") ||
    s.includes("logistica") ||
    s.includes("estoque") ||
    s.includes("expedição") ||
    s.includes("expedicao")
  ) {
    return ROLE_WORKSPACES.logistics;
  }

  if (
    s.includes("clínico") ||
    s.includes("clinico") ||
    s.includes("clinical") ||
    s.includes("pós-venda") ||
    s.includes("pos-venda") ||
    s.includes("suporte clínico") ||
    s.includes("suporte clinico")
  ) {
    return ROLE_WORKSPACES.clinical_support;
  }

  if (s.includes("inside") || s.includes("atendimento") || s.includes("interno")) {
    return ROLE_WORKSPACES.inside_sales;
  }

  if (
    s.includes("campo") ||
    s.includes("externo") ||
    s.includes("field_sales") ||
    s.includes("field sales")
  ) {
    return ROLE_WORKSPACES.field_sales;
  }

  if (s.includes("consultor") || s.includes("sdr")) return ROLE_WORKSPACES.inside_sales;

  // Desconhecido: least privilege — campo, não diretoria
  return ROLE_WORKSPACES.field_sales;
}

/** Flatten all leaf items (parents + children) for command palette. */
export function flattenNavItems(
  sections: { title: string; items: NavItem[] }[]
): (NavItem & { section: string })[] {
  return sections.flatMap((sec) =>
    sec.items.flatMap((item) => {
      const base = { ...item, section: sec.title };
      if (!item.children?.length) return [base];
      return [
        base,
        ...item.children.map((c) => ({
          ...c,
          section: `${sec.title} › ${item.label}`,
        })),
      ];
    })
  );
}

/**
 * Filter by visibleRoutes and reorder by priorityOrder (top = most used).
 * Groups keep journey titles; items without priority keep relative order.
 */
export function buildNavSections(
  roleConfig: RoleWorkspaceConfig,
  showAll: boolean
): { title: string; items: NavItem[] }[] {
  const source = rawNavSections;
  // Defensive: never trust a malformed role config into an empty sidebar
  const safeRole: RoleWorkspaceConfig =
    roleConfig && Array.isArray(roleConfig.visibleRoutes) && roleConfig.visibleRoutes.length > 0
      ? roleConfig
      : ROLE_WORKSPACES.superadmin;

  if (showAll) {
    return source.map((sec) => ({
      ...sec,
      items: sec.items.map((it) => (safeRole.allowSubmenus ? it : stripChildren(it))),
    }));
  }

  const allowed = new Set(safeRole.visibleRoutes);

  // Collect allowed items in journey order, then optionally re-sort by priority rank.
  const collected: { item: NavItem; journeyRank: number }[] = [];
  let journeyRank = 0;
  for (const sec of source) {
    for (const item of sec.items) {
      if (!allowed.has(item.id)) continue;
      collected.push({
        item: safeRole.allowSubmenus ? item : stripChildren(item),
        journeyRank: journeyRank++,
      });
    }
  }

  const priority = safeRole.priorityOrder;
  const priorityIndex = new Map<string, number>();
  if (priority) {
    priority.forEach((id, i) => priorityIndex.set(id, i));
  }

  if (priorityIndex.size > 0) {
    collected.sort((a, b) => {
      const ra = priorityIndex.has(a.item.id)
        ? priorityIndex.get(a.item.id)!
        : 10_000 + a.journeyRank;
      const rb = priorityIndex.has(b.item.id)
        ? priorityIndex.get(b.item.id)!
        : 10_000 + b.journeyRank;
      return ra - rb;
    });
  }

  // Re-group into journey sections (preserve section titles from source).
  const sectionOf = new Map<string, string>();
  for (const sec of source) {
    for (const item of sec.items) {
      sectionOf.set(item.id, sec.title);
    }
  }

  const bySection = new Map<string, NavItem[]>();
  for (const entry of collected) {
    const title = sectionOf.get(entry.item.id) || "Outros";
    if (!bySection.has(title)) bySection.set(title, []);
    bySection.get(title)!.push(entry.item);
  }

  // When priorityOrder is set, present a single prioritized stream under journey groups,
  // but only include groups that still have items.
  const journeyTitles = source.map((s) => s.title);
  const result: { title: string; items: NavItem[] }[] = [];
  for (const title of journeyTitles) {
    const items = bySection.get(title);
    if (items?.length) result.push({ title, items });
  }
  return result;
}

function stripChildren(item: NavItem): NavItem {
  const { children: _children, ...rest } = item;
  return rest;
}

/** Find a child facility item by route + facility id. */
export function findFacilityChild(
  routeId: string,
  facility?: string
): NavItem | undefined {
  if (!facility) return undefined;
  for (const sec of rawNavSections) {
    for (const item of sec.items) {
      if (item.id !== routeId || !item.children) continue;
      const hit = item.children.find((c) => c.facility === facility);
      if (hit) return hit;
    }
  }
  return undefined;
}

/** True when the sidebar exposes nested children for this route (hybrid tabs). */
export function sidebarModuleHasChildren(routeId: string): boolean {
  for (const sec of rawNavSections) {
    for (const item of sec.items) {
      if (item.id === routeId && item.children?.length) return true;
    }
  }
  return false;
}
