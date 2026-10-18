import * as React from "react";
import { cn } from "@/lib/utils";
import { Skeleton } from "./Skeleton";
import { EmptyState } from "./EmptyState";

export interface Column<T> {
  key: string;
  header: string;
  render?: (item: T) => React.ReactNode;
  className?: string;
}

export interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  isLoading?: boolean;
  emptyTitle?: string;
  emptyDescription?: string;
  onRowClick?: (item: T) => void;
  className?: string;
}

export function DataTable<T extends { id?: string | number }>({
  columns,
  data,
  isLoading = false,
  emptyTitle = "Nenhum registro encontrado",
  emptyDescription = "Não existem dados disponíveis para os filtros atuais.",
  onRowClick,
  className,
}: DataTableProps<T>) {
  if (isLoading) {
    return (
      <div className={cn("w-full overflow-hidden rounded-lg border border-border bg-surface-card", className)}>
        <div className="p-4 border-b border-border-subtle flex gap-4">
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-4 w-40" />
        </div>
        <div className="divide-y divide-border-subtle">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="flex gap-4 p-4 items-center">
              <Skeleton className="h-4 w-1/4" />
              <Skeleton className="h-4 w-1/3" />
              <Skeleton className="h-4 w-1/6" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (data.length === 0) {
    return <EmptyState title={emptyTitle} description={emptyDescription} className={className} />;
  }

  return (
    <div className={cn("w-full overflow-x-auto rounded-lg border border-border bg-surface-card shadow-card", className)}>
      <table className="w-full text-left text-sm border-collapse">
        <thead className="bg-surface-bg/60 text-xs font-semibold uppercase tracking-wider text-text-secondary border-b border-border">
          <tr>
            {columns.map((col) => (
              <th key={col.key} className={cn("px-4 py-3.5", col.className)}>
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-border-subtle text-text-main">
          {data.map((item, index) => (
            <tr
              key={item.id ?? index}
              onClick={() => onRowClick && onRowClick(item)}
              className={cn(
                "transition-colors hover:bg-surface-bg/50",
                onRowClick && "cursor-pointer"
              )}
            >
              {columns.map((col) => (
                <td key={col.key} className={cn("px-4 py-3.5 align-middle", col.className)}>
                  {col.render ? col.render(item) : (item as Record<string, any>)[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
