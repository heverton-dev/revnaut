import React, { useState, useEffect } from 'react';

export interface DentgoExpressOrder {
  id: string;
  hub_id: string;
  customer_cro_uf: string;
  delivery_address: string;
  distance_km: number;
  estimated_eta_minutes: number;
  subtotal: number;
  urgency_fee: number;
  total_amount: number;
  status: 'ORDER_PLACED' | 'PICKING_BIPADO' | 'SEALED_READY' | 'COURIER_ASSIGNED' | 'IN_TRANSIT_LIVE' | 'DELIVERED_VERIFIED';
  courier_id?: string;
  seal_code?: string;
  delivery_pin?: string;
  proof_of_delivery_r2_key?: string;
  recipient_signature_name?: string;
  created_at: string;
}

export const DentgoExpressCockpit: React.FC = () => {
  const [orders, setOrders] = useState<DentgoExpressOrder[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedOrder, setSelectedOrder] = useState<DentgoExpressOrder | null>(null);

  useEffect(() => {
    const mockOrders: DentgoExpressOrder[] = [
      {
        id: 'dord-9901a',
        hub_id: 'hub-jardins-01',
        customer_cro_uf: 'CRO-SP-109283',
        delivery_address: 'Av. Paulista, 1578 - Bela Vista, SP',
        distance_km: 2.8,
        estimated_eta_minutes: 25,
        subtotal: 1800.0,
        urgency_fee: 44.8,
        total_amount: 1844.8,
        status: 'IN_TRANSIT_LIVE',
        courier_id: 'courier-flash-02',
        seal_code: 'LACRE-SP-8821',
        delivery_pin: '4821',
        created_at: '2026-10-18T00:30:00Z',
      },
      {
        id: 'dord-8812b',
        hub_id: 'hub-pinheiros-02',
        customer_cro_uf: 'CRO-SP-99120',
        delivery_address: 'Rua dos Pinheiros, 850 - Pinheiros, SP',
        distance_km: 1.4,
        estimated_eta_minutes: 20,
        subtotal: 950.0,
        urgency_fee: 39.9,
        total_amount: 989.9,
        status: 'SEALED_READY',
        seal_code: 'LACRE-PIN-110',
        delivery_pin: '3319',
        created_at: '2026-10-18T00:35:00Z',
      },
      {
        id: 'dord-7723c',
        hub_id: 'hub-moema-03',
        customer_cro_uf: 'CRO-SP-44551',
        delivery_address: 'Av. Ibirapuera, 2100 - Moema, SP',
        distance_km: 3.2,
        estimated_eta_minutes: 30,
        subtotal: 2700.0,
        urgency_fee: 46.2,
        total_amount: 2746.2,
        status: 'DELIVERED_VERIFIED',
        courier_id: 'courier-exp-09',
        seal_code: 'LACRE-MOE-772',
        delivery_pin: '9012',
        proof_of_delivery_r2_key: 'pod/dord-7723c/lacre_assinado.jpg',
        recipient_signature_name: 'Dra. Vanessa Lima',
        created_at: '2026-10-18T00:10:00Z',
      }
    ];
    setOrders(mockOrders);
    setLoading(false);
  }, []);

  return (
    <div className="w-full bg-[#090d16] text-slate-100 min-h-screen p-6 font-sans">
      <div className="flex justify-between items-center mb-6 pb-4 border-b border-white/10">
        <div>
          <div className="flex items-center gap-2">
            <svg className="w-6 h-6 text-orange-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
            </svg>
            <h1 className="text-xl font-bold tracking-tight">DENTGO Express • Cockpit de Logística e Despacho Cirúrgico</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Rastreamento last-mile em tempo real com controle inviolável de lacre térmico, PIN sanitário e POD no Cloudflare R2.
          </p>
        </div>
        <div className="flex gap-2">
          <span className="inline-flex items-center px-3 py-1 text-xs font-semibold rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            Plantão Cirúrgico 24h Ativo
          </span>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-400 text-sm">Carregando cockpit logístico...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2 space-y-4">
            <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">Entregas de Urgência em Andamento</h2>
            <div className="space-y-3">
              {orders.map(order => (
                <div
                  key={order.id}
                  onClick={() => setSelectedOrder(order)}
                  className={`p-4 rounded-lg border transition-all cursor-pointer ${
                    selectedOrder?.id === order.id
                      ? 'bg-[#151c2c] border-orange-500/50 shadow-lg shadow-orange-500/10'
                      : 'bg-[#101622] border-white/5 hover:border-white/15'
                  }`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs text-orange-400 font-bold">{order.id}</span>
                      <span className="px-2 py-0.5 text-[11px] font-mono rounded bg-white/5 text-slate-300">
                        {order.customer_cro_uf}
                      </span>
                    </div>
                    <span className={`text-[11px] font-bold px-2 py-0.5 rounded-full border ${
                      order.status === 'DELIVERED_VERIFIED'
                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                        : order.status === 'IN_TRANSIT_LIVE'
                        ? 'bg-orange-500/10 text-orange-400 border-orange-500/20'
                        : 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20'
                    }`}>
                      {order.status}
                    </span>
                  </div>

                  <p className="text-sm font-medium text-slate-200 mb-2">{order.delivery_address}</p>

                  <div className="flex items-center justify-between text-xs text-slate-400 pt-2 border-t border-white/5 font-mono">
                    <span>Distância: {order.distance_km} km</span>
                    <span>ETA: ~{order.estimated_eta_minutes} min</span>
                    <span className="text-slate-200 font-semibold">R$ {order.total_amount.toFixed(2)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-[#101622] border border-white/5 rounded-lg p-5">
            <h3 className="text-sm font-bold text-white mb-4">Inspeção de Custódia e Lacre</h3>
            {selectedOrder ? (
              <div className="space-y-4 text-xs">
                <div>
                  <span className="text-slate-400 block mb-1">Status da Remessa</span>
                  <span className="font-mono text-cyan-400 font-bold text-sm">{selectedOrder.status}</span>
                </div>
                <div>
                  <span className="text-slate-400 block mb-1">Código do Lacre Físico</span>
                  <span className="font-mono text-slate-200 bg-white/5 px-2 py-1 rounded inline-block">
                    {selectedOrder.seal_code || 'Aguardando lacre'}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block mb-1">PIN de Desbloqueio (Cirurgião)</span>
                  <span className="font-mono text-orange-400 font-bold text-base bg-orange-500/10 px-3 py-1.5 rounded inline-block border border-orange-500/20">
                    {selectedOrder.delivery_pin || '----'}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block mb-1">Comprovante de Entrega POD (R2)</span>
                  {selectedOrder.proof_of_delivery_r2_key ? (
                    <div className="p-2 bg-emerald-500/10 border border-emerald-500/20 rounded font-mono text-emerald-400 text-[11px]">
                      {selectedOrder.proof_of_delivery_r2_key}
                      <span className="block text-[10px] text-slate-400 mt-1">Assinado por: {selectedOrder.recipient_signature_name}</span>
                    </div>
                  ) : (
                    <span className="text-slate-500 italic">Pendente de assinatura/foto na chegada</span>
                  )}
                </div>
              </div>
            ) : (
              <div className="h-48 flex items-center justify-center text-xs text-slate-500 text-center">
                Selecione uma ordem ao lado para inspecionar lacre e comprovante de custódia.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default DentgoExpressCockpit;
