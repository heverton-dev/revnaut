import * as React from "react";
import { cn } from "@/lib/utils";

export interface ModalTabItem {
  id: string;
  label: string;
  icon?: React.ReactNode;
  count?: number;
}

export interface ModalTabBarProps {
  tabs: ModalTabItem[];
  activeTab: string;
  onChange: (tabId: string) => void;
  className?: string;
}

export function ModalTabBar({
  tabs,
  activeTab,
  onChange,
  className,
}: ModalTabBarProps) {
  // Ajusta o número de colunas do grid dinamicamente baseado no total de abas (até 4)
  const colsClass =
    tabs.length === 2
      ? "grid-cols-2"
      : tabs.length === 3
      ? "grid-cols-3"
      : "grid-cols-2 sm:grid-cols-4";

  return (
    <div
      className={cn(
        "grid gap-2.5 pt-2 px-1.5 pb-3.5 border-b border-border-subtle mb-5 shrink-0 select-none",
        colsClass,
        className
      )}
    >
      {tabs.map((tab) => {
        const isActive = tab.id === activeTab;
        return (
          <button
            key={tab.id}
            type="button"
            onClick={() => onChange(tab.id)}
            className={cn(
              "flex items-center justify-center gap-2 px-3 py-2.5 text-xs font-semibold rounded-xl transition border text-center cursor-pointer shadow-2xs outline-none focus:outline-none focus-visible:outline-none",
              isActive
                ? "border border-brand-primary/50 text-brand-primary bg-brand-primary-subtle font-semibold shadow-2xs"
                : "border border-border/70 bg-surface-bg text-text-secondary hover:text-text-main hover:bg-surface-card hover:border-border"
            )}
          >
            {tab.icon && <span className="shrink-0">{tab.icon}</span>}
            <span className="truncate">
              {tab.label}
              {typeof tab.count === "number" && ` (${tab.count})`}
            </span>
          </button>
        );
      })}
    </div>
  );
}
