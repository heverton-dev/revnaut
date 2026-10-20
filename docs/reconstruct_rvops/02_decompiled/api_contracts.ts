/**
 * API Contracts & Data Schemas — Revnaut Core & Dental Ops (TICKET-00 .. TICKET-42)
 * Sincronizado estritamente 1:1 entre frontend/src/types/api_contracts.ts e docs/reconstruct_rvops/02_decompiled/api_contracts.ts
 */

export interface RvopsUser {
  id: string | number;
  email: string;
  first_name: string;
  last_name: string;
  profile_img: string | null;
  phone_number: string;
  timezone: string;
  mfa_enabled: boolean;
  default_mfa_method: 'WHATSAPP' | 'EMAIL' | 'APP';
  is_temp_token?: boolean;
}

export interface RvopsAccount {
  id: string;
  name: string;
  created_at?: string;
  plan_tier?: 'starter' | 'pro' | 'enterprise';
}

export interface UserRole {
  id: number;
  user_id: number;
  object:
    | 'ads'
    | 'asset'
    | 'billing'
    | 'campaign'
    | 'communication-inbox'
    | 'communication-management'
    | 'company'
    | 'config'
    | 'deal'
    | 'email'
    | 'form'
    | 'lead'
    | 'pipeline'
    | 'product'
    | 'report-dashboard'
    | 'task'
    | 'ticket';
  objectCreate: 0 | 1;
  objectRead: 0 | 1;
  objectEdit: 0 | 1;
  objectDelete: 0 | 1;
  mktPublish: 0 | 1;
}

export interface AuthLoginResponse {
  access_token: string;
  refresh_token: string;
  user: RvopsUser;
  roles: UserRole[];
}

export interface Contact {
  id: number | string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  company_name?: string;
  tags?: string[];
  owner_id?: number | string;
  owner_name?: string;
  created_at: string;
  updated_at: string;
  score?: number;
  status?: string;
}

export interface ContactListRequest {
  page?: number;
  limit?: number;
  search?: string;
  filters?: {
    owner_id?: string[];
    company_id?: string[];
    tags?: string[];
    created_after?: string;
    created_before?: string;
  };
}

export interface ContactListResponse {
  total: number;
  page: number;
  limit: number;
  data: Contact[];
}

export interface PipelineStage {
  id: number;
  pipeline_id: number;
  name: string;
  order: number;
  color?: string;
  probability?: number;
}

export interface Deal {
  id: number | string;
  title: string;
  value: number;
  stage_id: number;
  pipeline_id: number;
  contact_id?: number | string;
  contact_name?: string;
  company_id?: number | string;
  company_name?: string;
  owner_id: number | string;
  owner_name: string;
  field_owner_id?: string;
  inside_owner_id?: string;
  approval_status?: string;
  expected_close_date?: string;
  created_at: string;
}

export interface PipelineWithDeals {
  id: number;
  name: string;
  stages: Array<PipelineStage & { deals: Deal[]; total_value: number }>;
}

export interface ChatConversation {
  id: string;
  channel: 'whatsapp' | 'webchat' | 'sms';
  contact_id: string | number;
  contact_name: string;
  last_message: string;
  last_message_at: string;
  unread_count: number;
  status: 'open' | 'pending' | 'resolved';
  assigned_to?: string;
}

export interface Ticket {
  id: number | string;
  subject: string;
  status: 'novo' | 'em_andamento' | 'aguardando_cliente' | 'resolvido';
  priority: 'baixa' | 'media' | 'alta' | 'urgente' | 'P0_SURGICAL_TABLE';
  requester_name: string;
  requester_email: string;
  assigned_agent?: string;
  created_at: string;
  sla_due_at?: string;
}

export interface Task {
  id: number | string;
  title: string;
  due_date: string;
  completed: boolean;
  type: 'ligacao' | 'email' | 'reuniao' | 'whatsapp' | 'tarefa';
  associated_deal_id?: number | string;
  associated_contact_name?: string;
  owner_id: number | string;
}

export interface AccountUsageLimit {
  object: string;
  current_used: number;
  max_limit: number;
  percentage: number;
}

