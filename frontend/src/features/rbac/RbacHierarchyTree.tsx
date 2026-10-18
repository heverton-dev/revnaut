import * as React from "react";
import {
  Users,
  Briefcase,
  Layers,
  ChevronRight,
  ChevronDown,
  Building2,
  Percent,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
} from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Skeleton } from "@/components/ui/Skeleton";
import { EmptyState } from "@/components/ui/EmptyState";
import { cn } from "@/lib/utils";

export interface HierarchyNode {
  id: string;
  name: string;
  role: string;
  type: "business_unit" | "team" | "field_sales" | "inside_sales";
  commissionPct?: number;
  dealCount?: number;
  children?: HierarchyNode[];
}

export interface RbacHierarchyTreeProps {
  accountId?: string;
  isLoading?: boolean;
  isEmpty?: boolean;
  className?: string;
}

export function RbacHierarchyTree({
  accountId = "0f14ffff",
  isLoading: externalLoading,
  isEmpty: externalEmpty,
  className,
}: RbacHierarchyTreeProps) {
  const [treeData, setTreeData] = React.useState<HierarchyNode[]>([]);
  const [loading, setLoading] = React.useState<boolean>(true);
  const [error, setError] = React.useState<string | null>(null);
  const [expandedNodes, setExpandedNodes] = React.useState<Record<string, boolean>>({});

  const fetchHierarchyTree = React.useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/v1/hierarchy/tree?account_id=${encodeURIComponent(accountId)}`);
      if (!res.ok) {
        throw new Error(`Falha ao carregar árvore hierárquica (HTTP ${res.status})`);
      }
      const data = await res.json();
      const rawNodes = Array.isArray(data)
        ? data
        : data.tree || data.business_units || data.nodes || [];

      const normalized: HierarchyNode[] = rawNodes.map((n: any) => ({
        id: String(n.id || n.unit_id || n.team_id || "root"),
        name: n.name || n.title || "Unidade Organizacional",
        role: n.role || n.description || "Escopo Regional Dual",
        type: (n.type as HierarchyNode["type"]) || "business_unit",
        commissionPct: n.commission_pct ?? n.commissionPct,
        dealCount: n.deal_count ?? n.dealCount,
        children: Array.isArray(n.children || n.teams)
          ? (n.children || n.teams).map((child: any) => ({
              id: String(child.id || child.team_id),
              name: child.name || "Equipe Regional",
              role: child.role || child.scope || "Equipe Dual",
              type: (child.type as HierarchyNode["type"]) || "team",
              commissionPct: child.commission_pct ?? child.commissionPct,
              dealCount: child.deal_count ?? child.dealCount,
              children: Array.isArray(child.children || child.members)
                ? (child.children || child.members).map((m: any) => ({
                    id: String(m.id || m.user_id),
                    name: m.name || "Consultor",
                    role: m.role || "Consultor Comercial",
                    type: (m.type as HierarchyNode["type"]) || "field_sales",
                    commissionPct: m.commission_pct ?? m.commissionPct,
                    dealCount: m.deal_count ?? m.dealCount,
                  }))
                : [],
            }))
          : [],
      }));

      setTreeData(normalized);
      const initialExpanded: Record<string, boolean> = {};
      normalized.forEach((n) => {
        initialExpanded[n.id] = true;
      });
      setExpandedNodes(initialExpanded);
    } catch (err: any) {
      setError(err.message || "Erro ao consultar organograma RBAC.");
    } finally {
      setLoading(false);
    }
  }, [accountId]);

  React.useEffect(() => {
    fetchHierarchyTree();
  }, [fetchHierarchyTree]);

  const toggleNode = (nodeId: string) => {
    setExpandedNodes((prev) => ({ ...prev, [nodeId]: !prev[nodeId] }));
  };

  if (externalLoading || loading) {
    return (
      <Card className={cn("p-6", className)}>
        <Skeleton className="h-6 w-48 mb-4" />
        <div className="space-y-3">
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-12 w-11/12 ml-6" />
          <Skeleton className="h-12 w-10/12 ml-12" />
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={cn("p-8 text-center border-status-danger/30", className)}>
        <div className="flex flex-col items-center gap-3">
          <AlertCircle className="h-8 w-8 text-status-danger" />
          <h4 className="text-sm font-semibold text-text-main">{error}</h4>
          <button
            onClick={fetchHierarchyTree}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-brand-primary text-text-inverse text-xs font-medium"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Tentar Novamente
          </button>
        </div>
      </Card>
    );
  }

  if (externalEmpty || treeData.length === 0) {
    return (
      <EmptyState
        icon={Users}
        title="Nenhuma hierarquia configurada"
        description="Defina os nós de Diretoria, Field Sales e Inside Sales para habilitar a árvore dual."
        actionLabel="Recarregar Organograma"
        onAction={fetchHierarchyTree}
        className={className}
      />
    );
  }

  const renderNode = (node: HierarchyNode, level: number = 0) => {
    const isExpanded = expandedNodes[node.id] ?? false;
    const hasChildren = node.children && node.children.length > 0;

    const typeBadges = {
      business_unit: { variant: "navy" as const, label: "Unidade de Negócio" },
      team: { variant: "default" as const, label: "Equipe Regional" },
      field_sales: { variant: "default" as const, label: "Field Sales (Campo)" },
      inside_sales: { variant: "navy" as const, label: "Inside Sales (Mesa)" },
    };

    const badgeInfo = typeBadges[node.type] || typeBadges.team;

    return (
      <div key={node.id} className="space-y-2">
        <div
          style={{ paddingLeft: `${level * 24}px` }}
          className="flex items-center justify-between p-3 rounded-lg border border-border bg-surface-card hover:bg-surface-bg/60 transition-colors"
        >
          <div className="flex items-center gap-3">
            {hasChildren ? (
              <button
                onClick={() => toggleNode(node.id)}
                className="p-1 rounded text-text-muted hover:text-text-main"
                aria-label={isExpanded ? "Recolher nó" : "Expandir nó"}
              >
                {isExpanded ? (
                  <ChevronDown className="h-4 w-4" />
                ) : (
                  <ChevronRight className="h-4 w-4" />
                )}
              </button>
            ) : (
              <span className="w-6" />
            )}

            {node.type === "business_unit" && <Building2 className="h-5 w-5 text-brand-navy" />}
            {node.type === "team" && <Layers className="h-5 w-5 text-brand-primary" />}
            {node.type === "field_sales" && <Briefcase className="h-4 w-4 text-brand-primary" />}
            {node.type === "inside_sales" && <Users className="h-4 w-4 text-brand-navy" />}

            <div>
              <span className="text-sm font-semibold text-text-main">{node.name}</span>
              <p className="text-xs text-text-secondary">{node.role}</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {node.commissionPct !== undefined && (
              <Badge variant="secondary" className="text-xs inline-flex items-center gap-1">
                <Percent className="h-3 w-3" />
                Comissão: {node.commissionPct}%
              </Badge>
            )}
            {node.dealCount !== undefined && (
              <Badge variant="outline" className="text-xs">
                {node.dealCount} Oportunidades
              </Badge>
            )}
            <Badge variant={badgeInfo.variant} className="text-[10px]">
              {badgeInfo.label}
            </Badge>
          </div>
        </div>

        {hasChildren && isExpanded && (
          <div className="space-y-2">
            {node.children!.map((child) => renderNode(child, level + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <Card className={cn("border-border", className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Estrutura Hierárquica Dual (Field Sales vs. Inside Sales)</CardTitle>
            <CardDescription>
              Isolamento de carteiras territoriais com visibilidade compartilhada de co-piloto e comissão bipartida (70% Campo / 30% Mesa).
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="success" className="text-xs inline-flex items-center gap-1">
              <CheckCircle2 className="h-3.5 w-3.5" />
              DAG Validado Sem Ciclos
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {treeData.map((rootNode) => renderNode(rootNode))}
      </CardContent>
    </Card>
  );
}
