/**
 * RevNault Dental Ops — RBAC & Organogram Module (ES Module)
 * Renderização e gestão de árvores de equipes, divisões e presets.
 */

import { api } from './api-client.js';

export async function loadHierarchyTree(accountId = '0f14ffff') {
  const res = await api.get(`/hierarchy/teams?account_id=${accountId}`);
  if (!res.ok) throw new Error('Falha ao carregar árvore de equipes');
  return res.json();
}

export async function loadBusinessUnits(accountId = '0f14ffff') {
  const res = await api.get(`/hierarchy/business-units?account_id=${accountId}`);
  if (!res.ok) throw new Error('Falha ao carregar unidades de negócio');
  return res.json();
}

export async function applyPreset(presetName, accountId = '0f14ffff') {
  const res = await api.post(`/hierarchy/presets/apply?account_id=${accountId}`, {
    preset_name: presetName
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Falha ao aplicar preset');
  }
  return res.json();
}

export async function updateTeamParent(teamId, newParentId, accountId = '0f14ffff') {
  const res = await api.put(`/hierarchy/teams/${teamId}/parent?account_id=${accountId}`, {
    parent_id: newParentId
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Falha ao atualizar hierarquia');
  }
  return res.json();
}
