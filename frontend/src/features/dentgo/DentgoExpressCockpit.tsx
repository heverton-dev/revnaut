import React, { useState, useEffect, useCallback } from "react";
import {
  Truck,
  RefreshCw,
  AlertCircle,
  Plus,
  CheckCircle2,
  Package,
  ShieldCheck,
  Search,
  DollarSign,
  Tag,
  Zap,
  Barcode,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";
import { EmptyState } from "@/components/ui/EmptyState";
import { Tabs } from "@/components/ui/Tabs";
import { R2DirectUploader } from "@/components/shared/R2DirectUploader";
import { DentgoRadarMap } from "./DentgoRadarMap";

export interface DentgoExpressOrder {
  id: string;
  hub_id: string;
  customer_cro_uf: string;
  delivery_address: string;
  delivery_lat?: number;
  delivery_lng?: number;
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

export interface HubItem {
  id: string;
  name: string;
  cnpj: string;
  latitude: number;
  longitude: number;
  coverage_radius_km: number;
  on_duty_schedule: string;
  is_active: number;
  created_at: string;
}

export interface FefoDeal {
  id: string;
  hub_id: string;
  hub_name: string;
  inventory_id: string;
  product_id: string;
  product_name: string;
  batch_number: string;
  original_quantity: number;
  available_quantity: number;
  original_unit_price: number;
  discount_percentage: number;
  flash_unit_price: number;
  sterilization_expiry_date: string;
  months_to_expire: number;
  target_surgeons_count: number;
  status: string;
  checkout_one_click_url: string;
}

export interface FinancialSplitItem {
  id: string;
  order_id: string;
  gross_amount: number;
  items_amount: number;
  delivery_fee_total: number;
  platform_take_rate_pct: number;
  platform_fee_amount: number;
  courier_net_payout: number;
  seller_net_payout: number;
  payment_method: string;
  settlement_status: string;
  created_at: string;
}

// TICKET-DENTGO-01: Signature Pad interativo para recibo de entrega (POD)
const DeliverySignaturePad: React.FC<{
  onSigned: (dataUrl: string) => void;
  onClear: () => void;
  hasSignature: boolean;
}> = ({ onSigned, onClear, hasSignature }) => {
  const canvasRef = React.useRef<HTMLCanvasElement>(null);
  const drawingRef = React.useRef<boolean>(false);

  React.useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.lineWidth = 2;
    ctx.lineCap = "round";
    ctx.strokeStyle = "hsl(220, 20%, 12%)";
    ctx.fillStyle = "hsl(0, 0%, 100%)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }, []);

  const getPos = (e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current!;
    const rect = canvas.getBoundingClientRect();
    const clientX = "touches" in e ? e.touches[0].clientX : e.clientX;
    const clientY = "touches" in e ? e.touches[0].clientY : e.clientY;
    return {
      x: ((clientX - rect.left) / rect.width) * canvas.width,
      y: ((clientY - rect.top) / rect.height) * canvas.height,
    };
  };

  const start = (e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>) => {
    e.preventDefault();
    drawingRef.current = true;
    const ctx = canvasRef.current?.getContext("2d");
    const p = getPos(e);
    ctx?.beginPath();
    ctx?.moveTo(p.x, p.y);
  };

  const move = (e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>) => {
    if (!drawingRef.current) return;
    e.preventDefault();
    const ctx = canvasRef.current?.getContext("2d");
    const p = getPos(e);
    ctx?.lineTo(p.x, p.y);
    ctx?.stroke();
  };

  const end = () => {
    if (!drawingRef.current) return;
    drawingRef.current = false;
    const canvas = canvasRef.current;
    if (canvas) onSigned(canvas.toDataURL("image/png"));
  };

  const clear = () => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    if (canvas && ctx) {
      ctx.fillStyle = "hsl(0, 0%, 100%)";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
    }
    onClear();
  };

  return (
    <div className="space-y-1">
      <label className="text-[10px] text-text-secondary block">
        Assinatura Digital do Recebedor (desenhe abaixo):
      </label>
      <canvas
        ref={canvasRef}
        width={400}
        height={120}
        className="w-full h-24 rounded border border-border bg-surface-card cursor-crosshair touch-none"
        onMouseDown={start}
        onMouseMove={move}
        onMouseUp={end}
        onMouseLeave={end}
        onTouchStart={start}
        onTouchMove={move}
        onTouchEnd={end}
      />
      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={clear}
          className="text-[10px] text-text-secondary hover:text-text-main underline"
        >
          Limpar assinatura
        </button>
        {hasSignature && (
          <span className="text-[10px] font-medium text-status-success">Assinatura capturada</span>
        )}
      </div>
    </div>
  );
};

export const DentgoExpressCockpit: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>("orders");

  // Tab 1: Orders
  const [orders, setOrders] = useState<DentgoExpressOrder[]>([]);
  const [loadingOrders, setLoadingOrders] = useState<boolean>(true);
  const [ordersError, setOrdersError] = useState<string | null>(null);
  const [selectedOrder, setSelectedOrder] = useState<DentgoExpressOrder | null>(null);

  // New Order Modal
  const [showCheckoutModal, setShowCheckoutModal] = useState<boolean>(false);
  const [newOrderCro, setNewOrderCro] = useState<string>("SP-12345");
  const [newOrderAddress, setNewOrderAddress] = useState<string>("Av. Paulista 1000, Bela Vista, São Paulo - SP");
  const [newOrderLat, setNewOrderLat] = useState<number>(-23.5616);
  const [newOrderLng, setNewOrderLng] = useState<number>(-46.656);
  const [newOrderProductId, setNewOrderProductId] = useState<string>("IMP-CM-4311");
  const [newOrderQty, setNewOrderQty] = useState<number>(2);
  const [newOrderVoucher, setNewOrderVoucher] = useState<string>("");
  const [cartItems, setCartItems] = useState<Array<{ product_id: string; quantity: number }>>([]);
  const [voucherError, setVoucherError] = useState<string | null>(null);
  const [podPhotoKey, setPodPhotoKey] = useState<string | null>(null);
  const [checkingOut, setCheckingOut] = useState<boolean>(false);

  // Transition stage inputs
  const [pickingBarcode, setPickingBarcode] = useState<string>("7891234567890123");
  const [sealCode, setSealCode] = useState<string>("LACRE-DENTGO-9921");
  const [courierId, setCourierId] = useState<string>("courier-motoboy-04");
  const [deliveryPin, setDeliveryPin] = useState<string>("");
  const [deliveryRecipient, setDeliveryRecipient] = useState<string>("Dra. Camila Soares (Auxiliar)");
  const [transitionLoading, setTransitionLoading] = useState<boolean>(false);

  // TICKET-DENTGO-01: Signature Pad digital do recibo de entrega
  const [deliverySignatureDataUrl, setDeliverySignatureDataUrl] = useState<string | null>(null);

  // Tab 2: Hubs & Haversine
  const [hubs, setHubs] = useState<HubItem[]>([]);
  const [loadingHubs, setLoadingHubs] = useState<boolean>(false);
  const [showHubModal, setShowHubModal] = useState<boolean>(false);
  const [newHubName, setNewHubName] = useState<string>("DENTGO Hub Zona Sul SP");
  const [newHubCnpj, setNewHubCnpj] = useState<string>("44555666000188");
  const [newHubLat, setNewHubLat] = useState<number>(-23.605);
  const [newHubLng, setNewHubLng] = useState<number>(-46.678);
  const [newHubRadius, setNewHubRadius] = useState<number>(35.0);
  const [creatingHub, setCreatingHub] = useState<boolean>(false);

  // Hub Inventory
  const [inventoryHubId, setInventoryHubId] = useState<string>("");
  const [showInventoryModal, setShowInventoryModal] = useState<boolean>(false);
  const [invProductId, setInvProductId] = useState<string>("IMP-CM-4311");
  const [invProductName, setInvProductName] = useState<string>("Implante Cone Morse 4.3x11mm");
  const [invAnvisa, setInvAnvisa] = useState<string>("ANVISA-80123456789");
  const [invBatch, setInvBatch] = useState<string>("LOTE-HUB-2026-01");
  const [invQty, setInvQty] = useState<number>(25);
  const [invPrice, setInvPrice] = useState<number>(420.0);
  const [invExpiry, setInvExpiry] = useState<string>("2028-06-30");
  const [addingInventory, setAddingInventory] = useState<boolean>(false);
  const [inventoryFeedback, setInventoryFeedback] = useState<string | null>(null);

  // Emergency Search (Haversine)
  const [searchLat, setSearchLat] = useState<number>(-23.5616);
  const [searchLng, setSearchLng] = useState<number>(-46.656);
  const [searchProductId, setSearchProductId] = useState<string>("IMP-CM-4311");
  const [searchQty, setSearchQty] = useState<number>(2);
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searchingEmergency, setSearchingEmergency] = useState<boolean>(false);

  // Tab 3: FEFO Flash Deals
  const [fefoDeals, setFefoDeals] = useState<FefoDeal[]>([]);
  const [loadingFefo, setLoadingFefo] = useState<boolean>(false);
  const [scanningFefo, setScanningFefo] = useState<boolean>(false);
  const [fefoFeedback, setFefoFeedback] = useState<string | null>(null);
  const [selectedFefoDeal, setSelectedFefoDeal] = useState<FefoDeal | null>(null);
  const [reserveCro, setReserveCro] = useState<string>("12345-SP");
  const [reserveName, setReserveName] = useState<string>("Dr. Rafael Campinas");
  const [reserveQty, setReserveQty] = useState<number>(2);
  const [reservingDeal, setReservingDeal] = useState<boolean>(false);

  // Tab 4: Financial Split
  const [splits, setSplits] = useState<FinancialSplitItem[]>([]);
  const [loadingSplits, setLoadingSplits] = useState<boolean>(false);
  const [splitOrderId, setSplitOrderId] = useState<string>("");
  const [splitTakeRate, setSplitTakeRate] = useState<number>(5.0);
  const [splitMethod, setSplitMethod] = useState<string>("PIX_INSTANT");
  const [processingSplit, setProcessingSplit] = useState<boolean>(false);
  const [splitResult, setSplitResult] = useState<FinancialSplitItem | null>(null);
  const [orderSplitData, setOrderSplitData] = useState<FinancialSplitItem | null>(null);
  const [fetchingOrderSplit, setFetchingOrderSplit] = useState<boolean>(false);
  const [splitFeedback, setSplitFeedback] = useState<string | null>(null);

  const handleFetchOrderSplit = async (targetId?: string) => {
    const oid = targetId || selectedOrder?.id || splitOrderId;
    if (!oid) return;
    setFetchingOrderSplit(true);
    setSplitFeedback(null);
    try {
      const res = await fetch(`/api/v1/dentgo/orders/${oid}/split`);
      if (res.ok) {
        const data = await res.json();
        setOrderSplitData(data);
        setSplitResult(data);
      } else {
        const err = await res.json().catch(() => ({}));
        setSplitFeedback(err.detail || "Split ainda não gerado para este pedido.");
      }
    } catch (e: any) {
      setSplitFeedback(e.message || "Erro ao consultar split");
    } finally {
      setFetchingOrderSplit(false);
    }
  };

  // Fetch Orders
  const fetchOrders = useCallback(async () => {
    setLoadingOrders(true);
    setOrdersError(null);
    try {
      const res = await fetch("/api/v1/dentgo/orders");
      if (!res.ok) {
        throw new Error(`Falha ao carregar entregas DENTGO (HTTP ${res.status})`);
      }
      const data = await res.json();
      const list = Array.isArray(data) ? data : data.orders || [];
      setOrders(list);
      if (list.length > 0) {
        setSelectedOrder((prev) => (prev ? list.find((o: DentgoExpressOrder) => o.id === prev.id) || list[0] : list[0]));
      }
    } catch (err: any) {
      setOrdersError(err.message || "Erro ao consultar o cockpit logístico DENTGO.");
    } finally {
      setLoadingOrders(false);
    }
  }, []);

  // Fetch Hubs
  const fetchHubs = useCallback(async () => {
    setLoadingHubs(true);
    try {
      const res = await fetch("/api/v1/dentgo/hubs");
      if (res.ok) {
        const data = await res.json();
        const list = Array.isArray(data) ? data : [];
        setHubs(list);
        if (list.length > 0 && !inventoryHubId) {
          setInventoryHubId(list[0].id);
        }
      }
    } catch {
      // Fallback
    } finally {
      setLoadingHubs(false);
    }
  }, [inventoryHubId]);

  // Fetch FEFO
  const fetchFefoDeals = useCallback(async () => {
    setLoadingFefo(true);
    try {
      const res = await fetch("/api/v1/dentgo/fefo/deals");
      if (res.ok) {
        const data = await res.json();
        setFefoDeals(Array.isArray(data) ? data : []);
      }
    } catch {
      // Fallback
    } finally {
      setLoadingFefo(false);
    }
  }, []);

  // Fetch Splits
  const fetchSplits = useCallback(async () => {
    setLoadingSplits(true);
    try {
      const res = await fetch("/api/v1/dentgo/splits");
      if (res.ok) {
        const data = await res.json();
        setSplits(Array.isArray(data) ? data : []);
      }
    } catch {
      // Fallback
    } finally {
      setLoadingSplits(false);
    }
  }, []);

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  useEffect(() => {
    if (activeTab === "hubs") {
      fetchHubs();
    } else if (activeTab === "fefo") {
      fetchFefoDeals();
    } else if (activeTab === "split") {
      fetchSplits();
    }
  }, [activeTab, fetchHubs, fetchFefoDeals, fetchSplits]);

  // Order Stage Transitions
  const handleTransition = async (endpoint: string, payload: any) => {
    if (!selectedOrder) return;
    setTransitionLoading(true);
    try {
      const res = await fetch(`/api/v1/dentgo/orders/${selectedOrder.id}/${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        const updated: DentgoExpressOrder = await res.json();
        setSelectedOrder(updated);
        setOrders((prev) => prev.map((o) => (o.id === updated.id ? updated : o)));
      }
    } catch {
      // erro
    } finally {
      setTransitionLoading(false);
    }
  };

  const handleAddCartItem = () => {
    const qty = Math.max(1, Number(newOrderQty) || 1);
    const pid = newOrderProductId.trim();
    if (!pid) return;
    setCartItems((prev) => {
      const existing = prev.find((i) => i.product_id === pid);
      if (existing) {
        return prev.map((i) => (i.product_id === pid ? { ...i, quantity: i.quantity + qty } : i));
      }
      return [...prev, { product_id: pid, quantity: qty }];
    });
  };

  const handleCreateExpressOrder = async () => {
    const voucher = newOrderVoucher.trim().toUpperCase();
    if (voucher && !/^(MOEDA-EXPRESS|DENTGO-EXPRESS)-[A-Z0-9]+$/.test(voucher)) {
      setVoucherError("Voucher inválido. Use o formato MOEDA-EXPRESS-* ou DENTGO-EXPRESS-*.");
      return;
    }
    setVoucherError(null);
    setCheckingOut(true);
    try {
      const items =
        cartItems.length > 0
          ? cartItems
          : [{ product_id: newOrderProductId, quantity: Number(newOrderQty) }];
      const body = JSON.stringify({
        customer_cro_uf: newOrderCro,
        delivery_address: newOrderAddress,
        delivery_lat: Number(newOrderLat),
        delivery_lng: Number(newOrderLng),
        items,
        voucher_code: voucher || undefined,
        account_id: "0f14ffff",
      });
      const res = await fetch("/api/v1/dentgo/orders/express", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body,
      });
      if (res.ok) {
        setShowCheckoutModal(false);
        setCartItems([]);
        setNewOrderVoucher("");
        fetchOrders();
      } else {
        const err = await res.json().catch(() => ({}));
        setVoucherError(typeof err.detail === "string" ? err.detail : "Falha ao despachar o pedido.");
      }
    } catch {
      setVoucherError("Falha de rede ao despachar o pedido.");
    } finally {
      setCheckingOut(false);
    }
  };

  const handleCreateHub = async () => {
    setCreatingHub(true);
    try {
      const res = await fetch("/api/v1/dentgo/hubs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: newHubName,
          cnpj: newHubCnpj,
          latitude: Number(newHubLat),
          longitude: Number(newHubLng),
          coverage_radius_km: Number(newHubRadius),
          on_duty_schedule: "24h",
          account_id: "0f14ffff",
        }),
      });
      if (res.ok) {
        setShowHubModal(false);
        fetchHubs();
      }
    } catch {
      // erro
    } finally {
      setCreatingHub(false);
    }
  };

  const handleAddHubInventory = async () => {
    if (!inventoryHubId) return;
    setAddingInventory(true);
    setInventoryFeedback(null);
    try {
      const res = await fetch(`/api/v1/dentgo/hubs/${inventoryHubId}/inventory`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          product_id: invProductId,
          product_name: invProductName,
          anvisa_reg: invAnvisa,
          batch_number: invBatch,
          quantity_available: Number(invQty),
          unit_price: Number(invPrice),
          sterilization_expiry_date: invExpiry,
          account_id: "0f14ffff",
        }),
      });
      if (res.ok) {
        setInventoryFeedback("Lote cirúrgico abastecido com sucesso no Hub!");
        setShowInventoryModal(false);
      }
    } catch (e: any) {
      setInventoryFeedback(`Erro: ${e.message}`);
    } finally {
      setAddingInventory(false);
    }
  };

  const handleEmergencySearch = async () => {
    setSearchingEmergency(true);
    try {
      const res = await fetch("/api/v1/dentgo/hubs/search-emergency", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          delivery_lat: Number(searchLat),
          delivery_lng: Number(searchLng),
          product_id: searchProductId,
          required_qty: Number(searchQty),
          account_id: "0f14ffff",
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setSearchResults(Array.isArray(data) ? data : []);
      }
    } catch {
      // erro
    } finally {
      setSearchingEmergency(false);
    }
  };

  const handleRunFefoScan = async () => {
    setScanningFefo(true);
    setFefoFeedback(null);
    try {
      const res = await fetch("/api/v1/dentgo/fefo/scan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          discount_percentage: 35.0,
          max_target_surgeons: 50,
          radius_km: 50.0,
          account_id: "0f14ffff",
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setFefoFeedback(
          `Varredura concluída: ${data.scanned_batches} lotes escaneados, ${data.created_deals_count} ofertas criadas!`
        );
        fetchFefoDeals();
      }
    } catch (e: any) {
      setFefoFeedback(`Falha: ${e.message}`);
    } finally {
      setScanningFefo(false);
    }
  };

  const handleReserveFefoDeal = async () => {
    if (!selectedFefoDeal) return;
    setReservingDeal(true);
    try {
      const res = await fetch(`/api/v1/dentgo/fefo/deals/${selectedFefoDeal.id}/reserve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          surgeon_cro_uf: reserveCro,
          surgeon_name: reserveName,
          quantity: Number(reserveQty),
          account_id: "0f14ffff",
        }),
      });
      if (res.ok) {
        setSelectedFefoDeal(null);
        fetchFefoDeals();
      }
    } catch {
      // erro
    } finally {
      setReservingDeal(false);
    }
  };

  const handleProcessSplit = async () => {
    if (!splitOrderId.trim()) return;
    setProcessingSplit(true);
    try {
      const res = await fetch(`/api/v1/dentgo/orders/${splitOrderId}/split`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          platform_take_rate_pct: Number(splitTakeRate),
          payment_method: splitMethod,
          account_id: "0f14ffff",
        }),
      });
      if (res.ok) {
        const data: FinancialSplitItem = await res.json();
        setSplitResult(data);
        fetchSplits();
      }
    } catch {
      // erro
    } finally {
      setProcessingSplit(false);
    }
  };

  const tabsConfig = [
    { id: "orders", label: "Despacho Rápido (45 min)" },
    { id: "hubs", label: "Busca de Estoque Mais Próximo" },
    { id: "fefo", label: "Ofertas de Lotes Próximos do Vencimento" },
    { id: "split", label: "Repasses e Custos de Entrega" },
  ];

  return (
    <div className="w-full space-y-6 font-sans text-text-main">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-border">
        <div>
          <div className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand-primary-subtle text-brand-primary border border-brand-primary/20">
              <Truck className="h-5 w-5" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-text-main">
                Entrega Rápida (45 min) • Logística e Despacho Cirúrgico
              </h1>
              <p className="text-xs text-text-secondary mt-0.5">
                Despacho prioritário, busca de estoque mais próximo, ofertas de lotes e controle de entregas.
              </p>
            </div>
          </div>
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

      {/* Tabs */}
      <Tabs tabs={tabsConfig} activeTab={activeTab} onChange={setActiveTab} />

      {/* TAB 1: Despacho Same-Day & 6 Estágios */}
      {activeTab === "orders" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs text-text-secondary font-medium">
              Monitoramento live das ordens cirúrgicas emergenciais (SLA 45 min)
            </span>
            <Button size="sm" onClick={() => setShowCheckoutModal(true)} className="gap-1.5">
              <Plus className="w-3.5 h-3.5" />
              + Novo Despacho Emergencial
            </Button>
          </div>

          {loadingOrders ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="md:col-span-2 space-y-3">
                <Skeleton className="h-24 w-full" />
                <Skeleton className="h-24 w-full" />
              </div>
              <Skeleton className="h-64 w-full" />
            </div>
          ) : ordersError ? (
            <div className="p-8 rounded-xl border border-status-danger/30 bg-status-danger-subtle/20 text-center">
              <div className="flex flex-col items-center gap-3">
                <AlertCircle className="w-8 h-8 text-status-danger" />
                <h3 className="text-sm font-semibold text-text-main">{ordersError}</h3>
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
              description="Cadastre um novo despacho emergencial same-day para iniciar a esteira."
              actionLabel="+ Novo Despacho Emergencial"
              onAction={() => setShowCheckoutModal(true)}
            />
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Orders List */}
              <div className="lg:col-span-2 space-y-3">
                {orders.map((order) => (
                  <div
                    key={order.id}
                    onClick={() => {
                      setSelectedOrder(order);
                      setSplitOrderId(order.id);
                    }}
                    className={`p-4 rounded-xl border transition-all cursor-pointer ${
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
                        <span className="px-2 py-0.5 text-[11px] font-mono rounded bg-surface-bg text-text-secondary border border-border">
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

                    <p className="text-xs font-medium text-text-main mb-2">
                      {order.delivery_address}
                    </p>

                    <div className="flex items-center justify-between text-xs text-text-secondary pt-2 border-t border-border font-mono">
                      <span>Distância: {order.distance_km} km</span>
                      <span>ETA: ~{order.estimated_eta_minutes} min</span>
                      <span className="text-text-main font-semibold">
                        R$ {order.total_amount.toFixed(2)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Side Stage Actions & Custody Panel */}
              <div className="lg:col-span-1 bg-surface-card border border-border rounded-xl p-5 shadow-card space-y-4">
                <h3 className="text-sm font-bold text-text-main border-b border-border pb-3">
                  Inspeção de Custódia & Transições de Estágio
                </h3>

                {selectedOrder ? (
                  <div className="space-y-4 text-xs">
                    <div>
                      <span className="text-text-secondary block mb-1">Status Atual:</span>
                      <span className="font-mono font-bold text-sm text-brand-primary">
                        {selectedOrder.status}
                      </span>
                    </div>

                    {/* Stage 1 -> 2: Picking */}
                    {selectedOrder.status === "ORDER_PLACED" && (
                      <div className="p-3 bg-surface-bg rounded-xl border border-border space-y-2">
                        <span className="font-bold text-text-main block">1. Bipar Picking ANVISA</span>
                        <input
                          type="text"
                          value={pickingBarcode}
                          onChange={(e) => setPickingBarcode(e.target.value)}
                          placeholder="Código de barras..."
                          className="w-full rounded border border-border bg-surface-card p-1.5 font-mono text-xs"
                        />
                        <Button
                          size="sm"
                          onClick={() => handleTransition("picking", { scanned_barcode: pickingBarcode })}
                          disabled={transitionLoading}
                          className="w-full gap-1.5"
                        >
                          <Barcode className="w-3.5 h-3.5" />
                          Confirmar Picking
                        </Button>
                      </div>
                    )}

                    {/* Stage 2 -> 3: Seal */}
                    {selectedOrder.status === "PICKING_BIPADO" && (
                      <div className="p-3 bg-surface-bg rounded-xl border border-border space-y-2">
                        <span className="font-bold text-text-main block">2. Lacrar Embalagem Térmica</span>
                        <input
                          type="text"
                          value={sealCode}
                          onChange={(e) => setSealCode(e.target.value)}
                          placeholder="Código do lacre..."
                          className="w-full rounded border border-border bg-surface-card p-1.5 font-mono text-xs"
                        />
                        <Button
                          size="sm"
                          onClick={() => handleTransition("seal", { seal_code: sealCode })}
                          disabled={transitionLoading}
                          className="w-full gap-1.5"
                        >
                          <ShieldCheck className="w-3.5 h-3.5" />
                          Lacrar Maleta & Gerar PIN
                        </Button>
                      </div>
                    )}

                    {/* Stage 3 -> 4: Assign Courier */}
                    {selectedOrder.status === "SEALED_READY" && (
                      <div className="p-3 bg-surface-bg rounded-xl border border-border space-y-2">
                        <span className="font-bold text-text-main block">3. Designar Entregador</span>
                        <input
                          type="text"
                          value={courierId}
                          onChange={(e) => setCourierId(e.target.value)}
                          placeholder="ID do entregador..."
                          className="w-full rounded border border-border bg-surface-card p-1.5 font-mono text-xs"
                        />
                        <Button
                          size="sm"
                          onClick={() => handleTransition("assign-courier", { courier_id: courierId })}
                          disabled={transitionLoading}
                          className="w-full gap-1.5"
                        >
                          <Truck className="w-3.5 h-3.5" />
                          Vincular Courier
                        </Button>
                      </div>
                    )}

                    {/* Stage 4 -> 5: Start Transit */}
                    {selectedOrder.status === "COURIER_ASSIGNED" && (
                      <div className="p-3 bg-surface-bg rounded-xl border border-border space-y-2">
                        <span className="font-bold text-text-main block">4. Iniciar Rota Express</span>
                        <Button
                          size="sm"
                          onClick={() => handleTransition("start-transit", {})}
                          disabled={transitionLoading}
                          className="w-full gap-1.5"
                        >
                          <Zap className="w-3.5 h-3.5" />
                          Iniciar Trânsito Live
                        </Button>
                      </div>
                    )}

                    {/* Stage 5 -> 6: Verify Delivery */}
                    {selectedOrder.status === "IN_TRANSIT_LIVE" && (
                      <div className="p-3 bg-surface-bg rounded-xl border border-border space-y-2">
                        <span className="font-bold text-text-main block">5. Confirmar Entrega (PIN & POD)</span>
                        <div>
                          <label className="text-[10px] text-text-secondary block mb-1">PIN 4 Dígitos:</label>
                          <input
                            type="text"
                            maxLength={4}
                            value={deliveryPin}
                            onChange={(e) => setDeliveryPin(e.target.value)}
                            placeholder="PIN informado pelo cliente"
                            className="w-full rounded border border-border bg-surface-card p-1.5 font-mono text-xs"
                          />
                        </div>
                        <div>
                          <label className="text-[10px] text-text-secondary block mb-1">Recebedor:</label>
                          <input
                            type="text"
                            value={deliveryRecipient}
                            onChange={(e) => setDeliveryRecipient(e.target.value)}
                            className="w-full rounded border border-border bg-surface-card p-1.5 text-xs"
                          />
                        </div>
                        <div>
                          <label className="text-[10px] text-text-secondary block mb-1">Foto de Comprovante de Entrega (POD):</label>
                          <R2DirectUploader
                            module="consignments"
                            accept=".png,.jpg,.jpeg"
                            onUploadComplete={(r) => setPodPhotoKey(r.key)}
                          />
                          {podPhotoKey && (
                            <span className="text-[10px] font-mono text-status-success break-all block mt-1">
                              POD anexado: {podPhotoKey}
                            </span>
                          )}
                        </div>
                        <DeliverySignaturePad
                          hasSignature={Boolean(deliverySignatureDataUrl)}
                          onSigned={(dataUrl) => setDeliverySignatureDataUrl(dataUrl)}
                          onClear={() => setDeliverySignatureDataUrl(null)}
                        />
                        <Button
                          size="sm"
                          onClick={() =>
                            handleTransition("verify-delivery", {
                              entered_pin: deliveryPin,
                              proof_photo_r2_key: podPhotoKey || `pod/${selectedOrder.id}/entrega.jpg`,
                              recipient_name: deliveryRecipient,
                              recipient_signature_data_url: deliverySignatureDataUrl || undefined,
                            })
                          }
                          disabled={transitionLoading || deliveryPin.length !== 4}
                          className="w-full gap-1.5"
                        >
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          Verificar PIN & Finalizar Entrega
                        </Button>
                      </div>
                    )}

                    {/* Details section */}
                    <div className="space-y-2 pt-2 border-t border-border">
                      <div>
                        <span className="text-text-secondary block mb-0.5">Lacre Térmico:</span>
                        <span className="font-mono text-text-main bg-surface-bg border border-border px-2 py-0.5 rounded inline-block">
                          {selectedOrder.seal_code || "Aguardando lacre"}
                        </span>
                      </div>
                      <div>
                        <span className="text-text-secondary block mb-0.5">PIN Sanitário Gerado:</span>
                        <span className="font-mono text-brand-primary font-bold text-sm bg-brand-primary-subtle px-2.5 py-1 rounded inline-block border border-brand-primary/20">
                          {selectedOrder.delivery_pin || "----"}
                        </span>
                      </div>
                      {selectedOrder.proof_of_delivery_r2_key && (
                        <div>
                          <span className="text-text-secondary block mb-0.5">Comprovante POD (R2):</span>
                          <span className="font-mono text-[11px] text-status-success block">
                            {selectedOrder.proof_of_delivery_r2_key}
                          </span>
                          <span className="text-[10px] text-text-muted">
                            Assinado: {selectedOrder.recipient_signature_name}
                          </span>
                        </div>
                      )}

                      {/* Split Query Action */}
                      <div className="pt-2 border-t border-border space-y-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleFetchOrderSplit(selectedOrder.id)}
                          disabled={fetchingOrderSplit}
                          className="w-full text-xs gap-1.5"
                        >
                          <DollarSign className="w-3.5 h-3.5" />
                          {fetchingOrderSplit ? "Consultando..." : "Consultar Split do Pedido (GET)"}
                        </Button>
                        {orderSplitData && orderSplitData.order_id === selectedOrder.id && (
                          <div className="p-2 rounded bg-surface-bg border border-border text-[11px] space-y-1">
                            <div className="flex justify-between">
                              <span className="text-text-secondary">Bruto:</span>
                              <span className="font-mono">R$ {orderSplitData.gross_amount.toFixed(2)}</span>
                            </div>
                            <div className="flex justify-between text-status-success font-semibold">
                              <span>Indústria:</span>
                              <span className="font-mono">R$ {orderSplitData.seller_net_payout.toFixed(2)}</span>
                            </div>
                            <div className="flex justify-between text-brand-primary">
                              <span>Courier:</span>
                              <span className="font-mono">R$ {orderSplitData.courier_net_payout.toFixed(2)}</span>
                            </div>
                          </div>
                        )}
                        {splitFeedback && (
                          <p className="text-[10px] text-text-muted">{splitFeedback}</p>
                        )}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="h-48 flex items-center justify-center text-xs text-text-muted text-center border border-dashed border-border rounded-lg">
                    Selecione uma ordem para inspecionar.
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: Micro-Hubs & Radar Haversine */}
      {activeTab === "hubs" && (
        <div className="space-y-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <span className="text-xs text-text-secondary font-medium">
              Rede de Micro-Hubs de Pronta-Entrega & Busca Georreferenciada de Emergência
            </span>
            <div className="flex items-center gap-2">
              <Button size="sm" onClick={() => setShowHubModal(true)} className="gap-1.5">
                <Plus className="w-3.5 h-3.5" />
                + Novo Hub Urbano
              </Button>
              <Button size="sm" variant="outline" onClick={() => setShowInventoryModal(true)} className="gap-1.5">
                <Package className="w-3.5 h-3.5" />
                + Abastecer Lote no Hub
              </Button>
            </div>
          </div>

          <DentgoRadarMap
            hubs={hubs}
            orders={orders}
            clinic={{ label: "Clínica (busca de emergência)", lat: searchLat, lng: searchLng }}
          />

          {inventoryFeedback && (
            <div className="p-3 rounded-lg bg-status-success-subtle text-status-success border border-status-success/20 text-xs font-medium">
              {inventoryFeedback}
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Hubs List */}
            <div className="lg:col-span-1 bg-surface-card border border-border rounded-xl p-5 shadow-card space-y-4">
              <div className="flex items-center justify-between border-b border-border pb-3">
                <h3 className="text-sm font-bold text-text-main">Hubs Parceiros ({hubs.length})</h3>
                <RefreshCw
                  className="w-3.5 h-3.5 text-text-secondary cursor-pointer hover:text-brand-primary"
                  onClick={fetchHubs}
                />
              </div>

              {loadingHubs ? (
                <div className="space-y-2">
                  <Skeleton className="h-16 w-full" />
                  <Skeleton className="h-16 w-full" />
                </div>
              ) : hubs.length === 0 ? (
                <div className="py-6 text-center text-xs text-text-muted">Nenhum hub cadastrado.</div>
              ) : (
                <div className="space-y-2.5 max-h-96 overflow-y-auto">
                  {hubs.map((hub) => (
                    <div
                      key={hub.id}
                      onClick={() => setInventoryHubId(hub.id)}
                      className={`p-3 rounded-lg border transition-all cursor-pointer ${
                        inventoryHubId === hub.id
                          ? "bg-surface-bg border-brand-primary shadow-card"
                          : "bg-surface-bg border-border hover:border-brand-primary/40"
                      }`}
                    >
                      <div className="flex justify-between items-start mb-1">
                        <span className="font-bold text-xs text-text-main">{hub.name}</span>
                        <span className="text-[10px] font-mono text-brand-primary font-bold">{hub.id}</span>
                      </div>
                      <span className="text-[11px] text-text-secondary font-mono block">CNPJ: {hub.cnpj}</span>
                      <div className="flex justify-between items-center text-[10px] text-text-muted font-mono mt-2 pt-1 border-t border-border">
                        <span>Raio: {hub.coverage_radius_km} km</span>
                        <span>Plantão: {hub.on_duty_schedule}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Radar Haversine Search Console */}
            <div className="lg:col-span-2 bg-surface-card border border-border rounded-xl p-5 shadow-card space-y-4">
              <div className="flex items-center justify-between border-b border-border pb-3">
                <div>
                  <h3 className="text-sm font-bold text-text-main">
                    Busca de Estoque Mais Próximo para Atendimento Imediato
                  </h3>
                  <p className="text-xs text-text-secondary">
                    Localização instantânea da unidade mais próxima com lote esterilizado em estoque e tempo de entrega estimado
                  </p>
                </div>
                <span className="text-[10px] font-mono bg-surface-bg px-2 py-0.5 rounded text-text-muted border border-border">
                  POST /hubs/search-emergency
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                <div>
                  <label className="text-text-secondary block mb-1">Latitude da Cirurgia</label>
                  <input
                    type="number"
                    step="0.0001"
                    value={searchLat}
                    onChange={(e) => setSearchLat(Number(e.target.value))}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                  />
                </div>
                <div>
                  <label className="text-text-secondary block mb-1">Longitude da Cirurgia</label>
                  <input
                    type="number"
                    step="0.0001"
                    value={searchLng}
                    onChange={(e) => setSearchLng(Number(e.target.value))}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                  />
                </div>
                <div>
                  <label className="text-text-secondary block mb-1">Código do Implante</label>
                  <input
                    type="text"
                    value={searchProductId}
                    onChange={(e) => setSearchProductId(e.target.value)}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                  />
                </div>
                <div>
                  <label className="text-text-secondary block mb-1">Qtd Solicitada</label>
                  <input
                    type="number"
                    value={searchQty}
                    onChange={(e) => setSearchQty(Number(e.target.value))}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                  />
                </div>
              </div>

              <Button
                size="sm"
                onClick={handleEmergencySearch}
                disabled={searchingEmergency}
                className="w-full gap-1.5"
              >
                <Search className="w-3.5 h-3.5" />
                {searchingEmergency ? "Buscando Hubs..." : "Disparar Busca Haversine"}
              </Button>

              {searchResults.length > 0 && (
                <div className="space-y-3 pt-2">
                  <h4 className="text-xs font-bold text-text-main">
                    Hubs com Disponibilidade Imediata ({searchResults.length}):
                  </h4>
                  <div className="space-y-2">
                    {searchResults.map((res, i) => (
                      <div key={i} className="p-3 bg-surface-bg rounded-lg border border-border space-y-1 text-xs">
                        <div className="flex justify-between items-start">
                          <span className="font-bold text-text-main">{res.hub_name}</span>
                          <span className="font-mono font-bold text-status-success">
                            ETA ~{res.estimated_eta_minutes} min ({res.distance_km} km)
                          </span>
                        </div>
                        <p className="text-text-secondary">{res.product_name}</p>
                        <div className="flex items-center justify-between text-[11px] text-text-muted font-mono pt-1">
                          <span>
                            Lote: {res.batch_number} • {res.anvisa_reg}
                          </span>
                          <span>Estoque: {res.quantity_available} un</span>
                          <span className="text-text-main font-bold">R$ {res.unit_price.toFixed(2)}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: Liquidação Preventiva FEFO */}
      {activeTab === "fefo" && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-surface-card border border-border rounded-xl p-4 shadow-card">
            <div>
              <h3 className="text-sm font-bold text-text-main">Ofertas de Lotes Próximos do Vencimento</h3>
              <p className="text-xs text-text-secondary">
                Identificação automática de lotes com validade entre 6 e 9 meses para venda com desconto
              </p>
            </div>
            <Button size="sm" onClick={handleRunFefoScan} disabled={scanningFefo} className="gap-1.5">
              <Zap className="w-3.5 h-3.5" />
              {scanningFefo ? "Verificando Lotes..." : "Verificar Lotes com Vencimento Próximo"}
            </Button>
          </div>

          {fefoFeedback && (
            <div className="p-3 rounded-lg bg-status-success-subtle text-status-success border border-status-success/20 text-xs font-medium">
              {fefoFeedback}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {loadingFefo ? (
              <div className="col-span-full space-y-3">
                <Skeleton className="h-24 w-full" />
                <Skeleton className="h-24 w-full" />
              </div>
            ) : fefoDeals.length === 0 ? (
              <div className="col-span-full py-12 text-center text-xs text-text-muted border border-dashed border-border rounded-xl">
                Nenhuma oferta especial ativa no momento. Clique no botão acima para verificar os lotes.
              </div>
            ) : (
              fefoDeals.map((deal) => (
                <div
                  key={deal.id}
                  className="bg-surface-card border border-border rounded-xl p-4 shadow-card space-y-3 flex flex-col justify-between"
                >
                  <div>
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-mono text-xs text-brand-primary font-bold">{deal.id}</span>
                      <span className="text-xs font-mono font-bold text-status-danger bg-status-danger-subtle px-2 py-0.5 rounded">
                        -{deal.discount_percentage}% OFF
                      </span>
                    </div>

                    <h4 className="text-sm font-bold text-text-main mb-1">{deal.product_name}</h4>
                    <span className="text-[11px] text-text-secondary font-mono block">
                      Hub: {deal.hub_name} • Lote: {deal.batch_number}
                    </span>

                    <div className="mt-3 p-2 bg-surface-bg rounded border border-border space-y-1 text-xs">
                      <div className="flex justify-between text-text-secondary">
                        <span>Preço Original:</span>
                        <span className="line-through">R$ {deal.original_unit_price.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between font-bold text-sm text-status-success">
                        <span>Preço Flash:</span>
                        <span>R$ {deal.flash_unit_price.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between text-[11px] text-text-muted pt-1 border-t border-border">
                        <span>Validade Residual:</span>
                        <span>{deal.months_to_expire} meses</span>
                      </div>
                      <div className="flex justify-between text-[11px] text-text-muted">
                        <span>Saldo Disponível:</span>
                        <span className="font-bold">{deal.available_quantity} un</span>
                      </div>
                    </div>
                  </div>

                  <Button
                    size="sm"
                    onClick={() => setSelectedFefoDeal(deal)}
                    className="w-full gap-1.5 text-xs mt-2"
                  >
                    <Tag className="w-3.5 h-3.5" />
                    Reservar Lote Flash Deal
                  </Button>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* TAB 4: Split Financeiro & Repasses */}
      {activeTab === "split" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Split Calculator */}
            <div className="lg:col-span-1 bg-surface-card border border-border rounded-xl p-5 shadow-card space-y-4">
              <div className="flex items-center justify-between border-b border-border pb-3">
                <h3 className="text-sm font-bold text-text-main">Calcular Split do Pedido</h3>
                <span className="text-[10px] font-mono bg-surface-bg px-2 py-0.5 rounded text-text-muted border border-border">
                  POST /orders/{'{id}'}/split
                </span>
              </div>

              <div className="space-y-3 text-xs">
                <div>
                  <label className="text-text-secondary block mb-1">ID do Pedido DENTGO</label>
                  <input
                    type="text"
                    value={splitOrderId}
                    onChange={(e) => setSplitOrderId(e.target.value)}
                    placeholder="Ex: ord-..."
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                  />
                </div>
                <div>
                  <label className="text-text-secondary block mb-1">Comissão da Plataforma (%)</label>
                  <input
                    type="number"
                    step="0.5"
                    value={splitTakeRate}
                    onChange={(e) => setSplitTakeRate(Number(e.target.value))}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                  />
                </div>
                <div>
                  <label className="text-text-secondary block mb-1">Método de Liquidação</label>
                  <select
                    value={splitMethod}
                    onChange={(e) => setSplitMethod(e.target.value)}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                  >
                    <option value="PIX_INSTANT">PIX_INSTANT (Imediato)</option>
                    <option value="CORPORATE_CREDIT">CORPORATE_CREDIT (Quinzenal)</option>
                  </select>
                </div>

                <div className="flex gap-2">
                  <Button
                    size="sm"
                    onClick={handleProcessSplit}
                    disabled={processingSplit || !splitOrderId.trim()}
                    className="flex-1 gap-1.5"
                  >
                    <DollarSign className="w-3.5 h-3.5" />
                    {processingSplit ? "Processando..." : "Processar Split (POST)"}
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleFetchOrderSplit(splitOrderId)}
                    disabled={fetchingOrderSplit || !splitOrderId.trim()}
                    className="flex-1 gap-1.5"
                  >
                    <Search className="w-3.5 h-3.5" />
                    {fetchingOrderSplit ? "Consultando..." : "Consultar Split (GET)"}
                  </Button>
                </div>
              </div>

              {splitResult && (
                <div className="p-3 rounded-lg bg-surface-bg border border-border space-y-1.5 text-xs">
                  <span className="font-bold text-text-main block">Extrato do Pedido:</span>
                  <div className="flex justify-between text-text-secondary">
                    <span>Valor Bruto:</span>
                    <span className="font-mono">R$ {splitResult.gross_amount.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-status-success font-semibold">
                    <span>Repasse Indústria (80%+):</span>
                    <span className="font-mono">R$ {splitResult.seller_net_payout.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-brand-primary">
                    <span>Repasse Courier:</span>
                    <span className="font-mono">R$ {splitResult.courier_net_payout.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-text-muted">
                    <span>Taxa da Plataforma:</span>
                    <span className="font-mono">R$ {splitResult.platform_fee_amount.toFixed(2)}</span>
                  </div>
                </div>
              )}
            </div>

            {/* Splits Ledger */}
            <div className="lg:col-span-2 bg-surface-card border border-border rounded-xl p-5 shadow-card space-y-4">
              <div className="flex items-center justify-between border-b border-border pb-3">
                <h3 className="text-sm font-bold text-text-main">
                  Ledger de Splits Financeiros ({splits.length})
                </h3>
                <RefreshCw
                  className="w-3.5 h-3.5 text-text-secondary cursor-pointer hover:text-brand-primary"
                  onClick={fetchSplits}
                />
              </div>

              {loadingSplits ? (
                <div className="space-y-2">
                  <Skeleton className="h-16 w-full" />
                  <Skeleton className="h-16 w-full" />
                </div>
              ) : splits.length === 0 ? (
                <div className="py-8 text-center text-xs text-text-muted border border-dashed border-border rounded-xl">
                  Nenhum split liquidado até o momento.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-xs text-left">
                    <thead className="bg-surface-bg text-text-secondary border-b border-border">
                      <tr>
                        <th className="p-2 font-semibold">ID / Pedido</th>
                        <th className="p-2 font-semibold">Bruto</th>
                        <th className="p-2 font-semibold">Indústria</th>
                        <th className="p-2 font-semibold">Courier</th>
                        <th className="p-2 font-semibold">Taxa</th>
                        <th className="p-2 font-semibold">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border">
                      {splits.map((sp) => (
                        <tr key={sp.id} className="hover:bg-surface-bg">
                          <td className="p-2 font-mono font-bold text-brand-primary">{sp.order_id}</td>
                          <td className="p-2 font-mono">R$ {sp.gross_amount.toFixed(2)}</td>
                          <td className="p-2 font-mono font-semibold text-status-success">
                            R$ {sp.seller_net_payout.toFixed(2)}
                          </td>
                          <td className="p-2 font-mono text-brand-navy">R$ {sp.courier_net_payout.toFixed(2)}</td>
                          <td className="p-2 font-mono text-text-muted">R$ {sp.platform_fee_amount.toFixed(2)}</td>
                          <td className="p-2">
                            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-status-success-subtle text-status-success border border-status-success/20">
                              {sp.settlement_status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* MODAL: Checkout Novo Pedido Emergencial */}
      {showCheckoutModal && (
        <div className="fixed inset-0 bg-text-main/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-surface-card border border-border rounded-xl max-w-lg w-full p-6 shadow-modal space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-border">
              <h3 className="text-base font-bold text-text-main">+ Novo Despacho Emergencial (Same-Day)</h3>
              <button onClick={() => setShowCheckoutModal(false)} className="text-text-secondary hover:text-text-main">
                X
              </button>
            </div>
            <div className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-text-secondary block mb-1">CRO/UF do Cirurgião</label>
                  <input
                    type="text"
                    value={newOrderCro}
                    onChange={(e) => setNewOrderCro(e.target.value)}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                  />
                </div>
                <div>
                  <label className="text-text-secondary block mb-1">Voucher de Isenção</label>
                  <input
                    type="text"
                    value={newOrderVoucher}
                    onChange={(e) => setNewOrderVoucher(e.target.value)}
                    placeholder="Opcional"
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="text-text-secondary block mb-1">Endereço de Entrega (Clínica/Hospital)</label>
                <input
                  type="text"
                  value={newOrderAddress}
                  onChange={(e) => setNewOrderAddress(e.target.value)}
                  className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-text-secondary block mb-1">Latitude</label>
                  <input
                    type="number"
                    step="0.0001"
                    value={newOrderLat}
                    onChange={(e) => setNewOrderLat(Number(e.target.value))}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                  />
                </div>
                <div>
                  <label className="text-text-secondary block mb-1">Longitude</label>
                  <input
                    type="number"
                    step="0.0001"
                    value={newOrderLng}
                    onChange={(e) => setNewOrderLng(Number(e.target.value))}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-2 pt-2 border-t border-border">
                <div className="col-span-2">
                  <label className="text-text-secondary block mb-1">Código do Implante</label>
                  <input
                    type="text"
                    value={newOrderProductId}
                    onChange={(e) => setNewOrderProductId(e.target.value)}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                  />
                </div>
                <div>
                  <label className="text-text-secondary block mb-1">Quantidade</label>
                  <input
                    type="number"
                    value={newOrderQty}
                    onChange={(e) => setNewOrderQty(Number(e.target.value))}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Button type="button" size="sm" variant="outline" onClick={handleAddCartItem} className="w-full gap-1.5">
                  <Plus className="w-3.5 h-3.5" />
                  Adicionar Item ao Carrinho
                </Button>
                {cartItems.length > 0 && (
                  <ul className="rounded-lg border border-border divide-y divide-border">
                    {cartItems.map((i) => (
                      <li key={i.product_id} className="flex items-center justify-between p-2">
                        <span className="font-mono">
                          {i.product_id} x {i.quantity}
                        </span>
                        <button
                          type="button"
                          aria-label={`Remover ${i.product_id}`}
                          onClick={() => setCartItems((prev) => prev.filter((x) => x.product_id !== i.product_id))}
                          className="text-status-danger"
                        >
                          Remover
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              <div>
                <label className="text-text-secondary block mb-1">Voucher (isenção da taxa de urgência)</label>
                <input
                  type="text"
                  value={newOrderVoucher}
                  onChange={(e) => setNewOrderVoucher(e.target.value)}
                  placeholder="MOEDA-EXPRESS-XXXX ou DENTGO-EXPRESS-XXXX"
                  className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                />
                {voucherError && <p className="text-status-danger mt-1">{voucherError}</p>}
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-3 border-t border-border">
              <Button variant="outline" size="sm" onClick={() => setShowCheckoutModal(false)}>
                Cancelar
              </Button>
              <Button size="sm" onClick={handleCreateExpressOrder} disabled={checkingOut}>
                {checkingOut ? "Enviando..." : "Despachar Imediatamente"}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: Novo Hub */}
      {showHubModal && (
        <div className="fixed inset-0 bg-text-main/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-surface-card border border-border rounded-xl max-w-md w-full p-6 shadow-modal space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-border">
              <h3 className="text-base font-bold text-text-main">+ Cadastrar Hub Urbano</h3>
              <button onClick={() => setShowHubModal(false)} className="text-text-secondary hover:text-text-main">
                X
              </button>
            </div>
            <div className="space-y-3 text-xs">
              <div>
                <label className="text-text-secondary block mb-1">Nome do Hub</label>
                <input
                  type="text"
                  value={newHubName}
                  onChange={(e) => setNewHubName(e.target.value)}
                  className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main"
                />
              </div>
              <div>
                <label className="text-text-secondary block mb-1">CNPJ</label>
                <input
                  type="text"
                  value={newHubCnpj}
                  onChange={(e) => setNewHubCnpj(e.target.value)}
                  className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-text-secondary block mb-1">Latitude</label>
                  <input
                    type="number"
                    step="0.0001"
                    value={newHubLat}
                    onChange={(e) => setNewHubLat(Number(e.target.value))}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                  />
                </div>
                <div>
                  <label className="text-text-secondary block mb-1">Longitude</label>
                  <input
                    type="number"
                    step="0.0001"
                    value={newHubLng}
                    onChange={(e) => setNewHubLng(Number(e.target.value))}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                  />
                </div>
              </div>
              <div>
                <label className="text-text-secondary block mb-1">Raio de Cobertura (km)</label>
                <input
                  type="number"
                  value={newHubRadius}
                  onChange={(e) => setNewHubRadius(Number(e.target.value))}
                  className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-3 border-t border-border">
              <Button variant="outline" size="sm" onClick={() => setShowHubModal(false)}>
                Cancelar
              </Button>
              <Button size="sm" onClick={handleCreateHub} disabled={creatingHub}>
                {creatingHub ? "Salvando..." : "Salvar Hub"}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: Abastecer Estoque no Hub */}
      {showInventoryModal && (
        <div className="fixed inset-0 bg-text-main/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-surface-card border border-border rounded-xl max-w-md w-full p-6 shadow-modal space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-border">
              <h3 className="text-base font-bold text-text-main">+ Abastecer Lote no Hub</h3>
              <button onClick={() => setShowInventoryModal(false)} className="text-text-secondary hover:text-text-main">
                X
              </button>
            </div>
            <div className="space-y-3 text-xs">
              <div>
                <label className="text-text-secondary block mb-1">Hub de Destino</label>
                <select
                  value={inventoryHubId}
                  onChange={(e) => setInventoryHubId(e.target.value)}
                  className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                >
                  {hubs.map((h) => (
                    <option key={h.id} value={h.id}>
                      {h.name} ({h.id})
                    </option>
                  ))}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-text-secondary block mb-1">Código do Produto</label>
                  <input
                    type="text"
                    value={invProductId}
                    onChange={(e) => setInvProductId(e.target.value)}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                  />
                </div>
                <div>
                  <label className="text-text-secondary block mb-1">Descrição</label>
                  <input
                    type="text"
                    value={invProductName}
                    onChange={(e) => setInvProductName(e.target.value)}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-text-secondary block mb-1">Lote</label>
                  <input
                    type="text"
                    value={invBatch}
                    onChange={(e) => setInvBatch(e.target.value)}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                  />
                </div>
                <div>
                  <label className="text-text-secondary block mb-1">Registro ANVISA</label>
                  <input
                    type="text"
                    value={invAnvisa}
                    onChange={(e) => setInvAnvisa(e.target.value)}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                  />
                </div>
              </div>
              <div className="grid grid-cols-3 gap-2">
                <div>
                  <label className="text-text-secondary block mb-1">Qtd</label>
                  <input
                    type="number"
                    value={invQty}
                    onChange={(e) => setInvQty(Number(e.target.value))}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                  />
                </div>
                <div>
                  <label className="text-text-secondary block mb-1">Preço Unit (R$)</label>
                  <input
                    type="number"
                    value={invPrice}
                    onChange={(e) => setInvPrice(Number(e.target.value))}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                  />
                </div>
                <div>
                  <label className="text-text-secondary block mb-1">Validade</label>
                  <input
                    type="date"
                    value={invExpiry}
                    onChange={(e) => setInvExpiry(e.target.value)}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                  />
                </div>
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-3 border-t border-border">
              <Button variant="outline" size="sm" onClick={() => setShowInventoryModal(false)}>
                Cancelar
              </Button>
              <Button size="sm" onClick={handleAddHubInventory} disabled={addingInventory}>
                {addingInventory ? "Abastecendo..." : "Abastecer Hub"}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: Reservar Flash Deal */}
      {selectedFefoDeal && (
        <div className="fixed inset-0 bg-text-main/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-surface-card border border-border rounded-xl max-w-md w-full p-6 shadow-modal space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-border">
              <h3 className="text-base font-bold text-text-main">
                Reservar Lote Flash Deal ({selectedFefoDeal.discount_percentage}% OFF)
              </h3>
              <button onClick={() => setSelectedFefoDeal(null)} className="text-text-secondary hover:text-text-main">
                X
              </button>
            </div>
            <div className="space-y-3 text-xs">
              <div className="p-3 bg-surface-bg rounded-lg border border-border">
                <span className="font-bold text-text-main block">{selectedFefoDeal.product_name}</span>
                <span className="text-text-secondary font-mono text-[11px] block mt-0.5">
                  Lote: {selectedFefoDeal.batch_number} • Hub: {selectedFefoDeal.hub_name}
                </span>
                <div className="flex justify-between items-center mt-2 pt-1 border-t border-border font-bold text-sm text-status-success">
                  <span>Preço Unitário Promocional:</span>
                  <span>R$ {selectedFefoDeal.flash_unit_price.toFixed(2)}</span>
                </div>
              </div>

              <div>
                <label className="text-text-secondary block mb-1">Nome do Cirurgião</label>
                <input
                  type="text"
                  value={reserveName}
                  onChange={(e) => setReserveName(e.target.value)}
                  className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-text-secondary block mb-1">CRO-UF</label>
                  <input
                    type="text"
                    value={reserveCro}
                    onChange={(e) => setReserveCro(e.target.value)}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                  />
                </div>
                <div>
                  <label className="text-text-secondary block mb-1">Quantidade</label>
                  <input
                    type="number"
                    max={selectedFefoDeal.available_quantity}
                    min={1}
                    value={reserveQty}
                    onChange={(e) => setReserveQty(Number(e.target.value))}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                  />
                </div>
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-3 border-t border-border">
              <Button variant="outline" size="sm" onClick={() => setSelectedFefoDeal(null)}>
                Cancelar
              </Button>
              <Button size="sm" onClick={handleReserveFefoDeal} disabled={reservingDeal}>
                {reservingDeal ? "Reservando..." : "Confirmar Reserva Flash"}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DentgoExpressCockpit;
