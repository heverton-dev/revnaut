import { LucideIcon, Inbox } from "lucide-react";
import { Button } from "./Button";
import { cn } from "@/lib/utils";

export interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
  className?: string;
}

export function EmptyState({
  icon: Icon = Inbox,
  title,
  description,
  actionLabel,
  onAction,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center p-8 text-center rounded-lg border border-dashed border-border bg-surface-card",
        className
      )}
    >
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-brand-primary-subtle text-brand-primary mb-3">
        <Icon className="h-6 w-6 stroke-[1.5]" />
      </div>
      <h4 className="text-base font-semibold text-text-main">{title}</h4>
      <p className="mt-1 text-sm text-text-secondary max-w-sm">{description}</p>
      {actionLabel && onAction && (
        <Button onClick={onAction} className="mt-4" size="sm">
          {actionLabel}
        </Button>
      )}
    </div>
  );
}
