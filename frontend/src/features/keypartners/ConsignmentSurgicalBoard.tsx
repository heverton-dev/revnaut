import React, { useState, useEffect, useCallback } from "react";
import { Package, RefreshCw, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";
import { EmptyState } from "@/components/ui/EmptyState";

export interface SurgicalOrder {
  id: string;
  account_id: string;
  agreement_id: string;
  patient_identifier?: string;
  surgery_date: string;
  status: "SOLICITADO_FIELD" | "APROVADO_INSIDE" | "EM_POSSE_CLINICA" | "FATURADO_E_REPOSTO";
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
  const [error, setError] = useState<string | null>(null);
  const [selectedOrder, setSelectedOrder] = useState<SurgicalOrder | null>(null);

  const fetchSurgicalOrders = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/v1/keypartners/surgical-orders");
      if (!res.ok) {
        throw new Error(`Falha ao carregar ordens cirúrgicas (HTTP ${res.status})`);
      }
      const data = await res.json();
      setOrders(Array.isArray(data) ? data : data.orders || data.data || []);
    } catch (err: any) {
      setError(err.message || "Erro ao consultar o painel cirúrgico KeyPartners.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSurgicalOrders();
  }, [fetchSurgicalOrders]);

  const columns: { id: SurgicalOrder["status"]; title: string }[] = [
    { id: "SOLICITADO_FIELD", title: "Solicitado pelo Consultor" },
    { id: "APROVADO_INSIDE", title: "Aprovado (Backoffice)" },
    { id: "EM_POSSE_CLINICA", title: "Em Posse da Clínica" },
    { id: "FATURADO_E_REPOSTO", title: "Faturado & Reposto (CFOP 5.113)" },
  ];

  const handleApprove = async (orderId: string) => {
    try {
      const res = await fetch(`/api/v1/keypartners/surgical-orders/${orderId}/approve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ inside_analyst_id: "usr-inside-01" }),
      });
      if (res.ok) {
        setOrders((prev) =>
          prev.map((o) => (o.id === orderId ? { ...o, status: "APROVADO_INSIDE" } : o))
        );
      }
    } catch {
      // erro tratado na camada de rede
    }
  };

  const handleDispatch = async (orderId: string) => {
    try {
      const res = await fetch(`/api/v1/keypartners/surgical-orders/${orderId}/dispatch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ seal_photo_r2_key: `seals/${orderId}/lacre.jpg` }),
      });
      if (res.ok) {
        setOrders((prev) =>
          prev.map((o) => (o.id === orderId ? { ...o, status: "EM_POSSE_CLINICA" } : o))
        );
      }
    } catch {
      // erro tratado na camada de rede
    }
  };

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
              <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
              <rect x="8" y="2" width="8" height="4" rx="1" ry="1" />
            </svg>
            <h1 className="text-xl font-bold tracking-tight text-text-main">
              KeyPartners • Cockpit de Consignação Cirúrgica
            </h1>
          </div>
          <p className="text-xs text-text-secondary mt-1">
            Gestão integrada Field Sales + Inside Sales com custódia sanitária ANVISA e conciliação pós-operatória.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center px-3 py-1 text-xs font-semibold rounded-full bg-status-success-subtle text-status-success border border-status-success/20">
            CFOP 5.113 / 6.113 Ativo
          </span>
          <Button variant="outline" size="sm" onClick={fetchSurgicalOrders} className="gap-1.5">
            <RefreshCw className="w-3.5 h-3.5" />
            Atualizar
          </Button>
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {columns.map((col) => (
            <div key={col.id} className="bg-surface-card border border-border rounded-lg p-3 space-y-3">
              <Skeleton className="h-5 w-40" />
              <Skeleton className="h-24 w-full" />
              <Skeleton className="h-24 w-full" />
            </div>
          ))}
        </div>
      ) : error ? (
        <div className="p-8 rounded-xl border border-status-danger/30 bg-status-danger-subtle/20 text-center">
          <div className="flex flex-col items-center gap-3">
            <AlertCircle className="w-8 h-8 text-status-danger" />
            <h3 className="text-sm font-semibold text-text-main">{error}</h3>
            <Button size="sm" onClick={fetchSurgicalOrders} className="gap-1.5">
              <RefreshCw className="w-4 h-4" />
              Tentar Novamente
            </Button>
          </div>
        </div>
      ) : orders.length === 0 ? (
        <EmptyState
          icon={Package}
          title="Nenhuma ordem cirúrgica em consignação ativa"
          description="As solicitações de maletas cirúrgicas cone morse e kits guiados abertas pelos consultores de campo serão listadas neste quadro."
          actionLabel="Recarregar Ordens"
          onAction={fetchSurgicalOrders}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {columns.map((col) => {
            const colOrders = orders.filter((o) => o.status === col.id);
            return (
              <div
                key={col.id}
                className="bg-surface-card border border-border rounded-lg p-3 flex flex-col min-h-[500px] shadow-card"
              >
                <div className="flex justify-between items-center mb-3 pb-2 border-b border-border-subtle">
                  <span className="text-xs font-semibold text-text-secondary uppercase tracking-wider">
                    {col.title}
                  </span>
                  <span className="px-2 py-0.5 text-xs bg-surface-bg text-text-secondary rounded-full font-mono">
                    {colOrders.length}
                  </span>
                </div>
                <div className="flex-1 space-y-3 overflow-y-auto">
                  {colOrders.map((order) => (
                    <div
                      key={order.id}
                      onClick={() => setSelectedOrder(order)}
                      className="p-3 bg-surface-bg hover:bg-surface-card border border-border hover:border-brand-primary rounded-md cursor-pointer transition-all shadow-card"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <span className="text-xs font-mono text-brand-primary font-semibold">
                          {order.id}
                        </span>
                        <span className="text-[11px] text-text-secondary font-mono">
                          {order.surgery_date}
                        </span>
                      </div>
                      <h4 className="text-sm font-medium text-text-main mb-2">
                        {order.patient_identifier || "Paciente Sem Identificação"}
                      </h4>

                      {order.status === "SOLICITADO_FIELD" && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleApprove(order.id);
                          }}
                          className="w-full mt-2 py-1.5 px-3 bg-brand-primary hover:bg-brand-primary-hover text-text-inverse text-xs font-semibold rounded transition-colors flex items-center justify-center gap-1.5"
                        >
                          <svg
                            className="w-3.5 h-3.5"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                          >
                            <polyline points="20 6 9 17 4 12" />
                          </svg>
                          Aprovar Remessa
                        </button>
                      )}

                      {order.status === "APROVADO_INSIDE" && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDispatch(order.id);
                          }}
                          className="w-full mt-2 py-1.5 px-3 bg-status-success text-text-inverse text-xs font-semibold rounded transition-colors flex items-center justify-center gap-1.5"
                        >
                          <svg
                            className="w-3.5 h-3.5"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                          >
                            <line x1="5" y1="12" x2="19" y2="12" />
                            <polyline points="12 5 19 12 12 19" />
                          </svg>
                          Despachar Maleta
                        </button>
                      )}

                      {order.status === "FATURADO_E_REPOSTO" && (
                        <div className="mt-2 text-[11px] text-status-success font-mono bg-status-success-subtle p-1.5 rounded border border-status-success/20">
                          {order.billing_order_id}
                        </div>
                      )}
                    </div>
                  ))}
                  {colOrders.length === 0 && (
                    <div className="h-24 flex items-center justify-center border border-dashed border-border rounded text-xs text-text-muted">
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
        <div className="fixed inset-0 bg-text-main/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-surface-card border border-border rounded-xl max-w-lg w-full p-6 shadow-modal">
            <div className="flex justify-between items-center pb-3 border-b border-border">
              <h3 className="text-base font-bold text-text-main">Detalhes da Ordem Cirúrgica</h3>
              <button
                onClick={() => setSelectedOrder(null)}
                className="text-text-secondary hover:text-text-main"
              >
                <svg
                  className="w-5 h-5"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="6" />
                </svg>
              </button>
            </div>
            <div className="py-4 space-y-3 text-sm">
              <div>
                <span className="text-xs text-text-secondary block">ID da Ordem</span>
                <span className="font-mono text-brand-primary">{selectedOrder.id}</span>
              </div>
              <div>
                <span className="text-xs text-text-secondary block">Paciente / Procedimento</span>
                <span className="text-text-main">{selectedOrder.patient_identifier}</span>
              </div>
              <div>
                <span className="text-xs text-text-secondary block">Grade Remetida</span>
                <pre className="mt-1 p-2 bg-surface-bg rounded text-xs font-mono text-brand-navy overflow-x-auto border border-border">
                  {selectedOrder.remitted_items_json}
                </pre>
              </div>
              {selectedOrder.seal_photo_r2_key && (
                <div>
                  <span className="text-xs text-text-secondary block">
                    Comprovante de Lacre (Cloudflare R2)
                  </span>
                  <span className="font-mono text-xs text-status-success">
                    {selectedOrder.seal_photo_r2_key}
                  </span>
                </div>
              )}
            </div>
            <div className="flex justify-end pt-3 border-t border-border">
              <button
                onClick={() => setSelectedOrder(null)}
                className="px-4 py-2 bg-surface-bg hover:bg-surface-card text-text-main border border-border text-xs font-semibold rounded"
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
