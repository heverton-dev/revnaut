/**
 * omnichannel-sidebar.js
 * Componente Vanilla JS de Sidebar 360 para o Cockpit Omnichannel REVNAULT
 * Inviolable Law #14: Zero Emojis. Strictly inline SVG icons.
 */

export class OmnichannelSidebar {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.currentData = null;
  }

  async loadContext(contactIdentifier) {
    if (!this.container) return;
    this.renderLoading();
    try {
      const res = await fetch(`/api/v1/omnichannel/context/${encodeURIComponent(contactIdentifier)}`);
      if (!res.ok) throw new Error('Erro ao carregar contexto 360');
      this.currentData = await res.json();
      this.render();
    } catch (err) {
      this.renderError(err.message || 'Erro de comunicacao');
    }
  }

  renderLoading() {
    this.container.innerHTML = `
      <div class="sidebar-loading" style="padding:16px;color:#94a3b8;font-size:12px;display:flex;align-items:center;gap:8px;">
        <svg class="spin" style="width:16px;height:16px;color:#22d3ee;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" stroke-dasharray="32" stroke-dashoffset="12"/>
        </svg>
        <span>Carregando Contexto 360...</span>
      </div>
    `;
  }

  renderError(msg) {
    this.container.innerHTML = `
      <div class="sidebar-error" style="padding:16px;color:#fb7185;font-size:13px;display:flex;align-items:center;gap:8px;">
        <svg style="width:16px;height:16px;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <span>${msg}</span>
      </div>
    `;
  }

  render() {
    if (!this.currentData) return;
    const { contact, agreement, consignments_in_field = [], active_dentgo_orders = [], cro_uf } = this.currentData;

    const creditLimit = agreement ? agreement.credit_limit : 0;
    const usedCredit = agreement ? agreement.used_credit : 0;
    const availableCredit = agreement ? agreement.available_credit : 0;
    const creditPct = creditLimit > 0 ? Math.min(100, Math.round((usedCredit / creditLimit) * 100)) : 0;

    this.container.innerHTML = `
      <div class="omni-sidebar-card" style="padding:16px;background:#090d16;color:#e2e8f0;font-family:sans-serif;font-size:13px;display:flex;flex-direction:column;gap:16px;border-left:1px solid #1e293b;">
        <!-- Header -->
        <div style="border-bottom:1px solid #1e293b;padding-bottom:12px;display:flex;align-items:center;gap:10px;">
          <div style="background:#083344;color:#22d3ee;padding:8px;border-radius:6px;border:1px solid #0e7490;">
            <svg style="width:20px;height:20px;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <polyline points="16 11 18 13 22 9"/>
            </svg>
          </div>
          <div>
            <div style="font-weight:600;color:#f8fafc;">${contact ? contact.name : 'Cirurgiao'}</div>
            <div style="display:flex;gap:6px;margin-top:4px;">
              <span style="font-family:monospace;background:#082f49;color:#38bdf8;padding:2px 6px;border-radius:4px;font-size:11px;font-weight:700;">
                ${cro_uf || 'SEM CRO'}
              </span>
              ${contact && contact.score !== undefined ? `
                <span style="font-family:monospace;background:#451a03;color:#fcd34d;padding:2px 6px;border-radius:4px;font-size:11px;">
                  Score ${contact.score}
                </span>` : ''}
            </div>
          </div>
        </div>

        <!-- KeyPartners -->
        <div style="background:#0f172a;border:1px solid #1e293b;border-radius:6px;padding:12px;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <span style="font-size:11px;text-transform:uppercase;letter-spacing:0.05em;color:#94a3b8;font-weight:700;">KeyPartners • Credito</span>
            ${agreement ? `<span style="font-size:10px;background:#1e1b4b;color:#a5b4fc;padding:2px 6px;border-radius:4px;">${agreement.tier}</span>` : ''}
          </div>
          ${agreement ? `
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px;">
              <div>
                <div style="font-size:10px;color:#64748b;">Limite Total</div>
                <div style="font-family:monospace;font-weight:700;color:#f8fafc;">R$ ${creditLimit.toLocaleString('pt-BR', {minimumFractionDigits:2})}</div>
              </div>
              <div>
                <div style="font-size:10px;color:#64748b;">Disponivel</div>
                <div style="font-family:monospace;font-weight:700;color:#34d399;">R$ ${availableCredit.toLocaleString('pt-BR', {minimumFractionDigits:2})}</div>
              </div>
            </div>
            <div style="height:6px;background:#1e293b;border-radius:3px;overflow:hidden;">
              <div style="height:100%;width:${creditPct}%;background:${creditPct > 80 ? '#f43f5e' : '#22d3ee'};"></div>
            </div>
          ` : `<div style="font-size:11px;color:#64748b;font-style:italic;">Sem acordo registrado</div>`}
        </div>

        <!-- Kits em Campo -->
        <div style="background:#0f172a;border:1px solid #1e293b;border-radius:6px;padding:12px;">
          <div style="font-size:11px;text-transform:uppercase;letter-spacing:0.05em;color:#94a3b8;font-weight:700;margin-bottom:8px;">
            Kits em Custodia (${consignments_in_field.length})
          </div>
          ${consignments_in_field.length > 0 ? consignments_in_field.map(k => `
            <div style="background:#020617;border:1px solid #1e293b;border-radius:4px;padding:8px;margin-bottom:6px;">
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="font-family:monospace;color:#67e8f9;font-weight:700;">${k.serial_number}</span>
                <span style="font-size:9px;background:#064e3b;color:#6ee7b7;padding:1px 4px;border-radius:2px;">EM CAMPO</span>
              </div>
              <div style="font-size:11px;color:#cbd5e1;margin-top:2px;">${k.name}</div>
            </div>
          `).join('') : `<div style="font-size:11px;color:#64748b;font-style:italic;">Nenhum kit consignado</div>`}
        </div>

        <!-- DENTGO Express -->
        <div style="background:#0f172a;border:1px solid #1e293b;border-radius:6px;padding:12px;">
          <div style="font-size:11px;text-transform:uppercase;letter-spacing:0.05em;color:#94a3b8;font-weight:700;margin-bottom:8px;">
            DENTGO Express (${active_dentgo_orders.length})
          </div>
          ${active_dentgo_orders.length > 0 ? active_dentgo_orders.map(o => `
            <div style="background:#020617;border:1px solid #1e293b;border-radius:4px;padding:8px;margin-bottom:6px;">
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="font-family:monospace;color:#fde047;font-weight:700;">${o.id}</span>
                <span style="font-size:10px;color:#94a3b8;font-family:monospace;">ETA ~${o.estimated_eta_minutes}m</span>
              </div>
              <div style="display:flex;justify-content:space-between;align-items:center;margin-top:4px;">
                <span style="font-size:10px;background:#083344;color:#67e8f9;padding:1px 4px;border-radius:2px;">${o.status}</span>
                <span style="font-family:monospace;color:#f8fafc;">R$ ${(o.total_amount || 0).toFixed(2)}</span>
              </div>
            </div>
          `).join('') : `<div style="font-size:11px;color:#64748b;font-style:italic;">Nenhuma entrega em rota</div>`}
        </div>
      </div>
    `;
  }
}
