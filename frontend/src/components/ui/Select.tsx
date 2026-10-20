import * as React from "react";
import * as RadixSelect from "@radix-ui/react-select";
import { ChevronDown, Check, ChevronUp } from "lucide-react";
import { cn } from "@/lib/utils";

export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface SelectProps {
  options: SelectOption[];
  label?: string;
  error?: string;
  value?: string;
  defaultValue?: string;
  onChange?: (e: React.ChangeEvent<HTMLSelectElement>) => void;
  onValueChange?: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  name?: string;
  id?: string;
  className?: string;
  triggerClassName?: string;
  required?: boolean;
  "aria-label"?: string;
}

const EMPTY_VALUE_TOKEN = "__EMPTY_SELECT_TOKEN__";

/**
 * Componente Select Canônico de Alto Padrão (Radix UI)
 * Substitui o select nativo bruto do browser por um popover elegante,
 * com cantos arredondados, checkmark ativo, suporte a teclado e transições suaves.
 */
export const Select = React.forwardRef<HTMLButtonElement, SelectProps>(
  (
    {
      options = [],
      label,
      error,
      value,
      defaultValue,
      onChange,
      onValueChange,
      placeholder = "Selecione uma opção...",
      disabled = false,
      name,
      id,
      className,
      triggerClassName,
      required,
      "aria-label": ariaLabel,
    },
    ref
  ) => {
    // Tratamento de valor vazio para compatibilidade estrita com o Radix UI
    const toInternalVal = (v?: string) => (v === "" ? EMPTY_VALUE_TOKEN : v);
    const fromInternalVal = (v: string) => (v === EMPTY_VALUE_TOKEN ? "" : v);

    const controlledValue = value !== undefined ? toInternalVal(value) : undefined;
    const defaultVal = defaultValue !== undefined ? toInternalVal(defaultValue) : undefined;

    const handleValueChange = (newVal: string) => {
      const actualVal = fromInternalVal(newVal);
      if (onValueChange) {
        onValueChange(actualVal);
      }
      if (onChange) {
        const syntheticEvent = {
          target: { value: actualVal, name: name || "" },
          currentTarget: { value: actualVal, name: name || "" },
          type: "change",
        } as unknown as React.ChangeEvent<HTMLSelectElement>;
        onChange(syntheticEvent);
      }
    };

    return (
      <div className={cn("w-full space-y-1.5", className)}>
        {label && (
          <label
            htmlFor={id}
            className="block text-xs font-semibold text-text-secondary select-none"
          >
            {label} {required && <span className="text-status-danger">*</span>}
          </label>
        )}

        <RadixSelect.Root
          value={controlledValue}
          defaultValue={defaultVal}
          onValueChange={handleValueChange}
          disabled={disabled}
          name={name}
        >
          <RadixSelect.Trigger
            ref={ref}
            id={id}
            aria-label={ariaLabel || label}
            className={cn(
              "group flex h-9 w-full items-center justify-between rounded-xl border border-border bg-surface-card px-3 py-1.5 text-xs font-medium text-text-main shadow-2xs transition-all cursor-pointer hover:border-brand-primary/50 hover:bg-surface-bg/50 focus:outline-none focus:ring-2 focus:ring-brand-primary/30 disabled:cursor-not-allowed disabled:opacity-50",
              error && "border-status-danger focus:ring-status-danger/30",
              triggerClassName
            )}
          >
            <RadixSelect.Value placeholder={placeholder} />
            <RadixSelect.Icon asChild>
              <ChevronDown className="h-4 w-4 text-text-muted transition-transform duration-200 group-data-[state=open]:rotate-180 group-hover:text-text-main shrink-0" />
            </RadixSelect.Icon>
          </RadixSelect.Trigger>

          <RadixSelect.Portal>
            <RadixSelect.Content
              position="popper"
              sideOffset={6}
              className="z-50 min-w-[var(--radix-select-trigger-width)] max-h-72 overflow-hidden rounded-xl border border-border bg-surface-card p-1 text-text-main shadow-xl animate-in fade-in-0 zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=top]:slide-in-from-bottom-2"
            >
              <RadixSelect.ScrollUpButton className="flex items-center justify-center py-1 text-text-muted">
                <ChevronUp className="h-4 w-4" />
              </RadixSelect.ScrollUpButton>

              <RadixSelect.Viewport className="p-1">
                {options.map((opt) => {
                  const internalItemVal = toInternalVal(opt.value);
                  return (
                    <RadixSelect.Item
                      key={internalItemVal}
                      value={internalItemVal!}
                      disabled={opt.disabled}
                      className={cn(
                        "relative flex w-full cursor-pointer select-none items-center justify-between rounded-lg py-2 pl-3 pr-8 text-xs font-medium outline-none transition-colors hover:bg-surface-bg focus:bg-surface-bg data-[disabled]:pointer-events-none data-[disabled]:opacity-40 data-[state=checked]:bg-brand-primary-subtle data-[state=checked]:text-brand-primary data-[state=checked]:font-bold"
                      )}
                    >
                      <RadixSelect.ItemText>{opt.label}</RadixSelect.ItemText>
                      <RadixSelect.ItemIndicator className="absolute right-2.5 flex items-center justify-center">
                        <Check className="h-3.5 w-3.5 text-brand-primary stroke-[2.5]" />
                      </RadixSelect.ItemIndicator>
                    </RadixSelect.Item>
                  );
                })}
              </RadixSelect.Viewport>

              <RadixSelect.ScrollDownButton className="flex items-center justify-center py-1 text-text-muted">
                <ChevronDown className="h-4 w-4" />
              </RadixSelect.ScrollDownButton>
            </RadixSelect.Content>
          </RadixSelect.Portal>
        </RadixSelect.Root>

        {error && <p className="text-[11px] font-medium text-status-danger">{error}</p>}
      </div>
    );
  }
);

Select.displayName = "Select";

export default Select;
