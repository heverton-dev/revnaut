/**
 * Revnaut Dental Ops — Landing Page Builder Module (ES Module)
 * Motor visual GrapesJS integrado com publicação estática no Cloudflare R2
 * e conformidade com o Código de Ética Odontológica (CFO Resolução 196/2019).
 */

import { apiRequest } from './api-client.js';

export async function fetchTemplates() {
  return await apiRequest('/campaigns/landing-pages/templates');
}

export async function createLandingPage(payload) {
  return await apiRequest('/campaigns/landing-pages', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function updateLandingPage(pageId, payload) {
  return await apiRequest(`/campaigns/landing-pages/${pageId}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  });
}

export async function publishLandingToR2(pageId) {
  return await apiRequest(`/campaigns/landing-pages/${pageId}/publish`, {
    method: 'PUT',
  });
}

export function initLandingBuilder(containerId, options = {}) {
  if (typeof window === 'undefined' || !window.grapesjs) {
    console.warn('[LandingBuilder] GrapesJS core library not loaded in window context.');
    return null;
  }

  const editor = window.grapesjs.init({
    container: `#${containerId}`,
    height: options.height || '600px',
    width: 'auto',
    storageManager: false,
    blockManager: {
      appendTo: options.blocksContainerId ? `#${options.blocksContainerId}` : undefined,
      blocks: [
        {
          id: 'cfo-responsible',
          label: 'Responsável Técnico CFO',
          category: 'Odontologia CFO',
          content: `<div class="cfo-banner" style="padding: 12px; background: #f8fafc; border-top: 2px solid #0284c7; font-size: 12px; text-align: center; color: #475569;">
            <p>Responsável Técnico: ${options.cfoName || 'Dr. Cirurgião-Dentista'} — ${options.cfoCro || 'CRO-SP 00000'} | Conforme Resolução CFO 196/2019 e Art. 43 do CEO</p>
          </div>`,
        },
        {
          id: 'cro-verified-input',
          label: 'Input CRO/UF Verificado',
          category: 'Formulários Odonto',
          content: `<div style="margin-bottom: 12px;">
            <label style="display: block; font-size: 13px; font-weight: 600; margin-bottom: 4px;">CRO/UF do Profissional</label>
            <input type="text" name="cro" placeholder="CRO-SP 123456" style="width: 100%; padding: 8px 12px; border: 1px solid #cbd5e1; border-radius: 6px;" required />
          </div>`,
        },
        {
          id: 'implant-system-select',
          label: 'Seletor de Sistema de Implante',
          category: 'Formulários Odonto',
          content: `<div style="margin-bottom: 12px;">
            <label style="display: block; font-size: 13px; font-weight: 600; margin-bottom: 4px;">Linha de Implantes Utilizada</label>
            <select name="implant_system" style="width: 100%; padding: 8px 12px; border: 1px solid #cbd5e1; border-radius: 6px;">
              <option value="Cone Morse">Cone Morse Cônica de Alta Estabilidade</option>
              <option value="Hexágono Externo">Hexágono Externo (HE)</option>
              <option value="Hexágono Interno">Hexágono Interno (HI)</option>
              <option value="Zircônia">Implante Cerâmico Monobloco (Zircônia)</option>
            </select>
          </div>`,
        },
        {
          id: 'surgical-kit-hero',
          label: 'Hero Kit Cirúrgico',
          category: 'Estruturas',
          content: `<header style="background: linear-gradient(135deg, #0f172a, #1e293b); color: #fff; padding: 60px 20px; text-align: center;">
            <h1 style="color: #38bdf8; font-size: 32px; font-weight: bold; margin-bottom: 12px;">Reabilitação com Cirurgia Guiada de Alta Precisão</h1>
            <p style="color: #94a3b8; max-width: 600px; margin: 0 auto;">Planejamento digital com anilhas de precisão e torque controlado para estabilidade primária imediata.</p>
          </header>`,
        },
      ],
    },
  });

  return editor;
}
