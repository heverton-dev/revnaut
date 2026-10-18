import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          primary: "var(--color-brand-primary)",
          "primary-hover": "var(--color-brand-primary-hover)",
          "primary-subtle": "var(--color-brand-primary-subtle)",
          navy: "var(--color-brand-navy)",
          "navy-subtle": "var(--color-brand-navy-subtle)",
        },
        surface: {
          bg: "var(--color-surface-bg)",
          card: "var(--color-surface-card)",
          sidebar: "var(--color-surface-sidebar)",
          "sidebar-hover": "var(--color-surface-sidebar-hover)",
          "sidebar-active": "var(--color-surface-sidebar-active)",
        },
        border: {
          DEFAULT: "var(--color-border)",
          subtle: "var(--color-border-subtle)",
        },
        text: {
          main: "var(--color-text-main)",
          secondary: "var(--color-text-secondary)",
          muted: "var(--color-text-muted)",
          inverse: "var(--color-text-inverse)",
        },
        status: {
          success: "var(--color-success)",
          "success-subtle": "var(--color-success-subtle)",
          warning: "var(--color-warning)",
          "warning-subtle": "var(--color-warning-subtle)",
          danger: "var(--color-danger)",
          "danger-subtle": "var(--color-danger-subtle)",
          whatsapp: "var(--color-whatsapp)",
        },
      },
      fontFamily: {
        sans: ["var(--font-family-sans)", "sans-serif"],
        mono: ["var(--font-family-mono)", "monospace"],
      },
      borderRadius: {
        sm: "var(--radius-sm, 4px)",
        md: "var(--radius-md, 6px)",
        lg: "var(--radius-lg, 8px)",
        full: "var(--radius-full, 9999px)",
      },
      boxShadow: {
        card: "var(--shadow-card, 0 1px 3px rgba(0,0,0,0.05))",
        dropdown: "var(--shadow-dropdown, 0 4px 12px rgba(0,0,0,0.1))",
        modal: "var(--shadow-modal, 0 12px 32px rgba(0,0,0,0.15))",
      },
    },
  },
  plugins: [],
};

export default config;
