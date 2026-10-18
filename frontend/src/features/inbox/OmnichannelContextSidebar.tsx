// -*- coding: utf-8 -*-
/**
 * OmnichannelContextSidebar.tsx
 * Sidebar de Contexto 360° para Chatwoot & Central Omnichannel REVNAULT
 * Inviolable Law #14: Zero Emojis. Strictly inline SVG icons.
 */

import React, { useState, useEffect } from 'react';

interface ContactInfo {
  id: number;
  name: string;
  email?: string;
  phone?: string;
  cro_uf?: string;
  specialty?: string;
  score?: number;
}

interface AgreementInfo {
  id: string;
  partner_name: string;
  partner_cro_uf: string;
  tier: string;
  credit_limit: number;
  used_credit: number;
  available_credit: number;
}

interface ConsignmentKit {
  id: string;
  serial_number: string;
  name: string;
  status: string;
  created_at: string;
}

interface DentgoOrder {
  id: string;
  status: string;
  estimated_eta_minutes: number;
  delivery_address: string;
  total_amount: number;
}

interface Context360Data {
  contact_identifier: string;
  contact?: ContactInfo;
  cro_uf?: string;
  agreement?: AgreementInfo;
  consignments_in_field: ConsignmentKit[];
  active_dentgo_orders: DentgoOrder[];
  is_synced_chatwoot: boolean;
}

interface OmnichannelContextSidebarProps {
  contactIdentifier: string;
  onOpenSosVideo?: (croUf: string) => void;
}

