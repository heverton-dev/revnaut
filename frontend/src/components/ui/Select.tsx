import * as React from "react";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

export interface SelectOption {
  value: string;
  label: string;
}

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  options: SelectOption[];
  label?: string;
  error?: string;
}

export const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, options, label, error, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && <label className="mb-1.5 block text-xs font-medium text-text-secondary">{label}</label>}
        <div className="relative">
          <select
            ref={ref}
            className={cn(
              "flex h-9 w-full appearance-none rounded-md border border-border bg-surface-card px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-brand-primary disabled:cursor-not-allowed disabled:opacity-50 pr-8 text-text-main",
              error && "border-status-danger focus-visible:ring-status-danger",
              className
            )}
            {...props}
          >
            {options.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <ChevronDown className="pointer-events-none absolute right-2.5 top-2.5 h-4 w-4 text-text-muted" />
        </div>
        {error && <p className="mt-1 text-xs text-status-danger">{error}</p>}
      </div>
    );
  }
);
Select.displayName = "Select";