export type DataScopeEnum = 'self' | 'team' | 'subtree' | 'business_unit' | 'tenant_global';

export interface UserContext {
  user_id: string;
  account_id: string;
  role_id: string;
  team_id?: string | null;
  business_unit_id?: string | null;
  data_scope: DataScopeEnum;
  permissions: string[];
  is_superadmin: boolean;
}

export interface DentalContact extends Contact {
  cro: string;
  cro_uf: string;
  specialty: string;
  work_model: string;
  monthly_implants_volume: string;
  customer_type: 'Cirurgião' | 'Professor/KOL' | 'Aluno Especialização' | 'Clínica/DSO';
  city?: string;
  state?: string;
}

export interface ConsignmentBoxItem {
  id: string;
  sku: string;
  description: string;
  batch_number: string;
  expiry_date: string;
  quantity: number;
  unit_price: number;
}

export interface ConsignmentBox {
  id: string;
  account_id: string;
  contact_id: number | string;
  clinic_name: string;
  cro: string;
  box_status: 'em_campo' | 'em_cirurgia' | 'fechamento_pendente' | 'faturada_totvs';
  total_items: number;
  total_value: number;
  items: ConsignmentBoxItem[];
  created_at: string;
  updated_at: string;
}

export interface TotvsOrderItem {
  item_code: string;
  quantity: number;
  unit_price: number;
  total_value: number;
}

export interface TotvsOrderPayload {
  order_id: string;
  deal_id?: string;
  account_id: string;
  customer_code: string;
  customer_branch: string;
  customer_tax_id: string;
  cro?: string;
  cro_uf?: string;
  total_amount: number;
  items: TotvsOrderItem[];
  payment_condition: string;
  sales_channel: string;
  idempotency_key: string;
}

export interface HierarchyPreset {
  name: 'fabrica_enxuta' | 'nacional_expansao' | 'multidivisao_produtos' | 'multinacional_enterprise';
  title: string;
  description: string;
  business_units_count: number;
  teams_count: number;
  roles_count: number;
}

export type RelationshipTypeEnum = 'operates_at' | 'partner_cadcam' | 'teaches_at' | 'kol_speaker';

export interface ContactInstitution {
  id: string;
  account_id: string;
  contact_id: number;
  institution_id: string;
  relationship_type: RelationshipTypeEnum;
  role_title?: string;
  is_kol: boolean;
  notes?: string;
  created_at: string;
  institution_name?: string;
  institution_type?: string;
  contact_name?: string;
  contact_cro?: string;
}

export interface ClinicalGraphNode {
  id: string;
  label: string;
  node_type: 'surgeon' | 'clinic' | 'cadcam_lab' | 'university' | 'radiology';
  metadata?: Record<string, unknown>;
}

export interface ClinicalGraphEdge {
  source: string;
  target: string;
  relationship: string;
  is_kol: boolean;
  label: string;
}

export interface ClinicalGraphResponse {
  nodes: ClinicalGraphNode[];
  edges: ClinicalGraphEdge[];
  total_nodes: number;
  total_edges: number;
  kol_speakers_count: number;
}

export interface ChurnRiskItem {
  contact_id: number;
  name: string;
  cro?: string;
  clinic_name?: string;
  uf?: string;
  tier: string;
  monthly_implant_volume: number;
  avg_reorder_interval_days: number;
  days_since_last_order: number;
  days_overdue: number;
  last_order_date?: string;
  churn_risk_score: number;
  churn_risk_level: 'baixo' | 'medio' | 'alto' | 'critico';
  recommended_action: string;
}

export interface ChurnRiskSummary {
  total_monitored: number;
  critical_count: number;
  high_risk_count: number;
  medium_risk_count: number;
  low_risk_count: number;
}

export interface ChurnRiskResponse {
  summary: ChurnRiskSummary;
  radar: ChurnRiskItem[];
}

// =============================================================================
// FASE 0 a FASE 7: Storage R2, Vault, Marketing, Copilot, KeyPartners, DENTGO, CX, BI & Growth (TICKETS 01-37)
// =============================================================================

