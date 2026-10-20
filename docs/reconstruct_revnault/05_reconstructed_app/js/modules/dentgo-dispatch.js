/**
 * RevNault Dental Ops — DENTGO Express Dispatch & Last-Mile Module (ES Module)
 * Despacho cirúrgico, controle de lacre inviolável e validação sanitária por PIN.
 */

import { api } from './api-client.js';

export async function submitPicking(orderId, scannedBarcode) {
  const res = await api.post(`/dentgo/orders/${orderId}/picking`, {
    scanned_barcode: scannedBarcode
  });
  if (!res.ok) throw new Error('Falha ao registrar bipagem de separação');
  return res.json();
}

export async function sealPackage(orderId, sealCode) {
  const res = await api.post(`/dentgo/orders/${orderId}/seal`, {
    seal_code: sealCode
  });
  if (!res.ok) throw new Error('Falha ao lacrar maleta térmica');
  return res.json();
}

export async function assignCourier(orderId, courierId) {
  const res = await api.post(`/dentgo/orders/${orderId}/assign-courier`, {
    courier_id: courierId
  });
  if (!res.ok) throw new Error('Falha ao atribuir entregador');
  return res.json();
}

export async function startTransit(orderId) {
  const res = await api.post(`/dentgo/orders/${orderId}/start-transit`, {});
  if (!res.ok) throw new Error('Falha ao iniciar rota de entrega');
  return res.json();
}

export async function verifyAndCompleteDelivery(orderId, enteredPin, proofPhotoR2Key, recipientName) {
  const res = await api.post(`/dentgo/orders/${orderId}/verify-delivery`, {
    entered_pin: enteredPin,
    proof_photo_r2_key: proofPhotoR2Key,
    recipient_name: recipientName
  });
  if (!res.ok) throw new Error('PIN incorreto ou falha na validação sanitária');
  return res.json();
}