export const OmnichannelContextSidebar: React.FC<OmnichannelContextSidebarProps> = ({
  contactIdentifier,
  onOpenSosVideo
}) => {
  const [data, setData] = useState<Context360Data | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [syncing, setSyncing] = useState<boolean>(false);

  useEffect(() => {
    let isMounted = true;
    async function fetchContext() {
      if (!contactIdentifier) return;
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`/api/v1/omnichannel/context/${encodeURIComponent(contactIdentifier)}`);
        if (!res.ok) throw new Error('Falha ao carregar contexto 360 do cirurgiao');
        const json = await res.json();
        if (isMounted) setData(json);
      } catch (err: any) {
        if (isMounted) setError(err.message || 'Erro de conexao');
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    fetchContext();
    return () => { isMounted = false; };
  }, [contactIdentifier]);

  const handleSyncChatwoot = async () => {
    if (!data?.contact?.id) return;
    setSyncing(true);
    try {
      const res = await fetch(`/api/v1/omnichannel/chatwoot/sync-contact/${data.contact.id}`, {
        method: 'POST'
      });
      if (!res.ok) throw new Error('Falha na sincronizacao com Chatwoot');
    } catch (err: any) {
      alert(err.message);
    } finally {
      setSyncing(false);
    }
  };

  if (loading) {
    return (
      <aside className="w-80 border-l border-slate-800 bg-slate-900 p-4 text-slate-200">
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
          <svg className="h-4 w-4 animate-spin text-cyan-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" strokeDasharray="32" strokeDashoffset="12" />
          </svg>
          Carregando Contexto 360...
        </div>
      </aside>
    );
  }

  if (error || !data) {
    return (
      <aside className="w-80 border-l border-slate-800 bg-slate-900 p-4 text-slate-400">
        <div className="flex items-center gap-2 text-rose-400 text-sm">
          <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          {error || 'Sem dados de contexto disponiveis'}
        </div>
      </aside>
    );
  }

  const { contact, agreement, consignments_in_field, active_dentgo_orders, cro_uf } = data;
  const creditPct = agreement && agreement.credit_limit > 0
    ? Math.min(100, Math.round((agreement.used_credit / agreement.credit_limit) * 100))
    : 0;

  return (
    <aside className="w-88 border-l border-slate-800 bg-slate-950/90 backdrop-blur-md p-4 text-slate-200 flex flex-col gap-5 overflow-y-auto">
      {/* Header Contexto */}
      <div className="flex items-start justify-between border-b border-slate-800/80 pb-3">
        <div className="flex items-center gap-2.5">
          <div className="rounded-lg bg-cyan-950/60 p-2 border border-cyan-500/30 text-cyan-400">
            <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <polyline points="16 11 18 13 22 9" />
            </svg>
          </div>
          <div>
            <h2 className="text-sm font-semibold text-slate-100">{contact?.name || 'Cirurgiao Nao Identificado'}</h2>
            <div className="flex items-center gap-1.5 mt-0.5">
              <span className="font-mono text-xs text-cyan-400 font-bold bg-cyan-950/50 px-1.5 py-0.5 rounded border border-cyan-500/20">
                {cro_uf || 'SEM CRO'}
              </span>
              {contact?.score !== undefined && (
                <span className="font-mono text-xs text-amber-300 bg-amber-950/40 px-1.5 py-0.5 rounded border border-amber-500/20">
                  Score {contact.score}
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Acoes Rápidas de Atendimento */}
      <div className="grid grid-cols-2 gap-2">
        <button
          onClick={handleSyncChatwoot}
          disabled={syncing}
          className="flex items-center justify-center gap-1.5 py-1.5 px-2.5 rounded text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
        >
          <svg className="h-3.5 w-3.5 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="23 4 23 10 17 10" />
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
          </svg>
          {syncing ? 'Sincronizando...' : 'Sync Chatwoot'}
        </button>

        <button
          onClick={() => onOpenSosVideo && cro_uf && onOpenSosVideo(cro_uf)}
          className="flex items-center justify-center gap-1.5 py-1.5 px-2.5 rounded text-xs font-medium bg-rose-950/70 hover:bg-rose-900 text-rose-200 border border-rose-800/50 transition"
        >
          <svg className="h-3.5 w-3.5 text-rose-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polygon points="23 7 16 12 23 17 23 7" />
            <rect x="1" y="5" width="15" height="14" rx="2" ry="2" />
          </svg>
          Video SOS
        </button>
      </div>

      {/* Pilar 1: KeyPartners Consignacao & Credito */}
      <div className="rounded-lg bg-slate-900/80 border border-slate-800 p-3 flex flex-col gap-2.5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-slate-300">
            <svg className="h-4 w-4 text-cyan-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="2" y="7" width="20" height="14" rx="2" ry="2" />
              <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
            </svg>
            KeyPartners • Credito
          </div>
          {agreement && (
            <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-indigo-950/80 text-indigo-300 border border-indigo-700/40">
              {agreement.tier}
            </span>
          )}
        </div>

        {agreement ? (
          <>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div>
                <span className="text-[11px] text-slate-400 block">Limite Total</span>
                <span className="font-mono font-semibold text-slate-100">
                  R$ {agreement.credit_limit.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                </span>
              </div>
              <div>
                <span className="text-[11px] text-slate-400 block">Disponivel</span>
                <span className="font-mono font-semibold text-emerald-400">
                  R$ {agreement.available_credit.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                </span>
              </div>
            </div>

            <div className="space-y-1">
              <div className="flex justify-between text-[10px] text-slate-400 font-mono">
                <span>Utilizado: R$ {agreement.used_credit.toLocaleString('pt-BR')}</span>
                <span>{creditPct}%</span>
              </div>
              <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all ${
                    creditPct > 80 ? 'bg-rose-500' : creditPct > 50 ? 'bg-amber-400' : 'bg-cyan-400'
                  }`}
                  style={{ width: `${creditPct}%` }}
                />
              </div>
            </div>
          </>
        ) : (
          <p className="text-xs text-slate-400 italic">Sem acordo de consignacao formalizado</p>
        )}
      </div>

      {/* Pilar 2: Kits Consignados em Campo */}
      <div className="rounded-lg bg-slate-900/80 border border-slate-800 p-3 flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-slate-300">
            <svg className="h-4 w-4 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
            </svg>
            Kits em Custodia ({consignments_in_field.length})
          </div>
        </div>

        {consignments_in_field.length > 0 ? (
          <div className="space-y-2 max-h-36 overflow-y-auto">
            {consignments_in_field.map(kit => (
              <div key={kit.id || kit.serial_number} className="rounded border border-slate-800 bg-slate-950/60 p-2 text-xs">
                <div className="flex justify-between items-center">
                  <span className="font-mono font-bold text-cyan-300">{kit.serial_number}</span>
                  <span className="text-[10px] px-1 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800/40">
                    EM CAMPO
                  </span>
                </div>
                <p className="text-slate-300 text-[11px] truncate mt-0.5">{kit.name}</p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-slate-400 italic">Nenhum kit consignado sob custodia no momento</p>
        )}
      </div>

      {/* Pilar 3: Entregas Expressas DENTGO */}
      <div className="rounded-lg bg-slate-900/80 border border-slate-800 p-3 flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-slate-300">
            <svg className="h-4 w-4 text-amber-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="1" y="3" width="15" height="13" />
              <polygon points="16 8 20 8 23 11 23 16 16 16 16 8" />
              <circle cx="5.5" cy="18.5" r="2.5" />
              <circle cx="18.5" cy="18.5" r="2.5" />
            </svg>
            DENTGO Express ({active_dentgo_orders.length})
          </div>
        </div>

        {active_dentgo_orders.length > 0 ? (
          <div className="space-y-2 max-h-36 overflow-y-auto">
            {active_dentgo_orders.map(ord => (
              <div key={ord.id} className="rounded border border-slate-800 bg-slate-950/60 p-2 text-xs">
                <div className="flex justify-between items-center">
                  <span className="font-mono font-bold text-amber-300">{ord.id}</span>
                  <span className="font-mono text-[10px] text-slate-300">
                    ETA ~{ord.estimated_eta_minutes} min
                  </span>
                </div>
                <div className="flex justify-between items-center mt-1">
                  <span className="text-[10px] px-1 py-0.5 rounded bg-cyan-950/60 text-cyan-300 border border-cyan-800/40">
                    {ord.status}
                  </span>
                  <span className="font-mono text-slate-200">
                    R$ {ord.total_amount?.toFixed(2)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-slate-400 italic">Nenhuma entrega de urgencia em rota</p>
        )}
      </div>
    </aside>
  );
};