export interface PresignedUploadRequest {
  filename: string;
  module: 'consignments' | 'dicom' | 'contracts' | 'media';
  content_type: string;
}

export interface PresignedUploadResponse {
  upload_url: string;
  key: string;
  expires_in: number;
}

export interface VaultCredentialContract {
  id: string;
  account_id?: string;
  service_name: string;
  credential_type: string;
  masked_value: string;
  created_at?: string;
}

export interface CroVerificationContract {
  is_valid: boolean;
  status: 'ATIVO' | 'SUSPENSO' | 'CANCELADO' | 'INVALIDO';
  verified: boolean;
  canonical_cro: string;
  professional_name?: string;
  uf: string;
  clean_number: string;
  category: string;
  cached?: boolean;
}

export interface LandingPageContract {
  id: string;
  account_id: string;
  title: string;
  slug: string;
  template_type: string;
  published_r2_url?: string | null;
  cfo_compliance_status: string;
  cfo_responsible_cro: string;
  cfo_responsible_name: string;
}

export interface ScoringRuleContract {
  id: number | string;
  field: string;
  operator: string;
  value: string;
  points: number;
}

export interface ScoringHistoryContract {
  id: string;
  account_id: string;
  contact_id: number;
  previous_score: number;
  new_score: number;
  icp_fit_score: number;
  engagement_score: number;
  tier: string;
  trigger_reason: string;
  created_at: string;
}

export interface LiveKitRoomTokenContract {
  room_name: string;
  token: string;
  ws_url: string;
  egress_id?: string | null;
}

export interface MeetingIntelligenceExtraction {
  executive_summary: string;
  implant_systems_mentioned: string[];
  objections_raised: Array<{
    category: string;
    objection_text: string;
    suggested_counter_argument?: string;
  }>;
  next_steps_tasks: Array<{
    title: string;
    due_date: string;
    assignee?: string;
    priority?: string;
  }>;
  suggested_deal_value?: number | null;
}

export interface CatalogProduct {
  sku: string;
  name: string;
  category: string;
  implant_connection?: string;
  base_price: number;
  anvisa_registration: string;
}

export interface PriceTable {
  id: string;
  name: string;
  customer_segment: string;
  multiplier: number;
  max_consultant_discount_pct: number;
  max_manager_discount_pct: number;
}

export interface ProposalPricingResult {
  subtotal: number;
  discount_pct: number;
  discount_amount: number;
  final_total: number;
  approval_required_role?: string | null;
  approval_status: 'APPROVED' | 'PENDING_DISCOUNT_APPROVAL';
}

export interface DocumensoContractRecord {
  id: string;
  deal_id: string;
  documenso_document_id: string;
  status: 'PENDING_SIGNATURE' | 'SIGNED_COMPLETED';
  original_r2_key: string;
  signed_r2_key?: string | null;
  sha256_manifest?: string | null;
  signing_url: string;
}

export interface KeyPartnersAgreement {
  id: string;
  account_id: string;
  partner_name: string;
  partner_cro_uf: string;
  tier: string;
  credit_limit: number;
  used_credit: number;
  available_credit: number;
}

export interface KeyPartnersSurgicalOrder {
  id: string;
  account_id: string;
  agreement_id: string;
  patient_identifier?: string;
  surgery_date: string;
  status: 'SOLICITADO_FIELD' | 'APROVADO_INSIDE' | 'EM_POSSE_CLINICA' | 'FATURADO_E_REPOSTO';
  remitted_items_json: string;
  consumed_items_json: string;
  seal_photo_r2_key?: string | null;
  billing_order_id?: string | null;
}

export interface KolContract {
  id: string;
  account_id: string;
  surgeon_name: string;
  cro_uf: string;
  institution_name: string;
  monthly_implants_target: number;
  current_consumed_implants: number;
  compliance_status: 'COMPLIANT' | 'NON_COMPLIANT_ALERT';
}

export interface DentgoHub {
  id: string;
  name: string;
  city: string;
  uf: string;
  latitude: number;
  longitude: number;
  is_active: boolean;
}

