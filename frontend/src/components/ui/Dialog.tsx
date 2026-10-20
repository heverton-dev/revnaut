import * as React from "react";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

export interface DialogProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  className?: string;
  size?: "sm" | "md" | "lg" | "xl" | "5xl" | "80vh" | "dossier" | "form" | "confirm";
}

const sizeClasses: Record<NonNullable<DialogProps["size"]>, string> = {
  sm: "max-w-sm",
  md: "max-w-lg",
  lg: "max-w-2xl",
  xl: "max-w-4xl",
  "5xl": "max-w-5xl",
  "80vh": "max-w-5xl h-[80vh] max-h-[80vh] flex flex-col",
  dossier: "max-w-5xl h-[80vh] max-h-[80vh] flex flex-col",
  form: "max-w-2xl min-h-[420px] max-h-[85vh] flex flex-col",
  confirm: "max-w-md",
};

export function Dialog({
  isOpen,
  onClose,
  title,
  description,
  children,
  footer,
  className,
  size = "md",
}: DialogProps) {
  React.useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const isScrollable = size === "80vh" || size === "dossier" || size === "form";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5">
      {/* Backdrop Fumê com Desfoque Canônico (86% opacidade) */}
      <div
        className="fixed inset-0 bg-surface-overlay backdrop-blur-sm transition-all duration-200 animate-in fade-in-0"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal Dialog */}
      <div
        role="dialog"
        aria-modal="true"
        className={cn(
          "relative z-50 w-full rounded-2xl border border-border bg-surface-card p-5 sm:p-7 shadow-modal animate-in fade-in-0 zoom-in-95",
          sizeClasses[size],
          className
        )}
      >
        {/* Header com Respiro Topo */}
        <div className="flex items-center justify-between pb-4 border-b border-border-subtle shrink-0">
          <div className="min-w-0 pr-4">
            <h3 className="text-base sm:text-lg font-bold text-text-main truncate">{title}</h3>
            {description && <p className="text-xs text-text-secondary mt-0.5 truncate">{description}</p>}
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-text-muted hover:text-text-main hover:bg-surface-bg transition-colors shrink-0 cursor-pointer"
            aria-label="Fechar modal"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Corpo com Margem Inferior Generosa (evita colamento no rodapé no final do scroll) */}
        <div className={cn("text-sm text-text-main", isScrollable ? "flex-1 overflow-y-auto pt-4 pb-8 pr-1.5" : "py-4")}>
          {children}
        </div>

        {/* Footer com Respiro Bottom */}
        {footer && (
          <div className="flex items-center justify-end gap-2 pt-4 border-t border-border-subtle shrink-0">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}
