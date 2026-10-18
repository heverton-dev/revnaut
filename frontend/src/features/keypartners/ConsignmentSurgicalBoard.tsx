import React, { useState, useEffect } from 'react';

export interface SurgicalOrder {
  id: string;
  account_id: string;
  agreement_id: string;
  patient_identifier?: string;
  surgery_date: string;
  status: 'SOLICITADO_FIELD' | 'APROVADO_INSIDE' | 'EM_POSSE_CLINICA' | 'FATURADO_E_REPOSTO';
  field_consultant_id?: string;
  inside_analyst_id?: string;
  remitted_items_json: string;
  consumed_items_json: string;
  seal_photo_r2_key?: string;
  billing_order_id?: string;
}

export const ConsignmentSurgicalBoard: React.FC = () => {
  const [orders, setOrders] = useState<SurgicalOrder[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedOrder, setSelectedOrder] = useState<SurgicalOrder | null>(null);

  useEffect(() => {
    // Carrega dados iniciais simulados ou da API
    const initialOrders: SurgicalOrder[] = [
      {
        id: 'surg-8821a',
        account_id: '0f14ffff',
        agreement_id: 'kpa-99120',
        patient_identifier: 'Paciente Dr. André Mattos',
        surgery_date: '2026-11-12',
        status: 'SOLICITADO_FIELD',
        field_consultant_id: 'usr-field-01',
        remitted_items_json: '[{"product_name": "Implante Cone Morse 4.3x11.5", "quantity": 8, "batch_number": "LOTE-99"}]',
        consumed_items_json: '[]',
      },
      {
        id: 'surg-7742b',
        account_id: '0f14ffff',
        agreement_id: 'kpa-44312',
        patient_identifier: 'Dra. Camila Nogueira - Maxilar',
        surgery_date: '2026-11-08',
        status: 'APROVADO_INSIDE',
        field_consultant_id: 'usr-field-02',
        inside_analyst_id: 'usr-inside-01',
        remitted_items_json: '[{"product_name": "Kit Cirúrgico Guiado GM", "quantity": 1, "batch_number": "KIT-01"}]',
        consumed_items_json: '[]',
      },
      {
        id: 'surg-6619c',
        account_id: '0f14ffff',
        agreement_id: 'kpa-12009',
        patient_identifier: 'Cirurgia Protocolo Carga Imediata',
        surgery_date: '2026-11-04',
        status: 'EM_POSSE_CLINICA',
        field_consultant_id: 'usr-field-01',
        inside_analyst_id: 'usr-inside-02',
        remitted_items_json: '[{"product_name": "Implante Grand Morse 3.5x13", "quantity": 12, "batch_number": "LOTE-GM12"}]',
        consumed_items_json: '[]',
      },
      {
        id: 'surg-5510d',
        account_id: '0f14ffff',
        agreement_id: 'kpa-33201',
        patient_identifier: 'Hospital Odonto Cirúrgico',
        surgery_date: '2026-10-30',
        status: 'FATURADO_E_REPOSTO',
        field_consultant_id: 'usr-field-03',
        inside_analyst_id: 'usr-inside-01',
        remitted_items_json: '[{"product_name": "Implante CM 3.75x10", "quantity": 6, "batch_number": "LOTE-A1"}]',
        consumed_items_json: '[{"product_name": "Implante CM 3.75x10", "quantity": 2, "batch_number": "LOTE-A1"}]',
        seal_photo_r2_key: 'seals/surg-5510d/lacre.jpg',
        billing_order_id: 'ped-cfop-88123',
      }
    ];
    setOrders(initialOrders);
    setLoading(false);
  }, []);

  const columns: { id: SurgicalOrder['status']; title: string }[] = [
    { id: 'SOLICITADO_FIELD', title: 'Solicitado pelo Consultor' },
    { id: 'APROVADO_INSIDE', title: 'Aprovado (Backoffice)' },
    { id: 'EM_POSSE_CLINICA', title: 'Em Posse da Clínica' },
    { id: 'FATURADO_E_REPOSTO', title: 'Faturado & Reposto (CFOP 5.113)' },
  ];

  const handleApprove = (orderId: string) => {
    setOrders(prev => prev.map(o => o.id === orderId ? { ...o, status: 'APROVADO_INSIDE' } : o));
  };

  const handleDispatch = (orderId: string) => {
    setOrders(prev => prev.map(o => o.id === orderId ? { ...o, status: 'EM_POSSE_CLINICA' } : o));
  };

  return (
    <div className="w-full bg-[var(--color-bg-primary)] text-slate-100 min-h-screen p-6 font-sans">
      <div className="flex justify-between items-center mb-6 pb-4 border-b border-white/10">
        <div>
          <div className="flex items-center gap-2">
            <svg className="w-6 h-6 text-orange-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
              <rect x="8" y="2" width="8" height="4" rx="1" ry="1" />
            </svg>
            <h1 className="text-xl font-bold tracking-tight">KeyPartners • Cockpit de Consignação Cirúrgica</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Gestão integrada Field Sales + Inside Sales com custódia sanitária ANVISA e conciliação pós-operatória.
          </p>
        </div>
        <div className="flex gap-2">
          <span className="inline-flex items-center px-3 py-1 text-xs font-semibold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            CFOP 5.113 / 6.113 Ativo
          </span>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-400 text-sm">Carregando painel cirúrgico...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {columns.map(col => {
            const colOrders = orders.filter(o => o.status === col.id);
            return (
              <div key={col.id} className="bg-[var(--color-bg-secondary)] border border-white/5 rounded-lg p-3 flex flex-col min-h-[500px]">
                <div className="flex justify-between items-center mb-3 pb-2 border-b border-white/5">
                  <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">{col.title}</span>
                  <span className="px-2 py-0.5 text-xs bg-white/5 text-slate-400 rounded-full font-mono">{colOrders.length}</span>
                </div>
                <div className="flex-1 space-y-3 overflow-y-auto">
                  {colOrders.map(order => (
                    <div
                      key={order.id}
                      onClick={() => setSelectedOrder(order)}
                      className="p-3 bg-[var(--color-bg-elevated)] hover:bg-slate-800 border border-white/5 hover:border-orange-500/40 rounded-md cursor-pointer transition-all shadow-sm"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <span className="text-xs font-mono text-orange-400 font-semibold">{order.id}</span>
                        <span className="text-[11px] text-slate-400 font-mono">{order.surgery_date}</span>
                      </div>
                      <h4 className="text-sm font-medium text-slate-200 mb-2">{order.patient_identifier || 'Paciente Sem Identificação'}</h4>
                      
                      {order.status === 'SOLICITADO_FIELD' && (
                        <button
                          onClick={(e) => { e.stopPropagation(); handleApprove(order.id); }}
                          className="w-full mt-2 py-1.5 px-3 bg-orange-600 hover:bg-orange-500 text-white text-xs font-semibold rounded transition-colors flex items-center justify-center gap-1.5"
                        >
                          <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <polyline points="20 6 9 17 4 12" />
                          </svg>
                          Aprovar Remessa
                        </button>
                      )}

                      {order.status === 'APROVADO_INSIDE' && (
                        <button
                          onClick={(e) => { e.stopPropagation(); handleDispatch(order.id); }}
                          className="w-full mt-2 py-1.5 px-3 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded transition-colors flex items-center justify-center gap-1.5"
                        >
                          <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <line x1="5" y1="12" x2="19" y2="12" />
                            <polyline points="12 5 19 12 12 19" />
                          </svg>
                          Despachar Maleta
                        </button>
                      )}

                      {order.status === 'FATURADO_E_REPOSTO' && (
                        <div className="mt-2 text-[11px] text-emerald-400 font-mono bg-emerald-500/10 p-1.5 rounded border border-emerald-500/20">
                          {order.billing_order_id}
                        </div>
                      )}
                    </div>
                  ))}
                  {colOrders.length === 0 && (
                    <div className="h-24 flex items-center justify-center border border-dashed border-white/5 rounded text-xs text-slate-500">
                      Vazio
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {selectedOrder && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-[var(--color-bg-secondary)] border border-white/10 rounded-xl max-w-lg w-full p-6 shadow-2xl">
            <div className="flex justify-between items-center pb-3 border-b border-white/10">
              <h3 className="text-base font-bold text-white">Detalhes da Ordem Cirúrgica</h3>
              <button
                onClick={() => setSelectedOrder(null)}
                className="text-slate-400 hover:text-white"
              >
                <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="6" />
                </svg>
              </button>
            </div>
            <div className="py-4 space-y-3 text-sm">
              <div>
                <span className="text-xs text-slate-400 block">ID da Ordem</span>
                <span className="font-mono text-orange-400">{selectedOrder.id}</span>
              </div>
              <div>
                <span className="text-xs text-slate-400 block">Paciente / Procedimento</span>
                <span className="text-slate-200">{selectedOrder.patient_identifier}</span>
              </div>
              <div>
                <span className="text-xs text-slate-400 block">Grade Remetida</span>
                <pre className="mt-1 p-2 bg-[var(--color-bg-primary)] rounded text-xs font-mono text-cyan-300 overflow-x-auto border border-white/5">
                  {selectedOrder.remitted_items_json}
                </pre>
              </div>
              {selectedOrder.seal_photo_r2_key && (
                <div>
                  <span className="text-xs text-slate-400 block">Comprovante de Lacre (Cloudflare R2)</span>
                  <span className="font-mono text-xs text-emerald-400">{selectedOrder.seal_photo_r2_key}</span>
                </div>
              )}
            </div>
            <div className="flex justify-end pt-3 border-t border-white/10">
              <button
                onClick={() => setSelectedOrder(null)}
                className="px-4 py-2 bg-white/10 hover:bg-white/15 text-white text-xs font-semibold rounded"
              >
                Fechar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ConsignmentSurgicalBoard;
