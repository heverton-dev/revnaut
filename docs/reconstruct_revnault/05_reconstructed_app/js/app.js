/**
 * RevNault Reconstructed — Frontend Application Controller (ES Module)
 * Pure Vanilla JavaScript with modular ES Modules architecture.
 */

import { api, getAuthToken, setAuthToken, clearAuthToken } from './modules/api-client.js';
import * as rbacTree from './modules/rbac-tree.js';
import * as kanbanDeals from './modules/kanban-deals.js';
import * as consignments from './modules/consignments.js';

if (typeof window !== 'undefined') {
  window.RevNaultModules = { api, rbacTree, kanbanDeals, consignments };
  window.REVNAULT_DATA = window.REVNAULT_DATA || {};
}

document.addEventListener('DOMContentLoaded', () => {
  const data = window.REVNAULT_DATA;
  let currentView = 'deals';
  let dealViewMode = 'kanban';
  let activeChatId = 'chat-1';


  const API_URL = (window.location.protocol === 'file:' || window.location.origin === 'null')
    ? 'http://localhost:8000/api/v1'
    : (window.location.origin + '/api/v1');

  // Formatador de Moeda BRL
  const formatBRL = (val) => {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);
  };

  // Inicialização de Componentes
  initNavigation();
  checkApiConnectivity();
  renderDashboard();
  renderDeals();
  renderContacts();
  renderChat();
  setupModal();

  async function checkApiConnectivity() {
    try {
      const res = await fetch(`${API_URL}/health`, { signal: AbortSignal.timeout(1500) });
      if (res.ok) {
        isApiOnline = true;
        const badge = document.querySelector('.tenant-badge');
        if (badge) {
          badge.innerHTML = '<span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:#10b981;margin-right:6px;"></span>API Python SQLite WAL Ativa';
          badge.style.backgroundColor = 'hsl(148, 50%, 92%)';
          badge.style.color = 'hsl(148, 50%, 30%)';
        }
        await syncDataFromBackend();
      }
    } catch (e) {
      console.log('Modo autônomo offline ativo (dados da sessão RevNault local).');
    }
  }

  async function syncDataFromBackend() {
    try {
      const [dealsRes, metricsRes, contactsRes] = await Promise.all([
        fetch(`${API_URL}/deals`),
        fetch(`${API_URL}/metrics`),
        fetch(`${API_URL}/contacts`)
      ]);
      if (dealsRes.ok) {
        const pipelineData = await dealsRes.json();
        data.pipelines[0].stages = pipelineData.stages;
        renderDeals();
      }
      if (metricsRes.ok) {
        data.metrics = await metricsRes.json();
        renderDashboard();
      }
      if (contactsRes.ok) {
        data.contacts = await contactsRes.json();
        renderContacts();
      }
    } catch (err) {
      console.warn('Erro na sincronização síncrona com backend:', err);
    }
  }

  // 1. Navegação Lateral
  function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item[data-view]');
    navItems.forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        const viewId = item.getAttribute('data-view');
        switchView(viewId);
      });
    });

    // View Switcher (Kanban vs Lista)
    const segmentBtns = document.querySelectorAll('.segment-btn');
    segmentBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        segmentBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        dealViewMode = btn.getAttribute('data-mode');
        renderDeals();
      });
    });
  }

  function switchView(viewId) {
    currentView = viewId;
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    const activeNav = document.querySelector(`.nav-item[data-view="${viewId}"]`);
    if (activeNav) activeNav.classList.add('active');

    document.querySelectorAll('.view-container').forEach(el => el.classList.remove('active'));
    const activeContainer = document.getElementById(`view-${viewId}`);
    if (activeContainer) activeContainer.classList.add('active');

    const titles = {
      dashboards: 'Painel & Métricas de Receita',
      deals: 'Funil de Vendas Enterprise',
      contacts: 'Contatos & Base de Leads',
      inbox: 'Caixa de Entrada Omnichannel'
    };
    const titleEl = document.getElementById('topbar-title');
    if (titleEl && titles[viewId]) {
      titleEl.textContent = titles[viewId];
    }
  }

  // 2. Renderização do Dashboard
  function renderDashboard() {
    const m = data && data.metrics;
    if (!m) return;
    const mrrEl = document.getElementById('metric-mrr');
    if (mrrEl) mrrEl.textContent = formatBRL(m.mrr);
    const pipeEl = document.getElementById('metric-pipeline');
    if (pipeEl) pipeEl.textContent = formatBRL(m.pipelineTotal);
    const dealsEl = document.getElementById('metric-deals-count');
    if (dealsEl) dealsEl.textContent = m.dealsCount;
    const winEl = document.getElementById('metric-win-rate');
    if (winEl) winEl.textContent = m.winRate;
  }

  // 3. Renderização de Deals / Funil
  function renderDeals() {
    const container = document.getElementById('deals-view-content');
    if (!container) return;

    if (dealViewMode === 'kanban') {
      renderKanban(container);
    } else {
      renderDealsList(container);
    }
  }

  function renderKanban(container) {
    const pipeline = data.pipelines[0];
    let html = `<div class="kanban-board">`;

    pipeline.stages.forEach(stage => {
      const stageTotal = stage.deals.reduce((acc, d) => acc + d.value, 0);
      html += `
        <div class="kanban-column" data-stage-id="${stage.id}">
          <div class="column-header" style="border-top-color: ${stage.color};">
            <div class="column-title-wrap">
              <span class="column-title">${stage.name}</span>
              <span class="column-count">${stage.deals.length}</span>
            </div>
            <div class="column-total-value">${formatBRL(stageTotal)}</div>
          </div>
          <div class="cards-container" data-stage-id="${stage.id}">
            ${stage.deals.map(deal => createDealCardHtml(deal)).join('')}
          </div>
        </div>
      `;
    });

    html += `</div>`;
    container.innerHTML = html;
    setupDragAndDrop();
  }

  function createDealCardHtml(deal) {
    return `
      <div class="deal-card" draggable="true" data-deal-id="${deal.id}">
        <div class="deal-title">${deal.title}</div>
        <div class="deal-company">${deal.company} • ${deal.contact}</div>
        <div class="deal-footer">
          <span class="deal-value">${formatBRL(deal.value)}</span>
          <span class="priority-tag ${deal.priority}">${deal.priority}</span>
        </div>
      </div>
    `;
  }

  function renderDealsList(container) {
    const pipeline = data.pipelines[0];
    const allDeals = pipeline.stages.flatMap(s => s.deals.map(d => ({ ...d, stageName: s.name })));

    let html = `
      <div class="data-table-card">
        <table class="data-table">
          <thead>
            <tr>
              <th>Negócio</th>
              <th>Empresa & Contato</th>
              <th>Estágio Atual</th>
              <th>Valor Previsto</th>
              <th>Prioridade</th>
            </tr>
          </thead>
          <tbody>
            ${allDeals.map(d => `
              <tr>
                <td><strong>${d.title}</strong></td>
                <td>${d.company} (${d.contact})</td>
                <td><span class="chip-tag">${d.stageName}</span></td>
                <td><strong style="font-family: var(--font-family-mono);">${formatBRL(d.value)}</strong></td>
                <td><span class="priority-tag ${d.priority}">${d.priority}</span></td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
    container.innerHTML = html;
  }

  // 4. Drag and Drop Nativo
  function setupDragAndDrop() {
    const cards = document.querySelectorAll('.deal-card');
    const dropzones = document.querySelectorAll('.cards-container');

    cards.forEach(card => {
      card.addEventListener('dragstart', (e) => {
        card.classList.add('dragging');
        e.dataTransfer.setData('text/plain', card.getAttribute('data-deal-id'));
      });

      card.addEventListener('dragend', () => {
        card.classList.remove('dragging');
      });
    });

    dropzones.forEach(zone => {
      zone.addEventListener('dragover', (e) => {
        e.preventDefault();
        zone.style.backgroundColor = 'var(--color-surface-card)';
      });

      zone.addEventListener('dragleave', () => {
        zone.style.backgroundColor = '';
      });

      zone.addEventListener('drop', (e) => {
        e.preventDefault();
        zone.style.backgroundColor = '';
        const dealId = e.dataTransfer.getData('text/plain');
        const targetStageId = parseInt(zone.getAttribute('data-stage-id'), 10);

        moveDeal(dealId, targetStageId);
      });
    });
  }

  function moveDeal(dealId, targetStageId) {
    const pipeline = data.pipelines[0];
    let movedDeal = null;

    pipeline.stages.forEach(stage => {
      const idx = stage.deals.findIndex(d => d.id === dealId);
      if (idx !== -1) {
        movedDeal = stage.deals.splice(idx, 1)[0];
      }
    });

    if (movedDeal) {
      const targetStage = pipeline.stages.find(s => s.id === targetStageId);
      if (targetStage) {
        targetStage.deals.unshift(movedDeal);
        renderDeals();
      }
    }
  }

  // 5. Contatos & Busca
  function renderContacts() {
    const tbody = document.getElementById('contacts-table-body');
    const searchInput = document.getElementById('contacts-search');
    if (!tbody) return;

    const renderRows = (items) => {
      tbody.innerHTML = items.map(c => `
        <tr>
          <td>
            <div style="font-weight: var(--font-weight-semibold);">${c.name}</div>
            <div style="font-size: var(--font-size-xs); color: var(--color-text-secondary);">${c.email}</div>
          </td>
          <td>${c.company}</td>
          <td>${c.phone}</td>
          <td>
            ${c.tags.map(t => `<span class="chip-tag">${t}</span>`).join('')}
          </td>
          <td><strong style="color: var(--color-brand-primary);">${c.score} pts</strong></td>
          <td><span style="font-size: var(--font-size-xs); color: var(--color-text-muted);">${c.lastActivity}</span></td>
        </tr>
      `).join('');
    };

    renderRows(data.contacts);

    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        const filtered = data.contacts.filter(c =>
          c.name.toLowerCase().includes(query) ||
          c.email.toLowerCase().includes(query) ||
          c.company.toLowerCase().includes(query)
        );
        renderRows(filtered);
      });
    }
  }

  // 6. Chat Omnichannel
  function renderChat() {
    const chatList = document.getElementById('chat-contacts-list');
    const chatMessages = document.getElementById('chat-messages-container');
    const chatInput = document.getElementById('chat-message-input');
    const chatSendBtn = document.getElementById('chat-send-btn');
    if (!chatList || !chatMessages) return;

    chatList.innerHTML = data.conversations.map(chat => `
      <div class="chat-list-item ${chat.id === activeChatId ? 'active' : ''}" data-chat-id="${chat.id}">
        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
          <strong style="font-size: var(--font-size-sm);">${chat.contactName}</strong>
          <span style="font-size: 11px; color: var(--color-text-muted);">${chat.lastTime}</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-size: var(--font-size-xs); color: var(--color-text-secondary); text-overflow: ellipsis; overflow: hidden; white-space: nowrap; max-width: 180px;">
            ${chat.messages[chat.messages.length - 1]?.text || ''}
          </span>
          <span class="chat-channel-badge ${chat.channel}">${chat.channel.toUpperCase()}</span>
        </div>
      </div>
    `).join('');

    chatList.querySelectorAll('.chat-list-item').forEach(item => {
      item.addEventListener('click', () => {
        activeChatId = item.getAttribute('data-chat-id');
        renderChat();
      });
    });

    const activeConversation = data.conversations.find(c => c.id === activeChatId);
    if (activeConversation) {
      document.getElementById('chat-header-name').textContent = activeConversation.contactName;
      document.getElementById('chat-header-company').textContent = activeConversation.company;
      document.getElementById('chat-header-badge').textContent = activeConversation.channel.toUpperCase();
      document.getElementById('chat-header-badge').className = `chat-channel-badge ${activeConversation.channel}`;

      chatMessages.innerHTML = activeConversation.messages.map(msg => `
        <div class="bubble ${msg.sender}">
          <div>${msg.text}</div>
          <div style="font-size: 10px; opacity: 0.7; text-align: right; margin-top: 4px;">${msg.time}</div>
        </div>
      `).join('');

      chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    const sendMessage = () => {
      const text = chatInput.value.trim();
      if (!text || !activeConversation) return;

      const now = new Date();
      const timeStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;

      activeConversation.messages.push({
        sender: 'user',
        text: text,
        time: timeStr
      });

      chatInput.value = '';
      renderChat();
    };

    if (chatSendBtn) chatSendBtn.onclick = sendMessage;
    if (chatInput) {
      chatInput.onkeydown = (e) => {
        if (e.key === 'Enter') sendMessage();
      };
    }
  }

  // 7. Modal Novo Negócio
  function setupModal() {
    const modal = document.getElementById('deal-modal');
    const openBtn = document.getElementById('open-create-deal-btn');
    const closeBtn = document.getElementById('close-modal-btn');
    const form = document.getElementById('create-deal-form');

    if (openBtn) openBtn.onclick = () => modal.classList.add('active');
    if (closeBtn) closeBtn.onclick = () => modal.classList.remove('active');

    if (form) {
      form.onsubmit = (e) => {
        e.preventDefault();
        const title = document.getElementById('deal-form-title').value;
        const company = document.getElementById('deal-form-company').value;
        const contact = document.getElementById('deal-form-contact').value;
        const value = parseFloat(document.getElementById('deal-form-value').value) || 10000;
        const stageId = parseInt(document.getElementById('deal-form-stage').value, 10);

        const newDeal = {
          id: `d-${Date.now()}`,
          title,
          company,
          contact,
          value,
          priority: 'alta',
          daysInStage: 0
        };

        const stage = data.pipelines[0].stages.find(s => s.id === stageId);
        if (stage) {
          stage.deals.unshift(newDeal);
          data.metrics.pipelineTotal += value;
          data.metrics.dealsCount += 1;
          renderDashboard();
          renderDeals();
        }

        form.reset();
        modal.classList.remove('active');
      };
    }
  }
});
