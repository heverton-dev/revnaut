// -*- coding: utf-8 -*-
/**
 * bi-superset.js
 * Módulo de reconstrução visual para o Apache Superset Embedded BI (Lei #14: Zero Emojis).
 */

export function initBiSuperset(containerId, options = {}) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const {
    userId = 'usr-consultant-pr',
    dashboardId = 'dash-ind-consignment',
    dashboardType = 'industry_consignment',
    accountId = '0f14ffff',
    title = 'Painel Analítico de Giro de Consignado e Eficiência Fabril'
  } = options;

  container.innerHTML = `
    <div class="superset-bi-panel" style="display: flex; flex-direction: column; height: 100%; background: #0f172a; border-radius: 12px; border: 1px solid #1e293b; overflow: hidden;">
      <div style="display: flex; justify-content: space-between; align-items: center; padding: 16px 24px; border-bottom: 1px solid #1e293b; background: rgba(2, 6, 23, 0.7);">
        <div style="display: flex; align-items: center; gap: 12px;">
          <div style="padding: 8px; border-radius: 8px; background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.2); color: #818cf8;">
            <svg style="width: 20px; height: 20px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <div>
            <h3 style="margin: 0; font-size: 15px; font-weight: 600; color: #f8fafc;">${title}</h3>
            <span style="font-size: 12px; color: #94a3b8;">Apache Superset 3.1 com Row-Level Security Ativo</span>
          </div>
        </div>
        <div style="display: flex; gap: 8px; align-items: center;">
          <span id="bi-rls-badge" style="padding: 4px 10px; border-radius: 9999px; font-size: 11px; font-family: monospace; background: rgba(16, 185, 129, 0.1); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.2);">
            RLS Carregando...
          </span>
          <button id="btn-export-csv" style="display: flex; align-items: center; gap: 6px; padding: 6px 12px; font-size: 12px; background: #1e293b; color: #f1f5f9; border: 1px solid #334155; border-radius: 6px; cursor: pointer;">
            <svg style="width: 14px; height: 14px; color: #94a3b8;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Exportar CSV (R2)
          </button>
        </div>
      </div>
      <div id="superset-viewport" style="flex: 1; min-height: 580px; position: relative; background: #020617;">
        <div id="superset-loader" style="position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; color: #94a3b8; font-size: 13px;">
          <span>Autenticando Guest Token do Superset...</span>
        </div>
      </div>
    </div>
  `;

  // Chamada de API para o backend FastAPI
  fetch('/api/v1/intelligence/bi/guest-token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      dashboard_id: dashboardId,
      dashboard_type: dashboardType,
      account_id: accountId
    })
  })
    .then((r) => r.json())
    .then((data) => {
      const badge = document.getElementById('bi-rls-badge');
      if (badge && data.rls_clause) {
        badge.innerText = `RLS: ${data.rls_clause}`;
      }
      const viewport = document.getElementById('superset-viewport');
      if (viewport && data.token) {
        viewport.innerHTML = `
          <iframe
            src="${data.superset_domain}/embedded/${dashboardId}?guest_token=${encodeURIComponent(data.token)}"
            style="width: 100%; height: 100%; border: none;"
            allow="fullscreen"
          ></iframe>
        `;
      }
    })
    .catch((err) => {
      const loader = document.getElementById('superset-loader');
      if (loader) {
        loader.innerHTML = `<span style="color: #f87171;">Erro ao carregar dashboard de BI: ${err.message}</span>`;
      }
    });

  const exportBtn = document.getElementById('btn-export-csv');
  if (exportBtn) {
    exportBtn.addEventListener('click', () => {
      exportBtn.innerText = 'Exportando...';
      fetch('/api/v1/intelligence/bi/export-dataset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          dataset_name: 'consignment_turnover',
          user_id: userId,
          format: 'csv',
          account_id: accountId
        })
      })
        .then((r) => r.json())
        .then((res) => {
          alert(`Dataset exportado para Cloudflare R2: ${res.r2_storage_key}`);
          exportBtn.innerText = 'Exportar CSV (R2)';
        })
        .catch(() => {
          exportBtn.innerText = 'Exportar CSV (R2)';
        });
    });
  }
}