export interface DentgoOrderContract {
  id: string;
  hub_id: string;
  customer_cro_uf: string;
  delivery_address: string;
  distance_km: number;
  estimated_eta_minutes: number;
  subtotal: number;
  urgency_fee: number;
  total_amount: number;
  status: string;
  seal_code?: string | null;
  delivery_pin?: string | null;
  proof_of_delivery_r2_key?: string | null;
}

export interface DentgoFinancialSplit {
  order_id: string;
  gross_amount: number;
  seller_net_amount: number;
  courier_fee_amount: number;
  revnault_take_rate_amount: number;
  take_rate_pct: number;
}

export interface SurgicalSosTicket {
  id: string;
  cro_uf: string;
  customer_name: string;
  priority: 'P0_SURGICAL_TABLE';
  livekit_room_url: string;
  livekit_token: string;
  status: string;
}

export interface AnvisaRmaClaim {
  id: string;
  batch_number: string;
  sku: string;
  failure_reason: string;
  status: string;
  quarantine_triggered: boolean;
}

export interface SupersetGuestTokenContract {
  token: string;
  dashboard_id: string;
  dashboard_type: string;
  rls_clause: string;
  superset_domain: string;
  expires_in_seconds: number;
}

export interface PredictiveSokResult {
  agreement_id: string;
  days_without_consumption: number;
  target_cycle_days: number;
  sok_score: number;
  is_idle: boolean;
  recommended_action: string;
}

export interface PredictivePrResult {
  agreement_id: string;
  sku: string;
  daily_demand: number;
  lead_time_days: number;
  safety_stock: number;
  replenishment_point_pr: number;
  current_stock: number;
  needs_replenishment: boolean;
}

export interface ClinicalProcedureMargin {
  id: string;
  clinic_id: string;
  procedure_name: string;
  gross_revenue: number;
  total_cost: number;
  net_margin_brl: number;
  net_margin_pct: number;
  low_margin_alert: boolean;
}

export interface SurgicalHealthScoreHsc {
  partner_id: string;
  hsc_score: number;
  risk_band: 'CRITICAL_CHURN' | 'ATTENTION' | 'HEALTHY_EXPANSION';
  triggered_playbook: string;
}

export interface LoyaltyWallet {
  partner_id: string;
  balance_coins: number;
  lifetime_coins: number;
  tier: 'SILVER' | 'GOLD' | 'BLACK_KOL';
}

// =============================================================================
// FASE 8: ERP Fiscal Hub, Orthanc DICOM 3D & Webhooks Outbound (TICKETS 38-40)
// =============================================================================

export interface ErpFiscalInvoice {
  id: string;
  account_id: string;
  erp_type: 'totvs_protheus' | 'sap_b1' | 'sankhya';
  flow_type: 'REMITTANCE_5917' | 'RETURN_1918' | 'SALE_5113';
  reference_id?: string;
  cfop: string;
  nfe_number: string;
  nfe_series: string;
  nfe_access_key: string;
  recipient_cnpj_cpf: string;
  recipient_name: string;
  total_invoice_value: number;
  xml_r2_key: string;
  danfe_pdf_r2_key: string;
  xml_url?: string;
  danfe_pdf_url?: string;
  status: string;
  sefaz_protocol?: string;
  windmill_job_id?: string;
  created_at?: string;
}

export interface ImagingStudy {
  id: string;
  account_id: string;
  patient_name?: string | null;
  patient_anonymized_id: string;
  deal_id?: string | null;
  ticket_id?: string | null;
  study_type: 'DICOM_CBCT' | 'INTRAORAL_STL' | 'INTRAORAL_PLY' | 'GUIDED_SURGERY_PLAN';
  orthanc_study_id?: string | null;
  r2_storage_key: string;
  file_name: string;
  file_size_bytes: number;
  slice_count: number;
  jaw_type: 'MAXILA' | 'MANDIBULA' | 'AMBAS' | 'PERIAPICAL';
  bone_density_estimate: string;
  implant_site?: string | null;
  is_anonymized: boolean;
  created_at?: string;
}

