import React, { useState, useEffect, useCallback } from "react";
import { Truck, RefreshCw, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";
import { EmptyState } from "@/components/ui/EmptyState";

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
  status:
    | "ORDER_PLACED"
    | "PICKING_BIPADO"
    | "SEALED_READY"
    | "COURIER_ASSIGNED"
    | "IN_TRANSIT_LIVE"
    | "DELIVERED_VERIFIED";
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
  const [error, setError] = useState<string | null>(null);
  const [selectedOrder, setSelectedOrder] = useState<DentgoExpressOrder | null>(null);

  const fetchOrders = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/v1/dentgo/orders");
      if (!res.ok) {
        throw new Error(`Falha ao carregar entregas DENTGO (HTTP ${res.status})`);
      }
      const data = await res.json();
      const list = Array.isArray(data) ? data : data.orders || data.data || [];
      setOrders(list);
      if (list.length > 0 && !selectedOrder) {
        setSelectedOrder(list[0]);
      }
    } catch (err: any) {
      setError(err.message || "Erro ao consultar o cockpit logístico DENTGO.");
    } finally {
      setLoading(false);
    }
  }, [selectedOrder]);

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  return (
    <div className="w-full bg-surface-bg text-text-main min-h-screen p-6 font-sans">
      <div className="flex justify-between items-center mb-6 pb-4 border-b border-border">
        <div>
          <div className="flex items-center gap-2">
            <svg
              className="w-6 h-6 text-brand-primary"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
            </svg>
            <h1 className="text-xl font-bold tracking-tight text-text-main">
              DENTGO Express • Cockpit de Logística e Despacho Cirúrgico
            </h1>
          </div>
          <p className="text-xs text-text-secondary mt-1">
            Rastreamento last-mile em tempo real com controle inviolável de lacre térmico, PIN sanitário e POD no Cloudflare R2.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center px-3 py-1 text-xs font-semibold rounded-full bg-brand-navy-subtle text-brand-navy border border-border">
            Plantão Cirúrgico 24h Ativo
          </span>
          <Button variant="outline" size="sm" onClick={fetchOrders} className="gap-1.5">
            <RefreshCw className="w-3.5 h-3.5" />
            Atualizar
          </Button>
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2 space-y-3">
            <Skeleton className="h-24 w-full" />
            <Skeleton className="h-24 w-full" />
            <Skeleton className="h-24 w-full" />
          </div>
          <Skeleton className="h-64 w-full" />
        </div>
      ) : error ? (
        <div className="p-8 rounded-xl border border-status-danger/30 bg-status-danger-subtle/20 text-center">
          <div className="flex flex-col items-center gap-3">
            <AlertCircle className="w-8 h-8 text-status-danger" />
            <h3 className="text-sm font-semibold text-text-main">{error}</h3>
            <Button size="sm" onClick={fetchOrders} className="gap-1.5">
              <RefreshCw className="w-4 h-4" />
              Tentar Novamente
            </Button>
          </div>
        </div>
      ) : orders.length === 0 ? (
        <EmptyState
          icon={Truck}
          title="Nenhuma entrega de urgência em andamento"
          description="Os pedidos same-day (SLA 45 minutos) despachados a partir dos hubs regionais aparecerão neste cockpit."
          actionLabel="Recarregar Pedidos"
          onAction={fetchOrders}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2 space-y-4">
            <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wider">
              Entregas de Urgência em Andamento
            </h2>
            <div className="space-y-3">
              {orders.map((order) => (
                <div
                  key={order.id}
                  onClick={() => setSelectedOrder(order)}
                  className={`p-4 rounded-lg border transition-all cursor-pointer ${
                    selectedOrder?.id === order.id
                      ? "bg-surface-card border-brand-primary shadow-card"
                      : "bg-surface-card border-border hover:border-brand-primary/50"
                  }`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs text-brand-primary font-bold">
                        {order.id}
                      </span>
                      <span className="px-2 py-0.5 text-[11px] font-mono rounded bg-surface-bg text-text-secondary border border-border-subtle">
                        {order.customer_cro_uf}
                      </span>
                    </div>
                    <span
                      className={`text-[11px] font-bold px-2 py-0.5 rounded-full border ${
                        order.status === "DELIVERED_VERIFIED"
                          ? "bg-status-success-subtle text-status-success border-status-success/20"
                          : order.status === "IN_TRANSIT_LIVE"
                          ? "bg-brand-primary-subtle text-brand-primary border-brand-primary/20"
                          : "bg-brand-navy-subtle text-brand-navy border-border"
                      }`}
                    >
                      {order.status}
                    </span>
                  </div>

                  <p className="text-sm font-medium text-text-main mb-2">
                    {order.delivery_address}
                  </p>

                  <div className="flex items-center justify-between text-xs text-text-secondary pt-2 border-t border-border-subtle font-mono">
                    <span>Distância: {order.distance_km} km</span>
                    <span>ETA: ~{order.estimated_eta_minutes} min</span>
                    <span className="text-text-main font-semibold">
                      R$ {order.total_amount.toFixed(2)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-surface-card border border-border rounded-lg p-5 shadow-card">
            <h3 className="text-sm font-bold text-text-main mb-4">Inspeção de Custódia e Lacre</h3>
            {selectedOrder ? (
              <div className="space-y-4 text-xs">
                <div>
                  <span className="text-text-secondary block mb-1">Status da Remessa</span>
                  <span className="font-mono text-brand-navy font-bold text-sm">
                    {selectedOrder.status}
                  </span>
                </div>
                <div>
                  <span className="text-text-secondary block mb-1">Código do Lacre Físico</span>
                  <span className="font-mono text-text-main bg-surface-bg border border-border px-2 py-1 rounded inline-block">
                    {selectedOrder.seal_code || "Aguardando lacre"}
                  </span>
                </div>
                <div>
                  <span className="text-text-secondary block mb-1">
                    PIN de Desbloqueio (Cirurgião)
                  </span>
                  <span className="font-mono text-brand-primary font-bold text-base bg-brand-primary-subtle px-3 py-1.5 rounded inline-block border border-brand-primary/20">
                    {selectedOrder.delivery_pin || "----"}
                  </span>
                </div>
                <div>
                  <span className="text-text-secondary block mb-1">
                    Comprovante de Entrega POD (R2)
                  </span>
                  {selectedOrder.proof_of_delivery_r2_key ? (
                    <div className="p-2 bg-status-success-subtle border border-status-success/20 rounded font-mono text-status-success text-[11px]">
                      {selectedOrder.proof_of_delivery_r2_key}
                      <span className="block text-[10px] text-text-secondary mt-1">
                        Assinado por: {selectedOrder.recipient_signature_name}
                      </span>
                    </div>
                  ) : (
                    <span className="text-text-muted italic">
                      Pendente de assinatura/foto na chegada
                    </span>
                  )}
                </div>
              </div>
            ) : (
              <div className="h-48 flex items-center justify-center text-xs text-text-muted text-center">
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
