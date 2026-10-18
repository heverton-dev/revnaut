// -*- coding: utf-8 -*-
/**
 * SupersetEmbeddedDashboard.tsx
 * Componente React 19 + TypeScript para Apache Superset Embedded com Guest Tokens e RLS.
 * Totalmente aderente à Lei #14 (Zero Emojis Unicode — estritamente SVGs inline).
 */

import React, { useState, useEffect } from "react";

export interface SupersetEmbeddedProps {
  userId?: string;
  dashboardId: string;
  dashboardType?: "industry_consignment" | "clinic_chair" | "dentgo_sla" | "anvisa_quality_gate";
  accountId?: string;
  title?: string;
}

export interface GuestTokenData {
  token: string;
  dashboard_id: string;
  dashboard_type: string;
  rls_clause: string;
  superset_domain: string;
  expires_in_seconds: number;
}

export const SupersetEmbeddedDashboard: React.FC<SupersetEmbeddedProps> = ({
  userId = "usr-director-br",
  dashboardId,
  dashboardType = "industry_consignment",
  accountId = "0f14ffff",
  title = "Painel Analítico de Inteligência Cirúrgica",
}) => {
  const [loading, setLoading] = useState<boolean>(true);
  const [tokenData, setTokenData] = useState<GuestTokenData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [exporting, setExporting] = useState<boolean>(false);
  const [exportSuccess, setExportSuccess] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    setError(null);

    fetch("/api/v1/intelligence/bi/guest-token", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: userId,
        dashboard_id: dashboardId,
        dashboard_type: dashboardType,
        account_id: accountId,
      }),
    })
      .then(async (res) => {
        if (!res.ok) {
          throw new Error(`Falha ao obter Guest Token do Superset (HTTP ${res.status})`);
        }
        return res.json();
      })
      .then((data: GuestTokenData) => {
        if (isMounted) {
          setTokenData(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err.message || "Erro de conexão com o servidor de BI.");
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [userId, dashboardId, dashboardType, accountId]);

  const handleExportDataset = async (format: "csv" | "parquet") => {
    setExporting(true);
    setExportSuccess(null);
    try {
      const res = await fetch("/api/v1/intelligence/bi/export-dataset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          dataset_name:
            dashboardType === "industry_consignment" ? "consignment_turnover" : "deals_funnel",
          user_id: userId,
          format: format,
          account_id: accountId,
        }),
      });
      if (!res.ok) throw new Error("Erro ao exportar dataset");
      const data = await res.json();
      setExportSuccess(
        `Dataset exportado para R2: ${data.r2_storage_key} (${data.record_count} registros)`
      );
    } catch (err: any) {
      setError(err.message);
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="flex flex-col h-full w-full bg-surface-card border border-border rounded-xl overflow-hidden shadow-card">
      <div className="flex items-center justify-between px-6 py-4 border-b border-border bg-surface-bg">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-brand-navy-subtle border border-border text-brand-navy">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
          </div>
          <div>
            <h2 className="text-base font-semibold text-text-main">{title}</h2>
            <p className="text-xs text-text-secondary">
              Apache Superset 3.1 Embedded com Row-Level Security (RLS) ativo
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {tokenData && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono font-medium bg-status-success-subtle text-status-success border border-status-success/20">
              <span className="w-1.5 h-1.5 rounded-full bg-status-success animate-pulse"></span>
              RLS: {tokenData.rls_clause}
            </span>
          )}

          <button
            onClick={() => handleExportDataset("csv")}
            disabled={exporting || loading}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-text-main bg-surface-card hover:bg-surface-bg border border-border rounded-lg transition-colors disabled:opacity-50"
          >
            <svg className="w-4 h-4 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
              />
            </svg>
            {exporting ? "Exportando..." : "Exportar CSV (R2)"}
          </button>
        </div>
      </div>

      {exportSuccess && (
        <div className="px-6 py-2 bg-status-success-subtle border-b border-status-success/30 text-xs text-status-success">
          {exportSuccess}
        </div>
      )}

      <div className="flex-1 relative min-h-[640px] bg-surface-bg">
        {loading && (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-surface-bg/90 z-10">
            <div className="w-8 h-8 border-2 border-brand-primary border-t-transparent rounded-full animate-spin"></div>
            <p className="text-sm text-text-secondary font-medium">
              Autenticando Guest Token e aplicando cláusula RLS...
            </p>
          </div>
        )}

        {error && (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 p-6 text-center">
            <div className="p-3 rounded-full bg-status-danger-subtle border border-status-danger/20 text-status-danger">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>
            <h3 className="text-sm font-semibold text-text-main">
              Não foi possível carregar o dashboard
            </h3>
            <p className="text-xs text-text-secondary max-w-md">{error}</p>
          </div>
        )}

        {!loading && !error && tokenData && (
          <iframe
            id={`superset-frame-${dashboardId}`}
            title={title}
            src={`${tokenData.superset_domain}/embedded/${dashboardId}?guest_token=${encodeURIComponent(tokenData.token)}`}
            className="w-full h-full border-0"
            allow="fullscreen"
          />
        )}
      </div>
    </div>
  );
};

export default SupersetEmbeddedDashboard;
