import * as React from "react";
import {
  Users,
  Briefcase,
  Shield,
  Layers,
  ChevronRight,
  ChevronDown,
  Building2,
  Percent,
  CheckCircle2,
  UserCheck,
} from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
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
  isLoading?: boolean;
  isEmpty?: boolean;
  className?: string;
}

export function RbacHierarchyTree({
  isLoading = false,
  isEmpty = false,
  className,
}: RbacHierarchyTreeProps) {
  const [expandedNodes, setExpandedNodes] = React.useState<Record<string, boolean>>({
    bu_sp: true,
    team_sp_field: true,
    team_sp_inside: true,
  });

  const sampleTree: HierarchyNode = {
    id: "bu_sp",
    name: "Diretoria Regional São Paulo & Sul",
    role: "Diretor Comercial Regional",
    type: "business_unit",
    children: [
      {
        id: "team_sp_field",
        name: "Mesa Externa — Field Sales Cirúrgico",
        role: "Gerente Regional de Campo",
        type: "team",
        commissionPct: 70,
        children: [
          {
            id: "usr_field_a",
            name: "Dr. Carlos Mendonça (Consultor Titular SP Capital)",
            role: "Consultor Sênior de Campo",
            type: "field_sales",
            dealCount: 14,
            commissionPct: 70,
          },
          {
            id: "usr_field_b",
            name: "Mariana Alencar (Consultora Titular Campinas & Interior)",
            role: "Consultora Plena de Campo",
            type: "field_sales",
            dealCount: 9,
            commissionPct: 70,
          },
        ],
      },
      {
        id: "team_sp_inside",
        name: "Mesa Interna — Inside Sales & Backoffice Cirúrgico",
        role: "Coordenador de Operações & SDR",
        type: "team",
        commissionPct: 30,
        children: [
          {
            id: "usr_inside_sp",
            name: "Patrícia Diniz (Analista Inside SP & Triagem DENTGO)",
            role: "Analista de Suporte & Fechamento",
            type: "inside_sales",
            dealCount: 23,
            commissionPct: 30,
          },
        ],
      },
    ],
  };

  const toggleNode = (nodeId: string) => {
    setExpandedNodes((prev) => ({ ...prev, [nodeId]: !prev[nodeId] }));
  };

  if (isLoading) {
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

  if (isEmpty) {
    return (
      <EmptyState
        icon={Users}
        title="Nenhuma hierarquia configurada"
        description="Defina os nós de Diretoria, Field Sales e Inside Sales para habilitar a árvore dual."
        actionLabel="Configurar Organograma"
        onAction={() => {}}
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
            <Badge variant={typeBadges[node.type].variant} className="text-[10px]">
              {typeBadges[node.type].label}
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
      <CardContent className="space-y-3">{renderNode(sampleTree)}</CardContent>
    </Card>
  );
}
