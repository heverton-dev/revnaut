import * as React from "react";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

export interface SheetProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children: React.ReactNode;
  side?: "right" | "left";
  className?: string;
}

export function Sheet({
  isOpen,
  onClose,
  title,
  description,
  children,
  side = "right",
  className,
}: SheetProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex">
      {/* Backdrop com desfoque e esmaecimento estritos (Regra Global de Foco & UX) */}
      <div
        className="fixed inset-0 bg-surface-overlay backdrop-blur-sm transition-all duration-200 animate-in fade-in-0"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Drawer Panel */}
      <div
        className={cn(
          "fixed inset-y-0 z-50 flex flex-col bg-surface-card p-6 shadow-modal transition ease-in-out duration-300 w-full sm:max-w-md",
          side === "right" ? "right-0 border-l border-border" : "left-0 border-r border-border",
          className
        )}
      >
        <div className="flex items-center justify-between pb-4 border-b border-border-subtle">
          <div>
            <h3 className="text-base font-semibold text-text-main">{title}</h3>
            {description && <p className="text-xs text-text-secondary mt-0.5">{description}</p>}
          </div>
          <button
            onClick={onClose}
            className="rounded-md p-1 text-text-muted hover:text-text-main hover:bg-surface-bg transition-colors"
            aria-label="Fechar painel"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto py-4">{children}</div>
      </div>
    </div>
  );
}
