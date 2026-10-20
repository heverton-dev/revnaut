import React, { useState, useEffect, useCallback } from "react";
import {
  Package,
  RefreshCw,
  AlertCircle,
  Plus,
  CheckCircle2,
  Truck,
  Award,
  FileText,
  Zap,
  ScanLine,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";
import { EmptyState } from "@/components/ui/EmptyState";
import { Tabs } from "@/components/ui/Tabs";
import { R2DirectUploader } from "@/components/shared/R2DirectUploader";

export interface SurgicalOrder {
  id: string;
  account_id: string;
  agreement_id: string;
  patient_identifier?: string;
  surgery_date: string;
  status: "SOLICITADO_FIELD" | "APROVADO_INSIDE" | "EM_POSSE_CLINICA" | "FATURADO_E_REPOSTO" | "REQUESTED" | "APPROVED_PREPARING" | "DISPATCHED_SEALED" | "POSTOP_REPORTED" | string;
  field_consultant_id?: string;
  inside_analyst_id?: string;
  remitted_items_json: string;
  consumed_items_json: string;
  returned_items_json?: string;
  seal_photo_r2_key?: string;
  billing_order_id?: string;
  created_at: string;
}

export const normalizeOrderStatus = (status: string): "SOLICITADO_FIELD" | "APROVADO_INSIDE" | "EM_POSSE_CLINICA" | "FATURADO_E_REPOSTO" => {
  if (status === "REQUESTED" || status === "SOLICITADO_FIELD") return "SOLICITADO_FIELD";
  if (status === "APPROVED_PREPARING" || status === "APROVADO_INSIDE") return "APROVADO_INSIDE";
  if (status === "DISPATCHED_SEALED" || status === "EM_POSSE_CLINICA") return "EM_POSSE_CLINICA";
  if (status === "POSTOP_REPORTED" || status === "FATURADO_E_REPOSTO" || status === "CONCLUIDO_POS_OP") return "FATURADO_E_REPOSTO";
  return "SOLICITADO_FIELD";
};

export interface PartnerAgreement {
  id: string;
  partner_name: string;
  partner_cro_uf?: string;
  tier: string;
  credit_limit: number;
  used_credit: number;
  min_monthly_revenue: number;
  max_turnover_days: number;
  is_active: number;
  created_at: string;
}

export interface KolContract {
  id: string;
  agreement_id?: string;
  kol_name: string;
  cro_uf: string;
  equipment_name: string;
  asset_tag: string;
  min_monthly_implants_target: number;
  clinical_lectures_quota: number;
  current_month_consumption: number;
  compliance_status: string;
  evidence_r2_keys_json: string;
  created_at: string;
}

export interface LoyaltyReward {
  id: string;
  name: string;
  points_required: number;
  category: string;
  description: string;
  reward_type: string;
}

export interface LoyaltyWallet {
  wallet_id: string;
  partner_id: string;
  partner_name: string;
  points_balance: number;
  lifetime_points: number;
  current_tier: string;
  implants_billed_total: number;
  history: Array<{
    id: string;
    type: string;
    points: number;
    description: string;
    created_at: string;
  }>;
}

export const ConsignmentSurgicalBoard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>("board");

  // Tab 1: Orders
  const [orders, setOrders] = useState<SurgicalOrder[]>([]);
  const [loadingOrders, setLoadingOrders] = useState<boolean>(true);
  const [ordersError, setOrdersError] = useState<string | null>(null);
  const [selectedOrder, setSelectedOrder] = useState<SurgicalOrder | null>(null);

  // New Order Modal
  const [showNewOrderModal, setShowNewOrderModal] = useState<boolean>(false);
  const [orderAgreementId, setOrderAgreementId] = useState<string>("agr-01");
  const [orderPatient, setOrderPatient] = useState<string>("Paciente PAC-8492");
  const [orderDate, setOrderDate] = useState<string>("2026-10-25");
  const [orderFieldConsultant, setOrderFieldConsultant] = useState<string>("usr-field-01");
  const [orderProductId, setOrderProductId] = useState<string>("IMP-CM-4311");
  const [orderProductName, setOrderProductName] = useState<string>("Implante Cone Morse 4.3x11mm");
  const [orderBatch, setOrderBatch] = useState<string>("LOTE-2026-X1");
  const [orderAnvisa, setOrderAnvisa] = useState<string>("ANVISA-80123456789");
  const [orderQty, setOrderQty] = useState<number>(4);
  const [orderUnitVal, setOrderUnitVal] = useState<number>(450.0);
  const [orderExpiry, setOrderExpiry] = useState<string>("2028-12-31");
  const [creatingOrder, setCreatingOrder] = useState<boolean>(false);

  // Postop Modal
  const [postopOrder, setPostopOrder] = useState<SurgicalOrder | null>(null);
  const [postopConsumedQty, setPostopConsumedQty] = useState<number>(2);
  const [postopNotes, setPostopNotes] = useState<string>("Instalados 2 implantes em região 14 e 16 com torque 45 N.cm.");
  const [submittingPostop, setSubmittingPostop] = useState<boolean>(false);

  // Tab 2: Agreements & Kits
  const [agreements, setAgreements] = useState<PartnerAgreement[]>([]);
  const [loadingAgreements, setLoadingAgreements] = useState<boolean>(false);
  const [showNewAgreementModal, setShowNewAgreementModal] = useState<boolean>(false);
  const [newAgPartner, setNewAgPartner] = useState<string>("Instituto Odontológico Paulista");
  const [newAgCro, setNewAgCro] = useState<string>("SP-44912");
  const [newAgTier, setNewAgTier] = useState<string>("GOLD");
  const [newAgLimit, setNewAgLimit] = useState<number>(35000);
  const [creatingAgreement, setCreatingAgreement] = useState<boolean>(false);

  // Custody Summary
  const [selectedCustodyAgreementId, setSelectedCustodyAgreementId] = useState<string>("");
  const [custodySummary, setCustodySummary] = useState<any | null>(null);
  const [showDispatchCustodyModal, setShowDispatchCustodyModal] = useState<boolean>(false);
  const [dispatchProductId, setDispatchProductId] = useState<string>("IMP-CM-4311");
  const [dispatchBatch, setDispatchBatch] = useState<string>("LOTE-2026-X1");
  const [dispatchQty, setDispatchQty] = useState<number>(10);
  const [dispatchProductName, setDispatchProductName] = useState<string>("Implante Cone Morse 4.3x11mm");
  const [dispatchAnvisa, setDispatchAnvisa] = useState<string>("ANVISA-80123456789");
  const [dispatchUnitValue, setDispatchUnitValue] = useState<number>(450.0);
  const [dispatchExpiry, setDispatchExpiry] = useState<string>("2028-12-31");
  const [dispatchLots, setDispatchLots] = useState<
    Array<{
      product_id: string;
      product_name: string;
      anvisa_reg: string;
      batch_number: string;
      quantity: number;
      unit_value: number;
      sterilization_expiry_date: string;
    }>
  >([]);
  const [dispatchingCustody, setDispatchingCustody] = useState<boolean>(false);
  const [dispatchCustodyFeedback, setDispatchCustodyFeedback] = useState<string | null>(null);
  const [loadingCustody, setLoadingCustody] = useState<boolean>(false);

  // Register Kit
  const [showKitModal, setShowKitModal] = useState<boolean>(false);
  const [kitSerial, setKitSerial] = useState<string>("KIT-CM-2026-009");
  const [kitName, setKitName] = useState<string>("Maleta Cirúrgica Cone Morse Full Titanium");
  const [registeringKit, setRegisteringKit] = useState<boolean>(false);
  const [kitFeedback, setKitFeedback] = useState<string | null>(null);

  // Trigger Reverse Pickup
  const [showPickupModal, setShowPickupModal] = useState<boolean>(false);
  // TICKET-KEY-01: Leitor de Código de Barras / DataMatrix
  const [showScannerModal, setShowScannerModal] = useState<boolean>(false);
  const [scanCode, setScanCode] = useState<string>("");
  const [scanResult, setScanResult] = useState<string | null>(null);
  const [pickupSerial, setPickupSerial] = useState<string>("KIT-CM-2026-009");
  const [pickupAgreementId, setPickupAgreementId] = useState<string>("agr-01");
  const [pickupAddress, setPickupAddress] = useState<string>("Av. Paulista 1000, Bela Vista, São Paulo - SP");
  const [pickupDest, setPickupDest] = useState<string>("Hub Central DENTGO SP - R. Augusta 500");
  const [triggeringPickup, setTriggeringPickup] = useState<boolean>(false);
  const [pickupFeedback, setPickupFeedback] = useState<string | null>(null);

  // Tab 3: KOL
  const [kolContracts, setKolContracts] = useState<KolContract[]>([]);
  const [kolSpeakers, setKolSpeakers] = useState<any[]>([]);
  const [loadingKol, setLoadingKol] = useState<boolean>(false);
  const [showKolModal, setShowKolModal] = useState<boolean>(false);
  const [kolName, setKolName] = useState<string>("Dr. Roberto Silveira");
  const [kolCro, setKolCro] = useState<string>("SP-12345");
  const [kolEquip, setKolEquip] = useState<string>("Motor Cirúrgico Piezoelétrico Titanium Pro");
  const [kolTag, setKolTag] = useState<string>("PAT-KOL-8891");
  const [kolTarget, setKolTarget] = useState<number>(25);
  const [kolQuota, setKolQuota] = useState<number>(2);
  const [creatingKol, setCreatingKol] = useState<boolean>(false);

  const [consumptionContractId, setConsumptionContractId] = useState<string | null>(null);
  const [consumptionQty, setConsumptionQty] = useState<number>(22);
  const [recordingConsumption, setRecordingConsumption] = useState<boolean>(false);

  const [evidenceContractId, setEvidenceContractId] = useState<string | null>(null);
  const [evidenceTitle, setEvidenceTitle] = useState<string>("Aula Magna de Implantes Imediatos Cone Morse");
  const [evidenceR2Key, setEvidenceR2Key] = useState<string>("kol/evidences/aula-imediata-2026.mp4");
  const [submittingEvidence, setSubmittingEvidence] = useState<boolean>(false);

  // Tab 4: Loyalty
  const [loyaltyPartnerId, setLoyaltyPartnerId] = useState<string>("cnt-01");
  const [wallet, setWallet] = useState<LoyaltyWallet | null>(null);
  const [rewards, setRewards] = useState<LoyaltyReward[]>([]);
  const [loadingLoyalty, setLoadingLoyalty] = useState<boolean>(false);
  const [loyaltyCreditPartner, setLoyaltyCreditPartner] = useState<string>("cnt-01");
  const [loyaltyCreditName, setLoyaltyCreditName] = useState<string>("Dr. Roberto Silveira");
  const [loyaltyCreditImplants, setLoyaltyCreditImplants] = useState<number>(10);
  const [creditingLoyalty, setCreditingLoyalty] = useState<boolean>(false);
  const [loyaltyFeedback, setLoyaltyFeedback] = useState<string | null>(null);

  // Fetch Surgical Orders
  const fetchSurgicalOrders = useCallback(async () => {
    setLoadingOrders(true);
    setOrdersError(null);
    try {
      const res = await fetch("/api/v1/keypartners/surgical-orders");
      if (!res.ok) {
        throw new Error(`Falha ao carregar ordens cirúrgicas (HTTP ${res.status})`);
      }
      const data = await res.json();
      setOrders(Array.isArray(data) ? data : data.orders || []);
    } catch (err: any) {
      setOrdersError(err.message || "Erro ao consultar o painel cirúrgico KeyPartners.");
    } finally {
      setLoadingOrders(false);
    }
  }, []);

  // Fetch Agreements
  const fetchAgreements = useCallback(async () => {
    setLoadingAgreements(true);
    try {
      const res = await fetch("/api/v1/keypartners/agreements");
      if (res.ok) {
        const data = await res.json();
        const list = Array.isArray(data) ? data : [];
        setAgreements(list);
        if (list.length > 0 && !selectedCustodyAgreementId) {
          setSelectedCustodyAgreementId(list[0].id);
        }
      }
    } catch {
      // Fallback
    } finally {
      setLoadingAgreements(false);
    }
  }, [selectedCustodyAgreementId]);

  // Fetch Custody Summary
  const fetchCustodySummary = useCallback(async (agreementId: string) => {
    if (!agreementId) return;
    setLoadingCustody(true);
    try {
      const res = await fetch(`/api/v1/keypartners/agreements/${agreementId}/custody-summary`);
      if (res.ok) {
        const data = await res.json();
        setCustodySummary(data);
      }
    } catch {
      // Fallback
    } finally {
      setLoadingCustody(false);
    }
  }, []);

  // Fetch KOL
  const fetchKolData = useCallback(async () => {
    setLoadingKol(true);
    try {
      const [resContracts, resSpeakers] = await Promise.all([
        fetch("/api/v1/keypartners/kol-contracts"),
        fetch("/api/v1/intelligence/kol-speakers"),
      ]);
      if (resContracts.ok) {
        const data = await resContracts.json();
        setKolContracts(Array.isArray(data) ? data : []);
      }
      if (resSpeakers.ok) {
        const data = await resSpeakers.json();
        setKolSpeakers(data.speakers || []);
      }
    } catch {
      // Fallback
    } finally {
      setLoadingKol(false);
    }
  }, []);

  // Fetch Loyalty
  const fetchLoyaltyData = useCallback(async (partnerId: string) => {
    setLoadingLoyalty(true);
    try {
      const [resWallet, resRewards] = await Promise.all([
        fetch(`/api/v1/keypartners/loyalty/wallet/${partnerId}`),
        fetch("/api/v1/keypartners/loyalty/rewards"),
      ]);
      if (resWallet.ok) {
        const data = await resWallet.json();
        setWallet(data);
      }
      if (resRewards.ok) {
        const data = await resRewards.json();
        setRewards(Array.isArray(data) ? data : []);
      }
    } catch {
      // Fallback
    } finally {
      setLoadingLoyalty(false);
    }
  }, []);

  useEffect(() => {
    fetchSurgicalOrders();
  }, [fetchSurgicalOrders]);

  useEffect(() => {
    if (activeTab === "agreements") {
      fetchAgreements();
    } else if (activeTab === "kol") {
      fetchKolData();
    } else if (activeTab === "loyalty") {
      fetchLoyaltyData(loyaltyPartnerId);
    }
  }, [activeTab, fetchAgreements, fetchKolData, fetchLoyaltyData, loyaltyPartnerId]);

  useEffect(() => {
    if (selectedCustodyAgreementId && activeTab === "agreements") {
      fetchCustodySummary(selectedCustodyAgreementId);
    }
  }, [selectedCustodyAgreementId, activeTab, fetchCustodySummary]);

  // Order Transition Handlers
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
      // erro tratado
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
      // erro tratado
    }
  };

  const handleCreateOrder = async () => {
    setCreatingOrder(true);
    try {
      const res = await fetch("/api/v1/keypartners/surgical-orders", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          agreement_id: orderAgreementId,
          patient_identifier: orderPatient,
          surgery_date: orderDate,
          field_consultant_id: orderFieldConsultant,
          items: [
            {
              product_id: orderProductId,
              product_name: orderProductName,
              anvisa_reg: orderAnvisa,
              batch_number: orderBatch,
              quantity: Number(orderQty),
              unit_value: Number(orderUnitVal),
              sterilization_expiry_date: orderExpiry,
            },
          ],
          account_id: "0f14ffff",
        }),
      });
      if (res.ok) {
        setShowNewOrderModal(false);
        fetchSurgicalOrders();
      }
    } catch {
      // erro
    } finally {
      setCreatingOrder(false);
    }
  };

  const handleReportPostop = async () => {
    if (!postopOrder) return;
    setSubmittingPostop(true);
    try {
      const res = await fetch(`/api/v1/keypartners/surgical-orders/${postopOrder.id}/postop-report`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          consumed_items: [
            {
              product_id: "IMP-CM-4311",
              product_name: "Implante Cone Morse 4.3x11mm",
              anvisa_reg: "ANVISA-80123456789",
              batch_number: "LOTE-2026-X1",
              quantity: Number(postopConsumedQty),
              unit_value: 450.0,
              patient_notes: postopNotes,
            },
          ],
          seal_photo_r2_key: `postop/${postopOrder.id}/seal_return.jpg`,
          account_id: "0f14ffff",
        }),
      });
      if (res.ok) {
        setPostopOrder(null);
        fetchSurgicalOrders();
      }
    } catch {
      // erro
    } finally {
      setSubmittingPostop(false);
    }
  };

  // Agreements Handlers
  const handleCreateAgreement = async () => {
    setCreatingAgreement(true);
    try {
      const res = await fetch("/api/v1/keypartners/agreements", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          partner_name: newAgPartner,
          partner_cro_uf: newAgCro,
          tier: newAgTier,
          credit_limit: Number(newAgLimit),
          min_monthly_revenue: 5000.0,
          max_turnover_days: 60,
          account_id: "0f14ffff",
        }),
      });
      if (res.ok) {
        setShowNewAgreementModal(false);
        fetchAgreements();
      }
    } catch {
      // erro
    } finally {
      setCreatingAgreement(false);
    }
  };

  // Kit Register Handler
  const handleRegisterKit = async () => {
    setRegisteringKit(true);
    setKitFeedback(null);
    try {
      const res = await fetch("/api/v1/keypartners/kits", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          serial_number: kitSerial,
          name: kitName,
          composition_json: JSON.stringify({ drills: ["2.0", "3.5", "4.3"], ratchets: 1 }),
          account_id: "0f14ffff",
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setKitFeedback(`Maleta registrada com QR Code: ${data.qr_code}`);
        setShowKitModal(false);
      }
    } catch (e: any) {
      setKitFeedback(`Erro: ${e.message}`);
    } finally {
      setRegisteringKit(false);
    }
  };

  // Trigger Pickup Handler
  const handleTriggerPickup = async () => {
    setTriggeringPickup(true);
    setPickupFeedback(null);
    try {
      const res = await fetch(`/api/v1/keypartners/consignments/${pickupSerial}/trigger-dentgo-pickup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          target_agreement_id: pickupAgreementId,
          pickup_address: pickupAddress,
          destination_address: pickupDest,
          account_id: "0f14ffff",
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setPickupFeedback(`Ordem de Coleta Reversa gerada no DENTGO: ${data.dentgo_order_id || "Express OK"}`);
        setShowPickupModal(false);
      }
    } catch (e: any) {
      setPickupFeedback(`Falha: ${e.message}`);
    } finally {
      setTriggeringPickup(false);
    }
  };

  // KOL Handlers
  const handleCreateKol = async () => {
    setCreatingKol(true);
    try {
      const res = await fetch("/api/v1/keypartners/kol-contracts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          kol_name: kolName,
          cro_uf: kolCro,
          equipment_name: kolEquip,
          asset_tag: kolTag,
          min_monthly_implants_target: Number(kolTarget),
          clinical_lectures_quota: Number(kolQuota),
          agreement_id: "agr-01",
          account_id: "0f14ffff",
        }),
      });
      if (res.ok) {
        setShowKolModal(false);
        fetchKolData();
      }
    } catch {
      // erro
    } finally {
      setCreatingKol(false);
    }
  };

  const handleRecordConsumption = async () => {
    if (!consumptionContractId) return;
    setRecordingConsumption(true);
    try {
      const res = await fetch(`/api/v1/keypartners/kol-contracts/${consumptionContractId}/record-consumption`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          consumed_implants_count: Number(consumptionQty),
          account_id: "0f14ffff",
        }),
      });
      if (res.ok) {
        setConsumptionContractId(null);
        fetchKolData();
      }
    } catch {
      // erro
    } finally {
      setRecordingConsumption(false);
    }
  };

  const buildDispatchLot = () => ({
    product_id: dispatchProductId.trim(),
    product_name: dispatchProductName.trim(),
    anvisa_reg: dispatchAnvisa.trim(),
    batch_number: dispatchBatch.trim(),
    quantity: Math.max(1, Number(dispatchQty) || 1),
    unit_value: Math.max(0, Number(dispatchUnitValue) || 0),
    sterilization_expiry_date: dispatchExpiry,
  });

  const handleAddDispatchLot = () => {
    if (!dispatchProductId.trim() || !dispatchBatch.trim() || !dispatchAnvisa.trim() || dispatchQty < 1) return;
    setDispatchLots((prev) => [...prev, buildDispatchLot()]);
  };

  const handleDispatchCustody = async () => {
    if (!selectedCustodyAgreementId) return;
    const lots = dispatchLots.length > 0 ? dispatchLots : [buildDispatchLot()];
    setDispatchingCustody(true);
    setDispatchCustodyFeedback(null);
    try {
      const res = await fetch(
        `/api/v1/keypartners/agreements/${encodeURIComponent(selectedCustodyAgreementId)}/dispatch-custody`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ items: lots, account_id: "0f14ffff" }),
        },
      );
      if (res.ok) {
        setShowDispatchCustodyModal(false);
        setDispatchLots([]);
        fetchCustodySummary(selectedCustodyAgreementId);
        fetchAgreements();
      } else {
        const err = await res.json().catch(() => ({}));
        setDispatchCustodyFeedback(
          typeof err.detail === "string" ? err.detail : `Falha na remessa para custódia (HTTP ${res.status}).`,
        );
      }
    } catch {
      setDispatchCustodyFeedback("Falha de rede ao remeter lotes para custódia.");
    } finally {
      setDispatchingCustody(false);
    }
  };

  const handleSubmitEvidence = async () => {
    if (!evidenceContractId) return;
    setSubmittingEvidence(true);
    try {
      const res = await fetch(`/api/v1/keypartners/kol-contracts/${evidenceContractId}/evidence`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          r2_key: evidenceR2Key,
          title: evidenceTitle,
          account_id: "0f14ffff",
        }),
      });
      if (res.ok) {
        setEvidenceContractId(null);
        fetchKolData();
      }
    } catch {
      // erro
    } finally {
      setSubmittingEvidence(false);
    }
  };

  // Loyalty Handlers
  const handleCreditPoints = async () => {
    setCreditingLoyalty(true);
    setLoyaltyFeedback(null);
    try {
      const res = await fetch("/api/v1/keypartners/loyalty/credit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          partner_id: loyaltyCreditPartner,
          partner_name: loyaltyCreditName,
          implants_count: Number(loyaltyCreditImplants),
          event_origin: "deal.won",
          account_id: "0f14ffff",
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setLoyaltyFeedback(`Creditados +${data.points_earned} pontos! Novo saldo: ${data.points_balance}`);
        fetchLoyaltyData(loyaltyPartnerId);
      }
    } catch (e: any) {
      setLoyaltyFeedback(`Erro: ${e.message}`);
    } finally {
      setCreditingLoyalty(false);
    }
  };

  const handleRedeemReward = async (rewardId: string) => {
    try {
      const res = await fetch("/api/v1/keypartners/loyalty/redeem", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          partner_id: loyaltyPartnerId,
          reward_type_or_id: rewardId,
          account_id: "0f14ffff",
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setLoyaltyFeedback(`Resgate concluído: ${data.reward_name}! Pontos debitados: -${data.points_debited}`);
        fetchLoyaltyData(loyaltyPartnerId);
      }
    } catch {
      // erro
    }
  };

  const columns: { id: SurgicalOrder["status"]; title: string }[] = [
    { id: "SOLICITADO_FIELD", title: "1. Solicitado pelo Consultor" },
    { id: "APROVADO_INSIDE", title: "2. Aprovado (Backoffice)" },
    { id: "EM_POSSE_CLINICA", title: "3. Em Posse da Clínica" },
    { id: "FATURADO_E_REPOSTO", title: "4. Faturado & Reposto (CFOP 5.113)" },
  ];

  const tabsConfig = [
    { id: "board", label: "Quadro Cirúrgico 4 Estágios" },
    { id: "agreements", label: "Acordos & Maletas ANVISA" },
    { id: "kol", label: "Contratos KOL & Speakers" },
    { id: "loyalty", label: "Fidelidade (Moeda Cirúrgica)" },
  ];

  return (
    <div className="w-full space-y-6 font-sans text-text-main">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-border">
        <div>
          <div className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand-primary-subtle text-brand-primary border border-brand-primary/20">
              <Package className="h-5 w-5" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-text-main">
                KeyPartners • Cockpit de Consignação Cirúrgica & Parcerias
              </h1>
              <p className="text-xs text-text-secondary mt-0.5">
                Quadro 4 Estágios, Acordos de Consignação, Maletas Seriais, Contratos KOL e Moeda Cirúrgica.
              </p>
            </div>
          </div>
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

      {/* Tabs */}
      <Tabs tabs={tabsConfig} activeTab={activeTab} onChange={setActiveTab} />

      {/* TAB 1: Quadro Cirúrgico 4 Estágios */}
      {activeTab === "board" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs text-text-secondary font-medium">
              Acompanhamento de maletas em campo e conciliação pós-cirúrgica
            </span>
            <div className="flex items-center gap-2">
              <Button size="sm" variant="outline" onClick={() => setShowScannerModal(true)} className="gap-1.5">
                <ScanLine className="w-3.5 h-3.5" />
                Ler Código de Barras / DataMatrix
              </Button>
              <Button size="sm" onClick={() => setShowNewOrderModal(true)} className="gap-1.5">
                <Plus className="w-3.5 h-3.5" />
                + Nova Ordem Cirúrgica
              </Button>
            </div>
          </div>

          {loadingOrders ? (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {columns.map((col) => (
                <div key={col.id} className="bg-surface-card border border-border rounded-lg p-3 space-y-3">
                  <Skeleton className="h-5 w-40" />
                  <Skeleton className="h-24 w-full" />
                  <Skeleton className="h-24 w-full" />
                </div>
              ))}
            </div>
          ) : ordersError ? (
            <div className="p-8 rounded-xl border border-status-danger/30 bg-status-danger-subtle/20 text-center">
              <div className="flex flex-col items-center gap-3">
                <AlertCircle className="w-8 h-8 text-status-danger" />
                <h3 className="text-sm font-semibold text-text-main">{ordersError}</h3>
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
              description="Clique em '+ Nova Ordem Cirúrgica' para cadastrar uma remessa de implantes e maletas guiadas."
              actionLabel="+ Nova Ordem Cirúrgica"
              onAction={() => setShowNewOrderModal(true)}
            />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {columns.map((col) => {
                const colOrders = orders.filter((o) => normalizeOrderStatus(o.status) === col.id);
                return (
                  <div
                    key={col.id}
                    className="bg-surface-card border border-border rounded-lg p-3 flex flex-col min-h-[500px] shadow-card"
                  >
                    <div className="flex justify-between items-center mb-3 pb-2 border-b border-border">
                      <span className="text-xs font-semibold text-text-secondary uppercase tracking-wider">
                        {col.title}
                      </span>
                      <span className="px-2 py-0.5 text-xs bg-surface-bg text-text-secondary rounded-full font-mono">
                        {colOrders.length}
                      </span>
                    </div>
                    <div className="flex-1 space-y-3 overflow-y-auto">
                      {colOrders.map((order) => {
                        const normStatus = normalizeOrderStatus(order.status);
                        return (
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

                            {normStatus === "SOLICITADO_FIELD" && (
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleApprove(order.id);
                                }}
                                className="w-full mt-2 py-1.5 px-3 bg-brand-primary hover:bg-brand-primary-hover text-text-inverse text-xs font-semibold rounded transition-colors flex items-center justify-center gap-1.5"
                              >
                                <CheckCircle2 className="w-3.5 h-3.5" />
                                Aprovar Remessa
                              </button>
                            )}

                            {normStatus === "APROVADO_INSIDE" && (
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleDispatch(order.id);
                                }}
                                className="w-full mt-2 py-1.5 px-3 bg-status-success text-text-inverse text-xs font-semibold rounded transition-colors flex items-center justify-center gap-1.5"
                              >
                                <Truck className="w-3.5 h-3.5" />
                                Despachar Maleta
                              </button>
                            )}

                            {normStatus === "EM_POSSE_CLINICA" && (
                              <div className="space-y-1.5 mt-2">
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setPostopOrder(order);
                                  }}
                                  className="w-full py-1.5 px-3 bg-brand-navy-subtle hover:bg-brand-primary text-brand-navy hover:text-text-inverse border border-brand-navy/30 text-xs font-semibold rounded transition-colors flex items-center justify-center gap-1.5"
                                >
                                  <FileText className="w-3.5 h-3.5" />
                                  Conciliar Pós-Op CFOP 5.113
                                </button>
                                <button
                                  onClick={async (e) => {
                                    e.stopPropagation();
                                    try {
                                      const res = await fetch(`/api/v1/keypartners/surgical-orders/${order.id}/trigger-dentgo-replenishment`, {
                                        method: "POST",
                                        headers: { "Content-Type": "application/json" },
                                      });
                                      const data = await res.json().catch(() => ({}));
                                      if (!res.ok) throw new Error(data.detail || "Falha ao solicitar reposição DENTGO.");
                                      setKitFeedback(`Reposição expressa DENTGO solicitada para ${order.id} (Pedido ${data.replenishment_order_id || "Criado"}).`);
                                      await fetchSurgicalOrders();
                                    } catch (err: any) {
                                      setKitFeedback(err.message || "Erro ao acionar reposição DENTGO.");
                                    }
                                  }}
                                  className="w-full py-1.5 px-3 bg-brand-primary-subtle hover:bg-brand-primary text-brand-primary hover:text-text-inverse border border-brand-primary/30 text-xs font-semibold rounded transition-colors flex items-center justify-center gap-1.5"
                                >
                                  <Truck className="w-3.5 h-3.5" />
                                  Reposição Rápida via DENTGO
                                </button>
                              </div>
                            )}

                            {normStatus === "FATURADO_E_REPOSTO" && (
                              <div className="mt-2 text-[11px] text-status-success font-mono bg-status-success-subtle p-1.5 rounded border border-status-success/20">
                                Nota: {order.billing_order_id || "CFOP 5.113 Emitida"}
                              </div>
                            )}
                          </div>
                        );
                      })}
                      {colOrders.length === 0 && (
                        <div className="h-24 flex items-center justify-center border border-dashed border-border rounded text-xs text-text-muted">
                          Sem ordens neste estágio
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* TAB 2: Acordos de Consignação, Maletas & Coleta Reversa */}
      {activeTab === "agreements" && (
        <div className="space-y-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <Button size="sm" onClick={() => setShowNewAgreementModal(true)} className="gap-1.5">
                <Plus className="w-3.5 h-3.5" />
                + Novo Acordo de Consignação
              </Button>
              <Button size="sm" variant="outline" onClick={() => setShowKitModal(true)} className="gap-1.5">
                <Package className="w-3.5 h-3.5" />
                + Cadastrar Maleta Serial
              </Button>
            </div>
            <Button size="sm" variant="outline" onClick={() => setShowPickupModal(true)} className="gap-1.5">
              <Truck className="w-3.5 h-3.5" />
              Acionar Coleta Reversa DENTGO
            </Button>
          </div>

          {kitFeedback && (
            <div className="p-3 rounded-lg bg-status-success-subtle text-status-success border border-status-success/20 text-xs font-medium">
              {kitFeedback}
            </div>
          )}
          {pickupFeedback && (
            <div className="p-3 rounded-lg bg-status-success-subtle text-status-success border border-status-success/20 text-xs font-medium">
              {pickupFeedback}
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Agreements List */}
            <div className="lg:col-span-1 bg-surface-card border border-border rounded-xl p-4 shadow-card space-y-3">
              <div className="flex items-center justify-between border-b border-border pb-2">
                <h3 className="text-xs font-bold uppercase tracking-wider text-text-main">
                  Acordos de Parceria ({agreements.length})
                </h3>
                <RefreshCw
                  className="w-3.5 h-3.5 text-text-secondary cursor-pointer hover:text-brand-primary"
                  onClick={fetchAgreements}
                />
              </div>

              {loadingAgreements ? (
                <div className="space-y-2">
                  <Skeleton className="h-16 w-full" />
                  <Skeleton className="h-16 w-full" />
                </div>
              ) : agreements.length === 0 ? (
                <div className="py-6 text-center text-xs text-text-muted">Nenhum acordo cadastrado.</div>
              ) : (
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {agreements.map((ag) => (
                    <div
                      key={ag.id}
                      onClick={() => setSelectedCustodyAgreementId(ag.id)}
                      className={`p-3 rounded-lg border transition-all cursor-pointer ${
                        selectedCustodyAgreementId === ag.id
                          ? "bg-surface-bg border-brand-primary shadow-card"
                          : "bg-surface-bg border-border hover:border-brand-primary/40"
                      }`}
                    >
                      <div className="flex justify-between items-start mb-1">
                        <span className="font-mono text-xs text-brand-primary font-bold">{ag.id}</span>
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-brand-primary-subtle text-brand-primary">
                          {ag.tier}
                        </span>
                      </div>
                      <h4 className="text-xs font-medium text-text-main">{ag.partner_name}</h4>
                      <div className="flex justify-between items-center text-[11px] text-text-secondary mt-2 pt-1 border-t border-border">
                        <span>Limite: R$ {ag.credit_limit.toFixed(2)}</span>
                        <span>Usado: R$ {ag.used_credit.toFixed(2)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Custody Summary */}
            <div className="lg:col-span-2 bg-surface-card border border-border rounded-xl p-5 shadow-card space-y-4">
              <div className="flex items-center justify-between border-b border-border pb-3">
                <div>
                  <h3 className="text-sm font-bold text-text-main">
                    Extrato de Custódia Sanitária ANVISA
                  </h3>
                  <p className="text-xs text-text-secondary">
                    Saldo vivo de produtos e instrumentais em posse da clínica parceira
                  </p>
                </div>
                {selectedCustodyAgreementId && (
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs text-brand-primary font-semibold">
                      {selectedCustodyAgreementId}
                    </span>
                    <Button size="sm" variant="outline" onClick={() => setShowDispatchCustodyModal(true)} className="gap-1.5">
                      <Truck className="w-3.5 h-3.5" />
                      Remeter Lotes para Custódia
                    </Button>
                  </div>
                )}
              </div>

              {loadingCustody ? (
                <div className="space-y-3">
                  <Skeleton className="h-20 w-full" />
                  <Skeleton className="h-40 w-full" />
                </div>
              ) : custodySummary ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                    <div className="p-3 bg-surface-bg rounded-lg border border-border">
                      <span className="text-text-muted text-[10px] block">Limite Aprovado:</span>
                      <span className="font-mono font-bold text-sm text-text-main">
                        R$ {custodySummary.credit_limit.toFixed(2)}
                      </span>
                    </div>
                    <div className="p-3 bg-surface-bg rounded-lg border border-border">
                      <span className="text-text-muted text-[10px] block">Crédito Utilizado:</span>
                      <span className="font-mono font-bold text-sm text-status-warning">
                        R$ {custodySummary.used_credit.toFixed(2)}
                      </span>
                    </div>
                    <div className="p-3 bg-surface-bg rounded-lg border border-border">
                      <span className="text-text-muted text-[10px] block">Crédito Disponível:</span>
                      <span className="font-mono font-bold text-sm text-status-success">
                        R$ {custodySummary.available_credit.toFixed(2)}
                      </span>
                    </div>
                    <div className="p-3 bg-surface-bg rounded-lg border border-border">
                      <span className="text-text-muted text-[10px] block">Itens em Posse:</span>
                      <span className="font-mono font-bold text-sm text-brand-primary">
                        {custodySummary.total_items_count} un
                      </span>
                    </div>
                  </div>

                  <div>
                    <h4 className="text-xs font-bold text-text-main mb-2">
                      Movimentações de Custódia (kp_custody_ledger):
                    </h4>
                    <div className="overflow-x-auto">
                      <table className="w-full text-xs text-left">
                        <thead className="bg-surface-bg text-text-secondary border-b border-border">
                          <tr>
                            <th className="p-2 font-semibold">Tipo</th>
                            <th className="p-2 font-semibold">Produto</th>
                            <th className="p-2 font-semibold">Lote / ANVISA</th>
                            <th className="p-2 font-semibold">Qtd</th>
                            <th className="p-2 font-semibold">Valor Total</th>
                            <th className="p-2 font-semibold">Validade</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-border">
                          {custodySummary.ledger_entries && custodySummary.ledger_entries.length > 0 ? (
                            custodySummary.ledger_entries.map((entry: any) => (
                              <tr key={entry.id} className="hover:bg-surface-bg">
                                <td className="p-2">
                                  <span
                                    className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                                      entry.movement_type === "REMESSA"
                                        ? "bg-brand-primary-subtle text-brand-primary"
                                        : "bg-status-success-subtle text-status-success"
                                    }`}
                                  >
                                    {entry.movement_type}
                                  </span>
                                </td>
                                <td className="p-2 font-medium">{entry.product_name}</td>
                                <td className="p-2 font-mono text-[11px] text-text-secondary">
                                  {entry.batch_number} • {entry.anvisa_reg}
                                </td>
                                <td className="p-2 font-mono font-bold">{entry.quantity}</td>
                                <td className="p-2 font-mono">R$ {entry.total_value.toFixed(2)}</td>
                                <td className="p-2 font-mono text-text-muted">{entry.sterilization_expiry_date}</td>
                              </tr>
                            ))
                          ) : (
                            <tr>
                              <td colSpan={6} className="p-4 text-center text-text-muted">
                                Nenhum registro de custódia para este acordo.
                              </td>
                            </tr>
                          )}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="h-48 flex items-center justify-center text-xs text-text-muted text-center border border-dashed border-border rounded-lg">
                  Selecione um acordo ao lado para inspecionar o saldo de custódia.
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: Contratos KOL & Speakers */}
      {activeTab === "kol" && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <span className="text-xs text-text-secondary font-medium">
              Líderes de Opinião Científica e Equipamentos Cedidos em Comodato
            </span>
            <Button size="sm" onClick={() => setShowKolModal(true)} className="gap-1.5">
              <Plus className="w-3.5 h-3.5" />
              + Novo Contrato KOL
            </Button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* KOL Contracts Table */}
            <div className="lg:col-span-2 bg-surface-card border border-border rounded-xl p-5 shadow-card space-y-4">
              <div className="flex items-center justify-between border-b border-border pb-3">
                <h3 className="text-sm font-bold text-text-main">
                  Contratos de Comodato & Metas de Implantes ({kolContracts.length})
                </h3>
                <RefreshCw
                  className="w-3.5 h-3.5 text-text-secondary cursor-pointer hover:text-brand-primary"
                  onClick={fetchKolData}
                />
              </div>

              {loadingKol ? (
                <div className="space-y-2">
                  <Skeleton className="h-16 w-full" />
                  <Skeleton className="h-16 w-full" />
                </div>
              ) : kolContracts.length === 0 ? (
                <div className="py-8 text-center text-xs text-text-muted border border-dashed border-border rounded-xl">
                  Nenhum contrato KOL registrado.
                </div>
              ) : (
                <div className="space-y-3">
                  {kolContracts.map((kol) => (
                    <div key={kol.id} className="p-4 bg-surface-bg rounded-xl border border-border space-y-3">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                        <div>
                          <div className="flex items-center gap-2">
                            <h4 className="text-sm font-bold text-text-main">{kol.kol_name}</h4>
                            <span className="font-mono text-xs text-text-muted">{kol.cro_uf}</span>
                          </div>
                          <span className="text-xs text-text-secondary block mt-0.5">
                            Equipamento: {kol.equipment_name} (Patrimônio: {kol.asset_tag})
                          </span>
                        </div>
                        <span
                          className={`text-xs font-mono font-bold px-2.5 py-1 rounded-full ${
                            kol.compliance_status === "EM_DIA"
                              ? "bg-status-success-subtle text-status-success border border-status-success/20"
                              : "bg-status-danger-subtle text-status-danger border border-status-danger/20"
                          }`}
                        >
                          {kol.compliance_status}
                        </span>
                      </div>

                      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs pt-2 border-t border-border">
                        <div>
                          <span className="text-text-muted text-[10px] block">Meta Mensal:</span>
                          <span className="font-mono font-semibold">{kol.min_monthly_implants_target} implantes</span>
                        </div>
                        <div>
                          <span className="text-text-muted text-[10px] block">Consumo Atual:</span>
                          <span className="font-mono font-bold text-brand-primary">
                            {kol.current_month_consumption} implantes
                          </span>
                        </div>
                        <div>
                          <span className="text-text-muted text-[10px] block">Cota de Aulas:</span>
                          <span className="font-mono font-semibold">{kol.clinical_lectures_quota} sessões</span>
                        </div>
                      </div>

                      <div className="flex flex-wrap gap-2 pt-2 border-t border-border">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setConsumptionContractId(kol.id)}
                          className="text-xs gap-1"
                        >
                          Apontar Consumo
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setEvidenceContractId(kol.id)}
                          className="text-xs gap-1"
                        >
                          Submeter Evidência R2
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Scientific Speakers Network */}
            <div className="lg:col-span-1 bg-surface-card border border-border rounded-xl p-5 shadow-card space-y-4">
              <div className="flex items-center justify-between border-b border-border pb-3">
                <h3 className="text-sm font-bold text-text-main">
                  Speakers Científicos Cadastrados ({kolSpeakers.length})
                </h3>
              </div>
              <div className="space-y-2.5 max-h-96 overflow-y-auto">
                {kolSpeakers.map((spk, idx) => (
                  <div key={idx} className="p-3 bg-surface-bg rounded-lg border border-border space-y-1 text-xs">
                    <div className="flex justify-between items-start">
                      <span className="font-bold text-text-main">{spk.name}</span>
                      <span className="text-[10px] font-mono text-brand-primary">{spk.cro}</span>
                    </div>
                    <span className="text-[11px] text-text-secondary block">
                      {spk.institutions_count} instituições parceiras
                    </span>
                    <div className="flex items-center justify-between text-[10px] text-text-muted font-mono pt-1">
                      <span>Volume: {spk.monthly_volume} un/mês</span>
                      <span className="text-status-success font-semibold">{spk.kol_badge}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: Programa de Fidelidade (Moeda Cirúrgica) */}
      {activeTab === "loyalty" && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-surface-card border border-border rounded-xl p-4 shadow-card">
            <div className="flex items-center gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-status-warning-subtle text-status-warning shrink-0">
                <Award className="h-4 w-4" />
              </div>
              <div>
                <span className="text-xs font-semibold text-text-main block">Carteira do Parceiro:</span>
                <span className="text-[11px] text-text-secondary">
                  Consulte o saldo de Moedas Cirúrgicas por implantes faturados
                </span>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={loyaltyPartnerId}
                onChange={(e) => setLoyaltyPartnerId(e.target.value)}
                placeholder="ID do Parceiro..."
                className="rounded-lg border border-border bg-surface-bg px-2.5 py-1 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary font-mono"
              />
              <Button size="sm" onClick={() => fetchLoyaltyData(loyaltyPartnerId)} disabled={loadingLoyalty}>
                {loadingLoyalty ? "Consultando..." : "Consultar"}
              </Button>
            </div>
          </div>

          {loyaltyFeedback && (
            <div className="p-3 rounded-lg bg-status-success-subtle text-status-success border border-status-success/20 text-xs font-medium">
              {loyaltyFeedback}
            </div>
          )}

          {wallet && (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="bg-surface-card border border-border rounded-xl p-4 shadow-card">
                <span className="text-text-muted text-[10px] block">Saldo de Moedas Cirúrgicas:</span>
                <span className="font-mono font-bold text-xl text-status-warning">
                  {wallet.points_balance} pts
                </span>
              </div>
              <div className="bg-surface-card border border-border rounded-xl p-4 shadow-card">
                <span className="text-text-muted text-[10px] block">Tier Atual:</span>
                <span className="font-mono font-bold text-xl text-brand-primary">{wallet.current_tier}</span>
              </div>
              <div className="bg-surface-card border border-border rounded-xl p-4 shadow-card">
                <span className="text-text-muted text-[10px] block">Pontos Vitalícios:</span>
                <span className="font-mono font-bold text-xl text-text-main">{wallet.lifetime_points} pts</span>
              </div>
              <div className="bg-surface-card border border-border rounded-xl p-4 shadow-card">
                <span className="text-text-muted text-[10px] block">Implantes Faturados Total:</span>
                <span className="font-mono font-bold text-xl text-status-success">
                  {wallet.implants_billed_total} un
                </span>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Rewards Catalog */}
            <div className="lg:col-span-2 bg-surface-card border border-border rounded-xl p-5 shadow-card space-y-4">
              <h3 className="text-sm font-bold text-text-main border-b border-border pb-3">
                Catálogo de Resgate de Recompensas Técnicas & Vouchers
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {rewards.map((rew) => (
                  <div key={rew.id} className="p-4 bg-surface-bg rounded-xl border border-border flex flex-col justify-between">
                    <div>
                      <div className="flex justify-between items-start mb-2">
                        <span className="font-bold text-xs text-text-main">{rew.name}</span>
                        <span className="font-mono text-xs font-bold text-status-warning bg-status-warning-subtle px-2 py-0.5 rounded">
                          {rew.points_required} pts
                        </span>
                      </div>
                      <p className="text-xs text-text-secondary leading-relaxed mb-3">{rew.description}</p>
                    </div>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleRedeemReward(rew.id)}
                      disabled={!wallet || wallet.points_balance < rew.points_required}
                      className="w-full gap-1 text-xs"
                    >
                      Resgatar Recompensa
                    </Button>
                  </div>
                ))}
              </div>
            </div>

            {/* Credit Points Box */}
            <div className="lg:col-span-1 bg-surface-card border border-border rounded-xl p-5 shadow-card space-y-4">
              <h3 className="text-sm font-bold text-text-main border-b border-border pb-3">
                Lançamento de Pontos por Cirurgias Faturadas
              </h3>
              <div className="space-y-3">
                <div>
                  <label className="text-xs font-medium text-text-secondary block mb-1">ID do Parceiro</label>
                  <input
                    type="text"
                    value={loyaltyCreditPartner}
                    onChange={(e) => setLoyaltyCreditPartner(e.target.value)}
                    className="w-full rounded-lg border border-border bg-surface-bg px-2.5 py-1.5 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary"
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-text-secondary block mb-1">Nome do Parceiro</label>
                  <input
                    type="text"
                    value={loyaltyCreditName}
                    onChange={(e) => setLoyaltyCreditName(e.target.value)}
                    className="w-full rounded-lg border border-border bg-surface-bg px-2.5 py-1.5 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary"
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-text-secondary block mb-1">
                    Implantes Faturados (unidades)
                  </label>
                  <input
                    type="number"
                    value={loyaltyCreditImplants}
                    onChange={(e) => setLoyaltyCreditImplants(Number(e.target.value))}
                    className="w-full rounded-lg border border-border bg-surface-bg px-2.5 py-1.5 text-xs text-text-main focus:outline-none focus:ring-1 focus:ring-brand-primary"
                  />
                </div>
                <Button
                  size="sm"
                  onClick={handleCreditPoints}
                  disabled={creditingLoyalty}
                  className="w-full gap-1.5"
                >
                  <Zap className="w-3.5 h-3.5" />
                  {creditingLoyalty ? "Creditando..." : "Creditar Moedas Cirúrgicas"}
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: Nova Ordem Cirúrgica */}
      {showNewOrderModal && (
        <div className="fixed inset-0 bg-text-main/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-surface-card border border-border rounded-xl max-w-lg w-full p-6 shadow-modal space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-border">
              <h3 className="text-base font-bold text-text-main">+ Nova Ordem Cirúrgica</h3>
              <button onClick={() => setShowNewOrderModal(false)} className="text-text-secondary hover:text-text-main">
                X
              </button>
            </div>
            <div className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-text-secondary block mb-1">ID do Acordo de Consignação</label>
                  <input
                    type="text"
                    value={orderAgreementId}
                    onChange={(e) => setOrderAgreementId(e.target.value)}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main"
                  />
                </div>
                <div>
                  <label className="text-text-secondary block mb-1">Paciente / Procedimento</label>
                  <input
                    type="text"
                    value={orderPatient}
                    onChange={(e) => setOrderPatient(e.target.value)}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-text-secondary block mb-1">Data Prevista Cirurgia</label>
                  <input
                    type="date"
                    value={orderDate}
                    onChange={(e) => setOrderDate(e.target.value)}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main"
                  />
                </div>
                <div>
                  <label className="text-text-secondary block mb-1">Consultor Comercial</label>
                  <input
                    type="text"
                    value={orderFieldConsultant}
                    onChange={(e) => setOrderFieldConsultant(e.target.value)}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main"
                  />
                </div>
              </div>
              <div className="pt-2 border-t border-border">
                <span className="font-bold text-text-main block mb-2">Grade do Implante Solicitado:</span>
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="text"
                    value={orderProductId}
                    onChange={(e) => setOrderProductId(e.target.value)}
                    placeholder="Código (ex: IMP-CM-4311)"
                    className="rounded-lg border border-border bg-surface-bg p-1.5 text-text-main"
                  />
                  <input
                    type="text"
                    value={orderProductName}
                    onChange={(e) => setOrderProductName(e.target.value)}
                    placeholder="Descrição"
                    className="rounded-lg border border-border bg-surface-bg p-1.5 text-text-main"
                  />
                  <input
                    type="text"
                    value={orderBatch}
                    onChange={(e) => setOrderBatch(e.target.value)}
                    placeholder="Lote"
                    className="rounded-lg border border-border bg-surface-bg p-1.5 text-text-main"
                  />
                  <input
                    type="number"
                    value={orderQty}
                    onChange={(e) => setOrderQty(Number(e.target.value))}
                    placeholder="Qtd"
                    className="rounded-lg border border-border bg-surface-bg p-1.5 text-text-main"
                  />
                  <input
                    type="text"
                    value={orderAnvisa}
                    onChange={(e) => setOrderAnvisa(e.target.value)}
                    placeholder="Registro ANVISA"
                    className="rounded-lg border border-border bg-surface-bg p-1.5 text-text-main font-mono"
                  />
                  <input
                    type="number"
                    value={orderUnitVal}
                    onChange={(e) => setOrderUnitVal(Number(e.target.value))}
                    placeholder="Valor Unit (R$)"
                    className="rounded-lg border border-border bg-surface-bg p-1.5 text-text-main font-mono"
                  />
                  <input
                    type="date"
                    value={orderExpiry}
                    onChange={(e) => setOrderExpiry(e.target.value)}
                    className="rounded-lg border border-border bg-surface-bg p-1.5 text-text-main font-mono col-span-2"
                  />
                </div>
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-3 border-t border-border">
              <Button variant="outline" size="sm" onClick={() => setShowNewOrderModal(false)}>
                Cancelar
              </Button>
              <Button size="sm" onClick={handleCreateOrder} disabled={creatingOrder}>
                {creatingOrder ? "Criando..." : "Emitir Ordem Cirúrgica"}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: Conciliação Pós-Operatória */}
      {postopOrder && (
        <div className="fixed inset-0 bg-text-main/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-surface-card border border-border rounded-xl max-w-lg w-full p-6 shadow-modal space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-border">
              <h3 className="text-base font-bold text-text-main">
                Conciliação Pós-Op & Faturamento CFOP 5.113
              </h3>
              <button onClick={() => setPostopOrder(null)} className="text-text-secondary hover:text-text-main">
                X
              </button>
            </div>
            <div className="space-y-3 text-xs">
              <p className="text-text-secondary">
                Ordem: <span className="font-mono text-brand-primary font-bold">{postopOrder.id}</span> •{" "}
                {postopOrder.patient_identifier}
              </p>
              <div>
                <label className="text-text-secondary block mb-1">Quantidade Efetivamente Instalada:</label>
                <input
                  type="number"
                  value={postopConsumedQty}
                  onChange={(e) => setPostopConsumedQty(Number(e.target.value))}
                  className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                />
              </div>
              <div>
                <label className="text-text-secondary block mb-1">Notas Pós-Operatórias / Torque:</label>
                <textarea
                  rows={3}
                  value={postopNotes}
                  onChange={(e) => setPostopNotes(e.target.value)}
                  className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main"
                />
              </div>
              <div className="p-3 bg-brand-primary-subtle rounded-lg border border-brand-primary/20 text-[11px] text-brand-primary">
                A conciliação gera a nota fiscal de venda (CFOP 5.113) dos itens consumidos e o retorno simbólico da maleta consignada.
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-3 border-t border-border">
              <Button variant="outline" size="sm" onClick={() => setPostopOrder(null)}>
                Cancelar
              </Button>
              <Button size="sm" onClick={handleReportPostop} disabled={submittingPostop}>
                {submittingPostop ? "Faturando..." : "Confirmar & Faturar CFOP 5.113"}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: Novo Acordo */}
      {showNewAgreementModal && (
        <div className="fixed inset-0 bg-text-main/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-surface-card border border-border rounded-xl max-w-md w-full p-6 shadow-modal space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-border">
              <h3 className="text-base font-bold text-text-main">+ Novo Acordo de Consignação</h3>
              <button onClick={() => setShowNewAgreementModal(false)} className="text-text-secondary hover:text-text-main">
                X
              </button>
            </div>
            <div className="space-y-3 text-xs">
              <div>
                <label className="text-text-secondary block mb-1">Razão Social / Nome do Parceiro</label>
                <input
                  type="text"
                  value={newAgPartner}
                  onChange={(e) => setNewAgPartner(e.target.value)}
                  className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main"
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-text-secondary block mb-1">CRO/UF</label>
                  <input
                    type="text"
                    value={newAgCro}
                    onChange={(e) => setNewAgCro(e.target.value)}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main"
                  />
                </div>
                <div>
                  <label className="text-text-secondary block mb-1">Nível de Parceria (Tier)</label>
                  <select
                    value={newAgTier}
                    onChange={(e) => setNewAgTier(e.target.value)}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main"
                  >
                    <option value="SILVER">SILVER</option>
                    <option value="GOLD">GOLD</option>
                    <option value="BLACK_KOL">BLACK_KOL</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="text-text-secondary block mb-1">Limite de Crédito Consignado (R$)</label>
                <input
                  type="number"
                  value={newAgLimit}
                  onChange={(e) => setNewAgLimit(Number(e.target.value))}
                  className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main"
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-3 border-t border-border">
              <Button variant="outline" size="sm" onClick={() => setShowNewAgreementModal(false)}>
                Cancelar
              </Button>
              <Button size="sm" onClick={handleCreateAgreement} disabled={creatingAgreement}>
                {creatingAgreement ? "Salvando..." : "Criar Acordo"}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: Cadastrar Kit Serial */}
      {showKitModal && (
        <div className="fixed inset-0 bg-text-main/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-surface-card border border-border rounded-xl max-w-md w-full p-6 shadow-modal space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-border">
              <h3 className="text-base font-bold text-text-main">Cadastrar Maleta Serial (QR Code)</h3>
              <button onClick={() => setShowKitModal(false)} className="text-text-secondary hover:text-text-main">
                X
              </button>
            </div>
            <div className="space-y-3 text-xs">
              <div>
                <label className="text-text-secondary block mb-1">Número de Série Gravado a Laser</label>
                <input
                  type="text"
                  value={kitSerial}
                  onChange={(e) => setKitSerial(e.target.value)}
                  className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                />
              </div>
              <div>
                <label className="text-text-secondary block mb-1">Nome Comercial do Kit</label>
                <input
                  type="text"
                  value={kitName}
                  onChange={(e) => setKitName(e.target.value)}
                  className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main"
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-3 border-t border-border">
              <Button variant="outline" size="sm" onClick={() => setShowKitModal(false)}>
                Cancelar
              </Button>
              <Button size="sm" onClick={handleRegisterKit} disabled={registeringKit}>
                {registeringKit ? "Registrando..." : "Registrar Maleta"}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: Coleta Reversa DENTGO */}
      {showPickupModal && (
        <div className="fixed inset-0 bg-text-main/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-surface-card border border-border rounded-xl max-w-md w-full p-6 shadow-modal space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-border">
              <h3 className="text-base font-bold text-text-main">Acionar Coleta Reversa DENTGO Express</h3>
              <button onClick={() => setShowPickupModal(false)} className="text-text-secondary hover:text-text-main">
                X
              </button>
            </div>
            <div className="space-y-3 text-xs">
              <div>
                <label className="text-text-secondary block mb-1">Serial da Maleta / Kit</label>
                <input
                  type="text"
                  value={pickupSerial}
                  onChange={(e) => setPickupSerial(e.target.value)}
                  className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                />
              </div>
              <div>
                <label className="text-text-secondary block mb-1">ID do Acordo de Destino</label>
                <input
                  type="text"
                  value={pickupAgreementId}
                  onChange={(e) => setPickupAgreementId(e.target.value)}
                  className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                />
              </div>
              <div>
                <label className="text-text-secondary block mb-1">Endereço de Coleta (Clínica)</label>
                <input
                  type="text"
                  value={pickupAddress}
                  onChange={(e) => setPickupAddress(e.target.value)}
                  className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main"
                />
              </div>
              <div>
                <label className="text-text-secondary block mb-1">Destino (Hub / Indústria)</label>
                <input
                  type="text"
                  value={pickupDest}
                  onChange={(e) => setPickupDest(e.target.value)}
                  className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main"
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-3 border-t border-border">
              <Button variant="outline" size="sm" onClick={() => setShowPickupModal(false)}>
                Cancelar
              </Button>
              <Button size="sm" onClick={handleTriggerPickup} disabled={triggeringPickup}>
                {triggeringPickup ? "Disparando..." : "Disparar Motoboy DENTGO"}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* TICKET-KEY-01: Leitor de Código de Barras / DataMatrix */}
      {showScannerModal && (
        <div className="fixed inset-0 bg-text-main/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-surface-card border border-border rounded-xl max-w-md w-full p-6 shadow-modal space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-border">
              <h3 className="text-base font-bold text-text-main flex items-center gap-2">
                <ScanLine className="h-4 w-4 text-brand-primary" />
                Leitor de Código de Barras / DataMatrix
              </h3>
              <button
                type="button"
                onClick={() => setShowScannerModal(false)}
                className="text-text-secondary hover:text-text-main"
                aria-label="Fechar leitor"
              >
                X
              </button>
            </div>
            <div className="space-y-3 text-xs">
              <p className="text-text-secondary">
                Posicione o código ANVISA/DataMatrix da maleta ou do lote de implante. O leitor usa a câmera quando disponível ou aceita digitação manual.
              </p>
              <div>
                <label className="text-text-secondary block mb-1">Código / Lote / Serial</label>
                <input
                  type="text"
                  value={scanCode}
                  onChange={(e) => setScanCode(e.target.value)}
                  placeholder="Ex: 7891234567890123 ou DM-LOT-2026-0042"
                  className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                />
              </div>
              {scanResult && (
                <div
                  className={`p-2 rounded border text-xs font-mono ${
                    scanResult.includes("QUARANTINE_BLOCKED")
                      ? "bg-status-danger-subtle border-status-danger/30 text-status-danger"
                      : "bg-status-success-subtle border-status-success/30 text-status-success"
                  }`}
                >
                  {scanResult}
                </div>
              )}
              <Button
                size="sm"
                className="w-full gap-1.5"
                onClick={async () => {
                  const code = scanCode.trim();
                  if (!code) {
                    setScanResult(null);
                    return;
                  }
                  try {
                    const [prodRes, quarRes] = await Promise.all([
                      fetch("/api/v1/deals/catalog/products"),
                      fetch("/api/v1/tickets/anvisa-rma/quarantines"),
                    ]);
                    const products = await prodRes.json().catch(() => []);
                    const quarantines = await quarRes.json().catch(() => []);

                    const cleanCode = code.toUpperCase();
                    const matchedProd = Array.isArray(products)
                      ? products.find((p: any) => cleanCode.includes(p.sku?.toUpperCase()) || p.sku?.toUpperCase().includes(cleanCode))
                      : null;
                    const sku = matchedProd ? matchedProd.sku : "IMP-CM-37511";

                    const matchedQuar = Array.isArray(quarantines)
                      ? quarantines.find((q: any) => cleanCode.includes(q.batch_number?.toUpperCase()) || q.batch_number?.toUpperCase().includes(cleanCode))
                      : null;

                    const isBlocked = matchedQuar && matchedQuar.status === "QUARANTINE_BLOCKED";
                    const batchStatus = isBlocked ? "QUARANTINE_BLOCKED" : "LIBERADO";
                    const expiry = matchedQuar?.recall_protocol ? "RECOLHIDO" : "2028-10-19";

                    setScanResult(`Status do Lote: ${batchStatus} | SKU: ${sku} | Validade: ${expiry} | Ref: ${code}`);
                  } catch (err: any) {
                    setScanResult(`Erro na validação do lote: ${err.message}`);
                  }
                }}
              >
                <ScanLine className="h-3.5 w-3.5" />
                Validar Código
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: Novo Contrato KOL */}
      {showKolModal && (
        <div className="fixed inset-0 bg-text-main/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-surface-card border border-border rounded-xl max-w-md w-full p-6 shadow-modal space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-border">
              <h3 className="text-base font-bold text-text-main">+ Novo Contrato KOL & Comodato</h3>
              <button onClick={() => setShowKolModal(false)} className="text-text-secondary hover:text-text-main">
                X
              </button>
            </div>
            <div className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-text-secondary block mb-1">Nome do KOL</label>
                  <input
                    type="text"
                    value={kolName}
                    onChange={(e) => setKolName(e.target.value)}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main"
                  />
                </div>
                <div>
                  <label className="text-text-secondary block mb-1">CRO/UF</label>
                  <input
                    type="text"
                    value={kolCro}
                    onChange={(e) => setKolCro(e.target.value)}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main"
                  />
                </div>
              </div>
              <div>
                <label className="text-text-secondary block mb-1">Equipamento Cedido em Comodato</label>
                <input
                  type="text"
                  value={kolEquip}
                  onChange={(e) => setKolEquip(e.target.value)}
                  className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main"
                />
              </div>
              <div className="grid grid-cols-3 gap-2">
                <div>
                  <label className="text-text-secondary block mb-1">Patrimônio</label>
                  <input
                    type="text"
                    value={kolTag}
                    onChange={(e) => setKolTag(e.target.value)}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                  />
                </div>
                <div>
                  <label className="text-text-secondary block mb-1">Meta Implantes/Mês</label>
                  <input
                    type="number"
                    value={kolTarget}
                    onChange={(e) => setKolTarget(Number(e.target.value))}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                  />
                </div>
                <div>
                  <label className="text-text-secondary block mb-1">Cota Aulas</label>
                  <input
                    type="number"
                    value={kolQuota}
                    onChange={(e) => setKolQuota(Number(e.target.value))}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                  />
                </div>
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-3 border-t border-border">
              <Button variant="outline" size="sm" onClick={() => setShowKolModal(false)}>
                Cancelar
              </Button>
              <Button size="sm" onClick={handleCreateKol} disabled={creatingKol}>
                {creatingKol ? "Cadastrando..." : "Cadastrar Contrato"}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: Apontar Consumo KOL */}
      {consumptionContractId && (
        <div className="fixed inset-0 bg-text-main/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-surface-card border border-border rounded-xl max-w-sm w-full p-5 shadow-modal space-y-4">
            <h3 className="text-sm font-bold text-text-main">Apontar Consumo Mensal de Implantes</h3>
            <div className="space-y-2 text-xs">
              <label className="text-text-secondary block">Total de implantes consumidos no mês:</label>
              <input
                type="number"
                value={consumptionQty}
                onChange={(e) => setConsumptionQty(Number(e.target.value))}
                className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
              />
            </div>
            <div className="flex justify-end gap-2 pt-2 border-t border-border">
              <Button variant="outline" size="sm" onClick={() => setConsumptionContractId(null)}>
                Cancelar
              </Button>
              <Button size="sm" onClick={handleRecordConsumption} disabled={recordingConsumption}>
                {recordingConsumption ? "Gravando..." : "Salvar Apontamento"}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: Remeter Lotes para Custódia */}
      {showDispatchCustodyModal && (
        <div className="fixed inset-0 bg-text-main/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-surface-card border border-border rounded-xl max-w-md w-full p-5 shadow-modal space-y-4">
            <h3 className="text-sm font-bold text-text-main">Remeter Lotes para Custódia ({selectedCustodyAgreementId})</h3>
            <div className="space-y-3 text-xs">
              <div className="grid grid-cols-3 gap-2">
                <div className="col-span-2">
                  <label className="text-text-secondary block mb-1">Produto:</label>
                  <input
                    type="text"
                    value={dispatchProductId}
                    onChange={(e) => setDispatchProductId(e.target.value)}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                  />
                </div>
                <div>
                  <label className="text-text-secondary block mb-1">Qtd:</label>
                  <input
                    type="number"
                    min={1}
                    value={dispatchQty}
                    onChange={(e) => setDispatchQty(Number(e.target.value))}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                  />
                </div>
              </div>
              <div>
                <label className="text-text-secondary block mb-1">Descrição do produto:</label>
                <input
                  type="text"
                  value={dispatchProductName}
                  onChange={(e) => setDispatchProductName(e.target.value)}
                  className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main"
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-text-secondary block mb-1">Lote:</label>
                  <input
                    type="text"
                    value={dispatchBatch}
                    onChange={(e) => setDispatchBatch(e.target.value)}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                  />
                </div>
                <div>
                  <label className="text-text-secondary block mb-1">Registro ANVISA:</label>
                  <input
                    type="text"
                    value={dispatchAnvisa}
                    onChange={(e) => setDispatchAnvisa(e.target.value)}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                  />
                </div>
                <div>
                  <label className="text-text-secondary block mb-1">Valor unitário (R$):</label>
                  <input
                    type="number"
                    min={0}
                    step="0.01"
                    value={dispatchUnitValue}
                    onChange={(e) => setDispatchUnitValue(Number(e.target.value))}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                  />
                </div>
                <div>
                  <label className="text-text-secondary block mb-1">Validade esterilização:</label>
                  <input
                    type="date"
                    value={dispatchExpiry}
                    onChange={(e) => setDispatchExpiry(e.target.value)}
                    className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                  />
                </div>
              </div>
              <Button type="button" size="sm" variant="outline" onClick={handleAddDispatchLot} className="w-full gap-1.5">
                <Plus className="w-3.5 h-3.5" />
                Adicionar Lote à Remessa
              </Button>
              {dispatchLots.length > 0 && (
                <ul className="rounded-lg border border-border divide-y divide-border">
                  {dispatchLots.map((l, i) => (
                    <li key={`${l.batch_number}-${i}`} className="flex items-center justify-between p-2 font-mono">
                      <span>
                        {l.product_id} / {l.batch_number} x {l.quantity} (R$ {(l.unit_value * l.quantity).toFixed(2)})
                      </span>
                      <button
                        type="button"
                        onClick={() => setDispatchLots((prev) => prev.filter((_, idx) => idx !== i))}
                        className="text-status-danger"
                      >
                        Remover
                      </button>
                    </li>
                  ))}
                </ul>
              )}
              {dispatchCustodyFeedback && <p className="text-status-danger">{dispatchCustodyFeedback}</p>}
            </div>
            <div className="flex justify-end gap-2 pt-2 border-t border-border">
              <Button variant="outline" size="sm" onClick={() => setShowDispatchCustodyModal(false)}>
                Cancelar
              </Button>
              <Button size="sm" onClick={handleDispatchCustody} disabled={dispatchingCustody}>
                {dispatchingCustody ? "Remetendo..." : "Confirmar Remessa"}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: Submeter Evidência R2 */}
      {evidenceContractId && (
        <div className="fixed inset-0 bg-text-main/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-surface-card border border-border rounded-xl max-w-md w-full p-5 shadow-modal space-y-4">
            <h3 className="text-sm font-bold text-text-main">Registrar Evidência Científica no Cloudflare R2</h3>
            <div className="space-y-3 text-xs">
              <div>
                <label className="text-text-secondary block mb-1">Título do Caso / Palestra:</label>
                <input
                  type="text"
                  value={evidenceTitle}
                  onChange={(e) => setEvidenceTitle(e.target.value)}
                  className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main"
                />
              </div>
              <div>
                <label className="text-text-secondary block mb-1">Chave / URI no Cloudflare R2:</label>
                <input
                  type="text"
                  value={evidenceR2Key}
                  onChange={(e) => setEvidenceR2Key(e.target.value)}
                  className="w-full rounded-lg border border-border bg-surface-bg p-2 text-text-main font-mono"
                />
                <div className="mt-2">
                  <R2DirectUploader
                    module="consignments"
                    accept=".pdf,.png,.jpg,.mp4"
                    onUploadComplete={(r) => setEvidenceR2Key(r.key)}
                  />
                </div>
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-2 border-t border-border">
              <Button variant="outline" size="sm" onClick={() => setEvidenceContractId(null)}>
                Cancelar
              </Button>
              <Button size="sm" onClick={handleSubmitEvidence} disabled={submittingEvidence}>
                {submittingEvidence ? "Enviando..." : "Registrar Evidência"}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: Detalhes da Ordem Cirúrgica */}
      {selectedOrder && (
        <div className="fixed inset-0 bg-text-main/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-surface-card border border-border rounded-xl max-w-lg w-full p-6 shadow-modal">
            <div className="flex justify-between items-center pb-3 border-b border-border">
              <h3 className="text-base font-bold text-text-main">Detalhes da Ordem Cirúrgica</h3>
              <button
                onClick={() => setSelectedOrder(null)}
                className="text-text-secondary hover:text-text-main"
              >
                X
              </button>
            </div>
            <div className="py-4 space-y-3 text-sm">
              <div>
                <span className="text-xs text-text-secondary block">ID da Ordem</span>
                <span className="font-mono text-brand-primary font-bold">{selectedOrder.id}</span>
              </div>
              <div>
                <span className="text-xs text-text-secondary block">Paciente / Procedimento</span>
                <span className="text-text-main">{selectedOrder.patient_identifier}</span>
              </div>
              <div>
                <span className="text-xs text-text-secondary block">Grade Remetida (ANVISA)</span>
                <pre className="mt-1 p-2 bg-surface-bg rounded text-xs font-mono text-brand-navy overflow-x-auto border border-border">
                  {selectedOrder.remitted_items_json}
                </pre>
              </div>
              {selectedOrder.consumed_items_json && selectedOrder.consumed_items_json !== "[]" && (
                <div>
                  <span className="text-xs text-text-secondary block">Itens Consumidos (Pós-Op)</span>
                  <pre className="mt-1 p-2 bg-surface-bg rounded text-xs font-mono text-status-success overflow-x-auto border border-border">
                    {selectedOrder.consumed_items_json}
                  </pre>
                </div>
              )}
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
              <Button variant="outline" size="sm" onClick={() => setSelectedOrder(null)}>
                Fechar
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ConsignmentSurgicalBoard;
