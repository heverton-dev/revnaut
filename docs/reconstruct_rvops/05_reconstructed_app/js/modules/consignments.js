/**
 * Revnaut Dental Ops — Consignments & Surgical Kits Module (ES Module)
 * Rastreabilidade de caixas cirúrgicas consignadas e reposições de implantes.
 */

import { api } from './api-client.js';

export async function fetchConsignments(contactId = null) {
  const query = contactId ? `?contact_id=${contactId}` : '';
  const res = await api.get(`/consignments${query}`);
  if (!res.ok) {
    // Modo resiliente se a rota ainda não estiver montada
    return [];
  }
  return res.json();
}

export async function updateConsignmentStatus(boxId, status) {
  const res = await api.put(`/consignments/${boxId}/status`, { status });
  if (!res.ok) throw new Error('Falha ao atualizar status da caixa consignada');
  return res.json();
}
