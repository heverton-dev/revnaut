import React from "react";
import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import { Download, ChevronDown, Loader2, Check } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/utils";

export interface ExportFormatOption {
  value: string;
  label: string;
}

export interface ExportControlProps {
  format: string;
  formats?: ExportFormatOption[];
  onFormatChange: (format: string) => void;
  onExport: () => void;
  loading?: boolean;
  disabled?: boolean;
  label?: string;
  exportLabel?: string;
  className?: string;
}

const DEFAULT_FORMATS: ExportFormatOption[] = [
  { value: "csv", label: "CSV" },
  { value: "parquet", label: "PARQUET" },
];

/**
 * Componente canônico de Exportação Padronizada com Dropdown Estilizado
 * Padrão Shadcn / Radix UI (Sem uso de select nativo HTML bruto)
 */
export const ExportControl: React.FC<ExportControlProps> = ({
  format,
  formats = DEFAULT_FORMATS,
  onFormatChange,
  onExport,
  loading = false,
  disabled = false,
  label = "FORMATO",
  exportLabel = "Exportar",
  className,
}) => {
  const selectedOption = formats.find((f) => f.value === format) || formats[0] || { value: format, label: format.toUpperCase() };

  return (
    <div className={cn("inline-flex items-center gap-2 shrink-0", className)}>
      {/* Dropdown Estilizado Radix UI */}
      <DropdownMenu.Root>
        <DropdownMenu.Trigger asChild>
          <button
            type="button"
            disabled={disabled || loading}
            className={cn(
              "relative inline-flex items-center justify-between w-40 min-w-40 bg-surface-bg border border-border-subtle hover:border-brand-primary/50 hover:bg-surface-card rounded-xl px-3 py-1 h-8 shadow-2xs transition-all cursor-pointer group focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-primary/30 disabled:opacity-50 disabled:cursor-not-allowed select-none"
            )}
            title={`Formato atual: ${selectedOption.label}. Clique para alterar.`}
            aria-label={`Selecionar formato de exportação. Atual: ${selectedOption.label}`}
          >
            <span className="text-[10px] font-bold text-text-secondary tracking-widest uppercase mr-2 select-none shrink-0">
              {label}
            </span>
            <div className="flex items-center gap-1.5 min-w-0">
              <span className="text-xs font-bold text-text-main uppercase font-mono">
                {selectedOption.label}
              </span>
              <ChevronDown className="h-3.5 w-3.5 text-text-muted transition-transform duration-200 group-data-[state=open]:rotate-180 group-hover:text-text-main shrink-0" />
            </div>
          </button>
        </DropdownMenu.Trigger>

        <DropdownMenu.Portal>
          <DropdownMenu.Content
            align="start"
            sideOffset={6}
            className="z-50 w-40 min-w-40 overflow-hidden rounded-xl border border-border bg-surface-card p-1 text-text-main shadow-xl animate-in fade-in-0 zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=top]:slide-in-from-bottom-2"
          >
            <div className="px-2 py-1 text-[10px] font-bold text-text-muted uppercase tracking-wider border-b border-border-subtle mb-1">
              Opções de Arquivo
            </div>
            {formats.map((opt) => {
              const isSelected = opt.value === format;
              return (
                <DropdownMenu.Item
                  key={opt.value}
                  onClick={() => onFormatChange(opt.value)}
                  className={cn(
                    "relative flex cursor-pointer select-none items-center justify-between rounded-lg px-2.5 py-1.5 text-xs font-semibold outline-none transition-colors",
                    isSelected
                      ? "bg-brand-primary-subtle text-brand-primary font-bold"
                      : "text-text-main hover:bg-surface-bg hover:text-text-main"
                  )}
                >
                  <span className="font-mono">{opt.label}</span>
                  {isSelected && (
                    <Check className="h-3.5 w-3.5 text-brand-primary stroke-[2.5]" />
                  )}
                </DropdownMenu.Item>
              );
            })}
          </DropdownMenu.Content>
        </DropdownMenu.Portal>
      </DropdownMenu.Root>

      {/* Botão Primário de Destaque Laranja */}
      <Button
        variant="default"
        size="sm"
        onClick={onExport}
        disabled={disabled || loading}
        className="h-8 px-3.5 rounded-xl text-xs font-bold gap-1.5 shadow-sm shrink-0"
        title={`${exportLabel} dataset em ${selectedOption.label}`}
        aria-label={`${exportLabel} dataset em ${selectedOption.label}`}
      >
        {loading ? (
          <Loader2 className="h-3.5 w-3.5 animate-spin" />
        ) : (
          <Download className="h-3.5 w-3.5 stroke-[2.5]" />
        )}
        <span>{loading ? "Exportando..." : exportLabel}</span>
      </Button>
    </div>
  );
};

export default ExportControl;
