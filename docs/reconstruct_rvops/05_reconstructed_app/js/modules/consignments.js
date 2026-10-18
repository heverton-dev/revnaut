/**
 * Revnaut Dental Ops — Consignments & Surgical Kits Module (ES Module)
 * Rastreabilidade de caixas cirúrgicas consignadas e reposições de implantes.
 * KeyPartners: Ciclo cirúrgico completo e conciliação pós-operatória.
 */

import { api } from './api-client.js';

export async function fetchConsignments(contactId = null) {
  const query = contactId ? `?contact_id=${contactId}` : '';
  const res = await api.get(`/consignments${query}`);
  if (!res.ok) {
    return [];
  }
  return res.json();
}

export async function updateConsignmentStatus(boxId, status) {
  const res = await api.put(`/consignments/${boxId}/status`, { status });
  if (!res.ok) throw new Error('Falha ao atualizar status da caixa consignada');
  return res.json();
}

export async function fetchSurgicalOrder(orderId) {
  const res = await api.get(`/keypartners/surgical-orders/${orderId}`);
  if (!res.ok) throw new Error('Falha ao buscar ordem cirúrgica');
  return res.json();
}

export async function createSurgicalOrder(orderPayload) {
  const res = await api.post('/keypartners/surgical-orders', orderPayload);
  if (!res.ok) throw new Error('Falha ao solicitar remessa cirúrgica');
  return res.json();
}

export async function approveSurgicalOrder(orderId, insideAnalystId = 'usr-inside-01') {
  const res = await api.post(`/keypartners/surgical-orders/${orderId}/approve`, {
    inside_analyst_id: insideAnalystId
  });
  if (!res.ok) throw new Error('Falha ao aprovar remessa cirúrgica');
  return res.json();
}

export async function dispatchSurgicalOrder(orderId) {
  const res = await api.post(`/keypartners/surgical-orders/${orderId}/dispatch`, {});
  if (!res.ok) throw new Error('Falha ao despachar maleta cirúrgica');
  return res.json();
}

export async function reportSurgicalPostop(orderId, postopData) {
  const res = await api.post(`/keypartners/surgical-orders/${orderId}/postop-report`, postopData);
  if (!res.ok) throw new Error('Falha ao registrar conciliação pós-operatória');
  return res.json();
}

export async function fetchCustodySummary(agreementId) {
  const res = await api.get(`/keypartners/agreements/${agreementId}/custody-summary`);
  if (!res.ok) throw new Error('Falha ao obter extrato de custódia');
  return res.json();
}
