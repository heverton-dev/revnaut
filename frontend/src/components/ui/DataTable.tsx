import * as React from "react";
import { cn } from "@/lib/utils";
import { Skeleton } from "./Skeleton";
import { EmptyState } from "./EmptyState";
import { Select } from "./Select";

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
  pageSizeOptions?: number[];
  defaultPageSize?: number;
  enablePagination?: boolean;
}

export function DataTable<T extends { id?: string | number }>({
  columns,
  data,
  isLoading = false,
  emptyTitle = "Nenhum registro encontrado",
  emptyDescription = "Não existem dados disponíveis para os filtros atuais.",
  onRowClick,
  className,
  pageSizeOptions = [25, 50],
  defaultPageSize = 25,
  enablePagination = true,
}: DataTableProps<T>) {
  const [currentPage, setCurrentPage] = React.useState(1);
  const [pageSize, setPageSize] = React.useState(defaultPageSize);

  React.useEffect(() => {
    setCurrentPage(1);
  }, [data.length, pageSize]);

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

  const totalItems = data.length;
  const totalPages = enablePagination ? Math.max(1, Math.ceil(totalItems / pageSize)) : 1;
  const safePage = Math.min(currentPage, totalPages);
  const startIdx = enablePagination ? (safePage - 1) * pageSize : 0;
  const endIdx = enablePagination ? Math.min(startIdx + pageSize, totalItems) : totalItems;
  const paginatedData = enablePagination ? data.slice(startIdx, endIdx) : data;

  return (
    <div className={cn("w-full rounded-lg border border-border bg-surface-card shadow-card overflow-hidden", className)}>
      <div className="w-full overflow-x-auto">
        <table className="w-full table-fixed sm:table-auto text-left text-xs sm:text-sm border-collapse">
          <thead className="bg-surface-bg/60 text-[11px] font-semibold uppercase tracking-wider text-text-secondary border-b border-border">
            <tr>
              {columns.map((col, colIdx) => (
                <th
                  key={col.key}
                  className={cn(
                    "px-2.5 sm:px-4 py-3 break-words",
                    colIdx >= 3 && "hidden md:table-cell",
                    col.className
                  )}
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border-subtle text-text-main">
            {paginatedData.map((item, index) => (
              <tr
                key={item.id ?? startIdx + index}
                onClick={() => onRowClick && onRowClick(item)}
                className={cn(
                  "transition-colors hover:bg-surface-bg/50",
                  onRowClick && "cursor-pointer"
                )}
              >
                {columns.map((col, colIdx) => (
                  <td
                    key={col.key}
                    className={cn(
                      "px-2.5 sm:px-4 py-3 align-middle break-words",
                      colIdx >= 3 && "hidden md:table-cell",
                      col.className
                    )}
                  >
                    {col.render ? col.render(item) : (item as Record<string, any>)[col.key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {enablePagination && totalItems > 0 && (
        <div className="flex flex-wrap items-center justify-between gap-2 px-3 sm:px-4 py-2.5 border-t border-border bg-surface-bg/40 text-xs text-text-secondary">
          <div className="flex items-center gap-2">
            <span>
              Exibindo <strong className="text-text-main">{startIdx + 1}</strong>–
              <strong className="text-text-main">{endIdx}</strong> de{" "}
              <strong className="text-text-main">{totalItems}</strong> registros
            </span>
            <Select
              aria-label="Itens por página"
              value={String(pageSize)}
              onValueChange={(val) => setPageSize(Number(val))}
              options={pageSizeOptions.map((opt) => ({
                value: String(opt),
                label: `${opt} / pág`,
              }))}
              className="w-28"
              triggerClassName="h-7 text-xs py-0.5 px-2 bg-surface-card"
            />
          </div>

          <div className="flex items-center gap-1.5">
            <button
              type="button"
              disabled={safePage <= 1}
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              className="rounded border border-border bg-surface-card px-2.5 py-1 text-xs font-medium text-text-main hover:bg-surface-bg disabled:opacity-40"
            >
              Anterior
            </button>
            <span className="px-2 font-medium text-text-main">
              Pág. {safePage} / {totalPages}
            </span>
            <button
              type="button"
              disabled={safePage >= totalPages}
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              className="rounded border border-border bg-surface-card px-2.5 py-1 text-xs font-medium text-text-main hover:bg-surface-bg disabled:opacity-40"
            >
              Próxima
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

