import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 whitespace-nowrap shrink-0 select-none",
  {
    variants: {
      variant: {
        default: "border-transparent bg-brand-primary text-text-inverse",
        navy: "border-transparent bg-brand-navy text-text-inverse",
        secondary: "border-border bg-surface-bg text-text-main",
        success: "border-transparent bg-status-success-subtle text-status-success font-medium",
        warning: "border-transparent bg-status-warning-subtle text-status-warning font-medium",
        danger: "border-transparent bg-status-danger-subtle text-status-danger font-medium",
        outline: "border-border text-text-main",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export type BadgeVariant = VariantProps<typeof badgeVariants>["variant"];

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <div data-badge="true" className={cn(badgeVariants({ variant }), className)} {...props} />;
}
