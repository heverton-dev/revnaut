import * as React from "react";
import { CheckCircle2, AlertTriangle, AlertCircle, Info, X } from "lucide-react";
import { cn } from "@/lib/utils";

export type ToastType = "success" | "warning" | "error" | "info";

export interface ToastProps {
  id: string;
  type?: ToastType;
  title: string;
  description?: string;
  onClose?: (id: string) => void;
}

export function Toast({
  id,
  type = "info",
  title,
  description,
  onClose,
}: ToastProps) {
  const icons = {
    success: <CheckCircle2 className="h-5 w-5 text-status-success shrink-0" />,
    warning: <AlertTriangle className="h-5 w-5 text-status-warning shrink-0" />,
    error: <AlertCircle className="h-5 w-5 text-status-danger shrink-0" />,
    info: <Info className="h-5 w-5 text-brand-navy shrink-0" />,
  };

  return (
    <div
      role="alert"
      className={cn(
        "flex w-full max-w-sm items-start gap-3 rounded-lg border border-border bg-surface-card p-4 shadow-dropdown transition-all"
      )}
    >
      {icons[type]}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-text-main">{title}</p>
        {description && (
          <p className="mt-1 text-xs text-text-secondary leading-relaxed">
            {description}
          </p>
        )}
      </div>
      {onClose && (
        <button
          onClick={() => onClose(id)}
          className="text-text-muted hover:text-text-main transition-colors p-1"
          aria-label="Fechar notificação"
        >
          <X className="h-4 w-4" />
        </button>
      )}
    </div>
  );
}
