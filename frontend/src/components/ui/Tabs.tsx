import React from "react";
import { cn } from "@/lib/utils";
import { RouteSubTabs, type RouteSubTabItem } from "./RouteSubTabs";
import { type BadgeVariant } from "./Badge";

export type { RouteSubTabItem };
export { RouteSubTabs };

export interface TabItem {
  id: string;
  label: string;
  count?: number;
  icon?: React.ReactNode;
  badge?: React.ReactNode | string | number;
  badgeVariant?: BadgeVariant;
  disabled?: boolean;
}

export interface TabsProps {
  tabs: TabItem[];
  activeTab: string;
  onChange: (tabId: string) => void;
  className?: string;
  variant?: "underline" | "cards";
  columns?: 1 | 2 | 3 | 4 | 5 | 6;
}

export function Tabs({
  tabs,
  activeTab,
  onChange,
  className,
  variant = "cards",
  columns,
}: TabsProps) {
  // Variante padrão canônica: cards com grid, ícone e badge
  if (variant === "cards") {
    const subTabItems: RouteSubTabItem[] = tabs.map((t) => ({
      id: t.id,
      label: t.label,
      icon: t.icon,
      badge: t.badge !== undefined ? t.badge : t.count,
      badgeVariant: t.badgeVariant,
      disabled: t.disabled,
    }));
    return (
      <RouteSubTabs
        tabs={subTabItems}
        activeTab={activeTab}
        onChange={onChange}
        className={className}
        columns={columns}
      />
    );
  }

  // Variante alternativa underline horizontal
  return (
    <div
      role="tablist"
      aria-orientation="horizontal"
      className={cn("flex flex-wrap border-b border-border gap-1", className)}
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
              "flex items-center gap-2 border-b-2 px-4 py-2.5 text-sm font-medium transition-colors -mb-px select-none",
              isActive
                ? "border-brand-primary text-brand-primary font-semibold"
                : "border-transparent text-text-secondary hover:text-text-main hover:border-border disabled:opacity-50"
            )}
          >
            {tab.icon && (
              <span className={isActive ? "text-brand-primary" : "text-text-secondary"}>
                {tab.icon}
              </span>
            )}
            <span>{tab.label}</span>
            {(tab.badge !== undefined || tab.count !== undefined) && (
              <span
                className={cn(
                  "rounded-full px-2 py-0.5 text-xs font-semibold whitespace-nowrap shrink-0",
                  isActive
                    ? "bg-brand-primary-subtle text-brand-primary"
                    : "bg-surface-bg text-text-muted"
                )}
              >
                {tab.badge !== undefined ? tab.badge : tab.count}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
