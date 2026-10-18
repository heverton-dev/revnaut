/**
 * Inbox Context 360° Sidebar Module (KeyPartners + DENTGO + CRO)
 * Renderiza o painel lateral contextual em tempo real para operadores de atendimento Omnichannel.
 */

export async function fetchOmnichannelContext360(contactPhoneOrCro, accountId = "0f14ffff") {
    const cleanParam = encodeURIComponent((contactPhoneOrCro || "").trim());
    const url = `/api/v1/omnichannel/chatwoot-context-panel?contact_phone=${cleanParam}&account_id=${encodeURIComponent(accountId)}`;
    const response = await fetch(url, {
        method: "GET",
        headers: { "Accept": "application/json" }
    });
    if (!response.ok) {
        throw new Error(`Falha ao carregar Contexto 360: HTTP ${response.status}`);
    }
    return await response.json();
}

export function renderInboxContextSidebar(containerEl, contextData) {
    if (!containerEl || !contextData) return "";
    const contact = contextData.contact || {};
    const agreement = contextData.agreement || {};
    const kits = Array.isArray(contextData.consignments_in_field) ? contextData.consignments_in_field : [];
    const orders = Array.isArray(contextData.active_dentgo_orders) ? contextData.active_dentgo_orders : [];

    const html = `
        <aside class="revnault-context-360-sidebar" data-cro="${contextData.cro_uf || ""}">
            <header class="context-section">
                <h3>Perfil Clínico & CRO</h3>
                <p><strong>Cirurgião:</strong> ${contact.name || "Não identificado"}</p>
                <p><strong>Registro:</strong> <span class="badge-cro">${contextData.cro_uf || "Pendente"}</span></p>
            </header>
            <section class="context-section">
                <h4>Acordo KeyPartners (${agreement.tier || "STANDARD"})</h4>
                <p><strong>Limite Disponível:</strong> R$ ${Number(agreement.available_credit || 0).toFixed(2)}</p>
                <p><strong>Kits em Campo:</strong> ${kits.length}</p>
            </section>
            <section class="context-section">
                <h4>Entregas Expressas DENTGO (${orders.length})</h4>
                <ul>
                    ${orders.map(o => `<li>Pedido ${o.id} — Status: ${o.status} (ETA: ${o.estimated_eta_minutes} min)</li>`).join("")}
                </ul>
            </section>
        </aside>
    `;
    containerEl.innerHTML = html;
    return html;
}
