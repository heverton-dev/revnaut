import * as React from "react";
import { cn } from "@/lib/utils";
import { Skeleton } from "./Skeleton";
import { EmptyState } from "./EmptyState";

export interface KanbanStage<T> {
  id: string | number;
  name: string;
  color?: string;
  items: T[];
}

export interface KanbanBoardProps<T> {
  stages: KanbanStage<T>[];
  renderCard: (item: T) => React.ReactNode;
  isLoading?: boolean;
  onCardClick?: (item: T) => void;
  className?: string;
}

export function KanbanBoard<T extends { id: string | number }>({
  stages,
  renderCard,
  isLoading = false,
  onCardClick,
  className,
}: KanbanBoardProps<T>) {
  if (isLoading) {
    return (
      <div className={cn("grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4", className)}>
        {[1, 2, 3, 4, 5].map((col) => (
          <div key={col} className="flex flex-col gap-3 rounded-lg border border-border bg-surface-card p-3">
            <Skeleton className="h-5 w-24 mb-2" />
            <Skeleton className="h-24 w-full rounded-md" />
            <Skeleton className="h-24 w-full rounded-md" />
          </div>
        ))}
      </div>
    );
  }

  if (stages.length === 0) {
    return <EmptyState title="Nenhum estágio configurado" description="Cadastre os estágios do funil comercial para visualizar o Kanban." />;
  }

  return (
    <div className={cn("grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-4 pb-4", className)}>
      {stages.map((stage) => (
        <div
          key={stage.id}
          className="flex flex-col w-full min-w-0 rounded-lg border border-border bg-surface-bg/40 p-3 max-h-[540px]"
        >
          <div className="flex items-center justify-between pb-3 mb-2 border-b border-border-subtle">
            <div className="flex items-center gap-2 min-w-0">
              <span
                className="h-2.5 w-2.5 rounded-full shrink-0"
                style={{ backgroundColor: stage.color || "var(--color-brand-primary)" }}
              />
              <span className="text-xs font-semibold uppercase tracking-wider text-text-main truncate">
                {stage.name}
              </span>
            </div>
            <span className="text-xs font-medium text-text-muted bg-surface-card border border-border px-2 py-0.5 rounded-full shrink-0 whitespace-nowrap">
              {stage.items.length}
            </span>
          </div>

          <div className="flex flex-col gap-2.5 overflow-y-auto flex-1 pr-1">
            {stage.items.length === 0 ? (
              <div className="flex h-28 items-center justify-center rounded-md border border-dashed border-border-subtle p-4 text-center">
                <span className="text-xs text-text-muted">Sem itens nesta fase</span>
              </div>
            ) : (
              stage.items.slice(0, 25).map((item) => (
                <div
                  key={item.id}
                  onClick={() => onCardClick && onCardClick(item)}
                  className="cursor-pointer transition-transform hover:-translate-y-0.5"
                >
                  {renderCard(item)}
                </div>
              ))
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

