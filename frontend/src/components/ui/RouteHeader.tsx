import React from "react";
import { cn } from "@/lib/utils";
import { Button, type ButtonProps } from "@/components/ui/Button";

export interface RouteHeaderActionItem {
  id: string;
  label?: string; // Botões de destaque (variant="default") exibem no máximo 1 palavra
  icon?: React.ReactNode;
  variant?: ButtonProps["variant"];
  onClick: () => void;
  disabled?: boolean;
  loading?: boolean;
  title?: string;
  ariaLabel?: string;
}

export interface RouteHeaderProps {
  title: string;
  description?: string;
  badge?: React.ReactNode;
  children?: React.ReactNode;
  actions?: RouteHeaderActionItem[];
  className?: string;
}

/**
 * Garante deterministicamente no máximo 1 palavra para ações de destaque (laranja / default)
 */
export function formatHighlightActionLabel(label?: string): string | undefined {
  if (!label) return undefined;
  const trimmed = label.trim();
  const firstWord = trimmed.split(/\s+/)[0];
  return firstWord;
}

export const RouteHeader: React.FC<RouteHeaderProps> = ({
  title,
  description,
  badge,
  children,
  actions = [],
  className,
}) => {
  return (
    <div
      className={cn(
        "flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border-subtle pb-4",
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

        {actions.map((act) => {
          const isHighlight = !act.variant || act.variant === "default";
          const displayLabel = isHighlight
            ? formatHighlightActionLabel(act.label)
            : act.label;

          return (
            <Button
              key={act.id}
              variant={act.variant || "default"}
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
