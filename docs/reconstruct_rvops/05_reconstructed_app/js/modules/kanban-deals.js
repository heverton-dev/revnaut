/**
 * Revnaut Dental Ops — Kanban & Pipeline Module (ES Module)
 * Gestão visual de oportunidades, movimentação de estágios e travas de crédito.
 */

import { api } from './api-client.js';

export async function fetchPipelineDeals(pipelineId = 1) {
  const res = await api.get(`/deals?pipeline_id=${pipelineId}`);
  if (!res.ok) throw new Error('Falha ao carregar oportunidades');
  return res.json();
}

export async function moveDealStage(dealId, newStageId) {
  const res = await api.put(`/deals/${dealId}/stage`, {
    stage_id: newStageId
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Não foi possível mover o negócio');
  }
  return res.json();
}

export async function createDeal(dealData) {
  const res = await api.post('/deals', dealData);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Falha ao criar oportunidade comercial');
  }
  return res.json();
}

export async function approveDealCredit(dealId) {
  const res = await api.post(`/deals/${dealId}/approve-credit`, {});
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Falha ao aprovar limite de crédito');
  }
  return res.json();
}