export interface ImagingStudyViewerSession {
  study_id: string;
  viewer_token: string;
  viewer_stream_url: string;
  r2_public_url: string;
  study_type: string;
  patient_anonymized_id: string;
  jaw_type: string;
  bone_density_estimate: string;
  implant_site?: string | null;
  slice_count: number;
  recommended_implant_diameter_mm: number;
  recommended_implant_length_mm: number;
  bone_thickness_mm: number;
  expires_in_seconds: number;
}

export interface WebhookSubscription {
  id: string;
  account_id: string;
  name: string;
  target_url: string;
  subscribed_events: string[];
  signing_secret: string;
  is_active: boolean;
  consecutive_failures: number;
  circuit_breaker_tripped: boolean;
  created_at?: string;
}

export interface WebhookDeliveryLog {
  id: string;
  subscription_id: string;
  account_id: string;
  event_name: string;
  target_url: string;
  signature_header: string;
  status_code?: number;
  response_body?: string;
  latency_ms: number;
  attempt: number;
  success: boolean;
  created_at?: string;
}

// =============================================================================
// MAPA CANÔNICO 1:1 DE TODAS AS ROTAS /api/v1/* (TICKET-41)
// =============================================================================

export const API_V1_ROUTES = [
  '/api/v1/auth/credentials',
  '/api/v1/auth/credentials/{credential_id}',
  '/api/v1/auth/forgot-password',
  '/api/v1/auth/login',
  '/api/v1/auth/logout',
  '/api/v1/auth/me',
  '/api/v1/auth/reset-password-with-token',
  '/api/v1/auth/users',
  '/api/v1/auth/users/{user_id}/reset-password',
  '/api/v1/auth/users/{user_id}/status',
  '/api/v1/automations/calcom/bookings',
  '/api/v1/automations/calcom/scan-dispatches',
  '/api/v1/automations/calcom/schedule-reactivation',
  '/api/v1/automations/calcom/schedules',
  '/api/v1/automations/calcom/webhook',
  '/api/v1/automations/evaluate-hot-lead/{contact_id}',
  '/api/v1/automations/flows',
  '/api/v1/automations/flows/{flow_id}/test',
  '/api/v1/automations/flows/{flow_id}/toggle',
  '/api/v1/automations/logs',
  '/api/v1/automations/postop-care',
  '/api/v1/automations/postop-care/start',
  '/api/v1/automations/postop-care/{schedule_id}',
  '/api/v1/automations/postop-care/{schedule_id}/feedback',
  '/api/v1/campaigns',
  '/api/v1/campaigns/broadcast-listmonk',
  '/api/v1/campaigns/landing-pages',
  '/api/v1/campaigns/landing-pages/templates',
  '/api/v1/campaigns/landing-pages/{page_id}',
  '/api/v1/campaigns/landing-pages/{page_id}/publish',
  '/api/v1/campaigns/metrics',
  '/api/v1/campaigns/public/lp/{slug}/submit',
  '/api/v1/campaigns/referral/dashboard/{referrer_id}',
  '/api/v1/campaigns/referral/generate-link',
  '/api/v1/campaigns/referral/qualify',
  '/api/v1/campaigns/referral/register',
  '/api/v1/campaigns/webhooks/listmonk',
  '/api/v1/chat/conversations',
  '/api/v1/chat/messages',
  '/api/v1/chat/{chat_id}/messages',
  '/api/v1/communications/deals/{deal_id}/recordings',
  '/api/v1/communications/livekit/webhook',
  '/api/v1/communications/rooms/token',
  '/api/v1/communications/voip/dial',
  '/api/v1/communications/webhooks/livekit',
  '/api/v1/contacts',
  '/api/v1/contacts/import',
  '/api/v1/contacts/validate-cfo-compliance',
  '/api/v1/contacts/validate-cro',
  '/api/v1/contacts/{contact_id}/profile',
  '/api/v1/contacts/{contact_id}/timeline',
  '/api/v1/contacts/{contact_id}/timeline/comments',
  '/api/v1/conversations/{chat_id}/messages',
  '/api/v1/deals',
  '/api/v1/deals/catalog/approve-discount',
  '/api/v1/deals/catalog/calculate-proposal',
  '/api/v1/deals/catalog/price-tables',
  '/api/v1/deals/catalog/products',
  '/api/v1/deals/export/csv',
  '/api/v1/deals/{deal_id}',
  '/api/v1/deals/{deal_id}/approve-credit',
  '/api/v1/deals/{deal_id}/contracts',
  '/api/v1/deals/{deal_id}/contracts/generate',
  '/api/v1/deals/{deal_id}/generate-contract',
  '/api/v1/deals/{deal_id}/stage',
  '/api/v1/deals/{deal_id}/timeline',
  '/api/v1/dentgo/fefo/deals',
  '/api/v1/dentgo/fefo/deals/{deal_id}',
  '/api/v1/dentgo/fefo/deals/{deal_id}/reserve',
  '/api/v1/dentgo/fefo/scan',
  '/api/v1/dentgo/hubs',
  '/api/v1/dentgo/hubs/search-emergency',
  '/api/v1/dentgo/hubs/{hub_id}/inventory',
  '/api/v1/dentgo/orders',
  '/api/v1/dentgo/orders/checkout',
  '/api/v1/dentgo/orders/express',
  '/api/v1/dentgo/orders/{order_id}',
  '/api/v1/dentgo/orders/{order_id}/assign-courier',
  '/api/v1/dentgo/orders/{order_id}/picking',
  '/api/v1/dentgo/orders/{order_id}/seal',
  '/api/v1/dentgo/orders/{order_id}/split',
  '/api/v1/dentgo/orders/{order_id}/start-transit',
  '/api/v1/dentgo/orders/{order_id}/verify-delivery',
  '/api/v1/dentgo/splits',
  '/api/v1/health',
  '/api/v1/hierarchy/business-units',
  '/api/v1/hierarchy/catalog',
  '/api/v1/hierarchy/commissions/rules',
  '/api/v1/hierarchy/commissions/statement',
  '/api/v1/hierarchy/presets/apply',
  '/api/v1/hierarchy/roles',
  '/api/v1/hierarchy/roles/{role_id}/permissions',
  '/api/v1/hierarchy/targets',
  '/api/v1/hierarchy/targets/suggestion',
  '/api/v1/hierarchy/teams',
  '/api/v1/hierarchy/teams/{team_id}/parent',
  '/api/v1/hierarchy/tree',
  '/api/v1/imaging/studies',
  '/api/v1/imaging/studies/upload-presign',
  '/api/v1/imaging/studies/{study_id}',
  '/api/v1/imaging/studies/{study_id}/viewer-token',
  '/api/v1/institutions',
  '/api/v1/integrations/erp/invoices',
  '/api/v1/integrations/erp/invoices/{invoice_id}',
  '/api/v1/integrations/erp/remittance/emit',
  '/api/v1/integrations/erp/settlement/emit',
  '/api/v1/integrations/totvs/customers/sync',
  '/api/v1/integrations/totvs/orders',
  '/api/v1/integrations/totvs/outbox',
  '/api/v1/intelligence/bi/export-dataset',
  '/api/v1/intelligence/bi/guest-token',
  '/api/v1/intelligence/bi/text-to-sql',
  '/api/v1/intelligence/catalog-rag/ingest',
  '/api/v1/intelligence/catalog-rag/query',
  '/api/v1/intelligence/churn-risk',
  '/api/v1/intelligence/clinical-graph',
  '/api/v1/intelligence/copilot/extract-and-apply',
  '/api/v1/intelligence/health-score/calculate',
  '/api/v1/intelligence/health-score/history/{partner_id}',
  '/api/v1/intelligence/imaging/studies',
  '/api/v1/intelligence/imaging/studies/upload-presign',
  '/api/v1/intelligence/imaging/studies/{study_id}',
  '/api/v1/intelligence/imaging/studies/{study_id}/viewer-token',
  '/api/v1/intelligence/inventory/pr',
  '/api/v1/intelligence/inventory/report/{agreement_id}',
  '/api/v1/intelligence/inventory/sok',
  '/api/v1/intelligence/kol-speakers',
  '/api/v1/intelligence/links',
  '/api/v1/intelligence/links/contact/{contact_id}',
  '/api/v1/intelligence/links/{link_id}',
  '/api/v1/intelligence/margin/calculate',
  '/api/v1/intelligence/margin/summary/{clinic_id}',
  '/api/v1/intelligence/transcriptions/deal/{deal_id}',
  '/api/v1/intelligence/transcriptions/process',
  '/api/v1/intelligence/transcriptions/{transcription_id}',
  '/api/v1/keypartners/agreements',
  '/api/v1/keypartners/agreements/{agreement_id}/custody-summary',
  '/api/v1/keypartners/agreements/{agreement_id}/dispatch',
  '/api/v1/keypartners/consignments/{kit_serial}/trigger-dentgo-pickup',
  '/api/v1/keypartners/kits',
  '/api/v1/keypartners/kol-contracts',
  '/api/v1/keypartners/kol-contracts/{contract_id}',
  '/api/v1/keypartners/kol-contracts/{contract_id}/evidence',
  '/api/v1/keypartners/kol-contracts/{contract_id}/record-consumption',
  '/api/v1/keypartners/loyalty/credit',
  '/api/v1/keypartners/loyalty/redeem',
  '/api/v1/keypartners/loyalty/rewards',
  '/api/v1/keypartners/loyalty/wallet/{partner_id}',
  '/api/v1/keypartners/surgical-orders',
  '/api/v1/keypartners/surgical-orders/{order_id}',
  '/api/v1/keypartners/surgical-orders/{order_id}/approve',
  '/api/v1/keypartners/surgical-orders/{order_id}/dispatch',
  '/api/v1/keypartners/surgical-orders/{order_id}/postop-report',
  '/api/v1/metrics',
  '/api/v1/omnichannel/chatwoot-context-panel',
  '/api/v1/omnichannel/chatwoot/sync-contact/{contact_id}',
  '/api/v1/omnichannel/context/{contact_identifier}',
  '/api/v1/omnichannel/webhook/evolution',
  '/api/v1/omnichannel/whatsapp/instances',
  '/api/v1/omnichannel/whatsapp/instances/{instance_name}',
  '/api/v1/pipelines',
  '/api/v1/quarteto/manuais',
  '/api/v1/quarteto/manuais/{filename}',
  '/api/v1/scoring/evaluate-handoff',
  '/api/v1/scoring/presets',
  '/api/v1/scoring/presets/apply',
  '/api/v1/scoring/recalculate',
  '/api/v1/scoring/rules',
  '/api/v1/scoring/rules/{rule_id}',
  '/api/v1/storage/files/{file_key:path}',
  '/api/v1/storage/presign-download',
  '/api/v1/storage/presign-download/{file_id:path}',
  '/api/v1/storage/presign-upload',
  '/api/v1/storage/upload-direct',
  '/api/v1/storage/upload-direct/{file_key:path}',
  '/api/v1/tasks',
  '/api/v1/tasks/{task_id}/toggle',
  '/api/v1/tickets',
  '/api/v1/tickets/anvisa-rma',
  '/api/v1/tickets/anvisa-rma/quarantine/{batch_number}',
  '/api/v1/tickets/anvisa-rma/{claim_id}',
  '/api/v1/tickets/surgical-sos',
  '/api/v1/tickets/surgical-sos/{ticket_id}',
  '/api/v1/tickets/surgical-sos/{ticket_id}/dispatch-dentgo',
  '/api/v1/tickets/{ticket_id}/status',
  '/api/v1/webhooks/chatwoot',
  '/api/v1/webhooks/documenso/document-completed',
  '/api/v1/webhooks/evolution',
  '/api/v1/webhooks/listmonk',
  '/api/v1/webhooks/listmonk/events',
  '/api/v1/webhooks/logs',
  '/api/v1/webhooks/mautic',
  '/api/v1/webhooks/mautic/campaign-action',
  '/api/v1/webhooks/subscriptions',
  '/api/v1/webhooks/subscriptions/{subscription_id}',
  '/api/v1/webhooks/subscriptions/{subscription_id}/reset-circuit',
  '/api/v1/webhooks/test-dispatch',
] as const;

export type ApiV1Route = (typeof API_V1_ROUTES)[number];
