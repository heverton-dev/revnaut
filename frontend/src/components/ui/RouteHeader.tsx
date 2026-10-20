import React from "react";
import { cn } from "@/lib/utils";
import { Button, type ButtonProps } from "@/components/ui/Button";
import { ExportControl, type ExportControlProps } from "@/components/ui/ExportControl";

export interface RouteHeaderActionItem {
  id: string;
  label?: string; // Botões primários (variant="default") exibem 1 palavra; botões secundários com ícone colapsam para icon-only
  icon?: React.ReactNode;
  variant?: ButtonProps["variant"];
  onClick: () => void;
  disabled?: boolean;
  loading?: boolean;
  title?: string;
  ariaLabel?: string;
  showLabel?: boolean; // Permite forçar exibição ou ocultação de texto
}

export interface RouteHeaderProps {
  title: string;
  description?: string;
  badge?: React.ReactNode;
  children?: React.ReactNode;
  actions?: RouteHeaderActionItem[];
  exportConfig?: ExportControlProps;
  className?: string;
  sticky?: boolean;
}

/**
 * Garante rótulos contextuais focados na entidade de negócio (ex: '[+] Cirurgião', '[+] Oportunidade', '[+] Regra').
 * Remove automaticamente prefixos redundantes como 'Novo', 'Nova', 'Criar', '+' mantendo o substantivo contextual.
 */
export function formatHighlightActionLabel(label?: string): string | undefined {
  if (!label) return undefined;
  const cleaned = label.trim().replace(/^\+\s*/, "");
  const words = cleaned.split(/\s+/);
  if (
    words.length > 1 &&
    ["novo", "nova", "novos", "novas", "criar", "adicionar"].includes(words[0].toLowerCase())
  ) {
    return words.slice(1).join(" ");
  }
  return cleaned;
}

export const RouteHeader: React.FC<RouteHeaderProps> = ({
  title,
  description,
  badge,
  children,
  actions = [],
  exportConfig,
  className,
  sticky = false,
}) => {
  // Separação determinística de ações para garantir que o botão de atualizar (refresh/sync) fique no final SEMPRE
  const isRefreshAction = (act: RouteHeaderActionItem) =>
    act.id.toLowerCase().includes("refresh") ||
    act.id.toLowerCase().includes("sync") ||
    act.label?.toLowerCase().includes("atualizar") ||
    act.label?.toLowerCase().includes("sincronizar") ||
    act.title?.toLowerCase().includes("atualizar") ||
    act.title?.toLowerCase().includes("sincronizar") ||
    act.ariaLabel?.toLowerCase().includes("atualizar") ||
    act.ariaLabel?.toLowerCase().includes("sincronizar");

  const primaryActions = actions.filter(
    (act) => (!act.variant || act.variant === "default") && !isRefreshAction(act)
  );
  const secondaryActions = actions.filter(
    (act) => act.variant && act.variant !== "default" && !isRefreshAction(act)
  );
  const refreshActions = actions.filter((act) => isRefreshAction(act));

  return (
    <div
      className={cn(
        "flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border-subtle pb-4",
        sticky && "sticky top-0 z-20 bg-surface-bg/95 backdrop-blur-xs py-3 -mt-3",
        className
      )}
    >
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2.5">
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-text-main truncate">
            {title}
          </h1>
          {badge}
        </div>
        {description && (
          <p className="text-xs sm:text-sm text-text-secondary mt-1 max-w-3xl">
            {description}
          </p>
        )}
      </div>

      <div className="flex flex-wrap items-center gap-2 shrink-0">
        {children}

        {/* Grupo Canônico de Exportação Padronizada (Formato CSV/PARQUET + Botão Laranja) */}
        {exportConfig && <ExportControl {...exportConfig} />}

        {/* Divisor sutil entre Exportação e Ações Secundárias/Primárias */}
        {exportConfig && (secondaryActions.length > 0 || primaryActions.length > 0) && (
          <div className="h-4 w-px bg-border-subtle" />
        )}

        {/* Ações secundárias utilitárias compactas (ex: Importar CSV, Histórico) */}
        {secondaryActions.map((act) => {
          const shouldShowLabel =
            act.showLabel !== undefined ? act.showLabel : !act.icon;
          const displayLabel = shouldShowLabel ? act.label : undefined;

          return (
            <Button
              key={act.id}
              variant={act.variant}
              size="sm"
              onClick={act.onClick}
              disabled={act.disabled || act.loading}
              className={cn(
                "h-8 text-xs font-semibold shrink-0 gap-1.5",
                displayLabel ? "px-3" : "w-8 p-0 flex items-center justify-center"
              )}
              title={act.title || act.ariaLabel || act.label}
              aria-label={act.ariaLabel || act.title || act.label}
            >
              {act.icon && (
                <span className={cn("shrink-0", act.loading && "animate-spin")}>
                  {act.icon}
                </span>
              )}
              {displayLabel && <span>{displayLabel}</span>}
            </Button>
          );
        })}

        {/* Ações primárias de criação contextual ([+] Oportunidade, [+] Cirurgião) */}
        {primaryActions.map((act) => {
          const displayLabel = formatHighlightActionLabel(act.label);

          return (
            <Button
              key={act.id}
              variant="default"
              size="sm"
              onClick={act.onClick}
              disabled={act.disabled || act.loading}
              className="h-8 text-xs font-bold shrink-0 gap-1.5 px-3.5 shadow-sm rounded-xl"
              title={act.title || act.ariaLabel || act.label}
              aria-label={act.ariaLabel || act.title || act.label}
            >
              {act.icon && (
                <span className={cn("shrink-0", act.loading && "animate-spin")}>
                  {act.icon}
                </span>
              )}
              {displayLabel && <span>{displayLabel}</span>}
            </Button>
          );
        })}

        {/* Divisor sutil antes do botão de atualização / refresh */}
        {refreshActions.length > 0 &&
          (Boolean(exportConfig) ||
            secondaryActions.length > 0 ||
            primaryActions.length > 0 ||
            Boolean(children)) && (
            <div className="h-4 w-px bg-border-subtle" />
          )}

        {/* Botão Canônico de Atualização / Sincronização (Sempre no final) */}
        {refreshActions.map((act) => {
          const shouldShowLabel =
            act.showLabel !== undefined ? act.showLabel : !act.icon;
          const displayLabel = shouldShowLabel ? act.label : undefined;

          return (
            <Button
              key={act.id}
              variant={act.variant || "outline"}
              size="sm"
              onClick={act.onClick}
              disabled={act.disabled || act.loading}
              className={cn(
                "h-8 text-xs font-semibold shrink-0 gap-1.5",
                displayLabel ? "px-3" : "w-8 p-0 flex items-center justify-center"
              )}
              title={act.title || act.ariaLabel || act.label}
              aria-label={act.ariaLabel || act.title || act.label}
            >
              {act.icon && (
                <span className={cn("shrink-0", act.loading && "animate-spin")}>
                  {act.icon}
                </span>
              )}
              {displayLabel && <span>{displayLabel}</span>}
            </Button>
          );
        })}
      </div>
    </div>
  );
};
