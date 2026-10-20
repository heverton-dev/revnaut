import React from "react";
import { cn } from "@/lib/utils";
import { Badge, type BadgeVariant } from "@/components/ui/Badge";

export interface RouteSubTabItem {
  id: string;
  label: string;
  icon?: React.ReactNode;
  badge?: React.ReactNode | string | number;
  badgeVariant?: BadgeVariant;
  disabled?: boolean;
}

export interface RouteSubTabsProps {
  tabs: RouteSubTabItem[];
  activeTab: string;
  onChange: (tabId: string) => void;
  className?: string;
  columns?: 1 | 2 | 3 | 4 | 5 | 6;
}

export const RouteSubTabs: React.FC<RouteSubTabsProps> = ({
  tabs,
  activeTab,
  onChange,
  className,
  columns,
}) => {
  // Determina dinamicamente a contagem de colunas para responsividade otimizada
  const colsCount = columns || (tabs.length === 2 ? 2 : tabs.length === 4 ? 4 : 3);

  const getGridColsClass = () => {
    switch (colsCount) {
      case 1:
        return "grid-cols-1";
      case 2:
        return "grid-cols-1 sm:grid-cols-2";
      case 4:
        return "grid-cols-1 sm:grid-cols-2 lg:grid-cols-4";
      case 5:
        return "grid-cols-1 sm:grid-cols-3 lg:grid-cols-5";
      case 6:
        return "grid-cols-1 sm:grid-cols-3 lg:grid-cols-6";
      case 3:
      default:
        return "grid-cols-1 sm:grid-cols-3";
    }
  };

  return (
    <div
      role="tablist"
      aria-orientation="horizontal"
      className={cn(
        "grid gap-2.5 sm:gap-3 w-full border-b border-border-subtle pb-3",
        getGridColsClass(),
        className
      )}
    >
      {tabs.map((tab) => {
        const isActive = tab.id === activeTab;
        return (
          <button
            key={tab.id}
            type="button"
            role="tab"
            aria-selected={isActive}
            disabled={tab.disabled}
            onClick={() => onChange(tab.id)}
            className={cn(
              "w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-xs font-semibold transition-all cursor-pointer select-none",
              isActive
                ? "bg-brand-primary text-text-inverse shadow-xs"
                : "bg-surface-card border border-border text-text-secondary hover:text-text-main hover:bg-surface-bg disabled:opacity-50 disabled:cursor-not-allowed"
            )}
          >
            <div className="flex items-center gap-2 min-w-0">
              {tab.icon && (
                <span
                  className={cn(
                    "shrink-0 flex items-center justify-center",
                    isActive ? "text-text-inverse" : "text-brand-primary"
                  )}
                >
                  {tab.icon}
                </span>
              )}
              <span className="truncate">{tab.label}</span>
            </div>
            {tab.badge !== undefined && tab.badge !== null && tab.badge !== "" && (
              <Badge
                variant={isActive ? "outline" : (tab.badgeVariant || "secondary")}
                className={cn(
                  "text-[10px] shrink-0 font-semibold",
                  isActive && "border-text-inverse/40 text-text-inverse bg-transparent"
                )}
              >
                {tab.badge}
              </Badge>
            )}
          </button>
        );
      })}
    </div>
  );
};
